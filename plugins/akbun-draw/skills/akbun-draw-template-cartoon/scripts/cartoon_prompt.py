"""만화 템플릿 + 기존 akbun-draw 그림체로 이미지 생성 프롬프트를 조립한다.

  build <cartoon.json>   검사 후 cartoon.json 옆에 cartoon.txt(한 장) 또는 cartoon_01.txt …(컷마다 1장)
  check <cartoon.json>   검사만
  --selftest             자체 검사

글자(대사·효과음·컷 번호)는 폰트로 얹지 않는다. 이미지 생성 모델이 그림의 일부로 직접 쓴다.
그림체는 스타일 skill의 references/style.jsonl·palettes.jsonl을 읽어 넣고, 없으면 spec의 style_text를 쓴다.
"""
import json
import re
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
SKILLS = Path(__file__).resolve().parents[2]

TEMPLATES = {  # 컷 수 → 한 장의 비율과 배치. per_panel이면 컷마다 1장
    "4koma": {4: ("portrait 2:3", "four equal-height panels stacked in one column, read top to bottom")},
    "grid": {2: ("landscape 16:9", "two equal panels side by side, read left then right"),
             4: ("landscape 3:2", "a 2x2 grid of four equal panels, read left to right, then top to bottom"),
             6: ("portrait 2:3", "a 3-row by 2-column grid of six equal panels, read left to right, then top to bottom")},
    "instagram": {n: ("portrait 4:5", None) for n in range(2, 11)},
    "youtube": {n: ("square 1:1", None) for n in range(2, 11)},
}
MAX_CHARS, MAX_LINES, MAX_SFX = 12, 2, 6  # 대사 한 줄 글자 수(공백·문장부호 포함), 말풍선 줄 수, 효과음 글자 수
BANNED = re.compile(r"(?i)\b(font|typeface|typography)\b")  # 글씨체는 폰트 이름이 아니라 획 모양으로 묘사한다
ASPECT = re.compile(r"(?i)\s*(single[- ]panel\s*|,?\s*(landscape|portrait|square)\s+\d+:\d+)")
LETTERING = ("LETTERING: every letter is hand-lettered as part of the artwork, drawn with the same pen and medium as the lines "
             "of the illustration: rounded, slightly uneven hand strokes of even weight; the letters themselves have no outline and no shadow. "
             "Write each Korean text exactly as given, character by character, with correct Hangul spelling. "
             "Do not add any other words, letters, captions, signatures or watermarks anywhere.")


def style_parts(spec):
    """(그림체 문장, 남은 {자리표시자} 목록)."""
    ref = SKILLS / spec.get("style", "") / "references"
    if not (ref / "style.jsonl").is_file():
        return spec.get("style_text", ""), []
    rows = [json.loads(ln) for ln in (ref / "style.jsonl").read_text().splitlines() if ln.strip()]
    pals = [json.loads(ln) for ln in (ref / "palettes.jsonl").read_text().splitlines() if ln.strip()] if (ref / "palettes.jsonl").is_file() else []
    pal = next((p for p in pals if p["id"] == spec.get("palette")), pals[0] if pals else {})
    fill = {k: v for k, v in pal.items() if isinstance(v, str)} | pal.get("colors", {}) | spec.get("fill", {})
    text = " ".join(r["prompt"] for r in rows)
    missing = sorted(set(re.findall(r"\{(\w+)\}", text)) - set(fill))
    text = ASPECT.sub("", re.sub(r"\{(\w+)\}", lambda m: fill.get(m[1], m[0]), text))
    if pal.get("colors"):
        text += " COLOR PALETTE: " + "; ".join(f"{k} {v}" for k, v in pal["colors"].items()) + "."
    return text, missing


def bad_palette(spec):
    """palette를 적었는데 스타일 skill palettes.jsonl에 그 id가 없으면 True. 빼면 첫 줄을 쓰므로 False."""
    f = SKILLS / spec.get("style", "") / "references" / "palettes.jsonl"
    if not spec.get("palette") or not f.is_file():
        return False
    return spec["palette"] not in {json.loads(ln)["id"] for ln in f.read_text().splitlines() if ln.strip()}


def check(spec):
    """실패 이유 목록. 비면 통과."""
    t = TEMPLATES.get(spec.get("template"))
    if not t:
        return [f"template은 {sorted(TEMPLATES)} 중 하나"]
    cast, panels, out = spec.get("cast", []), spec.get("panels", []), []
    names = {c.get("name") for c in cast}
    style, missing = style_parts(spec)
    if not (SKILLS / spec.get("style", "-")).is_dir() or not spec["style"].startswith("akbun-draw-"):
        out.append(f"style은 akbun-draw 스타일 skill 이름: {spec.get('style')}")
    if len(style.split()) < 10:
        out.append("style skill에 references/style.jsonl이 없으면 style_text(영어 10단어 이상)로 그림체를 적는다")
    if missing:
        out.append(f"fill에 값 필요: {missing}")
    if bad_palette(spec):
        out.append(f"palette는 스타일 skill palettes.jsonl의 id: {spec.get('palette')}")
    if len(panels) not in t:
        out.append(f"{spec['template']} 컷 수는 {sorted(t)} 중 하나: {len(panels)}")
    if not 1 <= len(cast) <= 3 or len(names) != len(cast) or any(len(c.get("look", "").split()) < 4 for c in cast):
        out.append("cast 1~3명, name 중복 없이, look은 종·색·옷을 담은 영어 4단어 이상")
    for i, p in enumerate(panels, 1):
        if not 6 <= len(p.get("scene", "").split()) <= 40:
            out.append(f"{i}번 컷 scene은 영어 6~40단어(공백으로 나눈 수)")
        lines = p.get("lines", [])
        if len(lines) > 2 or any(ln.get("who") not in names for ln in lines):
            out.append(f"{i}번 컷 대사는 0~2개, who는 cast의 name")
        for ln in lines:
            rows = ln.get("text", "").split("\n")
            if not 1 <= len(rows) <= MAX_LINES or not all(1 <= len(r) <= MAX_CHARS for r in rows):
                out.append(f"{i}번 컷 대사 '{ln.get('text')}': \\n으로 나눈 {MAX_LINES}줄 이하, 줄마다 1~{MAX_CHARS}자")
        if len(p.get("sfx", "")) > MAX_SFX or "\n" in p.get("sfx", ""):
            out.append(f"{i}번 컷 sfx는 한 줄 {MAX_SFX}자 이하")
    english = " ".join([style] + [c.get("look", "") for c in cast] + [p.get("scene", "") for p in panels])
    if BANNED.search(english):
        out.append("폰트 이름·font·typeface를 쓰지 않는다. 글씨는 LETTERING 문장이 획 모양으로 정한다")
    return out


