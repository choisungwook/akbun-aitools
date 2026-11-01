"""bori 스타일 이미지 생성 프롬프트를 장면 spec(JSON)에서 조립하고 채점한다.

  build <spec.json> [-o prompt.txt]   채점 후 100점이면 프롬프트를 쓴다(없으면 stdout)
  check <spec.json>                   채점표만 출력
  --selftest                          자체 검사
"""
import json
import re
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"

# 장면 글에 나오면 안 되는 말. 원본 캐릭터 종과 사람, 스타일을 깨는 표현.
BANNED_BEINGS = r"\b(dogs?|pupp(y|ies)|cats?|kittens?|hamsters?|humans?|person|people|man|men|woman|women|boys?|girls?|child(ren)?)\b"
BANNED_STYLE = r"\b(black outlines?|3d|photorealistic|realistic|anime|gradients?|neon)\b"
SEASONS = ("spring", "summer", "autumn", "winter")
NO_TEXT = "No written words anywhere in the image."
NO_SURFACE_TEXT = "Screens, boards, books, papers and labels show only simple shapes, never letters."
LINE = {False: "#2F4858", True: "#1F3340"}


def load(name):
    return {r["id"]: r for r in map(json.loads, (REF / name).read_text().splitlines()) if r}


def free_text(spec):
    """모델이 직접 쓴 글(라이브러리·간판에서 오지 않은 글)만 모은다."""
    parts = [spec.get("scene", ""), spec.get("setting", "")]
    parts += [c.get("action", "") for c in spec.get("characters", [])]
    parts += spec.get("props", []) + spec.get("lights", [])
    return " ".join(parts)


def check(spec):
    """(항목, 통과 여부, 이유) 목록. 항목 하나 = 1점, 점수 = 통과 수 / 항목 수 × 100(내림)."""
    pal, comp, chars = load("palettes.jsonl"), load("compositions.jsonl"), load("characters.jsonl")
    c = comp.get(spec.get("composition"))
    cs = spec.get("characters", [])
    ids = [x.get("id") for x in cs]
    props, lights, signs = spec.get("props", []), spec.get("lights", []), spec.get("signs", [])
    scene_words = len(spec.get("scene", "").split())
    text = free_text(spec)
    lo, hi = c["chars"] if c else (0, 0)
    return [
        ("palette", spec.get("palette") in pal, f"palettes.jsonl id: {sorted(pal)}"),
        ("composition", c is not None, f"compositions.jsonl id: {sorted(comp)}"),
        ("character count", lo <= len(cs) <= hi, f"{len(cs)}명, 구도 허용 {lo}~{hi}명(경계 포함)"),
        ("character ids", bool(ids) and all(i in chars for i in ids) and len(set(ids)) == len(ids),
         f"characters.jsonl id만, 중복 없이: {ids}"),
        ("actions", bool(cs) and all(len(x.get("action", "").split()) >= 3 for x in cs), "캐릭터마다 action 3단어 이상"),
        ("season", spec.get("season") in SEASONS, f"season: {SEASONS}"),
        ("props", len(set(props)) == len(props) and (c["props_min"] if c else 1) <= len(props) <= 16,
         f"소품 {len(props)}개(중복 없이), {c['props_min'] if c else '?'}~16개(경계 포함)"),
        ("lights", 1 <= len(lights) <= 4, f"광원 {len(lights)}개, 1~4개"),
        ("signs", len(signs) <= 2 and all(1 <= len(s) <= 14 and all(ch.isascii() or "\uac00" <= ch <= "\ud7a3" for ch in s) for s in signs),
         "간판 0~2개, 각 1~14자(공백 포함), 영어·한글"),
        ("scene length", 6 <= scene_words <= 40, f"scene {scene_words}단어, 6~40단어"),
        ("english", text.isascii(), "모델이 쓴 글은 영어(ASCII)만"),
        ("no banned beings", not re.search(BANNED_BEINGS, text, re.I), "dog·puppy·cat·kitten·hamster·human·person·people·man·woman·boy·girl·child 금지"),
        ("no banned style", not re.search(BANNED_STYLE, text, re.I), "black outline·3d·photorealistic·realistic·anime·gradient·neon 금지"),
    ]


