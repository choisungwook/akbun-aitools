#!/usr/bin/env python3
"""클립마다 Log 촬영 여부를 근거로 판정(Log / 비Log / 미확인)하고, Log로 확인된 클립에만 라벨 CST(또는 LUT) 노드에
Log → Rec.709 변환 LUT를 건다. DaVinci Resolve 21.1 외부 스크립팅 API(Graph.SetLUT). 측정·세션은 exposure_scope.py를 가져다 쓴다.

  python3 logconvert.py --out DIR [--timeline NAME] --lut "PROFILE=LUT상대경로" [--profile "접두어=PROFILE"] [--dry-run] [--skip-missing] [--selftest]

판정 근거(우선순위): 사용자 지정(--profile) > Resolve 클립 속성 Input Color Space/Gamma에 'log' > ffprobe color_transfer에 'log'
> 8비트 소스는 비Log(Apple Log·I-Log는 10비트) > 그 밖은 미확인. BT.709 태그와 화면 외관은 근거로 쓰지 않는다.
"""
import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "akbun-davinciresolve-exposure", "scripts"))
import exposure_scope as X  # noqa: E402

KEYWORDS = ("cst", "lut")
NODE_HELP = ("CST 라벨 노드 없음. Color 페이지에서 Log 클립마다 Color → Nodes → Append a Node(또는 EXPOSURE·WB 뒤에 Add Serial Node)로 "
             "빈 노드를 붙이고 Label Selected Node로 라벨 CST를 단다. 라벨 없는 노드·기존 그레이드 노드에는 쓰지 않는다.")


# ---------- 순수 계산 ----------
def ffprobe_video(path):
    """{pix_fmt, color_transfer} 또는 {} (ffprobe 없음/실패)."""
    if not path or not shutil.which("ffprobe") or not os.path.exists(path):
        return {}
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=pix_fmt,color_transfer", "-of", "json", path],
                             capture_output=True, text=True, timeout=30).stdout
        return (json.loads(out).get("streams") or [{}])[0]
    except Exception:
        return {}


def detect(name, props, probe, declared):
    """-> (판정, 프로파일, 근거). 판정은 'Log' | '비Log' | '미확인'."""
    for prefix, profile in sorted(declared.items(), key=lambda kv: -len(kv[0])):
        if name.startswith(prefix):
            return "Log", profile, "사용자 지정 --profile %s=" % prefix
    cs, gm = (props.get("Input Color Space") or ""), (props.get("Input Gamma") or "")
    if "log" in cs.lower() or "log" in gm.lower():
        return "Log", cs if "log" in cs.lower() else gm, "Resolve 클립 속성 Input Color Space/Gamma"
    tr = (probe.get("color_transfer") or "").lower()
    if "log" in tr:
        return "Log", tr, "ffprobe color_transfer"
    pix = probe.get("pix_fmt") or ""
    if pix and not any(b in pix for b in ("10", "12", "16")):
        return "비Log", "", "8비트 소스(%s). Apple Log·I-Log는 10비트" % pix
    return "미확인", "", "근거 없음(BT.709 태그·외관은 근거 아님)"


def image_diff(p1, p2):
    """두 스틸의 평균 절대 차이(8비트). 같은 LUT를 다시 걸면 0이다."""
    from PIL import Image, ImageChops
    h = ImageChops.difference(Image.open(p1).convert("RGB"), Image.open(p2).convert("RGB")).convert("L").histogram()
    return sum(i * c for i, c in enumerate(h)) / max(1, sum(h))


def lut_for(profile, luts):
    """프로파일 이름에 맞는 LUT 상대경로. 키가 프로파일에 포함되면 맞는 것으로 본다(대소문자 무시)."""
    p = profile.lower()
    hit = [(k, v) for k, v in luts.items() if k.lower() in p or p in k.lower()]
    return max(hit, key=lambda kv: len(kv[0]))[1] if hit else None


def parse_pairs(items):
    d = {}
    for s in items or []:
        k, v = s.split("=", 1)
        d[k.strip()] = v.strip()
    return d


