"""facade-hairline 스타일 이미지 생성 프롬프트를 spec(JSON)에서 조립하고 채점한다.

  build <spec.json> [-o prompt.txt]   채점 후 100점이면 프롬프트를 쓴다(없으면 stdout)
  check <spec.json>                   채점표만 출력
  --selftest                          자체 검사
"""
import json
import re
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"

BANNED_FACE = r"\b(faces?|eyes?|nose|mouths?|smil\w*|grin\w*|frown\w*|expressions?|lips)\b"
BANNED_STYLE = r"\b(3d|photo\w*|realistic|anime|cartoon\w*|gradients?|neon|shad(ing|ed|ow|ows)|glossy|watercolou?r|bold|thick|crosshatch\w*|hatch\w*|perspective|isometric|vanishing)\b"
BANNED_TEXT = r"\b(texts?|letter(s|ing)?|words?|written|logos?|says|reading|numbers?|digits?|captions?|labels?)\b|[\"']"
NO_TEXT = "No written words, letters or numbers anywhere; signboards, posters and labels stay blank."


def load(name):
    return {r["id"]: r for r in (json.loads(l) for l in (REF / name).read_text().splitlines() if l.strip())}


def words(s):
    return len(str(s).split())


def lst(spec, key):
    v = spec.get(key, [])
    return v if isinstance(v, list) else []


def named(spec):
    """강조색을 칠할 수 있는 이름들: 구조물·세부·사람의 머리와 옷·동물·소품."""
    out = []
    for s in lst(spec, "structures"):
        out += [s.get("what", "")] + list(s.get("details", []))
    for f in lst(spec, "figures"):
        out += [f.get("head", ""), f.get("garment", "")]
    out += [a.get("what", "") for a in lst(spec, "animals")] + lst(spec, "props")
    return [str(n).lower() for n in out]


def free_text(spec):
    """모델이 직접 쓴 글만 모은다."""
    parts = [spec.get("scene", "")] + lst(spec, "lights") + named(spec)
    parts += [f.get("who", "") + " " + f.get("doing", "") for f in lst(spec, "figures")]
    parts += [a.get("doing", "") for a in lst(spec, "animals")] + [a.get("on", "") for a in lst(spec, "accents")]
    return " ".join(map(str, parts))


def check(spec):
    """(항목, 통과 여부, 이유) 목록. 항목 하나 = 1점, 점수 = 통과 수 / 항목 수 × 100(내림)."""
    tim, can, pen, acc = load("times.jsonl"), load("canvases.jsonl"), load("pens.jsonl"), load("accents.jsonl")
    sts, figs, ans, props = lst(spec, "structures"), lst(spec, "figures"), lst(spec, "animals"), lst(spec, "props")
    lights, accents = lst(spec, "lights"), lst(spec, "accents")
    text, names = free_text(spec), named(spec)
    night = spec.get("time") == "night"

    def has(term):
        t = str(term).lower().strip()
        return t not in ("", "a", "an", "the") and any(re.search(rf"\b{re.escape(t)}\b", n) for n in names)
    return [
        ("time", spec.get("time") in tim, f"times.jsonl id: {sorted(tim)}"),
        ("canvas", spec.get("canvas") in can, f"canvases.jsonl id: {sorted(can)}"),
        ("pen", spec.get("pen") in pen, f"pens.jsonl id: {sorted(pen)}"),
        ("scene length", 6 <= words(spec.get("scene", "")) <= 30, f"scene {words(spec.get('scene', ''))}단어, 6~30단어"),
        ("structures", 1 <= len(sts) <= 4 and all(words(s.get("what", "")) >= 2 and 2 <= len(s.get("details", [])) <= 6 for s in sts),
         f"구조물 {len(sts)}개, 1~4개. 각 what 2단어 이상, details 2~6개"),
        ("figures", len(figs) <= 5 and all(words(f.get("who", "")) >= 1 and words(f.get("head", "")) >= 2
                                           and words(f.get("garment", "")) >= 2 and words(f.get("doing", "")) >= 2 for f in figs),
         f"사람 {len(figs)}명, 0~5명. 각 who 1단어·head·garment·doing 2단어 이상"),
        ("animals", len(ans) <= 3 and all(words(a.get("what", "")) >= 2 and words(a.get("doing", "")) >= 2 for a in ans),
         f"동물 {len(ans)}마리, 0~3마리. 각 what·doing 2단어 이상"),
        ("props", len(props) <= 6 and len(set(props)) == len(props), f"소품 {len(props)}개(중복 없이), 0~6개"),
        ("lights", (2 <= len(lights) <= 5) if night else not lights, f"빛 {len(lights)}개. night면 2~5개, day면 0개"),
        ("accents", 1 <= len(accents) <= 2 and len({a.get("color") for a in accents}) == len(accents)
         and all(a.get("color") in acc and has(a.get("on", "")) for a in accents),
         f"강조색 1~2개(색 중복 없이), color는 accents.jsonl id {sorted(acc)}, on은 structures·figures head/garment·animals·props 한 항목에 낱말 단위로 든 말"),
        ("english", text.isascii(), "모델이 쓴 글은 영어(ASCII)만"),
        ("no faces", not re.search(BANNED_FACE, text, re.I), "face·eyes·nose·mouth·smile·expression 금지"),
        ("no banned style", not re.search(BANNED_STYLE, text, re.I),
         "3d·photo·realistic·anime·cartoon·gradient·neon·shading·shadow·glossy·watercolor·bold·thick·hatch·perspective·isometric 금지"),
        ("no lettering", not re.search(BANNED_TEXT, text, re.I), "text·letters·words·logo·number·label·caption·따옴표 금지"),
    ]


