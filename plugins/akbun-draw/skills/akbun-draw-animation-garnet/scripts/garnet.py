# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow", "numpy"]
# ///
"""garnet 애니메이션: 이야기 spec(JSON)을 채점하고, 배역 시트·컷·자세 프롬프트와 codex.sh·cues.txt를 쓰고,
박자에 맞춘 16:9 영상(임시 사운드 포함)과 GIF로 렌더한다.

  check <story.json>                 채점표만 출력(100점이 아니면 종료 코드 1)
  prompts <story.json>               100점이면 spec 옆에 cast_<id>.txt, NN_<id>.txt, NN_<id>_<k>.txt, codex.sh, cues.txt를 쓴다
  render <story.json> [-o out.mp4]   spec 옆 PNG들로 sound.wav, 영상, garnet.gif, sheet.jpg를 만든다
  --selftest                         자체 검사
"""
import json
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"
BANNED_STYLE = r"\b(watercolou?r|gouache|painterly|oil[- ]paint\w*|3d|photorealistic|realistic|pixel[- ]?art|chibi|anime|neon)\b"
BANNED_TEXT_PROPS = r"\b(signs?|signboards?|labels?|posters?|banners?|menus?|newspapers?|texts?|letters?|words?|numbers?|captions?)\b"
COLOR_WORDS = (r"\b(red|crimson|scarlet|blue|navy|green|olive|teal|yellow|mustard|orange|purple|plum|pink|white|black|"
               r"grey|gray|brown|beige|cream|charcoal|sand|gold|golden|silver|maroon|violet|khaki|tan)\b")
PICKED = ("gender", "age", "height", "build", "face", "skin")  # 참고 배역과 비교하는 특징
W, H, FPS, SR = 1920, 1080, 24, 48000
BLACK, FADE_IN = 8, 6  # 막의 첫 컷: 첫 8프레임 검정, 다음 6프레임 동안 검정에서 밝아짐
SHEET_BG = "#D9D4CF"
STYLE_SHEET = ("line", "shading", "figures")  # 캐릭터 시트에 넣는 그림체 규칙
FRAGMENT, WIDE = ("hand-insert", "extreme-close"), ("deep-wide", "high-down")
DONT = ("DO NOT: no painterly brush texture, no watercolor or gouache, no paper grain, no photorealism, no 3D render, "
        "no pixel art, no chibi, no characters from existing films, animations, games or brands, "
        "no checkerboard floors, no sunburst light rays, no spotlight cones, no pure-black vignette, no screaming wide-eyed faces, "
        "no written words, letters, numbers or signs anywhere, no watermark.")


def load(name):
    return {r["id"]: r for r in (json.loads(l) for l in (REF / name).read_text().splitlines() if l.strip())}


def words(s):
    return len(s.split())


def halves(x):
    """0.5 단위 값이면 정수 2배, 아니면 None."""
    return round(x * 2) if isinstance(x, (int, float)) and not isinstance(x, bool) and abs(x * 2 - round(x * 2)) < 1e-9 else None


def is_int(x, lo, hi):
    return isinstance(x, int) and not isinstance(x, bool) and lo <= x <= hi


def max_poses(beats):
    return 1 if beats <= 3 else 2


def cast_rows(c, traits, refs):
    same = [r for r, ref in refs.items() if sum(c.get(k) == ref[k] for k in PICKED) > len(PICKED) - 2]
    hair, outfit = c.get("hair", ""), c.get("outfit", "")
    return [
        ("id", bool(re.fullmatch(r"p(-[a-z]+)+", c.get("id", ""))), "배역 id는 p-영어소문자, 하이픈 가능(예: p-clerk)"),
        ("traits", all(c.get(k) in traits[k]["options"] for k in traits),
         "traits.jsonl의 gender·age·height·build·face·skin·color 값만: " + str({k: c.get(k) for k in traits})),
        ("hair", 2 <= words(hair) <= 12 and hair.isascii() and not re.search(r"\b(red|crimson|scarlet)\b", hair, re.I),
         "hair 영어 2~12단어, 붉은색 금지"),
        ("outfit", 3 <= words(outfit) <= 14 and outfit.isascii() and not re.search(COLOR_WORDS, outfit, re.I),
         "outfit 영어 3~14단어, 색 이름 금지(색은 color가 정함)"),
        ("no banned style", not re.search(BANNED_STYLE, hair + " " + outfit, re.I), "hair·outfit에 금지 화풍 낱말"),
        ("new face", not same, f"참고 배역과 gender·age·height·build·face·skin 중 2개 이상 달라야 함: {same}"),
    ]


