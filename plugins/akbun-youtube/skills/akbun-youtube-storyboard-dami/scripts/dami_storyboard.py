# /// script
# requires-python = ">=3.12"
# dependencies = ["python-pptx"]
# ///
"""영상 스토리보드 spec(storyboard.json)을 검사하고 스케치 프롬프트·pptx·대본을 만든다.

  check <spec>     검사만. 실패 이유를 모아 출력하고 종료 코드 1
  prompts <spec>   검사 후 spec 옆 prompts/cut_NN.txt
  build <spec>     검사 후 storyboard.pptx, script.md (sketches/cut_NN.png가 있으면 넣는다)
  --selftest       example spec으로 build하고 망가뜨린 spec이 기대대로 실패하는지 확인
"""
import copy
import io
import json
import math
import re
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
REF = Path(__file__).resolve().parent.parent / "references"

# 검사 상수. references/spec.md의 표와 같은 값으로 유지한다.
MIN_CUTS, MAX_CUTS = 6, 40
MIN_DUR, MAX_DUR = 1, 60
MAX_PARTS = 8  # 개요 한 장의 파트 표에 들어가는 수
MAX_RATE = 7  # 공백 뺀 글자 수 / dur
TL_PAGE_SEC = 120  # 타임라인 한 장에 담는 시간(초). 넘으면 장을 나눈다
MAX_AFTER_ANSWER = 0.20  # 답이 나온 컷 뒤 길이 / 전체 길이
SKETCH_WORDS = (6, 40)
BANNED = re.compile(r"\b(fonts?|typefaces?|texts?|captions?|letters?|lettering)\b", re.I)
HANGUL = re.compile(r"[ᄀ-ᇿ㄰-㆏가-힣]")
VOICES = ("live", "adr", "none")
SOURCES = ("화면 녹화", "촬영", "모션그래픽", "사진·자료")
MUSIC_TEXT = ("mood", "genre", "instruments", "energy", "search_keywords", "generation_prompt")

STYLE = ("Quick black-and-white pencil storyboard sketch: loose graphite lines, light gray tone shading, white paper, no border, no color. "
         "Movement is shown only with bold hollow arrow shapes. A generic sketch, not imitating any specific work, artist or existing storyboard.")
NO_WRITING = "No letters, numbers or writing anywhere in the image."
NO_FACE = ("No human face anywhere. Draw a person or hands only if the scene above asks for them, and then only as hands, a back view or a faceless silhouette. "
           "If a reference image is attached, copy only its line weight and shading, never its objects, hands or layout.")

# pptx 색(트랙 종류마다 하나)과 글꼴
FONT = "Pretendard"  # SIL OFL 1.1. 상업용으로 써도 되는 공개 라이선스 글꼴만 쓴다
INK, MUTED, WHITE, PAPER = "222222", "777777", "FFFFFF", "F4F4F4"
C_LABEL, C_V1, C_V1_MOTION, C_V2 = "3A3F4B", "4C78A8", "8E6BBF", "E0A030"
C_A1, C_A2, C_A3, C_A4, C_MARK = "5BA17A", "D9534F", "2E9CA6", "9AA0A6", "C0392B"


def load(name):
    return {r["id"]: r for r in (json.loads(ln) for ln in (REF / name).read_text(encoding="utf-8").splitlines() if ln.strip())}


def sval(d, k):
    v = d.get(k) if isinstance(d, dict) else None
    return v if isinstance(v, str) else ""


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def fmt(t):
    """mm:ss, 초는 반올림(0.5초는 올림)."""
    s = int(t + 0.5)
    return f"{s // 60:02d}:{s % 60:02d}"


def timeline(spec):
    """컷마다 (시작, 끝) 초. 시작은 앞 컷 dur의 합."""
    t, out = 0.0, []
    for c in spec["cuts"]:
        out.append((t, round(t + c["dur"], 3)))
        t = round(t + c["dur"], 3)
    return out


