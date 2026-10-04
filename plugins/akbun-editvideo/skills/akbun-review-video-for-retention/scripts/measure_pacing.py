# /// script
# requires-python = ">=3.12"
# ///

"""Measure how often the picture changes in a rendered video.

Prints JSON: duration, every visual change time, changes per minute, changes in the first 60/120 s,
average shot length and every static stretch longer than --static seconds (longest first).
A change is a frame whose ffmpeg scene score is above --threshold. Slow fades and small reveals on
a dark slide score low, so a low count means "the viewer sees little change", which is the point.
"""

import argparse
import json
import re
import subprocess


def changes(path, threshold, fps):
  vf = f"fps={fps},scale=480:-2,select='gt(scene,{threshold})',showinfo"
  err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vf", vf, "-an", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
  return [float(t) for t in re.findall(r"pts_time:([\d.]+)", err)]


def duration(path):
  out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True).stdout
  return float(out)


def mmss(t):
  return "%d:%04.1f" % (t // 60, t % 60)


def main():
  p = argparse.ArgumentParser(description=__doc__)
  p.add_argument("video")
  p.add_argument("--threshold", type=float, default=0.01, help="ffmpeg scene score that counts as a change (dark slides 0.01, live footage 0.1-0.3)")
  p.add_argument("--fps", type=float, default=6, help="analysis frame rate")
  p.add_argument("--static", type=float, default=5.0, help="report stretches without change longer than this (s)")
  a = p.parse_args()
  total = duration(a.video)
  ts = changes(a.video, a.threshold, a.fps)
  edges = [0.0] + ts + [total]
  gaps = sorted(((edges[i + 1] - edges[i], edges[i]) for i in range(len(edges) - 1)), reverse=True)
  report = {
    "duration": mmss(total),
    "changes": len(ts),
    "changes_per_minute": round(len(ts) / (total / 60), 1),
    "changes_first_60s": sum(t < 60 for t in ts),
    "changes_first_120s": sum(t < 120 for t in ts),
    "average_shot_seconds": round(total / (len(ts) + 1), 1),
    "first_change": mmss(ts[0]) if ts else None,
    "static_stretches": [{"start": mmss(s), "seconds": round(g, 1)} for g, s in gaps if g > a.static],
    "change_times": [mmss(t) for t in ts],
  }
  print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
  main()
