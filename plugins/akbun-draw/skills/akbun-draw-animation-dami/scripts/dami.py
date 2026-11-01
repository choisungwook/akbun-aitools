# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow"]
# ///
"""dami 애니메이션: 이야기 spec(JSON)을 채점하고, 배역 시트·컷·자세 프롬프트와 codex.sh를 쓰고, 9:16 영상으로 렌더한다.

  check <story.json>                 채점표만 출력(100점이 아니면 종료 코드 1)
  prompts <story.json>               100점이면 spec 옆에 cast_<id>.txt, NN_<id>.txt, NN_<id>_<k>.txt, codex.sh를 쓴다
  render <story.json> [-o out.mp4]   spec 옆 PNG들로 영상과 sheet.jpg를 만든다
  --selftest                         자체 검사
"""
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"
BANNED_STYLE = r"\b(outlines?|line ?art|3d|photorealistic|realistic|anime|chibi|neon|cel[- ]shaded)\b"
BANNED_TEXT_PROPS = r"\b(signs?|signboards?|labels?|posters?|banners?|menus?|newspapers?|texts?|letters?|words?|numbers?|captions?)\b"
CAPTION_CHARS = re.compile(r"^[가-힣 ,.!?…·0-9]+$")
PICKED = ("gender", "age", "height", "build", "face", "skin")  # 참고 배역과 비교하는 고르는 특징
W, H, FPS, FADE = 1080, 1920, 30, 3
PANEL_Y, CAP_Y, CAP_PITCH, CAP_SIZE = 216, 1336, 62, 44
FONT_DIRS = [Path.home() / "Library/Fonts", Path("/Library/Fonts"), Path.home() / ".local/share/fonts", Path("/usr/share/fonts")]
STYLE_SHEET = ("shape", "texture", "figures", "mood")  # 캐릭터 시트에 넣는 그림체 규칙


def load(name):
    return {r["id"]: r for r in map(json.loads, (REF / name).read_text().splitlines()) if r}


def words(s):
    return len(s.split())


def cast_rows(c, traits, refs):
    """배역 한 명의 (항목, 통과 여부, 이유) 목록."""
    free = c.get("hair", "") + " " + c.get("outfit", "")
    same = [r for r, ref in refs.items() if sum(c.get(k) == ref[k] for k in PICKED) > len(PICKED) - 2]
    return [
        ("id", bool(re.fullmatch(r"p(-[a-z]+)+", c.get("id", ""))), "배역 id는 p-영어소문자, 하이픈 가능(예: p-clerk, p-night-nurse)"),
        ("traits", all(c.get(k) in traits[k]["options"] for k in traits),
         "traits.jsonl의 gender·age·height·build·face·skin·color 값만: " + str({k: c.get(k) for k in traits})),
        ("hair", 2 <= words(c.get("hair", "")) <= 12, "hair 영어 2~12단어"),
        ("outfit", 3 <= words(c.get("outfit", "")) <= 14, "outfit 영어 3~14단어"),
        ("no red", not re.search(r"\b(red|crimson|scarlet)\b", free, re.I) and free.isascii(), "hair·outfit은 영어, 붉은색 금지(붉은색은 accent 전용)"),
        ("no banned style", not re.search(BANNED_STYLE, free, re.I), "hair·outfit에 outline·line art·3d·realistic·anime·chibi·neon 금지"),
        ("new face", not same, f"참고 배역과 gender·age·height·build·face·skin 중 2개 이상 달라야 함: {same}"),
    ]


