"""hana 스타일 캐릭터 이미지 생성 프롬프트를 spec(JSON)에서 조립하고 채점한다.

  build <spec.json> [-o prompt.txt]   채점 후 100점이면 프롬프트를 쓴다(없으면 stdout)
  check <spec.json>                   채점표만 출력
  --selftest                          자체 검사
"""
import json
import re
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"
BACKDROPS = {"white": "a plain solid pure white (#FFFFFF) backdrop",
             "transparent": "a fully transparent background (PNG with an alpha channel, no backdrop color at all)"}
ASPECTS = {"3:4": "3:4 portrait", "1:1": "1:1 square", "16:9": "16:9 landscape"}
# 인물 칸마다 (최소, 최대) 단어 수. 공백으로 나눈 수, 하이픈으로 이은 말은 한 단어, 경계 포함.
WORDS = {"who": (2, 10), "eye_color": (1, 4), "hair": (3, 15), "outfit": (3, 20), "expression": (2, 10), "pose": (3, 20)}
BANNED_STYLE = r"\b(3d|cgi|photo-?realistic|photographic|realistic|chibi|moe|gradients?|neon|glossy|sparkl\w*|watercolou?r)\b"
BANNED_SCENE = r"\b(background|backdrop|scenery|landscape|sky|street|room|walls?|floor|ground|windows?|counters?|tables?|desks?|buildings?|sea|river|city|harbou?r|shelf|shelves|chairs?|stools?|bench(es)?|sofas?|beds?|stairs?)\b"
BANNED_COPY = r"(in the style of|fan ?art|cosplay|parody|\blogo|\bbrand)"
NO_TEXT = "No written words, letters, numbers or logos anywhere in the image; screens, papers and signs show only simple shapes."


def load(name):
    return {r["id"]: r for r in (json.loads(l) for l in (REF / name).read_text().splitlines() if l.strip())}


def words(s):
    return len(s.split())


def free_text(spec):
    """모델이 직접 쓴 글만 모은다."""
    ch = spec.get("character", {})
    return " ".join([ch.get(k, "") for k in WORDS] + [spec.get("light", "")])


def check(spec):
    """(항목, 통과 여부, 이유) 목록. 항목 하나 = 1점, 점수 = 통과 수 / 항목 수 × 100(내림)."""
    pal, fr, ey = load("palettes.jsonl"), load("framings.jsonl"), load("eyes.jsonl")
    ch = spec.get("character", {})
    text = free_text(spec)
    rows = [
        ("palette", spec.get("palette") in pal, f"palettes.jsonl id: {sorted(pal)}"),
        ("framing", spec.get("framing") in fr, f"framings.jsonl id: {sorted(fr)}"),
        ("aspect", spec.get("aspect") in ASPECTS, f"aspect: {sorted(ASPECTS)}"),
        ("backdrop", spec.get("backdrop") in BACKDROPS, f"backdrop: {sorted(BACKDROPS)}"),
        ("eyes", ch.get("eyes") in ey, f"eyes.jsonl id: {sorted(ey)}"),
    ]
    for k, (lo, hi) in WORDS.items():
        n = words(ch.get(k, ""))
        rows.append((f"character.{k}", lo <= n <= hi, f"{n}단어, {lo}~{hi}단어"))
    rows += [
        ("no setting key", "setting" not in spec, "배경을 그리지 않으므로 setting 키 금지"),
        ("light", 3 <= words(spec.get("light", "")) <= 15, f"{words(spec.get('light', ''))}단어, 3~15단어"),
        ("english", text.isascii(), "모델이 쓴 글은 영어(ASCII)만"),
        ("no quotes", '"' not in text, "큰따옴표 금지(그림 속 글자를 만들지 않음)"),
        ("no banned style", not re.search(BANNED_STYLE, text, re.I),
         "3d·cgi·photorealistic·photographic·realistic·chibi·moe·gradient·neon·glossy·sparkle·watercolor 금지"),
        ("no scene words", not re.search(BANNED_SCENE, text, re.I),
         "배경·장소·가구 낱말(background·sky·street·room·wall·floor·window·counter·table·desk·sea·city 등) 금지"),
        ("no copying", not re.search(BANNED_COPY, text, re.I), "in the style of·fan art·cosplay·parody·logo·brand 금지"),
    ]
    return rows


