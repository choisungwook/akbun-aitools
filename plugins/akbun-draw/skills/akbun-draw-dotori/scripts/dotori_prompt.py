"""dotori 스타일 이미지 생성 프롬프트를 spec(JSON)에서 조립하고 채점한다.

  build <spec.json> [-o prompt.txt]   채점 후 100점이면 프롬프트를 쓴다(없으면 stdout)
  check <spec.json>                   채점표만 출력
  --selftest                          자체 검사
"""
import json
import re
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"
BANNED_STYLE = r"\b(3d|photorealistic|realistic|anime|gradients?|neon|shading|glossy|watercolou?r|font|typeface)\b"
NO_TEXT = "No written words, letters, numbers or speech bubbles anywhere in the image."


def load(name):
    return {r["id"]: r for r in (json.loads(ln) for ln in (REF / name).read_text().splitlines() if ln.strip())}


def free_text(spec):
    """모델이 직접 쓴 글만 모은다."""
    parts = [spec.get("moment", ""), spec.get("accent_on", "")]
    parts += [c.get("what", "") + " " + c.get("doing", "") for c in spec.get("characters", [])]
    return " ".join(parts + spec.get("props", []))


def check(spec):
    """(항목, 통과 여부, 이유) 목록. 항목 하나 = 1점, 점수 = 통과 수 / 항목 수 × 100(내림)."""
    pal, can = load("palettes.jsonl"), load("canvases.jsonl")
    chars, props = spec.get("characters", []), spec.get("props", [])
    words = len(spec.get("moment", "").split())
    text = free_text(spec)
    accent = spec.get("accent_on", "").lower()
    named = [c.get("what", "").lower() for c in chars] + [p.lower() for p in props]
    return [
        ("palette", spec.get("palette") in pal, f"palettes.jsonl id: {sorted(pal)}"),
        ("canvas", spec.get("canvas") in can, f"canvases.jsonl id: {sorted(can)}"),
        ("character count", 1 <= len(chars) <= 3, f"캐릭터 {len(chars)}명, 1~3명(경계 포함)"),
        ("character fields", bool(chars) and all(len(c.get("what", "").split()) >= 2 and len(c.get("doing", "").split()) >= 2 for c in chars),
         "캐릭터마다 what·doing 각 영어 2단어 이상"),
        ("props", len(props) <= 2 and len(set(props)) == len(props), f"소품 {len(props)}개(중복 없이), 0~2개"),
        ("moment length", 6 <= words <= 30, f"moment {words}단어, 6~30단어"),
        ("accent target", accent not in ("", "a", "an", "the") and any(re.search(rf"\b{re.escape(accent)}\b", n) for n in named),
         "accent_on은 characters.what 또는 props 한 항목에 낱말 단위로 들어 있는 말(관사만은 안 됨)"),
        ("english", text.isascii(), "모델이 쓴 글은 영어(ASCII)만"),
        ("no banned style", not re.search(BANNED_STYLE, text, re.I), "3d·realistic·anime·gradient·neon·shading·glossy·watercolor·font 금지"),
    ]


def score(rows):
    return sum(ok for _, ok, _ in rows) * 100 // len(rows)


def build(spec):
    style, pal, can = load("style.jsonl"), load("palettes.jsonl"), load("canvases.jsonl")
    c = pal[spec["palette"]]["colors"]
    chars = " ".join(f"{i}. {x['what']}, {x['doing']}." for i, x in enumerate(spec["characters"], 1))
    props = f"PROPS: {', '.join(spec['props'])}." if spec.get("props") else "PROPS: none."
    colors = "; ".join(f"{k} {v}" for k, v in c.items())
    rules = " ".join(style[k]["prompt"].format(**c) for k in style if k != "medium")
    return "\n\n".join([
        f"{style['medium']['prompt']} {can[spec['canvas']]['prompt']}.",
        f"MOMENT: {spec['moment']}",
        f"CHARACTERS ({len(spec['characters'])}): {chars}",
        props,
        f"ACCENT: only {spec['accent_on']} is colored {c['accent']}.",
        f"COLOR PALETTE: build the picture from these colors: {colors}. Any other color stays soft and pastel.",
        f"STYLE: {rules}",
        f"TEXT: {NO_TEXT}",
        "DO NOT: no realistic proportions or faces, no 3D, no gradients or soft shading, no detailed scenery, "
        "no colored patch or panel behind the characters, no thick heavy outlines, no existing mascots or known cartoon characters, no watermark.",
    ])


def report(rows):
    for name, ok, why in rows:
        print(f"{'PASS' if ok else 'FAIL'}  {name:16} {why}")
    print(f"score {score(rows)}")


def selftest():
    good = {
        "palette": "dotori", "canvas": "portrait",
        "moment": "A kid waits by the microwave, counting the last seconds with both hands on the door.",
        "characters": [{"what": "a small kid in a striped sweater", "doing": "presses both mittens on the microwave"}],
        "props": ["a microwave"], "accent_on": "striped sweater",
    }
    assert score(check(good)) == 100, check(good)
    out = build(good)
    assert "portrait 4:5" in out and "#FBE1C8" in out and "#2E9E8F" in out and "{" not in out
    assert "#E8743B" in build(dict(good, palette="soda")) and "#4C7FC0" in build(dict(good, palette="peach"))
    assert "landscape 16:9" in build(dict(good, canvas="wide")) and "PROPS: none" in build(dict(good, props=[]))
    bad = dict(good, palette="x", characters=[{"what": "kid", "doing": "waits"}], accent_on="moon",
               moment="A realistic kid.", props=["a", "b", "c"])
    failed = {n for n, ok, _ in check(bad) if not ok}
    assert {"palette", "character fields", "props", "moment length", "accent target", "no banned style"} <= failed, failed
    assert not dict((n, ok) for n, ok, _ in check(dict(good, moment="전자레인지 앞에서 마지막 초를 세는 아이 한 장면")))["english"]
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
        if argv.index("-o") + 1 >= len(argv):
            sys.exit("-o 뒤에 출력 파일 경로가 필요합니다")
        Path(argv[argv.index("-o") + 1]).write_text(out + "\n")
    else:
        print(out)


if __name__ == "__main__":
    main(sys.argv[1:])
