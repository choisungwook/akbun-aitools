# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow==11.3.0"]
# ///
"""장면 spec(JSON)을 읽어 모션그래픽 장면을 ProRes 4444 알파 MOV로 렌더한다.

uv run -q --python 3.12 render_mg.py --spec scenes.json --fps 24 --out mg/out S01 S02
"""

import argparse
import json
import math
import random
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1080
SAFE_X = 96
CAPTION_TOP = 880

THEME = {
  "bg": "#F4EFE6",
  "stripe": "#EAE2D3",
  "night": "#14213D",
  "card": "#FFFFFF",
  "ink": "#1F1F1F",
  "sub": "#6B6B6B",
  "accent": "#FFC93C",
  "stamp": "#D64541",
  "shadow": "#00000040",
}

RISE_SEC, RISE_PX = 0.4, 40
FADE_SEC = 0.3
POP_SEC, POP_PEAK_SEC = 0.3, 0.18
OUT_SEC = 0.25
BAR_GROW_SEC, BAR_STAGGER_SEC = 0.8, 0.12
ARROW_DRAW_SEC = 0.4

DEFAULT_SFX = {"stamp": "stamp", "chapter": "whoosh", "bar": "rise"}
ABSOLUTE = {"box", "arrow"}
GROWING = {"bar", "arrow"}

FONT_NAMES = {
  "bold": ["GmarketSansTTFBold.ttf", "GmarketSansBold.otf", "GmarketSansBold.ttf"],
  "medium": ["GmarketSansTTFMedium.ttf", "GmarketSansMedium.otf", "GmarketSansMedium.ttf"],
}
FONT_DIRS = ["~/Library/Fonts", "/Library/Fonts", "~/.local/share/fonts", "~/.fonts", "/usr/share/fonts", "/usr/local/share/fonts"]

WARNINGS = []


def clamp(v, lo=0.0, hi=1.0):
  return max(lo, min(hi, v))


def ease_out(t):
  return 1 - (1 - clamp(t)) ** 3


def pop_scale(k):
  if k >= POP_SEC:
    return 1.0
  if k < POP_PEAK_SEC:
    return 0.6 + 0.46 * ease_out(k / POP_PEAK_SEC)
  return 1.06 - 0.06 * ease_out((k - POP_PEAK_SEC) / (POP_SEC - POP_PEAK_SEC))


def anim_state(el, t):
  at, out = el.get("at", 0.0), el.get("out")
  if t < at or (out is not None and t >= out):
    return None
  k = t - at
  alpha, dy, scale = 1.0, 0.0, 1.0
  anim = el.get("anim", "rise")
  if anim == "rise":
    p = ease_out(k / RISE_SEC)
    alpha, dy = p, RISE_PX * (1 - p)
  elif anim == "fade":
    alpha = ease_out(k / FADE_SEC)
  elif anim == "pop":
    scale, alpha = pop_scale(k), clamp(k / 0.1)
  if out is not None and out - t < OUT_SEC:
    alpha *= (out - t) / OUT_SEC
  return alpha, dy, scale


def parse_fps(text):
  known = {"23.976": Fraction(24000, 1001), "29.97": Fraction(30000, 1001), "59.94": Fraction(60000, 1001)}
  return known.get(text) or Fraction(text)


def frame_count(duration, fps):
  return round(Fraction(str(duration)) * fps)


def scene_events(scene, fps):
  events = []
  for i, el in enumerate(scene["elements"]):
    kind = el.get("sfx", DEFAULT_SFX.get(el["type"], "pop" if el.get("anim") == "pop" else None))
    if kind and kind != "none":
      events.append({"frame": round(Fraction(str(el.get("at", 0.0))) * fps), "kind": kind, "element": el.get("name", f"{el['type']}{i}")})
  return sorted(events, key=lambda e: e["frame"])


class Fonts:
  def __init__(self, bold=None, medium=None):
    self.paths = {"bold": bold, "medium": medium}
    self.cache = {}

  def get(self, weight, size):
    key = (weight, size)
    if key not in self.cache:
      path = self.paths[weight]
      self.cache[key] = ImageFont.truetype(str(path), size) if path else ImageFont.load_default(size)
    return self.cache[key]


