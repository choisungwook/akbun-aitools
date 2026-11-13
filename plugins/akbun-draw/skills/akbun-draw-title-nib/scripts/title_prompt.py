"""nib 스타일 title을 그림 위에 직접 그리게 하는 이미지 편집 프롬프트를 spec(JSON)에서 조립하고 채점한다.
글자는 폰트로 얹지 않는다. 이미지 생성 모델이 그림의 일부로 그린다.

  build <spec.json> [-o prompt.txt]   채점 후 100점이면 프롬프트를 쓴다(없으면 stdout)
  check <spec.json>                   채점표만 출력
  --selftest                          자체 검사

spec의 image 경로는 spec 파일이 있는 폴더 기준이다.
"""
import json
import re
import sys
import tempfile
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"
# 폰트·브랜드를 가리키는 말. 글씨체는 획 모양으로만 묘사한다.
BANNED = (r"\b(fonts?|typefaces?|garamond|helvetica|times new roman|baskerville|caslon|bodoni|futura|didot|nanum|"
          r"pretendard|gaegu|logos?|trademarks?)\b|폰트|글꼴|서체|나눔|로고|™|®|©")


def load(name):
    return {r["id"]: r for r in map(json.loads, (REF / name).read_text().splitlines()) if r}


def luminance(rgb):
    """WCAG 상대 휘도(0~1)."""
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = map(ch, rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def mean_luminance(path):
    from PIL import Image
    return luminance(Image.open(path).convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0)))


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def check(spec, base=Path(".")):
    """(항목, 통과 여부, 이유). 점수 = 통과 수 / 항목 수 × 100(내림)."""
    title, sub = spec.get("title"), spec.get("subtitle", "")
    if not (isinstance(title, str) and isinstance(sub, str) and isinstance(spec.get("image"), str)):
        return [("shape", False, "image·title·subtitle은 문자열")]
    inks = load("inks.jsonl")
    img = base / spec["image"]
    rows = [
        ("image", img.is_file(), f"{img} 파일이 있어야 함"),
        ("ink", spec.get("ink") in inks, f"inks.jsonl id: {sorted(inks)}"),
        ("title length", 1 <= len(title.strip()) <= 20, f"제목 {len(title.strip())}자, 1~20자(공백 포함, 앞뒤 공백 제외, 경계 포함)"),
        ("subtitle length", len(sub.strip()) <= 40, f"부제 {len(sub.strip())}자, 0~40자(공백 포함, 경계 포함)"),
        ("one line each", "\n" not in title + sub, "제목·부제는 각각 한 줄"),
        ("no quotes", '"' not in title + sub, "큰따옴표 금지(프롬프트의 인용 표시와 겹침)"),
        ("no font or brand", not re.search(BANNED, title + " " + sub, re.I), "폰트·브랜드·로고를 가리키는 말 금지"),
    ]
    if rows[0][1] and rows[1][1]:
        try:
            lum = mean_luminance(img)
        except OSError:
            return rows + [("ink contrast", False, f"{img}를 그림으로 열 수 없음")]
        c = contrast(lum, luminance(hex_rgb(inks[spec["ink"]]["hex"])))
        rows.append(("ink contrast", c >= 3, f"잉크와 그림 평균색의 명도 대비 {c:.2f}:1, 3:1 이상(소수 둘째 자리 반올림 표시, 비교는 반올림 전 값)"))
    return rows


def score(rows):
    return sum(ok for _, ok, _ in rows) * 100 // len(rows)


def build(spec):
    style, ink = load("style.jsonl"), load("inks.jsonl")[spec["ink"]]
    color = f"Ink color for all letters: {ink['prompt']} {ink['hex']}."
    text = f'TITLE: "{spec["title"].strip()}"'
    if spec.get("subtitle", "").strip():
        text += f'\nSUBTITLE: "{spec["subtitle"].strip()}"'
    else:
        text += "\nNo subtitle."
    rules = " ".join(style[k]["prompt"] for k in ("title", "subtitle", "finish", "placement", "keep")
                     if k != "subtitle" or spec.get("subtitle", "").strip())
    return "\n\n".join([style["medium"]["prompt"], f"LETTERING: {rules} {color}", text])


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if len(argv) < 2 or argv[0] not in ("build", "check"):
        sys.exit(__doc__)
    path = Path(argv[1])
    spec = json.loads(path.read_text())
    rows = check(spec, path.parent)
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
    from PIL import Image
    assert round(contrast(luminance((255, 255, 255)), luminance((0, 0, 0))), 1) == 21.0
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        Image.new("RGB", (64, 36), (230, 230, 240)).save(t / "light.png")
        Image.new("RGB", (64, 36), (30, 30, 40)).save(t / "dark.png")
        good = {"image": "light.png", "ink": "navy", "title": "기억의 서랍", "subtitle": "인덱스가 길을 찾는 법"}
        assert score(check(good, t)) == 100, check(good, t)
        out = build(good)
        assert '"기억의 서랍"' in out and '"인덱스가 길을 찾는 법"' in out and "#2A3050" in out and "myeongjo" in out
        assert "No subtitle." in build(dict(good, subtitle="")) and "one third" not in build(dict(good, subtitle=""))
        fails = lambda s: {n for n, ok, _ in check(s, t) if not ok}  # noqa: E731
        assert "ink contrast" in fails(dict(good, image="dark.png"))
        assert not fails(dict(good, image="dark.png", ink="cream"))
        assert "image" in fails(dict(good, image="missing.png"))
        assert "title length" in fails(dict(good, title="가" * 21))
        assert "no quotes" in fails(dict(good, title='"제목"'))
        assert "no font or brand" in fails(dict(good, subtitle="Garamond 느낌"))
        assert not fails(dict(good, title="Fontaine Road"))
        (t / "broken.png").write_text("not an image")
        assert "ink contrast" in fails(dict(good, image="broken.png"))
        assert "one line each" in fails(dict(good, title="두 줄\n제목"))
        assert check(dict(good, title=3), t)[0][0] == "shape"
    ex = REF / "example"
    for spec_path in sorted(ex.glob("*.json")):
        assert build(json.loads(spec_path.read_text())).strip() == spec_path.with_suffix(".txt").read_text().strip(), \
            f"{spec_path.name}: 예시 txt를 다시 build 하세요"
    print("selftest ok")


if __name__ == "__main__":
    main(sys.argv[1:])