def check(spec):
    """실패 이유 목록. 비면 통과."""
    genres, shots, moves = load("genres.jsonl"), load("shots.jsonl"), load("moves.jsonl")
    out = []
    if not isinstance(spec, dict):
        return ["[spec] 최상위는 객체여야 한다"]
    for k in ("title", "message", "audience", "intent", "source_summary"):
        if not sval(spec, k).strip():
            out.append(f"[key] {k}: 비어 있지 않은 문자열 필요")
    hid = lambda v: v if isinstance(v, str) else None  # 문자열이 아닌 id는 없는 id로 본다
    genre = genres.get(hid(spec.get("genre")))
    if not genre:
        out.append(f"[genre] genres.jsonl의 id가 아님: {spec.get('genre')}")
    parts = spec.get("parts")
    pids = []
    if not isinstance(parts, list) or not parts:
        out.append("[parts] 1개 이상의 {id, title} 배열 필요")
    else:
        for p in parts:
            if not sval(p, "id").strip() or not sval(p, "title").strip():
                out.append(f"[parts] id·title은 비어 있지 않은 문자열: {p}")
            else:
                pids.append(p["id"])
        if len(parts) > MAX_PARTS:
            out.append(f"[parts] 파트는 {MAX_PARTS}개 이하: {len(parts)}")
        if len(set(pids)) != len(pids):
            out.append("[parts] id 중복")
    cuts = spec.get("cuts")
    if not isinstance(cuts, list):
        return out + ["[cuts] 배열 필요"]
    n = len(cuts)
    if not MIN_CUTS <= n <= MAX_CUTS:
        out.append(f"[cuts] 컷 수는 {MIN_CUTS}~{MAX_CUTS}: {n}")
    last, used, hook, run, prev = 0, set(), 0.0, 0, None
    for i, c in enumerate(cuts, 1):
        w = f"컷 {i}"
        if not isinstance(c, dict):
            out.append(f"[cut] {w}: 객체 필요")
            continue
        for k in ("part", "source", "sketch", "desc", "intent", "voice"):
            if not sval(c, k).strip():
                out.append(f"[key] {w}.{k}: 비어 있지 않은 문자열 필요")
        if not isinstance(c.get("narration"), str):
            out.append(f"[key] {w}.narration: 문자열 필요(없으면 빈 문자열)")
        for k, tab in (("shot", shots), ("move", moves)):
            if hid(c.get(k)) not in tab:
                out.append(f"[{k}] {w}: {k}s.jsonl의 id가 아님: {c.get(k)}")
        if c.get("source") and c["source"] not in SOURCES:
            out.append(f"[source] {w}: {'/'.join(SOURCES)} 중 하나: {c['source']}")
        dur = c.get("dur")
        if not num(dur) or not MIN_DUR <= dur <= MAX_DUR:
            out.append(f"[dur] {w}: {MIN_DUR}~{MAX_DUR}초: {dur}")
            dur = None
        part = c.get("part")
        if part in pids:
            used.add(part)
            idx = pids.index(part)
            if idx < last:
                out.append(f"[part-order] {w}: 파트 {part}가 앞 파트로 돌아가 끊겼다 다시 나옴")
            last = max(last, idx)
            if idx == 0 and dur:
                hook += dur
        elif sval(c, "part"):
            out.append(f"[part] {w}: parts의 id가 아님: {part}")
        voice, nar = c.get("voice"), c.get("narration") if isinstance(c.get("narration"), str) else ""
        if voice not in VOICES and sval(c, "voice"):
            out.append(f"[voice] {w}: {'/'.join(VOICES)} 중 하나: {voice}")
        if voice == "adr" and not sval(c, "adr_reason").strip():
            out.append(f"[adr] {w}: voice가 adr이면 adr_reason 필요")
        if voice == "none" and nar != "":
            out.append(f"[voice-none] {w}: voice가 none이면 narration은 빈 문자열")
        chars = len(re.sub(r"\s", "", nar))
        if dur and chars / dur > MAX_RATE:
            out.append(f"[rate] {w}: 말하는 속도 {chars / dur:.1f}자/초 > {MAX_RATE}")
        sk = sval(c, "sketch")
        words = len(sk.split())
        if sk and not SKETCH_WORDS[0] <= words <= SKETCH_WORDS[1]:
            out.append(f"[sketch] {w}: 영어 {SKETCH_WORDS[0]}~{SKETCH_WORDS[1]}단어: {words}")
        if HANGUL.search(sk):
            out.append(f"[sketch] {w}: 한글 금지")
        if (b := BANNED.search(sk)):
            out.append(f"[sketch] {w}: 금지 낱말 '{b.group()}'")
        mv = c.get("move")
        if mv in moves and not moves[mv].get("none"):
            run = run + 1 if mv == prev else 1
            if run >= 3:
                out.append(f"[move-run] {w}: move '{mv}'가 3컷 연속")
        else:
            run = 0
        prev = mv
        if "sfx" in c and not (isinstance(c["sfx"], list) and all(isinstance(x, str) for x in c["sfx"])):
            out.append(f"[sfx] {w}: 문자열 배열 필요")
        if "overlay" in c and not isinstance(c["overlay"], str):
            out.append(f"[overlay] {w}: 문자열 필요")
    if pids and set(pids) - used:
        out.append(f"[part-unused] 쓰이지 않은 파트: {sorted(set(pids) - used)}")
    if genre and pids and hook > genre["hook_max"] + 1e-9:
        out.append(f"[hook] 첫 파트 길이 {hook:g}초 > {genre['hook_max']}초")
    if cuts and isinstance(cuts[0], dict) and cuts[0].get("shot") == "title-card":
        out.append("[hook-open] 컷 1: title-card로 시작하지 않는다. 궁금증을 만드는 장면을 먼저 둔다")
    if n >= 8 and len({hid(c.get("shot")) for c in cuts if isinstance(c, dict)}) < 3:
        out.append("[shot-kinds] 컷이 8개 이상이면 shot 3종류 이상")
    # 답이 나온 뒤는 짧게, 반응 요소는 하나 이상
    durs = [c["dur"] if isinstance(c, dict) and num(c.get("dur")) else 0 for c in cuts]
    ac = spec.get("answer_cut")
    if not isinstance(ac, int) or isinstance(ac, bool) or not 1 <= ac <= n:
        out.append(f"[answer] answer_cut: 1~컷 수({n})의 정수 필요")
    elif sum(durs) and sum(durs[ac:]) / sum(durs) > MAX_AFTER_ANSWER + 1e-9:
        out.append(f"[answer] 답이 나온 컷 {ac} 뒤가 {sum(durs[ac:]):g}초로 전체의 {MAX_AFTER_ANSWER:.0%}를 넘는다. 마무리를 줄인다")
    re_ = spec.get("reaction")
    if not isinstance(re_, dict) or not sval(re_, "text").strip() or not isinstance(re_.get("cut"), int) or isinstance(re_.get("cut"), bool) or not 1 <= re_["cut"] <= n:
        out.append(f"[reaction] reaction: {{cut: 1~{n}, text: 비어 있지 않은 문자열}} 필요")
    music = spec.get("music")
    if not isinstance(music, list):
        return out + ["[music] 배열 필요(비어도 됨)"]
    spans, ids = [], set()
    for j, m in enumerate(music, 1):
        w = f"music {j}"
        if not isinstance(m, dict):
            out.append(f"[music] {w}: 객체 필요")
            continue
        if not sval(m, "id").strip() or hid(m.get("id")) in ids:
            out.append(f"[music] {w}: id 필요, 중복 없이")
        ids.add(hid(m.get("id")))
        for k in MUSIC_TEXT:
            if not sval(m, k).strip():
                out.append(f"[music] {w}.{k}: 비어 있지 않은 문자열 필요")
        if not num(m.get("bpm")) or m["bpm"] <= 0:
            out.append(f"[music] {w}.bpm: 0보다 큰 숫자")
        a, b = m.get("from_cut"), m.get("to_cut")
        if not (isinstance(a, int) and isinstance(b, int)) or isinstance(a, bool) or isinstance(b, bool):
            out.append(f"[music] {w}: from_cut·to_cut은 정수")
        elif not 1 <= a <= b <= n:
            out.append(f"[music] {w}: 1 ≤ from_cut ≤ to_cut ≤ 컷 수({n}): {a}~{b}")
        else:
            spans.append((a, b, w))
    spans.sort()
    for (a1, b1, w1), (a2, b2, w2) in zip(spans, spans[1:]):
        if a2 <= b1:
            out.append(f"[music-overlap] {w1}({a1}~{b1})과 {w2}({a2}~{b2}) 겹침")
    return out


