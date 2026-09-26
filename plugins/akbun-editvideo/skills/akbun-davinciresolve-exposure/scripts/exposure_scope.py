#!/usr/bin/env python3
"""클립마다 스코프(Waveform 중앙값)를 재고 시간대별 목표 대역과 컷 전환 피로 한계에 맞춰
CDL로 밝기를 맞춘다. DaVinci Resolve 21.1 외부 스크립팅 API + Pillow만 쓴다.

  python3 exposure_scope.py --out DIR [--timeline NAME] [--sunrise 06:30 --sunset 18:30]
                            [--max-shift 120] [--dry-run] [--reset] [--selftest]

측정값은 Resolve가 내보낸 현재 프레임(그레이드 적용 뒤)의 휘도 히스토그램이고 10비트(0~1023) 스케일로 적는다.
조정은 Color 페이지에서 새로 만들고 라벨 EXPOSURE를 단 노드에만 쓴다. 라벨 없는 노드와 기존 그레이드 노드는 건드리지 않는다.
"""
import argparse
import datetime as dt
import json
import math
import os
import re
import sys
import time

# ---------- 기준값 (SKILL.md 표와 같아야 한다) ----------
BANDS = {  # 시간대 -> (중앙값 하한, 상한)
    "밤": (120, 280), "아침": (320, 460), "낮": (420, 560),
    "오후": (360, 500), "저녁": (250, 400), "미상": (120, 560),
}
JUMP_SAME, JUMP_DIFF = 60, 120   # 인접 컷 tail→head 중앙값 차이 한계(같은 시간대 / 다른 시간대)
MAX_SHIFT = 120                  # 클립당 최대 변화(약 ±0.5 stop). 넘으면 `확인 필요`
BAND_SLACK = 40                  # 전환을 맞추려고 대역 밖으로 나갈 수 있는 여유
CLIP_HI_MAX = 0.5                # 하이라이트 클리핑(%) 허용치
BLACK_LIFT = 120                 # p1이 이보다 높으면 검은색이 회색으로 뜬 것(Lift 과다·안개)
TOL = 15                         # 목표 중앙값 허용 오차
IDENTITY = {"Slope": "1 1 1", "Offset": "0 0 0", "Power": "1 1 1", "Saturation": 1.0}
MARKER = ("Lemon", "EXPOSURE_CHECK", 5)  # video-editor 마커 등록표
NODE_HELP = ("EXPOSURE 라벨 노드 없음. Color 페이지에서 클립마다 Color → Nodes → Append a Node로 빈 노드를 붙이고 "
             "Color → Nodes → Label Selected Node로 라벨 EXPOSURE를 단다(그레이드 없는 클립은 기본 노드에 라벨만). "
             "변환 앞에 두려면(Log 소스) Add Serial Before Current. 라벨 없는 노드·기존 그레이드 노드에는 쓰지 않는다.")


# ---------- 순수 계산 ----------
def bucket(hour, sunrise, sunset):
    """촬영 시각(시, 소수) -> 시간대 이름. sunrise/sunset도 시 단위 소수. 일몰 뒤 30분은 하늘이 밝아 오후로 본다."""
    if hour is None:
        return "미상"
    if hour < sunrise - 0.5 or hour >= sunset + 1.5:
        return "밤"
    if hour < sunrise + 1.5:
        return "아침"
    if hour < sunset - 1.5:
        return "낮"
    if hour < sunset + 0.5:
        return "오후"
    return "저녁"


