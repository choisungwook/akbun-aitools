# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py", "numpy", "pillow"]
# ///
"""창 카드(스크린샷·화면 녹화) 장면을 Resolve 안의 Fusion 노드로 만든다. akbun-edit-* 카드 스킬이 같이 쓴다.

  frame   창 틀 PNG(캔버스 크기, 틀 밖 투명)와 content 사각형 JSON
  arrow   손그림 화살표 PNG(캔버스 크기, 투명)
  canvas  타임라인 fps의 단색 캔버스 영상(H.264). 정지 PNG는 AppendToTimeline 길이를 무시하고 5초로 들어가서 쓴다
  where   스크린샷 픽셀 사각형 → 화면(캔버스) 사각형. 표시·주석 좌표를 계산할 때 쓴다
  build   plan.json대로 작업 타임라인 복제 → 새 트랙에 캔버스 클립 → Fusion 노드 구성.
          plan "mode": "title"이면 장면 전용 타임라인 끝에 Fusion 타이틀로 붙이고, 노드를 Template 매크로로 감싸
          Edit 페이지 Inspector(Video > Title)에 표시 색·위치·크기, 카드 위치·크기, 주석 글자·위치를 띄운다
  retime  녹음 뒤 plan의 시각(at·duration·start·camera)만 바꿔 다시 적용. 사용자가 고친 노드 위치·색은 그대로 둔다
  grab    만든 클립 구간을 Deliver로 렌더해 프레임별 PNG와 contact sheet를 만든다

좌표는 모두 1920×1080 캔버스의 픽셀(왼쪽 위 원점)이고, 시간은 클립 시작 기준 초다.
Fusion 쪽 변환(정규화·아래 원점·Crop YOffset)은 이 스크립트가 한다.

  uv run resolve_cards.py frame --rect 239,70,1442,960 --theme light --title github.com/me/repo --out card01_frame.png
  uv run resolve_cards.py arrow --start 1300,520 --end 1080,460 --color '#FFD84D' --out callout01_arrow.png
  uv run resolve_cards.py canvas --fps 30 --seconds 60 --out canvas_30fps.mp4
  uv run resolve_cards.py where plan.json --card 01 --rect 240,1240,1760,64
  uv run resolve_cards.py build plan.json
  uv run resolve_cards.py retime plan.json --old-at 12.0
  uv run resolve_cards.py grab plan.json --frames 0,15,60,120 --out grab/
  uv run resolve_cards.py --selftest
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

W, H = 1920, 1080
THEMES = {
  "light": {"body": "#FFFFFF", "edge": "#D6D6DA", "bar": "#F6F6F7", "text": "#57606A"},
  "dark": {"body": "#1B2224", "edge": "#2E3A3D", "bar": "#232C2E", "text": "#9AA4AB"},
}
BAR = 44


def hex_rgb(value):
  return [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def frame_svg(x, y, w, h, theme, title):
  c = THEMES[theme]
  title_svg = (f'<text x="{x + 100}" y="{y + BAR / 2 + 6}" font-family="Pretendard, \'Noto Sans KR\', sans-serif" '
               f'font-size="17" font-weight="600" fill="{c["text"]}">{title}</text>') if title else ""
  lights = "".join(f'<circle cx="{x + 24 + i * 22}" cy="{y + BAR / 2}" r="7" fill="{col}"/>' for i, col in enumerate(("#FF5F57", "#FEBC2E", "#28C840")))
  return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">'
          f'<filter id="s" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="18"/></filter>'
          f'<rect x="{x}" y="{y + 18}" width="{w}" height="{h}" rx="14" fill="#000" opacity="0.16" filter="url(#s)"/>'
          f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{c["body"]}" stroke="{c["edge"]}" stroke-width="1.5"/>'
          f'<path d="M{x} {y + BAR}V{y + 14}a14 14 0 0 1 14 -14H{x + w - 14}a14 14 0 0 1 14 14V{y + BAR}Z" fill="{c["bar"]}"/>'
          f'<path d="M{x} {y + BAR}H{x + w}" stroke="{c["edge"]}" stroke-width="1.5"/>{lights}{title_svg}</svg>')


def frame_content(x, y, w, h):
  """제목줄 아래 안쪽 사각형. 스크린샷이 창 테두리 1px 안쪽까지 꽉 차게 둔다."""
  return [x + 1, y + BAR + 1, w - 2, h - BAR - 2]


def arrow_svg(start, end, color, width=7):
  """살짝 휜 손그림 화살표. 머리는 끝점에서 열린 두 획."""
  (x0, y0), (x1, y1) = start, end
  dx, dy = x1 - x0, y1 - y0
  length = math.hypot(dx, dy)
  nx, ny = -dy / length, dx / length
  bend = length * 0.16
  cx, cy = (x0 + x1) / 2 + nx * bend, (y0 + y1) / 2 + ny * bend
  a = math.atan2(y1 - cy, x1 - cx)
  head = [(x1 - 30 * math.cos(a + s), y1 - 30 * math.sin(a + s)) for s in (0.5, -0.5)]
  return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><g fill="none" stroke="{color}" stroke-width="{width}" '
          f'stroke-linecap="round" stroke-linejoin="round"><path d="M{x0} {y0}Q{cx:.1f} {cy:.1f} {x1} {y1}"/>'
          + "".join(f'<path d="M{x1} {y1}L{hx:.1f} {hy:.1f}"/>' for hx, hy in head) + "</g></svg>")


def write_png(svg, out):
  import resvg_py
  Path(out).write_bytes(bytes(resvg_py.svg_to_bytes(svg_string=svg, width=W, height=H)))


def canvas(fps, seconds, color, out):
  subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x{color.lstrip('#')}:s={W}x{H}:r={fps}",
                  "-t", str(seconds), "-c:v", "libx264", "-pix_fmt", "yuv420p", out], check=True)


def shot_size(card):
  if card.get("shot_size"):
    return card["shot_size"]
  from PIL import Image
  with Image.open(card["shot"]) as image:
    return list(image.size)


def placement(card):
  """스크린샷을 content 폭에 맞춘 배율과 보이는 crop 높이."""
  cx, cy, cw, ch = card["content"]
  sx, sy, sw, sh = card["crop"]
  scale = cw / sw
  return scale, (sh or ch / scale)


def where(card, rect):
  """스크린샷 픽셀 사각형 → 캔버스 픽셀 사각형(카메라 zoom 1 기준)."""
  scale, _ = placement(card)
  cx, cy = card["content"][:2]
  sx, sy = card["crop"][:2]
  x, y, w, h = rect
  return [round(cx + (x - sx) * scale, 1), round(cy + (y - sy) * scale, 1), round(w * scale, 1), round(h * scale, 1)]


# ---------- Fusion 좌표와 표현식 ----------

def norm(x, y):
  return {1: x / W, 2: 1 - y / H}


def ramp(start, length, fps):
  """시작 초·길이 초의 0→1 진행. 클립 comp는 0프레임이 클립 첫 프레임이라 time을 그대로 쓴다.
  comp.RenderStart는 한 프레임씩 렌더할 때 그 프레임으로 바뀌어(21.1 실측: 카드가 끝까지 안 보임) 표현식에 쓰지 않는다."""
  s, n = round(start * fps), max(1, round(length * fps))
  return f"min(1, max(0, (time - {s}) / {n}))"


def camera_keys(keys, fps):
  """카메라 키(at·zoom·x·y·ease)를 Size·Center X·Center Y 키프레임으로 바꾼다. 손잡이는 키 기준 상대 좌표다.
  화면 점 P를 가운데로 zoom z: Center = 0.5 + (0.5 - P정규화) × z (y는 1 - py/H)."""
  last = {"zoom": 1.0, "x": W / 2, "y": H / 2}
  filled = []
  for key in sorted(keys, key=lambda k: k["at"]):
    last = {**last, **{k: key[k] for k in ("zoom", "x", "y") if k in key}}
    z = last["zoom"]
    filled.append((round(key["at"] * fps), key.get("ease"), {"size": z, "cx": 0.5 + (0.5 - last["x"] / W) * z,
                                                             "cy": 0.5 + (0.5 - (1 - last["y"] / H)) * z}))
  curves = {}
  for name in ("size", "cx", "cy"):
    curve = {}
    for i, (frame, _, values) in enumerate(filled):
      point = {1: values[name]}
      for j, side in ((i - 1, "LH"), (i + 1, "RH")):
        if 0 <= j < len(filled):
          other_frame, other_values = filled[j][0], filled[j][2]
          linear = filled[max(i, j)][1] == "linear"  # 그 키로 가는 구간의 ease
          point[side] = {1: (other_frame - frame) / 3, 2: (other_values[name] - values[name]) / 3 if linear else 0.0}
      curve[frame] = point
    curves[name] = curve
  return curves


# ---------- Resolve ----------

def connect():
  api = os.environ.setdefault("RESOLVE_SCRIPT_API", "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting")
  os.environ.setdefault("RESOLVE_SCRIPT_LIB", "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so")
  sys.path.append(os.path.join(api, "Modules"))
  import DaVinciResolveScript as dvr
  resolve = dvr.scriptapp("Resolve")
  if not resolve:
    sys.exit("Resolve에 연결하지 못함: Resolve Studio 실행과 External scripting = Local 확인")
  return resolve


def find_timeline(project, name):
  for i in range(1, project.GetTimelineCount() + 1):
    timeline = project.GetTimelineByIndex(i)
    if timeline.GetName() == name:
      return timeline
  return None


def snapshot(timeline):
  """작업 트랙 밖의 클립·마커. 배치 전후로 같아야 본편을 밀지 않은 것이다."""
  items = {}
  for kind in ("video", "audio"):
    for track in range(1, timeline.GetTrackCount(kind) + 1):
      items[f"{kind}{track}"] = [(i.GetName(), i.GetStart(), i.GetEnd()) for i in timeline.GetItemListInTrack(kind, track) or []]
  return {"items": items, "markers": timeline.GetMarkers()}


def media_item(media_pool, path):
  for clip in media_pool.GetRootFolder().GetClipList():
    if clip.GetClipProperty("File Path") == path:
      return clip
  return media_pool.ImportMedia([path])[0]


def open_work(plan):
  resolve = connect()
  project = resolve.GetProjectManager().GetCurrentProject()
  fps = float(project.GetSetting("timelineFrameRate"))
  if abs(fps - plan["fps"]) > 1e-3:
    sys.exit(f"타임라인 fps {fps}와 plan fps {plan['fps']}가 다름")
  timeline = find_timeline(project, plan["work_timeline"])
  if not timeline:
    source = find_timeline(project, plan["source_timeline"]) if plan.get("source_timeline") else project.GetCurrentTimeline()
    project.SetCurrentTimeline(source)
    timeline = source.DuplicateTimeline(plan["work_timeline"])
  project.SetCurrentTimeline(timeline)
  return resolve, project, timeline, fps


def own_clip(timeline, plan, at, fps):
  record = timeline.GetStartFrame() + round(at * fps)
  for track in range(1, timeline.GetTrackCount("video") + 1):
    if timeline.GetTrackName("video", track) == plan["track_name"]:
      for item in timeline.GetItemListInTrack("video", track) or []:
        if item.GetStart() == record:
          return track, item
  return None, None


def place(project, timeline, plan, fps, track=None):
  """plan 위치에 캔버스 클립을 놓는다. 같은 이름의 트랙 중 그 구간이 빈 것을 쓰고, 없으면 맨 위에 새 트랙을 만든다."""
  record = timeline.GetStartFrame() + round(plan["at"] * fps)
  frames = round(plan["duration"] * fps)
  label = plan["track_name"]

  def busy(t):
    return [i for i in timeline.GetItemListInTrack("video", t) or [] if i.GetStart() < record + frames and i.GetEnd() > record]

  if track is None:
    track = next((t for t in range(1, timeline.GetTrackCount("video") + 1)
                  if timeline.GetTrackName("video", t) == label and not busy(t)), None)
  before = snapshot(timeline)
  if track is None:
    timeline.AddTrack("video")
    track = timeline.GetTrackCount("video")
    timeline.SetTrackName("video", track, label)
  if busy(track):
    sys.exit(f"트랙 {track}의 {plan['at']}초 구간이 비어 있지 않음")
  canvas_item = media_item(project.GetMediaPool(), plan["canvas_clip"])
  placed = project.GetMediaPool().AppendToTimeline([{"mediaPoolItem": canvas_item, "startFrame": 0, "endFrame": frames,
                                                      "trackIndex": track, "recordFrame": record, "mediaType": 1}])
  if not placed:
    sys.exit("AppendToTimeline 실패: Resolve에 열린 대화상자가 있는지, Edit 페이지인지 확인")
  item = placed[0]
  if (item.GetStart(), item.GetDuration()) != (record, frames):
    sys.exit(f"배치 길이 불일치: 요청 {record}+{frames}, 실제 {item.GetStart()}+{item.GetDuration()}")
  after = snapshot(timeline)
  others = lambda snap: {k: v for k, v in snap["items"].items() if k != f"video{track}"}
  if others(before) != others(after) or before["markers"] != after["markers"]:
    sys.exit("작업 트랙 밖의 클립·마커가 바뀜: 이 작업본을 쓰지 말 것")
  return track, item


def add(comp, kind, name, x, y, **inputs):
  tool = comp.AddTool(kind, x, y)
  tool.SetAttrs({"TOOLS_Name": name})
  for key, value in inputs.items():
    tool.SetInput(key, value)
  return tool


def color_inputs(hex_color, alpha=1.0):
  r, g, b = hex_rgb(hex_color)
  return {"TopLeftRed": r * alpha, "TopLeftGreen": g * alpha, "TopLeftBlue": b * alpha, "TopLeftAlpha": alpha}


def build_comp(comp, plan, fps):
  """노드 구조와 위치·색만 만든다. 시각은 apply_timing이 넣는다."""
  comp.Lock()
  for tool in list(comp.GetToolList().values()):
    if tool.GetAttrs()["TOOLS_Name"] != "MediaOut1":
      tool.Delete()
  made = []
  base = add(comp, "Background", "CANVAS", 0, 0, Width=W, Height=H, **color_inputs(plan.get("canvas_color", "#EAEAEA")))
  made.append("CANVAS")
  row = 0
  for card in plan["cards"]:
    cid = card["id"]
    row += 4
    size = shot_size(card)
    scale, crop_h = placement(card)
    cx, cy, cw, ch = card["content"]
    sx, sy, sw, _ = card["crop"]
    frame_png = add(comp, "Loader", f"FRAME_{cid}", 0, row, Clip=card["frame"], HoldLastFrame=100000)
    # Loader의 투명 영역은 DoD에서 빠져 창 밖에 놓은 라벨이 창 끝에서 잘렸다(21.1.1 실측). 투명한 화면 크기 바탕 위에 올린다
    space = add(comp, "Background", f"CARD_{cid}_SPACE", 0, row + 1, Width=W, Height=H, **color_inputs("#000000", 0.0))
    frame = add(comp, "Merge", f"FRAME_{cid}_PLACE", 1, row)
    frame.ConnectInput("Background", space)
    frame.ConnectInput("Foreground", frame_png)
    shot = add(comp, "Loader", f"SHOT_{cid}", 1, row + 1, Clip=card["shot"], HoldLastFrame=100000)
    if card.get("trim_in"):
      shot.SetInput("ClipTimeStart", round(card["trim_in"] * fps))
    crop = add(comp, "Crop", f"SHOT_{cid}_CROP", 2, row + 1, XOffset=sx, YOffset=size[1] - sy - crop_h, XSize=sw, YSize=crop_h)
    crop.ConnectInput("Input", shot)
    mask = add(comp, "RectangleMask", f"CONTENT_{cid}_MASK", 3, row + 2, Center=norm(cx + cw / 2, cy + ch / 2),
               Width=cw / W, Height=ch / H)
    content = add(comp, "Merge", f"CONTENT_{cid}", 3, row, Center=norm(cx + cw / 2, cy + crop_h * scale / 2), Size=scale)
    content.ConnectInput("Background", frame)
    content.ConnectInput("Foreground", crop)
    content.ConnectInput("EffectMask", mask)
    made += [f"FRAME_{cid}", f"SHOT_{cid}", f"SHOT_{cid}_CROP", f"CONTENT_{cid}"]
    top, col = content, 4
    for mark in [m for m in plan.get("marks", []) if m["card"] == cid]:
      top = add_mark(comp, mark, top, col, row)
      made.append(f"MARK_{mark['id']}")
      col += 1
    for call in [c for c in plan.get("callouts", []) if c["card"] == cid]:
      top = add_callout(comp, call, top, col, row)
      made.append(f"CALLOUT_{call['id']}")
      col += 2
    layout = add(comp, "Merge", f"CARD_{cid}_LAYOUT", max(col, 12), 0)
    layout.ConnectInput("Background", base)
    layout.ConnectInput("Foreground", top)
    base = layout
    made.append(f"CARD_{cid}_LAYOUT")
  camera = add(comp, "Transform", "CAMERA", 14, 0)
  camera.ConnectInput("Input", base)
  comp.FindTool("MediaOut1").ConnectInput("Input", camera)
  made.append("CAMERA")
  apply_timing(comp, plan, fps)
  comp.Unlock()
  return made


def sweeps(mark):
  return mark.get("sweep", mark["kind"] == "highlight")


def add_mark(comp, mark, top, col, row):
  """highlight: 연한 색을 Multiply로 칠함(밝은 화면). fill: 반투명 채움(어두운 화면). box: 외곽 상자.
  sweep(기본: highlight만 true)이면 왼쪽→오른쪽으로 쓸어 나타나고, 아니면 Blend로 페이드된다."""
  mid = mark["id"]
  x, y, w, h = mark["rect"]
  color = add(comp, "Background", f"MARK_{mid}_COLOR", col, row + 2, Width=W, Height=H,
              **color_inputs(mark["color"], mark.get("alpha", 1.0)))
  shape = add(comp, "RectangleMask", f"MARK_{mid}_SHAPE", col, row + 3, Center=norm(x + w / 2, y + h / 2), Width=w / W, Height=h / H,
              CornerRadius=mark.get("corner", 0.05))
  if mark["kind"] == "box":
    shape.SetInput("Solid", 0)
    shape.SetInput("BorderWidth", mark.get("border", 4) / W)
  color.ConnectInput("EffectMask", shape)
  merge = add(comp, "Merge", f"MARK_{mid}", col, row)
  merge.ConnectInput("Background", top)
  merge.ConnectInput("Foreground", color)
  if mark["kind"] == "highlight":
    merge.SetInput("ApplyMode", "Multiply")
  if sweeps(mark):
    reveal = add(comp, "RectangleMask", f"MARK_{mid}_REVEAL", col, row + 4)
    reveal.Width.SetExpression(f"MARK_{mid}_SHAPE.Width")
    reveal.Height.SetExpression(f"MARK_{mid}_SHAPE.Height * 2")
    shape.ConnectInput("EffectMask", reveal)
    shape.SetInput("PaintMode", "Multiply")
  return merge


def add_callout(comp, call, top, col, row):
  """손그림 화살표(PNG)와 Text+ 라벨."""
  cid = call["id"]
  arrow = add(comp, "Loader", f"CALLOUT_{cid}_ARROW", col, row + 2, Clip=call["arrow"], HoldLastFrame=100000)
  merge_arrow = add(comp, "Merge", f"CALLOUT_{cid}", col, row)
  merge_arrow.ConnectInput("Background", top)
  merge_arrow.ConnectInput("Foreground", arrow)
  r, g, b = hex_rgb(call["color"])
  label = add(comp, "TextPlus", f"CALLOUT_{cid}_LABEL", col + 1, row + 3, StyledText=call["label"], Font=call.get("font", "Gaegu"),
              Style=call.get("style", "Bold"), Size=call.get("size", 44) / W, Center=norm(*call["pos"]),  # Text+ Size는 화면 폭 기준
              Red1=r, Green1=g, Blue1=b, Width=W, Height=H)
  merge_label = add(comp, "Merge", f"CALLOUT_{cid}_TEXT", col + 1, row)
  merge_label.ConnectInput("Background", merge_arrow)
  merge_label.ConnectInput("Foreground", label)
  return merge_label


def apply_timing(comp, plan, fps):
  """시각만 넣는다: 카드·표시·주석의 등장 표현식과 CAMERA 키프레임. 위치·색·크기 입력은 건드리지 않는다."""
  for card in plan["cards"]:
    start, length = card.get("fade", [0, 0.25])
    comp.FindTool(f"CARD_{card['id']}_LAYOUT").Blend.SetExpression(ramp(start, length, fps))
  for mark in plan.get("marks", []):
    mid, progress = mark["id"], ramp(mark["start"], mark["len"], fps)
    if sweeps(mark):
      comp.FindTool(f"MARK_{mid}_REVEAL").Center.SetExpression(
        f"Point(MARK_{mid}_SHAPE.Center.X - MARK_{mid}_SHAPE.Width * (1 - {progress}), MARK_{mid}_SHAPE.Center.Y)")
    else:
      comp.FindTool(f"MARK_{mid}").Blend.SetExpression(progress)
  for call in plan.get("callouts", []):
    comp.FindTool(f"CALLOUT_{call['id']}").Blend.SetExpression(ramp(call["start"], 0.2, fps))
    comp.FindTool(f"CALLOUT_{call['id']}_TEXT").Blend.SetExpression(ramp(call["start"] + 0.25, 0.2, fps))
  camera = comp.FindTool("CAMERA")
  if plan.get("camera"):
    curves = camera_keys(plan["camera"], fps)
    size = comp.BezierSpline()
    camera.ConnectInput("Size", size)
    size.SetKeyFrames(curves["size"], True)
    path = comp.XYPath()
    camera.ConnectInput("Center", path)
    for axis, name in (("X", "cx"), ("Y", "cy")):
      spline = comp.BezierSpline()
      path.ConnectInput(axis, spline)
      spline.SetKeyFrames(curves[name], True)


STILL = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".exr")


def check_names(plan):
  """Fusion Loader는 이름이 숫자로 끝나는 정지 이미지(frame01.png, frame02.png)를 한 시퀀스로 읽어
  카드마다 다른 그림이 시간에 따라 바뀌어 나온다(21.1.1 실측). 정지 이미지 이름은 숫자로 끝나지 않게 한다."""
  paths = [c["frame"] for c in plan["cards"]] + [c["shot"] for c in plan["cards"]] + [c["arrow"] for c in plan.get("callouts", [])]
  bad = [p for p in paths if Path(p).suffix.lower() in STILL and Path(p).stem[-1:].isdigit()]
  if bad:
    sys.exit("정지 이미지 이름이 숫자로 끝나면 Loader가 이미지 시퀀스로 읽음. 이름을 바꿀 것(예: card01_frame.png): " + ", ".join(bad))


def reload_comp(item, path):
  """API로 만든 comp는 Fusion에서는 보여도 Edit 합성·Deliver 렌더에는 빈 캔버스로 나왔다(21.1.1 실측).
  .comp로 내보냈다 다시 들이면 반영된다. 들인 comp 하나만 남긴다."""
  if not item.ExportFusionComp(str(path), 1):
    sys.exit("ExportFusionComp 실패")
  item.ImportFusionComp(str(path))
  for name in item.GetFusionCompNameList()[:-1]:
    item.DeleteFusionCompByName(name)


def build(plan_path):
  plan = json.loads(Path(plan_path).read_text())
  check_names(plan)
  resolve, project, timeline, fps = open_work(plan)
  track, item = place(project, timeline, plan, fps)
  comp = item.AddFusionComp()
  made = build_comp(comp, plan, fps)
  reload_comp(item, Path(plan_path).with_suffix(f".{item.GetStart()}.comp").resolve())
  resolve.GetProjectManager().SaveProject()
  print(json.dumps({"timeline": timeline.GetName(), "track": track, "track_name": timeline.GetTrackName("video", track),
                    "start": item.GetStart(), "end": item.GetEnd(), "frames": item.GetDuration(), "nodes": made}, ensure_ascii=False))


# ---------- title 모드: Fusion 타이틀 + Template 매크로 ----------

def timecode(frame, fps):
  """절대 프레임 → HH:MM:SS:FF. ponytail: non-drop만. 29.97 DF 타임라인이면 SetCurrentTimecode 위치가 어긋난다"""
  n = round(fps)
  s, f = divmod(frame, n)
  return f"{s // 3600:02d}:{s // 60 % 60:02d}:{s % 60:02d}:{f:02d}"


def lua(value):
  return json.dumps(value, ensure_ascii=False) if isinstance(value, str) else f"{value:g}" if isinstance(value, float) else str(value)


def template_inputs(plan):
  """Edit Inspector에 공개할 InstanceInput 줄. Default는 plan 값이라 Inspector 되돌리기가 원래 자리로 간다."""
  rows, group = [], 0

  def inp(op, source, name=None, **extra):
    fields = {"SourceOp": op, "Source": source, **({"Name": name} if name else {}), **extra}
    rows.append("InstanceInput { " + ", ".join(f"{k} = {lua(v)}" for k, v in fields.items()) + " }")

  for mark in plan.get("marks", []):
    mid, (x, y, w, h) = mark["id"], mark["rect"]
    group += 1
    color = color_inputs(mark["color"], mark.get("alpha", 1.0))
    for i, channel in enumerate(("Red", "Green", "Blue", "Alpha")):
      inp(f"MARK_{mid}_COLOR", f"TopLeft{channel}", f"Mark {mid} Color" if i == 0 else None, ControlGroup=group,
          Default=round(color[f"TopLeft{channel}"], 4))
    center = norm(x + w / 2, y + h / 2)
    inp(f"MARK_{mid}_SHAPE", "Center", f"Mark {mid} Position", DefaultX=round(center[1], 4), DefaultY=round(center[2], 4))
    inp(f"MARK_{mid}_SHAPE", "Width", f"Mark {mid} Width", Default=round(w / W, 4))
    inp(f"MARK_{mid}_SHAPE", "Height", f"Mark {mid} Height", Default=round(h / H, 4))
  for card in plan["cards"]:
    inp(f"CARD_{card['id']}_LAYOUT", "Center", f"Card {card['id']} Position", DefaultX=0.5, DefaultY=0.5)
    inp(f"CARD_{card['id']}_LAYOUT", "Size", f"Card {card['id']} Size", Default=1)
  for call in plan.get("callouts", []):
    pos = norm(*call["pos"])
    inp(f"CALLOUT_{call['id']}_LABEL", "StyledText", f"Callout {call['id']} Text")
    inp(f"CALLOUT_{call['id']}_LABEL", "Center", f"Callout {call['id']} Position", DefaultX=round(pos[1], 4), DefaultY=round(pos[2], 4))
  return [f"Input{i} = {row}" for i, row in enumerate(rows, 1)]


GENERATORS = ("Background", "TextPlus")


def wrap_template(text, plan):
  """ExportFusionComp 텍스트의 MediaOut1·Loader 밖 노드를 모두 Template 매크로로 감싼다. Fusion이 쓰는 들여쓰기(최상위 툴 = 탭 2개)에 기댄다.
  화면 녹화 Loader를 매크로 안에 넣으면 Deliver 렌더가 실패하고 MediaOut1 연결이 끊겼다(21.1.1 실측). Loader는 comp 최상위에 둔다.
  생성기의 GlobalIn/GlobalOut은 지운다. 남기면 Edit에서 클립 끝을 늘렸을 때 그 프레임에서 잘린다."""
  head, rest = re.split(r"^\tTools = (?:ordered\(\) )?\{\n", text, maxsplit=1, flags=re.M)
  close = re.search(r"^\t\},?$", rest, re.M)
  body, tail = rest[:close.start()], rest[close.start():]
  inner, outside, media_out = [], [], None
  for block in re.finditer(r"^\t\t(\w+) = (\w+) \{\n.*?^\t\t\},?$", body, re.M | re.S):
    name, kind, chunk = block.group(1), block.group(2), block.group(0).rstrip(",")
    if name == "MediaOut1":
      media_out = chunk
      continue
    if kind == "Loader":
      outside.append(chunk)
      continue
    if kind in GENERATORS:
      chunk = re.sub(r"^\t+Global(?:In|Out) = Input \{ Value = [-\d.]+, \},?\n", "", chunk, flags=re.M)
    inner.append("\n".join("\t\t" + line for line in chunk.split("\n")))
  if not media_out or not inner:
    sys.exit("comp에서 MediaOut1이나 노드를 찾지 못함: ExportFusionComp 텍스트 형식이 다름")
  inputs = ",\n".join("\t\t\t\t" + row for row in template_inputs(plan))
  macro = ("\t\tTemplate = MacroOperator {\n\t\t\tCtrlWZoom = false,\n\t\t\tInputs = ordered() {\n" + inputs + "\n\t\t\t},\n"
           '\t\t\tOutputs = { MainOutput1 = InstanceOutput { SourceOp = "CAMERA", Source = "Output" } },\n'
           "\t\t\tViewInfo = GroupInfo { Pos = { 0, 0 } },\n\t\t\tTools = ordered() {\n" + ",\n".join(inner) + "\n\t\t\t},\n\t\t},\n")
  return head + "\tTools = ordered() {\n" + "".join(c + ",\n" for c in outside) + macro + media_out + "\n" + tail


@contextmanager
def generator_frames(resolve, frames, folder):
  """환경설정 Standard generator duration을 frames로 잠시 바꾼다. 타이틀은 이 길이로만 삽입된다.
  원래 설정은 프리셋으로 저장·파일로 내보내고 restore.json에 경로를 남긴다. finally에서 되돌린 뒤 실제 값이 돌아왔는지 대조한다."""
  folder.mkdir(parents=True, exist_ok=True)
  tag = f"akbun_cards_{os.getpid()}_{int(time.time())}"
  orig, temp, check = (f"{tag}_{k}" for k in ("orig", "temp", "check"))
  orig_file, temp_file, check_file = (folder / f"{n}.preset" for n in (orig, temp, check))
  if not (resolve.SaveUserPreferencesPreset(orig) and resolve.ExportUserPreferencesPreset(orig, str(orig_file))):
    sys.exit("환경설정 프리셋 저장 실패: 길이를 바꾸지 않음")
  original = orig_file.read_text()
  keys = ("GeneratorDurationType", "GeneratorDurationFrames", "GeneratorDurationSecs")
  before = {k: re.search(f"<{k}>(.*?)</{k}>", original).group(1) for k in keys}
  (folder / "restore.json").write_text(json.dumps({"preset": orig, "file": str(orig_file), "before": before}, ensure_ascii=False))
  changed = re.sub(r"<GeneratorDurationType>.*?</GeneratorDurationType>", "<GeneratorDurationType>DURATION_IN_FRAMES</GeneratorDurationType>", original)
  temp_file.write_text(re.sub(r"<GeneratorDurationFrames>.*?</GeneratorDurationFrames>", f"<GeneratorDurationFrames>{frames}</GeneratorDurationFrames>", changed))
  if not (resolve.ImportUserPreferencesPreset(str(temp_file), temp) and resolve.LoadUserPreferencesPreset(temp)):
    resolve.DeleteUserPreferencesPreset(temp)
    resolve.DeleteUserPreferencesPreset(orig)
    sys.exit("임시 환경설정 적용 실패: 원래 설정 그대로")
  try:
    yield
  finally:
    resolve.LoadUserPreferencesPreset(orig)
    resolve.SaveUserPreferencesPreset(check)
    resolve.ExportUserPreferencesPreset(check, str(check_file))
    after = {k: re.search(f"<{k}>(.*?)</{k}>", check_file.read_text()).group(1) for k in keys}
    for name in (temp, check):
      resolve.DeleteUserPreferencesPreset(name)
    if after != before:
      sys.exit(f"환경설정 길이가 돌아오지 않음 {after} ≠ {before}. Resolve에서 프리셋 {orig}(파일 {orig_file})를 불러올 것")
    resolve.DeleteUserPreferencesPreset(orig)


def title_timeline(project, plan):
  name = plan.get("title_timeline") or f"{plan['work_timeline']}_titles"
  timeline = find_timeline(project, name) or project.GetMediaPool().CreateEmptyTimeline(name)
  if not timeline:
    sys.exit(f"장면 타임라인 {name}을 만들지 못함")
  project.SetCurrentTimeline(timeline)
  return timeline


def title_item(timeline, name):
  return next((i for i in timeline.GetItemListInTrack("video", 1) or [] if i.GetName() == name), None)


def build_title(plan_path):
  """장면 전용 타임라인 V1 끝에 Text+ 타이틀을 붙이고 노드를 다시 짠다. InsertFusionTitleIntoTimeline은 재생 헤드의 V1에 끼워 넣어
  뒤 클립·마커를 민다(21.1.1 실측 90프레임). 그래서 본편이 없는 장면 타임라인의 끝에만 붙인다."""
  plan = json.loads(Path(plan_path).read_text())
  check_names(plan)
  resolve = connect()
  project = resolve.GetProjectManager().GetCurrentProject()
  fps = float(project.GetSetting("timelineFrameRate"))
  if abs(fps - plan["fps"]) > 1e-3:
    sys.exit(f"타임라인 fps {fps}와 plan fps {plan['fps']}가 다름")
  resolve.OpenPage("edit")
  timeline = title_timeline(project, plan)
  name = Path(plan_path).stem
  if title_item(timeline, name):
    sys.exit(f"{timeline.GetName()}에 {name} 클립이 이미 있음. 지우고 다시 빌드할 것")
  frames = round(plan["duration"] * fps)
  clips = [i for i in timeline.GetItemListInTrack("video", 1) or [] if i.GetType() != "transition"]
  end = max([i.GetEnd() for i in clips], default=timeline.GetStartFrame())
  markers = timeline.GetMarkers()
  timeline.SetCurrentTimecode(timecode(end, fps))
  with generator_frames(resolve, frames, Path(plan_path).resolve().parent / "prefs"):
    item = timeline.InsertFusionTitleIntoTimeline("Text+")
  if not item:
    sys.exit("InsertFusionTitleIntoTimeline 실패: Edit 페이지인지, 열린 대화상자가 있는지 확인")
  if (item.GetStart(), item.GetDuration()) != (end, frames) or timeline.GetMarkers() != markers:
    sys.exit(f"타이틀 위치 불일치: 요청 {end}+{frames}, 실제 {item.GetStart()}+{item.GetDuration()}. 장면 타임라인을 확인할 것")
  item.SetName(name)
  made = build_comp(item.GetFusionCompByIndex(1), plan, fps)
  path = Path(plan_path).with_suffix(f".{item.GetStart()}.comp").resolve()
  if not item.ExportFusionComp(str(path), 1):
    sys.exit("ExportFusionComp 실패")
  wrapped = path.with_suffix(".template.comp")
  wrapped.write_text(wrap_template(path.read_text(), plan))
  item.ImportFusionComp(str(wrapped))
  for old in item.GetFusionCompNameList()[:-1]:
    item.DeleteFusionCompByName(old)
  resolve.GetProjectManager().SaveProject()
  print(json.dumps({"timeline": timeline.GetName(), "clip": name, "start": item.GetStart(), "end": item.GetEnd(), "frames": item.GetDuration(),
                    "comp": str(wrapped), "inspector": [r.split('Name = "')[1].split('"')[0] for r in template_inputs(plan) if "Name =" in r],
                    "nodes": made}, ensure_ascii=False))


def retime(plan_path, old_at):
  """녹음 뒤 시각만 다시 맞춘다. 위치나 길이가 바뀌면 comp를 .comp로 내보내고 클립을 새 자리에 놓은 뒤 다시 들인다."""
  plan = json.loads(Path(plan_path).read_text())
  resolve, project, timeline, fps = open_work(plan)
  track, item = own_clip(timeline, plan, old_at, fps)
  if not item:
    sys.exit(f"{old_at}초에 {plan['track_name']} 클립 없음")
  moved = item.GetStart() != timeline.GetStartFrame() + round(plan["at"] * fps) or item.GetDuration() != round(plan["duration"] * fps)
  if moved:
    backup = Path(plan_path).with_suffix(f".{item.GetStart()}.comp").resolve()
    if not item.ExportFusionComp(str(backup), 1):
      sys.exit("ExportFusionComp 실패: 클립을 지우지 않음")
    timeline.DeleteClips([item], False)
    track, item = place(project, timeline, plan, fps, track)
    item.ImportFusionComp(str(backup))
    for name in item.GetFusionCompNameList()[:-1]:  # 새 캔버스 클립의 빈 기본 comp는 지우고 들여온 comp만 남긴다
      item.DeleteFusionCompByName(name)
  comp = item.GetFusionCompByIndex(1)
  comp.Lock()
  apply_timing(comp, plan, fps)
  comp.Unlock()
  reload_comp(item, Path(plan_path).with_suffix(f".{item.GetStart()}.timed.comp").resolve())
  resolve.GetProjectManager().SaveProject()
  print(json.dumps({"track": track, "start": item.GetStart(), "frames": item.GetDuration(), "moved": moved,
                    "comps": item.GetFusionCompNameList()}))


def grab(plan_path, frames, out, tool_name=None):
  """검증 프레임을 뽑는다. 기본은 Deliver 렌더 잡으로 클립 구간을 960×540 MP4로 한 번 렌더한 뒤 ffmpeg로 프레임을 꺼낸다
  (타임라인에 실제로 합성된 화면이다). Deliver 형식·코덱은 끝나면 되돌리고 자기 렌더 잡은 지운다.
  tool_name을 주면 그 Fusion 노드 출력을 Saver로 한 프레임씩 렌더한다. 21.1.1에서 이 방식은 렌더마다 'Render completed!'
  창을 남기고, 그 창이 열려 있는 동안 AppendToTimeline 같은 편집 API가 None을 돌려준다."""
  plan = json.loads(Path(plan_path).read_text())
  if plan.get("mode") == "title":
    resolve = connect()
    project = resolve.GetProjectManager().GetCurrentProject()
    item = title_item(title_timeline(project, plan), Path(plan_path).stem)
  else:
    resolve, project, timeline, fps = open_work(plan)
    _, item = own_clip(timeline, plan, plan["at"], fps)
  if not item:
    sys.exit("plan 위치에 클립 없음")
  out = Path(out).resolve()
  out.mkdir(parents=True, exist_ok=True)
  name = tool_name or "TIMELINE"
  if tool_name:
    comp = item.GetFusionCompByIndex(1)
    attrs = comp.GetAttrs()
    keep = {"COMPN_RenderStart": attrs["COMPN_RenderStart"], "COMPN_RenderEnd": attrs["COMPN_RenderEnd"]}
    saver = comp.AddTool("Saver", -10, -10)
    saver.ConnectInput("Input", comp.FindTool(tool_name))
    saver.SetInput("Clip", str(out / f"{name}_.png"))
    saver.SetInput("OutputFormat", "PNGFormat")
    try:
      for frame in frames:
        comp.Render({"Start": frame, "End": frame, "Wait": True})
    finally:
      saver.Delete()
      comp.SetAttrs(keep)
    print("Fusion 'Render completed!' 창이", len(frames), "개 남음. 다음 편집 전에 닫을 것", file=sys.stderr)
  else:
    import time
    keep = project.GetCurrentRenderFormatAndCodec()
    project.SetCurrentRenderFormatAndCodec("mp4", "H264")
    project.SetRenderSettings({"SelectAllFrames": False, "MarkIn": item.GetStart(), "MarkOut": item.GetEnd() - 1, "TargetDir": str(out),
                               "CustomName": "grab", "FormatWidth": 960, "FormatHeight": 540, "ExportVideo": True, "ExportAudio": False})
    job = project.AddRenderJob()
    try:
      project.StartRendering([job], False)
      began = time.time()
      while project.IsRenderingInProgress() and time.time() - began < 600:
        time.sleep(1)
      status = project.GetRenderJobStatus(job)
    finally:
      project.DeleteRenderJob(job)
      if keep:
        project.SetCurrentRenderFormatAndCodec(keep["format"], keep["codec"])
    video = out / "grab.mp4"
    if status.get("JobStatus") != "Complete" or not video.exists():
      sys.exit(f"Deliver 렌더 실패: {status}")
    for frame in frames:
      subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", f"select=eq(n\\,{frame})", "-frames:v", "1",
                      str(out / f"{name}_{frame:04d}.png")], check=True)
  files = [out / f"{name}_{f:04d}.png" for f in frames]
  found = [f for f in files if f.exists()]
  cols = {1: 1, 2: 2, 3: 3, 4: 2}.get(len(found), 3 if len(found) <= 6 else 4)
  sheet = out / f"sheet_{name}.jpg"
  if found:
    graph = ("".join(f"[{i}]scale=640:360[s{i}];" for i in range(len(found))) + "".join(f"[s{i}]" for i in range(len(found)))
             + f"xstack=inputs={len(found)}:fill=white:layout=" + "|".join(f"{(i % cols) * 640}_{(i // cols) * 360}" for i in range(len(found)))
             if len(found) > 1 else "[0]scale=640:360")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *sum([["-i", str(f)] for f in found], []), "-filter_complex", graph,
                    "-frames:v", "1", str(sheet)], check=True)
  print(json.dumps({"files": [str(f) for f in found], "missing": [str(f) for f in files if not f.exists()], "sheet": str(sheet)}))


def selftest():
  curves = camera_keys([{"at": 0}, {"at": 1, "zoom": 2, "x": 480, "y": 270}, {"at": 3, "zoom": 2.2, "ease": "linear"}], 30)
  assert curves["size"][30][1] == 2 and abs(curves["cx"][30][1] - (0.5 + 0.25 * 2)) < 1e-9, "P(480,270)을 가운데로: Center X = 0.5 + 0.25 × 2"
  assert abs(curves["cy"][30][1] - (0.5 + (0.5 - 0.75) * 2)) < 1e-9, "y는 아래 원점: 1 - 270/1080 = 0.75"
  assert curves["size"][0]["RH"] == {1: 10.0, 2: 0.0}, "ease-in-out: 손잡이가 수평"
  assert abs(curves["size"][30]["RH"][2] - 0.2 / 3) < 1e-9 and curves["size"][90]["LH"][2] != 0, "linear: 손잡이가 기울기를 따름"
  assert ramp(2, 0.5, 30) == "min(1, max(0, (time - 60) / 15))" and "RenderStart" not in ramp(0, 1, 30)
  assert norm(960, 270) == {1: 0.5, 2: 0.75}
  card = {"content": [240, 115, 1440, 914], "crop": [0, 120, 2880, 0]}
  assert placement(card) == (0.5, 1828.0), "2배 스크린샷은 0.5배로 줄여 content를 채움"
  assert where(card, [240, 1240, 1760, 64]) == [360.0, 675.0, 880.0, 32.0]
  x, y, w, h = frame_content(100, 100, 800, 600)
  assert (y, h) == (100 + BAR + 1, 600 - BAR - 2)
  assert "#1B2224" in frame_svg(0, 0, 400, 300, "dark", "")
  try:
    check_names({"cards": [{"frame": "a/q_frame01.png", "shot": "a/rec.mov"}]})
    raise AssertionError("숫자로 끝나는 정지 이미지 이름을 막아야 함")
  except SystemExit:
    pass
  check_names({"cards": [{"frame": "a/card01_frame.png", "shot": "a/take01.mov"}]})
  assert timecode(108000 + 61, 30) == "01:00:02:01"
  plan = {"cards": [{"id": "01"}], "marks": [{"id": "01", "rect": [960, 540, 192, 108], "color": "#FFFFFF"}],
          "callouts": [{"id": "01", "pos": [960, 270]}]}
  comp = ("Composition {\n\tTools = {\n\t\tCANVAS = Background {\n\t\t\tInputs = {\n\t\t\t\tGlobalOut = Input { Value = 89, },\n"
          "\t\t\t\tWidth = Input { Value = 1920, }\n\t\t\t},\n\t\t},\n\t\tSHOT_01 = Loader {\n\t\t},\n\t\tCAMERA = Transform {\n\t\t},\n"
          "\t\tMediaOut1 = Saver {\n\t\t\tInputs = { Input = Input { SourceOp = \"CAMERA\", Source = \"Output\", } },\n\t\t}\n\t},\n}\n")
  wrapped = wrap_template(comp, plan)
  assert "GlobalOut" not in wrapped and wrapped.count("MediaOut1") == 1 and "\t\t\t\tCAMERA = Transform" in wrapped
  assert wrapped.index("Template = MacroOperator") < wrapped.index("MediaOut1") and 'SourceOp = "CAMERA"' in wrapped
  assert wrapped.index("\t\tSHOT_01 = Loader") < wrapped.index("Template = MacroOperator"), "Loader는 매크로 밖"
  names = [r for r in template_inputs(plan) if "Name =" in r]
  assert ['Mark 01 Color', 'Mark 01 Position', 'Mark 01 Width', 'Mark 01 Height', 'Card 01 Position', 'Card 01 Size', 'Callout 01 Text',
          'Callout 01 Position'] == [r.split('Name = "')[1].split('"')[0] for r in names]
  assert "DefaultX = 0.55, DefaultY = 0.45" in names[1] and "Default = 0.1" in names[2]
  print("selftest ok")


def main():
  parser = argparse.ArgumentParser()
  sub = parser.add_subparsers(dest="cmd")
  p = sub.add_parser("frame")
  p.add_argument("--rect", required=True)
  p.add_argument("--theme", choices=THEMES, default="light")
  p.add_argument("--title", default="")
  p.add_argument("--out", required=True)
  p = sub.add_parser("arrow")
  p.add_argument("--start", required=True)
  p.add_argument("--end", required=True)
  p.add_argument("--color", default="#FFD84D")
  p.add_argument("--out", required=True)
  p = sub.add_parser("canvas")
  p.add_argument("--fps", type=float, required=True)
  p.add_argument("--seconds", type=float, default=60)
  p.add_argument("--color", default="#EAEAEA")
  p.add_argument("--out", required=True)
  p = sub.add_parser("where")
  p.add_argument("plan")
  p.add_argument("--card", required=True)
  p.add_argument("--rect", required=True, help="스크린샷 픽셀 x,y,w,h")
  p = sub.add_parser("build")
  p.add_argument("plan")
  p = sub.add_parser("retime")
  p.add_argument("plan")
  p.add_argument("--old-at", type=float, required=True, help="지금 클립이 놓인 초(바꾸기 전 plan의 at)")
  p = sub.add_parser("grab")
  p.add_argument("plan")
  p.add_argument("--frames", required=True)
  p.add_argument("--out", required=True)
  p.add_argument("--tool", help="이 Fusion 노드 출력을 뽑는다(렌더 완료 창이 남음). 없으면 Deliver로 타임라인 화면을 뽑는다")
  parser.add_argument("--selftest", action="store_true")
  args = parser.parse_args()
  if args.selftest:
    return selftest()
  if args.cmd == "frame":
    x, y, w, h = (float(v) for v in args.rect.split(","))
    write_png(frame_svg(x, y, w, h, args.theme, args.title), args.out)
    print(json.dumps({"frame": args.out, "window": [x, y, w, h], "content": frame_content(x, y, w, h)}))
  elif args.cmd == "arrow":
    write_png(arrow_svg([float(v) for v in args.start.split(",")], [float(v) for v in args.end.split(",")], args.color), args.out)
    print(args.out)
  elif args.cmd == "canvas":
    canvas(args.fps, args.seconds, args.color, args.out)
    print(args.out)
  elif args.cmd == "where":
    plan = json.loads(Path(args.plan).read_text())
    card = next(c for c in plan["cards"] if c["id"] == args.card)
    print(json.dumps(where(card, [float(v) for v in args.rect.split(",")])))
  elif args.cmd == "build":
    build_title(args.plan) if json.loads(Path(args.plan).read_text()).get("mode") == "title" else build(args.plan)
  elif args.cmd == "retime":
    retime(args.plan, args.old_at)
  elif args.cmd == "grab":
    grab(args.plan, [int(f) for f in args.frames.split(",")], args.out, args.tool)
  else:
    parser.print_help()


if __name__ == "__main__":
  main()
