"""juno 스타일 이미지 생성 프롬프트를 장면 spec(JSON)에서 조립하고 채점한다.

  build <spec.json> [-o prompt.txt]   채점 후 100점이면 프롬프트를 쓴다(없으면 stdout)
  check <spec.json>                   채점표만 출력
  --selftest                          자체 검사
"""
import json
import re
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"

# 모델이 쓴 글에 나오면 안 되는 말. 얼굴·인물 사진(사람은 figures에서 뒷모습·실루엣으로만), 스타일을 깨는 표현.
BANNED_FACE = r"\b(faces?|facial|portraits?|selfies?|smil\w*|eyes|looking at (the )?camera|close-?up)\b"
FIGURE_VIEW = r"\b(behind|back|silhouett\w*|blurr\w*)\b"
# 카메라는 고정. motion에 카메라 이동 낱말이 있으면 칸마다 화면이 달라져 영상이 끊긴다.
CAMERA_MOVE = r"\b(pans?|panning|zoom\w*|dolly|tracking|handheld|orbit\w*|tilts?)\b"
SHEET = ("A single image laid out as an animation sprite sheet: exactly 4 sequential frames in a precise 2-column by "
         "2-row grid, read left-to-right then top-to-bottom. Every panel is landscape 16:9 with identical dimensions "
         "and meets its neighbours edge to edge with no gutters or borders. Each panel is the same photograph: ")
BANNED_STYLE = (r"\b(3d|cgi|render(ed)?|illustration|cartoon|anime|vector|neon|hdr|4k|8k|ultra|sharp|"
                r"cinematic|cyberpunk)\b")
DONT = ("DO NOT: no visible or in-focus human face, no posed portrait, no one looking at the camera; no illustration, "
        "cartoon, anime, 3D or CGI look; no HDR, no digital sharpness, no oversaturated color; no readable text, "
        "logos, captions, borders, letterbox bars or watermark anywhere in the image.")


def load(name):
    return {r["id"]: r for r in map(json.loads, (REF / name).read_text().splitlines()) if r}


def check(spec):
    """(항목, 통과 여부, 이유) 목록. 항목 하나 = 1점, 점수 = 통과 수 / 항목 수 × 100(내림)."""
    props = spec.get("props", [])
    figures, motion = spec.get("figures", ""), spec.get("motion", "")
    text = " ".join([spec.get("scene", ""), spec.get("setting", ""), figures, motion] + props)
    words = len(spec.get("scene", "").split())
    palettes = load("palettes.jsonl")
    rows = [
        ("palette", spec.get("palette") in palettes, f"palettes.jsonl id: {sorted(palettes)}"),
        ("scene length", 6 <= words <= 40, f"scene {words}단어, 6~40단어(공백으로 나눈 수, 경계 포함)"),
        ("setting", bool(spec.get("setting", "").strip()), "setting은 빈칸 불가, 장소 한 구절"),
        ("props", 1 <= len(props) == len(set(props)) <= 6, f"소품 {len(props)}개, 1~6개(경계 포함), 중복 없이"),
        ("english", text.isascii(), "모델이 쓴 영어 글은 ASCII만"),
        ("figures", not figures or bool(re.search(FIGURE_VIEW, figures, re.I)),
         "figures는 빈칸이거나 behind·back·silhouette·blurred 중 하나를 담는다"),
        ("no faces", not re.search(BANNED_FACE, text, re.I),
         "face·facial·portrait·selfie·smile·eyes·looking at camera·close-up 금지"),
        ("no banned style", not re.search(BANNED_STYLE, text, re.I),
         "3d·cgi·render·illustration·cartoon·anime·vector·neon·hdr·4k·8k·ultra·sharp·cinematic·cyberpunk 금지"),
    ]
    if "motion" in spec:
        n = len(motion.split())
        rows.append(("motion", 4 <= n <= 30 and not re.search(CAMERA_MOVE, motion, re.I),
                     f"motion {n}단어, 4~30단어(경계 포함), pan·zoom·dolly·tracking·handheld·orbit·tilt 금지"))
    return rows


