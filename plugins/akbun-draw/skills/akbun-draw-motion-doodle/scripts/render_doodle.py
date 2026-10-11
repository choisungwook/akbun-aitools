# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py", "numpy", "pillow", "svgpathtools"]
# ///
"""SVG 장면 그림을 doodle 모션그래픽 영상으로 렌더한다.

스타일에서 숫자로 고정된 부분(그림 수 12장/초, 등장·그려지기·써지기, 하드 컷, 인코딩)은
이 스크립트가 맡고, 모델은 장면마다 SVG 그림(포즈)만 그린다. SVG 요소에 붙이는 시간 속성(장면 시작 기준 초):

  data-show="t"         t초부터 보인다
  data-draw="t0 t1"     <path>의 선이 t0~t1초 동안 시작점부터 끝점까지 그려진다
  data-write="t0 t1"    <text>의 글자가 t0~t1초 동안 한 글자씩 써진다(tspan 없는 text만)

  uv run render_doodle.py spec.json out.mp4            # 흰 배경 H.264
  uv run render_doodle.py spec.json out.mov            # 투명 배경 ProRes 4444 (Resolve 오버레이)
  uv run render_doodle.py spec.json out.mp4 --stills d # 포즈별 마지막 그림 PNG
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

TIMED = ("data-show", "data-draw", "data-write")
ET.register_namespace("", "http://www.w3.org/2000/svg")


def progress(window, t):
  t0, t1 = (float(v) for v in window.split())
  return 1.0 if t1 <= t0 else min(1.0, max(0.0, (t - t0) / (t1 - t0)))


def at_time(root, t):
  """시간 속성을 t초 상태로 풀어 SVG 문자열을 만든다. 시간 속성이 없으면 그대로."""
  if not any(el.get(a) for el in root.iter() for a in TIMED):
    return ET.tostring(root, encoding="unicode")
  root = copy.deepcopy(root)
  for el in root.iter():
    if el.get("data-show") and t + 1e-6 < float(el.get("data-show")):
      el.set("display", "none")
    if el.get("data-draw"):
      p = progress(el.get("data-draw"), t)
      if p <= 0:
        el.set("display", "none")
      elif p < 1:
        length = parse_path(el.get("d")).length()
        el.set("stroke-dasharray", f"{length:.2f} {length:.2f}")
        el.set("stroke-dashoffset", f"{length * (1 - p):.2f}")
    if el.get("data-write"):
      p = progress(el.get("data-write"), t)
      text = el.text or ""
      shown = math.ceil(len(text) * p)
      if shown == 0:
        el.set("display", "none")
      el.text = text[:shown]
  return ET.tostring(root, encoding="unicode")


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
    prev_svg, prev_frame, last = None, None, {}
    frames = round(scene["duration"] * fps)
    for frame in range(frames):
      drawing = frame // hold
      t = drawing / dps
      pose = max(i for i, p in enumerate(poses) if p.get("at", 0) <= t + 1e-6)
      svg = at_time(roots[pose], t)
      if svg != prev_svg:  # 빌드 상태는 거의 반복되지 않아 직전 그림만 들고 있는다
        prev_svg, prev_frame = svg, np.clip(flatten(rasterize(svg, size, font_dirs), background), 0, 255).astype(np.uint8).tobytes()
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


def selftest():
  """포즈 전환·그림 유지 프레임 수·그려지기·써지기·정지를 확인한다."""
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
    assert render(tmp / "spec.json", out) == 60
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(out), "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, 180, 320).astype(int)
    assert len(frames) == 60
    changes = [i for i in range(1, 24) if np.abs(frames[i] - frames[i - 1]).mean() > 0.05]
    assert changes == [12], f"포즈가 바뀌는 0.5초에만 그림이 바뀌어야 함(흔들림 없음): {changes}"
    drawn = [i for i in range(25, 24 + 24) if np.abs(frames[i] - frames[i - 1]).mean() > 0.05]
    assert all(i % 2 == 0 for i in drawn), f"그려지기는 2프레임씩 끊겨야 함: {drawn}"
    assert frames[0][:, 70:130].mean() < frames[0][:, 190:250].mean(), "0초에는 왼쪽 포즈"
    assert frames[23][:, 190:250].mean() < frames[23][:, 70:130].mean(), "0.5초 뒤에는 오른쪽 포즈"
    ink = lambda f, y0, y1, x0, x1: (frames[f][y0:y1, x0:x1] < 128).sum()
    first, mid, end = 24, 24 + 6, 24 + 35
    assert ink(first, 30, 50, 160, 300) == 0 and ink(end, 30, 50, 160, 300) > 0, "선은 시작점부터 그려져야 함"
    assert ink(mid, 30, 50, 20, 100) > 0 and ink(mid, 30, 50, 200, 300) == 0, "0.25초에는 선 앞부분만"
    assert ink(mid, 100, 170, 0, 320) == 0 and ink(end, 100, 170, 0, 320) > 0, "글자·점은 0.5초 전엔 안 보임"
    still = [i for i in range(end, 60) if np.abs(frames[i] - frames[i - 1]).mean() > 0.05]
    assert not still, f"다 그린 뒤에는 정지: {still}"
  print("selftest ok")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("spec", nargs="?")
  parser.add_argument("out", nargs="?")
  parser.add_argument("--stills")
  parser.add_argument("--selftest", action="store_true")
  args = parser.parse_args()
  if args.selftest:
    selftest()
    sys.exit()
  if not args.spec or not args.out or Path(args.out).suffix not in (".mp4", ".mov"):
    parser.error("spec.json과 .mp4 또는 .mov 출력 경로가 필요함")
  print(f"{render(args.spec, Path(args.out), args.stills)} frames -> {args.out}")
