"""wash 스타일 이미지 생성 프롬프트를 장면 spec(JSON)에서 조립하고 채점한다.

  build <spec.json> [-o prompt.txt]   채점 후 100점이면 프롬프트를 쓴다(없으면 stdout)
  check <spec.json>                   채점표만 출력
  --selftest                          자체 검사

akbun-draw-gag-deadpan의 스크립트가 이 파일의 load·style_block·common_rows를 가져다 쓴다.
"""
import json
import re
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"

# 모델이 쓴 글에 나오면 안 되는 말. 알려진 캐릭터와 닮을 수 있는 종·털 묘사, 사람, 스타일을 깨는 표현.
BANNED_BEINGS = (r"\b(dogs?|pupp(y|ies)|poodles?|sheepdogs?|cats?|kittens?|humans?|person|people|man|men|"
                 r"woman|women|boys?|girls?|child(ren)?|fluffy|white fur)\b")
BANNED_STYLE = r"\b(3d|photorealistic|realistic|anime|chibi|gradients?|neon|vector|cel[- ]shad\w*)\b"
DONT = ("DO NOT: no photorealism, no 3D, no anime or chibi proportions, no clean vector lines, no hard cel shading, "
        "no filled background, no humans, no dogs, no cats, no white fluffy animals, no existing mascots or known "
        "cartoon characters, no written words, captions, speech text or watermark anywhere in the image.")


def load(name, ref=REF):
    return {r["id"]: r for r in map(json.loads, (ref / name).read_text().splitlines()) if r}


def style_block(palette_id):
    """팔레트를 채운 그림체 문단 두 개(색, 스타일)."""
    p, style = load("palettes.jsonl")[palette_id], load("style.jsonl")
    c = p["colors"]
    rules = " ".join(style[k]["prompt"].format(paper=c["paper"], ink=c["ink"]) for k in style if k != "medium")
    colors = "; ".join(f"{k} {v}" for k, v in c.items())
    return [f"COLOR PALETTE ({p['prompt']}): build clothes, objects and shadows mostly from these colors as thin washes: {colors}. Each character keeps its own listed fur, skin or feather color.", f"STYLE: {rules}"]


def who(cast):
    chars = load("characters.jsonl")
    return " ".join(f"{i}. {chars[x['id']]['prompt']}, {x['action']}." for i, x in enumerate(cast, 1))


def common_rows(spec, cast, text):
    """두 skill이 같이 쓰는 항목: 팔레트, 캐릭터 id·행동, 영어, 금지 낱말."""
    chars = load("characters.jsonl")
    ids = [x.get("id") for x in cast]
    return [
        ("palette", spec.get("palette") in load("palettes.jsonl"), f"palettes.jsonl id: {sorted(load('palettes.jsonl'))}"),
        ("character ids", bool(ids) and all(i in chars for i in ids) and len(set(ids)) == len(ids),
         f"characters.jsonl id만, 중복 없이: {ids}"),
        ("actions", bool(cast) and all(len(x.get("action", "").split()) >= 3 for x in cast), "캐릭터마다 action 3단어 이상"),
        ("english", text.isascii(), "모델이 쓴 영어 글은 ASCII만"),
        ("no banned beings", not re.search(BANNED_BEINGS, text, re.I),
         "dog·puppy·poodle·sheepdog·cat·kitten·human·person·people·man·woman·boy·girl·child·fluffy·white fur 금지"),
        ("no banned style", not re.search(BANNED_STYLE, text, re.I),
         "3d·photorealistic·realistic·anime·chibi·gradient·neon·vector·cel shading 금지"),
    ]


def check(spec):
    """(항목, 통과 여부, 이유) 목록. 항목 하나 = 1점, 점수 = 통과 수 / 항목 수 × 100(내림)."""
    cast, props = spec.get("characters", []), spec.get("props", [])
    text = " ".join([spec.get("scene", ""), spec.get("setting", "")] + [c.get("action", "") for c in cast] + props)
    words = len(spec.get("scene", "").split())
    return common_rows(spec, cast, text) + [
        ("character count", 1 <= len(cast) <= 4, f"{len(cast)}명, 1~4명(경계 포함)"),
        ("scene length", 6 <= words <= 40, f"scene {words}단어, 6~40단어(공백으로 나눈 수)"),
        ("props", len(set(props)) == len(props) <= 6, f"소품 {len(props)}개, 0~6개, 중복 없이"),
    ]


def score(rows):
    return sum(ok for _, ok, _ in rows) * 100 // len(rows)


def build(spec):
    style = load("style.jsonl")
    setting = spec.get("setting") or "no particular place, just the white page"
    props = ", ".join(spec.get("props", [])) or "none"
    return "\n\n".join([
        style["medium"]["prompt"],
        f"SCENE: {spec['scene']} Setting: {setting}.",
        f"CHARACTERS ({len(spec['characters'])}): {who(spec['characters'])}",
        f"PROPS (only these, drawn just enough to read): {props}.",
        *style_block(spec["palette"]),
        DONT,
    ])


def report(rows):
    for name, ok, why in rows:
        print(f"{'PASS' if ok else 'FAIL'}  {name:18} {why}")
    print(f"score {score(rows)}")


def run(argv, check, build, selftest):
    """build/check/--selftest 공용 진입점. gag 스크립트도 이걸 쓴다."""
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


def selftest():
    good = {"palette": "paper-wash", "scene": "A tortoise waters balcony plants at dawn while a crow waits for the watering can.",
            "setting": "a narrow apartment balcony", "props": ["a dented watering can", "three clay pots"],
            "characters": [{"id": "tortoise", "action": "tips a watering can slowly"},
                           {"id": "crow", "action": "taps one foot, waiting"}]}
    assert score(check(good)) == 100, check(good)
    out = build(good)
    assert "#FCFCFA" in out and "#151515" in out and "olive shell" in out and "{" not in out
    assert "white page" in build(dict(good, setting=""))
    bad = dict(good, characters=[{"id": "dog", "action": "sits"}], scene="A fluffy cat.", props=["x"] * 7, palette="neon")
    failed = {n for n, ok, _ in check(bad) if not ok}
    assert {"palette", "character ids", "actions", "scene length", "props", "no banned beings"} <= failed, failed
    assert score(check(dict(good, scene=good["scene"] + " Drawn photorealistic."))) < 100
    assert score(check(dict(good, scene="A catalog of category mistakes is read aloud by the otter."))) == 100
    print("selftest ok")


if __name__ == "__main__":
    run(sys.argv[1:], check, build, selftest)
