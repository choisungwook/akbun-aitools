# /// script
# requires-python = ">=3.12"
# dependencies = ["python-pptx"]
# ///
"""summary spec(storyboard.json)에 더한 detail 키를 검사하고 컷 하나당 한 장인 detail.pptx를 만든다.

  check <spec>   summary 검사(akbun-youtube-storyboard-dami) 뒤 detail 키 검사. 실패 이유를 모아 출력하고 종료 코드 1
  build <spec>   검사 후 spec 옆 detail.pptx (sketches/cut_NN.png가 있으면 넣는다)
  --selftest     summary 예시 spec에 detail 키를 채워 build하고, 망가뜨린 spec이 기대대로 실패하는지 확인
"""
import contextlib
import copy
import io
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
SUMMARY = Path(__file__).resolve().parents[2] / "akbun-youtube-storyboard-dami"
SUMMARY_SCRIPT = SUMMARY / "scripts" / "dami_storyboard.py"

# 검사 상수. references/detail.md의 표와 같은 값으로 유지한다.
MAX_BEATS = 6
EPS = 0.01  # 비트 경계·끝 시각 비교 허용 오차(초)
PROMPT_WORDS = (8, 90)  # ai_prompt 낱말 수, 경계 포함
BEAT_TIME = re.compile(r"^(\d+(?:\.\d+)?)\s*[–-]\s*(\d+(?:\.\d+)?)초$")
HANGUL = re.compile(r"[ᄀ-ᇿ㄰-㆏가-힣]")
BANNED = re.compile(r"\b(fonts?|typefaces?)\b", re.I)
NEED_RECORD = ("화면 녹화", "사진·자료")
NEED_PROMPT = ("모션그래픽", "촬영")
NO_TEXT = "No words, letters or numbers anywhere on screen; labels are added in editing. No human face anywhere."

FONT = "Pretendard"  # SIL OFL 1.1. summary pptx와 같은 글꼴
INK, MUTED, ACCENT, HEAD, ROW, WHITE = "1F2A44", "6B7280", "1BA39C", "1F2A44", "F3F4F6", "FFFFFF"
VOICE = {"adr": "후시녹음", "live": "현장음", "none": "말 없음"}


def fmt(t):
    s = int(t + 0.5)
    return f"{s // 60:02d}:{s % 60:02d}"


def full_prompt(spec, cut):
    """AI 영상 생성에 그대로 넣는 문장. 모션그래픽이면 motion_style을 앞에, 금지 문장과 길이를 뒤에 붙인다."""
    head = spec.get("motion_style", "").rstrip(". ") + ". " if cut["source"] == "모션그래픽" else ""
    return f"{head}{cut['ai_prompt'].rstrip('. ')}. {NO_TEXT} {cut['dur']:g} seconds."


def load(name):
    """summary 라이브러리(shots·moves jsonl)를 id로 읽는다. 장 머리말에 한국어 이름을 쓰려고 쓴다."""
    lines = (SUMMARY / "references" / name).read_text(encoding="utf-8").splitlines()
    return {r["id"]: r for r in (json.loads(ln) for ln in lines if ln.strip())}


