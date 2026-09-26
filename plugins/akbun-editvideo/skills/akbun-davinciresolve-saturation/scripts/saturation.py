#!/usr/bin/env python3
"""변환·대비 뒤의 라벨 SAT 노드에서, 시간대별 채도 대역보다 낮은 클립만 CDL Saturation으로 보충한다. 채도를 낮추지는 않는다.
DaVinci Resolve 21.1 외부 스크립팅 API. 측정·세션은 exposure_scope.py를 가져다 쓴다.

  python3 saturation.py --out DIR [--timeline NAME] [--sunrise 06:30 --sunset 18:30] [--dry-run] [--skip-missing] [--reset] [--selftest]

채도 측정: Resolve 출력 스틸을 320px로 줄여 픽셀마다 (max-min)을 구한 평균, 10비트 스케일.
"""
import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "akbun-davinciresolve-exposure", "scripts"))
import exposure_scope as X  # noqa: E402

KEYWORDS = ("sat",)
LUT_DIR = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT"
# 밝기별 채도 롤오프(Luminosity vs Saturation): 섀도·하이라이트의 채도를 줄여 중간톤이 색을 끌고 가게 한다
ROLLOFF = """// akbun-davinciresolve-saturation: lum-vs-sat rolloff. shadows<{lo} and highlights>{hi} fade to {floor}
__DEVICE__ float3 transform(int p_Width, int p_Height, int p_X, int p_Y, float p_R, float p_G, float p_B)
{{
    float lum = 0.2126f * p_R + 0.7152f * p_G + 0.0722f * p_B;
    float wlo = _saturatef(lum / {lo}f);
    float whi = _saturatef((1.0f - lum) / (1.0f - {hi}f));
    float w = {floor}f + (1.0f - {floor}f) * wlo * whi;
    return make_float3(lum + (p_R - lum) * w, lum + (p_G - lum) * w, lum + (p_B - lum) * w);
}}
"""
BANDS = {"밤": (30, 80), "아침": (50, 110), "낮": (60, 120), "오후": (60, 130), "저녁": (45, 100), "미상": (45, 130)}  # ponytail: 경험값(화면 전체 평균이라 낮다). 촬영 스타일에 맞춰 조정
MAX_SAT = 1.25  # 덜어내기. 실무 튜토리얼 세 편 모두 '조금만'
TOL = 8
NODE_HELP = ("SAT 라벨 노드 없음. Color 페이지에서 클립마다 변환·CONTRAST 뒤에 Append a Node로 빈 노드를 붙이고 "
             "Label Selected Node로 라벨 SAT를 단다. 라벨 없는 노드·기존 그레이드 노드에는 쓰지 않는다.")


def chroma(path, size=320):
    """평균 채도(max-min), 10비트."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im = im.resize((size, max(1, im.height * size // im.width)))
    px = list(im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata())
    return round(sum(max(p) - min(p) for p in px) / len(px) * 4)


def target_gain(c, lo):
    """대역 하한 미만이면 필요한 Saturation 배수, 아니면 1.0."""
    return 1.0 if c >= lo else min(MAX_SAT, lo / max(c, 1))


def cdl(node, sat):
    return dict(X.IDENTITY, NodeIndex=node, Saturation=round(sat, 4))


def rolloff_name(lo, hi, floor):
    return "akbun/akbun_lumsat_lo%d_hi%d_f%d.dctl" % (round(lo * 100), round(hi * 100), round(floor * 100))


def rolloff_text(lo, hi, floor):
    return ROLLOFF.format(lo="%.3f" % lo, hi="%.3f" % hi, floor="%.3f" % floor)


def zone_chroma(path, size=320):
    """(섀도<15%·하이라이트>85% 픽셀의 평균 채도, 중간톤 평균 채도), 10비트. 롤오프 검증용."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im = im.resize((size, max(1, im.height * size // im.width)))
    px = list(im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata())
    ext, mid = [], []
    for r, g, b in px:
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        (ext if lum < 38 or lum > 217 else mid).append(max(r, g, b) - min(r, g, b))
    return (round(sum(ext) / len(ext) * 4) if ext else 0, round(sum(mid) / len(mid) * 4) if mid else 0)


