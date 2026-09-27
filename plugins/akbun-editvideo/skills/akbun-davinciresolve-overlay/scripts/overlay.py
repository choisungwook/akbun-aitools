#!/usr/bin/env python3
"""사진·영상·화면 캡처를 둥근 모서리 카드로 만들어 이름으로 찾은 비디오 트랙(기본 OVERLAY)에 놓고 등장·퇴장을 키프레임으로 넣는다.
본편 클립의 느린 확대·축소(push)도 넣는다. 다른 트랙의 클립, 타임라인 마커, 타임라인 길이는 바뀌지 않는다.
DaVinci Resolve 21.1 외부 스크립팅 API만 쓴다.

  python3 overlay.py place --timeline B --at TC --seconds N (--file PATH | --clip 미디어풀_이름) [--x 0.5] [--y 0.5] [--width 0.3]
                           [--radius 0.08] [--in pop] [--out fade] [--in-frames 8] [--out-frames 6] [--overshoot 0.0]
                           [--source-in 초] [--track OVERLAY] [--out-dir DIR]
  python3 overlay.py push --timeline B --at TC [--track-index 1] [--from 1.0] [--to 1.08] [--x 0.5] [--y 0.5] [--reset] [--out-dir DIR]
  python3 overlay.py write-on --timeline B --at TC [--seconds 0.8] [--track SUBTITLE] [--out-dir DIR]
  python3 overlay.py selftest

write-on은 textplus.py place로 놓은 Text+의 Write On End를 0에서 1로 키프레임해 글자가 타이핑되듯 나오게 한다.

카드를 지울 때는 davinciresolve-subtitle-travelnote의 textplus.py remove --track OVERLAY를 쓴다.

21.1 실측으로 정한 것:
- Edit 페이지 Inspector의 Pan·Tilt·Zoom은 API로 고정값만 넣을 수 있고 키프레임을 넣는 함수가 없다. 움직임은 클립의 Fusion 컴포지션에 넣는다.
- Pan·Tilt의 단위는 소스와 타임라인의 화면비가 다르면 픽셀과 다르다(세로 타임라인의 가로 소스에서 Tilt 300이 95px). 그래서 위치·크기는
  Fusion 안에서 타임라인 해상도의 투명 캔버스 위에 정한다. 캔버스 기준이라 x·y·width가 화면 비율 그대로다.
- Transform 도구에 마스크를 걸면 마스크 밖으로 변형 전 그림이 그대로 보인다. 둥근 모서리는 투명 배경 위 Merge에 마스크를 걸어 만든다.
- TimelineItem.SetFades로 건 값은 프로젝트를 닫았다 열면 0으로 돌아온다. 페이드는 Merge의 Blend 키프레임으로 넣는다.
"""
import argparse
import datetime as dt
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "akbun-davinciresolve-searchhook", "scripts"))
import searchhook as SH  # noqa: E402

TRACK = "OVERLAY"
ABOVE = ("GFX", "SUBTITLE", "HOOK_TEXT")  # 카드보다 위에 있어야 하는 트랙
COMP = "AKBUN_OVERLAY"
PUSH = "AKBUN_PUSH"
MOVES = ("pop", "slide-left", "slide-right", "slide-up", "slide-down", "fade", "none")
EASE = {"out": ((0.125, 0.9), (0.625, 0.0)), "in": ((0.625, 0.0), (0.125, 0.9)), "inout": ((0.4, 0.0), (0.4, 0.0))}
AUTO = -32768  # Fusion이 도구 위치를 알아서 정한다


# ---------- 순수 함수 ----------
def spline(points):
    """[(프레임, 값, 다음 키까지의 ease)] -> BezierSpline.SetKeyFrames에 넘길 표. 핸들은 키 기준 상대값이다.
    out은 빠르게 출발해 감속(등장), in은 천천히 출발해 가속(퇴장), inout은 양쪽 감속(push)."""
    keys = {float(t): {1: v} for t, v, _ in points}
    for (t0, v0, kind), (t1, v1, _) in zip(points, points[1:]):
        (rx, ry), (lx, ly) = EASE[kind]
        keys[float(t0)]["RH"] = {1: (t1 - t0) * rx, 2: (v1 - v0) * ry}
        keys[float(t1)]["LH"] = {1: -(t1 - t0) * lx, 2: -(v1 - v0) * ly}
    return keys