def has_blank_space(path):
  return ImageFont.truetype(str(path), 40).getmask(" ").getbbox() is None


def find_font(weight):
  for base in FONT_DIRS:
    root = Path(base).expanduser()
    if not root.is_dir():
      continue
    for name in FONT_NAMES[weight]:
      hit = next(root.rglob(name), None)
      if hit:
        return hit
  return None


def color(theme, value):
  return theme.get(value, value)


def text_size(font, text):
  box = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=font)
  return box[2] - box[0], box[3] - box[1], box[1]


def check_width(el, text, font, limit):
  width = text_size(font, text)[0]
  if width > limit:
    WARNINGS.append(f"{el.get('name', el['type'])}: '{text}' 폭 {width}px > {limit}px")


def with_shadow(img, theme, radius=16, offset=8):
  pad = radius * 2
  out = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
  shadow = Image.new("RGBA", img.size, color(theme, "shadow"))
  shadow.putalpha(Image.eval(img.getchannel("A"), lambda a: a * 64 // 255))
  out.alpha_composite(shadow, (pad, pad + offset))
  out = out.filter(ImageFilter.GaussianBlur(radius))
  out.alpha_composite(img, (pad, pad))
  return out


def draw_card(el, k, ctx):
  theme, fonts = ctx["theme"], ctx["fonts"]
  w, h = el.get("w", 720), el.get("h", 360)
  img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
  d = ImageDraw.Draw(img)
  d.rounded_rectangle((0, 0, w - 1, h - 1), radius=28, fill=color(theme, el.get("fill", "card")))
  y = 40
  if el.get("title"):
    font = fonts.get("bold", el.get("title_size", 64))
    check_width(el, el["title"], font, w - 80)
    d.text((40, y), el["title"], font=font, fill=color(theme, "ink"))
    y += text_size(font, el["title"])[1] + 28
  font = fonts.get("medium", el.get("body_size", 40))
  for line in el.get("body", "").split("\n") if el.get("body") else []:
    check_width(el, line, font, w - 80)
    d.text((40, y), line, font=font, fill=color(theme, "sub"))
    y += text_size(font, line)[1] + 18
  if y > h:
    WARNINGS.append(f"{el.get('name', 'card')}: 글 높이 {y}px > 카드 {h}px")
  return with_shadow(img, theme)


def draw_chip(el, k, ctx):
  theme = ctx["theme"]
  font = ctx["fonts"].get("medium", el.get("size", 44))
  tw, th, top = text_size(font, el["text"])
  w, h = tw + 56, max(64, th + 28)
  img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
  d = ImageDraw.Draw(img)
  d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=color(theme, el.get("fill", "accent")))
  d.text((28, (h - th) // 2 - top), el["text"], font=font, fill=color(theme, el.get("ink", "ink")))
  return with_shadow(img, theme, radius=10, offset=4)


def draw_tile(el, k, ctx):
  theme, fonts = ctx["theme"], ctx["fonts"]
  s = el.get("size", 240)
  img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
  d = ImageDraw.Draw(img)
  d.rounded_rectangle((0, 0, s - 1, s - 1), radius=32, fill=color(theme, el.get("fill", "card")))
  d.rounded_rectangle((0, 0, s - 1, 16), radius=8, fill=color(theme, "accent"))
  big = fonts.get("bold", int(s * 0.42))
  small = fonts.get("medium", int(s * 0.15))
  for text, font, cy, fill in ((el["value"], big, s * 0.45, "ink"), (el.get("label", ""), small, s * 0.8, "sub")):
    check_width(el, text, font, s - 24)
    tw, th, top = text_size(font, text)
    d.text(((s - tw) / 2, cy - th / 2 - top), text, font=font, fill=color(theme, fill))
  return with_shadow(img, theme)


def draw_stamp(el, k, ctx):
  theme = ctx["theme"]
  s = el.get("size", 260)
  ink = color(theme, el.get("color", "stamp"))
  img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
  d = ImageDraw.Draw(img)
  d.ellipse((4, 4, s - 5, s - 5), outline=ink, width=8)
  d.ellipse((20, 20, s - 21, s - 21), outline=ink, width=3)
  font = ctx["fonts"].get("bold", el.get("text_size", int(s * 0.2)))
  check_width(el, el["text"], font, s - 56)
  tw, th, top = text_size(font, el["text"])
  d.text(((s - tw) / 2, (s - th) / 2 - top), el["text"], font=font, fill=ink)
  return img.rotate(el.get("angle", -12), resample=Image.BICUBIC, expand=True)


def draw_dot(el, k, ctx):
  r = el.get("r", 14)
  img = Image.new("RGBA", (r * 2, r * 2), (0, 0, 0, 0))
  ImageDraw.Draw(img).ellipse((0, 0, r * 2 - 1, r * 2 - 1), fill=color(ctx["theme"], el.get("color", "accent")))
  return img


def draw_chapter(el, k, ctx):
  theme, fonts = ctx["theme"], ctx["fonts"]
  num, title = fonts.get("bold", 150), fonts.get("bold", el.get("title_size", 88))
  check_width(el, el["title"], title, W - SAFE_X * 2)
  nw, nh, ntop = text_size(num, el["number"])
  tw, th, ttop = text_size(title, el["title"])
  w, h = max(nw, tw) + 20, nh + th + 72
  img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
  d = ImageDraw.Draw(img)
  d.text(((w - nw) / 2, -ntop), el["number"], font=num, fill=color(theme, "accent"))
  d.text(((w - tw) / 2, nh + 32 - ttop), el["title"], font=title, fill=color(theme, el.get("ink", "ink")))
  d.rectangle(((w - 120) / 2, h - 12, (w + 120) / 2, h - 1), fill=color(theme, "accent"))
  return img


def draw_bar(el, k, ctx):
  theme, fonts = ctx["theme"], ctx["fonts"]
  items = el["items"]
  w, row = el.get("w", 1100), el.get("row", 96)
  label_w, value_w = el.get("label_w", 260), 180
  peak = el.get("max") or max(i["value"] for i in items)
  font, vfont = fonts.get("medium", 38), fonts.get("bold", 40)
  img = Image.new("RGBA", (w, row * len(items)), (0, 0, 0, 0))
  d = ImageDraw.Draw(img)
  track = w - label_w - value_w
  for n, item in enumerate(items):
    y = n * row + row / 2
    p = ease_out((k - n * BAR_STAGGER_SEC) / BAR_GROW_SEC)
    check_width(el, item["label"], font, label_w - 24)
    _, th, top = text_size(font, item["label"])
    d.text((0, y - th / 2 - top), item["label"], font=font, fill=color(theme, "ink"))
    length = max(2, track * item["value"] / peak * p)
    fill = color(theme, "accent" if item.get("hi") else "sub")
    d.rounded_rectangle((label_w, y - 24, label_w + length, y + 24), radius=12, fill=fill)
    text = item.get("text", str(item["value"]))
    _, vh, vtop = text_size(vfont, text)
    d.text((label_w + length + 20, y - vh / 2 - vtop), text, font=vfont, fill=color(theme, "ink"))
  return img


def draw_box(el, k, ctx):
  x, y, w, h = el["rect"]
  ink = color(ctx["theme"], el.get("color", "accent"))
  img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
  fill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
  ImageDraw.Draw(fill).rounded_rectangle((x, y, x + w, y + h), radius=12, fill=ink + "33" if len(ink) == 7 else ink)
  img.alpha_composite(fill)
  ImageDraw.Draw(img).rounded_rectangle((x, y, x + w, y + h), radius=12, outline=ink, width=8)
  return img


def draw_arrow(el, k, ctx):
  (x1, y1), (x2, y2) = el["from"], el["to"]
  p = ease_out(k / ARROW_DRAW_SEC)
  ex, ey = x1 + (x2 - x1) * p, y1 + (y2 - y1) * p
  ink = color(ctx["theme"], el.get("color", "accent"))
  img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
  d = ImageDraw.Draw(img)
  d.line((x1, y1, ex, ey), fill=ink, width=10)
  angle, head = math.atan2(ey - y1, ex - x1), 34
  wing = [(ex - head * math.cos(angle + s), ey - head * math.sin(angle + s)) for s in (0.45, -0.45)]
  d.polygon([(ex, ey), *wing], fill=ink)
  return img


def draw_text(el, k, ctx):
  font = ctx["fonts"].get(el.get("weight", "bold"), el.get("size", 64))
  check_width(el, el["text"], font, W - SAFE_X * 2)
  tw, th, top = text_size(font, el["text"])
  img = Image.new("RGBA", (tw + 4, th + 4), (0, 0, 0, 0))
  ImageDraw.Draw(img).text((2, 2 - top), el["text"], font=font, fill=color(ctx["theme"], el.get("color", "ink")))
  return img


DRAW = {
  "card": draw_card, "chip": draw_chip, "tile": draw_tile, "stamp": draw_stamp, "dot": draw_dot,
  "chapter": draw_chapter, "bar": draw_bar, "box": draw_box, "arrow": draw_arrow, "text": draw_text,
}


def stripe_bg(theme):
  img = Image.new("RGBA", (W, H), color(theme, "bg"))
  d = ImageDraw.Draw(img)
  for x in range(-H, W, 80):
    d.polygon([(x, H), (x + 40, H), (x + 40 + H, 0), (x + H, 0)], fill=color(theme, "stripe"))
  return img


def star_bg(theme, seed):
  img = Image.new("RGBA", (W, H), color(theme, "night"))
  d = ImageDraw.Draw(img)
  rng = random.Random(seed)
  for _ in range(160):
    x, y, r = rng.randrange(W), rng.randrange(H), rng.choice((1, 1, 2, 3))
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, rng.randrange(90, 230)))
  return img


def load_photo(bg, pic_dir):
  src = Image.open(Path(pic_dir) / bg["file"]).convert("RGBA")
  x, y, w, h = bg.get("crop") or cover_crop(src.width, src.height)
  if w > W * 2:
    ratio = W * 2 / w
    src = src.resize((round(src.width * ratio), round(src.height * ratio)), Image.LANCZOS)
    x, y, w, h = (v * ratio for v in (x, y, w, h))
  return src, (x, y, w, h)


def cover_crop(sw, sh):
  if sw / sh > W / H:
    w = sh * W / H
    return ((sw - w) / 2, 0, w, sh)
  h = sw * H / W
  return (0, (sh - h) / 2, sw, h)


def kenburns(src, base, p, bg):
  x, y, w, h = base
  z0, z1 = bg.get("zoom", [1.0, 1.0])
  z = z0 + (z1 - z0) * p
  (fx, fy), (tx, ty) = bg.get("pan", [[0.5, 0.5], [0.5, 0.5]])
  cw, ch = w / z, h / z
  cx = x + cw / 2 + (w - cw) * (fx + (tx - fx) * p)
  cy = y + ch / 2 + (h - ch) * (fy + (ty - fy) * p)
  box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
  return src.resize((W, H), Image.BICUBIC, box=box)


def background(scene, ctx):
  bg = scene.get("bg") or {"type": "none"}
  kind, theme = bg["type"], ctx["theme"]
  if kind == "none":
    return lambda p: Image.new("RGBA", (W, H), (0, 0, 0, 0))
  if kind == "color":
    still = Image.new("RGBA", (W, H), color(theme, bg.get("color", "bg")))
  elif kind == "stripe":
    still = stripe_bg(theme)
  elif kind == "star":
    still = star_bg(theme, scene["id"])
  elif kind == "photo":
    src, base = load_photo(bg, ctx["pic"])
    return lambda p: kenburns(src, base, p, bg)
  else:
    raise ValueError(f"{scene['id']}: 알 수 없는 bg.type {kind}")
  return lambda p: still.copy()


def composite(canvas, img, x, y):
  x, y = round(x), round(y)
  left, top = max(0, -x), max(0, -y)
  if left >= img.width or top >= img.height:
    return
  canvas.alpha_composite(img.crop((left, top, img.width, img.height)), (x + left, y + top))


def overlaps(a, b, gap=24):
  return a[0] < b[2] + gap and b[0] < a[2] + gap and a[1] < b[3] + gap and b[1] < a[3] + gap


def check_layout(scene, el, img, cx, cy, placed):
  if el["type"] in ABSOLUTE:
    return
  name = f"{scene['id']}/{el.get('name', el['type'])}"
  box = (cx - img.width / 2, cy - img.height / 2, cx + img.width / 2, cy + img.height / 2)
  span = (el.get("at", 0.0), el.get("out") or scene["duration"])
  for other, obox, ospan in placed:
    if span[0] < ospan[1] and ospan[0] < span[1] and overlaps(box, obox):
      WARNINGS.append(f"{name}: {other}와 24px 안쪽으로 겹침")
  placed.append((name, box, span))
  if cx - img.width / 2 < SAFE_X or cx + img.width / 2 > W - SAFE_X:
    WARNINGS.append(f"{name}: 좌우 안전 여백 {SAFE_X}px 침범")
  if scene.get("captions", True) and cy + img.height / 2 > CAPTION_TOP:
    WARNINGS.append(f"{name}: 아래쪽이 y={CAPTION_TOP} 자막 영역을 침범")


def render_frame(scene, t, duration, bg, ctx, cache):
  canvas = bg(clamp(t / duration) if duration else 0)
  for el in scene["elements"]:
    state = anim_state(el, t)
    if not state:
      continue
    alpha, dy, scale = state
    key = id(el)
    if el["type"] in GROWING or key not in cache:
      img = DRAW[el["type"]](el, t - el.get("at", 0.0), ctx)
      if el["type"] not in GROWING:
        cache[key] = img
        cx, cy = el.get("x", W / 2), el.get("y", H / 2)
        check_layout(scene, el, img, cx, cy, cache.setdefault("placed", []))
    else:
      img = cache[key]
    if scale != 1.0:
      img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.BICUBIC)
    if alpha < 1.0:
      img = img.copy()
      img.putalpha(Image.eval(img.getchannel("A"), lambda a: int(a * alpha)))
    cx, cy = (W / 2, H / 2) if el["type"] in ABSOLUTE else (el.get("x", W / 2), el.get("y", H / 2))
    composite(canvas, img, cx - img.width / 2, cy - img.height / 2 + dy)
  return canvas