def plan(clips):
    """clips: [{bucket, before:{median, head, tail}}] -> 목표 중앙값 목록. 대역 맞춤 뒤 인접 컷 차이를 완화한다."""
    m = [c["before"]["median"] for c in clips]
    t = [min(max(x, BANDS[c["bucket"]][0]), BANDS[c["bucket"]][1]) for x, c in zip(m, clips)]
    for _ in range(20):  # ponytail: 고정 20회 완화. 안 맞으면 확인 필요로 남긴다
        for i in range(len(clips) - 1):
            a, b = clips[i]["before"], clips[i + 1]["before"]
            lim = JUMP_SAME if clips[i]["bucket"] == clips[i + 1]["bucket"] else JUMP_DIFF
            j = (a["tail"] + t[i] - m[i]) - (b["head"] + t[i + 1] - m[i + 1])
            if abs(j) > lim:
                mv = (abs(j) - lim) / 2 * (1 if j > 0 else -1)
                t[i] -= mv
                t[i + 1] += mv
        for i, c in enumerate(clips):
            lo, hi = BANDS[c["bucket"]]
            t[i] = min(max(t[i], lo - BAND_SLACK, m[i] - MAX_SHIFT), hi + BAND_SLACK, m[i] + MAX_SHIFT)
    return [round(x) for x in t]


def jumps(clips, key):
    """인접 컷의 (tail→head 차이, 한계). key는 'before' 또는 'after'."""
    out = []
    for i in range(len(clips) - 1):
        lim = JUMP_SAME if clips[i]["bucket"] == clips[i + 1]["bucket"] else JUMP_DIFF
        out.append((round(clips[i][key]["tail"] - clips[i + 1][key]["head"]), lim))
    return out


def stats(path):
    """스틸 파일 -> {median, p1, p99, clip_hi(%)} 10비트 스케일."""
    from PIL import Image
    h = Image.open(path).convert("L").histogram()
    n = sum(h)

    def pct(p):
        acc = 0
        for v, c in enumerate(h):
            acc += c
            if acc >= n * p:
                return v * 4
        return 1020

    return {"median": pct(0.5), "p1": pct(0.01), "p10": pct(0.10), "p90": pct(0.90), "p99": pct(0.99), "clip_hi": round(sum(h[254:]) / n * 100, 2)}


def first_guess(param, median, target):
    if param == "Offset":
        return (target - median) / 1700.0  # ponytail: 실측 기울기(Apple Log 2 + LUT). 이후 secant가 보정
    return min(max(math.log(target / 1023) / math.log(max(median, 1) / 1023), 0.5), 2.0)


def clamp_param(param, x):
    return min(max(x, -0.3), 0.3) if param == "Offset" else min(max(x, 0.5), 2.0)


def cdl(node, param, x):
    d = dict(IDENTITY, NodeIndex=node)
    d[param] = "%.4f %.4f %.4f" % (x, x, x)
    return d


def verdict(c, target):
    lo, hi = BANDS[c["bucket"]]
    after = c.get("after") or {"median": target, "clip_hi": c["before"]["clip_hi"], "p1": c["before"].get("p1", 0)}
    flags = []
    if c["node"] is None:
        flags.append("EXPOSURE 노드 없음")
    if not (lo - BAND_SLACK - TOL <= after["median"] <= hi + BAND_SLACK + TOL):  # 계획이 허용한 여유 밖만 표시
        flags.append("대역 밖")
    if after["clip_hi"] > CLIP_HI_MAX:
        flags.append("클리핑")
    if after.get("p1", 0) > BLACK_LIFT:
        flags.append("블랙 뜸(p1 %d)" % after["p1"])
    return "확인 필요: " + ", ".join(flags) if flags else "통과"


# ---------- Resolve 연결 ----------
def connect():
    api = os.environ.setdefault("RESOLVE_SCRIPT_API", "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting")
    os.environ.setdefault("RESOLVE_SCRIPT_LIB", "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so")
    sys.path.append(os.path.join(api, "Modules"))
    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        sys.exit("Resolve에 연결 못 함: Resolve Studio 실행, External scripting=Local, 환경변수 확인")
    return resolve, resolve.GetProjectManager().GetCurrentProject()


def pick_timeline(project, name):
    if not name:
        return project.GetCurrentTimeline()
    for i in range(1, project.GetTimelineCount() + 1):
        tl = project.GetTimelineByIndex(i)
        if tl.GetName() == name:
            project.SetCurrentTimeline(tl)
            return tl
    sys.exit("타임라인 없음: " + name)