def bezier_at(keys, t0, t1, frame):
    """selftest용. 두 키 사이 곡선의 frame에서의 값."""
    a, b = keys[float(t0)], keys[float(t1)]
    px = [t0, t0 + a["RH"][1], t1 + b["LH"][1], t1]
    py = [a[1], a[1] + a["RH"][2], b[1] + b["LH"][2], b[1]]
    lo, hi = 0.0, 1.0
    for _ in range(40):
        u = (lo + hi) / 2
        x = (1 - u) ** 3 * px[0] + 3 * (1 - u) ** 2 * u * px[1] + 3 * (1 - u) * u * u * px[2] + u ** 3 * px[3]
        lo, hi = (u, hi) if x < frame else (lo, u)
    return (1 - u) ** 3 * py[0] + 3 * (1 - u) ** 2 * u * py[1] + 3 * (1 - u) * u * u * py[2] + u ** 3 * py[3]


def card(src, tl, x, y, width):
    """소스 (w, h)와 타임라인 (w, h), 화면 비율 위치·폭 -> Merge Size와 카드의 화면 비율 (폭, 높이). 안전 영역(90%) 밖이면 ValueError."""
    (sw, sh), (tw, th) = src, tl
    h = width * tw * sh / sw / th
    if not 0 < width <= 0.9 or h > 0.9:
        raise ValueError("카드가 너무 큼: 폭 %.2f, 높이 %.2f (각각 화면의 0.9 이하)" % (width, h))
    low, high = 0.05 - 1e-9, 0.95 + 1e-9
    if x - width / 2 < low or x + width / 2 > high or y - h / 2 < low or y + h / 2 > high:
        raise ValueError("카드가 안전 영역(화면의 90%%) 밖: 중심 %.2f, %.2f 폭 %.2f 높이 %.2f" % (x, y, width, h))
    return width * tw / sw, (width, h)


def motion(move_in, move_out, n_in, n_out, last, size, x, y, box, overshoot):
    """등장·퇴장 -> {Size|Blend|X|Y: spline points}. last는 컴포지션 마지막 프레임, box는 카드의 화면 비율 (폭, 높이)."""
    if n_in + n_out >= last:
        raise ValueError("등장 %d + 퇴장 %d 프레임이 클립 길이 %d 프레임 이상" % (n_in, n_out, last))
    hold = last - n_out
    off = {"slide-left": ("X", -box[0] / 2 - 0.02), "slide-right": ("X", 1 + box[0] / 2 + 0.02),
           "slide-up": ("Y", -box[1] / 2 - 0.02), "slide-down": ("Y", 1 + box[1] / 2 + 0.02)}
    rest = {"X": x, "Y": y, "Size": size, "Blend": 1.0}
    tracks = {}

    def add(key, away, entering):
        points = tracks.setdefault(key, [(0, rest[key], "inout"), (n_in, rest[key], "inout"), (hold, rest[key], "in"), (last, rest[key], "in")])
        if entering:
            points[0] = (0, away, "out")
        else:
            points[3] = (last, away, "in")

    for move, entering in ((move_in, True), (move_out, False)):
        if move == "pop":
            add("Size", 0.0, entering)
            if entering and overshoot:
                peak = round(n_in * 0.6)
                tracks["Size"][1:2] = [(peak, size * (1 + overshoot), "inout"), (n_in, size, "inout")]
        elif move == "fade":
            add("Blend", 0.0, entering)
        elif move in off:
            add(off[move][0], off[move][1], entering)
    return tracks


def resolution(text):
    w, _, h = str(text).lower().partition("x")
    return int(w), int(h)


# ---------- Resolve ----------
def open_timeline(a):
    resolve, project = SH.connect()
    tl, fps, _ = SH.open_source(project, a.timeline)
    try:
        at = SH.tc_to_frame(a.at, fps)
    except ValueError as e:
        sys.exit(str(e))
    project.SetCurrentTimeline(tl)
    resolve.OpenPage("edit")
    return resolve, project, tl, fps, at


