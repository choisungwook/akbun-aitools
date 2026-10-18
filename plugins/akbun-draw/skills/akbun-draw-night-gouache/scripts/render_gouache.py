# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py", "numpy", "pillow"]
# ///
"""night-gouache 장면 SVG를 PNG로 렌더한다.

모델은 장면 그림만 SVG로 쓰고, 스타일에서 숫자로 고정된 부분은 이 스크립트가 맡는다.

  - 배경: 루트 data-bg="night"(기본, 어두운 비네트+입자) 또는 "paper"(구김 종이)
  - 질감 필터·광·그늘 그라데이션 defs 주입: url(#paint) url(#brush) url(#pencil) url(#glow) url(#halo-*) url(#spot) url(#shade)
  - 자막 미리보기: 루트 data-subtitle="..."
  - 키워드 태그: <text class="tag" x=".." y="..">라벨</text> (x,y = 태그 상자 왼쪽 위)
  - 레이어: 루트 바로 아래 <g data-layer="이름"> 마다 투명 PNG 1장 + layers.json

  uv run render_gouache.py scene.svg still.png                   # 배경+자막 포함 확인용 스틸
  uv run render_gouache.py scene.svg still.png --layers out/dir  # + 레이어별 투명 PNG, background.png, layers.json
  uv run render_gouache.py --selftest
"""
import argparse
import copy
import html
import io
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import resvg_py
from PIL import Image

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
W, H = 1920, 1080
FONT = "Pretendard"

DEFS = f"""<defs xmlns="{NS}">
  <filter id="paint" x="-8%" y="-8%" width="116%" height="116%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.022" numOctaves="2" seed="3" result="warp"/>
    <feDisplacementMap in="SourceGraphic" in2="warp" scale="4" xChannelSelector="R" yChannelSelector="G" result="rough"/>
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" seed="11" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  1.6 0 0 0 -0.78" result="lightN"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 1.6 0 0 -0.80" result="darkN"/>
    <feComposite in="lightN" in2="rough" operator="in" result="lightS"/>
    <feComposite in="darkN" in2="rough" operator="in" result="darkS"/>
    <feMerge><feMergeNode in="rough"/><feMergeNode in="darkS"/><feMergeNode in="lightS"/></feMerge>
  </filter>
  <filter id="brush" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" seed="13" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 1.6 0 0 -0.75" result="darkN"/>
    <feComposite in="darkN" in2="SourceGraphic" operator="in" result="darkS"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="darkS"/></feMerge>
  </filter>
  <filter id="pencil" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.04 0.35" numOctaves="2" seed="5" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0.9 0 -0.42" result="hatch"/>
    <feComposite in="hatch" in2="SourceGraphic" operator="in" result="h"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="h"/></feMerge>
  </filter>
  <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="14" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <radialGradient id="halo-red"><stop offset="0.45" stop-color="#E8231B" stop-opacity="0.85"/><stop offset="1" stop-color="#E8231B" stop-opacity="0"/></radialGradient>
  <radialGradient id="halo-yellow"><stop offset="0.45" stop-color="#F5C518" stop-opacity="0.8"/><stop offset="1" stop-color="#F5C518" stop-opacity="0"/></radialGradient>
  <radialGradient id="halo-mint"><stop offset="0.45" stop-color="#17F0D8" stop-opacity="0.6"/><stop offset="1" stop-color="#17F0D8" stop-opacity="0"/></radialGradient>
  <radialGradient id="spot"><stop offset="0" stop-color="#000000" stop-opacity="0.7"/><stop offset="0.7" stop-color="#000000" stop-opacity="0.45"/><stop offset="1" stop-color="#000000" stop-opacity="0"/></radialGradient>
  <radialGradient id="shade" cx="0.38" cy="0.35" r="0.75"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.35"/><stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0"/><stop offset="1" stop-color="#000000" stop-opacity="0.45"/></radialGradient>
  <filter id="tag-shadow"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.6"/></filter>
</defs>"""

BG = {
  "night": f"""<svg xmlns="{NS}" viewBox="0 0 {W} {H}">
  <defs>
    <radialGradient id="v" cx="0.5" cy="0.45" r="0.78"><stop offset="0" stop-color="#1A1C21"/><stop offset="0.55" stop-color="#0E1014"/><stop offset="1" stop-color="#05070A"/></radialGradient>
    <filter id="g" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="2"/>
      <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0.9 0 0 0 -0.38"/></filter>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#v)"/><rect width="{W}" height="{H}" filter="url(#g)" opacity="0.10"/>
</svg>""",
  "paper": f"""<svg xmlns="{NS}" viewBox="0 0 {W} {H}">
  <defs><filter id="c" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="turbulence" baseFrequency="0.004 0.006" numOctaves="5" seed="8" result="n"/>
    <feDiffuseLighting in="n" surfaceScale="4" lighting-color="#ECECEA" diffuseConstant="1.1"><feDistantLight azimuth="235" elevation="58"/></feDiffuseLighting>
  </filter></defs>
  <rect width="{W}" height="{H}" filter="url(#c)"/>
</svg>""",
}


def text_width(s, size):
  return sum(size * (0.98 if ord(c) > 0x2E80 else 0.3 if c == " " else 0.58) for c in s)


def tag_group(el):
  label, x, y = (el.text or "").strip(), float(el.get("x", 0)), float(el.get("y", 0))
  w = text_width(label, 26) + 36
  return ET.fromstring(f"""<g xmlns="{NS}" filter="url(#tag-shadow)">
  <rect x="{x}" y="{y}" width="{w:.0f}" height="46" fill="#0B0C0F" fill-opacity="0.82"/>
  <rect x="{x}" y="{y + 44}" width="{w:.0f}" height="2" fill="#E8C840"/>
  <rect x="{x - 4}" y="{y - 4}" width="8" height="8" fill="#E8C840"/>
  <text x="{x + 18}" y="{y + 32}" font-family="{FONT}" font-weight="700" font-size="26" fill="#FFFFFF">{html.escape(label)}</text>
</g>"""), {"text": label, "box": [x, y, x + w, y + 46]}


