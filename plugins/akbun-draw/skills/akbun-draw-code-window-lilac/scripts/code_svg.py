# /// script
# requires-python = ">=3.12"
# dependencies = ["pygments"]
# ///
"""코드를 문법 색이 들어간 SVG 줄(<g>)과 줄 좌표 JSON으로 바꾼다.

SVG는 줄마다 <text> 하나이고 토큰은 <tspan>이다. --cps를 주면 줄마다 data-write가 붙어 한 줄씩 타이핑된다
(render_doodle.py가 tspan 안 글자까지 센다). JSON에는 줄별 x·baseline·top·height·width와 타이핑 시작·끝 시각,
--mark로 찾은 글자 상자 좌표가 들어 있다. 줄 띠·토큰 상자 좌표는 이 JSON으로 계산하고 눈대중으로 정하지 않는다.

글꼴은 D2Coding 고정폭이다. 영문·숫자·기호는 0.5em, 한글 같은 전각 글자는 1em로 폭을 센다.

창 틀(그림자·신호등·제목줄)은 --frame으로 만든다. 출력 JSON의 content가 코드를 놓을 안쪽 사각형이다.

  uv run code_svg.py snippet.py --lang python --x 260 --y 300 --size 26 --cps 40 --start 0.6 \
      --mark check_token --svg code.svg --json code.json
  uv run code_svg.py --frame 200,180,1000,640 --title retry.py --svg frame.svg --json frame.json
  uv run code_svg.py --frame 1240,300,460,260 --card --svg card.svg --json card.json
  uv run code_svg.py --selftest
"""
import argparse
import json
import sys
import unicodedata
from pathlib import Path
from xml.sax.saxutils import escape

from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Comment, Keyword, Name, Number, String, Token

THEMES = {
  "light": {"text": "#24292F", "comment": "#8C959F", "keyword": "#8250DF", "string": "#0A7E3E", "number": "#C2410C",
            "function": "#0B63CE", "type": "#B35900", "gutter": "#B8BEC6"},
  "dark": {"text": "#E6EDF3", "comment": "#7D8590", "keyword": "#D2A8FF", "string": "#7EE787", "number": "#FFA657",
           "function": "#79C0FF", "type": "#FFA657", "gutter": "#4D5562"},
}
FONT = "'D2Coding', monospace"
LINE_PAUSE = 0.12  # 줄바꿈 사이 쉼(초)


def role(ttype):
  for kind, name in ((Comment, "comment"), (String, "string"), (Number, "number"), (Keyword.Type, "type"),
                     (Keyword, "keyword"), (Name.Function, "function"), (Name.Class, "function"), (Name.Builtin, "type")):
    if ttype in kind:
      return name
  return "text"


def cols(text):
  return sum(1.0 if unicodedata.east_asian_width(c) in "WF" else 0.5 for c in text) * 2


