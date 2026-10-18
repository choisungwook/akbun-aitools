# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py", "numpy", "pillow", "svgpathtools"]
# ///
"""SVG 장면 그림을 모션그래픽 영상으로 렌더한다. akbun-draw의 SVG 영상 skill이 같이 쓰는 공용 렌더러다.

모델은 장면마다 SVG 그림(포즈)과 시간 속성만 쓰고, 등장·그려지기·써지기·페이드·카메라·그림 유지·하드 컷·
인코딩은 이 스크립트가 맡는다.

spec.json 구조(경로는 spec 기준 상대 경로):

  {
    "size": [1920, 1080],          # 출력 크기. SVG viewBox 비율과 같아야 함
    "fps": 24,                     # 출력 fps. drawings_per_second의 배수
    "drawings_per_second": 12,     # 초당 그림 수. 12는 기본값일 뿐이고 매끄러운 UI 장면은 fps와 같게 준다
    "background": "#FEFEFE",       # MP4 배경색. MOV는 항상 투명
    "grain": 0.0,                  # 종이 결. 0이면 없음. 0.03이면 밝기 ±3% 고정 노이즈(화면 고정, 프레임마다 같음)
    "font_dirs": [],               # 시스템 글꼴 밖의 글꼴 폴더
    "scenes": [
      {"id": "intro", "duration": 4.0,
       "poses": [{"svg": "intro_a.svg", "at": 0}, {"svg": "intro_b.svg", "at": 1.5}],   # 첫 at은 0
       "camera": [{"at": 0, "zoom": 1}, {"at": 4, "zoom": 1.1, "x": 900, "y": 520, "ease": "linear"}]}
    ]
  }

포즈는 at초부터 다음 포즈 전까지 보인다. 요소를 사라지게 하려면 그 요소가 없는 포즈로 바꾼다(사라짐 속성은 없다).

camera(선택): 키 목록. x·y는 화면 가운데에 올 SVG 좌표(기본은 viewBox 가운데), zoom은 배율(기본 1).
빠진 값은 바로 앞 키의 값을 쓴다. 키 사이는 ease-in-out으로 움직이고, 키에 "ease": "linear"가 있으면
그 키로 가는 구간만 등속이다. 첫 키 전과 마지막 키 뒤는 정지. 카메라는 그림 수와 상관없이 매 프레임 움직인다.

SVG 요소에 붙이는 시간 속성(장면 시작 기준 초, 그림 단위 1/drawings_per_second로 적용. 그 시각 이후 첫 그림부터 바뀌고,
소수 둘째 자리로 적은 값은 0.005초 안의 그림에 걸린다. 예: 12장/초에서 5.17은 5.1667초 그림, 2.3은 2.3333초 그림):

  data-show="t"         t초부터 보인다
  data-fade="t0 t1"     t0~t1초 동안 불투명도가 0에서 원래 값으로 올라간다
  data-draw="t0 t1"     <path>의 선이 t0~t1초 동안 시작점부터 끝점까지 그려진다.
                        점선(stroke-dasharray를 그 <path>에 직접 둔 경우)도 점선 모양을 유지한 채 그려진다
  data-write="t0 t1"    <text>의 글자가 t0~t1초 동안 한 글자씩 써진다. 안쪽 <tspan> 글자까지 순서대로 센다.
                        공백만 있는 글자 조각(tspan 사이 들여쓰기)은 세지 않는다

  uv run render_doodle.py spec.json out.mp4            # 배경색 H.264
  uv run render_doodle.py spec.json out.mov            # 투명 배경 ProRes 4444 (Resolve 오버레이)
  uv run render_doodle.py spec.json out.mp4 --stills d # 포즈별 마지막 그림 PNG
  uv run render_doodle.py --fonts "Pretendard,D2Coding,Gaegu"   # 글꼴이 대체되지 않고 실제로 쓰이는지
  uv run render_doodle.py --selftest
"""
import argparse
import copy
import io
import json
import math
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import resvg_py
from PIL import Image
from svgpathtools import parse_path

TIMED = ("data-show", "data-draw", "data-write", "data-fade")
EPS = 0.005  # 소수 둘째 자리로 적은 시각(5.17)이 그 그림(5.1667)에 걸리게 하는 반올림 여유
ET.register_namespace("", "http://www.w3.org/2000/svg")