def shot_rows(s, pal, cam, cast_ids, names):
    """한 컷의 (항목, 통과 여부, 이유) 목록. 영어 칸에는 배역·참고 배역 id를 쓰지 않는다(그림 모델은 id를 모른다)."""
    c = cam.get(s.get("camera"))
    cs = s.get("characters", [])
    ids = [x.get("id") for x in cs]
    lo, hi = c["chars"] if c else (0, 0)
    cap = s.get("caption", [])
    poses = s.get("poses", [])
    text = " ".join([s.get("scene", ""), s.get("setting", ""), s.get("accent", "")] + poses
                    + [x.get("action", "") for x in cs] + s.get("props", []))
    return [
        ("palette", s.get("palette") in pal, f"palettes.jsonl id: {sorted(pal)}"),
        ("camera", c is not None, f"cameras.jsonl id: {sorted(cam)}"),
        ("character count", lo <= len(cs) <= hi, f"{len(cs)}명, 카메라 허용 {lo}~{hi}명(경계 포함)"),
        ("character ids", bool(ids) and all(i in cast_ids for i in ids) and len(set(ids)) == len(ids),
         f"cast의 id만, 중복 없이: {ids}"),
        ("actions", bool(cs) and all(words(x.get("action", "")) >= 3 for x in cs), "인물마다 action 3단어 이상"),
        ("scene length", 6 <= words(s.get("scene", "")) <= 40, f"scene {words(s.get('scene', ''))}단어, 6~40"),
        ("props", 2 <= len(set(s.get("props", []))) == len(s.get("props", [])) <= 10, "소품 2~10개, 중복 없이"),
        ("no text props", not re.search(BANNED_TEXT_PROPS, " ".join(s.get("props", []) + [s.get("accent", "")]), re.I),
         "글자가 보이는 소품(sign·label·poster·banner·menu·newspaper·text·letter·word·number·caption) 금지"),
        ("accent", 1 <= words(s.get("accent", "")) <= 6, "붉은 물체 하나, 영어 1~6단어"),
        ("seconds", 2.5 <= s.get("seconds", 0) <= 4.5, f"{s.get('seconds')}초, 2.5~4.5(경계 포함)"),
        ("caption", 1 <= len(cap) <= 2 and all(2 <= len(x) <= 16 and CAPTION_CHARS.match(x) for x in cap),
         f"자막 1~2줄, 줄마다 2~16자(공백·문장부호 포함), 한글·숫자·공백·, . ! ? … ·만(따옴표 금지): {cap}"),
        ("poses", len(poses) <= 3 and all(3 <= words(p) <= 40 for p in poses), "poses는 0~3개, 각 영어 3~40단어(공백으로 나눈 수)"),
        ("english", text.isascii(), "모델이 쓴 영어 칸은 ASCII만"),
        ("no ids in english", not re.search(r"(?<![\w-])(" + "|".join(map(re.escape, names)) + r")(?![\w-])", text, re.I),
         "scene·action·poses·accent에 id 대신 생김새나 역할(the woman in the mustard cardigan)"),
        ("no banned style", not re.search(BANNED_STYLE, text, re.I), "outline·line art·3d·realistic·anime·chibi·neon 금지"),
    ]


def check(story):
    pal, cam, traits, refs = (load(n) for n in ("palettes.jsonl", "cameras.jsonl", "traits.jsonl", "characters.jsonl"))
    shots, cast = story.get("shots", []), story.get("cast", [])
    ids = [s.get("id", "") for s in shots]
    cast_ids = [c.get("id") for c in cast]
    used = {x.get("id") for s in shots for x in s.get("characters", [])}
    rows = [
        ("shot count", 1 <= len(shots) <= 12, f"{len(shots)}컷, 1~12"),
        ("shot ids", all(re.fullmatch(r"[a-z0-9-]+", i) for i in ids) and len(set(ids)) == len(ids),
         f"영어 소문자·숫자·하이픈, 중복 없이: {ids}"),
        ("cast count", 1 <= len(cast) <= 4 and len(set(cast_ids)) == len(cast_ids), f"배역 {len(cast)}명, 1~4명, id 중복 없이"),
        ("cast used", set(cast_ids) == used, f"배역은 모두 한 컷 이상 나오고 컷 인물은 모두 배역: {sorted(set(cast_ids) ^ used)}"),
        ("camera runs", not any(len({x.get("camera") for x in shots[i:i + 4]}) == 1 for i in range(len(shots) - 3)),
         "같은 카메라를 연달아 4컷 이상 쓰지 않음"),
        ("ending", bool(shots) and (shots[-1].get("caption") or [""])[-1].rstrip(" .!?…").endswith("니다"),
         "마지막 컷 마지막 줄은 -ㅂ니다/-습니다로 맺음(뒤 문장부호 제외)"),
    ]
    for c in cast:
        rows += [(f"{c.get('id')}: {n}", ok, why) for n, ok, why in cast_rows(c, traits, refs)]
    names = [i for i in cast_ids if i] + list(refs)
    for s in shots:
        rows += [(f"{s.get('id')}: {n}", ok, why) for n, ok, why in shot_rows(s, pal, cam, cast_ids, names)]
    return rows