def build(code, lang, x, y, size, line_height, cps, start, gutter, theme, marks):
  colors = THEMES[theme]
  em = size / 2  # 반각 한 칸 폭
  step = size * line_height
  lines = [[]]
  for ttype, value in lex(code.rstrip("\n") + "\n", get_lexer_by_name(lang)):
    for i, part in enumerate(value.split("\n")):
      if i:
        lines.append([])
      if part:
        lines[-1].append((role(ttype), part))
  lines = lines[:-1] if not lines[-1] else lines

  svg = [f'<g font-family="{FONT}" font-size="{size}">']
  info, t = [], start
  for n, tokens in enumerate(lines, 1):
    merged = []
    for kind, text in tokens:  # 같은 색·공백 토큰은 앞 토큰에 붙여 tspan 수를 줄인다
      if merged and (merged[-1][0] == kind or not text.strip()):
        merged[-1][1] += text
      else:
        merged.append([kind, text])
    raw = "".join(text for _, text in merged)
    indent = len(raw) - len(raw.lstrip(" "))
    if merged:
      merged[0][1] = merged[0][1][indent:]
      merged = [m for m in merged if m[1]]
    body = raw[indent:]
    baseline = y + (n - 1) * step
    x0 = x + indent * em
    typed = len(body.replace(" ", "")) and cps
    t0, t1 = (round(t, 2), round(t + len(body) / cps, 2)) if typed else (None, None)
    if typed:
      t = t1 + LINE_PAUSE
    if gutter:
      svg.append(f'<text x="{x - size:.1f}" y="{baseline:.1f}" text-anchor="end" fill="{colors["gutter"]}">{n}</text>')
    if body.strip():
      write = f' data-write="{t0} {t1}"' if typed else ""
      spans = "".join(f'<tspan fill="{colors[k]}">{escape(s)}</tspan>' for k, s in merged)
      svg.append(f'<text x="{x0:.1f}" y="{baseline:.1f}" xml:space="preserve"{write}>{spans}</text>')
    info.append({"n": n, "text": raw, "x": round(x0, 1), "baseline": round(baseline, 1),
                 "top": round(baseline - size * 0.85 - (step - size) / 2, 1), "height": round(step, 1),
                 "width": round(cols(body) * em, 1), "t0": t0, "t1": t1})
  svg.append("</g>")

  found = []
  for word in marks:
    for line in info:
      at = line["text"].find(word)
      while at >= 0:
        left = x + cols(line["text"][:at]) * em
        found.append({"text": word, "line": line["n"], "x": round(left, 1), "top": round(line["baseline"] - size * 0.85, 1),
                      "width": round(cols(word) * em, 1), "height": round(size * 1.08, 1), "typed_at": line["t1"]})
        at = line["text"].find(word, at + 1)
  return "\n".join(svg), {"font_size": size, "half_width": em, "line_step": step, "end": round(t - LINE_PAUSE, 2) if cps else None,
                          "lines": info, "marks": found}