def overlay_track(tl, name):
    names = [tl.GetTrackName("video", t) for t in range(1, tl.GetTrackCount("video") + 1)]
    if name in names:
        track = names.index(name) + 1
        under = [n for n in names[:track - 1] if n in ABOVE]
        if under:
            sys.exit("%s 트랙(V%d)이 %s보다 위에 있어 글자를 가림. 트랙 순서를 고치거나 --track으로 다른 트랙을 준다" % (name, track, ", ".join(under)))
        return track
    if any(n in ABOVE for n in names):
        sys.exit("%s 트랙이 없고 글자·그래픽 트랙이 이미 있음. 맨 위에 만들면 글자를 가리므로 만들지 않음. "
                 "akbun-davinciresolve-workflow의 workflow.py tracks로 트랙을 준비한 복제본에서 실행하거나 --track으로 글자 트랙 아래의 빈 트랙 이름을 준다" % name)
    return SH.named_track(tl, "video", name)


def source_item(mp, a):
    pool = SH.pool_clips(mp)
    if a.clip:
        hit = [c for c in pool if c.GetName() == a.clip]
        if len(hit) != 1:
            sys.exit("미디어 풀에서 이름이 `%s`인 항목 %d개. 하나여야 함" % (a.clip, len(hit)))
        return hit[0], 0
    path = os.path.abspath(a.file)
    if not os.path.isfile(path):
        sys.exit("파일 없음: " + path)
    hit = next((c for c in pool if c.GetClipProperty("File Path") == path), None)
    if hit:
        return hit, 0
    got = mp.ImportMedia([path])
    if not got:
        sys.exit("미디어 풀로 가져오기 실패: " + path)
    return got[0], 1


def animate(tool, key, points):
    if not tool.AddModifier(key, "BezierSpline"):
        sys.exit("키프레임을 넣을 수 없음: " + key)
    tool[key].GetConnectedOutput().GetTool().SetKeyFrames(spline(points), True)


def comp_range(comp):
    attrs = comp.GetAttrs()
    return int(attrs["COMPN_RenderStart"]), int(attrs["COMPN_RenderEnd"])


def export_still(resolve, project, tl, fps, frame, out_dir, name):
    if not out_dir:
        return "-"
    folder = os.path.join(out_dir, "overlay-stills")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name + ".jpg")
    resolve.OpenPage("color")
    tl.SetCurrentTimecode(SH.frame_to_tc(frame, fps))
    time.sleep(1)
    return path if project.ExportCurrentFrameAsStill(path) else "확인 필요: 스틸 내보내기 실패"


