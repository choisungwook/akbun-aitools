#!/usr/bin/env python3
"""미디어 풀의 영상 클립 전부를 촬영 시각순으로 나열한 새 타임라인을 만든다. DaVinci Resolve 21.1 외부 스크립팅 API만 쓴다.

  python3 chrono_timeline.py [--name NAME] [--folder BIN ...] [--offset PREFIX=SECONDS ...] [--out DIR] [--dry-run] [--selftest]

촬영 시각은 클립 메타데이터 Date Recorded(ISO), 없으면 Date Created(파일 생성 시각)다. 카메라 시계가 어긋나면 --offset으로
파일명 접두어별 초 단위 보정을 준다(예: --offset VID_=-37). 시각이 없는 클립은 맨 뒤에 이름순으로 붙이고 로그에 확인 필요로 남긴다.
"""
import argparse
import datetime as dt
import os
import re
import sys

FORMATS = ("%Y-%m-%dT%H:%M:%S%z", "%a %b %d %Y %H:%M:%S")


def parse_time(props):
    """클립 속성 dict -> (datetime 또는 None, 출처 키)."""
    for key in ("Date Recorded", "Date Created"):
        v = (props.get(key) or "").strip()
        for f in FORMATS:
            try:
                t = dt.datetime.strptime(v, f)
                return t.replace(tzinfo=None), key
            except ValueError:
                pass
    return None, ""


def offset_for(name, offsets):
    """파일명 접두어에 맞는 보정 초. 가장 긴 접두어 우선."""
    hit = [(p, s) for p, s in offsets.items() if name.startswith(p)]
    return max(hit, key=lambda x: len(x[0]))[1] if hit else 0


def order(clips, offsets):
    """clips: [{name, props}] -> 정렬된 목록. 각 항목에 time, source, offset, corrected가 붙는다."""
    for c in clips:
        t, src = parse_time(c["props"])
        c["time"], c["source"], c["offset"] = t, src, offset_for(c["name"], offsets)
        c["corrected"] = t + dt.timedelta(seconds=c["offset"]) if t else None
    timed = sorted((c for c in clips if c["corrected"]), key=lambda c: (c["corrected"], c["name"]))
    untimed = sorted((c for c in clips if not c["corrected"]), key=lambda c: c["name"])
    return timed + untimed


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


def video_clips(folder, only=None):
    """폴더를 재귀로 돌며 영상 클립(MediaPoolItem)을 모은다. only가 있으면 그 이름의 bin 아래만."""
    out = []
    if only is None or folder.GetName() in only:
        out += [c for c in folder.GetClipList() if "Video" in (c.GetClipProperty("Type") or "")]
        only_sub = None
    else:
        only_sub = only
    for sub in folder.GetSubFolderList():
        out += video_clips(sub, only_sub)
    return out


def table(ordered):
    L = ["| 순서 | 파일명 | 촬영 시각(보정 후) | 출처 | 보정(초) | 비고 |", "|---|---|---|---|---|---|"]
    for i, c in enumerate(ordered, 1):
        L.append("| %d | %s | %s | %s | %+d | %s |" % (i, c["name"], c["corrected"].strftime("%Y-%m-%d %H:%M:%S") if c["corrected"] else "없음",
                                                   c["source"] or "-", c["offset"], "" if c["corrected"] else "확인 필요: 촬영 시각 없음, 이름순으로 맨 뒤"))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", help="새 타임라인 이름. 기본 chrono_<YYYYMMDD_HHMM>")
    ap.add_argument("--folder", action="append", help="이 이름의 bin 아래 클립만(반복 가능). 기본 미디어 풀 전체")
    ap.add_argument("--offset", action="append", default=[], help="PREFIX=SECONDS. 예: VID_=-37")
    ap.add_argument("--out", help="로그를 쓸 폴더(없으면 stdout만)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    offsets = {}
    for o in a.offset:
        p, s = o.split("=", 1)
        offsets[p] = float(s)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M")
    name = a.name or "chrono_" + stamp

    resolve, project = connect()
    mp = project.GetMediaPool()
    items = video_clips(mp.GetRootFolder(), set(a.folder) if a.folder else None)
    if not items:
        sys.exit("영상 클립 없음")
    clips = [{"name": it.GetName(), "props": it.GetClipProperty(), "item": it} for it in items]
    ordered = order(clips, offsets)
    lines = ["## 2. 작업 타임라인(촬영 시간순)", "", "타임라인: `%s` (%s)" % (name, "dry-run, 만들지 않음" if a.dry_run else "생성"), "", table(ordered)]
    if not a.dry_run:
        for i in range(1, project.GetTimelineCount() + 1):
            if project.GetTimelineByIndex(i).GetName() == name:
                sys.exit("같은 이름의 타임라인이 이미 있음: " + name)
        tl = mp.CreateTimelineFromClips(name, [{"mediaPoolItem": c["item"]} for c in ordered])
        if not tl:
            sys.exit("타임라인 생성 실패")
        project.SetCurrentTimeline(tl)
        got = [it.GetName() for it in tl.GetItemListInTrack("video", 1)]
        want = [c["name"] for c in ordered]
        lines += ["", "검증: 타임라인 V1 순서 == 계획 순서 → %s (%d클립)" % ("일치" if got == want else "불일치", len(got))]
        if got != want:
            lines += ["", "실제 순서: " + ", ".join(got)]
    text = "\n".join(lines) + "\n"
    print(text)
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        path = os.path.join(a.out, "timeline-chrono_%s.md" % stamp)
        open(path, "w").write(text)
        print("로그:", path)


def selftest():
    P = lambda **k: {k2.replace("_", " "): v for k2, v in k.items()}
    clips = [
        {"name": "IMG_0002.MOV", "props": P(Date_Recorded="", Date_Created="Sat Sep 26 2026 18:19:29")},
        {"name": "VID_20260926_180154_052.mp4", "props": P(Date_Recorded="", Date_Created="Sat Sep 26 2026 18:01:54")},
        {"name": "IVDB4951.MOV", "props": P(Date_Recorded="2026-09-26T17:52:19+0900", Date_Created="Sat Sep 26 2026 17:52:19")},
        {"name": "NOTIME.MOV", "props": P(Date_Recorded="", Date_Created="")},
    ]
    o = order(clips, {})
    assert [c["name"] for c in o] == ["IVDB4951.MOV", "VID_20260926_180154_052.mp4", "IMG_0002.MOV", "NOTIME.MOV"], [c["name"] for c in o]
    assert o[0]["source"] == "Date Recorded" and o[1]["source"] == "Date Created" and o[3]["corrected"] is None
    o = order(clips, {"VID_": -1200})  # Insta360 시계가 20분 빠르면 앞으로 간다
    assert [c["name"] for c in o][:2] == ["VID_20260926_180154_052.mp4", "IVDB4951.MOV"]
    assert offset_for("VID_2026", {"VID_": 1, "VID_2026": 2, "IMG_": 3}) == 2
    assert "확인 필요" in table(o).splitlines()[-1]
    print("selftest ok")


if __name__ == "__main__":
    main()
