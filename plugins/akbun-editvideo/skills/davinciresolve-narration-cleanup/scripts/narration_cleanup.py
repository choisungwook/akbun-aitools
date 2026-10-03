# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy>=2"]
# ///

"""Find breaths in narration by their frequency profile, cut them with long pauses, keep the voice.

profile: band levels (dB over each band's floor) of ranges the user marked as breaths by ear
clean:   join segments, drop breaths and long pauses, master, write a wav and a JSON report

Frames are 10 ms (hop 480 at 48 kHz). Every level is relative to that band's 5th percentile
(the room noise floor), so the rules do not depend on the recording gain.
"""

import argparse
import json
import re
import subprocess
import sys

import numpy as np

SR, HOP, WIN = 48000, 480, 1024
EDGES = [70, 300, 600, 1000, 2000, 3000, 4000, 6000, 8000, 12000, 20000]
NAMES = ["70-300", "300-600", "600-1k", "1-2k", "2-3k", "3-4k", "4-6k", "6-8k", "8-12k", "12-20k"]
PRE = "highpass=f=70,acompressor=threshold=-24dB:ratio=3:attack=5:release=150:makeup=1"


def load(path, start=None, end=None):
  cmd = ["ffmpeg", "-v", "error"]
  if start is not None:
    cmd += ["-ss", f"{start:.3f}"]
  if end is not None:
    cmd += ["-to", f"{end:.3f}"]
  cmd += ["-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"]
  return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()


def band_matrix(x):
  """(frames, 10) dB over each band's floor, 30 ms smoothed."""
  n = max(0, (len(x) - WIN) // HOP)
  frames = np.lib.stride_tricks.sliding_window_view(x, WIN)[::HOP][:n] * np.hanning(WIN)
  power = np.abs(np.fft.rfft(frames, axis=1)) ** 2 + 1e-12
  freq = np.fft.rfftfreq(WIN, 1 / SR)
  m = np.stack([10 * np.log10(power[:, (freq >= a) & (freq < b)].sum(1)) for a, b in zip(EDGES, EDGES[1:])], 1)
  m -= np.percentile(m, 5, axis=0)
  return np.apply_along_axis(lambda v: np.convolve(v, np.ones(3) / 3, "same"), 0, m)


def runs(mask):
  out, i = [], 0
  while i < len(mask):
    if mask[i]:
      j = i
      while j < len(mask) and mask[j]:
        j += 1
      out.append((i, j))
      i = j
    else:
      i += 1
  return out


def detect(x, args, marked=()):
  """Return (speech mask without breaths, breath mask, breath list with the rule that matched)."""
  m = band_matrix(x)
  n = len(m)
  low, mid, top = m[:, 0], m[:, 3:7].mean(1), m[:, 8:10].mean(1)
  harmonic = m[:, 0:2].max(1)                     # 70-600 Hz: where voice harmonics live
  voiced = low > args.voiced_db
  speech = (harmonic > 15) | (mid > 15)
  breath = np.zeros(n, bool)
  found = []

  # rule A, breath between words: noise in 1-6 kHz, no harmonics, little above 8 kHz, away from voicing
  cand = (mid > args.mid_min) & (mid < args.mid_max) & (low < mid - 4) & (top < mid - 10)
  for a, b in runs(cand):
    gap = args.gap_frames
    if args.min_frames <= b - a <= 80 and not voiced[max(0, a - gap):a].any() and not voiced[b:b + gap].any():
      breath[a:b] = True
      found.append([a / 100, b / 100, "between-words"])

  # rule B, quiet breath inside a pause: high band only, harmonic band at floor, no speech within 40 ms
  for a, b in runs((mid > 8) & (mid < 30) & (harmonic < 8)):
    if 10 <= b - a <= 80 and a >= 4 and b + 4 <= n and not speech[a - 4:a].any() and not speech[b:b + 4].any():
      if not breath[a:b].any():
        breath[a:b] = True
        found.append([a / 100, b / 100, "quiet"])

  for a, b in marked:
    breath[int(a * 100):int(b * 100)] = True
    found.append([a, b, "marked"])

  # a short sound (< 0.15 s) glued to a breath with silence on its other side is the breath's onset or tail
  rest = speech & ~breath
  for a, b in runs(rest):
    if b - a < 15 and ((breath[b:b + 3].any() and not rest[max(0, a - 10):a].any()) or
                       (breath[max(0, a - 3):a].any() and not rest[b:b + 10].any())):
      breath[a:b] = True
  return speech & ~breath, breath, sorted(found)


def clean(x, args, marked=()):
  speech, breath, found = detect(x, args, marked)
  n = len(speech)
  sp = [r for r in runs(speech) if r[1] - r[0] >= 3]          # drop isolated clicks under 30 ms
  if not sp:
    return x[:0], [], found
  keep = []
  a = max(0, sp[0][0] - int(args.edge[0] * 100))
  for (s0, e0), (s1, _) in zip(sp, sp[1:]):
    if (s1 - e0) / 100 > args.max_pause:
      keep.append((a, e0 + int(args.keep[0] * 100)))
      a = s1 - int(args.keep[1] * 100)
  keep.append((a, min(n, sp[-1][1] + int(args.edge[1] * 100))))

  y = x.copy()
  ramp = int(0.01 * SR)
  for a, b in runs(breath):                                   # breaths left inside kept air are muted
    s, e = a * HOP, min(len(y), b * HOP + WIN // 2)
    g = np.full(e - s, 0.03, np.float32)
    g[:ramp] = np.linspace(1, 0.03, ramp)[:e - s]
    g[-ramp:] = np.linspace(0.03, 1, ramp)[-(e - s):]
    y[s:e] *= g

  out, pieces, pos, xf = [], [], 0, int(0.01 * SR)
  for a, b in keep:
    seg = y[a * HOP:b * HOP].copy()
    src = a * HOP
    if out:                                                   # 10 ms crossfade at every join
      seg[:xf] *= np.linspace(0, 1, xf)
      out[-1][-xf:] = out[-1][-xf:] * np.linspace(1, 0, xf) + seg[:xf]
      seg, src = seg[xf:], src + xf
    pieces.append([src / SR, b * HOP / SR, pos / SR])
    out.append(seg)
    pos += len(seg)
  return np.concatenate(out), pieces, found


def lufs(path, af=None):
  chain = (af + "," if af else "") + "ebur128"
  err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", chain, "-f", "null", "-"],
                       capture_output=True, text=True).stderr
  return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def write(path, y, target):
  raw = path + ".raw.wav"
  subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                  "-c:a", "pcm_f32le", raw], input=y.astype(np.float32).tobytes(), check=True)
  if target is None:
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-c:a", "pcm_s24le", path], check=True)
    gain = 0.0
  else:
    gain = target - lufs(raw, PRE)
    chain = f"{PRE},volume={gain:.2f}dB,alimiter=limit=0.79:level=0:latency=1:attack=2:release=60"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-af", chain, "-c:a", "pcm_s24le", path], check=True)
  subprocess.run(["rm", "-f", raw])
  return gain