def place(a, stamp):
    resolve, project, tl, fps, at = open_timeline(a)
    mp = project.GetMediaPool()
    origin, end, frames = tl.GetStartFrame(), tl.GetEndFrame(), round(a.seconds * fps)
    if not origin <= at < at + frames <= end or frames <= 0:
        sys.exit("카드 구간이 타임라인 밖: %s + %.1f초" % (a.at, a.seconds))
    tw, th = int(tl.GetSetting("timelineResolutionWidth")), int(tl.GetSetting("timelineResolutionHeight"))
    track = overlay_track(tl, a.track)
    if tl.GetIsTrackLocked("video", track):
        sys.exit("%s 트랙(V%d)이 잠겨 있음" % (a.track, track))
    before, marks = SH.layout(tl), tl.GetMarkers()
    hit = SH.clash(at - origin, frames, before[("video", track)])
    if hit:
        sys.exit("충돌: %s 트랙(V%d)의 %s에 이미 클립이 있어 놓지 않음" % (a.track, track, a.at))
    pool_before = len(SH.pool_clips(mp))
    item, imported = source_item(mp, a)
    try:
        src = resolution(item.GetClipProperty("Resolution"))
        size, box = card(src, (tw, th), a.x, a.y, a.width)
    except ValueError as e:
        sys.exit(str(e))
    # endFrame은 소스 프레임이다. 사진은 FPS가 비어 있어 타임라인 fps로 센다
    try:
        src_fps = float(item.GetClipProperty("FPS"))
    except (TypeError, ValueError):
        src_fps = float(fps)
    first = round(a.source_in * src_fps)
    got = mp.AppendToTimeline([{"mediaPoolItem": item, "trackIndex": track, "recordFrame": at, "startFrame": first,
                                "endFrame": first + round(a.seconds * src_fps) - 1, "mediaType": 1}])
    clip = got[0] if got and got[0] and got[0].GetStart() is not None else None
    if not clip:
        sys.exit("카드 배치 실패: V%d %s. 타임라인은 바뀌지 않음" % (track, a.at))

    def undo(reason):
        # 핸들은 지우기 직전에 다시 읽는다(오래된 핸들로 지우면 Resolve가 종료됨, 21.1 실측)
        gone = tl.DeleteClips([it for it in tl.GetItemListInTrack("video", track) if it.GetStart() == at], False)
        sys.exit("%s. 놓은 클립은 %s" % (reason, "지움" if gone else "V%d %s에 남음" % (track, a.at)))

    placed = clip.GetDuration()
    if abs(placed - frames) > 2:
        undo("놓인 길이 %d 프레임이 요청 %d 프레임과 다름(소스가 짧거나 --source-in이 끝에 가까움)" % (placed, frames))
    comp = clip.AddFusionComp()
    tools = comp and {t.GetAttrs()["TOOLS_RegID"]: t for t in comp.GetToolList(False).values()}
    if not comp or "MediaIn" not in tools or "MediaOut" not in tools:
        undo("Fusion 컴포지션을 만들 수 없음")
    clip.RenameFusionCompByName(clip.GetFusionCompNameList()[0], COMP)
    start, last = comp_range(comp)
    scale = (last - start + 1) / placed  # 컴포지션 프레임과 타임라인 프레임의 비
    try:
        tracks = motion(a.move_in, a.move_out, round(a.in_frames * scale), round(a.out_frames * scale), last - start, size, a.x, a.y, box, a.overshoot)
    except ValueError as e:
        undo(str(e))
    comp.Lock()
    canvas, clear = comp.AddTool("Background", AUTO, AUTO), comp.AddTool("Background", AUTO, AUTO)
    cut, mask, put = comp.AddTool("Merge", AUTO, AUTO), comp.AddTool("RectangleMask", AUTO, AUTO), comp.AddTool("Merge", AUTO, AUTO)
    comp.Unlock()
    for bg, (w, h) in ((canvas, (tw, th)), (clear, src)):
        for key, value in (("UseFrameFormatSettings", 0), ("Width", w), ("Height", h), ("TopLeftAlpha", 0.0)):
            bg.SetInput(key, value)
    for key, value in (("Width", 1.0), ("Height", 1.0), ("CornerRadius", a.radius)):
        mask.SetInput(key, value)
    cut.Background, cut.Foreground, cut.EffectMask = clear.Output, tools["MediaIn"].Output, mask.Mask
    put.Background, put.Foreground = canvas.Output, cut.Output
    tools["MediaOut"].Input = put.Output
    put.SetInput("Size", size)
    put.SetInput("Center", {1: a.x, 2: a.y})
    for key in ("Size", "Blend"):
        if key in tracks:
            animate(put, key, [(start + t, v, e) for t, v, e in tracks[key]])
    if "X" in tracks or "Y" in tracks:
        if not put.AddModifier("Center", "XYPath"):
            undo("위치 키프레임을 넣을 수 없음")
        path = put.Center.GetConnectedOutput().GetTool()
        for key, rest in (("X", a.x), ("Y", a.y)):
            if key in tracks:
                animate(path, key, [(start + t, v, e) for t, v, e in tracks[key]])
            else:
                path.SetInput(key, rest)
    # 멈춰 있는 구간의 값을 되읽어 확인한다
    mid = start + (last - start) // 2
    center = put.GetInput("Center", mid)
    if not (SH.same_value(put.GetInput("Size", mid), size) and abs(center[1] - a.x) < 1e-4 and abs(center[2] - a.y) < 1e-4 and canvas.GetInput("Width") == tw):
        undo("카드 값이 들어가지 않음")
    clip.SetName("CARD " + item.GetName())
    expect = dict(before)
    expect[("video", track)] = sorted(before[("video", track)] + [(at - origin, placed)])
    kept = SH.layout(tl) == expect and tl.GetMarkers() == marks and tl.GetEndFrame() == end
    added = len(SH.pool_clips(mp)) - pool_before - imported
    still = export_still(resolve, project, tl, fps, at + placed // 2, a.out_dir, "%s_%s" % (a.track, a.at.replace(":", "_")))
    ok = kept and not added
    L = ["## 오버레이 카드 배치", "", "| 타임라인 | 시작 TC | 종료 TC | 트랙 | 소스 | 중심(x, y) | 폭×높이(화면 비율) | 모서리 | 등장 | 퇴장 | 기존 클립·마커·타임라인 길이 | 스틸 | 결과 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
         "| %s | %s | %s | V%d %s | %s%s | %s, %s | %.2f×%.2f | %s | %s %df | %s %df | %s | %s | %s |" % (
             a.timeline, a.at, SH.frame_to_tc(at + placed, fps), track, a.track, item.GetName(), " (새로 가져옴)" if imported else "", a.x, a.y, box[0], box[1],
             a.radius, a.move_in, a.in_frames, a.move_out, a.out_frames, "그대로" if kept else "확인 필요: 바뀜", still, "적용" if ok else "확인 필요")]
    SH.write_log(a.out_dir, "overlay", stamp, "\n".join(L) + "\n")
    if not ok:
        sys.exit(1)


def push(a, stamp):
    resolve, project, tl, fps, at = open_timeline(a)
    clip = next((it for it in tl.GetItemListInTrack("video", a.track_index) or [] if it.GetStart() <= at < it.GetEnd() and it.GetMediaPoolItem()), None)
    if not clip:
        sys.exit("V%d의 %s에 영상 클립 없음" % (a.track_index, a.at))
    before, marks = SH.layout(tl), tl.GetMarkers()
    names = clip.GetFusionCompNameList() or []
    if [n for n in names if n != PUSH]:
        sys.exit("클립에 다른 Fusion 컴포지션이 있어 넣지 않음: %s. Fusion 페이지에서 Transform을 직접 더한다" % ", ".join(names))
    if not names and a.reset:
        print("%s V%d %s: push 없음" % (a.timeline, a.track_index, clip.GetName()))
        return
    if not (0.5 <= a.start <= 2 and 0.5 <= a.to <= 2 and 0 <= a.x <= 1 and 0 <= a.y <= 1):
        sys.exit("--from·--to는 0.5~2, --x·--y는 0~1")
    # 클립의 마지막 컴포지션은 DeleteFusionCompByName으로 지워지지 않는다(21.1 실측). 있던 것을 비워서 다시 쓴다
    comp = clip.GetFusionCompByName(PUSH) if names else clip.AddFusionComp()
    tools = comp and {t.GetAttrs()["TOOLS_RegID"]: t for t in comp.GetToolList(False).values()}
    if not comp or "MediaIn" not in tools or "MediaOut" not in tools:
        sys.exit("Fusion 컴포지션을 만들 수 없음")
    if not names:
        clip.RenameFusionCompByName(clip.GetFusionCompNameList()[0], PUSH)
    comp.Lock()
    for key, tool in tools.items():
        if key not in ("MediaIn", "MediaOut"):
            tool.Delete()
    comp.Unlock()
    tools["MediaOut"].Input = tools["MediaIn"].Output
    if a.reset:
        print("%s V%d %s: push 값을 지움. 빈 컴포지션 %s는 남는다" % (a.timeline, a.track_index, clip.GetName(), PUSH))
        return
    if min(a.start, a.to) < 1:
        print("주의: 1보다 작은 배율은 화면 가장자리에 빈 곳이 보인다")
    start, last = comp_range(comp)
    comp.Lock()
    move = comp.AddTool("Transform", AUTO, AUTO)
    comp.Unlock()
    move.Input = tools["MediaIn"].Output
    tools["MediaOut"].Input = move.Output
    move.SetInput("Pivot", {1: a.x, 2: a.y})
    animate(move, "Size", [(start, a.start, "inout"), (last, a.to, "inout")])
    got = (move.GetInput("Size", start), move.GetInput("Size", last))
    ok = SH.same_value(got[0], float(a.start)) and SH.same_value(got[1], float(a.to)) and SH.layout(tl) == before and tl.GetMarkers() == marks
    still = export_still(resolve, project, tl, fps, clip.GetEnd() - 1, a.out_dir, "push_%s" % a.at.replace(":", "_"))
    L = ["## 본편 push", "", "| 타임라인 | 클립 | 시작 TC | 종료 TC | 길이(초) | 배율 | 중심(x, y) | 초당 변화(%) | 끝 프레임 스틸 | 결과 |", "|---|---|---|---|---|---|---|---|---|---|",
         "| %s | V%d %s | %s | %s | %.1f | %s → %s | %s, %s | %.1f | %s | %s |" % (
             a.timeline, a.track_index, clip.GetName(), SH.frame_to_tc(clip.GetStart(), fps), SH.frame_to_tc(clip.GetEnd(), fps), clip.GetDuration() / fps,
             a.start, a.to, a.x, a.y, abs(a.to - a.start) * 100 / (clip.GetDuration() / fps), still, "적용" if ok else "확인 필요")]
    SH.write_log(a.out_dir, "overlay-push", stamp, "\n".join(L) + "\n")
    if not ok:
        sys.exit(1)


def write_on(a, stamp):
    _, _, tl, fps, at = open_timeline(a)
    track = next((t for t in range(1, tl.GetTrackCount("video") + 1) if tl.GetTrackName("video", t) == a.track), None)
    if not track:
        sys.exit("%s 트랙 없음" % a.track)
    clip = next((it for it in tl.GetItemListInTrack("video", track) or [] if it.GetStart() == at), None)
    comp = clip and not clip.GetMediaPoolItem() and clip.GetFusionCompCount() == 1 and clip.GetFusionCompByIndex(1)
    tool = comp and next((t for t in comp.GetToolList(False).values() if t.GetAttrs()["TOOLS_RegID"] == "TextPlus"), None)
    if not tool:
        sys.exit("%s 트랙(V%d)의 %s에서 시작하는 Text+ 클립 없음" % (a.track, track, a.at))
    start, last = comp_range(comp)
    frames = round(a.seconds * fps * (last - start + 1) / clip.GetDuration())
    if not 0 < frames < last - start:
        sys.exit("타이핑 길이 %.2f초가 클립 길이 %.2f초 이상" % (a.seconds, clip.GetDuration() / fps))
    # 글자가 한 글자씩 같은 속도로 나오게 선형으로 둔다. 핸들을 주지 않으면 BezierSpline은 직선이다
    if not tool.AddModifier("End", "BezierSpline"):
        sys.exit("Write On End에 키프레임을 넣을 수 없음")
    tool.End.GetConnectedOutput().GetTool().SetKeyFrames({float(start): {1: 0.0}, float(start + frames): {1: 1.0}}, True)
    got = [round(tool.GetInput("End", start + f), 3) for f in (0, frames // 2, frames)]
    ok = got[0] == 0.0 and got[2] == 1.0 and 0 < got[1] < 1
    L = ["## 글자 타이핑 등장", "", "| 타임라인 | 트랙 | 시작 TC | 타이핑(초) | 시작·중간·끝 Write On End | 결과 |", "|---|---|---|---|---|---|",
         "| %s | V%d %s | %s | %.2f | %s | %s |" % (a.timeline, track, a.track, a.at, a.seconds, " / ".join(map(str, got)), "적용" if ok else "확인 필요")]
    SH.write_log(a.out_dir, "overlay-writeon", stamp, "\n".join(L) + "\n")
    if not ok:
        sys.exit(1)


def selftest():
    keys = spline([(0, 0.0, "out"), (8, 1.0, "inout")])
    values = [bezier_at(keys, 0, 8, f) for f in range(1, 8)]
    assert values == sorted(values) and 0 < values[0] and values[-1] < 1.0 + 1e-9, values  # 넘치지 않고 단조 증가
    assert values[3] > 0.8, values  # out: 절반 시점에 80% 넘게 도착
    keys = spline([(10, 1.0, "in"), (16, 0.0, "in")])
    values = [bezier_at(keys, 10, 16, f) for f in range(11, 16)]
    assert values == sorted(values, reverse=True) and values[2] > 0.8, values  # in: 절반 시점에 아직 80% 넘게 남음
    keys = spline([(0, 1.0, "inout"), (100, 1.08, "inout")])
    assert abs(bezier_at(keys, 0, 100, 50) - 1.04) < 1e-3
    size, box = card((3840, 2160), (2160, 3840), 0.25, 0.7, 0.4)
    assert abs(size - 0.225) < 1e-9 and abs(box[1] - 0.12656) < 1e-4, (size, box)  # 21.1 실측: 폭 864px, 높이 486px
    size, box = card((1920, 1080), (3840, 2160), 0.75, 0.5, 0.3)
    assert abs(size - 0.6) < 1e-9 and abs(box[1] - 0.3) < 1e-9
    for bad in ((0.1, 0.5, 0.3), (0.5, 0.5, 0.95), (0.5, 0.9, 0.3)):
        try:
            card((1920, 1080), (3840, 2160), *bad)
        except ValueError:
            continue
        raise AssertionError("안전 영역 밖인데 통과: %s" % (bad,))
    t = motion("pop", "fade", 8, 6, 71, 0.6, 0.75, 0.5, (0.3, 0.3), 0.0)
    assert t["Size"] == [(0, 0.0, "out"), (8, 0.6, "inout"), (65, 0.6, "in"), (71, 0.6, "in")], t
    assert t["Blend"] == [(0, 1.0, "inout"), (8, 1.0, "inout"), (65, 1.0, "in"), (71, 0.0, "in")] and set(t) == {"Size", "Blend"}
    t = motion("pop", "none", 10, 6, 71, 0.6, 0.75, 0.5, (0.3, 0.3), 0.1)
    assert [p[0] for p in t["Size"]] == [0, 6, 10, 65, 71] and abs(t["Size"][1][1] - 0.66) < 1e-9
    t = motion("slide-left", "slide-right", 8, 8, 71, 0.6, 0.75, 0.5, (0.3, 0.3), 0.0)
    assert t["X"][0][1] < -0.15 and t["X"][3][1] > 1.15 and t["X"][1][1] == 0.75 and set(t) == {"X"}
    assert motion("none", "none", 8, 6, 71, 0.6, 0.5, 0.5, (0.3, 0.3), 0.0) == {}
    try:
        motion("pop", "fade", 40, 40, 71, 0.6, 0.5, 0.5, (0.3, 0.3), 0.0)
    except ValueError:
        pass
    else:
        raise AssertionError("클립보다 긴 등장·퇴장이 통과")
    assert resolution("3840x2160") == (3840, 2160)
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("place")
    p.add_argument("--timeline", required=True, help="작업 타임라인 이름")
    p.add_argument("--at", required=True, help="카드 시작 타임코드")
    p.add_argument("--seconds", type=float, required=True)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--file", help="사진·영상 파일 경로. 미디어 풀에 없으면 가져온다")
    g.add_argument("--clip", help="미디어 풀 항목 이름")
    p.add_argument("--x", type=float, default=0.5, help="카드 중심 X. 0 왼쪽 끝, 1 오른쪽 끝")
    p.add_argument("--y", type=float, default=0.5, help="카드 중심 Y. 0 아래 끝, 1 위 끝")
    p.add_argument("--width", type=float, default=0.3, help="카드 폭 / 화면 폭")
    p.add_argument("--radius", type=float, default=0.08, help="모서리 둥글기. 0 직각, 1 최대")
    p.add_argument("--in", dest="move_in", choices=MOVES, default="pop")
    p.add_argument("--out", dest="move_out", choices=MOVES, default="fade")
    p.add_argument("--in-frames", type=int, default=8)
    p.add_argument("--out-frames", type=int, default=6)
    p.add_argument("--overshoot", type=float, default=0.0, help="pop 등장이 목표 크기를 넘는 비율. 0이면 넘지 않는다")
    p.add_argument("--source-in", type=float, default=0.0, help="영상 소스의 시작 위치(초)")
    p.add_argument("--track", default=TRACK, help="놓을 비디오 트랙 이름")
    p.add_argument("--out-dir", help="로그와 확인 스틸(overlay-stills/)을 쓸 폴더(없으면 stdout만)")
    q = sub.add_parser("push")
    q.add_argument("--timeline", required=True)
    q.add_argument("--at", required=True, help="대상 클립 안의 타임코드")
    q.add_argument("--track-index", type=int, default=1)
    q.add_argument("--from", dest="start", type=float, default=1.0)
    q.add_argument("--to", type=float, default=1.08)
    q.add_argument("--x", type=float, default=0.5, help="확대 중심 X")
    q.add_argument("--y", type=float, default=0.5, help="확대 중심 Y")
    q.add_argument("--reset", action="store_true", help="이 스크립트가 넣은 push를 지운다")
    q.add_argument("--out-dir")
    w = sub.add_parser("write-on")
    w.add_argument("--timeline", required=True)
    w.add_argument("--at", required=True, help="Text+ 클립의 시작 타임코드")
    w.add_argument("--seconds", type=float, default=0.8, help="글자가 다 나올 때까지 걸리는 시간")
    w.add_argument("--track", default="SUBTITLE")
    w.add_argument("--out-dir")
    sub.add_parser("selftest")
    a = ap.parse_args()
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    {"place": place, "push": push, "write-on": write_on}.get(a.cmd, lambda *_: selftest())(a, stamp)


if __name__ == "__main__":
    main()