def shot_rows(s, pal, cam, sfx_ids, cast_ids, names):
    c = cam.get(s.get("camera"))
    cs = s.get("characters", [])
    ids = [x.get("id") for x in cs]
    lo, hi = c["chars"] if c else (0, 0)
    b = s.get("beats", 0)
    poses = s.get("poses", [])
    sfx = s.get("sfx", [])
    text = " ".join([s.get("scene", ""), s.get("setting", "")] + poses + [x.get("action", "") for x in cs] + s.get("props", []))
    return [
        ("act", is_int(s.get("act"), 1, 3), "act는 1~3 정수"),
        ("palette", s.get("palette") in pal, f"palettes.jsonl id: {sorted(pal)}"),
        ("camera", c is not None, f"cameras.jsonl id: {sorted(cam)}"),
        ("character count", lo <= len(cs) <= hi, f"{len(cs)}명, 카메라 허용 {lo}~{hi}명(경계 포함)"),
        ("character ids", bool(ids) and all(i in cast_ids for i in ids) and len(set(ids)) == len(ids), f"cast의 id만, 중복 없이: {ids}"),
        ("actions", bool(cs) and all(words(x.get("action", "")) >= 3 for x in cs), "인물마다 action 3단어 이상"),
        ("scene length", 6 <= words(s.get("scene", "")) <= 40, f"scene {words(s.get('scene', ''))}단어, 6~40"),
        ("setting", 2 <= words(s.get("setting", "")) <= 16, "setting 영어 2~16단어"),
        ("props", 1 <= len(set(s.get("props", []))) == len(s.get("props", [])) <= 8, "소품 1~8개, 중복 없이"),
        ("no text props", not re.search(BANNED_TEXT_PROPS, " ".join(s.get("props", [])), re.I), "글자가 보이는 소품 금지"),
        ("beats", halves(b) is not None and 2 <= halves(b) <= 16, f"beats {b}, 1~8(경계 포함), 0.5박 단위"),
        ("poses", len(poses) <= max_poses(b if halves(b) else 0) and all(3 <= words(p) <= 40 for p in poses),
         f"poses {len(poses)}개: 3박 이하 컷은 0~1개, 그보다 긴 컷은 0~2개, 각 영어 3~40단어"),
        ("energy", is_int(s.get("energy"), 0, 3), "energy는 0~3 정수"),
        ("sfx", isinstance(sfx, list) and len(sfx) <= 2 and len(set(sfx)) == len(sfx) and all(x in sfx_ids for x in sfx),
         f"sfx는 0~2개, 중복 없이, sound.jsonl의 sfx id: {sorted(sfx_ids)}"),
        ("english", text.isascii(), "영어 칸은 ASCII만"),
        ("no ids in english", not re.search(r"(?<![\w-])(" + "|".join(map(re.escape, names)) + r")(?![\w-])", text, re.I),
         "영어 칸에 id 대신 역할(scene·action)이나 생김새(poses)"),
        ("no banned style", not re.search(BANNED_STYLE, text, re.I), "watercolor·gouache·painterly·3d·realistic·pixel art·chibi·anime·neon 금지"),
    ]


