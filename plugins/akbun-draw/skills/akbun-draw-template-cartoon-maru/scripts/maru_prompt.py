"""인스타툰(한 박자 = 한 장, 세로 4:5) 이미지 생성 프롬프트를 maru spec(JSON)에서 조립하고 검사한다.

  build <maru.json>   검사 후 maru.json 옆에 maru_01.txt …(박자마다 1장)
  check <maru.json>   검사만
  --selftest          자체 검사

그림체는 spec의 style(akbun-draw 스타일 skill)에서 akbun-draw-template-cartoon의 style_parts로 읽는다.
이 skill이 더하는 것은 연출: 페이지 규칙(page.jsonl), 박자마다 고르는 샷(shots.jsonl), 말풍선 종류(bubbles.jsonl)다.
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
HEX = re.compile(r"#[0-9A-Fa-f]{6}")
MAX_CHARS, MAX_CAPTION, MAX_TOTAL = 12, 16, 60  # 대사 한 줄, 내레이션 한 줄, 한 장 전체 한글 글자 수(공백·문장부호 포함)
LETTERING = ("LETTERING: every letter is written by hand directly into the artwork with the same brush pen and the same line color as the drawing, "
             "as if a person wrote it stroke by stroke in a diary comic. Each Hangul stroke has a visible start and a softly tapered end; strokes are "
             "slightly uneven in length and angle; syllables vary a little in size and sit on a gently wavering baseline. The letters are never perfectly "
             "regular, geometric or machine-uniform, and have no outline and no shadow. Narration uses the same handwriting, a little larger. "
             "Write each Korean text exactly as given, character by character, with correct Hangul spelling. "
             "Do not add any other words, letters, captions, signatures or watermarks anywhere.")
DONT = "DO NOT: no panel border lines, no existing mascots or known cartoon characters, no watermark or signature."


def load(name):
    return {r["id"]: r for r in (json.loads(ln) for ln in (REF / name).read_text().splitlines() if ln.strip())}


def rows(text):
    return text.split("\n") if text else []


def check(spec):
    """실패 이유 목록. 비면 통과."""
    shots, kinds, out = load("shots.jsonl"), load("bubbles.jsonl"), []
    cast, beats = spec.get("cast", []), spec.get("beats", [])
    names = {c.get("name") for c in cast}
    style, missing = style_parts(spec)
    if not spec.get("style", "").startswith("akbun-draw-") or not (SKILLS / spec["style"]).is_dir():
        out.append(f"style은 akbun-draw 스타일 skill 이름: {spec.get('style')}")
    if len(style.split()) < 10:
        out.append("style skill에 references/style.jsonl이 없으면 style_text(영어 10단어 이상)로 그림체를 적는다")
    if missing:
        out.append(f"fill에 값 필요: {missing}")
    if bad_palette(spec):
        out.append(f"palette는 스타일 skill palettes.jsonl의 id: {spec.get('palette')}")
    if not 1 <= len(cast) <= 3 or len(names) != len(cast) or "narrator" in names or any(len(c.get("look", "").split()) < 4 for c in cast):
        out.append("cast 1~3명, name 중복 없이(narrator 금지), look은 종·색·옷을 담은 영어 4단어 이상")
    bubbles = [c["bubble"] for c in cast if "bubble" in c]
    if any(not HEX.fullmatch(str(x)) for x in bubbles) or len(set(map(str.upper, map(str, bubbles)))) != len(bubbles):
        out.append("cast.bubble은 #RRGGBB, 캐릭터마다 다른 색")
    if not 2 <= len(beats) <= 10:
        out.append(f"beats는 2~10개: {len(beats)}")
    seq = [b.get("shot") for b in beats]
    if any(s not in shots for s in seq):
        out.append(f"shot은 shots.jsonl id: {sorted(shots)}")
    if any(seq[i] == seq[i + 1] == seq[i + 2] for i in range(len(seq) - 2)):
        out.append("같은 shot을 3장 연달아 쓰지 않는다")
    if len(beats) >= 4 and len(set(seq)) < 3:
        out.append("beats가 4개 이상이면 shot을 3종류 이상 쓴다")
    for i, b in enumerate(beats, 1):
        lines, cap, sfx, shot = b.get("lines", []), b.get("caption", ""), b.get("sfx", ""), b.get("shot")
        if shot == "caption-only":
            if not cap or lines or sfx:
                out.append(f"{i}번 caption-only는 caption만 쓰고 lines·sfx는 뺀다")
        elif not 6 <= len(b.get("scene", "").split()) <= 40:
            out.append(f"{i}번 scene은 영어 6~40단어(공백으로 나눈 수, 경계 포함)")
        lo, hi = (3, 5) if shot == "rapid-fire" else (0, 3)
        if not lo <= len(lines) <= hi:
            out.append(f"{i}번 {shot} 대사는 {lo}~{hi}개: {len(lines)}")
        if len(rows(cap)) > 2 or not all(1 <= len(r) <= MAX_CAPTION for r in rows(cap)):
            out.append(f"{i}번 caption은 \\n으로 나눈 2줄 이하, 줄마다 1~{MAX_CAPTION}자")
        for ln in lines:
            k, who = ln.get("kind", "say"), ln.get("who")
            if k not in kinds:
                out.append(f"{i}번 kind는 bubbles.jsonl id: {sorted(kinds)}")
            elif (who != "narrator") if k == "box" else (who not in names):
                out.append(f"{i}번 who '{who}': box는 narrator, 나머지는 cast의 name")
            if not 1 <= len(rows(ln.get("text", ""))) <= 2 or not all(1 <= len(r) <= MAX_CHARS for r in rows(ln.get("text", ""))):
                out.append(f"{i}번 대사 '{ln.get('text')}': \\n으로 나눈 2줄 이하, 줄마다 1~{MAX_CHARS}자")
        if len(sfx) > 6 or "\n" in sfx:
            out.append(f"{i}번 sfx는 한 줄 1~6자(공백·문장부호 포함)")
        if shot == "reaction" and not sfx:
            out.append(f"{i}번 reaction은 sfx가 필요하다")
        total = len(cap.replace("\n", "")) + len(sfx) + sum(len(ln.get("text", "").replace("\n", "")) for ln in lines)
        if total > MAX_TOTAL:
            out.append(f"{i}번 글자 합 {total}자: 한 장 {MAX_TOTAL}자 이하(caption·대사·sfx, 줄바꿈 제외)")
    english = " ".join([spec.get("style_text", "")] + [c.get("look", "") for c in cast] + [b.get("scene", "") + " " + b.get("place", "") for b in beats])
    if not english.isascii():
        out.append("style_text·cast.look·scene·place는 영어(ASCII)만")
    if BANNED.search(english):
        out.append("font·typeface 낱말을 쓰지 않는다. 글씨는 LETTERING 문장이 획 모양으로 정한다")
    return out


def quote(text):
    return f'"{text.replace(chr(10), " / ")}"' + (" (two lines, break at /)" if "\n" in text else "")


def beat_text(i, n, b, spec, style):
    shots, kinds, page = load("shots.jsonl"), load("bubbles.jsonl"), load("page.jsonl")
    color = {c["name"]: c.get("bubble", "white") for c in spec["cast"]}
    head = [f"FORMAT: image {i} of {n} of one episode, portrait 4:5."]
    if b["shot"] == "caption-only":
        return head + ["PAGE: a plain page in the same paper color as the other images of the episode, with no scene area, no background block, no characters and no drawings.",
                       shots[b["shot"]]["prompt"], f"CAPTION: {quote(b['caption'])}", LETTERING, DONT]
    parts = head + ["PAGE: " + " ".join(r["prompt"] for r in page.values()), shots[b["shot"]]["prompt"], f"STYLE: {style}"]
    lines = b.get("lines", [])
    seen = [c for c in spec["cast"] if re.search(rf"(?i)\b{re.escape(c['name'])}\b", b["scene"])
            or any(ln["who"] == c["name"] and ln.get("kind", "say") not in ("offscreen", "box") for ln in lines)]
    parts.append("CHARACTERS (draw only these, nobody else, not even on screens or pictures): "
                 + " ".join(f"The {c['name']} is {c['look']}." for c in seen))
    if b.get("place"):
        parts.append(f"PLACE: {b['place']}.")
    parts.append(f"SCENE: {b['scene']}")
    parts.append(f"CAPTION: {quote(b['caption'])}" if b.get("caption") else "CAPTION: none.")
    bubbles = [f"{j}. {kinds[ln.get('kind', 'say')]['prompt']}"
               + ("" if ln.get("kind") == "box" else f" from the {ln['who']}, filled {color[ln['who']]}")
               + f", containing exactly: {quote(ln['text'])}." for j, ln in enumerate(b.get("lines", []), 1)]
    parts.append("BUBBLES in reading order: " + (" ".join(bubbles) if bubbles else "none."))
    if b.get("sfx"):
        parts.append(f'SOUND EFFECT, hand-lettered large without a bubble: "{b["sfx"]}".')
    return parts + [LETTERING, DONT]


def prompts(spec):
    style, _ = style_parts(spec)
    n = len(spec["beats"])
    return [(f"maru_{i:02}", "\n\n".join(beat_text(i, n, b, spec, style))) for i, b in enumerate(spec["beats"], 1)]


def selftest():
    good = json.loads((REF / "example" / "maru.json").read_text())
    assert check(good) == [], check(good)
    ps = prompts(good)
    assert [n for n, _ in ps] == [f"maru_{i:02}" for i in range(1, len(good["beats"]) + 1)]
    assert all("portrait 4:5" in p and "{" not in p and "16:9" not in p for _, p in ps)
    cap = next(p for (_, p), b in zip(ps, good["beats"]) if b["shot"] == "caption-only")
    assert "CHARACTERS" not in cap and "BUBBLES" not in cap and "STYLE" not in cap
    assert "filled #FBE1C8" in ps[0][1] and "filled white" in ps[3][1] and "one third" not in ps[1][1]
    assert "cast.bubble" in " ".join(check(dict(good, cast=[dict(c, bubble="#FBE1C8") for c in good["cast"]])))
    noreact = json.loads(json.dumps(good)); noreact["beats"][3].pop("sfx")
    assert "reaction은 sfx" in " ".join(check(noreact))
    assert all("stroke by stroke" in p and not BANNED.search(p) for _, p in ps), "글씨는 획으로 묘사하고 font 낱말을 쓰지 않는다"
    assert "manager" not in ps[3][1] and "cardigan" not in ps[0][1] and "cardigan" in ps[4][1], "그 장에 나오지 않는 인물·그림 밖 화자는 넣지 않는다"
    bad = json.loads(json.dumps(good))
    bad["beats"][0]["lines"] = [{"who": "ghost", "text": "열두 글자가 넘는 아주 긴 대사"}]
    bad["beats"][1]["shot"] = "rapid-fire"
    bad["beats"][1]["lines"] = bad["beats"][1]["lines"][:1]
    bad["beats"][2]["caption"] = "열여섯 글자를 훌쩍 넘겨 버리는 긴 내레이션"
    bad["cast"][0]["look"] = "a kid in Helvetica font shirt"
    errs = " ".join(check(bad))
    assert all(k in errs for k in ("who 'ghost'", "줄마다 1~12자", "rapid-fire 대사는 3~5개", "caption은", "font·typeface")), errs
    same = dict(good, beats=[dict(good["beats"][0], shot="two-shot") for _ in range(4)])
    assert "3장 연달아" in " ".join(check(same)) and "3종류" in " ".join(check(same))
    assert "style_text" in " ".join(check(dict(good, style="akbun-draw-motion-doodle")))
    assert "palette" in " ".join(check(dict(good, palette="no-such")))
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
        for name, text in prompts(spec):
            (path.parent / f"{name}.txt").write_text(text + "\n")
            print(path.parent / f"{name}.txt")


if __name__ == "__main__":
    main(sys.argv[1:])
