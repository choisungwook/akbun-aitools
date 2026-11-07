"""overcast 인물 사진 이미지 생성 프롬프트를 spec(JSON)에서 조립하고 채점한다.

  build <spec.json> [-o prompt.txt]   채점 후 100점이면 프롬프트를 쓴다(없으면 stdout)
  check <spec.json>                   채점표만 출력
  --selftest                          자체 검사
"""
import json
import re
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"
ASPECTS = ("4:5", "9:16")

# 모델이 쓴 글에 나오면 안 되는 말: 실존 인물 닮음, 미성년, 노출, 스타일을 깨는 빛·보정·매체.
BANNED_PEOPLE = (r"\b(celebrit(y|ies)|famous|idol|look-?alike|resembl\w*|in the style of|child(ren)?|kids?|"
                 r"teen\w*|boys?|girls?|minors?|nude|naked|lingerie|sexy)\b")
BANNED_STYLE = (r"\b(studio|flash|neon|hdr|golden hour|sunset|sunlight|sunny|backlit|anime|cartoon|"
                r"illustration|painting|3d|render)\b")
DONT = ("DO NOT: no text, signs, logos or watermark anywhere; no camera, photographer or other people in frame; "
        "no direct sun, flash, studio backdrop or colored gels; no heavy retouching or plastic skin; no HDR, "
        "no oversaturation, no strong vignette; the person must not resemble any real or famous person.")


def load(name):
    return {r["id"]: r for r in map(json.loads, (REF / name).read_text().splitlines()) if r}


def check(spec):
    """(항목, 통과 여부, 이유) 목록. 항목 하나 = 1점, 점수 = 통과 수 / 항목 수 × 100(내림)."""
    props = spec.get("props", [])
    text = " ".join([spec.get("subject", ""), spec.get("pose", ""), spec.get("setting", "")] + props)
    subject_words, pose_words = len(spec.get("subject", "").split()), len(spec.get("pose", "").split())
    return [
        ("palette", spec.get("palette") in load("palettes.jsonl"), f"palettes.jsonl id: {sorted(load('palettes.jsonl'))}"),
        ("shot", spec.get("shot") in load("shots.jsonl"), f"shots.jsonl id: {sorted(load('shots.jsonl'))}"),
        ("aspect", spec.get("aspect") in ASPECTS, f"aspect는 {ASPECTS} 중 하나"),
        ("subject length", 8 <= subject_words <= 40, f"subject {subject_words}단어, 8~40단어(공백으로 나눈 수, 경계 포함)"),
        ("pose length", 4 <= pose_words <= 25, f"pose {pose_words}단어, 4~25단어(경계 포함)"),
        ("setting", bool(spec.get("setting", "").strip()), "setting은 비우지 않는다"),
        ("props", len(set(props)) == len(props) <= 3, f"소품 {len(props)}개, 0~3개, 중복 없이"),
        ("english", text.isascii(), "모델이 쓴 영어 글은 ASCII만"),
        ("no banned people", not re.search(BANNED_PEOPLE, text, re.I),
         "celebrity·famous·idol·lookalike·resemble·in the style of·child·kid·teen·boy·girl·minor·nude·naked·lingerie·sexy 금지"),
        ("no banned style", not re.search(BANNED_STYLE, text, re.I),
         "studio·flash·neon·hdr·golden hour·sunset·sunlight·sunny·backlit·anime·cartoon·illustration·painting·3d·render 금지"),
    ]


def score(rows):
    return sum(ok for _, ok, _ in rows) * 100 // len(rows)


def build(spec):
    style = load("style.jsonl")
    pal = load("palettes.jsonl")[spec["palette"]]
    colors = "; ".join(f"{k} {v}" for k, v in pal["colors"].items())
    if pal.get("prompt"):
        colors = f"{pal['prompt']}; {colors}"
    rules = " ".join(style[k]["prompt"].format(colors=colors) for k in style if k != "medium")
    props = ", ".join(spec.get("props", [])) or "none"
    return "\n\n".join([
        style["medium"]["prompt"].format(aspect=spec["aspect"]),
        f"SUBJECT: {spec['subject']}, {load('shots.jsonl')[spec['shot']]['prompt']}. Pose: {spec['pose']}.",
        f"SETTING: {spec['setting']}. PROPS (only these): {props}.",
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
    good = json.loads((REF / "example" / "01_bookshop-break.json").read_text())
    assert score(check(good)) == 100, check(good)
    out = build(good)
    assert "#9A6A58" in out and "head to toe" in out and "vertical 4:5" in out and "{" not in out
    bad = dict(good, palette="neon", shot="wide", aspect="1:1", subject="a famous idol girl", pose="x",
               setting="", props=["a", "b", "c", "d"])
    failed = {n for n, ok, _ in check(bad) if not ok}
    assert {"palette", "shot", "aspect", "subject length", "pose length", "setting", "props", "no banned people"} <= failed, failed
    assert "form-tie holes" in build(dict(good, palette="warm-concrete"))
    assert score(check(dict(good, setting="a sunny wall at golden hour"))) < 100
    assert score(check(dict(good, pose="stands by the studio wall, girlish smile"))) < 100  # 'studio' 걸림
    assert score(check(dict(good, subject=good["subject"] + " with flashy rings"))) == 100  # flash는 낱말 단위
    print("selftest ok")


if __name__ == "__main__":
    main(sys.argv[1:])