def hour_of(mpi):
    """촬영 시각(시, 소수). Date Recorded가 비면(Insta360, iPhone 비Log) Date Created를 쓴다."""
    for key in ("Date Recorded", "Date Created"):
        m = re.search(r"(\d{2}):(\d{2}):\d{2}", (mpi.GetClipProperty(key) or "") if mpi else "")
        if m:
            return int(m.group(1)) + int(m.group(2)) / 60
    return None


CONV_TOOLS = ("LUT", "OFX: Color Space Transform")


def labeled_node(item, mpi, keywords):
    """라벨에 keywords 중 하나가 들어간 첫 노드 -> (idx, log_before_conv, tools) 또는 None.
    log_before_conv: Log 소스이고 변환(LUT·CST) 노드가 이 노드 뒤에 있음. 라벨 없는 노드에는 어떤 skill도 쓰지 않는다."""
    g = item.GetNodeGraph()
    n = g.GetNumNodes()
    labels = [(g.GetNodeLabel(i) or "").lower() for i in range(1, n + 1)]
    tools = [g.GetToolsInNode(i) or [] for i in range(1, n + 1)]
    hit = [i for i, l in enumerate(labels) if any(k in l for k in keywords)]
    if not hit:
        return None
    idx = hit[0] + 1
    cs = (mpi.GetClipProperty("Input Color Space") or "") if mpi else ""
    conv_after = any(t.startswith(CONV_TOOLS) for ts in tools[idx:] for t in ts)
    return idx, ("log" in cs.lower() and conv_after), tools


def node_for(item, mpi):
    """(노드 번호, 파라미터) 또는 (None, None). 라벨에 exposure가 들어간 노드만 쓴다.
    파라미터: Log 소스이고 변환 노드가 뒤에 있으면 Offset(로그 노출), 아니면 Power(감마)."""
    r = labeled_node(item, mpi, ("exposure",))
    return (None, None) if r is None else (r[0], "Offset" if r[1] else "Power")


