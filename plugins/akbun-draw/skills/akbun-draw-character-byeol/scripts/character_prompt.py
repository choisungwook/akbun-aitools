"""페르소나로 만든 캐릭터 spec(JSON)을 byeol 선·채색의 배경 없는 캐릭터 컷 프롬프트로 조립하고 채점한다.

  build <spec.json> [-o prompt.txt]   채점 후 100점이면 프롬프트를 쓴다(없으면 stdout)
  check <spec.json>                   채점표만 출력
  bg <image.png>                      테두리 흰 비율로 배경이 비었는지 검사(Pillow 필요)
  cutout <image.png> <out.png>        테두리에 이어진 흰 배경을 투명으로 바꾼 PNG를 쓴다(Pillow 필요)
  --selftest                          자체 검사

선·채색·인물 문장은 references/style.jsonl에서 가져온다.
"""
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TRAITS = json.loads((SKILL / "references" / "traits.json").read_text())
STYLE = SKILL / "references" / "style.jsonl"
STYLE_KEYS = ("line", "fill", "figures")

ASPECTS = {"portrait": "portrait 3:4", "square": "square 1:1"}
VIEWS = {"front": "seen from the front", "three-quarter": "seen in three-quarter view",
         "side": "seen in side profile", "back": "seen from behind, looking back over the shoulder"}
LOOK_TEXT = ("job", "hair", "eyes", "face", "outfit", "item")
BANNED_STYLE = r"\b(black outlines?|thick outlines?|3d|photorealistic|realistic|photo|chibi|watercolou?r|sketch(y)?|neon)\b"
# 배경을 끌어들이는 말.
BANNED_PLACE = r"\b(background|scenery|room|street|sky|floor|ground|forest|park|beach|city|indoors?|outdoors?|wall|window|sparkles?|glow(ing)?|motes?)\b"
# 고정 외형을 바꾸는 말(행동·자세 글에서).
BANNED_LOOK = r"\b(hair|bangs|freckles?|ponytail|braids?|wig|dyed)\b"
BACKGROUND = ("BACKGROUND: plain pure white (#FFFFFF) filling the whole frame. No scenery, no floor line, "
              "no cast shadow, no glow motes or sparkles, no patterns, no frame. The full body is visible "
              "from head to feet with empty white space on every side.")
BORDER = 0.03      # 테두리 두께 = 짧은 변 × 3%(내림, 최소 1px)
WHITE_TOL = 12     # R·G·B가 모두 255-12 이상이면 흰색
BG_MIN = 0.95      # 테두리 픽셀 중 흰색 비율 0.95 이상(경계 포함)이면 통과


def words(s):
    return len(s.split())


def look_rows(c):
    """캐릭터 외형 필드 채점."""
    text = " ".join(c.get(k, "") for k in LOOK_TEXT)
    return [
        ("name", bool(re.fullmatch(r"[a-z][a-z-]{1,19}", c.get("name", ""))), "name: 영어 소문자·하이픈 2~20자"),
        ("age", c.get("age") in TRAITS["age"], f"age: {sorted(TRAITS['age'])}"),
        ("gender", c.get("gender") in TRAITS["gender"], f"gender: {TRAITS['gender']}"),
        ("build", c.get("build") in TRAITS["build"], f"build: {sorted(TRAITS['build'])}"),
        ("accent", c.get("accent") in TRAITS["accent"], f"accent: {sorted(TRAITS['accent'])}"),
        ("job", 1 <= words(c.get("job", "")) <= 6, f"job {words(c.get('job', ''))}단어, 1~6단어"),
        ("hair", 3 <= words(c.get("hair", "")) <= 15, f"hair {words(c.get('hair', ''))}단어, 3~15단어"),
        ("eyes", 1 <= words(c.get("eyes", "")) <= 4, f"eyes {words(c.get('eyes', ''))}단어, 1~4단어"),
        ("face", words(c.get("face", "")) <= 10, f"face {words(c.get('face', ''))}단어, 0~10단어"),
        ("outfit", 5 <= words(c.get("outfit", "")) <= 30, f"outfit {words(c.get('outfit', ''))}단어, 5~30단어"),
        ("item", 1 <= words(c.get("item", "")) <= 8, f"item {words(c.get('item', ''))}단어, 1~8단어"),
        ("look english", text.isascii(), "외형 글은 영어(ASCII)만(persona는 예외)"),
        ("look style", not re.search(BANNED_STYLE, text, re.I),
         "black/thick outline·3d·photorealistic·realistic·photo·chibi·watercolor·sketch·neon 금지"),
    ]