def subtitle_svg(text, bg):
  # 종이 배경에서는 흰 글자가 묻히므로 어두운 테두리와 그림자를 붙인다
  edge = 'stroke="#1A1C21" stroke-opacity="0.8" stroke-width="6" stroke-linejoin="round" paint-order="stroke" filter="url(#s)"' if bg == "paper" else ""
  return f"""<svg xmlns="{NS}" viewBox="0 0 {W} {H}"><defs><filter id="s"><feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000" flood-opacity="0.6"/></filter></defs>
  <text x="{W / 2}" y="950" text-anchor="middle" font-family="{FONT}" font-weight="500" font-size="42" fill="#FFFFFF" {edge}>{html.escape(text)}</text></svg>"""


def raster(svg):
  return Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, width=W, height=H)))).convert("RGBA")


def prepare(root):
  """defs를 넣고 태그를 상자로 바꾼다. 태그 목록을 돌려준다."""
  root.insert(0, ET.fromstring(DEFS))
  tags = []
  for parent in list(root.iter()):
    for i, el in enumerate(list(parent)):
      if el.tag == f"{{{NS}}}text" and "tag" in (el.get("class") or "").split():
        g, info = tag_group(el)
        parent.remove(el)
        parent.insert(i, g)
        info["layer"] = parent.get("data-layer", "")
        tags.append(info)
  return tags


def render(svg_path, still_path, layers_dir=None):
  root = ET.parse(svg_path).getroot()
  bg = root.get("data-bg", "night")
  subtitle = root.get("data-subtitle", "")
  if len(subtitle) > 24:
    print(f"warning: 자막이 공백 포함 {len(subtitle)}자다(24자 이하). 장면을 나누자고 제안한다", file=sys.stderr)
  root.set("viewBox", f"0 0 {W} {H}")
  for k in ("width", "height"):
    root.attrib.pop(k, None)
  tags = prepare(root)
  scene = raster(ET.tostring(root, encoding="unicode"))
  back = raster(BG[bg])
  still = Image.alpha_composite(back, scene)
  if subtitle:
    still = Image.alpha_composite(still, raster(subtitle_svg(subtitle, bg)))
  still.convert("RGB").save(still_path)
  if not layers_dir:
    return None
  out = Path(layers_dir)
  out.mkdir(parents=True, exist_ok=True)
  back.convert("RGB").save(out / "background.png")
  layers = []
  names = [el.get("data-layer") for el in root if el.get("data-layer")]
  loose = [el.tag.split("}")[1] for el in root if not el.get("data-layer") and el.tag.split("}")[1] not in ("defs", "title", "desc")]
  if loose:
    print(f"warning: data-layer 밖 요소 {loose}는 레이어 PNG에 들어가지 않는다", file=sys.stderr)
  for name in names:
    one = copy.deepcopy(root)
    for el in list(one):
      if el.get("data-layer") and el.get("data-layer") != name:
        one.remove(el)
      elif not el.get("data-layer") and el.tag.split("}")[1] not in ("defs",):
        one.remove(el)
    img = raster(ET.tostring(one, encoding="unicode"))
    alpha = np.asarray(img)[:, :, 3]
    ys, xs = np.nonzero(alpha > 8)
    if not len(xs):
      print(f"warning: 레이어 {name}이 비어 있다", file=sys.stderr)
      continue
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    file = f"{len(layers) + 1:02d}_{name}.png"
    img.save(out / file)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    layers.append({"name": name, "file": file, "bbox": [x0, y0, x1, y1], "pivot": [round(cx / W, 4), round(1 - cy / H, 4)]})
  meta = {"size": [W, H], "bg": bg, "subtitle": subtitle, "background": "background.png", "layers": layers, "tags": tags}
  (out / "layers.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
  return meta


def selftest():
  import tempfile
  with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "s.svg"
    p.write_text(f"""<svg xmlns="{NS}" viewBox="0 0 1920 1080" data-subtitle="테스트">
  <g data-layer="cell"><circle cx="600" cy="400" r="100" fill="#17F0D8" filter="url(#paint)"/></g>
  <g data-layer="label"><text class="tag" x="1200" y="200">키워드</text></g></svg>""")
    meta = render(p, Path(d) / "still.png", Path(d) / "layers")
    x0, y0, x1, y1 = meta["layers"][0]["bbox"]
    assert 480 <= x0 <= 510 and 690 <= x1 <= 720 and 280 <= y0 <= 310, meta["layers"][0]
    assert abs(meta["layers"][0]["pivot"][0] - 600 / W) < 0.01
    assert meta["tags"][0]["text"] == "키워드" and meta["tags"][0]["layer"] == "label"
    still = np.asarray(Image.open(Path(d) / "still.png"))
    assert still[540, 20].max() < 30 and still[400, 600, 1] > 150, (still[540, 20], still[400, 600])
  print("selftest ok")


if __name__ == "__main__":
  ap = argparse.ArgumentParser()
  ap.add_argument("svg", nargs="?")
  ap.add_argument("still", nargs="?")
  ap.add_argument("--layers")
  ap.add_argument("--selftest", action="store_true")
  a = ap.parse_args()
  if a.selftest:
    selftest()
  elif a.svg and a.still:
    render(Path(a.svg), Path(a.still), a.layers)
  else:
    ap.error("svg와 still 경로가 필요하다")
