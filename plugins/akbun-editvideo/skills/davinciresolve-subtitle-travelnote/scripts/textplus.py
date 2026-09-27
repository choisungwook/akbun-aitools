#!/usr/bin/env python3
"""Text+ 자막을 이름으로 찾은 비디오 트랙(기본 SUBTITLE)에 일반 Text+ 클립 하나로 놓는다. 다른 트랙의 클립, 타임라인 마커, 타임라인 길이는 바뀌지 않는다.
DaVinci Resolve 21.1 외부 스크립팅 API만 쓴다.

  python3 textplus.py place --timeline B --at TC --seconds N --text "문구" --font "Gmarket Sans" --style Medium --size 0.12
                            [--x 0.5] [--y 0.5] [--set 입력=값 ...] [--track SUBTITLE] [--template HOOK_TEXT_TEMPLATE] [--out DIR]
  python3 textplus.py remove --timeline B --at TC [--track SUBTITLE]
  python3 textplus.py selftest

InsertFusionTitleIntoTimeline("Text+")은 항상 V1의 재생헤드에 끼워 넣는다(21.1 실측). 재생헤드 아래 V1 클립을 자르고
잠기지 않은 모든 트랙과 타임라인 마커를 타이틀 길이만큼 뒤로 민다. V1이 잠겨 있으면 아무것도 돌려주지 않는다. 트랙을 고르는 API는 없다.
그래서 place는 미디어 풀의 Fusion Title 항목(--template)을 대상 트랙의 원하는 위치와 길이로 놓고 글자 값을 넣는다.
놓는 함수는 akbun-davinciresolve-searchhook의 searchhook.py put_text다. 컴파운드 클립을 만들지 않으므로 놓인 자막은 Inspector에서 바로 고친다.
remove는 대상 트랙에서 --at에 시작하는 클립을 지운다. 컷 변경 뒤 다시 놓을 때 쓴다.
페이드는 넣지 않는다. TimelineItem.SetFades로 건 값은 프로젝트를 닫았다 열면 0으로 돌아온다(21.1 실측).
"""
import argparse
import datetime as dt
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "akbun-davinciresolve-searchhook", "scripts"))
import searchhook as SH  # noqa: E402

TRACK = "SUBTITLE"


def parse_set(pairs):
    """["LineSpacing=1.2", "Font=Pretendard"] -> [("LineSpacing", 1.2), ("Font", "Pretendard")]. 숫자로 읽히면 숫자."""
    out = []
    for p in pairs:
        key, sep, value = p.partition("=")
        if not sep or not key:
            raise ValueError("--set 형식은 입력=값: " + p)
        try:
            value = float(value)
        except ValueError:
            pass
        out.append((key, value))
    return out


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


