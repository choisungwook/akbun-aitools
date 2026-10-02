# /// script
# requires-python = ">=3.12"
# ///

import argparse
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path


def read_video(path):
  result = subprocess.run([
    "ffprobe", "-v", "error", "-select_streams", "v:0",
    "-show_entries", "format=duration:stream=width,height,avg_frame_rate",
    "-of", "json", str(path),
  ], check=True, capture_output=True, text=True)
  metadata = json.loads(result.stdout)
  if not metadata.get("streams"):
    raise ValueError("비디오 스트림이 없습니다")
  return metadata


def capture_frame(video, seconds, destination):
  subprocess.run([
    "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
    "-ss", f"{seconds:.6f}", "-i", str(video), "-map", "0:v:0",
    "-frames:v", "1", "-vf", "scale=min(1280\\,iw):-2",
    "-update", "1", str(destination),
  ], check=True, capture_output=True, text=True)
  if not destination.is_file() or destination.stat().st_size == 0:
    raise ValueError(f"{seconds:.6f}초에서 프레임을 얻지 못했습니다")


def capture_range(video, start, end, step, metadata):
  output = Path(tempfile.mkdtemp(prefix="article-overlay-", dir="/tmp"))
  frames = []
  count = math.floor((end - start) / step + 1e-9) + 1
  for index in range(count):
    seconds = start + index * step
    destination = output / f"frame-{index:04d}.png"
    capture_frame(video, seconds, destination)
    frames.append({"source_seconds": round(seconds, 6), "path": str(destination)})
  manifest = output / "frames.json"
  manifest.write_text(json.dumps({
    "source": str(video), "metadata": metadata, "frames": frames,
  }, ensure_ascii=False, indent=2) + "\n")
  return manifest


def main():
  parser = argparse.ArgumentParser(description="참고 영상 프레임을 /tmp에 캡처")
  parser.add_argument("video", type=Path)
  parser.add_argument("--start", type=float, required=True)
  parser.add_argument("--end", type=float, required=True)
  parser.add_argument("--step", type=float, default=1)
  args = parser.parse_args()
  if not all(math.isfinite(value) for value in (args.start, args.end, args.step)):
    parser.error("시간은 유한한 숫자여야 합니다")
  if args.start < 0 or args.end < args.start or args.step <= 0:
    parser.error("0 <= start <= end, step > 0이어야 합니다")
  video = args.video.expanduser().resolve()
  if not video.is_file():
    parser.error("영상 파일이 없습니다")
  for command in ("ffmpeg", "ffprobe"):
    if not shutil.which(command):
      parser.error(f"{command}가 필요합니다")
  try:
    metadata = read_video(video)
    duration = metadata.get("format", {}).get("duration")
    if duration is not None and args.end >= float(duration):
      raise ValueError("end는 영상 길이보다 작아야 합니다")
    manifest = capture_range(video, args.start, args.end, args.step, metadata)
  except (ValueError, OSError, subprocess.CalledProcessError) as error:
    parser.exit(1, f"캡처 실패: {error}\n")
  print(manifest.read_text(), end="")
  print(f"manifest: {manifest}")


if __name__ == "__main__":
  main()
