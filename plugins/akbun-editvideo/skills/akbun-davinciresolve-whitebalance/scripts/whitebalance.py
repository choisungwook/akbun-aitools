#!/usr/bin/env python3
"""클립마다 중립(무채색) 픽셀의 R·G·B를 재서 시간대별 허용 색온도 안에서 화이트밸런스를 맞춘다.
DaVinci Resolve 21.1 외부 스크립팅 API + Pillow만 쓴다. 측정·노드·세션 코드는 akbun-davinciresolve-exposure의 exposure_scope.py를 가져다 쓴다.

  python3 whitebalance.py --out DIR [--timeline NAME] [--sunrise 06:30 --sunset 18:30] [--dry-run] [--reset] [--selftest]

조정은 Color 페이지에서 새로 만들고 라벨 WB를 단 노드에만 쓴다. 라벨 없는 노드에는 쓰지 않는다. Log 소스이고 변환(LUT·CST) 노드가 뒤에 있으면 채널별 Offset(로그 공간의
채널 오프셋 = 선형 게인), 아니면 채널별 Slope. G는 고정하고 R·B만 움직인다.
"""
import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "akbun-davinciresolve-exposure", "scripts"))
import exposure_scope as X  # noqa: E402  ponytail: 같은 plugin 안의 형제 skill을 직접 import. 분리 배포하면 복사한다

# ---------- 기준값 (SKILL.md 표와 같아야 한다) ----------
SKEW = {"밤": 0, "아침": 10, "낮": 0, "오후": 30, "저녁": -20, "미상": 0}  # 시간대별 중립 픽셀의 목표 R-B (10비트). 양수 = 따뜻하게 남김
TOL = 20            # 채널 차이 허용
MIN_SHARE = 0.5     # 중립 픽셀이 화면의 이 %보다 적으면 기준 없음
MAX_OFFSET, MAX_SLOPE = 0.10, 0.20   # 채널당 최대 변화(Offset 절대값 / Slope 1±)
IDENT = {"Offset": 0.0, "Slope": 1.0}
MARKER = ("Sky", "WB_CHECK", 6)
NODE_HELP = ("WB 라벨 노드 없음. Color 페이지에서 클립마다 Color → Nodes → Append a Node로 빈 노드를 붙이고 "
             "Color → Nodes → Label Selected Node로 라벨 WB를 단다(그레이드 없는 클립은 기본 노드에 라벨만). "
             "변환 앞에 두려면(Log 소스) Add Serial Before Current. 라벨 없는 노드·기존 그레이드 노드에는 쓰지 않는다.")