class Session:
    def __init__(self, resolve, project, tl, out):
        self.resolve, self.project, self.tl, self.out = resolve, project, tl, out
        self.fps = float(tl.GetSetting("timelineFrameRate"))
        self.last = None
        os.makedirs(os.path.join(out, "stills"), exist_ok=True)
        resolve.OpenPage("edit")

    def tc(self, frame):  # ponytail: non-drop-frame만. 29.97DF면 SetCurrentTimecode가 어긋난다
        f = int(round(frame)); fi = int(round(self.fps)); s = f // fi
        return "%02d:%02d:%02d:%02d" % (s // 3600, (s // 60) % 60, s % 60, f % fi)

    def grab(self, frame, name):
        """현재 프레임을 스틸로 내보내 측정. 뷰어가 아직 이전 프레임이면(직전 측정과 완전히 같음) 기다려 다시 잰다."""
        path = os.path.join(self.out, "stills", name + ".jpg")
        if not self.tl.SetCurrentTimecode(self.tc(frame)):
            sys.exit("타임코드 이동 실패 " + name)
        for attempt in range(4):
            time.sleep(0.2 * (attempt + 1))
            if not self.project.ExportCurrentFrameAsStill(path):
                sys.exit("스틸 내보내기 실패 " + name)
            st = stats(path)
            if st != self.last:
                break
        self.last = st
        return st

    def measure(self, c, tag):
        d = c["end"] - c["start"]
        off = max(2, int(d * 0.1))
        r = self.grab((c["start"] + c["end"]) // 2, "%03d_%s_mid" % (c["i"], tag))
        r["head"] = self.grab(c["start"] + off, "%03d_%s_head" % (c["i"], tag))["median"]
        r["tail"] = self.grab(c["end"] - 1 - off, "%03d_%s_tail" % (c["i"], tag))["median"]
        c[tag] = r

    def solve(self, c, target):
        """secant로 파라미터 x를 찾아 중앙값을 target±TOL로. 반환: (x, 측정 stats)."""
        node, param = c["node"], c["param"]
        xp, fp = (0.0 if param == "Offset" else 1.0), c["before"]["median"]
        x = clamp_param(param, first_guess(param, fp, target))
        mid = (c["start"] + c["end"]) // 2
        for _ in range(3):
            c["item"].SetCDL(cdl(node, param, x))
            st = self.grab(mid, "_iter")
            if abs(st["median"] - target) <= TOL or st["median"] == fp:
                return x, st
            x, xp, fp = clamp_param(param, x + (target - st["median"]) * (x - xp) / (st["median"] - fp)), x, st["median"]
        c["item"].SetCDL(cdl(node, param, x))
        return x, self.grab(mid, "_iter")


def collect(sess, track):
    clips = []
    for it in sess.tl.GetItemListInTrack("video", track):
        if it.GetType() != "video" or not it.GetClipEnabled():
            continue
        mpi = it.GetMediaPoolItem()
        node, param = node_for(it, mpi)
        clips.append({"i": len(clips), "item": it, "name": it.GetName(), "start": int(it.GetStart()), "end": int(it.GetEnd()),
                      "tc": sess.tc(it.GetStart()), "hour": hour_of(mpi), "node": node, "param": param})
    return clips


def write_log(out, clips, targets, dry):
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M")
    L = ["## 4. 노출(밝기)", "", "측정: Resolve 출력 스틸 휘도 중앙값, 10비트 스케일. 모드: " + ("dry-run(적용 안 함)" if dry else "적용"), "",
         "| 파일명 | 시작 TC | 촬영 시각 | 시간대 | 목표 대역 | 중앙값 전→후 | p99 전→후 | 클리핑% 전→후 | 조정 | 판정 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for c, t in zip(clips, targets):
        lo, hi = BANDS[c["bucket"]]
        b, a = c["before"], c.get("after") or {"median": "목표 %d" % t, "p99": "-", "clip_hi": "-"}
        L.append("| %s | %s | %s | %s | %d~%d | %d→%s | %d→%s | %s→%s | %s | %s |" % (
            c["name"], c["tc"], "%02d:%02d" % (int(c["hour"]), int(c["hour"] * 60) % 60) if c["hour"] is not None else "없음", c["bucket"], lo, hi,
            b["median"], a["median"], b["p99"], a["p99"], b["clip_hi"], a["clip_hi"], c.get("adj", "-"), verdict(c, t)))
    L += ["", "| 컷 | 앞 클립 → 뒤 클립 | tail→head 차이 전→후 | 한계 | 판정 |", "|---|---|---|---|---|"]
    after_key = "after" if clips and "after" in clips[0] else "before"
    for i, ((jb, lim), (ja, _)) in enumerate(zip(jumps(clips, "before"), jumps(clips, after_key))):
        L.append("| %d | %s → %s | %d→%d | %d | %s |" % (i + 1, clips[i]["name"], clips[i + 1]["name"], abs(jb), abs(ja), lim, "통과" if abs(ja) <= lim else "확인 필요"))
    path = os.path.join(out, "exposure-scope_%s.md" % stamp)
    open(path, "w").write("\n".join(L) + "\n")
    json.dump([{k: v for k, v in c.items() if k != "item"} for c in clips], open(os.path.join(out, "exposure-scope_%s.json" % stamp), "w"), ensure_ascii=False, indent=1)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="출력 폴더")
    ap.add_argument("--timeline")
    ap.add_argument("--track", type=int, default=1)
    ap.add_argument("--sunrise", default="06:30")
    ap.add_argument("--sunset", default="18:30")
    ap.add_argument("--max-shift", type=int, default=MAX_SHIFT, help="클립당 최대 변화(10비트). 기본 120")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-missing", action="store_true", help="라벨 노드 없는 클립은 건너뛰고 확인 필요로만 남긴다")
    ap.add_argument("--reset", action="store_true", help="EXPOSURE 노드의 CDL을 identity로 되돌린다")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.out:
        ap.error("--out 필요")
    globals()["MAX_SHIFT"] = a.max_shift
    sr, ss = (int(a.sunrise[:2]) + int(a.sunrise[3:]) / 60), (int(a.sunset[:2]) + int(a.sunset[3:]) / 60)

    resolve, project = connect()
    tl = pick_timeline(project, a.timeline)
    sess = Session(resolve, project, tl, a.out)
    clips = collect(sess, a.track)
    missing = [c["name"] for c in clips if c["node"] is None]
    if a.reset:
        for c in clips:
            if c["node"]:
                c["item"].SetCDL(dict(IDENTITY, NodeIndex=c["node"]))
        print("reset", len(clips) - len(missing))
        return
    if missing and not a.dry_run and not a.skip_missing:
        sys.exit(NODE_HELP + "\n대상: " + ", ".join(missing))
    for c in clips:
        c["bucket"] = bucket(c["hour"], sr, ss)
        c["snapshot"] = c["item"].GetCurrentVersion().get("versionName") if c["node"] else None
        sess.measure(c, "before")
    targets = plan(clips)
    if not a.dry_run:
        for c, t in zip(clips, targets):
            if c["node"] is None or abs(t - c["before"]["median"]) <= TOL:
                c["adj"] = "없음"
                continue
            x, st = sess.solve(c, t)
            if st["clip_hi"] > CLIP_HI_MAX and t > c["before"]["median"]:  # 밝히다 하이라이트가 날아가면 한 번 낮춘다
                x, st = sess.solve(c, t - 40)
            c["adj"] = "노드%d %s %.4f" % (c["node"], c["param"], x)
        for c in clips:
            sess.measure(c, "after")
        for i, (j, lim) in enumerate(jumps(clips, "after")):
            if abs(j) > lim:
                nxt = clips[i + 1]
                nxt["item"].AddMarker(MARKER[2], MARKER[0], "%s %s 전환 차이 %d>%d" % (MARKER[1], nxt["name"], abs(j), lim), "", 1)
    print("로그:", write_log(a.out, clips, targets, a.dry_run))
    if missing:
        print(NODE_HELP + "\n대상: " + ", ".join(missing))


def selftest():
    def C(m, b, head=None, tail=None):
        return {"bucket": b, "before": {"median": m, "head": head or m, "tail": tail or m, "clip_hi": 0.0}, "node": 2}
    # 낮 클립 사이에 어두운 클립 하나: 대역으로 올리되 최대 변화 안에서
    clips = [C(480, "낮", 470, 490), C(200, "낮"), C(500, "낮")]
    t = plan(clips)
    assert t[1] == 320, t  # 200+MAX_SHIFT
    assert all(abs(x - c["before"]["median"]) <= MAX_SHIFT for x, c in zip(t, clips))
    # 저녁→밤 경계는 다른 시간대 한계(120)만 적용, 대역 안이면 손대지 않음
    clips = [C(300, "저녁"), C(200, "밤")]
    assert plan(clips) == [300, 200] and jumps(clips, "before") == [(100, JUMP_DIFF)]
    # 같은 시간대 안의 큰 차이는 양쪽이 절반씩 다가간다
    clips = [C(520, "낮"), C(420, "낮")]
    assert plan(clips) == [500, 440]
    assert bucket(12, 6.5, 18.5) == "낮" and bucket(17.5, 6.5, 18.5) == "오후" and bucket(18.8, 6.5, 18.5) == "오후"
    assert bucket(19.2, 6.5, 18.5) == "저녁" and bucket(20.5, 6.5, 18.5) == "밤" and bucket(None, 6.5, 18.5) == "미상"
    assert cdl(2, "Offset", 0.05) == {"NodeIndex": 2, "Slope": "1 1 1", "Offset": "0.0500 0.0500 0.0500", "Power": "1 1 1", "Saturation": 1.0}
    assert verdict(dict(C(300, "낮"), node=None), 420) == "확인 필요: EXPOSURE 노드 없음"  # dry-run: 목표값으로 판정
    assert verdict(dict(C(300, "낮"), after={"median": 300, "clip_hi": 0.8}), 420) == "확인 필요: 대역 밖, 클리핑"
    assert verdict(dict(C(480, "낮"), after={"median": 480, "clip_hi": 0.0, "p1": 150}), 480) == "확인 필요: 블랙 뜸(p1 150)"
    print("selftest ok")


if __name__ == "__main__":
    main()
