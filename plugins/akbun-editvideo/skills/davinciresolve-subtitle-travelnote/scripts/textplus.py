#!/usr/bin/env python3
"""Text+ 자막을 이름으로 찾은 비디오 트랙(기본 SUBTITLE)에 일반 Text+ 클립 하나로 놓는다. 다른 트랙의 클립, 타임라인 마커, 타임라인 길이는 바뀌지 않는다.
DaVinci Resolve 21.1 외부 스크립팅 API만 쓴다.

 python3 textplus.py place --timeline B --at TC --seconds N --text "문구" --font "Gmarket Sans" --style Medium --size 0.12
              [--x 0.5] [--y 0.5] [--set 입력=값 ...] [--track SUBTITLE] [--template HOOK_TEXT_TEMPLATE] [--out DIR]
 python3 textplus.py remove --timeline B --at TC [--track SUBTITLE]
 python3 textplus.py selftest

InsertFusionTitleIntoTimeline("Text+")은 항상 V1의 재생헤드에 끼워 넣는다(21.1 실측). 재생헤드 아래 V1 클립을 자르고
잠기지 않은 모든 트랙과 타임라인 마커를 타이틀 길이만큼 뒤로 민다. V1이 잠겨 있으면 아무것도 돌려주지 않는다. 트랙을 고르는 API는 없다.
그래서 place는 미디어 풀의 Fusion Title 항목(--template)을 대상 트랙의 원하는 위치와 길이로 놓고 글자 값을 넣는다.
놓는 함수는 이 스크립트의 put_text다. 컴파운드 클립을 만들지 않으므로 놓인 자막은 Inspector에서 바로 고친다.
remove는 대상 트랙에서 --at에 시작하는 클립을 지운다. 컷 변경 뒤 다시 놓을 때 쓴다.
페이드는 넣지 않는다. TimelineItem.SetFades로 건 값은 프로젝트를 닫았다 열면 0으로 돌아온다(21.1 실측).
"""
import argparse
import datetime as dt
import os
import sys
import time
import re


TRACK = "SUBTITLE"
TEXT_TEMPLATE = "HOOK_TEXT_TEMPLATE"
KINDS = ("video", "audio", "subtitle")


def tc_to_frame(tc, fps):
  m = re.fullmatch(r"(\d{2}):(\d{2}):(\d{2}):(\d{2})", tc.strip())
  if not m:
    raise ValueError("타임코드 형식은 HH:MM:SS:FF (drop-frame ';' 미지원): " + tc)
  h, mi, s, f = map(int, m.groups())
  if mi > 59 or s > 59 or f >= fps:
    raise ValueError("타임코드 범위 오류: " + tc)
  return ((h * 60 + mi) * 60 + s) * fps + f


def frame_to_tc(frame, fps):
  s, f = divmod(frame, fps)
  return "%02d:%02d:%02d:%02d" % (s // 3600, s // 60 % 60, s % 60, f)


def clash(start, frames, clips):
  """[start, start+frames)와 겹치는 기존 클립 [(시작, 길이)]. 끝 프레임은 포함하지 않으므로 맞닿은 클립은 겹치지 않는다."""
  return [(s, d) for s, d in clips if s < start + frames and start < s + d]


def connect():
  api = os.environ.setdefault("RESOLVE_SCRIPT_API", "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting")
  os.environ.setdefault("RESOLVE_SCRIPT_LIB", "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so")
  sys.path.append(os.path.join(api, "Modules"))
  import DaVinciResolveScript as dvr
  resolve = dvr.scriptapp("Resolve")
  if not resolve:
    sys.exit("Resolve에 연결 못 함: Resolve Studio 실행, External scripting=Local, 환경변수 확인")
  return resolve, resolve.GetProjectManager().GetCurrentProject()


def find_timeline(project, name):
  for i in range(1, project.GetTimelineCount() + 1):
    tl = project.GetTimelineByIndex(i)
    if tl.GetName() == name:
      return tl
  return None


def open_source(project, name):
  tl = find_timeline(project, name)
  if not tl:
    sys.exit("타임라인 없음: " + name)
  if str(tl.GetSetting("timelineDropFrameTimecode")) == "1":
    sys.exit("drop-frame 타임코드 타임라인은 지원하지 않음: " + name)
  fps = round(float(tl.GetSetting("timelineFrameRate")))
  return tl, fps, tl.GetEndFrame() - tl.GetStartFrame()


def layout(tl):
  """{(종류, 트랙 번호): [(시작, 길이)]}. 시작은 타임라인 첫 프레임 기준."""
  o = tl.GetStartFrame()
  return {(k, t): [(it.GetStart() - o, it.GetDuration()) for it in (tl.GetItemListInTrack(k, t) or [])]
      for k in KINDS for t in range(1, tl.GetTrackCount(k) + 1)}


def write_log(out, prefix, stamp, text):
  print(text)
  if out:
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "%s_%s.md" % (prefix, stamp))
    open(path, "w").write(text)
    print("로그:", path)


