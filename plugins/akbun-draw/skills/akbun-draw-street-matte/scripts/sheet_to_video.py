"""2×2 스프라이트 시트 PNG를 칸 4개로 잘라 고정 카메라 반복 영상(mp4 또는 gif)으로 잇는다.

  <sheet.png> -o <out.mp4|out.gif> [--hold 1.0] [--fade 0.6] [--width 1280]
  --selftest

칸 순서는 왼쪽 위 → 오른쪽 위 → 왼쪽 아래 → 오른쪽 아래이고, 마지막 칸 뒤에 첫 칸으로 돌아가 반복이 이어진다.
칸마다 hold+fade초 머문 뒤 다음 칸으로 fade초 동안 겹쳐 넘어간다. 마지막 칸은 첫 칸으로 겹쳐 끝나므로
영상 끝 장면 = 첫 장면이고, 길이 = 4 × (hold + fade) + fade 초.
출력 이름이 .gif면 같은 영상을 10fps·무한 반복 gif로 쓴다. gif는 입자를 더하지 않고 눌러 쓴다.
폭은 --width이고, 기본값 그대로면 640px.
칸 경계의 틈·테두리를 지우려고 칸마다 가장자리 2%(칸 폭·높이 기준, 내림 px)를 잘라 낸 뒤 16:9로 맞춘다.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

INSET = 0.02
GIF_FPS = 10


def probe(path, entry):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", entry,
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout
    return out.strip()


def render(sheet, out, hold=1.0, fade=0.6, width=1280):
    w, h = map(int, probe(sheet, "stream=width,height").split(","))
    pw, ph = w // 2, h // 2
    dx, dy = int(pw * INSET), int(ph * INSET)
    height = width * 9 // 16 // 2 * 2
    seg = hold + fade  # 칸 하나가 화면에 있는 길이(다음 칸과 겹치는 fade 포함)
    order = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 0)]  # 마지막에 첫 칸으로 돌아가 반복을 잇는다
    parts, inputs = [], []
    for i, (cx, cy) in enumerate(order):
        inputs += ["-loop", "1", "-t", f"{seg + fade:.3f}", "-i", str(sheet)]
        parts.append(f"[{i}:v]crop={pw - 2 * dx}:{ph - 2 * dy}:{cx * pw + dx}:{cy * ph + dy},"
                     f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},"
                     f"setsar=1,fps=24,format=yuv420p[p{i}]")
    last = "p0"
    for i in range(1, len(order)):
        parts.append(f"[{last}][p{i}]xfade=transition=fade:duration={fade}:offset={i * seg:.3f}[x{i}]")
        last = f"x{i}"
    # ponytail: 칸 사이를 디졸브로 잇는다. 큰 이동(열차가 화면을 가로지름)은 겹쳐 보인다; 매끈해야 하면 칸 수를 늘린다.
    total = 4 * seg + fade
    parts.append(f"[{last}]noise=alls=7:allf=t+u,vignette=PI/6,trim=duration={total:.3f}[v]")
    gif = Path(out).suffix.lower() == ".gif"
    if gif:  # gif는 프레임 차이만 저장하므로 입자를 더하지 않고 시트 입자도 눌러 둔다(그대로면 7초 640px에 8~17MB)
        parts[-1] = parts[-1].replace("noise=alls=7:allf=t+u,", "").replace("[v]", "[g]")
        parts.append(f"[g]fps={GIF_FPS},hqdn3d=4:4:0:0,split[a][b];[a]palettegen=stats_mode=diff[pal];"
                     "[b][pal]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle[v]")
        enc = ["-loop", "0"]
    else:
        enc = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(parts), "-map", "[v]", *enc, str(out)]
    subprocess.run(cmd, check=True)
    return total


def selftest():
    with tempfile.TemporaryDirectory() as d:
        sheet, out = Path(d) / "sheet.png", Path(d) / "out.mp4"
        # 칸마다 다른 색인 1280×720 시트
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=red:s=640x360", "-f", "lavfi", "-i",
                        "color=green:s=640x360", "-f", "lavfi", "-i", "color=blue:s=640x360", "-f", "lavfi", "-i",
                        "color=white:s=640x360", "-filter_complex", "[0][1]hstack[t];[2][3]hstack[b];[t][b]vstack",
                        "-frames:v", "1", str(sheet)], check=True)
        total = render(sheet, out, hold=0.5, fade=0.3, width=640)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    str(out)], capture_output=True, text=True, check=True).stdout)
        assert abs(dur - total) < 0.15, (dur, total)
        assert probe(out, "stream=width,height") == "640,360"
        # 0.2초 첫 칸(빨강), 1.2초 둘째 칸(초록), 끝 0.05초 전은 다시 첫 칸(빨강)
        for t, want in ((0.2, 0), (1.2, 1), (total - 0.05, 0)):
            px = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(out), "-frames:v", "1", "-vf",
                                 "crop=8:8:316:176,scale=1:1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                capture_output=True, check=True).stdout
            assert max(range(3), key=lambda c: px[c]) == want, (t, list(px))
        g = Path(d) / "out.gif"
        render(sheet, g, hold=0.5, fade=0.3, width=320)
        frames = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_entries", "stream=nb_read_frames",
                                     "-of", "csv=p=0", str(g)], capture_output=True, text=True, check=True).stdout)
        assert abs(frames - round(total * GIF_FPS)) <= 2 and g.read_bytes()[:3] == b"GIF", frames
    print("selftest ok")


def main():
    if sys.argv[1:2] == ["--selftest"]:
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("sheet")
    ap.add_argument("-o", required=True)
    ap.add_argument("--hold", type=float, default=1.0)
    ap.add_argument("--fade", type=float, default=0.6)
    ap.add_argument("--width", type=int, default=1280)
    a = ap.parse_args()
    if a.o.lower().endswith(".gif") and a.width == 1280:
        a.width = 640
    total = render(Path(a.sheet), Path(a.o), a.hold, a.fade, a.width)
    print(f"{a.o} {total:.1f}s")


if __name__ == "__main__":
    main()