def score(rows):
    return sum(ok for _, ok, _ in rows) * 100 // len(rows)


def build(spec):
    style, pal, fr, ey = load("style.jsonl"), load("palettes.jsonl"), load("framings.jsonl"), load("eyes.jsonl")
    p, ch = pal[spec["palette"]], spec["character"]
    fill = {"aspect": ASPECTS[spec["aspect"]], "ink": p["colors"]["ink"], "paper": p["colors"]["paper"], "backdrop": BACKDROPS[spec["backdrop"]]}
    colors = "; ".join(f"{k} {v}" for k, v in p["colors"].items())
    rules = " ".join(style[k]["prompt"].format(**fill) for k in style if k != "medium")
    return "\n\n".join([
        style["medium"]["prompt"].format(**fill),
        f"FRAMING: {fr[spec['framing']]['prompt']}",
        f"CHARACTER: {ch['who']}; hair: {ch['hair']}; wearing {ch['outfit']}; expression: {ch['expression']}; pose: {ch['pose']}.",
        f"EYES: {ey[ch['eyes']]['prompt']}, iris color {ch['eye_color']}.",
        f"LIGHT on the character: {spec['light']}.",
        f"COLOR PALETTE ({p['prompt']}): paint the character mainly with these colors; the backdrop stays empty: {colors}.",
        f"STYLE: {rules}",
        f"TEXT: {NO_TEXT}",
        "DO NOT: no 3D render, no photorealism, no modern glossy digital anime shading, no soft gradients on the character, "
        "no chibi, no oversized sparkling eyes, no resemblance to any existing anime, manga or game character, "
        "no scenery or props around the character, no ground shadow, no watermark, no captions, no frame border.",
    ])


def report(rows):
    for name, ok, why in rows:
        print(f"{'PASS' if ok else 'FAIL'}  {name:20} {why}", file=sys.stderr)
    print(f"score {score(rows)}", file=sys.stderr)


def selftest():
    good = {
        "palette": "lamp-amber", "framing": "knee", "aspect": "3:4", "backdrop": "white",
        "character": {"who": "a man in his fifties", "eyes": "droopy", "eye_color": "dark brown", "hair": "short grey crew cut with a receding hairline",
                      "outfit": "a navy work jacket over a knit vest", "expression": "tired but kind half smile",
                      "pose": "stands holding a paper cup of coffee in one hand"},
        "light": "a single warm bulb from the upper left",
    }
    assert score(check(good)) == 100, check(good)
    out = build(good)
    assert "#966C54" in out and "#241E18" in out and "#EDE0CC" in out and "3:4 portrait" in out and "{" not in out and "Knee-up" in out and "BACKGROUND" not in out and "droopy eyes" in out and "never black" in out and "#FFFFFF" in out
    assert "alpha channel" in build(dict(good, backdrop="transparent"))
    assert score(check(dict(good, character=dict(good["character"], eyes="sparkly")))) < 100
    assert "#1E1E24" in build(dict(good, palette="cold-dawn"))
    for k, v in [("backdrop", "grey"), ("aspect", "4:3"), ("framing", "close"), ("palette", "pink")]:
        assert score(check(dict(good, **{k: v}))) < 100, k
    bad_ch = dict(good["character"], hair="black", pose='holds a sign "OPEN" with a glossy 3D look')
    failed = {n for n, ok, _ in check(dict(good, character=bad_ch, light="a café lamp in the style of someone")) if not ok}
    assert {"character.hair", "no quotes", "no banned style", "english", "no copying"} <= failed, failed
    assert score(check(dict(good, light="photorealistic soft daylight"))) < 100
    assert score(check(dict(good, light="soft daylight from a branch-lined path"))) == 100  # brand만 막고 branch는 허용
    assert score(check(dict(good, setting="a kiosk"))) < 100  # 배경 키는 받지 않는다
    leans = dict(good["character"], pose="leans on a counter with one elbow")
    assert score(check(dict(good, character=leans))) < 100
    sits = dict(good["character"], pose="sits on a wooden stool")
    assert score(check(dict(good, character=sits))) < 100  # 가구·장소 낱말은 막는다
    print("selftest ok")


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if len(argv) < 2 or argv[0] not in ("build", "check") or argv[-1] == "-o":
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