def direction_rows(story):
    """direction.jsonl의 규칙을 수치로 채점한다. 컷 값이 잘못돼도 죽지 않게 기본값으로 계산한다."""
    shots = story.get("shots", [])
    if not shots:
        return []
    why = {k: v["ko"] for k, v in load("direction.jsonl").items()}
    acts = [s.get("act") if is_int(s.get("act"), 1, 3) else 0 for s in shots]
    beats = [s.get("beats") if halves(s.get("beats", 0)) else 0 for s in shots]
    energy = [s.get("energy") if is_int(s.get("energy"), 0, 3) else -1 for s in shots]
    sfx = [s.get("sfx", []) if isinstance(s.get("sfx", []), list) else [] for s in shots]
    cams = [s.get("camera") for s in shots]
    starts = [i for i in range(len(shots)) if i == 0 or acts[i] != acts[i - 1]]
    n_acts = max(acts)
    by_act = {a: [i for i in range(len(shots)) if acts[i] == a] for a in set(acts)}
    total = sum(beats) or 1
    climax = next((i for i, e in enumerate(energy) if e == 3), None)
    avg = total / len(shots)
    win = beats[max(0, (climax or 0) - 2):(climax or 0) + 1]
    first_act = by_act.get(1, [])[:3]
    rows = [
        ("acts", acts[0] == 1 and all(b - a in (0, 1) for a, b in zip(acts, acts[1:])) and len(starts) == n_acts
         and all(len(v) >= 2 for v in by_act.values()) and (len(shots) < 6 or n_acts >= 2), why["acts"]),
        ("act-palette", all(len({shots[i].get("palette") for i in v}) <= 2 for v in by_act.values())
         and all(shots[a].get("palette") != shots[b].get("palette") for a, b in zip(starts, starts[1:])), why["act-palette"]),
        ("act-open", all(beats[i] >= 3 for i in starts) and all(energy[i] < energy[i - 1] or energy[i] == 0 for i in starts[1:]), why["act-open"]),
        ("opening", cams[0] in WIDE or (cams[0] in FRAGMENT and any(cams[i] in WIDE for i in first_act)), why["opening"]),
        ("quiet-open", energy[0] in (0, 1), why["quiet-open"]),
        ("climax", climax is not None and sum(beats[:climax]) >= 0.4 * total - 1e-9 and "hit" in sfx[climax], why["climax"]),
        ("escalate", climax is not None and sum(win) / len(win) < avg, why["escalate"]),
        ("riser-payoff", all(i + 1 < len(shots) and "hit" in sfx[i + 1] for i in range(len(shots)) if "riser" in sfx[i]), why["riser-payoff"]),
        ("hold-ending", beats[-1] >= max(beats[-4:-1] or [0]) and energy[-1] in (0, 1), why["hold-ending"]),
        ("camera-runs", not any(len(set(cams[i:i + 3])) == 1 for i in range(len(cams) - 2)), why["camera-runs"]),
        ("rhythm", not any(len(set(beats[i:i + 3])) == 1 for i in range(len(beats) - 2)), why["rhythm"]),
    ]
    return [(f"direction: {n}", ok, w) for n, ok, w in rows]


def seconds(story):
    return sum(s.get("beats", 0) for s in story.get("shots", [])) * 60 / story.get("bpm", 120)


def check(story):
    pal, cam, traits, refs, snd = (load(n) for n in ("palettes.jsonl", "cameras.jsonl", "traits.jsonl", "characters.jsonl", "sound.jsonl"))
    sfx_ids = {k for k, v in snd.items() if v["kind"] == "sfx"}
    shots, cast = story.get("shots", []), story.get("cast", [])
    ids = [s.get("id", "") for s in shots]
    cast_ids = [c.get("id") for c in cast]
    used = {x.get("id") for s in shots for x in s.get("characters", [])}
    length, bpm = story.get("length", 0), story.get("bpm")
    length = length if isinstance(length, (int, float)) and not isinstance(length, bool) else -1
    ok_bpm = is_int(bpm, 90, 140)
    total = seconds(story) if ok_bpm and all(isinstance(s.get("beats"), (int, float)) for s in shots) else -99
    rows = [
        ("length", 6 <= length <= 40, f"length {story.get('length')}초, 6~40 숫자"),
        ("bpm", ok_bpm, f"bpm {bpm}, 90~140 정수"),
        ("total", abs(total - length) <= 0.5 + 1e-6, f"박 수 합 × 60 ÷ bpm = {total:.2f}초, length와 0.5초 이내(경계 포함)"),
        ("shot count", 4 <= len(shots) <= 20, f"{len(shots)}컷, 4~20"),
        ("shot ids", all(re.fullmatch(r"[a-z0-9-]+", i) for i in ids) and len(set(ids)) == len(ids), f"영어 소문자·숫자·하이픈, 중복 없이: {ids}"),
        ("cast count", 1 <= len(cast) <= 3 and len(set(cast_ids)) == len(cast_ids), f"배역 {len(cast)}명, 1~3명, id 중복 없이"),
        ("cast used", set(cast_ids) == used, f"배역은 모두 한 컷 이상 나오고 컷 인물은 모두 배역: {sorted(set(cast_ids) ^ used)}"),
    ] + direction_rows(story)
    pairs = [(a, b) for i, a in enumerate(cast) for b in cast[i + 1:] if a.get("height") == b.get("height") and a.get("build") == b.get("build")]
    rows.append(("cast silhouettes", not pairs, f"배역끼리 height·build 중 하나 이상 달라야 함: {[(a.get('id'), b.get('id')) for a, b in pairs]}"))
    for c in cast:
        rows += [(f"{c.get('id')}: {n}", ok, why) for n, ok, why in cast_rows(c, traits, refs)]
    names = [i for i in cast_ids if i] + list(refs)
    for s in shots:
        rows += [(f"{s.get('id')}: {n}", ok, why) for n, ok, why in shot_rows(s, pal, cam, sfx_ids, cast_ids, names)]
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
        style["medium"]["prompt"].replace("landscape 16:9", "portrait 2:3"),
        f"CHARACTER SHEET: one full-body front view of {describe(c)}. Standing in a neutral pose, whole body visible from head to "
        f"shoes, centered on a plain flat light grey background ({SHEET_BG}) under even neutral light. No other people, no props, no scenery.",
        f"STYLE: {rules}",
        DONT,
    ])