def check_detail(spec):
    """detail 키만 본다. 형식이 틀린 값은 summary 검사가 보고하므로 여기서는 건너뛰고 traceback을 내지 않는다."""
    fails = []
    cuts = spec.get("cuts") if isinstance(spec, dict) else None
    if not isinstance(cuts, list):
        return ["[cuts] cuts 배열이 없어 detail 키를 검사하지 못함"]
    cuts = [c for c in cuts if isinstance(c, dict)]
    if any(c.get("source") == "모션그래픽" for c in cuts):
        ms = spec.get("motion_style")
        if not isinstance(ms, str) or not ms.strip() or HANGUL.search(ms):
            fails.append("[motion_style] 모션그래픽 컷이 있으면 영어 문자열 motion_style이 필요")
    prod = spec.get("production", [])
    if not (isinstance(prod, list) and all(isinstance(x, str) and x.strip() for x in prod)):
        fails.append("[production] 비어 있지 않은 문자열 배열이어야 함")
    for i, c in enumerate(spec["cuts"], 1):
        if not isinstance(c, dict):
            continue
        dur = c.get("dur")
        beats = c.get("beats")
        if not (isinstance(beats, list) and 1 <= len(beats) <= MAX_BEATS):
            fails.append(f"[beats] 컷 {i}: 1~{MAX_BEATS}개 배열이 필요")
            continue
        prev = 0.0
        for j, b in enumerate(beats, 1):
            if not (isinstance(b, list) and len(b) == 3 and all(isinstance(x, str) for x in b)):
                fails.append(f"[beats] 컷 {i} 비트 {j}: [시간, 화면, 자막·소리] 문자열 3개")
                break
            m = BEAT_TIME.match(b[0].strip())
            if not m:
                fails.append(f"[beats] 컷 {i} 비트 {j}: 시간은 '0–2초' 형식 ({b[0]!r})")
                break
            a, z = float(m[1]), float(m[2])
            if abs(a - prev) > EPS or z <= a:
                fails.append(f"[beats] 컷 {i} 비트 {j}: {prev:g}초에서 이어져야 하고 끝이 시작보다 커야 함 ({b[0]})")
                break
            if not b[1].strip():
                fails.append(f"[beats] 컷 {i} 비트 {j}: 화면 칸이 비어 있음")
            prev = z
        else:
            if isinstance(dur, (int, float)) and not isinstance(dur, bool) and abs(prev - dur) > EPS:
                fails.append(f"[beats] 컷 {i}: 마지막 비트 끝 {prev:g}초 ≠ dur {dur}초")
        src = c.get("source")
        if src in NEED_RECORD and not (isinstance(c.get("record"), str) and c["record"].strip()):
            fails.append(f"[record] 컷 {i}: {src} 컷은 녹화 방법(record)이 필요")
        p = c.get("ai_prompt")
        if src in NEED_PROMPT and not (isinstance(p, str) and p.strip()):
            fails.append(f"[ai_prompt] 컷 {i}: {src} 컷은 ai_prompt가 필요")
        elif p is not None:
            if not isinstance(p, str) or HANGUL.search(p) or BANNED.search(p) or not PROMPT_WORDS[0] <= len(p.split()) <= PROMPT_WORDS[1]:
                fails.append(f"[ai_prompt] 컷 {i}: 영어 {PROMPT_WORDS[0]}~{PROMPT_WORDS[1]}낱말, 한글·font·typeface 없음")
    return fails