def write_log(out, clips, dry):
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M")
    L = ["## 4d. 채도", "", "측정: Resolve 출력 스틸 평균 채도(max-min), 10비트. 모드: " + ("dry-run" if dry else "적용"), "",
         "| 파일명 | 시작 TC | 시간대 | 대역 | 채도 전→후 | 양끝/중간 채도 전→후 | 조정 | 판정 |", "|---|---|---|---|---|---|---|---|"]
    for c in clips:
        lo, hi = BANDS[c["bucket"]]
        zb, za = c.get("zones_before"), c.get("zones_after")
        L.append("| %s | %s | %s | %d~%d | %d→%s | %s | %s | %s |" % (c["name"], c["tc"], c["bucket"], lo, hi, c["before"], c.get("after", "-"),
                                                          ("%d/%d→%s" % (zb[0], zb[1], "%d/%d" % za if za else "-")) if zb else "-", c.get("adj", "-"), c.get("result", "-")))
    path = os.path.join(out, "saturation_%s.md" % stamp)
    open(path, "w").write("\n".join(L) + "\n")
    json.dump([{k: v for k, v in c.items() if k != "item"} for c in clips], open(os.path.join(out, "saturation_%s.json" % stamp), "w"), ensure_ascii=False, indent=1)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--timeline")
    ap.add_argument("--track", type=int, default=1)
    ap.add_argument("--sunrise", default="06:30")
    ap.add_argument("--sunset", default="18:30")
    ap.add_argument("--rolloff", action="store_true", help="섀도·하이라이트 채도 롤오프 DCTL을 SAT 노드 LUT에 건다")
    ap.add_argument("--rolloff-lo", type=float, default=0.15)
    ap.add_argument("--rolloff-hi", type=float, default=0.85)
    ap.add_argument("--rolloff-floor", type=float, default=0.6, help="양끝에서 남기는 채도 비율")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-missing", action="store_true")
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.out:
        ap.error("--out 필요")
    sr, ss = (int(a.sunrise[:2]) + int(a.sunrise[3:]) / 60), (int(a.sunset[:2]) + int(a.sunset[3:]) / 60)

    resolve, project = X.connect()
    tl = X.pick_timeline(project, a.timeline)
    sess = X.Session(resolve, project, tl, a.out)
    clips = []
    for it in tl.GetItemListInTrack("video", a.track):
        if it.GetType() != "video" or not it.GetClipEnabled():
            continue
        mpi = it.GetMediaPoolItem()
        r = X.labeled_node(it, mpi, KEYWORDS)
        hour = X.hour_of(mpi)
        clips.append({"i": len(clips), "item": it, "name": it.GetName(), "start": int(it.GetStart()), "end": int(it.GetEnd()), "tc": sess.tc(it.GetStart()),
                      "hour": hour, "bucket": X.bucket(hour, sr, ss), "node": r[0] if r else None})
    missing = [c["name"] for c in clips if c["node"] is None]
    if a.reset:
        for c in clips:
            if c["node"]:
                c["item"].SetCDL(dict(X.IDENTITY, NodeIndex=c["node"]))
                c["item"].GetNodeGraph().SetLUT(c["node"], "")
        print("reset", len(clips) - len(missing))
        return
    if missing and not a.dry_run and not a.skip_missing:
        sys.exit(NODE_HELP + "\n대상: " + ", ".join(missing))
    rel = rolloff_name(a.rolloff_lo, a.rolloff_hi, a.rolloff_floor)
    if a.rolloff and not a.dry_run:
        os.makedirs(os.path.join(LUT_DIR, "akbun"), exist_ok=True)
        open(os.path.join(LUT_DIR, rel), "w").write(rolloff_text(a.rolloff_lo, a.rolloff_hi, a.rolloff_floor))
        project.RefreshLUTList()
    for c in clips:
        mid = (c["start"] + c["end"]) // 2
        name = "%03d_before_mid" % c["i"]
        sess.grab(mid, name)
        c["before"] = chroma(os.path.join(a.out, "stills", name + ".jpg"))
        c["zones_before"] = zone_chroma(os.path.join(a.out, "stills", name + ".jpg"))
        lo, hi = BANDS[c["bucket"]]
        gain = target_gain(c["before"], lo)
        if c["node"] is None:
            c["result"] = "확인 필요: SAT 노드 없음"
            continue
        if gain == 1.0:
            c["adj"], c["after"], c["result"] = "없음", c["before"], "통과" if c["before"] <= hi else "통과(대역 위, 낮추지 않음)"
            continue
        if a.dry_run:
            c["result"] = "적용 예정 Saturation %.3f" % gain
            continue
        for _ in range(2):  # 측정 채도는 Saturation에 거의 비례. 한 번 보정
            c["item"].SetCDL(cdl(c["node"], gain))
            name = "%03d_after_mid" % c["i"]
            sess.grab(mid, name)
            c["after"] = chroma(os.path.join(a.out, "stills", name + ".jpg"))
            if c["after"] >= lo - TOL or gain >= MAX_SAT:
                break
            gain = min(MAX_SAT, gain * lo / max(c["after"], 1))
        c["adj"] = "노드%d Saturation %.3f" % (c["node"], gain)
        c["result"] = "통과" if c["after"] >= lo - TOL else "확인 필요: 상한 %.1f로도 대역 미달" % MAX_SAT
    if a.rolloff and not a.dry_run:
        for c in clips:
            if c["node"] is None:
                continue
            g = c["item"].GetNodeGraph()
            okset = g.SetLUT(c["node"], rel)
            name = "%03d_rolloff_mid" % c["i"]
            sess.grab((c["start"] + c["end"]) // 2, name)
            c["zones_after"] = zone_chroma(os.path.join(a.out, "stills", name + ".jpg"))
            c["adj"] = (c.get("adj") or "") + " + 롤오프 " + rel
            if not okset or os.path.basename(rel) not in (g.GetLUT(c["node"]) or "") or c["zones_after"][0] > c["zones_before"][0]:
                c["result"] = "확인 필요: 롤오프 LUT 미적용(SetLUT=%s) 또는 양끝 채도 감소 없음 %s→%s" % (okset, c["zones_before"], c["zones_after"])
    print("로그:", write_log(a.out, clips, a.dry_run))
    if missing:
        print(NODE_HELP + "\n대상: " + ", ".join(missing))


def selftest():
    from PIL import Image
    import tempfile
    p = os.path.join(tempfile.mkdtemp(), "t.png")
    Image.new("RGB", (40, 40), (120, 100, 80)).save(p)
    assert chroma(p) == 160
    assert target_gain(80, 90) == 90 / 80 and target_gain(100, 90) == 1.0 and target_gain(10, 90) == MAX_SAT and BANDS["오후"] == (60, 130)
    assert cdl(4, 1.25)["Saturation"] == 1.25 and cdl(4, 1.25)["Slope"] == "1 1 1"
    assert rolloff_name(0.15, 0.85, 0.6) == "akbun/akbun_lumsat_lo15_hi85_f60.dctl"
    t = rolloff_text(0.15, 0.85, 0.6)
    assert "0.150f" in t and "0.850f" in t and "__DEVICE__ float3 transform" in t
    im = Image.new("RGB", (40, 40), (120, 100, 80))
    for x in range(40):
        for y in range(20):
            im.putpixel((x, y), (20, 10, 5))  # 어두운 절반
    im.save(p)
    assert zone_chroma(p)[0] == 60 and 158 <= zone_chroma(p)[1] <= 160
    print("selftest ok")


if __name__ == "__main__":
    main()