def out_name(scene):
  return f"{scene['id']}_{scene['version']}.mov" if scene.get("version") else f"{scene['id']}.mov"


def encode(scene, fps, ctx, path):
  frames = frame_count(scene["duration"], fps)
  tmp = path.with_suffix(".tmp.mov")
  cmd = [
    "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
    "-r", str(fps), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
    "-vendor", "apl0", "-r", str(fps), str(tmp),
  ]
  proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
  bg, cache = background(scene, ctx), {}
  for i in range(frames):
    proc.stdin.write(render_frame(scene, float(i / fps), scene["duration"], bg, ctx, cache).tobytes())
  proc.stdin.close()
  if proc.wait() != 0:
    tmp.unlink(missing_ok=True)
    raise RuntimeError(f"{scene['id']}: ffmpeg 종료 코드 {proc.returncode}")
  got = probe_frames(tmp)
  if got != frames:
    raise RuntimeError(f"{scene['id']}: 프레임 수 {got} != 기대 {frames}")
  tmp.replace(path)
  return frames


def probe_frames(path):
  cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
         "-show_entries", "stream=nb_read_packets,pix_fmt,codec_name,profile", "-of", "json", str(path)]
  result = subprocess.run(cmd, capture_output=True, text=True, check=True)
  stream = json.loads(result.stdout)["streams"][0]
  if stream["codec_name"] != "prores" or "4444" not in stream.get("profile", "") or not stream["pix_fmt"].startswith("yuva"):
    raise RuntimeError(f"{path.name}: 알파 ProRes 4444 아님 ({stream})")
  return int(stream["nb_read_packets"])


