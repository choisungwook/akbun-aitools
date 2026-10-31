# /// script
# requires-python = ">=3.12"
# ///
"""gold reference 생성 스크립트. styles/clay-isometric.json의 투영 공식과 모양 수치를 그대로 쓴다.

uv run --python 3.12 make_clay_isometric.py > clay-isometric.svg
"""

import sys

OX, OY = 703, 225
COS30, SIN30 = 0.8660, 0.5

COLORS = {
  "SLATE": ("#CBD5E1", "#64748B", "#475569"),
  "COBALT": ("#93C5FD", "#3B82F6", "#1D4ED8"),
  "MINT": ("#A7F3D0", "#34D399", "#059669"),
}
FONT = "Inter, 'Noto Sans KR', sans-serif"
MONO = "'JetBrains Mono', monospace"


def proj(u, v, z=0):
  return round(OX + (u - v) * COS30, 1), round(OY + (u + v) * SIN30 - z, 1)


def points(coords):
  return " ".join(f"{x},{y}" for x, y in (proj(*c) for c in coords))


def polygon(coords, fill, extra=""):
  return f'<polygon points="{points(coords)}" fill="{fill}" stroke="{fill}" stroke-width="10" stroke-linejoin="round"{extra}/>'


def shadow(u, v, w, d, z0, floating=False):
  cx, cy = proj(u + w / 2, v + d / 2, z0)
  rx = round((w + d) * COS30 * 0.5)
  opacity = "0.08" if floating else "0.14"
  return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{rx // 2}" fill="#0F172A" opacity="{opacity}" filter="url(#ao)"/>'


def block(u, v, w, d, h, z0, color):
  top, side, dark = COLORS[color]
  parts = [] if (h <= 40 and max(w, d) >= 300) else [shadow(u, v, w, d, z0)]
  parts.append(polygon([(u + w, v, z0), (u + w, v + d, z0), (u + w, v + d, z0 + h), (u + w, v, z0 + h)], dark))
  parts.append(polygon([(u, v + d, z0), (u + w, v + d, z0), (u + w, v + d, z0 + h), (u, v + d, z0 + h)], side))
  parts.append(polygon([(u, v, z0 + h), (u + w, v, z0 + h), (u + w, v + d, z0 + h), (u, v + d, z0 + h)], top))
  return "\n".join(parts)


def slot(u, v, size, z):
  return polygon([(u, v, z), (u + size, v, z), (u + size, v + size, z), (u, v + size, z)], "#E2E8F0")


def ground_arrow(u0, u1, vc, color):
  side = COLORS[color][1]
  coords = [(u0, vc - 9), (u1 - 40, vc - 9), (u1 - 40, vc - 22), (u1, vc), (u1 - 40, vc + 22), (u1 - 40, vc + 9), (u0, vc + 9)]
  return f'<polygon points="{points([(u, v, 0) for u, v in coords])}" fill="{side}" stroke="{side}" stroke-width="4" stroke-linejoin="round"/>'


def acrylic(u, v, w, d, z):
  coords = [(u, v, z), (u + w, v, z), (u + w, v + d, z), (u, v + d, z)]
  return (f'<polygon points="{points(coords)}" fill="#FFFFFF" fill-opacity="0.35" stroke="#FFFFFF" '
          f'stroke-width="2" stroke-opacity="0.7" stroke-linejoin="round"/>')


def text(x, y, s, size=24, weight=600, fill="#334155", family=FONT):
  return f'<text x="{x}" y="{y}" font-family="{family}" font-weight="{weight}" font-size="{size}" fill="{fill}" text-anchor="middle">{s}</text>'


def main():
  out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080">',
         '<defs><filter id="ao" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter></defs>',
         '<rect class="bg" width="1920" height="1080" fill="#EEF2F7"/>']

  out.append(block(0, 160, 80, 80, 80, 0, "COBALT"))
  out.append(ground_arrow(100, 220, 200, "COBALT"))
  out.append(block(240, 120, 160, 160, 120, 0, "SLATE"))
  out.append(ground_arrow(420, 540, 200, "MINT"))

  out.append(block(560, 40, 320, 320, 32, 0, "SLATE"))
  for su, sv in ((600, 80), (740, 80), (600, 220), (740, 220)):
    out.append(slot(su, sv, 100, 32))
  out.append(block(610, 90, 80, 80, 80, 32, "COBALT"))
  for i in range(3):
    dx, dy = proj(840, 320 + 24 * i, 32)
    out.append(f'<circle cx="{dx}" cy="{dy}" r="8" fill="{COLORS["MINT"][1]}"/>')

  out.append(acrylic(230, 110, 180, 180, 170))
  ax, ay = proj(320, 200, 170)
  out.append(text(ax, ay + 8, "Auto Mode Engine"))

  px, py = proj(40, 200, 80)
  out.append(text(px, py - 104, "Pod"))
  out.append(text(px, py - 76, "2 vCPU · 4 GiB", 18, 400, "#334155", MONO))
  out.append(f'<line x1="{px}" y1="{py - 64}" x2="{px}" y2="{py - 44}" stroke="#94A3B8" stroke-width="1.5"/>')

  nx, ny = proj(880, 360, 0)
  out.append(f'<line x1="{nx}" y1="{ny + 8}" x2="{nx}" y2="{ny + 36}" stroke="#94A3B8" stroke-width="1.5"/>')
  out.append(text(nx, ny + 66, "EC2 Node"))
  out.append(text(nx, ny + 94, "auto-provisioned", 18, 400, "#94A3B8"))

  out.append("</svg>")
  sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
  main()