def score(rows):
    return sum(ok for _, ok, _ in rows) * 100 // len(rows)


def build(spec):
    style, p = load("style.jsonl"), load("palettes.jsonl")[spec["palette"]]
    colors = "; ".join(f"{k} {v}" for k, v in p["colors"].items())
    motion = (spec.get("motion") or "").rstrip(". ")
    rules = " ".join(style[k]["prompt"] for k in style if k not in ("medium", "motion") or (k == "motion" and motion))
    head = SHEET + style["medium"]["prompt"] if motion else style["medium"]["prompt"]
    moving = (f"MOTION: {motion}. Frames 1 to 4 show it in clear, even steps and frame 4 leads smoothly back to frame 1. "
              "Everything else (background, light, signs, camera position) stays identical in all four frames.")
    return "\n\n".join([
        head,
        f"SCENE: {spec['scene']} Setting: {spec['setting']}.",
        f"OBJECTS (only these as the readable subjects): {', '.join(spec['props'])}.",
        f"FIGURES: {spec.get('figures') or 'none, the place is empty of people'}.",
        f"COLOR GRADE ({p['prompt']}): the whole frame is graded toward these colors: {colors}.",
        *([moving] if motion else []),
        f"STYLE: {rules}",
        DONT + (" No gutters, borders or panel numbers between frames." if motion else ""),
    ])


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if len(argv) < 2 or argv[0] not in ("build", "check"):
        sys.exit(__doc__)
    spec = json.loads(Path(argv[1]).read_text())
    rows = check(spec)
    for name, ok, why in rows:
        print(f"{'PASS' if ok else 'FAIL'}  {name:16} {why}")
    print(f"score {score(rows)}")
    if argv[0] == "check":
        sys.exit(0 if score(rows) == 100 else 1)
    if score(rows) < 100:
        sys.exit("FAIL 항목을 고친 뒤 다시 build 하세요")
    out = build(spec)
    if "-o" in argv:
        Path(argv[argv.index("-o") + 1]).write_text(out + "\n")
    else:
        print(out)


def selftest():
    good = json.loads((REF / "example" / "01_fish-market-dawn.json").read_text())
    assert score(check(good)) == 100, check(good)
    out = build(good)
    assert "#D2A06A" in out and "Matte color grade" in out and "{" not in out
    assert "empty of people" in build(dict(good, figures=""))
    assert "sprite sheet" not in out and "tripod" not in out
    sheet = json.loads((REF / "example" / "02_overpass-night-motion.json").read_text())
    assert score(check(sheet)) == 100, check(sheet)
    sout = build(sheet)
    assert "2-column by 2-row" in sout and "tripod" in sout and "MOTION:" in sout and "panel numbers" in sout
    assert sout.strip() == (REF / "example" / "02_overpass-night-motion.txt").read_text().strip(), "예시 txt를 다시 build 하세요"
    assert {n for n, ok, _ in check(dict(sheet, motion="slow zoom on the lights")) if not ok} == {"motion"}
    assert out.strip() == (REF / "example" / "01_fish-market-dawn.txt").read_text().strip(), "예시 txt를 다시 build 하세요"
    bad = dict(good, palette="neon", scene="A smiling face.", setting="", props=["x"] * 7, figures="a tall man")
    failed = {n for n, ok, _ in check(bad) if not ok}
    assert {"palette", "scene length", "setting", "props", "figures", "no faces"} <= failed, failed
    assert score(check(dict(good, scene=good["scene"] + " Shot in 4k HDR."))) < 100
    assert score(check(dict(good, scene="A backstreet laundromat glows at night, its eyesore sign half lit."))) == 100
    print("selftest ok")


if __name__ == "__main__":
    main(sys.argv[1:])