def checker(size, cell=24):
  img = Image.new("RGB", size, "#CCCCCC")
  d = ImageDraw.Draw(img)
  for y in range(0, size[1], cell):
    for x in range((y // cell % 2) * cell, size[0], cell * 2):
      d.rectangle((x, y, x + cell - 1, y + cell - 1), fill="#999999")
  return img


def contact_sheet(scenes, fps, ctx, path):
  tw, th, label = 480, 270, 36
  sheet = Image.new("RGB", (tw * 3, (th + label) * len(scenes)), "#FFFFFF")
  d = ImageDraw.Draw(sheet)
  font = ctx["fonts"].get("medium", 24)
  for row, scene in enumerate(scenes):
    last = frame_count(scene["duration"], fps) - 1
    bg, cache = background(scene, ctx), {}
    for col, (tag, i) in enumerate((("start", 0), ("mid", last // 2), ("end", last))):
      frame = render_frame(scene, float(i / fps), scene["duration"], bg, ctx, cache).resize((tw, th), Image.LANCZOS)
      base = checker((tw, th))
      base.paste(frame, mask=frame.getchannel("A"))
      y = row * (th + label)
      sheet.paste(base, (col * tw, y + label))
      d.text((col * tw + 8, y + 4), f"{scene['id']} {tag} f{i}", font=font, fill="#000000")
  sheet.save(path, quality=88)


def merge_events(path, scenes, fps):
  data = json.loads(path.read_text()) if path.exists() else {}
  data["fps"] = str(fps)
  for scene in scenes:
    data[scene["id"]] = {"file": out_name(scene), "frames": frame_count(scene["duration"], fps), "events": scene_events(scene, fps)}
  path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def load_spec(path):
  spec = json.loads(Path(path).read_text())
  ids = [s["id"] for s in spec["scenes"]]
  if len(ids) != len(set(ids)):
    raise ValueError("장면 id 중복")
  for scene in spec["scenes"]:
    for el in scene["elements"]:
      if el["type"] not in DRAW:
        raise ValueError(f"{scene['id']}: 알 수 없는 요소 {el['type']}")
      if el.get("at", 0.0) >= scene["duration"]:
        raise ValueError(f"{scene['id']}: {el['type']} at {el['at']}초가 장면 길이 이상")
  return spec


def selftest():
  assert ease_out(0) == 0 and ease_out(1) == 1 and ease_out(2) == 1
  assert abs(pop_scale(0) - 0.6) < 1e-9 and abs(pop_scale(POP_PEAK_SEC) - 1.06) < 1e-9 and pop_scale(0.3) == 1.0
  el = {"type": "chip", "at": 1.0, "out": 2.0, "anim": "rise", "text": "x"}
  assert anim_state(el, 0.5) is None and anim_state(el, 2.0) is None
  assert anim_state(el, 1.0)[0] == 0 and anim_state(el, 1.0)[1] == RISE_PX
  assert abs(anim_state(el, 1.9)[0] - 0.4) < 1e-9
  assert parse_fps("23.976") == Fraction(24000, 1001) and parse_fps("24") == 24
  assert frame_count(2.5, Fraction(24)) == 60 and frame_count(1.0, parse_fps("29.97")) == 30
  scene = {"id": "T", "duration": 0.5, "captions": True, "elements": [
    {"type": "stamp", "at": 0.25, "text": "A", "x": 960, "y": 300, "anim": "pop"},
    {"type": "chip", "at": 0.0, "text": "B", "x": 960, "y": 950},
    {"type": "bar", "at": 0.0, "x": 960, "y": 500, "items": [{"label": "a", "value": 3}, {"label": "b", "value": 1, "hi": True}]},
    {"type": "arrow", "at": 0.0, "from": [100, 100], "to": [400, 300], "sfx": "none"},
    {"type": "box", "at": 0.0, "rect": [500, 500, 200, 100]},
  ]}
  events = scene_events(scene, Fraction(24))
  assert [(e["frame"], e["kind"]) for e in events] == [(0, "rise"), (6, "stamp")], events
  ctx = {"theme": THEME, "fonts": Fonts(), "pic": "."}
  WARNINGS.clear()
  frame = render_frame(scene, 0.2, 0.5, background(scene, ctx), ctx, {})
  assert frame.getpixel((0, 0))[3] == 0
  assert any("자막 영역" in w for w in WARNINGS), WARNINGS
  WARNINGS.clear()
  crowded = {"id": "C", "duration": 1.0, "elements": [
    {"type": "chip", "text": "A", "x": 900, "y": 400}, {"type": "chip", "text": "B", "x": 940, "y": 410},
    {"type": "chip", "text": "C", "x": 900, "y": 700, "out": 0.5}, {"type": "chip", "text": "D", "x": 905, "y": 700, "at": 0.5}]}
  cache = {}
  for t in (0.0, 0.6):
    render_frame(crowded, t, 1.0, background(crowded, ctx), ctx, cache)
  assert [w for w in WARNINGS if "겹침" in w] == ["C/chip: C/chip와 24px 안쪽으로 겹침"], WARNINGS
  full = dict(scene, bg={"type": "stripe"})
  assert render_frame(full, 0.0, 0.5, background(full, ctx), ctx, {}).getpixel((0, 0))[3] == 255
  if shutil.which("ffmpeg") and shutil.which("ffprobe"):
    with tempfile.TemporaryDirectory() as tmp:
      path = Path(tmp) / "T.mov"
      assert encode(scene, Fraction(24), ctx, path) == 12 and path.exists()
      contact_sheet([scene], Fraction(24), ctx, Path(tmp) / "sheet.jpg")
  else:
    print("ffmpeg 없음: 인코딩 검사 건너뜀")
  font = Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
  if font.exists():
    assert has_blank_space(font)
  print("selftest ok")


def main():
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("scenes", nargs="*", help="렌더할 장면 id. 비우면 spec의 전체 장면")
  parser.add_argument("--spec", help="장면 spec JSON")
  parser.add_argument("--fps", help="타임라인 fps. 24, 25, 30, 23.976, 29.97, 24000/1001")
  parser.add_argument("--out", help="출력 폴더(<프로젝트>/mg/out)")
  parser.add_argument("--pic", default=".", help="photo 배경 파일 폴더")
  parser.add_argument("--font-bold", help="Gmarket Sans Bold 경로")
  parser.add_argument("--font-medium", help="Gmarket Sans Medium 경로")
  parser.add_argument("--force", action="store_true", help="같은 이름 MOV를 덮어씀")
  parser.add_argument("--stills", action="store_true", help="MOV 없이 시작·중간·끝 contact sheet만 만듦")
  parser.add_argument("--selftest", action="store_true")
  args = parser.parse_args()
  if args.selftest:
    selftest()
    return 0
  if not (args.spec and args.fps and args.out):
    parser.error("--spec, --fps, --out 필요")

  bold = Path(args.font_bold) if args.font_bold else find_font("bold")
  medium = Path(args.font_medium) if args.font_medium else find_font("medium")
  if not (bold and bold.exists() and medium and medium.exists()):
    print("Gmarket Sans Bold/Medium을 찾지 못함. 설치 후 다시 실행하거나 --font-bold/--font-medium으로 경로를 지정한다.", file=sys.stderr)
    return 2
  broken = [p.name for p in (bold, medium) if not has_blank_space(p)]
  if broken:
    print(f"공백 글리프가 비어 있지 않은 글꼴(띄어쓰기가 네모로 그려짐): {broken}. 웹용 woff 대신 TTF/OTF를 쓴다.", file=sys.stderr)
    return 2

  spec = load_spec(args.spec)
  fps = parse_fps(args.fps)
  ctx = {"theme": {**THEME, **spec.get("theme", {})}, "fonts": Fonts(bold, medium), "pic": args.pic}
  wanted = set(args.scenes)
  scenes = [s for s in spec["scenes"] if not wanted or s["id"] in wanted]
  missing = wanted - {s["id"] for s in scenes}
  if missing:
    print(f"spec에 없는 장면: {sorted(missing)}", file=sys.stderr)
    return 2
  out = Path(args.out)
  out.mkdir(parents=True, exist_ok=True)

  if args.stills:
    (out / "stills").mkdir(exist_ok=True)
    contact_sheet(scenes, fps, ctx, out / "stills" / "contact.jpg")
    print(out / "stills" / "contact.jpg")
  else:
    for scene in scenes:
      path = out / out_name(scene)
      if path.exists() and not args.force:
        print(f"건너뜀(이미 있음): {path.name}")
        continue
      frames = encode(scene, fps, ctx, path)
      print(f"{path.name}: {frames}프레임 @ {fps}fps")
    merge_events(out / "events.json", scenes, fps)
  for warning in dict.fromkeys(WARNINGS):
    print(f"경고: {warning}")
  return 1 if WARNINGS else 0


if __name__ == "__main__":
  sys.exit(main())