def panel_text(i, p, cast):
    look = {c["name"]: c["look"] for c in cast}
    bubbles = " ".join(f'A hand-drawn speech bubble near the top of the panel with its tail pointing to the {ln["who"]}, '
                       f'containing exactly: "{ln["text"].replace(chr(10), " / ")}"' + (" (two lines, break at /)." if "\n" in ln["text"] else ".")
                       for ln in p.get("lines", []))
    sfx = f' A sound effect written large without a bubble: "{p["sfx"]}".' if p.get("sfx") else ""
    who = " ".join(f"The {n} is {look[n]}." for n in look if re.search(rf"\b{re.escape(n)}\b", p["scene"] + " ".join(ln["who"] for ln in p.get("lines", []))))
    return f"PANEL {i}: small hand-drawn number \"{i}\" in a circle at the top-left corner. {p['scene']} {who} {bubbles or 'No speech bubble.'}{sfx}"


def prompts(spec):
    t = TEMPLATES[spec["template"]][len(spec["panels"])]
    style, _ = style_parts(spec)
    cast = "CHARACTERS (identical in every panel, same species, colors, outfit and proportions): " + " ".join(
        f"The {c['name']} is {c['look']}." for c in spec["cast"])
    head = [f"STYLE: {style}", cast]
    tail = [LETTERING, "Leave the top quarter of each panel calm so the speech bubbles do not cover faces."]
    if t[1]:
        frame = f"FORMAT: one comic page, {t[0]}, with {t[1]}. Thin hand-drawn panel borders with even white gutters."
        return [("cartoon", "\n\n".join([frame] + head + [panel_text(i, p, spec["cast"]) for i, p in enumerate(spec["panels"], 1)] + tail))]
    n = len(spec["panels"])
    return [(f"cartoon_{i:02}", "\n\n".join(
        [f"FORMAT: comic panel {i} of {n}, {t[0]}, one panel filling the image with a thin hand-drawn border."] + head
        + [panel_text(i, p, spec["cast"])] + tail)) for i, p in enumerate(spec["panels"], 1)]


def selftest():
    good = {"template": "4koma", "style": "akbun-draw-wash",
            "cast": [{"name": "otter", "look": "a small brown otter in a mustard knit vest"},
                     {"name": "bear", "look": "a big grey bear in a denim jacket"}],
            "panels": [{"scene": f"The otter and the bear wait at a quiet bus stop, moment {i}.",
                        "lines": [{"who": "otter", "text": "버스 왔어?"}, {"who": "bear", "text": "아직...\n10분 남았대"}]} for i in range(4)]}
    assert check(good) == [], check(good)
    (name, p), = prompts(good)
    assert name == "cartoon" and "portrait 2:3" in p and "16:9" not in p and "Single-panel" not in p and "{" not in p
    assert p.count("mustard knit vest") >= 2 and '"아직... / 10분 남았대"' in p and 'number "4"' in p
    ig = prompts(dict(good, template="instagram"))
    assert [n for n, _ in ig] == [f"cartoon_0{i}" for i in range(1, 5)] and "portrait 4:5" in ig[0][1]
    bad = json.loads(json.dumps(good))
    bad["panels"][0]["lines"][0]["text"] = "열두 글자가 넘는 아주 긴 대사"
    bad["panels"][1]["lines"][0]["who"] = "cat"
    bad["cast"][0]["look"] = "otter in Helvetica font shirt"
    bad["panels"] = bad["panels"][:3]
    errs = " ".join(check(bad))
    assert all(k in errs for k in ("컷 수", "줄마다", "who는", "폰트")), errs
    assert "style_text" in " ".join(check(dict(good, style="akbun-draw-motion-doodle")))
    assert check(dict(good, style="akbun-draw-motion-doodle", style_text="black ink doodle lines on white paper with flat orange fills and grey shadow ellipses")) == []
    assert "fill" in " ".join(check(dict(good, style="akbun-draw-bori")))  # season 같은 값은 spec이 채운다
    assert check(dict(good, style="akbun-draw-bori", fill={"season": "autumn", "line": "#5A4636"})) == []
    assert "palette" in " ".join(check(dict(good, palette="no-such")))
    moss = prompts(dict(good, style="akbun-draw-moss", palette="moss", fill={"canvas": "landscape 16:9"}))[0][1]
    assert "16:9" not in moss, "자리표시자로 들어온 비율도 지운다"
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
