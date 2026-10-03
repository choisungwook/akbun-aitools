#!/usr/bin/env python3
"""색보정 workflow의 보조 스크립트. 타임라인 복제, 트랙 준비, 클립별 라벨 노드 준비 상태 점검만 한다.
색보정 자체는 각 skill의 스크립트가 한다. 측정·세션·노드 규칙은 exposure_scope.py를 가져다 쓴다.

  python3 workflow.py duplicate --src "<타임라인 A>" [--name "<작업 타임라인>"]
  python3 workflow.py tracks --timeline "<작업 타임라인>" [--out DIR]
  python3 workflow.py nodes --timeline "<작업 타임라인>" [--profile "VID_=Insta360 I-Log"] [--out DIR]

tracks: 비디오 트랙 3개와 오디오 트랙 3개를 더하고 역할 이름을 붙인다. 이미 그 이름의 트랙이 있으면 더하지 않는다.
nodes: 클립마다 필요한 라벨(EXPOSURE, WB, CST(Log만), CONTRAST, SAT)과 현재 라벨을 비교해 빠진 것을 표로 낸다.
"""
import argparse
import datetime as dt
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "akbun-davinciresolve-exposure", "scripts"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "akbun-davinciresolve-logconvert", "scripts"))
import exposure_scope as X  # noqa: E402
import logconvert as LC  # noqa: E402

ORDER = [("EXPOSURE", ("exposure",)), ("WB", ("wb", "white")), ("CST", ("cst", "lut")), ("CONTRAST", ("contrast",)), ("SAT", ("sat",))]

# 아래에서 위 순서. 자막은 영상·그래픽 위에 온다
TRACKS = {"video": ["OVERLAY", "GFX", "SUBTITLE"], "audio": ["AMBIENCE", "SFX", "MUSIC"]}


def lacking(have, want):
    """현재 트랙 이름 목록에 없는 필요 이름. 순서는 want를 따른다."""
    return [n for n in want if n not in have]


def required(verdict):
    """클립의 Log 판정에 따라 필요한 라벨 순서."""
    return [name for name, _ in ORDER if name != "CST" or verdict == "Log"]


def missing(labels, need):
    """현재 라벨 목록(소문자)에서 빠진 필요 라벨."""
    keys = dict(ORDER)
    return [n for n in need if not any(any(k in l for k in keys[n]) for l in labels)]


def order_ok(labels, need):
    """필요 라벨이 있는 노드들이 필요 순서대로 놓였는지."""
    keys = dict(ORDER)
    pos = []
    for n in need:
        idx = [i for i, l in enumerate(labels) if any(k in l for k in keys[n])]
        if idx:
            pos.append(idx[0])
    return pos == sorted(pos)


def cmd_duplicate(a):
    resolve, project = X.connect()
    src = X.pick_timeline(project, a.src)
    name = a.name or "%s_edit_%s" % (a.src, dt.datetime.now().strftime("%Y%m%d_%H%M"))
    for i in range(1, project.GetTimelineCount() + 1):
        if project.GetTimelineByIndex(i).GetName() == name:
            sys.exit("같은 이름의 타임라인이 이미 있음: " + name)
    new = src.DuplicateTimeline(name)
    if not new:
        sys.exit("복제 실패")
    project.SetCurrentTimeline(new)
    print("작업 타임라인:", new.GetName(), "클립", len(new.GetItemListInTrack("video", 1)))


def cmd_tracks(a):
    resolve, project = X.connect()
    tl = X.pick_timeline(project, a.timeline)
    project.SetCurrentTimeline(tl)
    names = lambda kind: [tl.GetTrackName(kind, t) for t in range(1, tl.GetTrackCount(kind) + 1)]
    added = []
    for kind, want in TRACKS.items():
        for name in lacking(names(kind), want):
            if not (tl.AddTrack(kind, "stereo") if kind == "audio" else tl.AddTrack(kind)):
                sys.exit("트랙 추가 실패: " + name)
            tl.SetTrackName(kind, tl.GetTrackCount(kind), name)
            added.append(name)
    rows = ["| 트랙 | 이름 | 클립 수 | 이번에 추가 |", "|---|---|---|---|"]
    for kind in TRACKS:
        for t, name in enumerate(names(kind), 1):
            rows.append("| %s%d | %s | %d | %s |" % (kind[0].upper(), t, name, len(tl.GetItemListInTrack(kind, t) or []), "예" if name in added else "-"))
    lack = [n for kind, want in TRACKS.items() for n in lacking(names(kind), want)]
    text = "## 트랙 준비\n\n타임라인: `%s`, 빠진 트랙 %d개%s\n\n%s\n" % (tl.GetName(), len(lack), " (%s)" % ", ".join(lack) if lack else "", "\n".join(rows))
    print(text)
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        p = os.path.join(a.out, "track-plan_%s.md" % dt.datetime.now().strftime("%Y%m%d_%H%M"))
        open(p, "w").write(text)
        print("로그:", p)
    sys.exit(1 if lack else 0)


