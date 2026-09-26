#!/usr/bin/env python3
"""변환 뒤의 라벨 CONTRAST 노드에 피벗 기준 대비(Contrast + Pivot)를 CDL로 건다. 클리핑이 생기면 대비를 줄여 다시 잰다.
DaVinci Resolve 21.1 외부 스크립팅 API. 측정·세션은 exposure_scope.py를 가져다 쓴다.

  python3 contrast.py --out DIR [--timeline NAME] [--contrast 1.15] [--pivot 0.435] [--dry-run] [--skip-missing] [--reset] [--selftest]

CDL로 표현한 피벗 대비: out = (in - pivot) * c + pivot  →  Slope = c, Offset = pivot * (1 - c). S 커브는 CDL로 만들 수 없어 하지 않는다.
"""
import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "akbun-davinciresolve-exposure", "scripts"))
import exposure_scope as X  # noqa: E402

KEYWORDS = ("contrast",)
CLIP_LO, CLIP_HI = 16, 1008   # p1이 이보다 낮거나 p99가 이보다 높으면 클리핑으로 본다
MAX_CONTRAST = 1.5
NODE_HELP = ("CONTRAST 라벨 노드 없음. Color 페이지에서 클립마다 변환(LUT·CST) 뒤에 Append a Node로 빈 노드를 붙이고 "
             "Label Selected Node로 라벨 CONTRAST를 단다. 라벨 없는 노드·기존 그레이드 노드에는 쓰지 않는다.")


def cdl(node, c, pivot):
    d = dict(X.IDENTITY, NodeIndex=node)
    d["Slope"] = "%.4f %.4f %.4f" % ((c,) * 3)
    d["Offset"] = "%.4f %.4f %.4f" % ((pivot * (1 - c),) * 3)
    return d


def spread(st):
    return st["p90"] - st["p10"]


def clipped(st):
    return st["p1"] < CLIP_LO or st["p99"] > CLIP_HI or st["clip_hi"] > X.CLIP_HI_MAX


def write_log(out, clips, dry):
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M")
    L = ["## 4c. 대비", "", "측정: Resolve 출력 스틸 휘도 p10~p90 폭(10비트). 모드: " + ("dry-run" if dry else "적용"), "",
         "| 파일명 | 시작 TC | p10~p90 전→후 | p1/p99 후 | 클리핑% 후 | 조정 | 판정 |", "|---|---|---|---|---|---|---|"]
    for c in clips:
        b, a = c["before"], c.get("after")
        L.append("| %s | %s | %d→%s | %s | %s | %s | %s |" % (
            c["name"], c["tc"], spread(b), spread(a) if a else "-", "%d/%d" % (a["p1"], a["p99"]) if a else "-", a["clip_hi"] if a else "-",
            c.get("adj", "-"), c.get("result", "-")))
    path = os.path.join(out, "contrast_%s.md" % stamp)
    open(path, "w").write("\n".join(L) + "\n")
    json.dump([{k: v for k, v in c.items() if k != "item"} for c in clips], open(os.path.join(out, "contrast_%s.json" % stamp), "w"), ensure_ascii=False, indent=1)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--timeline")
    ap.add_argument("--track", type=int, default=1)
    ap.add_argument("--contrast", type=float, default=1.15)
    ap.add_argument("--pivot", type=float, default=0.435, help="Rec.709 18%% 회색 부호화값")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-missing", action="store_true")
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.out:
        ap.error("--out 필요")
    if not 0.5 <= a.contrast <= MAX_CONTRAST:
        ap.error("--contrast는 0.5~%.1f" % MAX_CONTRAST)

    resolve, project = X.connect()
    tl = X.pick_timeline(project, a.timeline)
    sess = X.Session(resolve, project, tl, a.out)
    clips = []
    for it in tl.GetItemListInTrack("video", a.track):
        if it.GetType() != "video" or not it.GetClipEnabled():
            continue
        r = X.labeled_node(it, it.GetMediaPoolItem(), KEYWORDS)
        clips.append({"i": len(clips), "item": it, "name": it.GetName(), "start": int(it.GetStart()), "end": int(it.GetEnd()), "tc": sess.tc(it.GetStart()),
                      "node": r[0] if r else None, "before_conv": bool(r and r[1])})
    missing = [c["name"] for c in clips if c["node"] is None]
    if a.reset:
        for c in clips:
            if c["node"]:
                c["item"].SetCDL(dict(X.IDENTITY, NodeIndex=c["node"]))
        print("reset", len(clips) - len(missing))
        return
    if missing and not a.dry_run and not a.skip_missing:
        sys.exit(NODE_HELP + "\n대상: " + ", ".join(missing))
    for c in clips:
        mid = (c["start"] + c["end"]) // 2
        c["before"] = sess.grab(mid, "%03d_before_mid" % c["i"])
        if c["node"] is None:
            c["result"] = "확인 필요: CONTRAST 노드 없음"
            continue
        if c["before_conv"]:
            c["result"] = "확인 필요: 노드가 변환 앞에 있음(대비는 변환 뒤에서)"
            continue
        if a.dry_run:
            c["result"] = "적용 예정 c=%.2f" % a.contrast
            continue
        cval = a.contrast
        for _ in range(3):  # 클리핑이 생기면 대비를 10%씩 줄인다
            c["item"].SetCDL(cdl(c["node"], cval, a.pivot))
            st = sess.grab(mid, "%03d_after_mid" % c["i"])
            if not clipped(st) or cval <= 1.0:
                break
            cval = max(1.0, round(cval - 0.1 * (a.contrast - 1.0) / 0.3, 3)) if a.contrast > 1 else cval
            if cval == 1.0:
                c["item"].SetCDL(dict(X.IDENTITY, NodeIndex=c["node"]))
                st = sess.grab(mid, "%03d_after_mid" % c["i"])
                break
        c["after"] = st
        c["adj"] = "노드%d Slope %.3f Offset %.4f" % (c["node"], cval, a.pivot * (1 - cval))
        c["result"] = "통과" if not clipped(st) else "확인 필요: 클리핑"
        if cval != a.contrast:
            c["result"] += " (대비 %.2f→%.2f로 낮춤)" % (a.contrast, cval)
    print("로그:", write_log(a.out, clips, a.dry_run))
    if missing:
        print(NODE_HELP + "\n대상: " + ", ".join(missing))


def selftest():
    d = cdl(3, 1.2, 0.435)
    assert d["Slope"] == "1.2000 1.2000 1.2000" and d["Offset"] == "-0.0870 -0.0870 -0.0870" and d["NodeIndex"] == 3
    # 피벗은 고정점: (0.435 - 0.435) * c + 0.435 = 0.435
    assert abs((0.435 * 1.2 + 0.435 * (1 - 1.2)) - 0.435) < 1e-9
    assert spread({"p10": 100, "p90": 700}) == 600
    assert clipped({"p1": 8, "p99": 900, "clip_hi": 0}) and not clipped({"p1": 40, "p99": 950, "clip_hi": 0.1}) and clipped({"p1": 40, "p99": 1012, "clip_hi": 0})
    print("selftest ok")


if __name__ == "__main__":
    main()
