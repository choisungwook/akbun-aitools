#!/usr/bin/env python3
"""Render a hand-drawn (Excalidraw-like) relationship sketch SVG from a JSON model.

The model describes git repositories as nodes and their relationships as labeled,
directed arrows. Output is a self-contained SVG with a paper background, wobbly
"hand-drawn" strokes, and English labels — the same look as a whiteboard sketch.

Usage:
    python render_sketch_svg.py <model.json> [output.svg]

If output.svg is omitted, the file is written into a per-run directory:
    ~/Downloads/<model-name>/<model-name>.svg

Model schema (see assets/example-relation.json):
{
  "name": "akbun-aitools",            # used for the default filename / title
  "title": "How the repos relate",     # optional heading drawn at top
  "nodes": [
    {"id": "core", "label": "akbun-core", "keywords": ["library", "go"]},
    ...
  ],
  "edges": [
    {"from": "core", "to": "api", "label": "imports", "direction": "forward"},
    ...
  ]
}

direction: "forward" (from->to, default), "back" (to->from), or "both".
"""

import json
import math
import os
import sys

# ---------------------------------------------------------------------------
# Palette — warm "paper notebook" look, matching the reference sketch.
# ---------------------------------------------------------------------------
PAPER = "#faf6ee"
INK = "#2b2b2b"
ACCENT = "#d2691e"   # warm orange for emphasis dots / key arrows
HILITE = "#ffe1a8"   # marker highlight behind edge labels
FONT = "'Comic Sans MS', 'Segoe Print', 'Bradley Hand', 'Chalkboard SE', cursive"


def _jitter(seed):
    """Deterministic small pseudo-random offset in roughly [-1, 1]."""
    x = math.sin(seed * 12.9898) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