def cmd_nodes(a):
    resolve, project = X.connect()
    tl = X.pick_timeline(project, a.timeline)
    declared = LC.parse_pairs(a.profile)
    rows = ["| 파일명 | 시작 TC | Log 판정 | 필요 라벨(순서) | 현재 라벨 | 빠진 라벨 | 순서 |", "|---|---|---|---|---|---|---|"]
    lack = 0
    fps = float(tl.GetSetting("timelineFrameRate"))
    for it in tl.GetItemListInTrack("video", a.track):
        if it.GetType() != "video" or not it.GetClipEnabled():
            continue
        mpi = it.GetMediaPoolItem()
        props = mpi.GetClipProperty() if mpi else {}
        verdict = LC.detect(it.GetName(), props, LC.ffprobe_video(props.get("File Path")), declared)[0]
        g = it.GetNodeGraph()
        labels = [(g.GetNodeLabel(i) or "") for i in range(1, g.GetNumNodes() + 1)]
        need = required(verdict)
        miss = missing([l.lower() for l in labels], need)
        ok = order_ok([l.lower() for l in labels], need)
        lack += bool(miss) or not ok
        f = int(it.GetStart()); fi = int(round(fps)); s = f // fi
        tc = "%02d:%02d:%02d:%02d" % (s // 3600, (s // 60) % 60, s % 60, f % fi)
        rows.append("| %s | %s | %s | %s | %s | %s | %s |" % (it.GetName(), tc, verdict, " → ".join(need), ", ".join(l or "(없음)" for l in labels), ", ".join(miss) or "-", "OK" if ok else "어긋남"))
    text = "## 노드 준비 상태\n\n타임라인: `%s`, 준비 안 된 클립 %d개\n\n%s\n" % (tl.GetName(), lack, "\n".join(rows))
    print(text)
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        p = os.path.join(a.out, "node-plan_%s.md" % dt.datetime.now().strftime("%Y%m%d_%H%M"))
        open(p, "w").write(text)
        print("로그:", p)
    sys.exit(1 if lack else 0)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    d = sp.add_parser("duplicate"); d.add_argument("--src", required=True); d.add_argument("--name")
    n = sp.add_parser("nodes"); n.add_argument("--timeline"); n.add_argument("--track", type=int, default=1)
    n.add_argument("--profile", action="append"); n.add_argument("--out")
    t = sp.add_parser("tracks"); t.add_argument("--timeline"); t.add_argument("--out")
    s = sp.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    {"duplicate": cmd_duplicate, "tracks": cmd_tracks, "nodes": cmd_nodes}[a.cmd](a)


def selftest():
    assert required("Log") == ["EXPOSURE", "WB", "CST", "CONTRAST", "SAT"]
    assert required("비Log") == ["EXPOSURE", "WB", "CONTRAST", "SAT"]
    assert missing(["exposure", "wb", "03_cst"], required("Log")) == ["CONTRAST", "SAT"]
    assert order_ok(["exposure", "wb", "cst", "contrast", "sat"], required("Log"))
    assert not order_ok(["cst", "exposure", "wb"], required("Log"))
    assert order_ok(["", "wb"], required("미확인"))  # 빠진 건 순서 판정에서 무시
    assert lacking(["Video 1"], TRACKS["video"]) == TRACKS["video"] and all(len(v) == 3 for v in TRACKS.values())
    assert lacking(["Audio 1", "SFX"], TRACKS["audio"]) == ["AMBIENCE", "MUSIC"]
    print("selftest ok")


if __name__ == "__main__":
    main()