# ---------- 순수 계산 ----------
def neutral_rgb(path, size=320):
    """스틸 -> 중립 후보 픽셀(채도 낮고 중간 밝기)의 평균 {R,G,B}(10비트)와 share(%). 후보가 없으면 None."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im = im.resize((size, max(1, im.height * size // im.width)))
    acc = [0, 0, 0]
    n = 0
    px = list(im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata())
    for r, g, b in px:
        mx, mn = max(r, g, b), min(r, g, b)
        if 64 <= mx <= 217 and (mx - mn) <= 0.2 * mx:  # ponytail: 캐스트가 20%를 넘으면 중립 픽셀이 후보에서 빠진다. 그때는 기준 없음
            acc[0] += r; acc[1] += g; acc[2] += b; n += 1
    share = round(n / len(px) * 100, 2)
    if share < MIN_SHARE:
        return None
    return {"R": round(acc[0] / n * 4), "G": round(acc[1] / n * 4), "B": round(acc[2] / n * 4), "share": share}


def errors(rgb, skew):
    """목표 대비 R·B 오차. 목표: R-G = +skew/2, B-G = -skew/2."""
    return {"R": (rgb["R"] - rgb["G"]) - skew / 2, "B": (rgb["B"] - rgb["G"]) + skew / 2}


def ok(rgb, skew):
    e = errors(rgb, skew)
    return abs(e["R"]) <= TOL and abs(e["B"]) <= TOL


def first_guess(param, rgb, skew):
    e = errors(rgb, skew)
    if param == "Offset":
        return {"R": -e["R"] / 1700.0, "B": -e["B"] / 1700.0}  # ponytail: exposure_scope와 같은 실측 기울기
    return {"R": (rgb["R"] - e["R"]) / max(rgb["R"], 1), "B": (rgb["B"] - e["B"]) / max(rgb["B"], 1)}


def clamp(param, v):
    return max(-MAX_OFFSET, min(MAX_OFFSET, v)) if param == "Offset" else max(1 - MAX_SLOPE, min(1 + MAX_SLOPE, v))


def cdl(node, param, x):
    d = dict(X.IDENTITY, NodeIndex=node)
    g = IDENT[param]
    d[param] = "%.4f %.4f %.4f" % (x["R"], g, x["B"])
    return d


def wb_node_for(item, mpi):
    """라벨에 wb 또는 white가 들어간 노드만 쓴다. Log 소스이고 변환 앞이면 채널 Offset, 아니면 채널 Slope."""
    r = X.labeled_node(item, mpi, ("wb", "white"))
    return (None, None) if r is None else (r[0], "Offset" if r[1] else "Slope")


def verdict(c):
    flags = []
    if c["node"] is None:
        flags.append("WB 노드 없음")
    if c["before"] is None:
        flags.append("중립 기준 없음")
    elif c.get("after") is not None and not ok(c["after"], c["skew"]):
        flags.append("채널 차이 %d 초과" % TOL)
    return "확인 필요: " + ", ".join(flags) if flags else "통과"


# ---------- 실행 ----------
def grab_rgb(sess, c, tag):
    name = "%03d_%s_mid" % (c["i"], tag)
    sess.grab((c["start"] + c["end"]) // 2, name)
    return neutral_rgb(os.path.join(sess.out, "stills", name + ".jpg"))


def solve(sess, c):
    node, param, skew = c["node"], c["param"], c["skew"]
    x = {k: clamp(param, v) for k, v in first_guess(param, c["before"], skew).items()}
    xp = {"R": IDENT[param], "B": IDENT[param]}
    fp = errors(c["before"], skew)
    for _ in range(3):
        c["item"].SetCDL(cdl(node, param, x))
        rgb = grab_rgb(sess, c, "_iter")
        if rgb is None:
            return x, None
        f = errors(rgb, skew)
        if ok(rgb, skew):
            return x, rgb
        nx = {}
        for k in ("R", "B"):
            nx[k] = clamp(param, x[k] - f[k] * (x[k] - xp[k]) / (f[k] - fp[k])) if f[k] != fp[k] else x[k]
        x, xp, fp = nx, x, f
    c["item"].SetCDL(cdl(node, param, x))
    return x, grab_rgb(sess, c, "_iter")


def fmt(rgb):
    return "-" if rgb is None else "%d/%d/%d" % (rgb["R"], rgb["G"], rgb["B"])


def write_log(out, clips, dry):
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M")
    L = ["## 4b. 화이트밸런스", "", "측정: Resolve 출력 스틸의 중립 후보 픽셀(채도 20% 이하, 중간 밝기) 평균 R/G/B, 10비트. 모드: " + ("dry-run" if dry else "적용"), "",
         "| 파일명 | 시작 TC | 촬영 시각 | 시간대 | 목표 R-B | 기준 픽셀% | R/G/B 전 | R/G/B 후 | 조정 | 판정 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for c in clips:
        L.append("| %s | %s | %s | %s | %+d | %s | %s | %s | %s | %s |" % (
            c["name"], c["tc"], "%02d:%02d" % (int(c["hour"]), int(c["hour"] * 60) % 60) if c["hour"] is not None else "없음", c["bucket"], c["skew"],
            c["before"]["share"] if c["before"] else "-", fmt(c["before"]), fmt(c.get("after")), c.get("adj", "-"), verdict(c)))
    path = os.path.join(out, "whitebalance_%s.md" % stamp)
    open(path, "w").write("\n".join(L) + "\n")
    json.dump([{k: v for k, v in c.items() if k != "item"} for c in clips], open(os.path.join(out, "whitebalance_%s.json" % stamp), "w"), ensure_ascii=False, indent=1)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--timeline")
    ap.add_argument("--track", type=int, default=1)
    ap.add_argument("--sunrise", default="06:30")
    ap.add_argument("--sunset", default="18:30")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-missing", action="store_true", help="라벨 노드 없는 클립은 건너뛰고 확인 필요로만 남긴다")
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
        node, param = wb_node_for(it, mpi)
        hour = X.hour_of(mpi)
        b = X.bucket(hour, sr, ss)
        clips.append({"i": len(clips), "item": it, "name": it.GetName(), "start": int(it.GetStart()), "end": int(it.GetEnd()),
                      "tc": sess.tc(it.GetStart()), "hour": hour, "bucket": b, "skew": SKEW[b], "node": node, "param": param})
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
        c["before"] = grab_rgb(sess, c, "before")
    if not a.dry_run:
        for c in clips:
            if c["node"] is None or c["before"] is None or ok(c["before"], c["skew"]):
                c["adj"] = "없음"
                c["after"] = c["before"]
                continue
            x, rgb = solve(sess, c)
            c["after"] = rgb
            c["adj"] = "노드%d %s R %.4f B %.4f" % (c["node"], c["param"], x["R"], x["B"])
            if rgb is None or not ok(rgb, c["skew"]):
                c["item"].AddMarker(MARKER[2], MARKER[0], "%s %s %s" % (MARKER[1], c["name"], "기준 없음" if rgb is None else "채널 차이 초과"), "", 1)
    print("로그:", write_log(a.out, clips, a.dry_run))
    if missing:
        print(NODE_HELP + "\n대상: " + ", ".join(missing))


def selftest():
    from PIL import Image
    import tempfile
    # 따뜻한 캐스트가 낀 회색 카드 + 채도 높은 영역: 중립 후보는 회색 카드만 잡혀야 한다
    im = Image.new("RGB", (100, 100), (150, 140, 120))
    for x in range(100):
        for y in range(50, 100):
            im.putpixel((x, y), (200, 40, 40))
    p = os.path.join(tempfile.mkdtemp(), "t.png")
    im.save(p)
    rgb = neutral_rgb(p)
    assert 48 <= rgb["share"] <= 52 and (rgb["R"], rgb["G"], rgb["B"]) == (600, 560, 480), rgb  # 축소 보간으로 경계가 흐려진다
    assert not ok(rgb, 0) and errors(rgb, 0) == {"R": 40, "B": -80}
    assert ok({"R": 575, "G": 560, "B": 545}, 30)          # 오후: R-B 30 남긴 상태가 통과
    g = first_guess("Slope", rgb, 0)
    assert abs(g["R"] * 600 - 560) < 1 and abs(g["B"] * 480 - 560) < 1
    assert clamp("Slope", 2.0) == 1.2 and clamp("Offset", -1) == -0.1
    assert cdl(2, "Slope", {"R": 0.93, "B": 1.17})["Slope"] == "0.9300 1.0000 1.1700"
    assert cdl(2, "Offset", {"R": 0.01, "B": -0.02})["Offset"] == "0.0100 0.0000 -0.0200"
    im2 = Image.new("RGB", (10, 10), (250, 250, 250)); im2.save(p)
    assert neutral_rgb(p) is None                          # 너무 밝아 후보 없음
    print("selftest ok")


if __name__ == "__main__":
    main()