def shot_names(story):
    return [f"{i:02d}_{s['id']}" for i, s in enumerate(story["shots"], 1)]


def prompt(s, cast):
    style, pal, cam = (load(n) for n in ("style.jsonl", "palettes.jsonl", "cameras.jsonl"))
    p, c = pal[s["palette"]], cam[s["camera"]]
    near = {"silhouette-frame": ", standing right in front of the camera as a near-black silhouette",
            "hand-insert": ", seen only as hands and sleeves"}.get(s["camera"], "")
    who = " ".join(f"{i}. {describe(cast[x['id']])}{near if i == 1 else ''}, {x['action']}."
                   for i, x in enumerate(s["characters"], 1))
    rules = " ".join(style[k]["prompt"].format(light=p["light"]) for k in style if k != "medium")
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
        DONT,
    ])


def pose_prompt(name, pose):
    return (f"Edit the first attached image ({name}.png). Keep everything identical: drawing style, line weight, colors, lighting, "
            "camera framing, background, props and every character's face, body and clothes (the other attached images are "
            f"their character sheets). Change only the pose to this: {pose} Landscape 16:9, no written words.")


def keys(name, s):
    """컷의 열쇠 그림 파일 이름 목록: 첫 장 + 자세마다 한 장."""
    return [name] + [f"{name}_{k}" for k in range(2, len(s.get("poses", [])) + 2)]


def codex_script(story):
    """3단계(배역 시트 → 컷 첫 장 → 자세)를 단계마다 동시에 돌리는 codex.sh. 이미 있는 PNG는 건너뛴다.
    파일 이름은 채점을 통과한 id(영어 소문자·숫자·하이픈)로만 만든다."""
    def line(stem, task, attach, aspect="landscape 16:9"):
        files = "".join(f" -i {a}.png" for a in attach)  # -i는 값을 여러 개 받으므로 프롬프트 뒤에 둔다
        return (f'[ -s {stem}.png ] || codex exec --skip-git-repo-check -s workspace-write "Read {stem}.txt. Use your built-in '
                f'image generation tool{" " + task if task else ""} with that file\'s full text as the prompt, {aspect}. Save the result as '
                f'{stem}.png here. Reply with the path only."{files} < /dev/null > {stem}.log 2>&1 &')
    sheets = [f"cast_{c['id']}" for c in story["cast"]]
    stage1 = [line(n, "", [], "portrait 2:3") for n in sheets]
    stage2, stage3, every = [], [], list(sheets)
    for name, s in zip(shot_names(story), story["shots"]):
        refs = [f"cast_{x['id']}" for x in s["characters"]]
        stage2.append(line(name, "", refs))
        stage3 += [line(k, "to edit the attached images", [name] + refs) for k in keys(name, s)[1:]]
        every += keys(name, s)
    out = ["#!/bin/bash", "# garnet.py prompts가 만든 파일. 출력 폴더에서 bash codex.sh로 돌린다. 잘못 나온 그림은 PNG를 지우고 다시 돌린다.",
           'cd "$(dirname "$0")"']
    for title, stage in (("배역 시트", stage1), ("컷 첫 장", stage2), ("자세", stage3)):
        if stage:
            out += [f"echo '{title} {len(stage)}장'", *stage, "wait"]
    out += [f"for f in {' '.join(every)}; do [ -s $f.png ] || {{ echo \"없음: $f.png ($f.log 확인)\"; exit 1; }}; done",
            "echo '모든 그림 완료'"]
    return "\n".join(out) + "\n"


def timeline(story):
    """컷마다 (시작 프레임, 프레임 수, 막의 첫 컷인지). 누적 박 수에서 프레임을 계산해 컷 경계가 박자에서 밀리지 않는다."""
    spb = 60 / story["bpm"]
    out, cum = [], 0.0
    for i, s in enumerate(story["shots"]):
        a, cum = half_up(cum * spb * FPS), cum + s["beats"]
        out.append((a, half_up(cum * spb * FPS) - a, i == 0 or s["act"] != story["shots"][i - 1]["act"]))
    return out


