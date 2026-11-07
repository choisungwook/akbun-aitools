"""deadpan 개그 한 컷 이미지 생성 프롬프트를 gag spec(JSON)에서 조립하고 채점한다.

  build <spec.json> [-o prompt.txt]   채점 후 100점이면 프롬프트를 쓴다(없으면 stdout)
  check <spec.json>                   채점표만 출력
  --selftest                          자체 검사

그림체·팔레트·캐릭터는 akbun-draw-illust-wash의 라이브러리와 스크립트를 그대로 쓴다.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True  # skill 폴더에 __pycache__를 남기지 않는다
sys.path.insert(0, str(HERE.parent / "akbun-draw-illust-wash" / "scripts"))
import wash_prompt as w  # noqa: E402

REF = HERE / "references"
HANGUL = re.compile("[가-힣]")


def cast(spec):
    return [spec.get("endurer", {}), spec.get("unaware", {})]


def check(spec):
    """(항목, 통과 여부, 이유). 점수는 wash_prompt.score와 같다."""
    gags = w.load("gags.jsonl", REF)
    g = gags.get(spec.get("gag"))
    title, prop = spec.get("title", ""), spec.get("prop", "")
    text = " ".join([spec.get("setting", ""), prop] + [c.get("action", "") for c in cast(spec)])
    return w.common_rows(spec, cast(spec), text) + [
        ("gag", g is not None, f"gags.jsonl id: {sorted(gags)}"),
        ("prop", (len(prop.split()) >= 2) if (g and g["prop"]) else not prop,
         "prop이 필요한 gag면 영어 2단어 이상, 아니면 빈 문자열"),
        ("title", 8 <= len(title) <= 30 and bool(HANGUL.search(title)) and not title.isascii(),
         f"title {len(title)}자, 한글 8~30자(공백 포함)"),
    ]


def build(spec):
    staging = w.load("staging.jsonl", REF)
    g = w.load("gags.jsonl", REF)[spec["gag"]]
    e, u = spec["endurer"], spec["unaware"]
    chars = w.load("characters.jsonl")
    setting = spec.get("setting") or "no particular place, just the white page"
    return "\n\n".join([
        w.load("style.jsonl")["medium"]["prompt"],
        "STAGING: " + " ".join(staging[k]["prompt"] for k in staging),
        "GAG: " + g["prompt"].format(prop=spec.get("prop", "")),
        f"ENDURING CHARACTER: {chars[e['id']]['prompt']}, {e['action']}.",
        f"UNAWARE CHARACTER: {chars[u['id']]['prompt']}, {u['action']}.",
        f"SETTING: {setting}.",
        *w.style_block(spec["palette"]),
        w.DONT,
    ])


def selftest():
    good = {"title": "조용히 기다려 주는 마음", "gag": "overhead-hold", "palette": "warm-room",
            "prop": "a cast-iron frying pan", "setting": "a small kitchen table",
            "endurer": {"id": "hedgehog", "action": "has waited twenty minutes for the bathroom"},
            "unaware": {"id": "otter", "action": "slurps noodles loudly and slowly"}}
    assert w.score(check(good)) == 100, check(good)
    out = build(good)
    assert "cast-iron frying pan" in out and "#FCFAF6" in out and "deadpan" in out and "{" not in out
    assert w.score(check(dict(good, gag="sealed-mouth", prop=""))) == 100
    bad = dict(good, title="Waiting", gag="sealed-mouth", unaware={"id": "hedgehog", "action": "x"})
    failed = {n for n, ok, _ in check(bad) if not ok}
    assert {"title", "prop", "character ids", "actions"} <= failed, failed
    assert w.score(check(dict(good, prop="a fluffy white dog"))) < 100
    print("selftest ok")


if __name__ == "__main__":
    w.run(sys.argv[1:], check, build, selftest)