def named_track(tl, kind, name):
  """이름이 name인 트랙 번호. 없으면 새로 만들어 이름을 붙인다(비디오는 맨 위, 오디오는 맨 아래)."""
  for t in range(1, tl.GetTrackCount(kind) + 1):
    if tl.GetTrackName(kind, t) == name:
      return t
  if not (tl.AddTrack(kind, "stereo") if kind == "audio" else tl.AddTrack(kind)):
    sys.exit("트랙 추가 실패: " + name)
  t = tl.GetTrackCount(kind)
  tl.SetTrackName(kind, t, name)
  return t


def pool_clips(mp):
  """미디어 풀의 모든 항목(하위 bin 포함). 타임라인과 컴파운드 클립도 항목이다."""
  stack, clips = [mp.GetRootFolder()], []
  while stack:
    folder = stack.pop()
    clips += folder.GetClipList() or []
    stack += folder.GetSubFolderList() or []
  return clips


def same_value(got, want):
  return abs(got - want) < 1e-6 if isinstance(want, float) and isinstance(got, (int, float)) else got == want


def put_text(resolve, project, tl, fps, track_name, template, at, frames, inputs):
  """미디어 풀의 Fusion Title 항목 template을 이름이 track_name인 비디오 트랙의 at 프레임에 frames 길이의 일반 Text+ 클립 하나로 놓고
  inputs [(Text+ 입력 이름, 값)]를 넣는다. Font와 Style은 꼭 있어야 한다. -> {track, kept, added}. 놓을 수 없으면 타임라인을 바꾸지 않고 종료한다."""
  origin, end, tc, want = tl.GetStartFrame(), tl.GetEndFrame(), frame_to_tc(at, fps), dict(inputs)
  if not origin <= at < at + frames <= end or frames <= 0:
    sys.exit("텍스트 구간이 타임라인 밖: %s + %.1f초" % (tc, frames / fps))
  # Text+는 없는 글꼴 이름도 그대로 받아들이고 다른 글꼴로 그리므로(21.1 실측) Resolve의 글꼴 목록으로 확인한다
  styles = list(((resolve.Fusion().FontManager.GetFontList() or {}).get(want["Font"]) or {}).keys())
  if want["Style"] not in styles:
    sys.exit("Resolve에 글꼴 없음: %s %s (있는 굵기: %s). 설치한 뒤 Resolve를 다시 열고 실행한다" % (want["Font"], want["Style"], ", ".join(styles) or "없음"))
  # API에는 트랙과 위치를 정해 Text+를 새로 만드는 함수가 없다(InsertFusionTitleIntoTimeline은 재생헤드에 끼워 넣어 뒤와 마커를 민다, 21.1 실측).
  # 미디어 풀의 Fusion Title 항목은 AppendToTimeline으로 트랙·위치·길이를 정해 놓을 수 있고, 놓인 것은 항목과 이어지지 않은 일반 Text+다.
  mp = project.GetMediaPool()
  pool = pool_clips(mp)
  source = next((c for c in pool if c.GetName() == template and c.GetClipProperty("Type") == "Fusion Title"), None)
  if not source:
    sys.exit("미디어 풀에 Fusion Title 항목 `%s`이 없음. API로는 만들 수 없으니 davinciresolve-subtitle-travelnote SKILL.md의 'Text+ 템플릿 준비' 절차를 Resolve 화면에서 한 번 한 뒤 다시 실행한다" % template)
  project.SetCurrentTimeline(tl)
  resolve.OpenPage("edit")
  track = named_track(tl, "video", track_name)
  if tl.GetIsTrackLocked("video", track):
    sys.exit("%s 트랙(V%d)이 잠겨 있음. 잠금을 풀고 다시 실행한다" % (track_name, track))
  before, marks = layout(tl), tl.GetMarkers()
  hit = clash(at - origin, frames, before[("video", track)])
  if hit:
    sys.exit("충돌: %s 트랙(V%d)에 이미 클립이 있어 놓지 않음. 요청 %s + %.1f초, 기존 %s. 기존 클립은 그대로다" % (
      track_name, track, tc, frames / fps, ", ".join("%s~%s" % (frame_to_tc(origin + s, fps), frame_to_tc(origin + s + d, fps)) for s, d in hit)))
  got = mp.AppendToTimeline([{"mediaPoolItem": source, "trackIndex": track, "recordFrame": at, "startFrame": 0, "endFrame": frames, "mediaType": 1}])
  clip = got[0] if got and got[0] and got[0].GetStart() is not None else None
  if not clip:
    sys.exit("Text+ 배치 실패: V%d %s. 타임라인은 바뀌지 않음" % (track, tc))
  comp = clip.GetFusionCompByIndex(1) if clip.GetFusionCompCount() == 1 and not clip.GetMediaPoolItem() else None
  tool = comp and next((t for t in comp.GetToolList(False).values() if t.GetAttrs()["TOOLS_RegID"] == "TextPlus"), None)
  if not tool:
    sys.exit("놓인 클립이 일반 Text+가 아님. `%s` 항목이 Text+로 만든 것인지 확인한다. 놓인 클립: V%d %s" % (template, track, tc))
  for key, value in inputs:
    tool.SetInput(key, value)
  # 없는 입력 이름은 조용히 무시되므로 되읽어 확인한다. 표로 받는 Center는 빼고 본다
  wrong = [k for k, v in inputs if not isinstance(v, dict) and not same_value(tool.GetInput(k), v)]
  if wrong:
    # 핸들은 지우기 직전에 다시 읽는다(오래된 핸들로 지우면 Resolve가 종료됨, 21.1 실측)
    gone = tl.DeleteClips([it for it in tl.GetItemListInTrack("video", track) if it.GetStart() == at], False)
    sys.exit("Text+ 입력이 들어가지 않음: %s. 놓은 클립은 %s" % (", ".join(wrong), "지움" if gone else "V%d %s에 남음" % (track, tc)))
  clip.SetName("Text+")
  expect = dict(before)
  expect[("video", track)] = sorted(before[("video", track)] + [(at - origin, frames)])
  kept = layout(tl) == expect and tl.GetMarkers() == marks and tl.GetEndFrame() == end
  return {"track": track, "kept": kept, "added": len(pool_clips(mp)) - len(pool)}


