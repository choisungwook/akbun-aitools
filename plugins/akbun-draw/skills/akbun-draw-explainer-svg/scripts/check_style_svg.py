# /// script
# requires-python = ">=3.12"
# ///
"""akbun-draw-explainer-svg가 만든 SVG를 styles/<style>.json 토큰으로 숫자 검수한다.

사용법:
  uv run --python 3.12 check_style_svg.py --style tech-minimal [--caption-left 30] out.svg
  uv run --python 3.12 check_style_svg.py --style path/to/custom.json out.svg
  uv run --python 3.12 check_style_svg.py --selftest

검사 항목(토큰 키): viewBox(canvas.viewBox), 금지 요소(checks.forbidElements), 팔레트 밖 색(colors·effects의 hex 전부),
글꼴(typography.fonts 첫 글꼴), stroke-width 범위(checks.strokeWidthRange), 자막 영역 비움과 여유(canvas.captionMarginPx),
가장자리 여백(canvas.edgeMarginPx), 여백 비율(checks.minNegativeSpacePct), 내용 중심이 그릴 영역 중심에서 ±canvas.centerTolerancePx 안인지.
`class="bg"` 요소(배경·장식)는 자막·가장자리·여백 계산에서 뺀다.
못 보는 것: 요소 사이 간격, 강조 채움 면적 비율, 발광 개수, 글자 길이, 그리는 순서. SKILL.md의 눈 검수 항목이다.
글자 폭은 영어·숫자 0.6em, 한글 등 넓은 글자 1.0em으로 추정한다.
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

CANVAS = (1920, 1080)
GRID = 8
HEX = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
NUM = re.compile(r"-?\d+(?:\.\d+)?")
STYLES_DIR = Path(__file__).resolve().parent.parent / "styles"


def load_style(name_or_path):
  path = Path(name_or_path)
  if not path.suffix == ".json":
    path = STYLES_DIR / f"{name_or_path}.json"
  return json.loads(path.read_text(encoding="utf-8"))


def hex_values(obj, out=None):
  if out is None:
    out = set()
  if isinstance(obj, dict):
    for value in obj.values():
      hex_values(value, out)
  elif isinstance(obj, list):
    for value in obj:
      hex_values(value, out)
  elif isinstance(obj, str):
    out.update(c.upper() for c in HEX.findall(obj))
  return out


def allowed_fonts(style):
  fonts = set()
  for family in style.get("typography", {}).get("fonts", {}).values():
    fonts.add(family.split(",")[0].strip().strip("'\""))
  return fonts


def local(tag):
  return tag.split("}", 1)[-1]


def translate_of(el):
  tf = el.get("transform", "")
  match = re.search(r"translate\(\s*(-?[\d.]+)[ ,]*(-?[\d.]+)?\s*\)", tf)
  complex_tf = any(k in tf for k in ("matrix", "scale", "rotate", "skew"))
  if not match:
    return 0.0, 0.0, complex_tf
  return float(match[1]), float(match[2] or 0), complex_tf


def text_width(el, inherited):
  size = float(NUM.search(el.get("font-size") or inherited.get("font-size") or "16")[0])
  text = "".join(el.itertext())
  wide = sum(1 for ch in text if ord(ch) > 0x2E7F)
  return (wide * 1.0 + (len(text) - wide) * 0.6) * size, size


def element_box(el, skipped, inherited):
  tag = local(el.tag)
  f = lambda k, d="0": float(NUM.search(el.get(k, d) or d)[0])
  if tag == "rect":
    return f("x"), f("y"), f("x") + f("width"), f("y") + f("height")
  if tag == "circle":
    return f("cx") - f("r"), f("cy") - f("r"), f("cx") + f("r"), f("cy") + f("r")
  if tag == "ellipse":
    return f("cx") - f("rx"), f("cy") - f("ry"), f("cx") + f("rx"), f("cy") + f("ry")
  if tag == "line":
    xs, ys = (f("x1"), f("x2")), (f("y1"), f("y2"))
    return min(xs), min(ys), max(xs), max(ys)
  if tag in ("polygon", "polyline"):
    nums = [float(n) for n in NUM.findall(el.get("points", ""))]
    xs, ys = nums[0::2], nums[1::2]
    return (min(xs), min(ys), max(xs), max(ys)) if xs and ys else None
  if tag == "path":
    d = el.get("d", "")
    if re.search(r"[a-zA-Z]", re.sub(r"[MLQCTSZz]|e[-+]?\d", "", d)):
      skipped.append("path")
      return None
    nums = [float(n) for n in NUM.findall(d)]
    xs, ys = nums[0::2], nums[1::2]
    return (min(xs), min(ys), max(xs), max(ys)) if xs and ys else None
  if tag == "use":
    if el.get("width") and el.get("height"):
      return f("x"), f("y"), f("x") + f("width"), f("y") + f("height")
    skipped.append("use")
    return None
  if tag == "text":
    width, size = text_width(el, inherited)
    x, y = f("x"), f("y")
    anchor = el.get("text-anchor") or inherited.get("text-anchor") or "start"
    left = x - width if anchor == "end" else x - width / 2 if anchor == "middle" else x
    return left, y - size, left + width, y + size * 0.25
  return None


def collect_boxes(el, dx=0.0, dy=0.0, skipped=None, inherited=None):
  if skipped is None:
    skipped = []
  inherited = {**(inherited or {}), **{k: el.get(k) for k in ("text-anchor", "font-size") if el.get(k)}}
  boxes = []
  if "bg" in (el.get("class") or "").split():
    return boxes
  tag = local(el.tag)
  if tag in ("defs", "marker", "clipPath", "mask", "pattern", "filter", "linearGradient", "radialGradient", "style", "title", "desc", "symbol"):
    return boxes
  tx, ty, complex_tf = translate_of(el)
  if complex_tf:
    skipped.append(tag)
    return boxes
  dx, dy = dx + tx, dy + ty
  box = element_box(el, skipped, inherited)
  if box is not None:
    boxes.append((box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy))
  if tag != "text":
    for child in el:
      boxes.extend(collect_boxes(child, dx, dy, skipped, inherited))
  return boxes


def coverage(boxes):
  cols, rows = CANVAS[0] // GRID, CANVAS[1] // GRID
  filled = bytearray(cols * rows)
  for x0, y0, x1, y1 in boxes:
    c0, c1 = max(0, int(x0 // GRID)), min(cols, int(-(-x1 // GRID)))
    r0, r1 = max(0, int(y0 // GRID)), min(rows, int(-(-y1 // GRID)))
    for r in range(r0, r1):
      start = r * cols
      filled[start + c0:start + c1] = b"\x01" * max(0, c1 - c0)
  return sum(filled) / (cols * rows)


def strip_references(svg_text):
  svg_text = re.sub(r"url\(#[^)]*\)", "url()", svg_text)
  svg_text = re.sub(r"href=\"#[^\"]*\"", 'href=""', svg_text)
  return re.sub(r"\bid=\"[^\"]*\"", 'id=""', svg_text)


def check(svg_text, style, caption_left=0):
  checks = style.get("checks", {})
  canvas = style.get("canvas", {})
  errors = []
  try:
    root = ET.fromstring(svg_text)
  except ET.ParseError as error:
    return [f"XML 파싱 실패: {error}"], {}
  if local(root.tag) != "svg":
    return ["루트가 <svg>가 아님"], {}
  expected = canvas.get("viewBox", "0 0 1920 1080").split()
  if root.get("viewBox", "").split() != expected:
    errors.append(f"viewBox가 {' '.join(expected)!r}이 아님: {root.get('viewBox')!r}")
  tags = {local(el.tag) for el in root.iter()}
  for tag in sorted(set(checks.get("forbidElements", [])) & tags):
    errors.append(f"금지 요소 <{tag}> 사용")
  if re.search(r"href=\"(?!#)", svg_text):
    errors.append("외부 href 사용")
  palette = hex_values(style)
  used = set()
  for color in HEX.findall(strip_references(svg_text)):
    color = color.upper()
    if len(color) == 4:
      color = "#" + "".join(ch * 2 for ch in color[1:])
    used.add(color)
  for color in sorted(used - palette):
    errors.append(f"팔레트 밖 색 {color}")
  fonts = allowed_fonts(style)
  for family in re.findall(r"font-family=\"([^\"]+)\"", svg_text) + re.findall(r"font-family:\s*([^;\"]+)", svg_text):
    first = family.split(",")[0].strip().strip("'\"")
    if first not in fonts:
      errors.append(f"허용 밖 글꼴 {first!r} (허용: {', '.join(sorted(fonts))})")
  width_range = checks.get("strokeWidthRange")
  if width_range:
    low, high = width_range
    for value in re.findall(r"stroke-width=\"([\d.]+)\"", svg_text):
      if not low <= float(value) <= high:
        errors.append(f"stroke-width {value}가 {low}~{high} 밖")
  skipped = []
  boxes = collect_boxes(root, skipped=skipped)
  boxes = [b for b in boxes if not (b[0] <= 0 and b[1] <= 0 and b[2] >= CANVAS[0] and b[3] >= CANVAS[1])]
  edge = canvas.get("edgeMarginPx", 0)
  if edge:
    outside = [b for b in boxes if b[0] < edge or b[1] < edge or b[2] > CANVAS[0] - edge or b[3] > CANVAS[1] - edge]
    if outside:
      errors.append(f"가장자리 {edge}px 안에 요소 {len(outside)}개")
  if caption_left:
    limit = CANVAS[0] * caption_left / 100
    margin = canvas.get("captionMarginPx", 0)
    intruding = [b for b in boxes if b[0] < limit]
    if intruding:
      errors.append(f"자막 영역(x<{limit:.0f}) 안에 요소 {len(intruding)}개")
    elif margin:
      close = [b for b in boxes if b[0] < limit + margin]
      if close:
        errors.append(f"자막 영역 경계에서 {margin}px 안에 요소 {len(close)}개")
  tolerance = canvas.get("centerTolerancePx", 40)
  offset = (0.0, 0.0)
  if boxes:
    x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    x1, y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    left = CANVAS[0] * caption_left / 100 if caption_left else 0
    offset = (round((x0 + x1) / 2 - (left + CANVAS[0]) / 2, 1), round((y0 + y1) / 2 - CANVAS[1] / 2, 1))
    if abs(offset[0]) > tolerance or abs(offset[1]) > tolerance:
      errors.append(f"내용의 bounding box 중심이 그릴 영역 중심에서 x {offset[0]:+}px, y {offset[1]:+}px 벗어남(허용 ±{tolerance}px)")
  space = round((1 - coverage(boxes)) * 100, 1)
  minimum = checks.get("minNegativeSpacePct", 0)
  if space < minimum:
    errors.append(f"여백 {space}%가 최소 {minimum}% 미만")
  info = {"negative_space_pct": space, "colors": sorted(used), "skipped": skipped, "center_offset": offset}
  return errors, info


def selftest():
  style = load_style("tech-minimal")
  body = (
    '<rect x="760" y="440" width="300" height="200" rx="12" fill="#FFFFFF" stroke="#212529" stroke-width="2"/>'
    '<line x1="1060" y1="540" x2="1160" y2="540" stroke="#212529" stroke-width="2" marker-end="url(#add)"/>'
    '<text x="910" y="540" font-family="Inter, sans-serif" font-size="28" text-anchor="middle" fill="#212529">Pod</text>'
  )
  head = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080">'
    '<defs><marker id="add" markerWidth="12" markerHeight="12"><path d="M0,0 L12,6 L0,12 Z" fill="#212529"/></marker></defs>'
    '<rect class="bg" width="1920" height="1080" fill="#FFFFFF"/>'
  )
  ok_min = head + body + "</svg>"
  errors, info = check(ok_min, style)
  assert errors == [], errors
  assert info["negative_space_pct"] > 90 and info["center_offset"] == (0.0, 0.0), info
  off = head + '<g transform="translate(-120 90)">' + body + "</g></svg>"
  errors, info = check(off, style)
  assert any("중심" in e for e in errors) and info["center_offset"] == (-120.0, 90.0), (errors, info)
  captioned = head + '<g transform="translate(288 0)">' + body + "</g></svg>"
  errors, _ = check(captioned, style, caption_left=30)
  assert errors == [], errors
  errors, _ = check(head + '<g transform="translate(-200 0)">' + body + "</g></svg>", style, caption_left=30)
  assert any("자막 영역(x<576)" in e for e in errors), errors
  errors, _ = check(head + '<g transform="translate(-160 0)">' + body + "</g></svg>", style, caption_left=30)
  assert any("경계에서 40px" in e for e in errors), errors
  bad = ok_min.replace('stroke-width="2"', 'stroke-width="4"').replace('fill="#212529">', 'fill="#FF0000">')
  bad = bad.replace("</svg>", '<filter id="f"/><text x="900" y="1050" font-family="Comic Sans" font-size="20">x</text></svg>')
  errors, _ = check(bad, style)
  joined = "\n".join(errors)
  for needle in ("금지 요소 <filter>", "팔레트 밖 색 #FF0000", "허용 밖 글꼴 'Comic Sans'", "stroke-width 4", "가장자리 80px"):
    assert needle in joined, (needle, joined)
  big = head + '<rect x="260" y="70" width="1400" height="940" fill="#FFFFFF" stroke="#212529" stroke-width="2"/></svg>'
  errors, info = check(big, style)
  assert any("여백" in e for e in errors), (errors, info)
  errors, _ = check(ok_min.replace('viewBox="0 0 1920 1080"', 'viewBox="0 0 1080 1920"'), style)
  assert any("viewBox" in e for e in errors), errors
  inherited = head + '<g text-anchor="end" font-size="28"><text x="1110" y="540" font-family="Inter, sans-serif" fill="#212529">Pod</text></g>' + body + "</svg>"
  errors, _ = check(inherited, style)
  assert errors == [], errors
  korean = head + '<text x="1800" y="540" font-family="Inter, sans-serif" font-size="28" fill="#212529">노드하나</text>' + body + "</svg>"
  errors, _ = check(korean, style)
  assert any("가장자리" in e for e in errors), errors
  paper = load_style("paper-cutout")
  svg = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080"><defs>'
    '<filter id="paper"><feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#3D405B" flood-opacity="0.18"/></filter></defs>'
    '<rect class="bg" width="1920" height="1080" fill="#F4EFE6"/>'
    '<g transform="translate(960 540)"><circle cx="0" cy="0" r="100" fill="#E07A5F" filter="url(#paper)"/></g>'
    '<path d="M940 540 Q960 510 980 540" fill="none"/><path d="M940 560 h 40" fill="none"/></svg>'
  )
  errors, info = check(svg, paper)
  assert errors == [], errors
  assert info["skipped"] == ["path"], info
  for name in sorted(p.stem for p in STYLES_DIR.glob("*.json")):
    data = load_style(name)
    assert data["canvas"]["viewBox"] == "0 0 1920 1080", name
    assert "checks" in data and "minNegativeSpacePct" in data["checks"], name
    assert allowed_fonts(data), name
  print("selftest ok")


def main():
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("svg", nargs="?", type=Path)
  parser.add_argument("--style", help="styles/ 아래 토큰 이름(예: tech-minimal) 또는 .json 경로")
  parser.add_argument("--caption-left", type=float, default=0, help="왼쪽에서 비워 둘 자막 영역 비율(%%)")
  parser.add_argument("--selftest", action="store_true")
  args = parser.parse_args()
  if args.selftest:
    selftest()
    return 0
  if not args.svg or not args.style:
    parser.error("svg 경로와 --style이 필요함")
  style = load_style(args.style)
  errors, info = check(args.svg.read_text(encoding="utf-8"), style, args.caption_left)
  print(f"[{style.get('id')}] 여백 {info.get('negative_space_pct')}%, 중심 오차 x {info.get('center_offset', (0, 0))[0]:+}px y {info.get('center_offset', (0, 0))[1]:+}px, 색 {len(info.get('colors', []))}종: {', '.join(info.get('colors', []))}")
  if info.get("skipped"):
    print(f"bbox 계산에서 건너뜀 {len(info['skipped'])}개 요소({', '.join(sorted(set(info['skipped'])))}): 상대 좌표·H/V/A 명령 path, 크기 없는 use, matrix/scale/rotate transform")
  if errors:
    print("\n".join(f"- {e}" for e in errors))
    return 1
  print("ok")
  return 0


if __name__ == "__main__":
  sys.exit(main())