def half_up(x):
    """프레임 반올림: 0.5는 올린다(파이썬 round의 짝수 반올림을 쓰지 않음)."""
    return int(x + 0.5 + 1e-9)


def tc(frame):
    return f"{frame // FPS // 60:02d}:{frame // FPS % 60:02d}:{frame % FPS:02d}"


def cue_sheet(story):
    """편집기에서 진짜 음악·효과음으로 바꿀 때 쓰는 큐 시트(시작 타임코드 mm:ss:ff, 24fps)."""
    snd = load("sound.jsonl")
    lines = [f"# {story.get('title', '')}  bpm {story['bpm']}  24fps  {seconds(story):.2f}s", "# 시작      막 컷              박   energy  sfx"]
    for (a, n, first), name, s in zip(timeline(story), shot_names(story), story["shots"]):
        mark = " (검정에서 밝아짐)" if first else ""
        lines.append(f"{tc(a)}  {s['act']}  {name:16} {s['beats']:<4} {s['energy']}       {', '.join(s['sfx']) or '-'}{mark}")
    lines += ["", "# energy·sfx 뜻"] + [f"# {k}: {v['ko']}" for k, v in snd.items()]
    return "\n".join(lines) + "\n"


def synth(story):
    """임시 사운드(모노 float 배열, SR Hz). 팔레트 화음 지속음 + energy 단계별 박자 + sfx. 진짜 음악으로 바꿀 때까지 연출 타이밍을 듣는 용도."""
    import numpy as np
    pal = load("palettes.jsonl")
    spb = 60 / story["bpm"]
    tl = timeline(story)
    total = (tl[-1][0] + tl[-1][1]) / FPS
    out = np.zeros(int(round(total * SR)) + 1)
    rng = np.random.default_rng(7)

    def add(t0, sig):
        i = int(round(t0 * SR))
        if i < 0:
            sig, i = sig[-i:], 0
        j = min(len(out), i + len(sig))
        if j > i:
            out[i:j] += sig[:j - i]

    def env(n, decay):
        return np.exp(-np.arange(n) / (decay * SR))

    def tone(f0, f1, dur, amp, decay):
        n = int(dur * SR)
        f = np.geomspace(f0, f1, n)
        return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, decay)

    def noise(dur, amp, decay, high=False):
        n = int(dur * SR)
        x = rng.standard_normal(n + 1)
        return amp * (np.diff(x) if high else x[:n]) * env(n, decay)

    for (a, n, first), s in zip(tl, story["shots"]):
        t0, t1 = (a + (BLACK if first else 0)) / FPS, (a + n) / FPS
        if t1 <= t0:
            continue
        p, e = pal[s["palette"]], s["energy"]
        m = int((t1 - t0) * SR)
        t = np.arange(m) / SR
        fade = np.minimum(1, np.minimum(t, t[::-1]) / 0.02)  # 컷 경계 딸깍 소리 방지
        drone = sum(np.sin(2 * np.pi * p["root_hz"] * 2 ** (k / 12) * t) for k in p["chord"]) / len(p["chord"])
        add(t0, (0.06 + 0.01 * e) * drone * (0.85 + 0.15 * np.sin(2 * np.pi * 0.5 * t)) * fade)
        beat0 = int(np.ceil(t0 / spb - 1e-9))
        for k in range(beat0, int(np.floor((t1 - 1e-9) / spb)) + 1):
            bt = k * spb
            if e >= 1:
                add(bt, tone(p["root_hz"] * 4, p["root_hz"] * 4, 0.15, 0.05, 0.05))
            if e >= 2:
                add(bt, tone(110, 45, 0.3, 0.5, 0.08))
                add(bt + spb / 2, noise(0.05, 0.06, 0.01, high=True))
            if e >= 3:
                if k % 2:
                    add(bt, noise(0.18, 0.25, 0.05) + tone(180, 160, 0.18, 0.2, 0.05))
                add(bt, sum(tone(p["root_hz"] * 2 * h, p["root_hz"] * 2 * h, 0.4, 0.15 / h, 0.15) for h in (1, 2, 3)))
            if "heartbeat" in s["sfx"]:
                add(bt, tone(70, 50, 0.15, 0.6, 0.05))
                add(bt + 0.14, tone(65, 45, 0.15, 0.45, 0.05))
        if "hit" in s["sfx"]:
            add(t0, noise(0.3, 0.5, 0.06))
            add(t0, tone(60, 28, 0.8, 0.8, 0.25))
        if "riser" in s["sfx"]:
            r = tone(p["root_hz"] * 4, p["root_hz"] * 16, t1 - t0, 0.12, 1e9) + noise(t1 - t0, 0.08, 1e9)
            add(t0, r * np.linspace(0, 1, len(r)) ** 2)
        if "sting" in s["sfx"]:
            add(t0, sum(tone(p["root_hz"] * 8 * 2 ** (k / 12), p["root_hz"] * 8 * 2 ** (k / 12), 0.9, 0.08, 0.35) for k in (0, 1, 6)))
    for a, n, first in tl:  # 막의 첫 컷 검정 동안은 무음
        if first:
            out[int(a / FPS * SR):int((a + BLACK) / FPS * SR)] = 0
    for (a, n, first), s in zip(tl, story["shots"]):  # whoosh는 컷 직전에 들리므로 무음 처리 뒤에 더한다
        if "whoosh" in s["sfx"]:
            w = noise(0.35, 0.3, 10)
            add((a + (BLACK if first else 0)) / FPS - 0.35, w * np.sin(np.linspace(0, np.pi, len(w))) ** 2)
    tail = int(0.5 * SR)
    out[-tail:] *= np.linspace(1, 0, tail)
    return np.tanh(out * 1.2) * 0.9