def score(rows):
    return sum(ok for _, ok, _ in rows) * 100 // len(rows)


def describe(c):
    """배역 특징 → 영어 인물 묘사. 컷·시트 프롬프트가 같은 문장을 쓴다."""
    t = {k: v["options"][c[k]] for k, v in load("traits.jsonl").items()}
    article = "an" if t["age"][0] in "aeiou" else "a"
    return (f"{article} {t['age']} {t['gender']}, {t['height']} with a {t['build']} build, a {t['face']} face and {t['skin']} skin, "
            f"{c['hair']}, wearing {c['outfit']} mainly in {t['color']}")


def sheet_prompt(c):
    style = load("style.jsonl")
    rules = " ".join(style[k]["prompt"] for k in STYLE_SHEET)
    return "\n\n".join([
        style["medium"]["prompt"],
        f"CHARACTER SHEET: one full-body front view of {describe(c)}. Standing in a relaxed neutral pose, whole body visible "
        "from head to shoes, centered on a plain pale haze background (#CCC6C2). No other people, no props, no scenery.",
        f"STYLE: {rules}",
        "DO NOT: no outlines or ink lines, no photorealism, no 3D render, no anime big shiny eyes, no chibi, "
        "no existing film, cartoon or brand characters, no written words, letters or labels anywhere, no watermark.",
    ])


def shot_names(story):
    return [f"{i:02d}_{s['id']}" for i, s in enumerate(story["shots"], 1)]


def prompt(s, cast):
    style, pal, cam = (load(n) for n in ("style.jsonl", "palettes.jsonl", "cameras.jsonl"))
    p, c = pal[s["palette"]], cam[s["camera"]]
    near = {"passing-foreground": ", standing closest to the camera and cut off by the frame edge",
            "close-detail": ", seen only as hands and sleeves"}.get(s["camera"], "")
    who = " ".join(f"{i}. {describe(cast[x['id']])}{near if i == 1 else ''}, {x['action']}."
                   for i, x in enumerate(s["characters"], 1))
    rules = " ".join(style[k]["prompt"].format(ambient=p["ambient"], warm=p["warm"], accent=s["accent"])
                     for k in style if k != "medium")
    colors = "; ".join(f"{k} {v}" for k, v in p["colors"].items())
    return "\n\n".join([
        style["medium"]["prompt"],
        f"CAMERA: {c['prompt']}",
        f"SCENE: {s['scene']} Setting: {s['setting'].rstrip('.')}.",
        f"CHARACTERS ({len(s['characters'])}): {who} The attached character sheet images show these people in the same "
        "order; match each one's face, hair, body shape and clothes exactly.",
        f"PROPS: {', '.join(s['props'])}.",
        f"COLOR PALETTE: build the whole image mainly from these colors: {colors}.",
        f"STYLE: {rules}",
        "DO NOT: no outlines or ink lines, no photorealism, no 3D render, no anime big shiny eyes, no chibi, "
        "no existing film, cartoon or brand characters, no written words, letters or captions anywhere, no watermark.",
    ])


def pose_prompt(name, pose):
    return (f"Edit the first attached image ({name}.png). Keep everything identical: painting style, colors, lighting, "
            "camera framing, background, props and every character's face, body and clothes (the other attached images are "
            f"their character sheets). Change only the pose to this: {pose} Square 1:1, no written words.")


def keys(name, s):
    """컷의 열쇠 그림 파일 이름 목록: 첫 장 + 자세마다 한 장."""
    return [name] + [f"{name}_{k}" for k in range(2, len(s.get("poses", [])) + 2)]


