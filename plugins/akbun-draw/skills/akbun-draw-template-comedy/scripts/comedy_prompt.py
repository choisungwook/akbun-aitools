"""개그 한 컷 이미지 생성 프롬프트를 comedy spec(JSON)에서 조립하고 검사한다.

  build <spec.json>   검사 후 spec 옆에 같은 이름의 .txt를 쓴다
  check <spec.json>   검사만
  --selftest          자체 검사

그림체는 spec의 style(akbun-draw 스타일 skill)에서 akbun-draw-template-cartoon의 style_parts로 읽는다.
이 skill이 더하는 것은 연출(staging.jsonl)과 개그 유형(gags.jsonl)뿐이다.
"""
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE.parent / "akbun-draw-template-cartoon" / "scripts"))
from cartoon_prompt import BANNED, SKILLS, bad_palette, style_parts  # noqa: E402

REF = HERE / "references"
HANGUL = re.compile("[가-힣]")
DONT = ("DO NOT: no existing mascots or known cartoon characters, nobody is hit or hurt, no blood or weapons, "
        "no written words, captions, speech text, signatures or watermark anywhere in the image.")


def load(name):
    return {r["id"]: r for r in map(json.loads, (REF / name).read_text().splitlines()) if r}


def check(spec):
    """실패 이유 목록. 비면 통과."""
    gags, out = load("gags.jsonl"), []
    g = gags.get(spec.get("gag"))
    style, missing = style_parts(spec)
    e, u = spec.get("endurer", {}), spec.get("unaware", {})
    title, prop = spec.get("title", ""), spec.get("prop", "")
    if not spec.get("style", "").startswith("akbun-draw-") or not (SKILLS / spec["style"]).is_dir():
        out.append(f"style은 akbun-draw 스타일 skill 이름: {spec.get('style')}")
    if len(style.split()) < 10:
        out.append("style skill에 references/style.jsonl이 없으면 style_text(영어 10단어 이상)로 그림체를 적는다")
    if missing:
        out.append(f"fill에 값 필요: {missing}")
    if bad_palette(spec):
        out.append(f"palette는 스타일 skill palettes.jsonl의 id: {spec.get('palette')}")
    if not g:
        out.append(f"gag는 gags.jsonl id: {sorted(gags)}")
    elif (len(prop.split()) < 2) if g["prop"] else prop:
        out.append("prop이 필요한 gag면 영어 2단어 이상, 아니면 빈 문자열")
    if not (8 <= len(title) <= 30 and HANGUL.search(title)):
        out.append(f"title {len(title)}자: 한글이 들어간 8~30자(공백·문장부호 포함)")
    for k, c in (("endurer", e), ("unaware", u)):
        if len(c.get("look", "").split()) < 4 or len(c.get("action", "").split()) < 3:
            out.append(f"{k}: look은 종·색(옷은 스타일 skill 규칙대로)을 담은 영어 4단어 이상, action은 영어 3단어 이상")
    if e.get("look") and e.get("look") == u.get("look"):
        out.append("endurer와 unaware는 서로 다른 look")
    text = " ".join([spec.get("setting", ""), prop] + [c.get(x, "") for c in (e, u) for x in ("look", "action")])
    if not text.isascii():
        out.append("모델이 쓴 영어 글은 ASCII만")
    if BANNED.search(text):
        out.append("폰트 이름·font·typeface를 쓰지 않는다")
    return out


def build(spec):
    staging, g = load("staging.jsonl"), load("gags.jsonl")[spec["gag"]]
    e, u = spec["endurer"], spec["unaware"]
    style, _ = style_parts(spec)
    return "\n\n".join([
        "FORMAT: a single-panel illustration, landscape 16:9.",
        "STAGING: " + " ".join(staging[k]["prompt"] for k in staging if k not in g.get("skip", [])),
        "GAG: " + g["prompt"].format(prop=spec.get("prop", "")),
        f"ENDURING CHARACTER: {e['look']}, {e['action']}.",
        f"UNAWARE CHARACTER: {u['look']}, {u['action']}.",
        f"SETTING: {spec.get('setting') or 'no particular place, the background follows the style'}.",
        f"STYLE: {style}",
        DONT,
    ])


def selftest():
    good = {"title": "조용히 기다려 주는 마음", "gag": "overhead-hold", "style": "akbun-draw-wash", "palette": "warm-room",
            "prop": "a cast-iron frying pan", "setting": "a small kitchen table",
            "endurer": {"look": "a pear-shaped hedgehog in a striped apron", "action": "has waited twenty minutes for the table"},
            "unaware": {"look": "a long-bodied otter in a grey hoodie", "action": "slurps noodles loudly and slowly"}}
    assert check(good) == [], check(good)
    out = build(good)
    assert "cast-iron frying pan" in out and "deadpan" in out and "{" not in out and "striped apron" in out
    assert out.count("16:9") == 1, "스타일 문장의 비율은 지우고 FORMAT 한 번만"
    assert "cannot see it" in out and "cannot see it" not in build(dict(good, gag="mutual-hold"))
    assert check(dict(good, gag="sealed-mouth", prop="")) == []
    assert check(dict(good, style="akbun-draw-moss", palette="moss", fill={"canvas": "landscape 16:9"})) == []
    assert build(dict(good, style="akbun-draw-moss", palette="moss", fill={"canvas": "landscape 16:9"})).count("16:9") == 1
    assert "palette" in " ".join(check(dict(good, palette="no-such")))
    assert "fill" in " ".join(check(dict(good, style="akbun-draw-bori", palette=None)))
    assert check(dict(good, style="akbun-draw-bori", palette=None, fill={"season": "autumn", "line": "#5A4636"})) == []
    assert "style_text" in " ".join(check(dict(good, style="akbun-draw-motion-doodle")))
    bad = dict(good, title="Waiting", gag="sealed-mouth", style="ghibli",
               unaware={"look": "otter in Helvetica font", "action": "x"})
    errs = " ".join(check(bad))
    assert all(k in errs for k in ("title", "prop", "style은", "unaware", "폰트")), errs
    print("selftest ok")


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if len(argv) != 2 or argv[0] not in ("build", "check"):
        sys.exit(__doc__)
    path = Path(argv[1])
    spec = json.loads(path.read_text())
    if errs := check(spec):
        sys.exit("\n".join(["FAIL"] + errs))
    print("PASS")
    if argv[0] == "build":
        path.with_suffix(".txt").write_text(build(spec) + "\n")
        print(path.with_suffix(".txt"))


if __name__ == "__main__":
    main(sys.argv[1:])