def write_wav(path, x):
    import numpy as np
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.repeat(pcm, 2).tobytes())


def schedule(n, count):
    """n프레임에 열쇠 그림 count장을 같은 간격으로 놓는다(셀 애니메이션처럼 섞지 않고 바로 바꾼다).
    프레임마다 그림 번호와, 시트에 넣을 그림마다 가운데 프레임 집합을 돌려준다."""
    seg = n / count
    return [min(int(f / seg), count - 1) for f in range(n)], {int(seg * i + seg / 2) for i in range(count)}


def frames(story, root):
    """(프레임, 시트에 넣을지) 생성기. 컷 사이는 하드컷, 막의 첫 컷은 검정에서 밝아진다. 컷 안에서는 밀어 들어가며 열쇠 그림을 바꾼다."""
    from PIL import Image, ImageOps
    cam = load("cameras.jsonl")
    black = Image.new("RGB", (W, H), "#000000")
    for (a, n, first), name, s in zip(timeline(story), shot_names(story), story["shots"]):
        imgs = [ImageOps.fit(Image.open(root / f"{k}.png").convert("RGB"), (W, H), Image.LANCZOS) for k in keys(name, s)]
        dark = BLACK if first else 0
        for _ in range(dark):
            yield black, False
        v = n - dark
        plan, mids = schedule(v, len(imgs))
        drift = cam[s["camera"]]["drift"]
        for f, i in enumerate(plan):
            z = 1 + drift * f / max(v - 1, 1)
            mx, my = round(W * (1 - 1 / z) / 2), round(H * (1 - 1 / z) / 2)
            img = imgs[i].crop((mx, my, W - mx, H - my)).resize((W, H), Image.LANCZOS) if mx else imgs[i]
            if first and f < FADE_IN:
                img = Image.blend(black, img, (f + 1) / (FADE_IN + 1))
            yield img, f in mids


