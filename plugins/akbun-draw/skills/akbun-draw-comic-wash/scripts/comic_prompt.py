"""wash 그림체 2·4·6컷 만화: 컷 프롬프트를 쓰고, 생성된 컷 그림에 말풍선·대사·번호를 얹어 묶는다.

  build <comic.json>     채점 후 100점이면 comic.json 옆에 panel_01.txt … 를 쓴다
  check <comic.json>     채점표만 출력
  compose <comic.json>   panel_01.png … 에 말풍선·번호·테두리를 얹어 comic.png(page) 또는 comic_01.png …(1장씩)
  --selftest             자체 검사

그림체·팔레트·캐릭터는 akbun-draw-illust-wash의 라이브러리와 스크립트를 그대로 쓴다.
대사는 이미지 모델이 아니라 이 스크립트가 SIL OFL 글꼴(Gaegu)로 쓴다.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True  # skill 폴더에 __pycache__를 남기지 않는다
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "akbun-draw-illust-wash" / "scripts"))
import wash_prompt as w  # noqa: E402

FORMATS = {  # 이미지 비율 문장, 컷 한 장 크기(px), page 격자 열 수
    "page": {"aspect": "landscape 16:9", "panel": (960, 540)},
    "instagram": {"aspect": "portrait 4:5", "panel": (1080, 1350)},
    "youtube": {"aspect": "square 1:1", "panel": (1080, 1080)},
}
SHOTS = {
    "wide": "Wide shot: characters full body, small in the frame, with a hint of the place.",
    "medium": "Medium shot: characters from the knees up.",
    "close": "Close-up: one character's head and shoulders fill the lower part of the frame.",
}
POS = {"left": 0.22, "center": 0.5, "right": 0.78}  # 캐릭터 가로 위치(컷 폭 비율). 말풍선 꼬리도 여기를 가리킨다
BAND = 0.28  # 말풍선 자리: 컷 위쪽 28%는 그림 없이 비운다
INK, PAPER = (21, 21, 21), (252, 252, 250)
FONT_DIRS = [Path.home() / "Library/Fonts", Path("/Library/Fonts"), Path("/usr/share/fonts")]
FONT_FILE = "Gaegu-Bold.ttf"
MAX_CHARS, MAX_LINES = 12, 2  # 대사 한 줄 글자 수(공백 포함), 말풍선 하나의 줄 수


def check(spec):
    """(항목, 통과 여부, 이유). 점수 = 통과 수 / 항목 수 × 100(내림)."""
    cast = spec.get("cast", [])
    ids = [c.get("id") for c in cast]
    panels = spec.get("panels", [])
    chars = [c for p in panels for c in p.get("chars", [])]
    lines = [ln for p in panels for ln in p.get("lines", [])]
    text = " ".join([c.get("outfit", "") for c in cast] + [p.get("scene", "") + " " + p.get("setting", "") for p in panels]
                    + [c.get("action", "") for c in chars])
    rows = w.common_rows(spec, [{"id": c.get("id"), "action": c.get("outfit", "")} for c in cast], text)
    rows = [r for r in rows if r[0] != "actions"]  # cast에는 action 대신 outfit이 있다
    shots = [p.get("shot") for p in panels]
    return rows + [
        ("format", spec.get("format") in FORMATS, f"format: {sorted(FORMATS)}"),
        ("cast", 1 <= len(cast) <= 3 and all(len(c.get("outfit", "").split()) >= 2 for c in cast),
         f"cast {len(cast)}명, 1~3명, outfit 영어 2단어 이상"),
        ("panel count", len(panels) in (2, 4, 6), f"컷 {len(panels)}개, 2·4·6 중 하나"),
        ("panel cast", bool(chars) and all(c.get("id") in ids for c in chars), "컷의 chars id는 cast 안에서만"),
        ("panel chars", all(1 <= len(p.get("chars", [])) <= 3 and len({c.get("pos") for c in p["chars"]}) == len(p["chars"])
                            and all(c.get("pos") in POS for c in p["chars"]) for p in panels),
         f"컷마다 1~3명, pos는 {sorted(POS)} 중 서로 다르게"),
        ("actions", bool(chars) and all(len(c.get("action", "").split()) >= 3 for c in chars), "action 영어 3단어 이상"),
        ("scenes", all(6 <= len(p.get("scene", "").split()) <= 30 for p in panels), "scene 영어 6~30단어(공백으로 나눈 수)"),
        ("shots", all(s in SHOTS for s in shots) and (len(panels) == 2 or "close" in shots),
         f"shot은 {sorted(SHOTS)}, 4·6컷이면 close 1컷 이상"),
        ("lines", all(len(p.get("lines", [])) <= 2 and {ln.get("who") for ln in p.get("lines", [])} <= {c.get("id") for c in p.get("chars", [])}
                      for p in panels), "컷마다 대사 0~2개, who는 그 컷에 나온 캐릭터"),
        ("line text", all(1 <= len(ln.get("text", "").split("\n")) <= MAX_LINES and all(1 <= len(t) <= MAX_CHARS for t in ln["text"].split("\n"))
                          for ln in lines), f"대사는 \\n으로 나눈 {MAX_LINES}줄 이하, 줄마다 1~{MAX_CHARS}자(공백 포함)"),
    ]


def prompts(spec):
    f = FORMATS[spec["format"]]
    chars = w.load("characters.jsonl")
    outfit = {c["id"]: c["outfit"] for c in spec["cast"]}
    style = w.load("style.jsonl")["medium"]["prompt"].replace("landscape 16:9", f["aspect"])
    out = []
    for i, p in enumerate(spec["panels"], 1):
        who = " ".join(f"{chars[c['id']]['prompt']}, wearing {outfit[c['id']]}, stands in the {c['pos']} third of the frame and {c['action']}."
                       for c in p["chars"])
        out.append("\n\n".join([
            style,
            f"COMIC PANEL {i} of {len(spec['panels'])}. Every panel shows the same characters with exactly the same species, colors and outfits.",
            f"FRAME: {f['aspect']}. Keep the top {round(BAND * 100)}% of the image completely empty white paper; speech bubbles are added there later. "
            + SHOTS[p["shot"]],
            f"SCENE: {p['scene']} Setting: {p.get('setting') or 'just the white page'}.",
            f"CHARACTERS: {who}",
            *w.style_block(spec["palette"]),
            w.DONT + " No speech bubbles, no panel border, no panel number.",
        ]))
    return out


def font(size):
    for d in FONT_DIRS:
        for path in d.rglob(FONT_FILE) if d.exists() else []:
            from PIL import ImageFont
            return ImageFont.truetype(str(path), size)
    sys.exit(f"{FONT_FILE}(SIL OFL)가 없습니다. Google Fonts 공식 배포처에서 Gaegu를 설치한 뒤 다시 실행하세요")


def panel_image(src, size, number, lines, chars):
    """컷 그림을 size로 채워 자르고, 위 띠에 말풍선, 왼쪽 위에 번호, 테두리를 그린다."""
    from PIL import Image, ImageDraw, ImageOps
    W, H = size
    img = ImageOps.fit(Image.open(src).convert("RGB"), size)
    d = ImageDraw.Draw(img)
    fs = round(W * 0.048)
    fnt, pad = font(fs), round(fs * 0.5)
    xs = {c["id"]: POS[c["pos"]] * W for c in chars}
    left = round(W * 0.14)  # 번호 자리를 비운 뒤부터 말풍선을 놓는다
    for k, ln in enumerate(lines):
        text = ln["text"]
        tw = max(d.textlength(t, font=fnt) for t in text.split("\n"))
        th = fs * 1.15 * len(text.split("\n"))
        bw, bh = tw + 2 * pad, th + 2 * pad
        cx = min(max(xs[ln["who"]], left + bw / 2), W - 16 - bw / 2)
        top = H * 0.03 + k * (H * BAND - H * 0.03) / max(len(lines), 1) * 0.55
        box = (cx - bw / 2, top, cx + bw / 2, top + bh)
        base = min(max(xs[ln["who"]], box[0] + bw * 0.25), box[2] - bw * 0.25)
        tip = (base + max(-fs, min(fs, xs[ln["who"]] - base)), box[3] + fs * 1.3)  # 짧은 꼬리, 말하는 쪽으로 기움
        d.polygon([(base - fs * 0.35, box[3] - 2), (base + fs * 0.35, box[3] - 2), tip], fill=PAPER, outline=INK)
        d.rounded_rectangle(box, radius=round(bh / 2), fill=PAPER, outline=INK, width=3)
        d.line([(base - fs * 0.35 + 2, box[3] - 1), (base + fs * 0.35 - 2, box[3] - 1)], fill=PAPER, width=4)
        d.multiline_text((cx, top + pad), text, font=fnt, fill=INK, anchor="ma", align="center", spacing=fs * 0.15)
    r = round(W * 0.035)
    d.ellipse((r, r, 3 * r, 3 * r), fill=INK)
    d.text((2 * r, 2 * r), str(number), font=font(round(r * 1.3)), fill=PAPER, anchor="mm")
    d.rectangle((0, 0, W - 1, H - 1), outline=INK, width=3)
    return img


def compose(spec, folder):
    from PIL import Image
    f = FORMATS[spec["format"]]
    tiles = [panel_image(folder / f"panel_{i:02}.png", f["panel"], i, p.get("lines", []), p["chars"])
             for i, p in enumerate(spec["panels"], 1)]
    if spec["format"] != "page":
        for i, t in enumerate(tiles, 1):
            t.save(folder / f"comic_{i:02}.png")
        return [folder / f"comic_{i:02}.png" for i in range(1, len(tiles) + 1)]
    pw, ph = f["panel"]
    gap, rows = 24, len(tiles) // 2
    page = Image.new("RGB", (2 * pw + 3 * gap, rows * ph + (rows + 1) * gap), PAPER)
    for i, t in enumerate(tiles):  # 읽는 순서: 왼쪽 → 오른쪽, 위 → 아래
        page.paste(t, (gap + (i % 2) * (pw + gap), gap + (i // 2) * (ph + gap)))
    page.save(folder / "comic.png")
    return [folder / "comic.png"]


def selftest():
    good = {"format": "instagram", "palette": "paper-wash",
            "cast": [{"id": "otter", "outfit": "a mustard knit vest"}, {"id": "bear", "outfit": "a denim jacket"}],
            "panels": [{"scene": f"The otter and bear meet at a quiet bus stop, panel {i}.", "shot": "close" if i == 3 else "medium",
                        "chars": [{"id": "otter", "pos": "left", "action": "holds a paper cup"},
                                  {"id": "bear", "pos": "right", "action": "checks a wristwatch twice"}],
                        "lines": [{"who": "otter", "text": "버스 왔어?"}, {"who": "bear", "text": "아직...\n10분 남았대"}]} for i in range(1, 5)]}
    assert w.score(check(good)) == 100, check(good)
    ps = prompts(good)
    assert len(ps) == 4 and "portrait 4:5" in ps[0] and "landscape 16:9" not in ps[0] and "mustard knit vest" in ps[3] and "{" not in ps[0]
    bad = json.loads(json.dumps(good))
    bad["panels"][0]["lines"][0]["text"] = "열두 글자가 넘는 아주 긴 대사"
    bad["panels"][1]["chars"][1]["pos"] = "left"
    bad["panels"][2]["shot"] = "wide"
    bad["panels"] = bad["panels"][:3]
    failed = {n for n, ok, _ in check(bad) if not ok}
    assert {"line text", "panel chars", "panel count"} <= failed, failed
    assert "shots" in {n for n, ok, _ in check(dict(good, panels=[dict(p, shot="wide") for p in good["panels"]])) if not ok}
    from PIL import Image
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        for i in range(1, 5):
            Image.new("RGB", (1024, 1536), (250, 250, 250)).save(t / f"panel_{i:02}.png")
        out = compose(good, t)
        img = Image.open(out[0])
        assert len(out) == 4 and img.size == (1080, 1350)
        assert img.getpixel((1, 600)) == INK and img.crop((0, 0, 1080, 378)).convert("L").getextrema()[0] < 50  # 테두리, 말풍선 선
        page = compose(dict(good, format="page"), t)
        assert Image.open(page[0]).size == (2 * 960 + 72, 2 * 540 + 72)
    print("selftest ok")


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if len(argv) < 2 or argv[0] not in ("build", "check", "compose"):
        sys.exit(__doc__)
    path = Path(argv[1])
    spec = json.loads(path.read_text())
    rows = check(spec)
    w.report(rows)
    if w.score(rows) < 100:
        sys.exit("FAIL 항목을 고친 뒤 다시 실행하세요")
    if argv[0] == "build":
        for i, p in enumerate(prompts(spec), 1):
            (path.parent / f"panel_{i:02}.txt").write_text(p + "\n")
        print(f"panel_01.txt … panel_{len(spec['panels']):02}.txt")
    elif argv[0] == "compose":
        print("\n".join(map(str, compose(spec, path.parent))))


if __name__ == "__main__":
    main(sys.argv[1:])