def codex_script(story):
    """3단계(배역 시트 → 컷 첫 장 → 자세)를 단계마다 동시에 돌리는 codex.sh. 이미 있는 PNG는 건너뛴다.
    파일 이름은 채점을 통과한 id(영어 소문자·숫자·하이픈)로만 만든다."""
    def line(stem, task, attach):
        files = "".join(f" -i {a}.png" for a in attach)
        return (f'[ -s {stem}.png ] || codex exec --skip-git-repo-check -s workspace-write "Read {stem}.txt. Use your built-in '
                f'image generation tool{" " + task if task else ""} with that file\'s full text as the prompt, square 1:1. Save the result as '
                f'{stem}.png here. Reply with the path only."{files} < /dev/null > {stem}.log 2>&1 &')
    sheets = [f"cast_{c['id']}" for c in story["cast"]]
    stage1 = [line(n, "", []) for n in sheets]
    stage2, stage3, every = [], [], list(sheets)
    for name, s in zip(shot_names(story), story["shots"]):
        refs = [f"cast_{x['id']}" for x in s["characters"]]
        stage2.append(line(name, "", refs))
        stage3 += [line(k, "to edit the attached images", [name] + refs) for k in keys(name, s)[1:]]
        every += keys(name, s)
    out = ["#!/bin/bash", "# dami.py prompts가 만든 파일. 출력 폴더에서 bash codex.sh로 돌린다. 잘못 나온 그림은 PNG를 지우고 다시 돌린다.",
           'cd "$(dirname "$0")"']
    for title, stage in (("배역 시트", stage1), ("컷 첫 장", stage2), ("자세", stage3)):
        if stage:
            out += [f"echo '{title} {len(stage)}장'", *stage, "wait"]
    out += [f"for f in {' '.join(every)}; do [ -s $f.png ] || {{ echo \"없음: $f.png ($f.log 확인)\"; exit 1; }}; done",
            "echo '모든 그림 완료'"]
    return "\n".join(out) + "\n"


def find_font(name="Pretendard-Regular"):
    for d in FONT_DIRS:
        for f in d.rglob(f"{name}.*") if d.exists() else []:
            if f.suffix.lower() in (".otf", ".ttf"):
                return f
    sys.exit(f"{name} 글꼴이 없습니다. SIL OFL 글꼴 Pretendard를 설치한 뒤 다시 실행하세요.")


def schedule(n, count):
    """n프레임 컷에 열쇠 그림 count장을 같은 간격으로 놓는다. 프레임마다 (그림 번호, 앞 그림과 섞는 비율 0~1 또는 None)과
    시트용 가운데 프레임 집합을 돌려준다. 그림 i는 ceil(n*i/count) 프레임에서 시작하고 처음 FADE 프레임 동안 교차 전환한다."""
    seg = n / count
    starts = [math.ceil(seg * i - 1e-9) for i in range(count)]
    plan = []
    for f in range(n):
        i = max(j for j in range(count) if starts[j] <= f)
        local = f - starts[i]
        plan.append((i, (local + 1) / (FADE + 1) if i and local < FADE else None))
    return plan, {int(seg * i + seg / 2) for i in range(count)}