# ---------- 실행 ----------
def write_log(out, clips, dry):
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M")
    L = ["## 5. LUT(Log 변환)", "", "모드: " + ("dry-run" if dry else "적용"), "",
         "| 파일명 | 시작 TC | 색공간/감마 | 비트 | 판정 | 근거 | 프로파일 | 노드/LUT | 중앙값 전→후 | 결과 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for c in clips:
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            c["name"], c["tc"], "%s / %s" % (c["cs"], c["gamma"]), c["pix"] or "-", c["verdict"], c["evidence"], c["profile"] or "-",
            ("노드%d %s" % (c["node"], c["lut"])) if c.get("lut") else "-", c.get("delta", "-"), c.get("result", "-")))
    path = os.path.join(out, "logconvert_%s.md" % stamp)
    open(path, "w").write("\n".join(L) + "\n")
    json.dump([{k: v for k, v in c.items() if k != "item"} for c in clips], open(os.path.join(out, "logconvert_%s.json" % stamp), "w"), ensure_ascii=False, indent=1)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--timeline")
    ap.add_argument("--track", type=int, default=1)
    ap.add_argument("--lut", action="append", help='"PROFILE=LUT 상대경로". 예: "Apple Log 2=Apple Log 2/65x/Eterna_iPh17_ALog2_G4_65x.cube"')
    ap.add_argument("--profile", action="append", help='"파일명 접두어=PROFILE". 메타데이터가 없는 카메라를 사용자가 지정. 예: "VID_=Insta360 I-Log"')
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-missing", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.out:
        ap.error("--out 필요")
    luts, declared = parse_pairs(a.lut), parse_pairs(a.profile)

    resolve, project = X.connect()
    tl = X.pick_timeline(project, a.timeline)
    sess = X.Session(resolve, project, tl, a.out)
    clips = []
    for it in tl.GetItemListInTrack("video", a.track):
        if it.GetType() != "video" or not it.GetClipEnabled():
            continue
        mpi = it.GetMediaPoolItem()
        props = mpi.GetClipProperty() if mpi else {}
        probe = ffprobe_video(props.get("File Path"))
        verdict, profile, evidence = detect(it.GetName(), props, probe, declared)
        r = X.labeled_node(it, mpi, KEYWORDS)
        c = {"i": len(clips), "item": it, "name": it.GetName(), "start": int(it.GetStart()), "end": int(it.GetEnd()), "tc": sess.tc(it.GetStart()),
             "cs": props.get("Input Color Space") or "", "gamma": props.get("Input Gamma") or "", "pix": probe.get("pix_fmt") or "",
             "verdict": verdict, "profile": profile, "evidence": evidence, "node": r[0] if r else None, "tools": r[2] if r else None}
        clips.append(c)
    targets = [c for c in clips if c["verdict"] == "Log"]
    missing = [c["name"] for c in targets if c["node"] is None]
    if missing and not a.dry_run and not a.skip_missing:
        sys.exit(NODE_HELP + "\n대상: " + ", ".join(missing))
    for c in clips:
        if c["verdict"] != "Log":
            c["result"] = "변환 안 함(%s)" % c["verdict"]
            continue
        if c["node"] is None:
            c["result"] = "확인 필요: CST 노드 없음"
            continue
        other_conv = any(t.startswith(X.CONV_TOOLS) for i, ts in enumerate(c["tools"]) if i != c["node"] - 1 for t in ts)
        if other_conv:
            c["result"] = "건너뜀: 다른 노드에 변환(LUT·CST) 있음"
            continue
        lut = lut_for(c["profile"], luts)
        if not lut:
            c["result"] = "확인 필요: 프로파일 '%s'에 맞는 --lut 없음" % c["profile"]
            continue
        c["lut"] = lut
        if a.dry_run:
            c["result"] = "적용 예정"
            continue
        nb, na = "%03d_before_mid" % c["i"], "%03d_after_mid" % c["i"]
        before = sess.grab((c["start"] + c["end"]) // 2, nb)["median"]
        g = c["item"].GetNodeGraph()
        okset = g.SetLUT(c["node"], lut)
        got = g.GetLUT(c["node"]) or ""
        after = sess.grab((c["start"] + c["end"]) // 2, na)["median"]
        diff = image_diff(os.path.join(a.out, "stills", nb + ".jpg"), os.path.join(a.out, "stills", na + ".jpg"))
        c["delta"] = "%d→%d (픽셀 차이 %.1f)" % (before, after, diff)
        c["result"] = "적용" if okset and os.path.basename(lut) in got and diff > 1.0 else "확인 필요: SetLUT=%s GetLUT=%s 픽셀 차이=%.1f" % (okset, got, diff)
    print("로그:", write_log(a.out, clips, a.dry_run))
    if missing:
        print(NODE_HELP + "\n대상: " + ", ".join(missing))


def selftest():
    P = lambda cs="", gm="": {"Input Color Space": cs, "Input Gamma": gm}
    assert detect("IVDB4951.MOV", P("Apple Log 2", "Apple Log"), {}, {})[0] == "Log"
    assert detect("VID_1.mp4", P("Rec.709 (Scene)", "Rec.709"), {"pix_fmt": "yuv420p10le", "color_transfer": "bt709"}, {}) == ("미확인", "", "근거 없음(BT.709 태그·외관은 근거 아님)")
    assert detect("VID_1.mp4", P("Rec.709 (Scene)"), {"pix_fmt": "yuv420p10le"}, {"VID_": "Insta360 I-Log"})[:2] == ("Log", "Insta360 I-Log")
    assert detect("IMG_1829.MOV", P("Rec.709 (Scene)"), {"pix_fmt": "yuv420p"}, {})[0] == "비Log"
    assert detect("X.MOV", P(), {}, {})[0] == "미확인"                       # ffprobe 없음 → 8비트 판정도 못 함
    luts = {"Apple Log 2": "Apple Log 2/65x/E.cube", "I-Log": "Luna_Ultra/L.cube"}
    assert lut_for("Apple Log 2", luts) == "Apple Log 2/65x/E.cube" and lut_for("Insta360 I-Log", luts) == "Luna_Ultra/L.cube" and lut_for("S-Log3", luts) is None
    assert parse_pairs(["VID_=Insta360 I-Log", "A = B"]) == {"VID_": "Insta360 I-Log", "A": "B"}
    print("selftest ok")


if __name__ == "__main__":
    main()