def prompt(cut, shots, moves):
    arrow = moves[cut["move"]].get("arrow", "")
    parts = [STYLE, f"Draw: {shots[cut['shot']]['draw']}.", f"Scene: {cut['sketch'].rstrip('.')}.", arrow, NO_WRITING, NO_FACE, "Landscape 16:9 frame."]
    return " ".join(p for p in parts if p)


def write_prompts(spec, base):
    shots, moves = load("shots.jsonl"), load("moves.jsonl")
    d = base / "prompts"
    d.mkdir(exist_ok=True)
    for i, c in enumerate(spec["cuts"], 1):
        (d / f"cut_{i:02d}.txt").write_text(prompt(c, shots, moves) + "\n", encoding="utf-8")
    return len(spec["cuts"])


# ---- script.md ----

def script_md(spec):
    tl, parts = timeline(spec), {p["id"]: p["title"] for p in spec["parts"]}
    out, adr = [f"# {spec['title']}", "", f"핵심 메시지: {spec['message']}", ""], []
    cur = None
    for i, (c, (a, b)) in enumerate(zip(spec["cuts"], tl), 1):
        if c["part"] != cur:
            cur = c["part"]
            out += [f"## {parts[cur]}", ""]
        rng = f"{fmt(a)}–{fmt(b)}"
        out += [f"컷 {i} ({rng}){' · 후시녹음' if c['voice'] == 'adr' else ''}", "", c["narration"] or "(대본 없음)", ""]
        if c["voice"] == "adr":
            adr.append((i, rng, c["adr_reason"]))
    out += ["## 후시녹음 구간", ""]
    if adr:
        out += ["| 컷 | 시각 | 이유 |", "|---|---|---|"] + [f"| {i} | {r} | {why} |" for i, r, why in adr]
    else:
        out.append("후시녹음 구간 없음")
    return "\n".join(out) + "\n"