def parse_segment(text):
  """path or path@start:end (seconds)."""
  path, _, rng = text.partition("@")
  if not rng:
    return path, None, None
  a, b = rng.split(":")
  return path, float(a) if a else None, float(b) if b else None


def parse_ranges(texts):
  return [tuple(map(float, t.split("-"))) for t in texts]


def cmd_profile(args):
  x = load(args.input)
  m = band_matrix(x)
  print("range        " + " ".join(f"{n:>7}" for n in NAMES))
  for a, b in parse_ranges(args.range):
    row = m[int(a * 100):int(b * 100)].mean(0)
    print(f"{a:5.2f}-{b:5.2f}  " + " ".join(f"{v:7.1f}" for v in row))
  print("between-words rule: 1-6k mean in (%g, %g), 70-300 < 1-6k - 4, 8-20k < 1-6k - 10" % (args.mid_min, args.mid_max))


def cmd_clean(args):
  parts, offsets = [], []
  for seg in args.segment:
    path, a, b = parse_segment(seg)
    offsets.append(sum(len(p) for p in parts) / SR)
    parts.append(load(path, a, b))
  x = np.concatenate(parts)
  y, pieces, found = clean(x, args, parse_ranges(args.mark))
  gain = write(args.output, y, None if args.no_master else args.lufs)
  report = {"input_seconds": round(len(x) / SR, 3), "output_seconds": round(len(y) / SR, 3),
            "segments": [{"source": s, "joined_start": round(o, 3)} for s, o in zip(args.segment, offsets)],
            "breaths": [[round(a, 2), round(b, 2), r] for a, b, r in found],
            "pieces": [[round(a, 4), round(b, 4), round(p, 4)] for a, b, p in pieces], "gain_db": round(gain, 2)}
  if args.report:
    json.dump(report, open(args.report, "w"), ensure_ascii=False, indent=1)
  print(f"{report['input_seconds']:.1f}s -> {report['output_seconds']:.1f}s, breaths {len(found)}, gain {gain:+.1f} dB")
  for a, b, r in report["breaths"]:
    print(f"  breath {a:6.2f}-{b:6.2f}s  {r}")


def main():
  p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  p.add_argument("--mid-min", type=float, default=14, help="1-6 kHz lower bound over floor (dB)")
  p.add_argument("--mid-max", type=float, default=42, help="1-6 kHz upper bound over floor (dB); speech is higher")
  p.add_argument("--voiced-db", type=float, default=38, help="70-300 Hz level that counts as voicing")
  p.add_argument("--min-frames", type=int, default=12, help="shortest breath in 10 ms frames")
  p.add_argument("--gap-frames", type=int, default=3, help="frames that must separate a breath from voicing")
  sub = p.add_subparsers(dest="cmd", required=True)
  pr = sub.add_parser("profile", help="print band levels of marked breath ranges")
  pr.add_argument("input")
  pr.add_argument("--range", action="append", required=True, help="start-end seconds, e.g. 3.08-3.37")
  pr.set_defaults(func=cmd_profile)
  cl = sub.add_parser("clean", help="remove breaths and long pauses")
  cl.add_argument("--segment", action="append", required=True, help="path or path@start:end (seconds), joined in order")
  cl.add_argument("--mark", action="append", default=[], help="extra breath range in joined seconds, e.g. 4.57-4.66")
  cl.add_argument("--max-pause", type=float, default=0.3, help="pauses longer than this are shortened (s)")
  cl.add_argument("--keep", type=float, nargs=2, default=[0.12, 0.15], help="air kept after / before words (s)")
  cl.add_argument("--edge", type=float, nargs=2, default=[0.06, 0.15], help="air kept before first / after last word (s)")
  cl.add_argument("--lufs", type=float, default=-16.0, help="integrated loudness target")
  cl.add_argument("--no-master", action="store_true", help="skip compressor, gain and limiter")
  cl.add_argument("--report", help="JSON report path")
  cl.add_argument("-o", "--output", required=True)
  cl.set_defaults(func=cmd_clean)
  args = p.parse_args()
  args.func(args)
  return 0


if __name__ == "__main__":
  sys.exit(main())
