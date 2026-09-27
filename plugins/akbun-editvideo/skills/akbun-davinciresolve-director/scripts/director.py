#!/usr/bin/env python3
"""타임라인을 읽어 화면 변화(컷·카드·글자·push)와 효과음의 짝, 효과음 없는 변화, 변화 없는 긴 구간, 분당 밀도를 표로 낸다.
타임라인은 바꾸지 않는다. 판정은 하지 않고 감독이 볼 곳만 표시한다. DaVinci Resolve 21.1 외부 스크립팅 API만 쓴다.

  python3 director.py audit --timeline B [--window-frames 3] [--still-seconds 8] [--main-track 1] [--out-dir DIR]
  python3 director.py selftest

효과음의 위치는 오디오 클립의 시작 프레임이다. 파일 앞에 여백이 있으면 들리는 어택은 그보다 늦다. 표의 오프셋이 작아도 귀로 다시 확인한다.
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "akbun-davinciresolve-searchhook", "scripts"))
import searchhook as SH  # noqa: E402

VISUAL = {"OVERLAY": "카드", "GFX": "그래픽", "SUBTITLE": "글자", "HOOK_TEXT": "글자"}
PUSH = "AKBUN_PUSH"


# ---------- 순수 함수 ----------
def pair(events, sounds, window):
    """events [(프레임, 종류, 이름)], sounds [프레임] -> (rows [(프레임, 종류, 이름, 오프셋 또는 None)], 짝 없는 sounds).
    오프셋은 소리 시작 - 화면 변화 시작(프레임). 음수면 소리가 먼저다. 한 소리는 가장 가까운 변화 하나와만 짝이 된다."""
    free, rows = sorted(sounds), []
    for frame, kind, name in sorted(events):
        near = min(free, key=lambda s: abs(s - frame), default=None)
        if near is not None and abs(near - frame) <= window:
            free.remove(near)
            rows.append((frame, kind, name, near - frame))
        else:
            rows.append((frame, kind, name, None))
    return rows, free


def still(changes, moving, start, end, limit):
    """changes [프레임]: 화면이 바뀌는 시점, moving [(시작, 끝)]: 본편이 움직이는 구간 -> 변화 없이 limit 프레임을 넘는 [(시작, 끝)]."""
    out, points = [], sorted(set([start, end] + [c for c in changes if start < c < end]))
    for a, b in zip(points, points[1:]):
        if b - a > limit and not any(s <= a and b <= e for s, e in moving):
            out.append((a, b))
    return out


def density(count, frames, fps):
    return count * 60 * fps / frames if frames else 0.0


# ---------- Resolve ----------
def audit(a, stamp):
    _, project = SH.connect()
    tl, fps, length = SH.open_source(project, a.timeline)
    origin, end = tl.GetStartFrame(), tl.GetEndFrame()
    video = {t: tl.GetTrackName("video", t) for t in range(1, tl.GetTrackCount("video") + 1)}
    audio = {t: tl.GetTrackName("audio", t) for t in range(1, tl.GetTrackCount("audio") + 1)}
    events, changes, moving = [], [], []
    for it in tl.GetItemListInTrack("video", a.main_track) or []:
        if not it.GetMediaPoolItem():
            continue
        changes.append(it.GetStart())
        if it.GetStart() > origin:
            events.append((it.GetStart(), "컷", it.GetName()))
        if PUSH in (it.GetFusionCompNameList() or []):
            moving.append((it.GetStart(), it.GetEnd()))
            events.append((it.GetStart(), "push", it.GetName()))
    # 본편 밖의 비디오 트랙은 이름과 관계없이 모두 화면 위 변화로 센다. 오래된 타임라인은 카드를 다른 이름의 트랙에 두기도 한다
    for t, name in video.items():
        if t != a.main_track:
            for it in tl.GetItemListInTrack("video", t) or []:
                events.append((it.GetStart(), VISUAL.get(name, "오버레이"), it.GetName()))
                changes += [it.GetStart(), it.GetEnd()]
    sfx_tracks = [t for t, name in audio.items() if name.upper().startswith("SFX")]
    sounds = [it.GetStart() for t in sfx_tracks for it in tl.GetItemListInTrack("audio", t) or []]
    rows, orphans = pair(events, sounds, a.window_frames)
    quiet = still(changes, moving, origin, end, round(a.still_seconds * fps))
    tc = lambda f: SH.frame_to_tc(f, fps)  # noqa: E731
    paired = [r for r in rows if r[3] is not None]
    L = ["## 연출 점검 %s" % a.timeline, "",
         "- 길이 %.1f초, 화면 변화 %d개(분당 %.1f), 효과음 %d개(분당 %.1f), 효과음 트랙 %s" % (
             length / fps, len(rows), density(len(rows), length, fps), len(sounds), density(len(sounds), length, fps),
             ", ".join("A%d %s" % (t, audio[t]) for t in sfx_tracks) or "없음(이름이 SFX로 시작하는 오디오 트랙)"),
         "- 효과음과 짝인 변화 %d개, 짝 없는 변화 %d개, 짝 없는 효과음 %d개, 짝 기준 ±%d프레임" % (len(paired), len(rows) - len(paired), len(orphans), a.window_frames),
         "", "### 화면 변화와 효과음", "", "| TC | 종류 | 이름 | 효과음 오프셋(프레임) |", "|---|---|---|---|"]
    L += ["| %s | %s | %s | %s |" % (tc(f), kind, name, "없음" if off is None else "%+d" % off) for f, kind, name, off in rows]
    L += ["", "### 짝 없는 효과음", "", "| TC |", "|---|"] + (["| %s |" % tc(f) for f in orphans] or ["| 없음 |"])
    L += ["", "### 변화 없이 %.0f초를 넘는 구간" % a.still_seconds, "", "| 시작 TC | 종료 TC | 길이(초) |", "|---|---|---|"]
    L += ["| %s | %s | %.1f |" % (tc(s), tc(e), (e - s) / fps) for s, e in quiet] or ["| 없음 | | |"]
    SH.write_log(a.out_dir, "director-audit", stamp, "\n".join(L) + "\n")


def selftest():
    events = [(100, "컷", "a"), (148, "카드", "b"), (300, "글자", "c")]
    rows, orphans = pair(events, [98, 150, 500], 3)
    assert rows == [(100, "컷", "a", -2), (148, "카드", "b", 2), (300, "글자", "c", None)] and orphans == [500], (rows, orphans)
    rows, orphans = pair([(100, "컷", "a"), (102, "카드", "b")], [101], 3)
    assert [r[3] for r in rows] == [1, None] and orphans == []  # 한 소리는 한 변화와만 짝
    assert pair([], [10], 3) == ([], [10])
    assert still([100, 200, 500], [], 0, 700, 192) == [(200, 500), (500, 700)]
    assert still([100, 200, 500], [(200, 500)], 0, 700, 192) == [(500, 700)]  # push 구간은 움직이는 것으로 본다
    assert still([], [], 0, 100, 192) == []
    assert abs(density(12, 24 * 60, 24) - 12) < 1e-9 and density(3, 0, 24) == 0.0
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("audit")
    p.add_argument("--timeline", required=True, help="작업 타임라인 이름")
    p.add_argument("--window-frames", type=int, default=3, help="화면 변화와 효과음을 짝으로 보는 최대 차이")
    p.add_argument("--still-seconds", type=float, default=8.0, help="변화 없는 구간으로 표시할 길이")
    p.add_argument("--main-track", type=int, default=1, help="본편 비디오 트랙 번호")
    p.add_argument("--out-dir", help="표를 쓸 폴더(없으면 stdout만)")
    sub.add_parser("selftest")
    a = ap.parse_args()
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    audit(a, stamp) if a.cmd == "audit" else selftest()


if __name__ == "__main__":
    main()