def progress(window, t):
  t0, t1 = (float(v) for v in window.split())
  return 1.0 if t1 <= t0 else min(1.0, max(0.0, (t - t0) / (t1 - t0)))


def dashed(el):
  dash = el.get("stroke-dasharray") or ""
  return (dash and dash != "none") or "stroke-dasharray" in (el.get("style") or "")


def text_nodes(el, top=True):
  """<text> 안 글자 조각을 화면 순서대로 (요소, "text"|"tail")로 돌려준다."""
  nodes = [(el, "text")] if el.text else []
  for child in el:
    nodes += text_nodes(child, False)
  if not top and el.tail:
    nodes.append((el, "tail"))
  return nodes


def write(el, p):
  nodes = [(node, part) for node, part in text_nodes(el) if getattr(node, part).strip()]
  shown = math.ceil(sum(len(getattr(n, part)) for n, part in nodes) * p)
  if shown == 0:
    el.set("display", "none")
  for node, part in nodes:
    text = getattr(node, part)
    setattr(node, part, text[:shown])
    shown = max(0, shown - len(text))


def draw(el, p):
  if p <= 0:
    el.set("display", "none")
  elif p < 1:
    path = parse_path(el.get("d"))
    length = path.length()
    if dashed(el):  # 대시 무늬를 지키려고 경로 자체를 진행만큼 자른다
      el.set("d", path.cropped(0, at_length(path, length * p)).d() if length * p > 0.5 else "M0 0")
    else:
      el.set("stroke-dasharray", f"{length:.2f} {length:.2f}")
      el.set("stroke-dashoffset", f"{length * (1 - p):.2f}")


def at_length(path, target):
  """경로 시작에서 target 길이인 지점의 T. svgpathtools ilength는 거의 직선인 Q 곡선에서
  'Maximum iterations reached'로 죽어서 이분 탐색으로 찾는다."""
  lo, hi = 0.0, 1.0
  for _ in range(40):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if path.length(0, mid) < target else (lo, mid)
  return max(lo, 1e-6)


def at_time(root, t, view=None):
  """시간 속성을 t초 상태로 풀고 카메라 view(x, y, zoom)를 viewBox에 적용해 SVG 문자열을 만든다."""
  if view is None and not any(el.get(a) for el in root.iter() for a in TIMED):
    return ET.tostring(root, encoding="unicode")
  root = copy.deepcopy(root)
  for el in root.iter():
    if el.get("data-show") and t + EPS < float(el.get("data-show")):
      el.set("display", "none")
    if el.get("data-fade"):
      p = progress(el.get("data-fade"), t)
      if p <= 0:
        el.set("display", "none")
      el.set("opacity", f"{float(el.get('opacity', 1)) * p:.4f}")
    if el.get("data-draw"):
      draw(el, progress(el.get("data-draw"), t))
    if el.get("data-write"):
      write(el, progress(el.get("data-write"), t))
  if view:
    x0, y0, w, h = (float(v) for v in root.get("viewBox").replace(",", " ").split())
    x, y, zoom = view
    root.set("viewBox", f"{x - w / zoom / 2:.6f} {y - h / zoom / 2:.6f} {w / zoom:.6f} {h / zoom:.6f}")
    root.set("width", f"{w:g}")  # 반올림한 viewBox 비율 때문에 출력 높이가 1px 바뀌지 않게 크기를 고정
    root.set("height", f"{h:g}")
  return ET.tostring(root, encoding="unicode")


def camera_at(keys, t, center):
  """카메라 키 목록에서 t초의 (x, y, zoom)."""
  filled, last = [], {"x": center[0], "y": center[1], "zoom": 1.0}
  for key in sorted(keys, key=lambda k: k["at"]):
    last = {**last, **{k: key[k] for k in ("x", "y", "zoom") if k in key}}
    filled.append((key["at"], key.get("ease"), last))
  if t <= filled[0][0]:
    return tuple(filled[0][2][k] for k in ("x", "y", "zoom"))
  for (a, _, va), (b, ease, vb) in zip(filled, filled[1:]):
    if t < b:
      u = (t - a) / (b - a)
      u = u if ease == "linear" else u * u * (3 - 2 * u)
      return tuple(va[k] + (vb[k] - va[k]) * u for k in ("x", "y", "zoom"))
  return tuple(filled[-1][2][k] for k in ("x", "y", "zoom"))