def score(rows):
    return sum(ok for _, ok, _ in rows) * 100 // len(rows)


def build(spec):
    style, pal, comp, chars = (load(n) for n in ("style.jsonl", "palettes.jsonl", "compositions.jsonl", "characters.jsonl"))
    p, c = pal[spec["palette"]], comp[spec["composition"]]
    who = " ".join(f"{i}. {chars[x['id']]['prompt']}, {x['action']}." for i, x in enumerate(spec["characters"], 1))
    signs = " ".join(f'A small hand-lettered sign reads "{s}".' for s in spec.get("signs", [])) or NO_TEXT
    fill = {"line": LINE[p["night"]], "season": spec["season"]}
    colors = "; ".join(f"{k} {v}" for k, v in p["colors"].items())
    rules = " ".join(style[k]["prompt"].format(**fill) for k in style if k != "medium")
    return "\n\n".join([
        style["medium"]["prompt"],
        f"COMPOSITION: {c['prompt']}",
        f"SCENE: {spec['scene']} Setting: {spec['setting']}.",
        f"CHARACTERS ({len(spec['characters'])}): {who}",
        f"PROPS: {', '.join(spec['props'])}.",
        f"LIGHT: {', '.join(spec['lights'])}.",
        f"SIGNS: {signs} {NO_SURFACE_TEXT}",
        f"COLOR PALETTE ({p['prompt']}): build the whole image mainly from these colors: {colors}.",
        f"STYLE: {rules}",
        "DO NOT: no photorealism, no 3D, no anime-style big shiny eyes, no thick black outlines, "
        "no heavy gradients on objects, no humans, no dogs, no cats, no hamsters, no existing mascots "
        "or brand characters, no watermark, no captions; written words only on the listed signs.",
    ])


def report(rows):
    for name, ok, why in rows:
        print(f"{'PASS' if ok else 'FAIL'}  {name:18} {why}")
    print(f"score {score(rows)}")


def selftest():
    good = {
        "palette": "lamp-interior", "composition": "wide-room", "season": "autumn",
        "scene": "Neighbors wait for their laundry on a rainy evening, chatting and reading.",
        "setting": "a small laundromat with round washing machines",
        "characters": [{"id": "raccoon", "action": "folds a striped towel on the counter"},
                       {"id": "frog", "action": "reads a paperback on a bench"},
                       {"id": "seal", "action": "watches the machine spin"}],
        "props": [f"prop {i}" for i in range(10)], "lights": ["pendant lamps"], "signs": ["WASH"],
    }
    assert score(check(good)) == 100, check(good)
    out = build(good)
    assert "#EE8B7B" in out and "pear-shaped" not in out and '"WASH"' in out and "#2F4858" in out and "in autumn" in out
    assert "#1F3340" in build(dict(good, palette="night-lights")) and "{" not in out
    assert score(check(dict(good, signs=["붕어빵"]))) == 100
    assert score(check(dict(good, props=["a photorealistic vase"] + good["props"][1:]))) < 100
    assert score(check(dict(good, props=["a photograph frame"] + good["props"][1:]))) == 100
    assert score(check(dict(good, props=["a phone"] + good["props"][1:]))) == 100
    bad = dict(good, characters=[{"id": "dog", "action": "sits"}], signs=["A VERY LONG SIGN TEXT"],
               scene="A cat with black outline.")
    failed = {n for n, ok, _ in check(dict(bad, season="rainy")) if not ok}
    assert {"season", "character count", "character ids", "actions", "signs", "scene length",
            "no banned beings", "no banned style"} <= failed, failed
    assert NO_TEXT in build(dict(good, signs=[]))
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
