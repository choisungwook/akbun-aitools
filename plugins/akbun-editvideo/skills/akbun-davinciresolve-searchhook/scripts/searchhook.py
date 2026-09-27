#!/usr/bin/env python3
"""완성 타임라인 B에서 훅 후보를 찾을 재료를 뽑고(inventory), 승인된 구간으로 훅 타임라인 H를 만든다(build).
DaVinci Resolve 21.1 외부 스크립팅 API만 쓴다.

  python3 searchhook.py inventory --timeline B --out DIR [--step SECONDS] [--no-stills]
  python3 searchhook.py build --timeline B --seg IN-OUT[=이름] [--seg ...] [--bgm-track N ...] [--name H] [--out DIR] [--max-seconds 45] [--dry-run]
  python3 searchhook.py text --timeline H --at TC --seconds N --text "문구" [--size 0.16] [--style Bold] [--x 0.5] [--y 0.5] [--out DIR]
  python3 searchhook.py selftest

H는 B를 복제한 타임라인이다. 복제본의 클립은 그대로 두고 맨 앞에 훅 길이만큼 공간을 ripple로 만들어 훅 구간을 넣는다.
훅 구간의 소스는 B를 한 번 더 복제한 <H>_src(BGM 트랙을 끈 스냅숏)의 중첩 클립이다. B는 수정하지 않는다.
훅 구간의 영상은 V1에, 소리는 새로 만든 HOOK 오디오 트랙에 놓는다.
--bgm-track으로 준 오디오 트랙은 잠근 채 밀어서 음악이 처음부터 끊기지 않고 이어진다. 밀린 만큼의 음악 길이 보정은 표로 알린다.
IN·OUT은 B의 타임라인 타임코드이고 OUT 프레임은 포함하지 않는다.
text는 H의 HOOK_TEXT 비디오 트랙에 일반 Text+ 클립 하나를 요청한 위치와 길이로 놓는다. 컴파운드 클립이나 다른 타임라인을 만들지 않고,
기존 클립·마커·타임라인 길이를 바꾸지 않는다. 미디어 풀에 Fusion Title 항목 HOOK_TEXT_TEMPLATE이 있어야 한다(SKILL.md의 Text+ 템플릿 준비).
"""
import argparse
import datetime as dt
import hashlib
import os
import re
import sys
import time

CHAPTER_MIN_SECONDS = 10  # YouTube 챕터 최소 길이
TEXT_TRACK = "HOOK_TEXT"
TEXT_TEMPLATE = "HOOK_TEXT_TEMPLATE"  # 미디어 풀의 Fusion Title 항목 이름
AUDIO_TRACK = "HOOK"
FONT = "Gmarket Sans"
KINDS = ("video", "audio", "subtitle")


# ---------- 순수 함수 ----------
# ponytail: non-drop-frame 타임코드만 지원. 29.97/59.94 drop-frame 타임라인이 필요해지면 DF 변환을 추가한다.
def tc_to_frame(tc, fps):
    m = re.fullmatch(r"(\d{2}):(\d{2}):(\d{2}):(\d{2})", tc.strip())
    if not m:
        raise ValueError("타임코드 형식은 HH:MM:SS:FF (drop-frame ';' 미지원): " + tc)
    h, mi, s, f = map(int, m.groups())
    if mi > 59 or s > 59 or f >= fps:
        raise ValueError("타임코드 범위 오류: " + tc)
    return ((h * 60 + mi) * 60 + s) * fps + f


