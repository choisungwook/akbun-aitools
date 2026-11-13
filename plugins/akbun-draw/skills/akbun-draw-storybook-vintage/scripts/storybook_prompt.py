"""storybook-vintage 스타일 이미지 생성 프롬프트를 장면 spec(JSON)에서 조립하고 채점한다.

  build <spec.json> [-o prompt.txt]   채점 후 100점이면 프롬프트를 쓴다(없으면 stdout)
  check <spec.json>                   채점표만 출력
  --selftest                          자체 검사
"""
import json
import re
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"

# 모델이 쓴 글에 나오면 안 되는 말. 사람(이 스타일에 인물 없음), 옷 입은 동물, 스타일을 깨는 표현.
BANNED_PEOPLE = (r"\b(humans?|person|people|man|men|woman|women|boys?|girls?|child(ren)?|kids?|faces?|"
                 r"portraits?|princess|prince|king|queen|hands?|silhouettes?)\b")
BANNED_DRESSED = r"\b(coats?|jackets?|waistcoats?|vests?|dress(es|ed)?|hats?|gloves?|shoes?|clothes|clothing|wearing)\b"
BANNED_STYLE = (r"\b(photo(graph)?s?|photorealistic|realistic|3d|cgi|render(ed)?|anime|vector|neon|hdr|4k|8k|"
                r"ultra|glossy|cyberpunk)\b")
BANNED_TEXT = r"\b(text|letters?|lettering|words?|titles?|captions?|signs?|signboards?|labels?|logos?|book covers?)\b"
DONT = ("DO NOT: no people, faces, hands or human silhouettes anywhere; no animals wearing clothes; no photograph, "
        "3D, CGI, anime or vector look; no heavy black outlines; no neon or saturated digital colors; no readable "
        "text, letters, titles, logos, captions, frames, borders or watermark anywhere in the image.")


def load(name):
    return {r["id"]: r for r in map(json.loads, (REF / name).read_text().splitlines()) if r}


def check(spec):
    """(항목, 통과 여부, 이유) 목록. 항목 하나 = 1점, 점수 = 통과 수 / 항목 수 × 100(내림)."""
    subjects = spec.get("subjects", [])
    shape = (isinstance(spec.get("scene"), str) and isinstance(spec.get("setting"), str)
             and isinstance(subjects, list) and all(isinstance(x, str) for x in subjects))
    if not shape:
        return [("shape", False, "scene·setting은 문자열, subjects는 문자열 목록")]
    text = " ".join([spec["scene"], spec["setting"]] + subjects)
    words = len(spec.get("scene", "").split())
    palettes = load("palettes.jsonl")
    return [
        ("palette", spec.get("palette") in palettes, f"palettes.jsonl id: {sorted(palettes)}"),
        ("scene length", 6 <= words <= 40, f"scene {words}단어, 6~40단어(공백으로 나눈 수, 경계 포함)"),
        ("setting", bool(spec["setting"].strip()) and not spec["setting"].rstrip().endswith("."),
         "setting은 빈칸 불가, 장소 한 구절, 마침표로 끝내지 않음"),
        ("subjects", 1 <= len(subjects) == len({x.strip().lower() for x in subjects}) <= 5,
         f"소재 {len(subjects)}개, 1~5개(경계 포함), 대소문자·앞뒤 공백 무시하고 중복 없이"),
        ("english", text.isascii(), "모델이 쓴 영어 글은 ASCII만"),
        ("no people", not re.search(BANNED_PEOPLE, text, re.I),
         "human·person·people·man·woman·boy·girl·child·kid·face·portrait·princess·prince·king·queen·hand·silhouette 금지"),
        ("no dressed animals", not re.search(BANNED_DRESSED, text, re.I),
         "coat·jacket·waistcoat·vest·dress·hat·glove·shoe·clothes·clothing·wearing 금지(옷 입은 동물 없음)"),
        ("no banned style", not re.search(BANNED_STYLE, text, re.I),
         "photo·photorealistic·realistic·3d·cgi·render·anime·vector·neon·hdr·4k·8k·ultra·glossy·cyberpunk 금지"),
        ("no text", not re.search(BANNED_TEXT, text, re.I),
         "text·letter·lettering·word·title·caption·sign·signboard·label·logo·book cover 금지(그림 안 글자 없음)"),
    ]


def score(rows):
    return sum(ok for _, ok, _ in rows) * 100 // len(rows)


def build(spec):
    style, p = load("style.jsonl"), load("palettes.jsonl")[spec["palette"]]
    colors = "; ".join(f"{k} {v}" for k, v in p["colors"].items())
    rules = " ".join(style[k]["prompt"] for k in style if k != "medium")
    return "\n\n".join([
        style["medium"]["prompt"],
        f"SCENE: {spec['scene']} Setting: {spec['setting']}.",
        f"SUBJECTS (only these as the readable subjects): {', '.join(spec['subjects'])}.",
        f"PALETTE ({p['prompt']}): paint only with these colors and their mixes: {colors}.",
        f"STYLE: {rules}",
        DONT,
    ])


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if len(argv) < 2 or argv[0] not in ("build", "check"):
        sys.exit(__doc__)
    spec = json.loads(Path(argv[1]).read_text())
    rows = check(spec)
    for name, ok, why in rows:
        print(f"{'PASS' if ok else 'FAIL'}  {name:18} {why}")
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
    ex = REF / "example"
    for spec_path in sorted(ex.glob("*.json")):
        good = json.loads(spec_path.read_text())
        assert score(check(good)) == 100, (spec_path.name, check(good))
        out = build(good)
        assert "sepia" in out and "{" not in out
        assert out.strip() == spec_path.with_suffix(".txt").read_text().strip(), f"{spec_path.name}: 예시 txt를 다시 build 하세요"
    good = json.loads(next(ex.glob("*.json")).read_text())
    bad = dict(good, palette="neon", scene="A girl in coat.", setting="", subjects=["x"] * 6)
    failed = {n for n, ok, _ in check(bad) if not ok}
    assert {"palette", "scene length", "setting", "subjects", "no people", "no dressed animals"} <= failed, failed
    assert score(check(dict(good, scene=good["scene"] + " Rendered in 3d."))) < 100
    assert score(check(dict(good, subjects=["A fox", "a fox "]))) < 100
    assert score(check(dict(good, setting="a quiet room."))) < 100
    assert score(check(dict(good, subjects=["a shop sign"]))) < 100
    assert score(check(dict(good, subjects="a fox"))) == 0
    assert score(check(dict(good, scene="A heron stands among the hats of tall mushrooms by the manor."))) < 100
    assert score(check(dict(good, scene="A heron stands among tall mushrooms by a quiet mossy manor wall."))) == 100
    print("selftest ok")


if __name__ == "__main__":
    main(sys.argv[1:])