# ---- pptx ----

def build_pptx(spec, base):
    from PIL import Image
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    from pptx.oxml.ns import qn
    from pptx.util import Inches, Pt

    shots, moves = load("shots.jsonl"), load("moves.jsonl")
    genre = load("genres.jsonl")[spec["genre"]]
    cuts, tl, parts = spec["cuts"], timeline(spec), spec["parts"]
    ptitle = {p["id"]: p["title"] for p in parts}
    total = tl[-1][1]
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)

    def font(run, size, bold, color):
        f = run.font
        f.size, f.bold, f.name = Pt(size), bold, FONT
        f.color.rgb = RGBColor.from_string(color)
        rpr = run._r.get_or_add_rPr()
        rpr.append(rpr.makeelement(qn("a:ea"), {"typeface": FONT}))  # latin 뒤에 east asian 글꼴

    def fill_tf(tf, paras, size, color, align=None, bold=False):
        tf.word_wrap = True
        for k, p in enumerate(paras):
            para = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            if align:
                para.alignment = align
            for t, b in ([(p, bold)] if isinstance(p, str) else p):
                r = para.add_run()
                r.text = t
                font(r, size, b, color)

    def new():
        return prs.slides.add_slide(prs.slide_layouts[6])

    def tb(sl, x, y, w, h, paras, size=10, color=INK, bold=False, align=None, name=None):
        s = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        fill_tf(s.text_frame, paras, size, color, align, bold)
        if name:
            s.name = name
        return s

    def box(sl, x, y, w, h, paras=(), size=9, color=WHITE, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE, name=None, wrap=True, bold=False):
        s = sl.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
        if fill:
            s.fill.solid()
            s.fill.fore_color.rgb = RGBColor.from_string(fill)
        else:
            s.fill.background()
        if line:
            s.line.color.rgb = RGBColor.from_string(line)
            s.line.width = Pt(0.75)
        else:
            s.line.fill.background()
        s.shadow.inherit = False
        tf = s.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = tf.margin_right = Inches(0.03)
        tf.margin_top = tf.margin_bottom = Inches(0.02)
        fill_tf(tf, list(paras), size, color, PP_ALIGN.CENTER, bold)
        tf.word_wrap = wrap
        if name:
            s.name = name
        return s

    def table(sl, x, y, header, rows, widths, size=9, row_h=0.3):
        gs = sl.shapes.add_table(len(rows) + 1, len(header), Inches(x), Inches(y), Inches(sum(widths)), Inches(row_h * (len(rows) + 1)))
        gs.name = "table"
        for j, wd in enumerate(widths):
            gs.table.columns[j].width = Inches(wd)
        for i, row in enumerate([header] + rows):
            gs.table.rows[i].height = Inches(row_h)
            for j, val in enumerate(row):
                c = gs.table.cell(i, j)
                c.fill.solid()
                c.fill.fore_color.rgb = RGBColor.from_string(C_LABEL if i == 0 else (WHITE if i % 2 else PAPER))
                fill_tf(c.text_frame, [str(val)], size, WHITE if i == 0 else INK, bold=(i == 0))

    def heading(sl, text):
        tb(sl, 0.4, 0.25, 12.5, 0.6, [text], 22, bold=True)

    # 1 개요
    sl = new()
    tb(sl, 0.4, 0.3, 12.5, 0.7, [spec["title"]], 26, bold=True, name="title")
    tb(sl, 0.4, 1.0, 12.5, 0.4, [f"{genre['ko']} · 총 {fmt(total)} · 컷 {len(cuts)}개"], 12, MUTED)
    for k, (label, key) in enumerate((("핵심 메시지", "message"), ("대상", "audience"), ("의도", "intent"), ("입력 요약", "source_summary"))):
        tb(sl, 0.4 + (k % 2) * 6.3, 1.5 + (k // 2) * 1.5, 6.1, 1.4, [[(label, True)], spec[key]], 11, name=f"info_{key}")
    tb(sl, 0.4, 4.25, 12.5, 0.3, [[("답이 나오는 곳 ", True), (f"컷 {spec['answer_cut']} ({fmt(tl[spec['answer_cut'] - 1][0])}) · 그 뒤 {total - tl[spec['answer_cut'] - 1][1]:g}초", False),
                                    ("    반응 요소 ", True), (f"컷 {spec['reaction']['cut']} · {spec['reaction']['text']}", False)]], 10, name="info_retention")
    rows = []
    for p in parts:
        idx = [i for i, c in enumerate(cuts) if c["part"] == p["id"]]
        rows.append([p["title"], f"{fmt(tl[idx[0]][0])}–{fmt(tl[idx[-1]][1])}", f"{idx[0] + 1}–{idx[-1] + 1}"])
    table(sl, 0.4, 4.75, ["파트", "시간 범위", "컷 번호"], rows, [4.0, 3.0, 2.5], 10, 0.3 if len(rows) < 7 else 0.25)

    # 2 타임라인. 한 장에 TL_PAGE_SEC초까지 담고 넘으면 다음 장으로 이어진다.
    x0, x1, gap = 2.1, 12.9, 0.02
    n_tl = max(1, math.ceil(total / TL_PAGE_SEC))
    win = total if n_tl == 1 else TL_PAGE_SEC
    sc = (x1 - x0) / win
    starts = {}
    for i, c in enumerate(cuts):
        starts.setdefault(c["part"], i)
    order = [p["id"] for p in parts]
    step = next((s for s in (5, 10, 15, 30, 60) if win / s <= 12), 60)
    tracks = [("V2 모션그래픽·자막", C_V2), ("V1 영상", C_V1), ("A1 현장음·녹화 음성", C_A1), ("A2 후시녹음", C_A2), ("A3 배경음악", C_A3), ("A4 효과음", C_A4)]
    legend = [(C_V1, "V1 영상"), (C_V1_MOTION, "V1 모션그래픽 컷"), (C_V2, "V2 얹는 것"), (C_A1, "A1 현장음"), (C_A2, "A2 후시녹음"), (C_A3, "A3 BGM"), (C_A4, "A4 효과음")]
    for pg in range(n_tl):
        p0 = pg * win
        p1 = min(p0 + win, total)
        sl = new()
        heading(sl, "타임라인 (DaVinci Resolve 타임라인처럼 읽기)" + (f" {pg + 1}/{n_tl} · {fmt(p0)}–{fmt(p1)}" if n_tl > 1 else ""))
        tx = lambda t: x0 + (t - p0) * sc

        def blk(name, t0, t1, y, fill, label, h=0.5):
            # 이 장의 시간 범위와 겹치는 부분만 그린다. 장 경계에 걸친 블록은 두 장에 나뉘어 보인다.
            t0, t1 = max(t0, p0), min(t1, p1)
            if t1 - t0 <= 0:
                return
            box(sl, tx(t0) + gap / 2, y, max((t1 - t0) * sc - gap, 0.05), h, [label], 9, WHITE, fill, name=name, wrap=False)

        for k, pid in enumerate(order):
            t0 = tl[starts[pid]][0]
            t1 = tl[starts[order[k + 1]]][0] if k + 1 < len(order) else total
            if not p0 <= t0 < p1:
                continue
            sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(tx(t0)), Inches(1.0), Inches(0.03), Inches(0.5)).name = f"marker_pole_{pid}"
            box(sl, tx(t0) + 0.03, 1.0, max((min(t1, p1) - t0) * sc - 0.05, 0.4), 0.3, [ptitle[pid]], 9, WHITE, C_MARK, None, MSO_SHAPE.PENTAGON, f"marker_{pid}", False)
        for k in range(math.ceil(p0 / step), int(p1 // step) + 1):
            t = k * step
            tb(sl, tx(t) - 0.4, 1.6, 0.8, 0.25, [fmt(t)], 8, MUTED, align=PP_ALIGN.CENTER, name=f"ruler_{fmt(t)}")
            box(sl, tx(t), 1.85, 0.01, 0.12, fill=MUTED, name=f"tick_{fmt(t)}")
        ys = {}
        for k, (lab, col) in enumerate(tracks):
            ys[lab[:2]] = y = 2.1 + k * 0.62
            box(sl, 0.4, y, 1.6, 0.5, [lab], 9, WHITE, C_LABEL, name=f"track_{lab[:2]}")
        for i, (c, (a, b)) in enumerate(zip(cuts, tl), 1):
            if sval(c, "overlay"):
                blk(f"v2_cut_{i:02d}", a, b, ys["V2"], C_V2, str(i))
            blk(f"v1_cut_{i:02d}", a, b, ys["V1"], C_V1_MOTION if c["source"] == "모션그래픽" else C_V1, str(i))
            if c["voice"] == "live":
                blk(f"a1_cut_{i:02d}", a, b, ys["A1"], C_A1, str(i))
            if c["voice"] == "adr":
                blk(f"a2_cut_{i:02d}", a, b, ys["A2"], C_A2, str(i))
            if c.get("sfx") and p0 <= a < p1:
                box(sl, tx(a) + gap / 2, ys["A4"], min(0.3, max((b - a) * sc - gap, 0.05)), 0.5, [str(i)], 8, WHITE, C_A4, name=f"a4_cut_{i:02d}", wrap=False)
        for m in spec["music"]:
            blk(f"a3_{m['id']}", tl[m["from_cut"] - 1][0], tl[m["to_cut"] - 1][1], ys["A3"], C_A3, m["id"])
        for k, (col, lab) in enumerate(legend):
            box(sl, 0.4 + k * 1.75, 6.55, 0.2, 0.2, fill=col, name=f"legend_{k}")
            tb(sl, 0.65 + k * 1.75, 6.5, 1.5, 0.3, [lab], 9, MUTED)
        tb(sl, 0.4, 6.9, 12.5, 0.3, ["블록 안 숫자는 컷 번호. 블록은 하나씩 끌어서 고칠 수 있다."], 9, MUTED)

    # 3 사운드·후시녹음 계획
    def sound(title, header, rows, widths, per, size=8, row_h=0.3):
        chunks = [rows[i:i + per] for i in range(0, len(rows), per)] or [[["없음"] + [""] * (len(header) - 1)]]
        for k, ch in enumerate(chunks, 1):
            sl = new()
            heading(sl, title + (f" ({k}/{len(chunks)})" if len(chunks) > 1 else ""))
            table(sl, 0.4, 1.1, header, ch, widths, size, row_h)

    span = lambda a, b: f"{fmt(tl[a - 1][0])}–{fmt(tl[b - 1][1])} (컷 {a}–{b})"
    sound("사운드 계획 - 배경음악", ["id", "구간", "분위기", "장르 · BPM", "악기", "에너지", "검색어", "생성 문장"],
          [[m["id"], span(m["from_cut"], m["to_cut"]), m["mood"], f"{m['genre']} · {m['bpm']:g}", m["instruments"], m["energy"], m["search_keywords"], m["generation_prompt"]] for m in spec["music"]],
          [0.6, 1.3, 1.0, 1.2, 1.5, 1.7, 2.2, 2.5], 5, 8, 0.7)
    sound("후시녹음 구간", ["컷", "시각", "이유"], [[i, span(i, i).split(" (")[0], c["adr_reason"]] for i, c in enumerate(cuts, 1) if c["voice"] == "adr"], [0.8, 2.0, 9.7], 12, 9, 0.35)
    sound("효과음", ["컷", "서술"], [[i, "; ".join(c["sfx"])] for i, c in enumerate(cuts, 1) if c.get("sfx")], [0.8, 11.7], 12, 9, 0.35)

    # 4 스토리보드
    cw, cx0 = 4.0, 0.47
    for s0 in range(0, len(cuts), 3):
        sl = new()
        notes = []
        for k, i in enumerate(range(s0, min(s0 + 3, len(cuts)))):
            c, (a, b), x = cuts[i], tl[i], cx0 + k * (cw + 0.2)
            box(sl, x, 0.3, 0.45, 0.45, [str(i + 1)], 12, WHITE, C_LABEL, None, MSO_SHAPE.OVAL, f"num_{i + 1:02d}", bold=True)
            tb(sl, x + 0.5, 0.33, cw - 0.5, 0.4, [f"{fmt(a)}–{fmt(b)} · {ptitle[c['part']]} · {c['source']}"], 10, bold=True, name=f"head_{i + 1:02d}")
            img = base / "sketches" / f"cut_{i + 1:02d}.png"
            if img.exists():
                # 원본 PNG는 장당 몇 MB라 pptx가 무거워진다. 폭 1280px JPEG로 줄여 넣는다(Pillow는 python-pptx 의존성).
                buf = io.BytesIO()
                im = Image.open(img).convert("RGB")
                im.thumbnail((1280, 1280))
                im.save(buf, "JPEG", quality=85)
                buf.seek(0)
                pic = sl.shapes.add_picture(buf, Inches(x), Inches(0.9), Inches(cw), Inches(cw * 9 / 16))
                pic.name = f"sketch_{i + 1:02d}"
                box(sl, x, 0.9, cw, cw * 9 / 16, line=INK, name=f"frame_{i + 1:02d}")
            else:
                box(sl, x, 0.9, cw, cw * 9 / 16, ["스케치 없음"], 11, MUTED, "E6E6E6", MUTED, name=f"frame_{i + 1:02d}")
            mv = f"{moves[c['move']]['ko']}" + (f" · {c['move_note']}" if sval(c, "move_note") else "")
            paras = [[(f"{shots[c['shot']]['ko']} · {mv}", True)],
                     [("화면 ", True), (c["desc"], False)],
                     [("의도 ", True), (c["intent"], False)],
                     [("대본 ", True), (("[후시녹음] " if c["voice"] == "adr" else "") + (c["narration"] or "(없음)"), False)]]
            if sval(c, "overlay"):
                paras.append([("얹는 것 ", True), (c["overlay"], False)])
            if c.get("sfx"):
                paras.append([("효과음 ", True), ("; ".join(c["sfx"]), False)])
            tb(sl, x, 3.3, cw, 3.75, paras, 11, name=f"info_{i + 1:02d}")
            notes.append(f"컷 {i + 1}: {c['narration'] or '(대본 없음)'}")
        tb(sl, 0.47, 7.12, 6, 0.3, [f"스토리보드 {s0 // 3 + 1}/{math.ceil(len(cuts) / 3)}"], 8, MUTED)
        sl.notes_slide.notes_text_frame.text = "\n".join(notes)

    prs.save(str(base / "storyboard.pptx"))


# ---- 실행 ----

def run(cmd, spec_path):
    path = Path(spec_path)
    spec = json.loads(path.read_text(encoding="utf-8"))
    fails = check(spec)
    if fails:
        print("FAIL")
        print("\n".join(f"- {f}" for f in fails))
        return 1
    base = path.parent
    if cmd == "prompts":
        print(f"prompts {write_prompts(spec, base)}개 -> {base / 'prompts'}")
    elif cmd == "build":
        build_pptx(spec, base)
        (base / "script.md").write_text(script_md(spec), encoding="utf-8")
        print(f"build ok -> {base / 'storyboard.pptx'}, {base / 'script.md'}")
    else:
        print(f"check ok (컷 {len(spec['cuts'])}개, 총 {fmt(timeline(spec)[-1][1])})")
    return 0


def selftest():
    from pptx import Presentation

    spec = json.loads((REF / "example" / "storyboard.json").read_text(encoding="utf-8"))
    assert check(spec) == [], check(spec)
    n = len(spec["cuts"])

    def expect(tag, mut):
        s = copy.deepcopy(spec)
        mut(s)
        got = check(s)
        assert any(f"[{tag}]" in g for g in got), (tag, got)

    def expect_ok(mut):
        s = copy.deepcopy(spec)
        mut(s)
        assert check(s) == [], check(s)

    cuts = lambda s: s["cuts"]
    expect("rate", lambda s: cuts(s)[0].update(narration="가" * 36, dur=5))  # 7.2자/초
    expect_ok(lambda s: cuts(s)[0].update(narration="가" * 35, dur=5))  # 7.0자/초는 통과
    expect("sketch", lambda s: cuts(s)[0].update(sketch="한글 sketch of a hand on a desk with a cup"))
    expect("sketch", lambda s: cuts(s)[0].update(sketch="a hand holding a cup next to the text on a desk"))
    expect("sketch", lambda s: cuts(s)[0].update(sketch="one two three four five"))
    expect_ok(lambda s: cuts(s)[0].update(sketch="one two three four five six"))
    expect_ok(lambda s: cuts(s)[0].update(sketch=" ".join(["word"] * 40)))
    expect("sketch", lambda s: cuts(s)[0].update(sketch=" ".join(["word"] * 41)))
    expect("dur", lambda s: cuts(s)[1].update(dur=61))
    expect("dur", lambda s: cuts(s)[1].update(dur=0.9))
    expect("move-run", lambda s: [c.update(move="punch-in") for c in cuts(s)[2:5]])
    expect_ok(lambda s: [c.update(move="hold") for c in cuts(s)[2:6]])  # hold는 연속 허용
    expect("part-order", lambda s: cuts(s)[4].update(part="hook"))
    expect("part-unused", lambda s: [c.update(part="problem") for c in cuts(s) if c["part"] == "wrap"])
    expect("adr", lambda s: cuts(s)[0].pop("adr_reason"))
    expect("voice-none", lambda s: cuts(s)[7].update(narration="말"))
    expect("hook", lambda s: cuts(s)[1].update(dur=11))  # 5+11=16 > 15
    expect("answer", lambda s: s.update(answer_cut=3))  # 뒤가 20%를 넘는다
    expect("answer", lambda s: s.pop("answer_cut"))
    expect("reaction", lambda s: s.pop("reaction"))
    expect("reaction", lambda s: s.update(reaction={"cut": 99, "text": "x"}))
    expect("parts", lambda s: s.update(parts=s["parts"] + [{"id": f"x{i}", "title": "x"} for i in range(4)]))  # 9개
    expect("shot", lambda s: cuts(s)[0].update(shot={}))  # 타입이 틀려도 traceback 없이 FAIL
    expect("genre", lambda s: s.update(genre=["x"]))
    expect("hook-open", lambda s: cuts(s)[0].update(shot="title-card"))
    expect_ok(lambda s: cuts(s)[1].update(dur=10))  # 5+10=15는 통과
    expect("shot", lambda s: cuts(s)[0].update(shot="nope"))
    expect("move", lambda s: cuts(s)[0].update(move="nope"))
    expect("genre", lambda s: s.update(genre="nope"))
    expect("cuts", lambda s: s.update(cuts=cuts(s)[:5]))
    expect("shot-kinds", lambda s: [c.update(shot="screen-full") for c in cuts(s)])
    expect("music-overlap", lambda s: s["music"][1].update(from_cut=5))
    expect("music", lambda s: s["music"][1].update(to_cut=n + 1))
    expect("music", lambda s: s["music"][0].update(mood=""))
    expect_ok(lambda s: s.update(music=[]))
    s = copy.deepcopy(spec)  # 한 번에 여러 이유를 모은다
    cuts(s)[0].update(shot="nope", dur=99)
    s["music"][0]["bpm"] = 0
    assert len(check(s)) >= 3

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        (base / "storyboard.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        from PIL import Image
        (base / "sketches").mkdir()
        Image.new("RGB", (1600, 900), (200, 200, 200)).save(base / "sketches" / "cut_01.png")
        assert run("prompts", base / "storyboard.json") == 0
        txt = (base / "prompts" / "cut_01.txt").read_text(encoding="utf-8")
        assert "No letters" in txt and "No human face" in txt and "16:9" in txt and "arrow" in txt
        assert len(list((base / "prompts").glob("cut_*.txt"))) == n
        assert run("build", base / "storyboard.json") == 0
        prs = Presentation(str(base / "storyboard.pptx"))
        pages = -(-n // 3)  # 스토리보드 장 수
        assert len(prs.slides) == 2 + 3 + pages, len(prs.slides)  # 개요, 타임라인, 사운드 표 3장
        names = [sh.name for sl in prs.slides for sh in sl.shapes]
        count = lambda p: sum(x.startswith(p) for x in names)
        assert count("v1_cut_") == n
        assert count("a1_cut_") == sum(c["voice"] == "live" for c in spec["cuts"])
        assert count("a2_cut_") == sum(c["voice"] == "adr" for c in spec["cuts"])
        assert count("a3_") == len(spec["music"])
        assert count("v2_cut_") == sum(bool(c.get("overlay")) for c in spec["cuts"])
        assert count("a4_cut_") == sum(bool(c.get("sfx")) for c in spec["cuts"])
        assert count("marker_pole_") == len(spec["parts"])
        assert count("frame_") == n and count("sketch_") == 1  # cut_01.png만 있음
        assert sum(sh.shape_type == 13 for sl in prs.slides for sh in sl.shapes) == 1
        assert all(sl.has_notes_slide and "컷" in sl.notes_slide.notes_text_frame.text for sl in list(prs.slides)[-pages:])
        md = (base / "script.md").read_text(encoding="utf-8")
        assert md.startswith("# ") and md.count("\n# ") == 0 and "## 후시녹음 구간" in md and "컷 1 (00:00–00:05) · 후시녹음" in md
        bad = base / "bad.json"
        s = copy.deepcopy(spec)
        s["cuts"][0]["shot"] = "nope"
        bad.write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
        assert run("check", bad) == 1
        # 긴 영상: 타임라인이 여러 장으로 나뉜다(컷 11개 x 30초 = 330초 -> 3장). 검사를 거치지 않고 바로 만든다.
        long = copy.deepcopy(spec)
        for c in long["cuts"]:
            c["dur"] = 30
        (base / "long").mkdir()
        build_pptx(long, base / "long")
        lp = Presentation(str(base / "long" / "storyboard.pptx"))
        assert len(lp.slides) == len(prs.slides) + 2, len(lp.slides)
        tl_pages = [sl for sl in lp.slides if any(sh.name == "track_V1" for sh in sl.shapes)]
        assert len(tl_pages) == 3
        assert all(0 <= sh.left and sh.left + sh.width <= lp.slide_width for sl in tl_pages for sh in sl.shapes), "타임라인 도형이 장 밖으로 나감"
    print("selftest ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
    elif len(a) == 2 and a[0] in ("check", "prompts", "build"):
        sys.exit(run(a[0], a[1]))
    else:
        sys.exit(__doc__)
