"""moss 스타일 이미지 생성 프롬프트를 spec(JSON)에서 조립하고 채점한다.

  build <spec.json> [-o prompt.txt]   채점 후 100점이면 프롬프트를 쓴다(없으면 stdout)
  check <spec.json>                   채점표만 출력
  --selftest                          자체 검사
"""
import json
import re
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"

BANNED_BEINGS = r"\b(humans?|person|people|man|men|woman|women|boys?|girls?|child(ren)?|lady|guy)\b"
BANNED_STYLE = r"\b(3d|photorealistic|realistic|anime|gradients?|neon|shading|glossy|watercolou?r)\b"
NO_TEXT = "No written words, letters or numbers anywhere in the image."


def load(name):
    return {r["id"]: r for r in map(json.loads, (REF / name).read_text().splitlines()) if r}


def free_text(spec):
    """모델이 직접 쓴 글만 모은다."""
    parts = [spec.get("moment", ""), spec.get("accent_on", "")]
    parts += [s.get("what", "") + " " + s.get("doing", "") for s in spec.get("subjects", [])]
    parts += spec.get("props", [])
    return " ".join(parts)


def check(spec):
    """(항목, 통과 여부, 이유) 목록. 항목 하나 = 1점, 점수 = 통과 수 / 항목 수 × 100(내림)."""
    pal, can = load("palettes.jsonl"), load("canvases.jsonl")
    subs, props = spec.get("subjects", []), spec.get("props", [])
    words = len(spec.get("moment", "").split())
    text = free_text(spec)
    accent = spec.get("accent_on", "").lower()
    named = [s.get("what", "").lower() for s in subs] + [p.lower() for p in props]
    return [
        ("palette", spec.get("palette") in pal, f"palettes.jsonl id: {sorted(pal)}"),
        ("canvas", spec.get("canvas") in can, f"canvases.jsonl id: {sorted(can)}"),
        ("subject count", 1 <= len(subs) <= 3, f"소재 {len(subs)}개, 1~3개(경계 포함)"),
        ("subject fields", bool(subs) and all(len(s.get("what", "").split()) >= 2 and len(s.get("doing", "").split()) >= 2 for s in subs),
         "소재마다 what·doing 각 2단어 이상"),
        ("props", len(props) <= 4 and len(set(props)) == len(props), f"소품 {len(props)}개(중복 없이), 0~4개"),
        ("moment length", 6 <= words <= 30, f"moment {words}단어, 6~30단어"),
        ("accent target", accent not in ("", "a", "an", "the") and any(re.search(rf"\b{re.escape(accent)}\b", n) for n in named),
         "accent_on은 subjects.what 또는 props 한 항목에 낱말 단위로 들어 있는 말(관사만은 안 됨)"),
        ("english", text.isascii(), "모델이 쓴 글은 영어(ASCII)만"),
        ("no humans", not re.search(BANNED_BEINGS, text, re.I), "human·person·people·man·woman·boy·girl·child 금지"),
        ("no banned style", not re.search(BANNED_STYLE, text, re.I), "3d·photorealistic·realistic·anime·gradient·neon·shading·glossy·watercolor 금지"),
    ]


def score(rows):
    return sum(ok for _, ok, _ in rows) * 100 // len(rows)


def build(spec):
    style, pal, can = load("style.jsonl"), load("palettes.jsonl"), load("canvases.jsonl")
    c = pal[spec["palette"]]["colors"]
    fill = dict(c, canvas=can[spec["canvas"]]["prompt"])
    subs = " ".join(f"{i}. {s['what']}, {s['doing']}." for i, s in enumerate(spec["subjects"], 1))
    props = f"PROPS: {', '.join(spec['props'])}." if spec.get("props") else "PROPS: none beyond the subjects."
    colors = "; ".join(f"{k.replace('_', ' ')} {v}" for k, v in c.items())
    rules = " ".join(style[k]["prompt"].format(**fill) for k in style if k != "medium")
    return "\n\n".join([
        style["medium"]["prompt"].format(**fill),
        f"MOMENT: {spec['moment']}",
        f"SUBJECTS ({len(spec['subjects'])}): {subs}",
        props,
        f"ACCENT: only {spec['accent_on']} is colored {c['accent']}.",
        f"COLOR PALETTE: use only these five colors: {colors}.",
        f"STYLE: {rules}",
        f"TEXT: {NO_TEXT}",
        "DO NOT: no humans, no photorealism, no 3D, no gradients or soft shading, no extra accent colors, "
        "no clouds or background patterns, no detailed scenery, no existing mascots or brand characters, no watermark, no captions.",
    ])


def report(rows):
    for name, ok, why in rows:
        print(f"{'PASS' if ok else 'FAIL'}  {name:16} {why}")
    print(f"score {score(rows)}")


def selftest():
    good = {
        "palette": "moss", "canvas": "wide",
        "moment": "A sleepy teapot waits for a cup of tea to cool down on a quiet afternoon.",
        "subjects": [{"what": "a round teapot with a small face", "doing": "peeks at the cup sideways"},
                     {"what": "a tiny snail", "doing": "rests on the teapot lid"}],
        "props": ["a steaming cup"], "accent_on": "a steaming cup",
    }
    assert score(check(good)) == 100, check(good)
    out = build(good)
    assert "#9CB436" in out and "#36301E" in out and "landscape 16:9" in out and "{" not in out
    assert "#C8573A" in build(dict(good, palette="brick")) and "inner 80%" in build(dict(good, canvas="badge"))
    assert "#3E9C93" in build(dict(good, palette="pond"))
    assert score(check(dict(good, accent_on="a"))) < 100 and score(check(dict(good, accent_on="cup"))) == 100
    assert "none beyond" in build(dict(good, props=[], accent_on="snail"))
    bad = dict(good, palette="x", subjects=[{"what": "a girl", "doing": "smiles"}], accent_on="moon",
               moment="A realistic girl.", props=["a", "b", "c", "d", "e"])
    failed = {n for n, ok, _ in check(bad) if not ok}
    assert {"palette", "subject fields", "props", "moment length", "accent target", "no humans", "no banned style"} <= failed, failed
    korean = check(dict(good, moment="찻주전자가 차를 기다린다 조용한 오후 한 장면"))
    assert not {n: ok for n, ok, _ in korean}["english"]
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