def frame_to_tc(frame, fps):
    s, f = divmod(frame, fps)
    return "%02d:%02d:%02d:%02d" % (s // 3600, s // 60 % 60, s % 60, f)


def plan(segs, start_tc, length, fps, max_seconds):
    """segs: ["IN-OUT" 또는 "IN-OUT=이름"] -> [{name, tc_in, tc_out, start, end, frames, record}]. start·end는 B 첫 프레임 기준, end 미포함."""
    origin = tc_to_frame(start_tc, fps)
    rows, record = [], 0
    for i, seg in enumerate(segs, 1):
        span, _, name = seg.partition("=")
        tc_in, sep, tc_out = span.partition("-")
        if not sep:
            raise ValueError("구간 형식은 IN-OUT[=이름]: " + seg)
        start, end = tc_to_frame(tc_in, fps) - origin, tc_to_frame(tc_out, fps) - origin
        if not 0 <= start < end <= length:
            raise ValueError("구간이 타임라인 밖이거나 길이가 0 이하: " + seg)
        rows.append({"name": name or "H%d" % i, "tc_in": tc_in.strip(), "tc_out": tc_out.strip(),
                     "start": start, "end": end, "frames": end - start, "record": record})
        record += end - start
    if not rows:
        raise ValueError("--seg가 하나 이상 필요")
    if record > max_seconds * fps:
        raise ValueError("훅 전체 %.1f초 > 허용 %d초. 구간을 줄이거나 --max-seconds를 올린다" % (record / fps, max_seconds))
    return rows


def chapter_fix(chapters, hook, fps):
    """ripple 뒤 H의 CHAPTER 마커 프레임 목록 -> 첫 챕터를 0프레임에 두는 방법.
    "intro": 0프레임에 CHAPTER 인트로 추가(훅 10초 이상), "move": 훅 끝의 첫 챕터를 0프레임으로 옮김, None: 할 일 없음."""
    if not chapters or 0 in chapters:
        return None
    if hook >= CHAPTER_MIN_SECONDS * fps:
        return "intro"
    return "move" if hook in chapters else None


def expected(before, hook, fixed):
    """before: {(종류, 트랙): [(시작, 길이)]} -> ripple 뒤 기대 위치. fixed(잠근 트랙)는 그대로, 나머지는 hook만큼 뒤로."""
    return {k: [(s + (0 if k in fixed else hook), d) for s, d in v] for k, v in before.items()}


def bgm_rows(items, hook, video_end):
    """BGM 트랙 클립 [(시작, 길이, 오른쪽 여유)] -> 보정 표 [(시작, 끝, 할 일)]. 프레임은 H 첫 프레임 기준.
    본편이 hook만큼 밀렸으므로 첫 클립 끝을 hook만큼 늘리면 뒤 경계와 끝이 본편과 다시 맞는다."""
    rows = []
    for i, (start, frames, room) in enumerate(sorted(items)):
        end, last = start + frames, i == len(items) - 1
        if i == 0:
            todo = "끝을 +%d프레임 ripple로 늘림" % hook if room >= hook else "끝을 늘릴 소스가 %d프레임뿐(필요 %d). 훅 전용 음악이나 다른 곡으로 채움" % (room, hook)
        else:
            todo = "첫 클립을 늘리면 +%d프레임 따라 밀림" % hook
        if last and end + hook < video_end:
            todo += ". 보정 뒤에도 영상 끝보다 %d프레임 짧음" % (video_end - end - hook)
        rows.append((start, end, todo))
    return rows


def clash(start, frames, clips):
    """[start, start+frames)와 겹치는 기존 클립 [(시작, 길이)]. 끝 프레임은 포함하지 않으므로 맞닿은 클립은 겹치지 않는다."""
    return [(s, d) for s, d in clips if s < start + frames and start < s + d]


def free_frame(frame, end, used):
    """frame부터 end 전까지 마커가 없는 첫 프레임. 없으면 None."""
    return next((f for f in range(frame, end) if f not in used), None)


# ---------- Resolve ----------
def connect():
    api = os.environ.setdefault("RESOLVE_SCRIPT_API", "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting")
    os.environ.setdefault("RESOLVE_SCRIPT_LIB", "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so")
    sys.path.append(os.path.join(api, "Modules"))
    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        sys.exit("Resolve에 연결 못 함: Resolve Studio 실행, External scripting=Local, 환경변수 확인")
    return resolve, resolve.GetProjectManager().GetCurrentProject()


def find_timeline(project, name):
    for i in range(1, project.GetTimelineCount() + 1):
        tl = project.GetTimelineByIndex(i)
        if tl.GetName() == name:
            return tl
    return None


def open_source(project, name):
    tl = find_timeline(project, name)
    if not tl:
        sys.exit("타임라인 없음: " + name)
    if str(tl.GetSetting("timelineDropFrameTimecode")) == "1":
        sys.exit("drop-frame 타임코드 타임라인은 지원하지 않음: " + name)
    fps = round(float(tl.GetSetting("timelineFrameRate")))
    return tl, fps, tl.GetEndFrame() - tl.GetStartFrame()


def layout(tl):
    """{(종류, 트랙 번호): [(시작, 길이)]}. 시작은 타임라인 첫 프레임 기준."""
    o = tl.GetStartFrame()
    return {(k, t): [(it.GetStart() - o, it.GetDuration()) for it in (tl.GetItemListInTrack(k, t) or [])]
            for k in KINDS for t in range(1, tl.GetTrackCount(k) + 1)}


def duplicate(project, src, name):
    tl = src.DuplicateTimeline(name)
    if not tl or tl.GetName() != name or not project.SetCurrentTimeline(tl) or project.GetCurrentTimeline().GetName() != name:
        sys.exit("타임라인 복제 실패: " + name)
    return tl


def write_log(out, prefix, stamp, text):
    print(text)
    if out:
        os.makedirs(out, exist_ok=True)
        path = os.path.join(out, "%s_%s.md" % (prefix, stamp))
        open(path, "w").write(text)
        print("로그:", path)


def inventory(a, stamp):
    resolve, project = connect()
    tl, fps, length = open_source(project, a.timeline)
    origin = tl.GetStartFrame()
    clips = tl.GetItemListInTrack("video", 1) or []
    if not clips:
        sys.exit("V1에 클립 없음: " + a.timeline)
    stills = None
    if not a.no_stills:
        stills = os.path.join(a.out, "hook-stills")
        os.makedirs(stills, exist_ok=True)
        project.SetCurrentTimeline(tl)
        resolve.OpenPage("color")
    L = ["## 훅 재료 목록", "", "타임라인: `%s` (%d fps, %.1f초, V1 %d클립)" % (a.timeline, fps, length / fps, len(clips)), "",
         "| 파일명 | 시작 TC | 끝 TC | 길이(초) | 스틸 |", "|---|---|---|---|---|"]
    last = None
    for it in clips:
        s, e = it.GetStart(), it.GetEnd()
        frames = [(s + e) // 2] if not a.step else list(range(s + int(a.step * fps / 2), e, int(a.step * fps))) or [(s + e) // 2]
        names = []
        for f in frames if stills else []:
            name = frame_to_tc(f, fps).replace(":", "_") + ".jpg"
            path = os.path.join(stills, name)
            if not tl.SetCurrentTimecode(frame_to_tc(f, fps)):
                sys.exit("타임코드 이동 실패 " + name)
            for attempt in range(4):  # 뷰어가 아직 이전 프레임이면 기다려 다시 내보낸다
                time.sleep(0.3 * (attempt + 1))
                if not project.ExportCurrentFrameAsStill(path):
                    sys.exit("스틸 내보내기 실패 " + path)
                digest = hashlib.md5(open(path, "rb").read()).hexdigest()
                if digest != last:
                    break
            last = digest
            names.append(name)
        L.append("| %s | %s | %s | %.1f | %s |" % (it.GetName(), frame_to_tc(s, fps), frame_to_tc(e, fps), (e - s) / fps, ", ".join(names) or "-"))
    marks = tl.GetMarkers() or {}
    if marks:
        L += ["", "| 마커 TC | 색 | 이름 |", "|---|---|---|"]
        L += ["| %s | %s | %s |" % (frame_to_tc(origin + int(f), fps), m["color"], m["name"]) for f, m in sorted(marks.items(), key=lambda x: int(x[0]))]
    write_log(a.out, "searchhook-inventory", stamp, "\n".join(L) + "\n")


def build(a, stamp):
    resolve, project = connect()
    src, fps, length = open_source(project, a.timeline)
    name = a.name or "%s_hook_%s" % (a.timeline, stamp[:13])
    try:
        rows = plan(a.seg, src.GetStartTimecode(), length, fps, a.max_seconds)
    except ValueError as e:
        sys.exit(str(e))
    hook = sum(r["frames"] for r in rows)
    tracks = src.GetTrackCount("audio")
    bgm = sorted(set(a.bgm_track))
    if any(not 1 <= t <= tracks for t in bgm):
        sys.exit("--bgm-track은 1~%d" % tracks)
    L = ["## 훅 타임라인", "", "원본: `%s` → 새 타임라인: `%s`, 훅 소스: `%s_src` (%s)" % (a.timeline, name, name, "dry-run, 만들지 않음" if a.dry_run else "생성"),
         "", "훅 길이: %.1f초(%d프레임), 본편 시작: %s" % (hook / fps, hook, frame_to_tc(tc_to_frame(src.GetStartTimecode(), fps) + hook, fps)), "",
         "| 순서 | 이름 | B의 IN | B의 OUT | 길이(초) | 훅 안 시작(초) |", "|---|---|---|---|---|---|"]
    L += ["| %d | %s | %s | %s | %.1f | %.1f |" % (i, r["name"], r["tc_in"], r["tc_out"], r["frames"] / fps, r["record"] / fps) for i, r in enumerate(rows, 1)]
    L += ["", "| 오디오 트랙 | 이름 | 클립 수 | 처리 |", "|---|---|---|---|"]
    L += ["| A%d | %s | %d | %s |" % (t, src.GetTrackName("audio", t), len(src.GetItemListInTrack("audio", t) or []),
                                  "BGM: 잠그고 제자리" if t in bgm else "훅 구간의 소리" if src.GetTrackName("audio", t) == AUDIO_TRACK else "훅 길이만큼 뒤로") for t in range(1, tracks + 1)]
    if AUDIO_TRACK not in [src.GetTrackName("audio", t) for t in range(1, tracks + 1)]:
        L += ["| A%d (새 트랙) | %s | 0 | 훅 구간의 소리 |" % (tracks + 1, AUDIO_TRACK)]
    if a.dry_run:
        return write_log(a.out, "searchhook-dryrun", stamp, "\n".join(L) + "\n")

    for n in (name, name + "_src"):
        if find_timeline(project, n):
            sys.exit("같은 이름의 타임라인이 이미 있음: " + n)
    before, marks = layout(src), sorted(int(f) for f in (src.GetMarkers() or {}))
    # 훅 소스: BGM 트랙을 끈 B의 스냅숏. 중첩 클립의 소리에 음악이 섞이지 않고, 나중에 B를 고쳐도 훅이 바뀌지 않는다
    snap = duplicate(project, src, name + "_src")
    for t in bgm:
        snap.SetTrackEnable("audio", t, False)
    source = snap.GetMediaPoolItem()
    tl = duplicate(project, src, name)
    resolve.OpenPage("edit")
    origin, mp = tl.GetStartFrame(), project.GetMediaPool()
    fixed = {(k, t) for k in KINDS for t in range(1, tl.GetTrackCount(k) + 1) if tl.GetIsTrackLocked(k, t)} | {("audio", t) for t in bgm}
    if ("video", 1) in fixed:
        sys.exit("V1이 잠겨 있으면 훅을 넣을 수 없음. `%s`, `%s_src`는 만들어진 채 남음" % (name, name))
    # 훅 구간의 소리는 본편 트랙에 섞지 않고 훅 전용 오디오 트랙에 놓는다. workflow가 만들어 둔 HOOK 트랙이 있으면 그것을 쓴다
    voice = named_track(tl, "audio", AUDIO_TRACK)
    if ("audio", voice) in fixed:
        sys.exit("%s 오디오 트랙이 잠겨 있거나 BGM으로 지정됨. `%s`, `%s_src`는 만들어진 채 남음" % (AUDIO_TRACK, name, name))
    for t in bgm:
        tl.SetTrackLock("audio", t, True)

    def stop(why):
        sys.exit("%s. `%s`는 만들다 만 상태이고 BGM 트랙 %s이 잠겨 있을 수 있음. 확인 뒤 지우고 다시 실행" % (why, name, bgm))

    # 1) 맨 앞에 타이틀을 끼워 넣어(ripple) 잠기지 않은 트랙과 마커를 민다. 타이틀 길이가 고정이라 hook 이상이 될 때까지 넣는다
    gap = 0
    while gap < hook:
        tl.SetCurrentTimecode(tl.GetStartTimecode())
        title = tl.InsertFusionTitleIntoTimeline("Text+")
        if not title or title.GetStart() != origin:
            stop("앞 공간 만들기 실패")
        gap += title.GetDuration()
    # 2) 타이틀을 지워 빈 공간으로. 핸들은 지우기 직전에 다시 읽는다(오래된 핸들로 지우면 Resolve가 종료됨, 21.1 실측)
    if not tl.DeleteClips([it for it in tl.GetItemListInTrack("video", 1) if it.GetStart() - origin < gap], False):
        stop("자리 표시 타이틀 삭제 실패")
    # 3) 훅 구간을 놓는다. 같은 항목을 한 번에 여러 개 넘기면 첫 개만 들어가므로 하나씩 붙인다
    for r in rows:
        for media, track in ((1, 1), (2, voice)):  # 1 영상은 V1, 2 소리는 훅 오디오 트랙
            if not mp.AppendToTimeline([{"mediaPoolItem": source, "mediaType": media, "trackIndex": track, "recordFrame": origin + r["record"],
                                         "startFrame": r["start"], "endFrame": r["end"]}]):
                stop("훅 구간 붙이기 실패: " + r["name"])
    # 4) 남는 공간은 채움 클립을 놓고 ripple 삭제해 닫는다
    if gap > hook:
        if not mp.AppendToTimeline([{"mediaPoolItem": source, "trackIndex": 1, "recordFrame": origin + hook, "startFrame": 0, "endFrame": gap - hook, "mediaType": 1}]):
            stop("채움 클립 붙이기 실패")
        filler = [it for it in tl.GetItemListInTrack("video", 1) if it.GetStart() - origin == hook and it.GetDuration() == gap - hook]
        if len(filler) != 1 or not tl.DeleteClips(filler, True):
            stop("남는 공간 닫기 실패")
    for t in bgm:
        tl.SetTrackLock("audio", t, False)

    want = expected(before, hook, fixed)
    for k in (("video", 1), ("audio", voice)):
        want[k] = [(r["record"], r["frames"]) for r in rows] + want.get(k, [])
    got = layout(tl)
    wrong = sorted("%s%d" % (k[0][0].upper(), k[1]) for k in want if got.get(k) != want[k])
    have = sorted(int(f) for f in (tl.GetMarkers() or {}))
    used, failed = set(have), []
    fix = chapter_fix([int(f) for f, m in tl.GetMarkers().items() if m["name"].startswith("CHAPTER")], hook, fps)
    if fix == "intro":
        tl.AddMarker(0, "Blue", "CHAPTER 인트로", "", 1) or failed.append("CHAPTER 인트로")
    elif fix == "move":
        m = tl.GetMarkers()[hook]
        tl.DeleteMarkerAtFrame(hook)
        tl.AddMarker(0, m["color"], m["name"], m["note"], m["duration"], m["customData"]) or failed.append(m["name"])
        used.discard(hook)
    used.add(0) if fix else None
    for r in rows:
        f = free_frame(r["record"], r["record"] + r["frames"], used)
        ok = f is not None and tl.AddMarker(f, "Mint", "HOOK " + r["name"], "B %s-%s" % (r["tc_in"], r["tc_out"]), r["record"] + r["frames"] - f)
        used.add(f) if ok else failed.append("HOOK " + r["name"])
    video_end = max(s + d for s, d in got[("video", 1)])
    music = []
    for t in bgm:
        items = [(it.GetStart() - origin, it.GetDuration(), int(it.GetRightOffset() or 0)) for it in tl.GetItemListInTrack("audio", t) or []]
        for start, end, todo in bgm_rows(items, hook, video_end):
            music.append("| A%d | %s | %s | %s |" % (t, frame_to_tc(origin + start, fps), frame_to_tc(origin + end, fps), todo))
            f = free_frame(end, end + fps, used) if "늘림" in todo or "채움" in todo else None
            if f is not None and tl.AddMarker(f, "Mint", "HOOK_BGM A%d" % t, todo, 1):
                used.add(f)
    same = layout(src) == before and sorted(int(f) for f in (src.GetMarkers() or {})) == marks
    L += ["", "| 검증 | 결과 |", "|---|---|",
          "| 트랙별 클립 위치·길이 == 계획 | %s |" % ("일치 (%d트랙)" % len(want) if not wrong else "불일치: " + ", ".join(wrong)),
          "| 마커가 훅 길이만큼 밀림 | %s |" % ("일치" if have == [f + hook for f in marks] else "확인 필요: %s" % have),
          "| 해상도·프레임레이트 == 원본 | %s |" % ("일치" if all(tl.GetSetting(k) == src.GetSetting(k) for k in ("timelineResolutionWidth", "timelineResolutionHeight", "timelineFrameRate")) else "불일치"),
          "| 원본 `%s` 클립·마커 위치 | %s |" % (a.timeline, "그대로" if same else "바뀜"),
          "| 훅 오디오 트랙 | A%d `%s`%s |" % (voice, tl.GetTrackName("audio", voice), "" if tl.GetTrackName("audio", voice) == AUDIO_TRACK else " (확인 필요: 이름 설정 실패)"),
          "| 새 마커 | %s |" % ("전부 등록" if not failed else "확인 필요: 등록 실패 " + ", ".join(failed))]
    if music:
        L += ["", "### BGM 길이 보정", "", "BGM 트랙은 제자리에 있고 본편은 %d프레임(%.1f초) 밀렸다. 트림 API가 없어 아래 보정은 Resolve에서 직접 하거나 `davinciresolve-sfx-epidemicsound`에 넘긴다." % (hook, hook / fps),
              "", "| 트랙 | 시작 TC | 끝 TC | 할 일 |", "|---|---|---|---|"] + music
    write_log(a.out, "searchhook", stamp, "\n".join(L) + "\n")
    if wrong or not same:
        sys.exit(1)


def named_track(tl, kind, name):
    """이름이 name인 트랙 번호. 없으면 새로 만들어 이름을 붙인다(비디오는 맨 위, 오디오는 맨 아래)."""
    for t in range(1, tl.GetTrackCount(kind) + 1):
        if tl.GetTrackName(kind, t) == name:
            return t
    if not (tl.AddTrack(kind, "stereo") if kind == "audio" else tl.AddTrack(kind)):
        sys.exit("트랙 추가 실패: " + name)
    t = tl.GetTrackCount(kind)
    tl.SetTrackName(kind, t, name)
    return t


def pool_clips(mp):
    """미디어 풀의 모든 항목(하위 bin 포함). 타임라인과 컴파운드 클립도 항목이다."""
    stack, clips = [mp.GetRootFolder()], []
    while stack:
        folder = stack.pop()
        clips += folder.GetClipList() or []
        stack += folder.GetSubFolderList() or []
    return clips


def same_value(got, want):
    return abs(got - want) < 1e-6 if isinstance(want, float) and isinstance(got, (int, float)) else got == want


def put_text(resolve, project, tl, fps, track_name, template, at, frames, inputs):
    """미디어 풀의 Fusion Title 항목 template을 이름이 track_name인 비디오 트랙의 at 프레임에 frames 길이의 일반 Text+ 클립 하나로 놓고
    inputs [(Text+ 입력 이름, 값)]를 넣는다. Font와 Style은 꼭 있어야 한다. -> {track, kept, added}. 놓을 수 없으면 타임라인을 바꾸지 않고 종료한다.
    davinciresolve-subtitle-travelnote의 textplus.py도 이 함수를 쓴다."""
    origin, end, tc, want = tl.GetStartFrame(), tl.GetEndFrame(), frame_to_tc(at, fps), dict(inputs)
    if not origin <= at < at + frames <= end or frames <= 0:
        sys.exit("텍스트 구간이 타임라인 밖: %s + %.1f초" % (tc, frames / fps))
    # Text+는 없는 글꼴 이름도 그대로 받아들이고 다른 글꼴로 그리므로(21.1 실측) Resolve의 글꼴 목록으로 확인한다
    styles = list(((resolve.Fusion().FontManager.GetFontList() or {}).get(want["Font"]) or {}).keys())
    if want["Style"] not in styles:
        sys.exit("Resolve에 글꼴 없음: %s %s (있는 굵기: %s). 설치한 뒤 Resolve를 다시 열고 실행한다" % (want["Font"], want["Style"], ", ".join(styles) or "없음"))
    # API에는 트랙과 위치를 정해 Text+를 새로 만드는 함수가 없다(InsertFusionTitleIntoTimeline은 재생헤드에 끼워 넣어 뒤와 마커를 민다, 21.1 실측).
    # 미디어 풀의 Fusion Title 항목은 AppendToTimeline으로 트랙·위치·길이를 정해 놓을 수 있고, 놓인 것은 항목과 이어지지 않은 일반 Text+다.
    mp = project.GetMediaPool()
    pool = pool_clips(mp)
    source = next((c for c in pool if c.GetName() == template and c.GetClipProperty("Type") == "Fusion Title"), None)
    if not source:
        sys.exit("미디어 풀에 Fusion Title 항목 `%s`이 없음. API로는 만들 수 없으니 akbun-davinciresolve-searchhook SKILL.md의 'Text+ 템플릿 준비' 절차를 Resolve 화면에서 한 번 한 뒤 다시 실행한다" % template)
    project.SetCurrentTimeline(tl)
    resolve.OpenPage("edit")
    track = named_track(tl, "video", track_name)
    if tl.GetIsTrackLocked("video", track):
        sys.exit("%s 트랙(V%d)이 잠겨 있음. 잠금을 풀고 다시 실행한다" % (track_name, track))
    before, marks = layout(tl), tl.GetMarkers()
    hit = clash(at - origin, frames, before[("video", track)])
    if hit:
        sys.exit("충돌: %s 트랙(V%d)에 이미 클립이 있어 놓지 않음. 요청 %s + %.1f초, 기존 %s. 기존 클립은 그대로다" % (
            track_name, track, tc, frames / fps, ", ".join("%s~%s" % (frame_to_tc(origin + s, fps), frame_to_tc(origin + s + d, fps)) for s, d in hit)))
    got = mp.AppendToTimeline([{"mediaPoolItem": source, "trackIndex": track, "recordFrame": at, "startFrame": 0, "endFrame": frames, "mediaType": 1}])
    clip = got[0] if got and got[0] and got[0].GetStart() is not None else None
    if not clip:
        sys.exit("Text+ 배치 실패: V%d %s. 타임라인은 바뀌지 않음" % (track, tc))
    comp = clip.GetFusionCompByIndex(1) if clip.GetFusionCompCount() == 1 and not clip.GetMediaPoolItem() else None
    tool = comp and next((t for t in comp.GetToolList(False).values() if t.GetAttrs()["TOOLS_RegID"] == "TextPlus"), None)
    if not tool:
        sys.exit("놓인 클립이 일반 Text+가 아님. `%s` 항목이 Text+로 만든 것인지 확인한다. 놓인 클립: V%d %s" % (template, track, tc))
    for key, value in inputs:
        tool.SetInput(key, value)
    # 없는 입력 이름은 조용히 무시되므로 되읽어 확인한다. 표로 받는 Center는 빼고 본다
    wrong = [k for k, v in inputs if not isinstance(v, dict) and not same_value(tool.GetInput(k), v)]
    if wrong:
        # 핸들은 지우기 직전에 다시 읽는다(오래된 핸들로 지우면 Resolve가 종료됨, 21.1 실측)
        gone = tl.DeleteClips([it for it in tl.GetItemListInTrack("video", track) if it.GetStart() == at], False)
        sys.exit("Text+ 입력이 들어가지 않음: %s. 놓은 클립은 %s" % (", ".join(wrong), "지움" if gone else "V%d %s에 남음" % (track, tc)))
    clip.SetName("Text+")
    expect = dict(before)
    expect[("video", track)] = sorted(before[("video", track)] + [(at - origin, frames)])
    kept = layout(tl) == expect and tl.GetMarkers() == marks and tl.GetEndFrame() == end
    return {"track": track, "kept": kept, "added": len(pool_clips(mp)) - len(pool)}


def text_inputs(text, font, style, size, x, y):
    return [("StyledText", text.replace("\\n", "\n")), ("Font", font), ("Style", style), ("Size", size), ("Center", {1: x, 2: y})]


def text(a, stamp):
    resolve, project = connect()
    tl, fps, length = open_source(project, a.timeline)
    if not any(m["name"].startswith("HOOK ") for m in (tl.GetMarkers() or {}).values()):
        sys.exit("HOOK 마커가 없음. build로 만든 훅 타임라인에만 텍스트를 넣는다: " + a.timeline)
    try:
        at, frames = tc_to_frame(a.at, fps), round(a.seconds * fps)
    except ValueError as e:
        sys.exit(str(e))
    r = put_text(resolve, project, tl, fps, TEXT_TRACK, TEXT_TEMPLATE, at, frames, text_inputs(a.text, FONT, a.style, a.size, a.x, a.y))
    track, kept, added, font = r["track"], r["kept"], r["added"], (FONT, a.style)
    still = "-"
    if a.out:
        os.makedirs(os.path.join(a.out, "hook-stills"), exist_ok=True)
        still = os.path.join(a.out, "hook-stills", "text_%s.jpg" % a.at.replace(":", "_"))
        resolve.OpenPage("color")
        tl.SetCurrentTimecode(frame_to_tc(at + frames // 2, fps))
        time.sleep(1)
        if not project.ExportCurrentFrameAsStill(still):
            still = "확인 필요: 스틸 내보내기 실패"
    ok = kept and not added
    L = ["## 훅 텍스트", "", "| 타임라인 | 시작 TC | 길이(초) | 트랙 | 클립 | 문구 | 글꼴 | Size | Center | 기존 클립·마커·타임라인 길이 | 새 컴파운드 클립·타임라인 | 스틸 | 결과 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
         "| %s | %s | %.1f | V%d %s | Text+ 1개 | %s | %s %s | %s | %s, %s | %s | %s | %s | %s |" % (
             a.timeline, a.at, frames / fps, track, TEXT_TRACK, a.text, font[0], font[1], a.size, a.x, a.y,
             "그대로" if kept else "확인 필요: 바뀜", "없음" if not added else "확인 필요: 미디어 풀 항목 %+d" % added, still, "적용" if ok else "확인 필요")]
    write_log(a.out, "searchhook-text", stamp, "\n".join(L) + "\n")
    if not ok:
        sys.exit(1)


def selftest():
    assert tc_to_frame("01:00:00:00", 24) == 86400 and frame_to_tc(86448, 24) == "01:00:02:00"
    assert frame_to_tc(tc_to_frame("00:59:59:29", 30), 30) == "00:59:59:29"
    rows = plan(["01:00:25:00-01:00:27:00=절정", "01:00:41:16-01:00:44:16"], "01:00:00:00", 1440, 24, 45)
    assert [(r["name"], r["start"], r["end"], r["record"]) for r in rows] == [("절정", 600, 648, 0), ("H2", 1000, 1072, 48)], rows
    for bad, fps in ((["01:00:59:00-01:01:01:00"], 24), (["01:00:02:00-01:00:02:00"], 24), (["00:59:59:00-01:00:01:00"], 24),
                     (["01:00:00:00-01:00:50:00"], 24), (["01:00:00:00"], 24), (["01:00:00;00-01:00:01;00"], 30), ([], 24)):
        try:
            plan(bad, "01:00:00:00", 1440, fps, 45)
        except ValueError:
            continue
        raise AssertionError("통과하면 안 되는 구간: %s" % bad)
    assert chapter_fix([720, 1320], 720, 24) == "intro"  # 30초 훅: 0프레임에 인트로 챕터
    assert chapter_fix([120, 720], 120, 24) == "move"  # 5초 훅: 첫 챕터를 0프레임으로
    assert chapter_fix([], 720, 24) is None and chapter_fix([0, 720], 720, 24) is None and chapter_fix([130], 120, 24) is None
    lay = {("video", 1): [(0, 480), (480, 480)], ("audio", 2): [(100, 240)]}
    assert expected(lay, 200, {("audio", 2)}) == {("video", 1): [(200, 480), (680, 480)], ("audio", 2): [(100, 240)]}
    rows = bgm_rows([(500, 400, 0), (0, 500, 300)], 200, 1160)
    assert [(s, e) for s, e, _ in rows] == [(0, 500), (500, 900)] and "+200프레임 ripple" in rows[0][2] and "60프레임 짧음" in rows[1][2], rows
    assert "100프레임뿐" in bgm_rows([(0, 500, 100)], 200, 700)[0][2]
    assert free_frame(0, 48, {0, 1}) == 2 and free_frame(0, 2, {0, 1}) is None
    assert same_value(1.2000000001, 1.2) and same_value(1, 1.0) and not same_value(None, 1.2) and not same_value("Arial", "Pretendard")
    assert text_inputs("a\\nb", "F", "Bold", 0.12, 0.5, 0.2)[0] == ("StyledText", "a\nb")
    assert clash(100, 50, [(0, 100), (150, 10)]) == [] and clash(100, 50, [(60, 41), (149, 5), (110, 10)]) == [(60, 41), (149, 5), (110, 10)]
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    inv = sub.add_parser("inventory")
    inv.add_argument("--timeline", required=True, help="완성된 작업 타임라인 B 이름")
    inv.add_argument("--out", required=True, help="로그와 hook-stills/를 쓸 폴더")
    inv.add_argument("--step", type=float, default=0, help="클립 안에서 이 초 간격으로 스틸. 기본은 클립 중간 1장")
    inv.add_argument("--no-stills", action="store_true")
    b = sub.add_parser("build")
    b.add_argument("--timeline", required=True, help="완성된 작업 타임라인 B 이름")
    b.add_argument("--seg", action="append", default=[], help="IN-OUT[=이름]. B의 타임라인 타임코드, 재생 순서대로 반복")
    b.add_argument("--bgm-track", type=int, action="append", default=[], help="BGM 오디오 트랙 번호. 잠근 채 밀어 음악을 제자리에 둔다(반복 가능)")
    b.add_argument("--name", help="새 타임라인 이름. 기본 <B>_hook_<YYYYMMDD_HHMM>")
    b.add_argument("--out", help="로그를 쓸 폴더(없으면 stdout만)")
    b.add_argument("--max-seconds", type=int, default=45)
    b.add_argument("--dry-run", action="store_true")
    t = sub.add_parser("text")
    t.add_argument("--timeline", required=True, help="build로 만든 훅 타임라인 H 이름")
    t.add_argument("--at", required=True, help="텍스트 시작 타임코드(H 기준)")
    t.add_argument("--seconds", type=float, required=True)
    t.add_argument("--text", required=True, help="문구. 줄바꿈은 \\n")
    t.add_argument("--size", type=float, default=0.16)
    t.add_argument("--style", default="Bold")
    t.add_argument("--x", type=float, default=0.5)
    t.add_argument("--y", type=float, default=0.5)
    t.add_argument("--out", help="로그와 확인 스틸을 쓸 폴더(없으면 stdout만)")
    sub.add_parser("selftest")
    a = ap.parse_args()
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    {"inventory": inventory, "build": build, "text": text}.get(a.cmd, lambda *_: selftest())(a, stamp)


if __name__ == "__main__":
    main()