def text_inputs(text, font, style, size, x, y):
  return [("StyledText", text.replace("\\n", "\n")), ("Font", font), ("Style", style), ("Size", size), ("Center", {1: x, 2: y})]


def parse_set(pairs):
  """["LineSpacing=1.2", "Font=Pretendard"] -> [("LineSpacing", 1.2), ("Font", "Pretendard")]. 숫자로 읽히면 숫자."""
  out = []
  for p in pairs:
    key, sep, value = p.partition("=")
    if not sep or not key:
      raise ValueError("--set 형식은 입력=값: " + p)
    try:
      value = float(value)
    except ValueError:
      pass
    out.append((key, value))
  return out


def open_timeline(a):
  resolve, project = connect()
  tl, fps, _ = open_source(project, a.timeline)
  try:
    at = tc_to_frame(a.at, fps)
  except ValueError as e:
    sys.exit(str(e))
  project.SetCurrentTimeline(tl)
  resolve.OpenPage("edit")
  return resolve, project, tl, fps, at


def place(a, stamp):
  resolve, project, tl, fps, at = open_timeline(a)
  frames = round(a.seconds * fps)
  try:
    inputs = text_inputs(a.text, a.font, a.style, a.size, a.x, a.y) + parse_set(a.set)
  except ValueError as e:
    sys.exit(str(e))
  r = put_text(resolve, project, tl, fps, a.track, a.template, at, frames, inputs)
  still = "-"
  if a.out:
    os.makedirs(os.path.join(a.out, "subtitle-stills"), exist_ok=True)
    still = os.path.join(a.out, "subtitle-stills", "%s_%s.jpg" % (a.track, a.at.replace(":", "_")))
    resolve.OpenPage("color")
    tl.SetCurrentTimecode(frame_to_tc(at + frames // 2, fps))
    time.sleep(1)
    if not project.ExportCurrentFrameAsStill(still):
      still = "확인 필요: 스틸 내보내기 실패"
  ok = r["kept"] and not r["added"]
  L = ["## Text+ 배치", "", "| 타임라인 | 시작 TC | 종료 TC | 트랙 | 문구 | 글꼴 | Size | Center | 기존 클립·마커·타임라인 길이 | 새 미디어 풀 항목 | 스틸 | 결과 |",
    "|---|---|---|---|---|---|---|---|---|---|---|---|",
    "| %s | %s | %s | V%d %s | %s | %s %s | %s | %s, %s | %s | %s | %s | %s |" % (
      a.timeline, a.at, frame_to_tc(at + frames, fps), r["track"], a.track, a.text, a.font, a.style, a.size, a.x, a.y,
      "그대로" if r["kept"] else "확인 필요: 바뀜", "없음" if not r["added"] else "확인 필요: %+d" % r["added"], still, "적용" if ok else "확인 필요")]
  write_log(a.out, "textplus", stamp, "\n".join(L) + "\n")
  if not ok:
    sys.exit(1)


def remove(a, stamp):
  _, _, tl, fps, at = open_timeline(a)
  track = next((t for t in range(2, tl.GetTrackCount("video") + 1) if tl.GetTrackName("video", t) == a.track), None)
  if not track:
    sys.exit("%s 트랙 없음" % a.track)
  before, marks = layout(tl), tl.GetMarkers()
  # 핸들은 지우기 직전에 다시 읽는다(오래된 핸들로 지우면 Resolve가 종료됨, 21.1 실측)
  hit = [it for it in tl.GetItemListInTrack("video", track) or [] if it.GetStart() == at]
  if not hit:
    sys.exit("%s 트랙에 %s에서 시작하는 클립 없음" % (a.track, a.at))
  if not tl.DeleteClips(hit, False):
    sys.exit("삭제 실패: " + a.at)
  after = layout(tl)
  gone = [x for x in before[("video", track)] if x not in after[("video", track)]]
  kept = all(after[k] == v for k, v in before.items() if k != ("video", track)) and tl.GetMarkers() == marks
  print("%s V%d %s: %s 클립 %d개 삭제, 다른 트랙·마커 %s" % (a.timeline, track, a.track, a.at, len(gone), "그대로" if kept else "확인 필요: 바뀜"))
  if len(gone) != 1 or not kept:
    sys.exit(1)


def selftest():
  assert tc_to_frame("01:00:00:00", 24) == 86400
  assert frame_to_tc(86448, 24) == "01:00:02:00"
  assert frame_to_tc(tc_to_frame("00:59:59:29", 30), 30) == "00:59:59:29"
  assert clash(10, 5, [(5, 5), (15, 5)]) == []
  assert clash(10, 5, [(14, 2)]) == [(14, 2)]
  assert dict(text_inputs("a\\nb", "Pretendard", "Bold", 0.12, 0.5, 0.2))["StyledText"] == "a\nb"
  assert parse_set(["LineSpacing=1.2", "Font=Noto Sans KR", "Enabled2=1"]) == [("LineSpacing", 1.2), ("Font", "Noto Sans KR"), ("Enabled2", 1.0)]
  for bad in ("LineSpacing", "=1"):
    try:
      parse_set([bad])
    except ValueError:
      continue
    raise AssertionError("통과하면 안 되는 --set: " + bad)
  print("selftest ok")


def main():
  ap = argparse.ArgumentParser()
  sub = ap.add_subparsers(dest="cmd", required=True)
  p = sub.add_parser("place")
  p.add_argument("--timeline", required=True, help="작업 타임라인 이름")
  p.add_argument("--at", required=True, help="글자 시작 타임코드")
  p.add_argument("--seconds", type=float, required=True)
  p.add_argument("--text", required=True, help="문구. 줄바꿈은 \\n")
  p.add_argument("--font", required=True)
  p.add_argument("--style", required=True, help="글꼴 굵기 이름. 예: Medium, Bold")
  p.add_argument("--size", type=float, required=True)
  p.add_argument("--x", type=float, default=0.5, help="Text+ Center X. 0 왼쪽 끝, 1 오른쪽 끝")
  p.add_argument("--y", type=float, default=0.5, help="Text+ Center Y. 0 아래 끝, 1 위 끝")
  p.add_argument("--set", action="append", default=[], help="그 밖의 Text+ 입력. 입력=값, 반복 가능")
  p.add_argument("--track", default=TRACK, help="놓을 비디오 트랙 이름. 없으면 맨 위에 만든다")
  p.add_argument("--template", default=TEXT_TEMPLATE, help="미디어 풀의 Fusion Title 항목 이름")
  p.add_argument("--out", help="로그와 확인 스틸(subtitle-stills/)을 쓸 폴더(없으면 stdout만)")
  r = sub.add_parser("remove")
  r.add_argument("--timeline", required=True)
  r.add_argument("--at", required=True, help="지울 글자의 시작 타임코드")
  r.add_argument("--track", default=TRACK)
  sub.add_parser("selftest")
  a = ap.parse_args()
  stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
  {"place": place, "remove": remove}.get(a.cmd, lambda *_: selftest())(a, stamp)


if __name__ == "__main__":
  main()