def score(rows):
    return sum(ok for _, ok, _ in rows) * 100 // len(rows)


def build(spec):
    style, tim, can = load("style.jsonl"), load("times.jsonl"), load("canvases.jsonl")
    pen, acc = load("pens.jsonl"), load("accents.jsonl")
    t = tim[spec["time"]]
    fill = dict(t["colors"], canvas=can[spec["canvas"]]["prompt"])
    sts = " ".join(f"{i}. {s['what']}, with {', '.join(s['details'])}." for i, s in enumerate(spec["structures"], 1))
    figs = " ".join(f"{i}. a {f['who']} with {f['head']}, wearing {f['garment']}, {f['doing']}."
                    for i, f in enumerate(spec.get("figures", []), 1)) or "none."
    ans = " ".join(f"{i}. {a['what']}, {a['doing']}." for i, a in enumerate(spec.get("animals", []), 1)) or "none."
    props = ", ".join(spec.get("props", [])) or "none beyond the structures"
    accents = "; ".join(f"{acc[a['color']]['hex']} only on {a['on']}" for a in spec["accents"])
    colors = ", ".join(f"{k} {v}" for k, v in t["colors"].items())
    rules = " ".join(style[k]["prompt"].format(**fill) for k in style if k != "medium")
    parts = [
        style["medium"]["prompt"].format(**fill),
        t["prompt"].format(**fill),
        f"SCENE: {spec['scene']}",
        f"STRUCTURES ({len(spec['structures'])}): {sts}",
        f"PEOPLE ({len(spec.get('figures', []))}): {figs}",
        f"ANIMALS ({len(spec.get('animals', []))}): {ans}",
        f"PROPS: {props}.",
    ]
    if spec.get("lights"):
        parts.append(f"LIGHT SOURCES (the only things that glow): {', '.join(spec['lights'])}.")
    parts += [
        f"ACCENT COLORS: {accents}. No other color anywhere.",
        f"BASE COLORS: {colors}.",
        f"STYLE: {rules} {pen[spec['pen']]['prompt']}",
        f"TEXT: {NO_TEXT}",
        "DO NOT: no faces or facial features, no thick or bold outlines, no hatching or cast shadows, no perspective "
        "or isometric views, no gradients on objects, no extra accent colors, no busy sky, no photorealism, no 3D, "
        "no anime, no existing characters or brands, no frame or border, no watermark, no captions.",
    ]
    return "\n\n".join(parts)


def report(rows):
    for name, ok, why in rows:
        print(f"{'PASS' if ok else 'FAIL'}  {name:16} {why}")
    print(f"score {score(rows)}")


def selftest():
    good = {
        "time": "day", "canvas": "wide", "pen": "steady",
        "scene": "A quiet ferry landing on a bright morning as the first passengers arrive.",
        "structures": [{"what": "a wooden ticket office", "details": ["a corrugated roof", "slatted shutters", "a wall clock"]}],
        "figures": [{"who": "woman", "head": "a low bun", "garment": "a long belted coat", "doing": "waits with a basket"}],
        "animals": [{"what": "a small terrier", "doing": "sniffs a rope"}],
        "props": ["coiled ropes", "a red buoy"], "lights": [],
        "accents": [{"color": "vermilion", "on": "red buoy"}],
    }
    assert score(check(good)) == 100, check(good)
    out = build(good)
    assert "#C8402E only on red buoy" in out and "#FDFCF8" in out and "landscape 16:9" in out and "{" not in out
    assert "LIGHT SOURCES" not in out and "steady and smooth" in out
    night = dict(good, time="night", lights=["the office window", "a lamp post"])
    assert score(check(night)) == 100 and "#1D2340" in build(night) and "INVERTED" in build(night)
    assert "LIGHT SOURCES" in build(night)
    assert not dict((n, ok) for n, ok, _ in check(dict(good, time="night")))["lights"]
    assert not dict((n, ok) for n, ok, _ in check(dict(good, lights=["a lamp"])))["lights"]
    assert "wobble" in build(dict(good, pen="wobble")) and "2:1" in build(dict(good, canvas="panorama"))
    two = dict(good, accents=[{"color": "vermilion", "on": "buoy"}, {"color": "indigo", "on": "coat"}])
    assert score(check(two)) == 100
    assert score(check(dict(good, accents=[{"color": "teal", "on": "a"}]))) < 100
    assert score(check(dict(good, accents=[{"color": "teal", "on": "bus"}]))) < 100
    assert score(check(dict(good, accents=[{"color": "teal", "on": "buoy"}, {"color": "teal", "on": "coat"}]))) < 100
    bad = dict(good, canvas="x", scene="A smiling bold face.", props=["a", "a"],
               structures=[{"what": "shop", "details": ["a sign that says OPEN"]}])
    failed = {n for n, ok, _ in check(bad) if not ok}
    assert {"canvas", "scene length", "structures", "props", "no faces", "no banned style", "no lettering"} <= failed, failed
    assert not dict((n, ok) for n, ok, _ in check(dict(good, scene="조용한 아침 나루터에 첫 손님이 도착한다")))["english"]
    print("selftest ok")


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if len(argv) < 2 or argv[0] not in ("build", "check"):
        sys.exit(__doc__)
    spec = json.loads(Path(argv[1]).read_text())
    rows = check(spec)
    report(rows)
    if argv[0] == "check":
        sys.exit(0 if score(rows) == 100 else 1)
    if score(rows) < 100:
        sys.exit("FAIL 항목을 고친 뒤 다시 build 하세요")
    out = build(spec)
    if "-o" in argv:
        Path(argv[argv.index("-o") + 1]).write_text(out + "\n")
    else:
        print(out)


if __name__ == "__main__":
    main(sys.argv[1:])
