#!/usr/bin/env python3
"""하늘(파란 색상 범위) 픽셀만 채도·밝기를 조정하는 DCTL을 만들어 라벨 SKY 노드에 LUT로 건다. 하늘이 3% 미만인 클립은 건드리지 않는다.
DaVinci Resolve 21.1 외부 스크립팅 API(Graph.SetLUT에 .dctl). 측정·세션은 exposure_scope.py를 가져다 쓴다.

  python3 sky.py --out DIR [--timeline NAME] [--sat-gain 1.25] [--lum-gain 0.9] [--hue 215] [--hue-width 40] [--dry-run] [--skip-missing] [--reset] [--selftest]

Qualifier·Power Window는 API가 없다. 대신 색상(hue)·채도로 가중치를 만드는 DCTL을 Resolve LUT 폴더 akbun/ 아래에 쓰고 노드에 건다.
"""
import argparse
import datetime as dt
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "akbun-davinciresolve-exposure", "scripts"))
import exposure_scope as X  # noqa: E402

KEYWORDS = ("sky",)
LUT_DIR = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT"
MIN_SHARE = 3.0      # 화면 위쪽 절반에서 하늘 픽셀 비율(%) 최소
SAT_MIN = 0.12       # 하늘 후보 최소 채도
NODE_HELP = ("SKY 라벨 노드 없음. Color 페이지에서 하늘이 있는 클립마다 변환·CONTRAST·SAT 뒤에 Append a Node로 빈 노드를 붙이고 "
             "Label Selected Node로 라벨 SKY를 단다. 라벨 없는 노드·기존 그레이드 노드에는 쓰지 않는다.")

DCTL = """// akbun-davinciresolve-sky: hue {hue} ±{hw}, sat gain {sg}, lum gain {lg}
__DEVICE__ float3 transform(int p_Width, int p_Height, int p_X, int p_Y, float p_R, float p_G, float p_B)
{{
    float mx = _fmaxf(p_R, _fmaxf(p_G, p_B));
    float mn = _fminf(p_R, _fminf(p_G, p_B));
    float d = mx - mn;
    float s = mx > 0.0f ? d / mx : 0.0f;
    float h = 0.0f;
    if (d > 0.0f) {{
        if (mx == p_R) h = 60.0f * ((p_G - p_B) / d);
        else if (mx == p_G) h = 60.0f * (2.0f + (p_B - p_R) / d);
        else h = 60.0f * (4.0f + (p_R - p_G) / d);
        if (h < 0.0f) h += 360.0f;
    }}
    float dh = _fabs(h - {hue}f);
    if (dh > 180.0f) dh = 360.0f - dh;
    float wh = _saturatef(1.0f - (dh - {hw}f * 0.5f) / ({hw}f * 0.5f));
    float ws = _saturatef((s - {smin}f) / {smin}f);
    float w = wh * ws;
    float lum = 0.2126f * p_R + 0.7152f * p_G + 0.0722f * p_B;
    float sg = 1.0f + ({sg}f - 1.0f) * w;
    float lg = 1.0f + ({lg}f - 1.0f) * w;
    float r = (lum + (p_R - lum) * sg) * lg;
    float g = (lum + (p_G - lum) * sg) * lg;
    float b = (lum + (p_B - lum) * sg) * lg;
    return make_float3(r, g, b);
}}
"""


def hue_of(r, g, b):
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d == 0:
        return 0.0, 0.0
    if mx == r:
        h = 60 * ((g - b) / d)
    elif mx == g:
        h = 60 * (2 + (b - r) / d)
    else:
        h = 60 * (4 + (r - g) / d)
    return (h + 360) % 360, d / mx


