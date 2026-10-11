# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py", "pillow"]
# ///
"""컷 SVG 여러 장을 doodle 만화로 묶는다. 출력은 형식(format)에 따라 둘 중 하나다.

  page       모든 컷을 격자로 놓은 한 장. 컷 viewBox 1920×1080          → out.svg, out.png
  instagram  컷마다 1장, 1080×1350(4:5). 컷 viewBox 1080×1350            → out_01.svg/png …
  youtube    컷마다 1장, 1080×1080(1:1, 커뮤니티 게시물). 컷 viewBox 1080×1080 → out_01.svg/png …

컷 테두리와 왼쪽 위 읽는 순서 번호는 이 스크립트가 그리고, 모델은 컷 그림만 그린다.

  uv run compose_comic.py comic.json out/comic
  uv run compose_comic.py --selftest
"""
import argparse
import copy
import json
import random
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import resvg_py
from PIL import Image

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

LAYOUTS = {2: (1, 2), 4: (2, 2), 6: (3, 2)}  # 컷 수: (행, 열). 읽는 순서는 왼쪽→오른쪽, 위→아래
PANEL_W, PANEL_H = 960, 540  # page: 1920×1080 컷을 절반으로 줄여 넣는다
GUTTER, MARGIN = 36, 48
SINGLE = {  # 컷마다 1장: 캔버스 크기, 컷 viewBox, 컷이 들어갈 안쪽 사각형(x, y, w, h)
  "instagram": {"canvas": (1080, 1350), "viewbox": (1080, 1350), "inner": (40, 50, 1000, 1250)},
  "youtube": {"canvas": (1080, 1080), "viewbox": (1080, 1080), "inner": (40, 40, 1000, 1000)},
}
PAPER, INK, WHITE = "#FEFEFE", "#000000", "#FFFFFF"
FONT = "'Gaegu', 'Nanum Pen Script', sans-serif"
BADGE_INSET, BADGE_R = 22, 30


def page_size(count):
  rows, cols = LAYOUTS[count]
  return MARGIN * 2 + cols * PANEL_W + (cols - 1) * GUTTER, MARGIN * 2 + rows * PANEL_H + (rows - 1) * GUTTER


def panel_origin(index, count):
  cols = LAYOUTS[count][1]
  row, col = divmod(index, cols)
  return MARGIN + col * (PANEL_W + GUTTER), MARGIN + row * (PANEL_H + GUTTER)


def wobbly_frame(x, y, seed, w=PANEL_W, h=PANEL_H):
  """손으로 그은 컷 테두리. 모서리를 2~4px 어긋나게 해 자로 그은 직사각형을 피한다."""
  rng = random.Random(seed)
  j = lambda: rng.uniform(-3, 3)
  corners = [(x + j(), y + j()), (x + w + j(), y + j()), (x + w + j(), y + h + j()), (x + j(), y + h + j())]
  d = f"M{corners[0][0]:.1f} {corners[0][1]:.1f} " + " ".join(f"L{cx:.1f} {cy:.1f}" for cx, cy in corners[1:]) + " Z"
  return ET.Element(f"{{{SVG_NS}}}path", {"d": d, "fill": "none", "stroke": INK, "stroke-width": "6", "stroke-linejoin": "round"})


def badge(x, y, number):
  cx, cy = x + BADGE_INSET + BADGE_R, y + BADGE_INSET + BADGE_R
  g = ET.Element(f"{{{SVG_NS}}}g")
  ET.SubElement(g, f"{{{SVG_NS}}}circle", {"cx": str(cx), "cy": str(cy), "r": str(BADGE_R), "fill": WHITE, "stroke": INK, "stroke-width": "5"})
  text = ET.SubElement(g, f"{{{SVG_NS}}}text", {"x": str(cx), "y": str(cy + 14), "text-anchor": "middle", "font-family": FONT, "font-size": "42", "font-weight": "700", "fill": INK})
  text.text = str(number)
  return g


def load_panel(path, viewbox):
  panel = ET.parse(path).getroot()
  if panel.get("viewBox", "").split() != ["0", "0", str(viewbox[0]), str(viewbox[1])]:
    raise ValueError(f"{path.name}: viewBox는 0 0 {viewbox[0]} {viewbox[1]}이어야 함")
  return panel


def nested(parent, panel, rect, viewbox):
  x, y, w, h = rect
  el = ET.SubElement(parent, f"{{{SVG_NS}}}svg", {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "viewBox": f"0 0 {viewbox[0]} {viewbox[1]}"})
  el.extend(copy.deepcopy(list(panel)))


def page_root(width, height):
  root = ET.Element(f"{{{SVG_NS}}}svg", {"viewBox": f"0 0 {width} {height}"})
  ET.SubElement(root, f"{{{SVG_NS}}}rect", {"width": str(width), "height": str(height), "fill": PAPER})
  return root


def write(root, stem, size, font_dirs):
  svg = ET.tostring(root, encoding="unicode")
  stem.with_suffix(".svg").write_text(svg)
  png = resvg_py.svg_to_bytes(svg_string=svg, width=size[0], height=size[1], font_dirs=font_dirs or None)
  stem.with_suffix(".png").write_bytes(bytes(png))