def render(story, root, out):
    from PIL import Image
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg가 없습니다. 설치한 뒤 다시 실행하세요(macOS: brew install ffmpeg).")
    missing = [f"{k}.png" for name, s in zip(shot_names(story), story["shots"]) for k in keys(name, s) if not (root / f"{k}.png").is_file()]
    if missing:
        sys.exit(f"그림이 없습니다: {', '.join(missing)} (codex.sh를 다시 돌리세요)")
    out.parent.mkdir(parents=True, exist_ok=True)
    wav = out.with_name("sound.wav")
    write_wav(wav, synth(story))
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                            "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)],
                           stdin=subprocess.PIPE)
    thumbs, written = [], 0
    for frame, mid in frames(story, root):
        enc.stdin.write(frame.tobytes())
        written += 1
        if mid:
            thumbs.append(frame.resize((384, 216)))
    enc.stdin.close()
    if enc.wait():
        sys.exit("ffmpeg 인코딩 실패")
    gif = out.with_name("garnet.gif")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out), "-vf",
                    "fps=12,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse", str(gif)], check=True)
    cols = min(len(thumbs), 6)
    sheet = Image.new("RGB", (384 * cols, 216 * -(-len(thumbs) // cols)), "#000000")
    for i, m in enumerate(thumbs):
        sheet.paste(m, (384 * (i % cols), 216 * (i // cols)))
    sheet.save(out.with_name("sheet.jpg"), quality=88)
    tl = timeline(story)
    want = tl[-1][0] + tl[-1][1]
    print(f"{out} H.264+AAC {W}x{H} {FPS}fps {written}프레임 ({written / FPS:.2f}s), {wav}, {gif}, {out.with_name('sheet.jpg')}")
    if written != want:
        sys.exit(f"프레임 수 불일치: 쓴 {written} != 박 수 합 기준 {want}")


def report(rows):
    for name, ok, why in rows:
        if not ok:
            print(f"FAIL  {name:28} {why}")
    print(f"score {score(rows)} ({sum(ok for _, ok, _ in rows)}/{len(rows)})")


def selftest():
    lead = {"id": "p-courier", "gender": "woman", "age": "twenties", "height": "short", "build": "stocky", "face": "square",
            "skin": "olive", "hair": "a tight high ponytail", "outfit": "a puffy vest over a hoodie and cargo shorts", "color": "teal"}
    base = {"palette": "teal-dusk", "scene": "A courier hurries down an empty alley toward the last lit doorway.",
            "setting": "a narrow alley at night", "characters": [{"id": "p-courier", "action": "runs carrying a parcel"}],
            "props": ["cardboard parcel", "lit doorway"], "sfx": [], "poses": []}
    shots = [dict(base, id="hand", act=1, camera="hand-insert", beats=3, energy=0),
             dict(base, id="alley", act=1, camera="deep-wide", beats=4, energy=1, poses=["The short woman in the teal vest skids to a stop."]),
             dict(base, id="face", act=1, camera="extreme-close", beats=2, energy=2, sfx=["riser"]),
             dict(base, id="door", act=1, camera="tilted-mid", beats=1.5, energy=3, sfx=["hit"]),
             dict(base, id="inside", act=2, palette="sage-morning", camera="low-hero", beats=3.5, energy=1, sfx=["whoosh"]),
             dict(base, id="rest", act=2, palette="sage-morning", camera="high-down", beats=4, energy=0)]
    good = {"length": 9, "bpm": 120, "cast": [lead], "shots": shots}

    def fails(story):
        return {n.split(": ")[-1] for n, ok, _ in check(story) if not ok}

    def swap(i, **kw):
        return dict(good, shots=[dict(s, **kw) if k == i else s for k, s in enumerate(shots)])
    assert score(check(good)) == 100, [r for r in check(good) if not r[1]]
    cast = {lead["id"]: lead}
    p = prompt(shots[1], cast)
    assert "single warm lamp against cool dusk" in p and "{" not in p and "teal #2F6A66" in p and "landscape 16:9" in p
    assert "a twenty-something woman, short with a stocky build" in p and "#1E0A0C" in p
    assert "hands and sleeves" in prompt(shots[0], cast) and "near-black silhouette" not in p
    sp = sheet_prompt(lead)
    assert SHEET_BG in sp and "portrait 2:3" in sp and "COLOR PALETTE" not in sp and "light cones" not in sp.split("DO NOT")[0]
    assert keys("02_alley", shots[1]) == ["02_alley", "02_alley_2"]
    # 박자 → 프레임: 120bpm 한 박 = 12프레임, 경계는 누적 박 수로
    tl = timeline(good)
    assert [x[0] for x in tl] == [0, 36, 84, 108, 126, 168] and tl[-1][1] == 48 and [x[2] for x in tl] == [1, 0, 0, 0, 1, 0]
    assert [x[0] for x in timeline(dict(good, bpm=128))][1] == 34 and half_up(112.5) == 113
    plan, mids = schedule(48, 3)
    assert [plan.index(i) for i in range(3)] == [0, 16, 32] and mids == {8, 24, 40}
    cs = cue_sheet(good)
    assert "00:05:06  2  05_inside" in cs and "(검정에서 밝아짐)" in cs and "whoosh" in cs
    snd = synth(good)
    assert abs(len(snd) - 216 / FPS * SR) <= 1 and abs(snd).max() <= 0.9 and abs(snd[: int(BLACK / FPS * SR)]).max() == 0
    assert abs(snd[-10:]).max() < 0.01
    assert abs(snd[int(132 / FPS * SR):int(134 / FPS * SR)]).max() > 0.05  # inside 컷의 whoosh가 검정 끝에서 들림
    sh = codex_script(good)
    assert sh.index("cast_p-courier.txt") < sh.index("01_hand.txt") < sh.index("02_alley_2.txt")
    assert "-i 02_alley.png -i cast_p-courier.png" in sh and sh.count("wait") == 3 and "portrait 2:3. Save the result as cast_p-courier.png" in sh
    # 실패해야 하는 것: 배역
    assert "new face" in fails(dict(good, cast=[dict(lead, gender="woman", age="middle-aged", height="tall", build="slim", face="angular", skin="tan")]))
    assert "outfit" in fails(dict(good, cast=[dict(lead, outfit="a long navy coat and boots")]))
    assert "hair" in fails(dict(good, cast=[dict(lead, hair="bright red curls")]))
    assert "no banned style" in fails(dict(good, cast=[dict(lead, outfit="an anime jacket and jeans")]))
    assert "traits" in fails(dict(good, cast=[dict(lead, color="red")]))
    assert "cast used" in fails(dict(good, cast=[lead, dict(lead, id="p-ghost")]))
    assert "cast silhouettes" in fails(dict(good, cast=[lead, dict(lead, id="p-twin", gender="man", age="elderly", face="long", skin="brown")]))
    assert "length" in fails(dict(good, length="9"))
    assert "act-open" in fails(swap(0, beats=2) | {"shots": [dict(shots[0], beats=2), dict(shots[1], beats=5)] + shots[2:]})
    # 컷
    assert "character ids" in fails(swap(1, characters=[{"id": "juno", "action": "a b c"}]))
    assert "no ids in english" in fails(swap(1, poses=["p-courier turns and walks away."]))
    assert "poses" in fails(swap(2, poses=["a b c", "d e f"]))
    assert "beats" in fails(swap(1, beats=4.25)) and "beats" in fails(swap(1, beats=9))
    assert "sfx" in fails(swap(1, sfx=["boom"])) and "energy" in fails(swap(1, energy=4))
    assert "no text props" in fails(swap(1, props=["a shop sign", "bench"]))
    assert {"scene length", "no banned style"} <= fails(swap(1, scene="Painterly gouache alley."))
    assert "total" in fails(dict(good, length=12)) and "bpm" in fails(dict(good, bpm=160))
    # 연출
    assert "opening" in fails(swap(0, camera="tilted-mid")) and "opening" in fails(swap(1, camera="low-hero"))
    assert "opening" not in fails(swap(0, camera="high-down") | {"shots": [dict(shots[0], camera="high-down"), dict(shots[1], camera="low-hero")] + shots[2:]})
    assert "checkerboard" in p and "pure black" in p and "light beams" not in sheet_prompt(lead)
    assert "quiet-open" in fails(swap(0, energy=2))
    assert "climax" in fails(swap(3, sfx=[])) and "climax" in fails(swap(3, energy=2))
    assert "climax" in fails(dict(good, shots=[shots[0], dict(shots[1], energy=3, sfx=["hit"])] + shots[2:]))
    assert "escalate" in fails(swap(3, beats=6))
    assert "riser-payoff" in fails(swap(4, sfx=["riser"]))
    assert "hold-ending" in fails(swap(5, beats=3)) and "hold-ending" in fails(swap(5, energy=2))
    assert "act-open" in fails(swap(4, energy=3)) and "act-open" in fails(swap(4, beats=2.5))
    assert "act-palette" in fails(swap(4, palette="teal-dusk", act=2) | {"shots": [dict(s, palette="teal-dusk") for s in shots]})
    assert "acts" in fails(swap(5, act=3)) and "acts" in fails(dict(good, shots=[dict(s, act=1, palette="teal-dusk") for s in shots]))
    assert "camera-runs" in fails(swap(2, camera="deep-wide") | {"shots": [shots[0], shots[1], dict(shots[2], camera="deep-wide"), dict(shots[3], camera="deep-wide")] + shots[4:]})
    assert "rhythm" in fails(swap(2, beats=4) | {"shots": [shots[0], shots[1], dict(shots[2], beats=4), dict(shots[3], beats=4)] + shots[4:]})
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
        (path.parent / "cues.txt").write_text(cue_sheet(story))
        print(path.parent / "codex.sh", path.parent / "cues.txt")
    elif argv[0] == "render":
        out = Path(argv[argv.index("-o") + 1]) if "-o" in argv else path.parent / "garnet.mp4"
        render(story, path.parent, out)


if __name__ == "__main__":
    main(sys.argv[1:])