def sky_stats(path, hue, hw, size=320):
    """위쪽 절반에서 하늘 후보(색상 창 안, 채도 SAT_MIN 이상) -> {share, chroma, luma} 10비트."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im = im.resize((size, max(2, im.height * size // im.width)))
    w, h = im.size
    top = im.crop((0, 0, w, h // 2))
    px = list(top.get_flattened_data() if hasattr(top, "get_flattened_data") else top.getdata())
    n, cs, ls = 0, 0, 0
    for r, g, b in px:
        hh, s = hue_of(r, g, b)
        dh = abs(hh - hue)
        dh = 360 - dh if dh > 180 else dh
        if dh <= hw and s >= SAT_MIN:
            n += 1
            cs += max(r, g, b) - min(r, g, b)
            ls += 0.2126 * r + 0.7152 * g + 0.0722 * b
    share = round(n / len(px) * 100, 2)
    return {"share": share, "chroma": round(cs / n * 4) if n else 0, "luma": round(ls / n * 4) if n else 0}


def dctl_text(hue, hw, sg, lg):
    return DCTL.format(hue="%.1f" % hue, hw="%.1f" % hw, sg="%.3f" % sg, lg="%.3f" % lg, smin="%.3f" % SAT_MIN)


def dctl_name(hue, hw, sg, lg):
    return "akbun/akbun_sky_h%d_w%d_s%d_l%d.dctl" % (hue, hw, round(sg * 100), round(lg * 100))


def write_log(out, clips, dry):
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M")
    L = ["## 4e. 하늘", "", "측정: Resolve 출력 스틸 위쪽 절반의 하늘 후보 픽셀(색상 창·채도) 비율, 평균 채도·밝기(10비트). 모드: " + ("dry-run" if dry else "적용"), "",
         "| 파일명 | 시작 TC | 하늘% | 채도 전→후 | 밝기 전→후 | 조정 | 판정 |", "|---|---|---|---|---|---|---|"]
    for c in clips:
        b, a = c["before"], c.get("after")
        L.append("| %s | %s | %s | %d→%s | %d→%s | %s | %s |" % (c["name"], c["tc"], b["share"], b["chroma"], a["chroma"] if a else "-", b["luma"], a["luma"] if a else "-",
                                                         c.get("adj", "-"), c.get("result", "-")))
    path = os.path.join(out, "sky_%s.md" % stamp)
    open(path, "w").write("\n".join(L) + "\n")
    json.dump([{k: v for k, v in c.items() if k != "item"} for c in clips], open(os.path.join(out, "sky_%s.json" % stamp), "w"), ensure_ascii=False, indent=1)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--timeline")
    ap.add_argument("--track", type=int, default=1)
    ap.add_argument("--sat-gain", type=float, default=1.25)
    ap.add_argument("--lum-gain", type=float, default=0.9)
    ap.add_argument("--hue", type=float, default=215.0, help="하늘 색상 중심(도). 파랑 215")
    ap.add_argument("--hue-width", type=float, default=40.0, help="색상 창 전체 폭(도)")
    ap.add_argument("--min-share", type=float, default=MIN_SHARE, help="하늘 픽셀 최소 비율(%%). 기본 3")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-missing", action="store_true")
    ap.add_argument("--reset", action="store_true", help="SKY 노드의 LUT를 뗀다")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.out:
        ap.error("--out 필요")
    if not (0.5 <= a.sat_gain <= 2.0 and 0.5 <= a.lum_gain <= 1.5):
        ap.error("gain 범위: sat 0.5~2.0, lum 0.5~1.5")

    resolve, project = X.connect()
    tl = X.pick_timeline(project, a.timeline)
    sess = X.Session(resolve, project, tl, a.out)
    clips = []
    for it in tl.GetItemListInTrack("video", a.track):
        if it.GetType() != "video" or not it.GetClipEnabled():
            continue
        r = X.labeled_node(it, it.GetMediaPoolItem(), KEYWORDS)
        clips.append({"i": len(clips), "item": it, "name": it.GetName(), "start": int(it.GetStart()), "end": int(it.GetEnd()), "tc": sess.tc(it.GetStart()),
                      "node": r[0] if r else None})
    missing = [c["name"] for c in clips if c["node"] is None]
    if a.reset:
        for c in clips:
            if c["node"]:
                c["item"].GetNodeGraph().SetLUT(c["node"], "")
        print("reset", len(clips) - len(missing))
        return
    if missing and not a.dry_run and not a.skip_missing:
        sys.exit(NODE_HELP + "\n대상: " + ", ".join(missing))
    rel = dctl_name(a.hue, a.hue_width, a.sat_gain, a.lum_gain)
    if not a.dry_run:
        os.makedirs(os.path.join(LUT_DIR, "akbun"), exist_ok=True)
        open(os.path.join(LUT_DIR, rel), "w").write(dctl_text(a.hue, a.hue_width, a.sat_gain, a.lum_gain))
        project.RefreshLUTList()
    for c in clips:
        mid = (c["start"] + c["end"]) // 2
        name = "%03d_before_mid" % c["i"]
        sess.grab(mid, name)
        c["before"] = sky_stats(os.path.join(a.out, "stills", name + ".jpg"), a.hue, a.hue_width / 2)
        if c["before"]["share"] < a.min_share:
            c["result"] = "건너뜀: 하늘 %.1f%% 미만" % a.min_share
            continue
        if c["node"] is None:
            c["result"] = "확인 필요: SKY 노드 없음"
            continue
        if a.dry_run:
            c["result"] = "적용 예정 " + rel
            continue
        g = c["item"].GetNodeGraph()
        okset = g.SetLUT(c["node"], rel)
        got = g.GetLUT(c["node"]) or ""
        name = "%03d_after_mid" % c["i"]
        sess.grab(mid, name)
        c["after"] = sky_stats(os.path.join(a.out, "stills", name + ".jpg"), a.hue, a.hue_width / 2)
        c["adj"] = "노드%d %s" % (c["node"], rel)
        moved = (c["after"]["chroma"] - c["before"]["chroma"]) * (1 if a.sat_gain >= 1 else -1) >= 0 and c["after"] != c["before"]
        c["result"] = "통과" if okset and os.path.basename(rel) in got and moved else "확인 필요: SetLUT=%s GetLUT=%s 변화 없음" % (okset, got)
    print("로그:", write_log(a.out, clips, a.dry_run))
    if missing:
        print(NODE_HELP + "\n대상: " + ", ".join(missing))


def selftest():
    from PIL import Image
    import tempfile
    assert abs(hue_of(0, 0, 255)[0] - 240) < 1e-9 and abs(hue_of(255, 0, 0)[0]) < 1e-9 and hue_of(100, 100, 100) == (0.0, 0.0)
    im = Image.new("RGB", (40, 40), (60, 60, 60))
    for x in range(40):
        for y in range(0, 20):
            im.putpixel((x, y), (90, 140, 200))  # 하늘색 위쪽
    p = os.path.join(tempfile.mkdtemp(), "t.png")
    im.save(p)
    st = sky_stats(p, 215, 20)
    assert st["share"] == 100.0 and 438 <= st["chroma"] <= 440, st  # 위쪽 절반 전부 하늘(축소 보간 오차)
    st = sky_stats(p, 30, 20)
    assert st["share"] == 0.0
    t = dctl_text(215, 40, 1.25, 0.9)
    assert "__DEVICE__ float3 transform" in t and "215.0f" in t and "1.250f" in t and "{" not in t.replace("{{", "").replace("}}", "").split("transform")[0]
    assert dctl_name(215, 40, 1.25, 0.9) == "akbun/akbun_sky_h215_w40_s125_l90.dctl"
    print("selftest ok")


if __name__ == "__main__":
    main()