def summary_check(path):
    r = subprocess.run([sys.executable, str(SUMMARY_SCRIPT), "check", str(path)], capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


# ---- pptx ----

def build_pptx(spec, base):
    from PIL import Image
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.oxml.ns import qn
    from pptx.util import Inches, Pt

    def style(run, size, bold=False, color=INK):
        run.font.size, run.font.bold, run.font.name = Pt(size), bold, FONT
        run.font.color.rgb = RGBColor.from_string(color)
        rpr = run._r.get_or_add_rPr()
        ea = rpr.find(qn("a:ea"))
        if ea is None:
            ea = rpr.makeelement(qn("a:ea"), {})
            rpr.append(ea)
        ea.set("typeface", FONT)

    def text(sl, x, y, w, h, paras, size):
        tf = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)).text_frame
        tf.word_wrap = True
        for k, runs in enumerate(paras):
            p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            p.space_after = Pt(4)
            for t, bold, color in runs:
                r = p.add_run()
                r.text = t
                style(r, size, bold, color or INK)

    def cell(c, t, size, bold=False, color=INK, fill=None):
        c.text_frame.word_wrap = True
        c.text = ""
        r = c.text_frame.paragraphs[0].add_run()
        r.text = t
        style(r, size, bold, color)
        if fill:
            c.fill.solid()
            c.fill.fore_color.rgb = RGBColor.from_string(fill)
        for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
            setattr(c, side, Inches(0.05))

    plain = lambda s: s.replace("`", "").replace("**", "")
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]
    parts = {p["id"]: p["title"] for p in spec["parts"]}
    shots, moves = load("shots.jsonl"), load("moves.jsonl")
    cuts = spec["cuts"]

    sl = prs.slides.add_slide(blank)
    text(sl, 0.6, 0.5, 12, 0.8, [[(f"{spec['title']} · 세부 스토리보드", True, None)]], 26)
    text(sl, 0.6, 1.3, 12, 0.5, [[(f"컷 {len(cuts)}개 · 총 {fmt(sum(c['dur'] for c in cuts))} · 컷 하나당 한 장", False, MUTED)]], 14)
    text(sl, 0.6, 2.0, 12, 0.5, [[("핵심 메시지  ", True, ACCENT), (spec["message"], False, None)]], 14)
    rules = list(spec.get("production", []))
    if spec.get("motion_style"):
        rules.append(f"모션그래픽 공통 스타일(AI 영상 프롬프트 앞에 붙음): {spec['motion_style']}")
    text(sl, 0.6, 2.9, 12, 0.4, [[("제작 공통 규칙", True, None)]], 16)
    text(sl, 0.6, 3.4, 12, 3.8, [[("- " + r, False, None)] for r in rules], 13)

    t = 0.0
    for i, c in enumerate(cuts, 1):
        t0, t = t, t + c["dur"]
        sl = prs.slides.add_slide(blank)
        text(sl, 0.4, 0.25, 7.5, 0.6, [[(f"컷 {i:02d}  ", True, ACCENT), (f"{fmt(t0)}–{fmt(t)} · {c['dur']:g}초", True, None)]], 22)
        text(sl, 7.9, 0.33, 5.0, 0.5, [[(f"{parts[c['part']]} · {c['source']} · {shots[c['shot']]['ko']} · {moves[c['move']]['ko']}", False, MUTED)]], 12)
        img = base / "sketches" / f"cut_{i:02d}.png"
        if img.exists():
            buf = io.BytesIO()
            Image.open(img).convert("RGB").resize((1280, 720)).save(buf, "JPEG", quality=85)
            sl.shapes.add_picture(buf, Inches(0.4), Inches(0.95), Inches(6.0), Inches(3.375))
        narr = c["narration"] or "(말 없음)"
        left = [[("대본 ", True, ACCENT), (f"[{VOICE[c['voice']]}] ", False, MUTED), (narr, False, None)]]
        for key, label in (("overlay", "자막·라벨 "), ("move_note", "움직임 ")):
            if c.get(key):
                left.append([(label, True, ACCENT), (c[key], False, None)])
        if c.get("sfx"):
            left.append([("효과음 ", True, ACCENT), ("; ".join(c["sfx"]), False, None)])
        left.append([("의도 ", True, ACCENT), (c["intent"], False, None)])
        text(sl, 0.4, 4.45, 6.0, 2.9, left, 12)

        beats = c["beats"]
        tbl = sl.shapes.add_table(len(beats) + 1, 3, Inches(6.7), Inches(0.95), Inches(6.25), Inches(0.3 * (len(beats) + 1))).table
        for j, (w, h) in enumerate(((1.0, "시간"), (3.35, "화면에서 일어나는 일"), (1.9, "자막·소리"))):
            tbl.columns[j].width = Inches(w)
            cell(tbl.cell(0, j), h, 10, True, WHITE, HEAD)
        for r, row in enumerate(beats, 1):
            for j, v in enumerate(row):
                cell(tbl.cell(r, j), plain(v), 10.5, j == 0, INK, ROW if r % 2 else None)
        how = [("녹화 방법 ", plain(c["record"]))] if c.get("record") else []
        how += [("AI 영상 프롬프트 ", full_prompt(spec, c))] if c.get("ai_prompt") else []
        text(sl, 6.7, 4.75, 6.25, 2.6, [[(k, True, ACCENT), (v, False, None)] for k, v in how], 11)
        sl.notes_slide.notes_text_frame.text = f"컷 {i}: {narr}"
    prs.save(base / "detail.pptx")
    return len(prs.slides)


# ---- 실행 ----

def run(cmd, spec_path):
    path = Path(spec_path)
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL\n- [json] {path}: {e}")
        return 1
    ok, out = summary_check(path)
    fails = check_detail(spec)
    if not ok or fails:
        print("FAIL")
        if not ok:
            print(f"- [summary] {out}")
        print("\n".join(f"- {f}" for f in fails))
        return 1
    if cmd == "build":
        print(f"detail build ok -> {path.parent / 'detail.pptx'} ({build_pptx(spec, path.parent)}장)")
    else:
        print(f"detail check ok (컷 {len(spec['cuts'])}개)")
    return 0


def filled(spec):
    """summary 예시 spec에 최소 detail 키를 채운다."""
    s = copy.deepcopy(spec)
    s["motion_style"] = "Flat 2D motion graphic on a plain white background with thin navy line icons"
    s["production"] = ["화면 녹화 1920x1080"]
    for c in s["cuts"]:
        half = c["dur"] / 2
        c["beats"] = [[f"0–{half:g}초", "첫 동작", ""], [f"{half:g}–{c['dur']:g}초", "둘째 동작", "자막"]]
        if c["source"] in NEED_RECORD:
            c["record"] = "창 1920x1080으로 녹화한다."
        if c["source"] in NEED_PROMPT:
            c["ai_prompt"] = "A small navy box slides from left to right and stops in the center"
    return s