def frame(x, y, w, h, title, theme, card=False):
  """창 틀 <g>와 안쪽 사각형. 그림자는 filter 없이 어긋난 반투명 사각형 두 장으로 만든다(렌더가 빠름).
  card=True면 제목줄·신호등 없는 카드 틀(정보 카드)이다."""
  body, line, text = ("#FFFFFF", "#D6D6DA", "#57606A") if theme == "light" else ("#1B2224", "#2E3A3D", "#9AA4AB")
  if card:
    svg = [f'<g class="card">',
           f'<rect x="{x}" y="{y + 16}" width="{w}" height="{h}" rx="14" fill="#000" opacity="0.035"/>',
           f'<rect x="{x}" y="{y + 6}" width="{w}" height="{h}" rx="14" fill="#000" opacity="0.045"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{body}" stroke="{line}" stroke-width="1.5"/>', "</g>"]
    return "\n".join(svg), {"window": [x, y, w, h], "content": [x + 24, y + 24, w - 48, h - 48]}
  bar = 44
  svg = [f'<g class="window">',
         f'<rect x="{x}" y="{y + 16}" width="{w}" height="{h}" rx="14" fill="#000" opacity="0.035"/>',
         f'<rect x="{x}" y="{y + 6}" width="{w}" height="{h}" rx="14" fill="#000" opacity="0.045"/>',
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{body}" stroke="{line}" stroke-width="1.5"/>',
         f'<path d="M{x} {y + bar}H{x + w}" stroke="{line}" stroke-width="1.5"/>']
  svg += [f'<circle cx="{x + 24 + i * 22}" cy="{y + bar / 2}" r="7" fill="{c}"/>' for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840"))]
  if title:
    svg.append(f'<text x="{x + 100}" y="{y + bar / 2 + 6}" font-family="\'Pretendard\', \'Noto Sans KR\', sans-serif" '
               f'font-size="17" font-weight="600" fill="{text}">{escape(title)}</text>')
  svg.append("</g>")
  return "\n".join(svg), {"window": [x, y, w, h], "content": [x + 28, y + bar + 24, w - 56, h - bar - 48]}


def selftest():
  code = "def f(a):\n    # 메모\n    return a + 1\n"
  svg, data = build(code, "python", 100, 200, 20, 1.5, 10, 1.0, True, "light", ["return", "a"])
  lines = data["lines"]
  assert [l["n"] for l in lines] == [1, 2, 3]
  assert lines[1]["x"] == 100 + 4 * 10, "들여쓰기 4칸은 x로 옮기고 타이핑에서 뺀다"
  assert lines[1]["width"] == (2 + 2 * 2) * 10, "'# 메모' = 반각 2칸 + 전각 2글자"
  assert lines[0]["t0"] == 1.0 and lines[0]["t1"] == 1.9 and lines[1]["t0"] == round(1.9 + LINE_PAUSE, 2)
  assert lines[2]["baseline"] - lines[1]["baseline"] == 30
  box = next(m for m in data["marks"] if m["text"] == "return")
  assert box["x"] == 140 and box["width"] == 60 and box["line"] == 3
  assert ">    " not in svg and "> " not in svg.replace("> <", ""), "들여쓰기 공백은 글자로 남지 않고 x로만 옮긴다"
  assert svg.count("data-write") == 3 and svg.count("<tspan") >= 5 and "&lt;" not in svg
  assert data["end"] == lines[2]["t1"]
  svg, box = frame(100, 100, 600, 400, "a.py", "light")
  assert box["content"] == [128, 168, 544, 308] and svg.count("<circle") == 3 and "filter" not in svg
  svg, box = frame(100, 100, 400, 200, "", "light", card=True)
  assert box["content"] == [124, 124, 352, 152] and "<circle" not in svg
  print("selftest ok")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("code", nargs="?")
  parser.add_argument("--lang", default="text")
  parser.add_argument("--x", type=float, default=200, help="코드 첫 글자 x(들여쓰기 0 기준)")
  parser.add_argument("--y", type=float, default=300, help="첫 줄 baseline y")
  parser.add_argument("--size", type=float, default=26)
  parser.add_argument("--line-height", type=float, default=1.6)
  parser.add_argument("--cps", type=float, default=0, help="초당 타이핑 글자 수. 0이면 처음부터 다 보임")
  parser.add_argument("--start", type=float, default=0, help="첫 줄 타이핑 시작 초")
  parser.add_argument("--gutter", action="store_true", help="왼쪽에 줄 번호")
  parser.add_argument("--theme", choices=THEMES, default="light")
  parser.add_argument("--frame", help="창 틀만 만든다: x,y,w,h")
  parser.add_argument("--title", default="", help="--frame 제목줄 글자(파일명)")
  parser.add_argument("--card", action="store_true", help="--frame을 제목줄·신호등 없는 정보 카드 틀로")
  parser.add_argument("--mark", action="append", default=[], help="상자 좌표를 낼 글자(여러 번 가능)")
  parser.add_argument("--svg")
  parser.add_argument("--json")
  parser.add_argument("--selftest", action="store_true")
  args = parser.parse_args()
  if args.selftest:
    selftest()
    sys.exit()
  if args.frame and args.svg and args.json:
    svg, data = frame(*(float(v) for v in args.frame.split(",")), args.title, args.theme, args.card)
    Path(args.svg).write_text(svg + "\n")
    Path(args.json).write_text(json.dumps(data) + "\n")
    print(f"content {data['content']} -> {args.svg}")
    sys.exit()
  if not args.code or not args.svg or not args.json:
    parser.error("코드 파일, --svg, --json이 필요함")
  svg, data = build(Path(args.code).read_text(), args.lang, args.x, args.y, args.size, args.line_height,
                    args.cps, args.start, args.gutter, args.theme, args.mark)
  Path(args.svg).write_text(svg + "\n")
  Path(args.json).write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
  print(f"{len(data['lines'])} lines, typing ends at {data['end']} -> {args.svg}, {args.json}")