def rasterize(svg, size, font_dirs):
  png = resvg_py.svg_to_bytes(svg_string=svg, width=size[0], height=size[1], font_dirs=font_dirs or None)
  image = Image.open(io.BytesIO(bytes(png))).convert("RGBA")
  if image.size != tuple(size):
    raise ValueError(f"viewBox 비율이 {size}와 다름 ({image.size})")
  return np.asarray(image, dtype=np.float32)


def flatten(rgba, background):
  if background == "transparent":
    return rgba
  bg = np.array([int(background[i:i + 2], 16) for i in (1, 3, 5)] + [255], dtype=np.float32)
  alpha = rgba[..., 3:4] / 255
  return rgba * alpha + bg * (1 - alpha)


def grain_map(size, amount):
  """화면에 고정된 종이 결. 반 해상도 노이즈를 키워 알갱이를 부드럽게 한다(feTurbulence보다 수백 배 빠름)."""
  noise = np.random.default_rng(7).uniform(-1, 1, (size[1] // 2, size[0] // 2)).astype(np.float32)
  noise = np.asarray(Image.fromarray(noise, mode="F").resize(tuple(size), Image.BILINEAR))
  return (1 + amount * noise)[..., None]


def encoder_args(out, size, fps):
  head = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{size[0]}x{size[1]}", "-r", str(fps), "-i", "-"]
  if out.suffix == ".mov":
    return head + ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", str(out)]
  return head + ["-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]


def render(spec_path, out, stills=None):
  spec_path = Path(spec_path)
  spec = json.loads(spec_path.read_text())
  base = spec_path.parent
  size = spec.get("size", [1920, 1080])
  fps = spec.get("fps", 24)
  dps = spec.get("drawings_per_second", 12)
  background = "transparent" if out.suffix == ".mov" else spec.get("background", "#FEFEFE")
  font_dirs = [str(base / Path(d).expanduser()) for d in spec.get("font_dirs", [])]
  grain = grain_map(size, spec["grain"]) if spec.get("grain") else None
  if fps % dps:
    raise ValueError(f"fps({fps})는 drawings_per_second({dps})의 배수여야 그림 한 장이 같은 프레임 수로 유지됨")
  hold = fps // dps

  encoder = subprocess.Popen(encoder_args(Path(out), size, fps), stdin=subprocess.PIPE)
  total = 0
  for index, scene in enumerate(spec["scenes"]):
    poses = sorted(scene["poses"], key=lambda p: p.get("at", 0))
    if poses[0].get("at", 0) != 0:
      raise ValueError(f"{scene['id']}: 첫 포즈의 at은 0이어야 함")
    roots = [ET.parse(base / p["svg"]).getroot() for p in poses]
    box = [float(v) for v in roots[0].get("viewBox").replace(",", " ").split()]
    center = (box[0] + box[2] / 2, box[1] + box[3] / 2)
    prev_svg, prev_frame, last = None, None, {}
    frames = round(scene["duration"] * fps)
    for frame in range(frames):
      t = frame // hold / dps
      pose = max(i for i, p in enumerate(poses) if p.get("at", 0) <= t + EPS)
      view = camera_at(scene["camera"], frame / fps, center) if scene.get("camera") else None
      svg = at_time(roots[pose], t, view)
      if svg != prev_svg:  # 빌드 상태는 거의 반복되지 않아 직전 그림만 들고 있는다
        rgba = flatten(rasterize(svg, size, font_dirs), background)
        if grain is not None:
          rgba[..., :3] *= grain
        prev_svg, prev_frame = svg, np.clip(rgba, 0, 255).astype(np.uint8).tobytes()
      last[pose] = prev_frame
      encoder.stdin.write(prev_frame)
    if stills:
      Path(stills).mkdir(parents=True, exist_ok=True)
      for pose, data in last.items():
        Image.frombytes("RGBA", tuple(size), data).save(Path(stills) / f"{index + 1:02d}_{scene['id']}_{pose + 1}.png")
    total += frames
  encoder.stdin.close()
  if encoder.wait():
    raise RuntimeError("ffmpeg 인코딩 실패")
  return total


def font_check(families, font_dirs=None):
  """글꼴마다 '가Ag1'을 그려, 없는 글꼴 이름(대체 글꼴)과 픽셀이 같으면 missing으로 본다."""
  probe = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 100"><text x="10" y="75" font-size="64" font-family="{}">가Ag1</text></svg>'
  fallback = rasterize(probe.format("NoSuchFont-xyz"), (400, 100), font_dirs)
  return {f: "ok" if np.abs(rasterize(probe.format(f"'{f}'"), (400, 100), font_dirs) - fallback).mean() > 0.5 else "missing" for f in families}


def decode(out, w, h):
  raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(out), "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
  return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(int)


def selftest():
  """포즈 전환·그림 유지·그려지기(실선·점선)·써지기(tspan 포함)·페이드·카메라·종이 결·정지를 확인한다."""
  with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180"><circle cx="{}" cy="90" r="30" fill="none" stroke="#000" stroke-width="4"/></svg>'
    (tmp / "a.svg").write_text(svg.format(100))
    (tmp / "b.svg").write_text(svg.format(220))
    (tmp / "draw.svg").write_text(
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180">'
      '<path d="M20 40 L300 40" stroke="#000" stroke-width="8" data-draw="0 1"/>'
      '<text x="20" y="150" font-size="60" fill="#000" data-write="0.5 1">ABCD</text>'
      '<circle cx="160" cy="100" r="10" fill="#000" data-show="0.5"/></svg>')
    spec = {"size": [320, 180], "fps": 24, "scenes": [
      {"id": "t", "duration": 1.0, "poses": [{"svg": "a.svg", "at": 0}, {"svg": "b.svg", "at": 0.5}]},
      {"id": "d", "duration": 1.5, "poses": [{"svg": "draw.svg", "at": 0}]}]}
    (tmp / "spec.json").write_text(json.dumps(spec))
    out = tmp / "out.mp4"
    spec["scenes"][0]["poses"][1]["at"] = 0.17  # 0.1667초 그림에 걸려야 함(소수 둘째 자리 반올림)
    (tmp / "spec.json").write_text(json.dumps(spec))
    assert render(tmp / "spec.json", out) == 60
    frames = decode(out, 320, 180)
    assert len(frames) == 60
    changes = [i for i in range(1, 24) if np.abs(frames[i] - frames[i - 1]).mean() > 0.05]
    assert changes == [4], f"포즈가 바뀌는 0.17초(그림 2장)에만 그림이 바뀌어야 함(흔들림 없음): {changes}"
    drawn = [i for i in range(25, 24 + 24) if np.abs(frames[i] - frames[i - 1]).mean() > 0.05]
    assert all(i % 2 == 0 for i in drawn), f"그려지기는 2프레임씩 끊겨야 함: {drawn}"
    assert frames[0][:, 70:130].mean() < frames[0][:, 190:250].mean(), "0초에는 왼쪽 포즈"
    assert frames[23][:, 190:250].mean() < frames[23][:, 70:130].mean(), "0.17초 뒤에는 오른쪽 포즈"
    ink = lambda f, y0, y1, x0, x1: (f[y0:y1, x0:x1] < 128).sum()
    first, mid, end = 24, 24 + 6, 24 + 35
    assert ink(frames[first], 30, 50, 160, 300) == 0 and ink(frames[end], 30, 50, 160, 300) > 0, "선은 시작점부터 그려져야 함"
    assert ink(frames[mid], 30, 50, 20, 100) > 0 and ink(frames[mid], 30, 50, 200, 300) == 0, "0.25초에는 선 앞부분만"
    assert ink(frames[mid], 100, 170, 0, 320) == 0 and ink(frames[end], 100, 170, 0, 320) > 0, "글자·점은 0.5초 전엔 안 보임"
    still = [i for i in range(end, 60) if np.abs(frames[i] - frames[i - 1]).mean() > 0.05]
    assert not still, f"다 그린 뒤에는 정지: {still}"

    (tmp / "extra.svg").write_text(
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180">'
      '<path d="M20 30 Q160 30.1 300 30" stroke="#000" stroke-width="8" stroke-dasharray="20 20" data-draw="0 1"/>'
      '<text x="20" y="100" font-size="50" fill="#000" data-write="0 1"><tspan>AB</tspan> <tspan fill="#000">CD</tspan></text>'
      '<rect x="20" y="130" width="280" height="40" fill="#000" data-fade="0 1"/></svg>')
    (tmp / "dot.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180"><rect x="20" y="70" width="40" height="40" fill="#000"/></svg>')
    spec = {"size": [320, 180], "fps": 24, "drawings_per_second": 24, "grain": 0.04, "scenes": [
      {"id": "x", "duration": 1.5, "poses": [{"svg": "extra.svg", "at": 0}]},
      {"id": "c", "duration": 1.0, "poses": [{"svg": "dot.svg", "at": 0}],
       "camera": [{"at": 0}, {"at": 1, "zoom": 2, "x": 40, "y": 90}]}]}
    (tmp / "spec2.json").write_text(json.dumps(spec))
    out = tmp / "out2.mp4"
    assert render(tmp / "spec2.json", out) == 60
    frames = decode(out, 320, 180)
    half, done = frames[12], frames[30]
    assert ink(half, 20, 40, 20, 150) > 0 and ink(half, 20, 40, 170, 300) == 0, "점선도 시작점부터 그려져야 함"
    row = (done[30, 20:300] < 128)
    assert 0.3 < row.mean() < 0.7, f"다 그린 점선은 대시 무늬를 유지해야 함: {row.mean():.2f}"
    assert ink(half, 50, 110, 20, 120) > 0 and ink(half, 50, 110, 150, 300) == 0, "tspan 글자도 앞 글자부터 써져야 함"
    assert ink(done, 50, 110, 150, 300) > 0, "다 써지면 뒤 tspan 글자까지 보임"
    fade = [frames[i][140:160, 40:280].mean() for i in (0, 12, 30)]
    assert fade[0] > 200 and 60 < fade[1] < 200 and fade[2] < 60, f"페이드는 중간 밝기를 거쳐야 함: {fade}"
    g = (np.abs(frames[30] - frames[31]).mean(), frames[30][0:15].std())
    assert g[0] < 0.3 and g[1] > 1, f"종이 결은 프레임마다 같은 고정 노이즈: {g}"
    cam = frames[36:60]
    moved = [i for i in range(1, len(cam)) if np.abs(cam[i] - cam[i - 1]).mean() > 0.05]
    assert len(moved) >= 20, f"카메라는 매 프레임 움직여야 함: {moved}"
    width = lambda f: (f[90] < 128).sum()
    assert width(frames[36]) < 50 and width(frames[59]) > 70, "줌 2배면 상자 폭이 두 배 가까이"
    assert 120 < np.nonzero(frames[59][90] < 128)[0].mean() < 200, "x·y 지점이 화면 가운데로 옴"
    step = [np.nonzero(frames[i][90] < 128)[0].mean() for i in (37, 38, 47, 48)]
    assert abs(step[1] - step[0]) < abs(step[3] - step[2]), "ease-in-out: 시작은 느리고 중간은 빠름"
  print("selftest ok")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("spec", nargs="?")
  parser.add_argument("out", nargs="?")
  parser.add_argument("--stills")
  parser.add_argument("--fonts", help="쉼표로 나눈 글꼴 이름. 대체 글꼴로 그려지는지 검사")
  parser.add_argument("--selftest", action="store_true")
  args = parser.parse_args()
  if args.fonts:
    result = font_check([f.strip() for f in args.fonts.split(",")])
    print(json.dumps(result))
    sys.exit(1 if "missing" in result.values() else 0)
  if args.selftest:
    selftest()
    sys.exit()
  if not args.spec or not args.out or Path(args.out).suffix not in (".mp4", ".mov"):
    parser.error("spec.json과 .mp4 또는 .mov 출력 경로가 필요함")
  print(f"{render(args.spec, Path(args.out), args.stills)} frames -> {args.out}")