def frames(story, root, font):
    """(프레임, 시트에 넣을지) 생성기. 컷 사이는 하드컷, 컷 안에서는 천천히 밀어 들어가며
    열쇠 그림을 같은 간격으로 넘긴다. 넘길 때 FADE 프레임 동안 교차 전환한다."""
    from PIL import Image, ImageDraw, ImageFont
    cam = load("cameras.jsonl")
    ft = ImageFont.truetype(str(font), CAP_SIZE)
    for name, s in zip(shot_names(story), story["shots"]):
        imgs = [Image.open(root / f"{k}.png").convert("RGB").resize((W, W), Image.LANCZOS) for k in keys(name, s)]
        base = Image.new("RGB", (W, H), "#FFFFFF")
        d = ImageDraw.Draw(base)
        for i, line in enumerate(s["caption"]):
            d.text((W // 2, CAP_Y + i * CAP_PITCH), line, font=ft, fill="#1A1A1A", anchor="ma")
        n = round(s["seconds"] * FPS)
        plan, mids = schedule(n, len(imgs))
        drift = cam[s["camera"]]["drift"]
        for f, (i, mix) in enumerate(plan):
            img = imgs[i] if mix is None else Image.blend(imgs[i - 1], imgs[i], mix)
            z = 1 + drift * f / max(n - 1, 1)
            m = round(W * (1 - 1 / z) / 2)
            panel = img.crop((m, m, W - m, W - m)).resize((W, W), Image.LANCZOS) if m else img
            frame = base.copy()
            frame.paste(panel, (0, PANEL_Y))
            yield frame, f in mids


def render(story, root, out):
    from PIL import Image
    font = find_font()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg가 없습니다. 설치한 뒤 다시 실행하세요(macOS: brew install ffmpeg).")
    out.parent.mkdir(parents=True, exist_ok=True)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(out)],
                           stdin=subprocess.PIPE)
    thumbs, written = [], 0
    for frame, mid in frames(story, root, font):
        enc.stdin.write(frame.tobytes())
        written += 1
        if mid:
            thumbs.append(frame.resize((270, 480)))
    enc.stdin.close()
    if enc.wait():
        sys.exit("ffmpeg 인코딩 실패")
    sheet = Image.new("RGB", (270 * len(thumbs), 480), "#FFFFFF")
    for i, m in enumerate(thumbs):
        sheet.paste(m, (270 * i, 0))
    sheet.save(out.with_name("sheet.jpg"), quality=88)
    want = sum(round(s["seconds"] * FPS) for s in story["shots"])
    print(f"{out} H.264 {W}x{H} {FPS}fps {written}프레임 ({written / FPS:.1f}s), {out.with_name('sheet.jpg')}")
    if written != want:
        sys.exit(f"프레임 수 불일치: 쓴 {written} != 컷 길이 합 × {FPS} = {want}")


def report(rows):
    for name, ok, why in rows:
        if not ok:
            print(f"FAIL  {name:28} {why}")
    print(f"score {score(rows)} ({sum(ok for _, ok, _ in rows)}/{len(rows)})")