def compose(spec_path, out_stem):
  """만든 파일의 (폭, 높이)와 PNG 경로 목록을 돌려준다."""
  spec_path = Path(spec_path)
  spec = json.loads(spec_path.read_text())
  panels, fmt = spec["panels"], spec.get("format", "page")
  if len(panels) not in LAYOUTS:
    raise ValueError(f"컷 수는 {sorted(LAYOUTS)} 중 하나여야 함: {len(panels)}")
  if fmt != "page" and fmt not in SINGLE:
    raise ValueError(f"format은 page, {', '.join(SINGLE)} 중 하나여야 함: {fmt}")
  font_dirs = [str(spec_path.parent / Path(d).expanduser()) for d in spec.get("font_dirs", [])]
  out_stem = Path(out_stem)
  out_stem.parent.mkdir(parents=True, exist_ok=True)
  if fmt == "page":
    size = page_size(len(panels))
    root = page_root(*size)
    for index, name in enumerate(panels):
      x, y = panel_origin(index, len(panels))
      nested(root, load_panel(spec_path.parent / name, (1920, 1080)), (x, y, PANEL_W, PANEL_H), (1920, 1080))
      root.append(wobbly_frame(x, y, seed=index))
      root.append(badge(x, y, index + 1))
    write(root, out_stem, size, font_dirs)
    return size, [out_stem.with_suffix(".png")]
  conf = SINGLE[fmt]
  outputs = []
  for index, name in enumerate(panels):
    root = page_root(*conf["canvas"])
    x, y, w, h = conf["inner"]
    nested(root, load_panel(spec_path.parent / name, conf["viewbox"]), conf["inner"], conf["viewbox"])
    root.append(wobbly_frame(x, y, seed=index, w=w, h=h))
    root.append(badge(x, y, index + 1))
    stem = out_stem.with_name(f"{out_stem.name}_{index + 1:02d}")
    write(root, stem, conf["canvas"], font_dirs)
    outputs.append(stem.with_suffix(".png"))
  return conf["canvas"], outputs


def selftest():
  """컷 수별 페이지 크기, 읽는 순서 번호 위치, 1장씩 출력, 잘못된 컷 수·viewBox 거부를 확인한다."""
  assert page_size(2) == (2052, 636) and page_size(4) == (2052, 1212) and page_size(6) == (2052, 1788)
  assert panel_origin(1, 4)[1] == panel_origin(0, 4)[1], "2번은 1번 오른쪽"
  assert panel_origin(2, 4)[0] == panel_origin(0, 4)[0], "3번은 1번 아래"
  with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    (tmp / "p.svg").write_text(f'<svg xmlns="{SVG_NS}" viewBox="0 0 1920 1080"><circle cx="960" cy="540" r="200" fill="#000"/></svg>')
    (tmp / "comic.json").write_text(json.dumps({"panels": ["p.svg"] * 4}))
    assert compose(tmp / "comic.json", tmp / "page")[0] == (2052, 1212)
    image = Image.open(tmp / "page.png").convert("L")
    assert image.size == (2052, 1212)
    for index in range(4):
      x, y = panel_origin(index, 4)
      cx, cy = x + PANEL_W // 2, y + PANEL_H // 2
      assert image.getpixel((cx, cy)) < 50, f"{index + 1}번 컷 그림이 제자리에 있어야 함"
      bx, by = x + BADGE_INSET + BADGE_R, y + BADGE_INSET
      assert image.getpixel((bx, by)) < 128, f"{index + 1}번 번호 원이 왼쪽 위에 있어야 함"
    (tmp / "ig.svg").write_text(f'<svg xmlns="{SVG_NS}" viewBox="0 0 1080 1350"><circle cx="540" cy="675" r="200" fill="#000"/></svg>')
    (tmp / "ig.json").write_text(json.dumps({"format": "instagram", "panels": ["ig.svg"] * 2}))
    size, outputs = compose(tmp / "ig.json", tmp / "ig")
    assert size == (1080, 1350) and [o.name for o in outputs] == ["ig_01.png", "ig_02.png"], "컷마다 순서 번호 붙은 1장"
    single = Image.open(outputs[1]).convert("L")
    assert single.size == (1080, 1350) and single.getpixel((540, 675)) < 50
    assert single.getpixel((40 + BADGE_INSET + BADGE_R, 50 + BADGE_INSET)) < 128, "1장에도 왼쪽 위 번호"
    (tmp / "yt.json").write_text(json.dumps({"format": "youtube", "panels": ["ig.svg"] * 2}))
    try:
      compose(tmp / "yt.json", tmp / "yt")
      raise AssertionError("youtube 형식에 4:5 컷은 거부해야 함")
    except ValueError:
      pass
    (tmp / "bad.json").write_text(json.dumps({"panels": ["p.svg"] * 3}))
    try:
      compose(tmp / "bad.json", tmp / "bad")
      raise AssertionError("3컷은 거부해야 함")
    except ValueError:
      pass
  print("selftest ok")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("spec", nargs="?")
  parser.add_argument("out", nargs="?", help="확장자 없는 출력 경로. .svg와 .png가 생긴다")
  parser.add_argument("--selftest", action="store_true")
  args = parser.parse_args()
  if args.selftest:
    selftest()
    sys.exit()
  if not args.spec or not args.out:
    parser.error("comic.json과 출력 경로가 필요함")
  (w, h), outputs = compose(args.spec, args.out)
  print(f"{w}x{h} -> " + ", ".join(str(o) for o in outputs))