def rough_line(x1, y1, x2, y2, stroke=INK, width=2.2, seed=0, passes=2):
    """A wobbly line, optionally drawn twice for a sketchy double-stroke."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1
    # perpendicular unit vector for offsetting control points
    px, py = -dy / length, dx / length
    out = []
    for p in range(passes):
        amp = 1.4 + p * 0.6
        c1 = 0.30 + 0.08 * _jitter(seed + p + 1)
        c2 = 0.68 + 0.08 * _jitter(seed + p + 5)
        o1 = amp * _jitter(seed + p + 11)
        o2 = amp * _jitter(seed + p + 17)
        cx1 = x1 + dx * c1 + px * o1
        cy1 = y1 + dy * c1 + py * o1
        cx2 = x1 + dx * c2 + px * o2
        cy2 = y1 + dy * c2 + py * o2
        sx = x1 + _jitter(seed + p + 3) * 0.8
        sy = y1 + _jitter(seed + p + 4) * 0.8
        ex = x2 + _jitter(seed + p + 7) * 0.8
        ey = y2 + _jitter(seed + p + 8) * 0.8
        out.append(
            f'<path d="M {sx:.1f} {sy:.1f} C {cx1:.1f} {cy1:.1f} '
            f'{cx2:.1f} {cy2:.1f} {ex:.1f} {ey:.1f}" fill="none" '
            f'stroke="{stroke}" stroke-width="{width:.1f}" '
            f'stroke-linecap="round"/>'
        )
    return "\n".join(out)


def rough_rect(x, y, w, h, seed=0, stroke=INK, fill="#ffffff", width=2.4):
    """A hand-drawn rectangle: four wobbly sides over a faint solid fill."""
    parts = [
        f'<rect x="{x+3:.1f}" y="{y+4:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="6" fill="#000000" fill-opacity="0.10"/>',  # soft drop shadow
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="6" fill="{fill}"/>',
    ]
    parts.append(rough_line(x, y, x + w, y, stroke, width, seed + 1))
    parts.append(rough_line(x + w, y, x + w, y + h, stroke, width, seed + 2))
    parts.append(rough_line(x + w, y + h, x, y + h, stroke, width, seed + 3))
    parts.append(rough_line(x, y + h, x, y, stroke, width, seed + 4))
    return "\n".join(parts)


def arrow_head(x, y, angle, stroke=INK, size=14, seed=0, width=2.4):
    """Two short hand-drawn strokes forming an arrowhead pointing along `angle`."""
    a1 = angle + math.radians(152)
    a2 = angle - math.radians(152)
    x1, y1 = x + size * math.cos(a1), y + size * math.sin(a1)
    x2, y2 = x + size * math.cos(a2), y + size * math.sin(a2)
    return (
        rough_line(x1, y1, x, y, stroke, width, seed + 21, passes=1)
        + "\n"
        + rough_line(x2, y2, x, y, stroke, width, seed + 23, passes=1)
    )


def text(x, y, s, size=18, fill=INK, anchor="middle", weight="normal", rotate=0):
    transform = f' transform="rotate({rotate:.1f} {x:.1f} {y:.1f})"' if rotate else ""
    s = (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" '
        f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
        f'font-weight="{weight}"{transform}>{s}</text>'
    )


def text_width(s, size, bold=False):
    """Rough pixel width of a string in the handwritten-marker font.

    The marker font is fairly wide; bold is wider still. We over-estimate a
    little on purpose so text never spills past the box border.
    """
    factor = 0.64 if bold else 0.56
    return len(s) * size * factor


def layout(n, cx, cy, radius):
    """Return node centers. 1=center, 2=horizontal, >=3 around a circle."""
    if n == 1:
        return [(cx, cy)]
    if n == 2:
        return [(cx - radius, cy), (cx + radius, cy)]
    pts = []
    for i in range(n):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        pts.append((cx + radius * math.cos(ang), cy + radius * math.sin(ang)))
    return pts


def edge_endpoints(a, b, a_half, b_half):
    """Trim a center-to-center segment to each box's border so arrows touch edges.

    a_half / b_half are (half_width, half_height) for the two boxes, which may
    differ because boxes are sized to their text.
    """
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay

    def border(cx, cy, dirx, diry, hw, hh):
        if dirx == 0 and diry == 0:
            return cx, cy
        tx = hw / abs(dirx) if dirx else float("inf")
        ty = hh / abs(diry) if diry else float("inf")
        t = min(tx, ty)
        return cx + dirx * t, cy + diry * t

    start = border(ax, ay, dx, dy, a_half[0], a_half[1])
    end = border(bx, by, -dx, -dy, b_half[0], b_half[1])
    return start, end


def render(model):
    nodes = model.get("nodes", [])
    edges = model.get("edges", [])
    n = len(nodes)

    box_h = 84
    half_h = box_h / 2
    pad = 22  # horizontal breathing room on each side of the text

    # Size every box to its own text so labels/captions never spill out.
    dims = {}
    for node in nodes:
        label = node.get("label", node["id"])
        kw = " · ".join(node.get("keywords", [])[:4])
        w = max(
            170,
            text_width(label, 19, bold=True) + 2 * pad,
            text_width(kw, 13) + 2 * pad,
        )
        dims[node["id"]] = (w / 2, half_h)
    max_w = max((d[0] * 2 for d in dims.values()), default=170)

    # canvas + layout scale with node count AND the widest box, so neighbouring
    # boxes keep enough gap for the arrows and their labels between them.
    radius = max(230, 70 * n, max_w * 1.15) if n > 2 else max(230, max_w * 0.75)
    margin = 150
    W = int(2 * radius + 2 * max_w + margin) if n > 1 else int(max_w + 360)
    H = int(2 * (radius + box_h) + margin) if n > 2 else 480
    W = max(W, 760)
    H = max(H, 460)
    cx, cy = W / 2, H / 2 + (24 if model.get("title") else 0)

    centers = layout(n, cx, cy, radius)
    pos = {node["id"]: centers[i] for i, node in enumerate(nodes)}

    svg = [
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">',
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
    ]

    if model.get("title"):
        svg.append(text(W / 2, 50, model["title"], size=26, weight="bold"))

    # ---- edges first, so boxes sit on top ----
    for i, e in enumerate(edges):
        if e["from"] not in pos or e["to"] not in pos:
            continue
        a, b = pos[e["from"]], pos[e["to"]]
        ah = (dims[e["from"]][0] + 6, dims[e["from"]][1] + 6)
        bh = (dims[e["to"]][0] + 6, dims[e["to"]][1] + 6)
        start, end = edge_endpoints(a, b, ah, bh)
        direction = e.get("direction", "forward")
        emphasize = e.get("emphasize", False)
        col = ACCENT if emphasize else INK
        wdt = 3.0 if emphasize else 2.2

        # draw the (slightly wobbly) connector and remember its midpoint for the label
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        svg.append(rough_line(start[0], start[1], end[0], end[1], col, wdt, seed=i * 9 + 100))

        ang = math.atan2(end[1] - start[1], end[0] - start[0])
        if direction in ("forward", "both"):
            svg.append(arrow_head(end[0], end[1], ang, col, seed=i * 9 + 200, width=wdt))
        if direction in ("back", "both"):
            svg.append(arrow_head(start[0], start[1], ang + math.pi, col, seed=i * 9 + 300, width=wdt))

        label = e.get("label", "")
        if label:
            # size the highlighter swatch to the label, same estimator as the boxes
            tw = text_width(label, 17, bold=True) + 16
            svg.append(
                f'<rect x="{mx - tw/2:.1f}" y="{my - 16:.1f}" width="{tw:.1f}" '
                f'height="26" rx="5" fill="{HILITE}" opacity="0.9"/>'
            )
            svg.append(text(mx, my + 3, label, size=17, weight="bold", fill=INK))

    # ---- nodes ----
    for i, node in enumerate(nodes):
        x, y = pos[node["id"]]
        hw, hh = dims[node["id"]]
        bx, by = x - hw, y - hh
        svg.append(rough_rect(bx, by, hw * 2, hh * 2, seed=i * 7 + 1))
        svg.append(text(x, y - 6, node.get("label", node["id"]), size=19, weight="bold"))
        kws = node.get("keywords", [])
        if kws:
            kw = " · ".join(kws[:4])
            svg.append(text(x, y + 20, kw, size=13, fill="#6b6b6b"))

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    model_path = sys.argv[1]
    with open(model_path, "r", encoding="utf-8") as f:
        model = json.load(f)

    if len(sys.argv) >= 3:
        out_path = sys.argv[2]
    else:
        name = model.get("name", "repo-relation")
        out_path = os.path.expanduser(f"~/Downloads/{name}/{name}.svg")

    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    svg = render(model)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(out_path)


if __name__ == "__main__":
    main()