def selftest():
    lead = {"id": "p-commuter", "gender": "man", "age": "twenties", "height": "very-tall", "build": "thin", "face": "long",
            "skin": "tan", "hair": "a short messy fringe", "outfit": "a long padded coat and wide trousers", "color": "slate-blue"}
    shot = {"id": "late-bus", "palette": "night-blue", "camera": "locked-wide",
            "scene": "A tired commuter waits alone at a foggy bus stop after midnight.",
            "setting": "an empty bus stop under a flickering lamp",
            "characters": [{"id": "p-commuter", "action": "checks the timetable twice"}],
            "props": ["bus stop shelter", "street lamp"], "accent": "a red scarf",
            "caption": ["막차는 이미", "떠난 뒤였습니다…"], "seconds": 3.5}
    walk = dict(shot, id="walk", poses=["The tall man turns away from the shelter.", "The tall man walks off into the fog."])
    good = {"cast": [lead], "shots": [shot, walk]}

    def fails(story):
        return {n.split(": ")[-1] for n, ok, _ in check(story) if not ok}
    assert score(check(good)) == 100, [r for r in check(good) if not r[1]]
    cast = {lead["id"]: lead}
    p = prompt(shot, cast)
    assert "#A81C1C" in p and "a red scarf" in p and "street light" in p and "{" not in p and "slate blue #5A6B80" in p
    assert "an elderly man" in prompt(shot, {"p-commuter": dict(lead, age="elderly")})
    assert "Cool, dim blue night" in p and "overcast" not in p and "very tall with a thin, bony build" in p
    two = {"p-commuter": lead, "p-friend": dict(lead, id="p-friend")}
    fg = prompt(dict(shot, camera="passing-foreground", characters=[{"id": "p-friend", "action": "walks past slowly"}, shot["characters"][0]]), two)
    assert fg.count("cut off by the frame edge") == 2
    assert "hands and sleeves" in prompt(dict(shot, camera="close-detail"), cast)
    assert ".." not in prompt(dict(shot, setting="a stop at 5 a.m."), cast)
    assert "plain pale haze background" in sheet_prompt(lead) and "COLOR PALETTE" not in sheet_prompt(lead)
    assert keys("02_walk", walk) == ["02_walk", "02_walk_2", "02_walk_3"]
    plan, mids = schedule(99, 4)  # 3.3초 컷, 4장
    starts = [f for f, (i, _) in enumerate(plan) if f and plan[f - 1][0] != i]
    assert starts == [25, 50, 75] and len(plan) == 99 and mids == {12, 37, 61, 86}, (starts, mids)
    for s0 in starts:  # 넘길 때마다 정확히 FADE 프레임, 비율 1/4·2/4·3/4
        assert [plan[s0 + k][1] for k in range(FADE + 1)] == [0.25, 0.5, 0.75, None]
    assert schedule(30, 1) == ([(0, None)] * 30, {15})
    sh = codex_script(good)
    assert sh.index("cast_p-commuter.txt") < sh.index("01_late-bus.txt") < sh.index("02_walk_2.txt")
    assert "-i 02_walk.png -i cast_p-commuter.png" in sh and sh.count("wait") == 3
    assert "Change only the pose to this: The tall man" in pose_prompt("02_walk", walk["poses"][0])
    # 실패해야 하는 것
    assert "new face" in fails(dict(good, cast=[dict(lead, gender="woman", age="twenties", height="tall", build="thin", face="heart", skin="light")]))
    assert not fails(dict(good, cast=[dict(lead, gender="woman", age="twenties", height="tall", build="thin", face="round", skin="tan")]))
    assert "no red" in fails(dict(good, cast=[dict(lead, outfit="a long red coat and boots")]))
    assert "no banned style" in fails(dict(good, cast=[dict(lead, outfit="a neon anime jacket and jeans")]))
    assert "no text props" in fails(dict(good, shots=[dict(shot, accent="a red shop sign")]))
    assert "traits" in fails(dict(good, cast=[dict(lead, color="red")]))
    assert "cast used" in fails(dict(good, cast=[lead, dict(lead, id="p-ghost")]))
    assert "character ids" in fails(dict(good, shots=[dict(shot, characters=[{"id": "mira", "action": "a b c"}])]))
    assert "no ids in english" in fails(dict(good, shots=[dict(walk, poses=["p-commuter turns and walks away."])]))
    assert "no ids in english" in fails(dict(good, shots=[dict(shot, scene="Mira waits alone at a foggy bus stop after midnight.")]))
    assert "poses" in fails(dict(good, shots=[dict(walk, poses=["a b c d"] * 4)]))
    assert "ending" in fails(dict(good, shots=[dict(shot, caption=["막차는 이미", "떠났다."])]))
    assert "caption" in fails(dict(good, shots=[dict(shot, caption=['"늦었어"', "떠났습니다"])]))
    assert "camera runs" in fails(dict(good, shots=[dict(shot, id=f"s{i}") for i in range(4)]))
    assert "no text props" in fails(dict(good, shots=[dict(shot, props=["a shop sign", "bench"])]))
    assert {"seconds", "scene length", "no banned style", "accent"} <= fails(
        dict(good, shots=[dict(shot, seconds=6, scene="Anime line art.", accent="")]))
    print("selftest ok")


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if len(argv) < 2 or argv[0] not in ("check", "prompts", "render"):
        sys.exit(__doc__)
    path = Path(argv[1])
    story = json.loads(path.read_text())
    rows = check(story)
    report(rows)
    if score(rows) < 100:
        sys.exit("FAIL 항목을 고친 뒤 다시 실행하세요")
    if argv[0] == "prompts":
        cast = {c["id"]: c for c in story["cast"]}
        for c in story["cast"]:
            (path.parent / f"cast_{c['id']}.txt").write_text(sheet_prompt(c) + "\n")
        for name, s in zip(shot_names(story), story["shots"]):
            (path.parent / f"{name}.txt").write_text(prompt(s, cast) + "\n")
            for k, pose in zip(keys(name, s)[1:], s.get("poses", [])):
                (path.parent / f"{k}.txt").write_text(pose_prompt(name, pose) + "\n")
        (path.parent / "codex.sh").write_text(codex_script(story))
        print(path.parent / "codex.sh")
    elif argv[0] == "render":
        out = Path(argv[argv.index("-o") + 1]) if "-o" in argv else path.parent / "dami.mp4"
        render(story, path.parent, out)


if __name__ == "__main__":
    main(sys.argv[1:])