def look(c):
    """캐릭터 외형 영어 문장."""
    a = TRAITS["age"][c["age"]]
    noun = a["noun"][TRAITS["gender"].index(c["gender"])]
    face = f", {c['face'].rstrip('.')}" if c.get("face") else ""
    return (f"{c['name'].replace('-', ' ').title()}, an original {noun} {a['prompt']}, "
            f"{TRAITS['build'][c['build']]}, works as a {c['job']}: hair {c['hair']}, {c['eyes']} eyes{face}; "
            f"wearing {c['outfit'].rstrip('.')}, with the main garment in {c['accent']} ({TRAITS['accent'][c['accent']]}); "
            f"carries {c['item'].rstrip('.')}")


def check(spec):
    """(항목, 통과 여부, 이유) 목록. 항목 하나 = 1점, 점수 = 통과 수 / 항목 수 × 100(내림)."""
    pose = spec.get("pose", "")
    return look_rows(spec) + [
        ("persona", bool(spec.get("persona", "").strip()), "persona: 사용자가 준 원문, 없으면 지어낸 페르소나 한 줄"),
        ("aspect", spec.get("aspect") in ASPECTS, f"aspect: {sorted(ASPECTS)}"),
        ("view", spec.get("view") in VIEWS, f"view: {sorted(VIEWS)}"),
        ("pose length", 3 <= words(pose) <= 25, f"pose {words(pose)}단어, 3~25단어"),
        ("pose look", not re.search(BANNED_LOOK, pose, re.I), "pose에 hair·bangs·freckle·ponytail·braid·wig·dyed 금지(외형)"),
        ("pose place", not re.search(BANNED_PLACE, pose, re.I), "pose에 장소·배경·빛 말 금지(배경 없음)"),
        ("pose english", pose.isascii() and not re.search(BANNED_STYLE, pose, re.I), "pose는 영어(ASCII), 금지 스타일 낱말 없음"),
    ]


def score(rows):
    return sum(ok for _, ok, _ in rows) * 100 // len(rows)


def build(spec):
    style = {r["id"]: r for r in map(json.loads, STYLE.read_text().splitlines()) if r}
    rules = " ".join(style[k]["prompt"] for k in STYLE_KEYS)
    return "\n\n".join([
        f"Character illustration of one figure alone, {ASPECTS[spec['aspect']]}, polished 2D anime style, "
        "clean and carefully colored like a character sheet.",
        f"CHARACTER: {look(spec)}. The character keeps exactly this look.",
        f"POSE: {VIEWS[spec['view']]}, {spec['pose'].rstrip('.')}. Anything held is small and drawn in the same style.",
        BACKGROUND,
        f"STYLE: {rules}",
        "DO NOT: no background scene, no other characters, no text, no watermark, no photorealism, no 3D, "
        "no chibi proportions, no thick or pure black outlines, no real people, no existing anime, game or brand characters.",
    ])


def bg_ratio(path):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    w, h = im.size
    b = max(1, int(min(w, h) * BORDER))
    px = im.load()
    pts = [(x, y) for y in range(h) for x in range(w) if x < b or y < b or x >= w - b or y >= h - b]
    return sum(all(v >= 255 - WHITE_TOL for v in px[p]) for p in pts) / len(pts)