def selftest():
    from pptx import Presentation

    spec = filled(json.loads((SUMMARY / "references" / "example" / "storyboard.json").read_text(encoding="utf-8")))
    assert check_detail(spec) == [], check_detail(spec)
    src = {c["source"] for c in spec["cuts"]}
    rec = next(i for i, c in enumerate(spec["cuts"]) if c["source"] in NEED_RECORD)
    mg = next(i for i, c in enumerate(spec["cuts"]) if c["source"] == "모션그래픽")
    assert src & set(NEED_RECORD) and "모션그래픽" in src, src

    def expect(tag, mut):
        s = copy.deepcopy(spec)
        mut(s)
        got = check_detail(s)
        assert any(f"[{tag}]" in g for g in got), (tag, got)

    def expect_ok(mut):
        s = copy.deepcopy(spec)
        mut(s)
        assert check_detail(s) == [], check_detail(s)

    c0 = lambda s: s["cuts"][0]
    d0 = spec["cuts"][0]["dur"]
    expect("beats", lambda s: c0(s).pop("beats"))
    expect("beats", lambda s: c0(s).update(beats=[]))
    expect("beats", lambda s: c0(s).update(beats=[[f"0–{d0}초", "a", ""]] * 7))
    expect("beats", lambda s: c0(s).update(beats=[["1–2초", "a", ""]]))  # 0에서 시작하지 않음
    expect("beats", lambda s: c0(s).update(beats=[[f"0–{d0 - 1}초", "a", ""]]))  # dur보다 일찍 끝남
    expect("beats", lambda s: c0(s).update(beats=[["0–1초", "a", ""], [f"2–{d0}초", "b", ""]]))  # 틈
    expect("beats", lambda s: c0(s).update(beats=[[f"0~{d0}초", "a", ""]]))  # 형식
    expect("beats", lambda s: c0(s).update(beats=[[f"0–{d0}초", " ", ""]]))  # 화면 비어 있음
    expect_ok(lambda s: c0(s).update(beats=[[f"0-{d0}초", "a", ""]]))  # 하이픈 허용
    expect_ok(lambda s: c0(s).update(beats=[[f"0–{d0 + 0.005}초", "a", ""]]))  # 허용 오차 안
    expect("record", lambda s: s["cuts"][rec].pop("record"))
    expect("ai_prompt", lambda s: s["cuts"][mg].pop("ai_prompt"))
    expect("ai_prompt", lambda s: s["cuts"][mg].update(ai_prompt="한글이 들어간 prompt with enough english words here"))
    expect("ai_prompt", lambda s: s["cuts"][mg].update(ai_prompt="a title in a bold font slides in from the left side"))
    expect("ai_prompt", lambda s: s["cuts"][mg].update(ai_prompt="one two three four five six seven"))
    expect_ok(lambda s: s["cuts"][mg].update(ai_prompt="one two three four five six seven eight"))
    expect("motion_style", lambda s: s.pop("motion_style"))
    expect("production", lambda s: s.update(production="화면 녹화"))
    expect("ai_prompt", lambda s: s["cuts"][rec].update(ai_prompt="한글 프롬프트"))  # 녹화 컷이라도 있으면 검사
    expect_ok(lambda s: s.pop("production"))  # 없으면 빈 배열
    check_detail({**copy.deepcopy(spec), "cuts": [dict(spec["cuts"][0], dur="5")] + spec["cuts"][1:]})  # traceback 없음
    check_detail({**copy.deepcopy(spec), "cuts": [[1, 2]] + spec["cuts"][1:]})
    check_detail({"cuts": "x"})
    p = full_prompt(spec, spec["cuts"][mg])
    assert p.startswith(spec["motion_style"]) and NO_TEXT in p and p.endswith(f"{spec['cuts'][mg]['dur']:g} seconds."), p

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "storyboard.json"
        path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            assert run("build", path) == 0
        prs = Presentation(Path(tmp) / "detail.pptx")
        assert len(prs.slides) == len(spec["cuts"]) + 1
        bad = copy.deepcopy(spec)
        bad["cuts"][0]["dur"] = 99  # summary 검사(dur 1~60)가 먼저 막는다
        path.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()) as quiet:
            assert run("check", path) == 1
        assert "[summary]" in quiet.getvalue(), quiet.getvalue()
        path.write_text("{not json", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            assert run("check", path) == 1
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif len(sys.argv) == 3 and sys.argv[1] in ("check", "build"):
        sys.exit(run(sys.argv[1], sys.argv[2]))
    else:
        print(__doc__)
        sys.exit(2)