def place(a, stamp):
    resolve, project, tl, fps, at = open_timeline(a)
    frames = round(a.seconds * fps)
    try:
        inputs = SH.text_inputs(a.text, a.font, a.style, a.size, a.x, a.y) + parse_set(a.set)
    except ValueError as e:
        sys.exit(str(e))
    r = SH.put_text(resolve, project, tl, fps, a.track, a.template, at, frames, inputs)
    still = "-"
    if a.out:
        os.makedirs(os.path.join(a.out, "subtitle-stills"), exist_ok=True)
        still = os.path.join(a.out, "subtitle-stills", "%s_%s.jpg" % (a.track, a.at.replace(":", "_")))
        resolve.OpenPage("color")
        tl.SetCurrentTimecode(SH.frame_to_tc(at + frames // 2, fps))
        time.sleep(1)
        if not project.ExportCurrentFrameAsStill(still):
            still = "확인 필요: 스틸 내보내기 실패"
    ok = r["kept"] and not r["added"]
    L = ["## Text+ 배치", "", "| 타임라인 | 시작 TC | 종료 TC | 트랙 | 문구 | 글꼴 | Size | Center | 기존 클립·마커·타임라인 길이 | 새 미디어 풀 항목 | 스틸 | 결과 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|",
         "| %s | %s | %s | V%d %s | %s | %s %s | %s | %s, %s | %s | %s | %s | %s |" % (
             a.timeline, a.at, SH.frame_to_tc(at + frames, fps), r["track"], a.track, a.text, a.font, a.style, a.size, a.x, a.y,
             "그대로" if r["kept"] else "확인 필요: 바뀜", "없음" if not r["added"] else "확인 필요: %+d" % r["added"], still, "적용" if ok else "확인 필요")]
    SH.write_log(a.out, "textplus", stamp, "\n".join(L) + "\n")
    if not ok:
        sys.exit(1)


def remove(a, stamp):
    _, _, tl, fps, at = open_timeline(a)
    track = next((t for t in range(2, tl.GetTrackCount("video") + 1) if tl.GetTrackName("video", t) == a.track), None)
    if not track:
        sys.exit("%s 트랙 없음" % a.track)
    before, marks = SH.layout(tl), tl.GetMarkers()
    # 핸들은 지우기 직전에 다시 읽는다(오래된 핸들로 지우면 Resolve가 종료됨, 21.1 실측)
    hit = [it for it in tl.GetItemListInTrack("video", track) or [] if it.GetStart() == at]
    if not hit:
        sys.exit("%s 트랙에 %s에서 시작하는 클립 없음" % (a.track, a.at))
    if not tl.DeleteClips(hit, False):
        sys.exit("삭제 실패: " + a.at)
    after = SH.layout(tl)
    gone = [x for x in before[("video", track)] if x not in after[("video", track)]]
    kept = all(after[k] == v for k, v in before.items() if k != ("video", track)) and tl.GetMarkers() == marks
    print("%s V%d %s: %s 클립 %d개 삭제, 다른 트랙·마커 %s" % (a.timeline, track, a.track, a.at, len(gone), "그대로" if kept else "확인 필요: 바뀜"))
    if len(gone) != 1 or not kept:
        sys.exit(1)


def selftest():
    assert parse_set(["LineSpacing=1.2", "Font=Noto Sans KR", "Enabled2=1"]) == [("LineSpacing", 1.2), ("Font", "Noto Sans KR"), ("Enabled2", 1.0)]
    for bad in ("LineSpacing", "=1"):
        try:
            parse_set([bad])
        except ValueError:
            continue
        raise AssertionError("통과하면 안 되는 --set: " + bad)
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("place")
    p.add_argument("--timeline", required=True, help="작업 타임라인 이름")
    p.add_argument("--at", required=True, help="글자 시작 타임코드")
    p.add_argument("--seconds", type=float, required=True)
    p.add_argument("--text", required=True, help="문구. 줄바꿈은 \\n")
    p.add_argument("--font", required=True)
    p.add_argument("--style", required=True, help="글꼴 굵기 이름. 예: Medium, Bold")
    p.add_argument("--size", type=float, required=True)
    p.add_argument("--x", type=float, default=0.5, help="Text+ Center X. 0 왼쪽 끝, 1 오른쪽 끝")
    p.add_argument("--y", type=float, default=0.5, help="Text+ Center Y. 0 아래 끝, 1 위 끝")
    p.add_argument("--set", action="append", default=[], help="그 밖의 Text+ 입력. 입력=값, 반복 가능")
    p.add_argument("--track", default=TRACK, help="놓을 비디오 트랙 이름. 없으면 맨 위에 만든다")
    p.add_argument("--template", default=SH.TEXT_TEMPLATE, help="미디어 풀의 Fusion Title 항목 이름")
    p.add_argument("--out", help="로그와 확인 스틸(subtitle-stills/)을 쓸 폴더(없으면 stdout만)")
    r = sub.add_parser("remove")
    r.add_argument("--timeline", required=True)
    r.add_argument("--at", required=True, help="지울 글자의 시작 타임코드")
    r.add_argument("--track", default=TRACK)
    sub.add_parser("selftest")
    a = ap.parse_args()
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    {"place": place, "remove": remove}.get(a.cmd, lambda *_: selftest())(a, stamp)


if __name__ == "__main__":
    main()