def cutout(src, dst):
    """테두리에서 출발해 이어진 흰 픽셀(bg와 같은 기준)만 투명으로 바꾼다. 인물 안의 흰 면은 남는다."""
    from collections import deque
    from PIL import Image
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    px = im.load()
    white = lambda p: all(v >= 255 - WHITE_TOL for v in px[p][:3])  # noqa: E731
    seen = bytearray(w * h)
    q = deque(p for p in [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)] if white(p))
    for x, y in q:
        seen[y * w + x] = 1
    while q:
        x, y = q.popleft()
        px[x, y] = (255, 255, 255, 0)
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= n[0] < w and 0 <= n[1] < h and not seen[n[1] * w + n[0]] and white(n):
                seen[n[1] * w + n[0]] = 1
                q.append(n)
    im.save(dst)
    return sum(1 for a in im.getchannel("A").tobytes() if a == 0) / (w * h)


def report(rows):
    for name, ok, why in rows:
        print(f"{'PASS' if ok else 'FAIL'}  {name:14} {why}")
    print(f"score {score(rows)}")


GOOD = {
    "name": "dohee", "persona": "동네 빵집을 하는 40대 제빵사, 늘 밀가루가 묻어 있음",
    "age": "adult", "gender": "female", "build": "sturdy", "accent": "tomato", "job": "neighborhood baker",
    "hair": "dark brown, tied in a low bun under a white kerchief", "eyes": "warm brown",
    "face": "a dusting of flour on one cheek", "outfit": "a tomato-red apron over a cream shirt with rolled sleeves, beige trousers and clogs",
    "item": "a wooden peel with a round loaf", "aspect": "portrait", "view": "three-quarter",
    "pose": "holds the peel forward proudly with a wide grin",
}


def selftest():
    assert score(check(GOOD)) == 100, [r for r in check(GOOD) if not r[1]]
    out = build(GOOD)
    assert "Dohee, an original woman in their late thirties to forties" in out and "#E8604A" in out and "#3B2F4F" in out
    assert "#FFFFFF" in out and "drift through the air" not in out and "{" not in out and "동네" not in out
    assert "an original boy about 8" in look(dict(GOOD, age="child", gender="male"))
    fail = lambda **kw: {n for n, ok, _ in check(dict(GOOD, **kw)) if not ok}
    assert fail(pose="stands in a sunny park") == {"pose place"}
    assert fail(pose="lets her hair down slowly") == {"pose look"}
    assert fail(outfit="a photorealistic red coat and boots") == {"look style"}
    assert fail(face="") == set()
    assert fail(job="park ranger", item="a window squeegee") == set()
    assert {"age", "gender", "build", "accent", "name", "view", "aspect", "persona"} <= fail(
        age="baby", gender="x", build="huge", accent="blue", name="Do Hee", view="top", aspect="wide", persona="")
    try:
        from PIL import Image
    except ImportError:
        print("selftest ok (bg 검사는 Pillow 없어 건너뜀)")
        return
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        im = Image.new("RGB", (200, 200), "white")
        im.paste((232, 96, 74), (60, 40, 140, 190))
        im.save(f"{d}/w.png")
        Image.new("RGB", (200, 200), (138, 192, 204)).save(f"{d}/c.png")
        assert bg_ratio(f"{d}/w.png") >= BG_MIN > bg_ratio(f"{d}/c.png")
        im.paste((255, 255, 255), (90, 90, 110, 110))  # 인물 안 흰 면
        im.save(f"{d}/w.png")
        cutout(f"{d}/w.png", f"{d}/t.png")
        a = Image.open(f"{d}/t.png").getchannel("A")
        assert a.getpixel((0, 0)) == 0 and a.getpixel((100, 100)) == 255 and a.getpixel((70, 60)) == 255
    print("selftest ok")


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if argv[:1] == ["cutout"] and len(argv) == 3:
        print(f"transparent {cutout(argv[1], argv[2]):.3f} -> {argv[2]}")
        return
    if len(argv) < 2 or argv[0] not in ("build", "check", "bg"):
        sys.exit(__doc__)
    if argv[0] == "bg":
        r = bg_ratio(argv[1])
        print(f"{'PASS' if r >= BG_MIN else 'FAIL'}  border white {r:.3f} (기준 {BG_MIN} 이상)")
        sys.exit(0 if r >= BG_MIN else 1)
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
