# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py", "numpy", "pillow"]
# ///
"""explainer 장면 spec(JSON) → SVG·레이어 PNG, 채점, Resolve comp.

모양은 references/shapes.jsonl, 도형 스타일은 shape-styles.jsonl, 색은 palettes.jsonl에서만 읽는다.
spec은 무엇을 어디에 언제 둘지와 theme(palette·shape 스타일 id)만 정한다.

  uv run scene.py build spec.json out/          # out/<id>.svg, <id>_still.png, <id>_layers/
  uv run scene.py check out/ spec1.json ...     # references/checklist.jsonl 채점, 95% 미만이면 종료 코드 1
  uv run scene.py comp spec.json out/           # out/<id>.comp (Template 매크로, Timing 컨트롤)
  uv run scene.py timing "자막1" "자막2"          # 녹음 전 subs·dur
  uv run scene.py --selftest
"""
import argparse, html, importlib.util, json, math, re, sys, tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
REF = SKILL / "references"
RENDER = SKILL.parents[2] / "akbun-draw/skills/akbun-draw-night-gouache/scripts/render_gouache.py"
NS = "http://www.w3.org/2000/svg"
FPS = 24


def jsonl(name):
  return [json.loads(l) for l in (REF / name).read_text().splitlines() if l.strip()]


PAL_KEYS = jsonl("palettes.jsonl")[0]["keys"]
PALETTES = {p["id"]: p for p in jsonl("palettes.jsonl")[1:]}
STYLES = {s["id"]: s for s in jsonl("shape-styles.jsonl")}
DEFAULT_THEME = {"palette": "night", "shape": "gouache"}
SHAPES = {s["id"]: s for s in jsonl("shapes.jsonl")}
CHECKS = jsonl("checklist.jsonl")
CHECK_TEXT = {c["id"]: c["item"] for c in CHECKS}
ROW = next(r for r in jsonl("layout.jsonl") if r["id"] == "row")


def color(spec, key):
  return PALETTES[spec["theme"]["palette"]]["colors"][key]


def style(spec):
  return STYLES[spec["theme"]["shape"]]


# ---------- spec ----------

def load_spec(path):
  path = Path(path)
  spec = json.loads(path.read_text())
  spec["_dir"] = path.parent
  base = load_spec(path.parent / spec["extends"]) if "extends" in spec else None
  spec["theme"] = {**DEFAULT_THEME, **(base["theme"] if base else {}), **spec.get("theme", {})}
  if spec["theme"]["palette"] not in PALETTES or spec["theme"]["shape"] not in STYLES:
    sys.exit(f"error: theme {spec['theme']}. palette는 {list(PALETTES)}, shape는 {list(STYLES)} 중 하나")
  if base:
    spec["_base"] = base
    inherited = [dict(l, at=-1, _inherited=True) for l in base["layers"]]
    spec["layers"] = inherited + spec["layers"]
    spec["row"] = base.get("row", []) + [n for n in spec.get("row", []) if n not in base.get("row", [])]
  for l in spec["layers"]:
    if l["shape"] not in SHAPES:
      sys.exit(f"error: shapes.jsonl에 없는 shape {l['shape']} (레이어 {l['name']})")
  ats = {l["name"]: l.get("at") for l in spec["layers"]}
  for l in spec["layers"]:
    if l["shape"] == "arrow" and not l.get("_inherited"):
      ends = [ats[l["from"]], ats[l["to"]]]
      if "at" in l and max(ends) != -1 and not (l.get("flow") == "reply" and l["at"] >= max(ends) + 0.3 - 1e-6):
        sys.exit(f"error: 화살표 {l['name']}의 at은 쓰지 않는다(두 끝 중 늦은 등장 + 0.3초). reply 화살표만 그 응답을 말하는 자막 시작을 줄 수 있다")
      if "at" not in l:
        if max(ends) == -1:
          sys.exit(f"error: 화살표 {l['name']}은 두 끝이 모두 이어받은 대상이라 at(그 화살표를 말하는 자막 시작)을 준다")
        l["at"] = round(max(ends) + 0.3, 2)
  if spec.get("punch"):
    if "at" in spec["punch"]:
      sys.exit("error: punch.at은 쓰지 않는다(max(마지막 등장 + 0.5, 장면 길이 - 2.0)초로 정해진다)")
    last = max(l["at"] for l in spec["layers"])
    spec["punch"]["at"] = round(max(last + 0.5, spec["dur"] - 2.0), 2)
  return spec


def size_of(l):
  s = SHAPES[l["shape"]]
  if l["shape"] == "person":
    return s["size"]
  if l["shape"] == "box":
    return [min(s["w_max"], max(s["w_min"], len(l["label"]) * s["w_per_char"] + s["w_pad"])), s["h"]]
  if l["shape"] == "db":
    return [s["w"], s["h"] + 2 * round(s["w"] * s["cap_ry_ratio"])]
  raise ValueError(l["shape"])


def code_lines(spec, l):
  s = SHAPES["code-card"]
  f = spec["_dir"] / l["file"]
  src = f.read_text().splitlines()
  a, b = l["lines"]
  rows = [("dim", f"$ cat {f.name}", None)]
  if a > 1:
    rows.append(("dim", "...", None))
  rows += [("code", src[i - 1], i) for i in range(a, b + 1)]
  if b < len(src):
    rows.append(("dim", "...", None))
  if len(rows) > s["max_lines"]:
    sys.exit(f"error: 코드 카드가 {len(rows)}줄이다(최대 {s['max_lines']})")
  return rows


def layout(spec):
  """레이어 이름 → 기하 정보. 그리기 전에 bbox를 정해 화살표·점선 상자·태그 위치를 계산한다."""
  g = dict(layout(spec["_base"])) if "_base" in spec else {}  # 이어받은 레이어는 앞 장면 위치 그대로
  by = {l["name"]: l for l in spec["layers"]}
  slots = []  # row 칸 하나 = 이름 하나 또는 세로로 쌓을 이름 목록
  for item in spec.get("row", []):
    names = [n for n in ([item] if isinstance(item, str) else item) if n not in g]
    if names:
      slots.append([(n, size_of(by[n])) for n in names])
  if slots:
    vg = ROW["min_gap"]
    dims = [(max(w for _, (w, _) in sl), sum(h for _, (_, h) in sl) + vg * (len(sl) - 1)) for sl in slots]
    total = sum(w for w, _ in dims)
    gap = max(vg, (ROW["x1"] - ROW["x0"] - total) // (len(slots) - 1)) if len(slots) > 1 else 0
    x = 960 - (total + gap * (len(slots) - 1)) // 2
    for sl, (sw, sh) in zip(slots, dims):
      y = ROW["cy"] - sh // 2
      for n, (w, h) in sl:
        mx = x + (sw - w) // 2
        g[n] = {"bbox": [mx, y, mx + w, y + h]}
        y += h + vg
      x += sw + gap
  rank = {"dashed-box": 1, "arrow": 2, "cross": 3, "tag": 3, "code-mark": 3}
  for l in sorted(spec["layers"], key=lambda l: rank.get(l["shape"], 0)):
    n, sh = l["name"], l["shape"]
    if n in g:
      continue
    if SHAPES[sh].get("object") and sh != "code-card":
      sys.exit(f"error: object 레이어 {n}을 row에 넣는다(위아래로 갈라지면 세로 묶음)")
    elif sh == "code-card":
      s = SHAPES[sh]
      rows = code_lines(spec, l)
      lh = round(s["font_size"] * s["line_height"])
      h = s["bar_h"] + s["pad_top"] + lh * len(rows) + s["pad_bottom"]
      g[n] = {"bbox": [s["x"], s["y"], s["x"] + s["w"], s["y"] + h], "rows": rows, "lh": lh}
    elif sh == "arrow":
      s = dict(SHAPES[sh], bend=style(spec)["arrow"]["bend"])
      a, b = outer(spec, g, l["from"]), outer(spec, g, l["to"])
      gp = s["gap"]
      if l.get("lane") == "below":  # 같은 두 대상 사이의 되돌아오는 화살표는 두 대상 아래로 돈다
        p0 = ((a[0] + a[2]) / 2, a[3] + gp / 2)
        p1 = (b[2] + gp, max(a[3], b[3]) - 20) if b[2] < a[0] else (b[0] - gp, max(a[3], b[3]) - 20)
        bend = -(s["bend"] or 30) * 2
      else:
        acx, acy, bcx, bcy = (a[0] + a[2]) / 2, (a[1] + a[3]) / 2, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        if b[0] >= a[2]:
          p0, p1 = (a[2] + gp, acy), (b[0] - gp, bcy)
        elif b[2] <= a[0]:
          p0, p1 = (a[0] - gp, acy), (b[2] + gp, bcy)
        elif b[1] >= a[3]:
          p0, p1 = (acx, a[3] + gp), (bcx, b[1] - gp)
        else:
          p0, p1 = (acx, a[1] - gp), (bcx, b[3] + gp)
        bend = s["bend"]
      dx, dy = p1[0] - p0[0], p1[1] - p0[1]
      ln = math.hypot(dx, dy) or 1
      c = ((p0[0] + p1[0]) / 2 + dy / ln * bend, (p0[1] + p1[1]) / 2 - dx / ln * bend)
      xs, ys = [p0[0], c[0], p1[0]], [p0[1], c[1], p1[1]]
      g[n] = {"p0": p0, "c": c, "p1": p1, "bbox": [min(xs), min(ys), max(xs), max(ys)]}
    elif sh == "dashed-box":
      p = SHAPES[sh]["pad"]
      bb = [g[t]["bbox"] for t in l["around"]]
      g[n] = {"bbox": [min(b[0] for b in bb) - p, min(b[1] for b in bb) - p, max(b[2] for b in bb) + p, max(b[3] for b in bb) + p]}
    elif sh == "tag":
      s = SHAPES[sh]
      t = g[l["on"]]["bbox"]
      g[n] = {"xy": (t[0], t[1] - s["gap"] - s["height"]), "bbox": [t[0], t[1] - s["gap"] - s["height"], t[0] + 300, t[1] - s["gap"]]}
    elif sh == "cross":
      a = g[l["on"]]
      m = (0.25 * a["p0"][0] + 0.5 * a["c"][0] + 0.25 * a["p1"][0], 0.25 * a["p0"][1] + 0.5 * a["c"][1] + 0.25 * a["p1"][1])
      d = SHAPES[sh]["size"] / 2
      g[n] = {"m": m, "bbox": [m[0] - d, m[1] - d, m[0] + d, m[1] + d]}
    elif sh == "code-mark":
      s, cs = SHAPES[sh], SHAPES["code-card"]
      card = g[l["card"]]
      i = next(k for k, r in enumerate(card["rows"]) if r[2] == l["line"])
      text = card["rows"][i][1]
      cw = cs["font_size"] * 0.5  # D2Coding 영문 한 글자 = 글자 크기의 0.5
      base = card["bbox"][1] + cs["bar_h"] + cs["pad_top"] + card["lh"] * i + cs["font_size"]
      x0 = card["bbox"][0] + cs["pad_x"] + cw * (len(text) - len(text.lstrip())) - s["pad_x"]
      x1 = card["bbox"][0] + cs["pad_x"] + cw * len(text.rstrip()) + s["pad_x"]
      g[n] = {"bbox": [x0, base - cs["font_size"] - s["pad_top"], x1, base + s["pad_bottom"]]}
  return g


def outer(spec, g, name):
  """대상을 감싼 점선 상자가 있으면 그 상자를 대상의 바깥 경계로 본다(화살표가 점선 안으로 들어가지 않게)."""
  bb = g[name]["bbox"]
  for l in spec["layers"]:
    if l["shape"] == "dashed-box" and name in l["around"]:
      bb = g[l["name"]]["bbox"]
  return bb


def curve(p0, c, p1, n=20):
  return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]) for t in (i / n for i in range(n + 1))]


# ---------- SVG ----------

def prim(p, fill):
  if p["t"] == "circle":
    return f'<circle cx="{p["cx"]}" cy="{p["cy"]}" r="{p["r"]}" fill="{fill}"/>'
  return f'<path d="{p["d"]}" fill="{fill}"/>'


def text_width(t, size):
  return sum(size * (0.98 if ord(c) > 0x2E80 else 0.3 if c == " " else 0.58) for c in t)


def draw(spec, l, g):
  sh, s, geo, st = l["shape"], SHAPES[l["shape"]], g[l["name"]], style(spec)
  C = lambda k: color(spec, k)
  tex = st["texture"]
  if sh == "person":
    x, y = geo["bbox"][:2]
    body = "".join(prim(p, C(s["color"])) for p in s["prims"])
    if not tex:
      return f'<g transform="translate({x} {y})">{body}</g>'
    shade = "".join(prim(p, "url(#shade)") for p in s["prims"])
    return f'<g transform="translate({x} {y})"><g filter="url(#paint)">{body}</g>{shade}</g>'
  if sh in ("box", "db"):
    x0, y0, x1, y1 = geo["bbox"]
    if sh == "box":
      if l.get("role") not in s["roles"]:
        sys.exit(f"error: box role은 {list(s['roles'])} 중 하나다 ({l['name']}: {l.get('role')})")
      fill, ink = C(s["roles"][l["role"]]["fill"]), C(s["roles"][l["role"]]["ink"])
      shape = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{st["box_rx"]}" FILL/>']
      ty, label = (y0 + y1) / 2 + 12, l["label"]
    else:  # 원통: 윗면 타원 전체 + 곧은 옆면 + 둥근 밑면. 옆면 선은 윗면을 가로지르지 않는다
      fill, ink = C(s["color"]), C(s["ink"])
      ry = round(s["w"] * s["cap_ry_ratio"])
      top, bot, rx, cx = y0 + ry, y1 - ry, s["w"] / 2, (x0 + x1) / 2
      side = f"M{x0} {top} V{bot} A{rx} {ry} 0 0 0 {x1} {bot} V{top}"
      cap = f'<ellipse cx="{cx}" cy="{top}" rx="{rx}" ry="{ry}"'
      ty, label = (top + bot) / 2 + 30, l.get("label", "DB")
      if st["fill"]:
        line = f'fill="none" stroke="{ink}" stroke-width="4"'
        body = f'<path d="{side} Z" fill="{fill}"/>{cap} fill="{C(s["cap"])}"/>'
        rim = f'<path d="{side}" {line}/>{cap} {line}/>'
        # 음영은 윗면 타원 아래(옆면)에만. 윗면에 겹치면 윗면 오른쪽에 쐐기 모양 얼룩이 생긴다
        shade = f'<path d="M{x0} {top} A{rx} {ry} 0 0 0 {x1} {top} V{bot} A{rx} {ry} 0 0 1 {x0} {bot} Z" fill="url(#shade)"/>'
        # 원통은 모양이 휘면 안 되므로 가장자리를 흔드는 paint 대신 입자만 얹는 brush 질감
        out = f'<g filter="url(#brush)">{body}</g>{shade}{rim}' if tex else body + rim
      else:
        line = f'fill="none" stroke="{fill}" stroke-width="{st["stroke"]}"'
        out = f'<path d="{side}" {line}/>{cap} {line}/>'
        ink = fill
      return out + f'<text x="{cx}" y="{ty}" text-anchor="middle" font-family="{s["font"]}" font-weight="{s["font_weight"]}" font-size="{s["font_size"]}" fill="{ink}">{html.escape(label)}</text>'
    if st["fill"]:
      body = "".join(e.replace("FILL", f'fill="{fill}"') for e in shape)
      shade = "".join(e.replace("FILL", 'fill="url(#shade)"') for e in shape[:1])
      out = f'<g filter="url(#paint)">{body}</g>{shade}' if tex else body
    else:  # 채움 없는 테두리. 글자도 테두리 색
      out = "".join(e.replace("FILL", f'fill="none" stroke="{fill}" stroke-width="{st["stroke"]}"') for e in shape)
      ink = fill
    return out + f'<text x="{(x0 + x1) / 2}" y="{ty}" text-anchor="middle" font-family="{s["font"]}" font-weight="{s["font_weight"]}" font-size="{s["font_size"]}" fill="{ink}">{html.escape(label)}</text>'
  if sh == "code-card":
    x0, y0, x1, _ = geo["bbox"]
    w = x1 - x0
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{geo["bbox"][3] - y0}" rx="{s["rx"]}" fill="{C(s["bg"])}"/>',
           f'<rect x="{x0}" y="{y0}" width="{w}" height="{s["bar_h"]}" rx="{s["rx"]}" fill="{C(s["bar"])}"/><rect x="{x0}" y="{y0 + s["bar_h"] - s["rx"]}" width="{w}" height="{s["rx"]}" fill="{C(s["bar"])}"/>']
    for i, d in enumerate(s["dots"]):
      out.append(f'<circle cx="{x0 + 28 + i * s["dot_gap"]}" cy="{y0 + s["bar_h"] / 2}" r="{s["dot_r"]}" fill="{C(d)}"/>')
    out.append(f'<text x="{x0 + w / 2}" y="{y0 + 30}" text-anchor="middle" font-family="Pretendard" font-size="20" fill="{C(s["dim"])}">{s["shell"]}</text>')
    for i, (kind, t, _) in enumerate(geo["rows"]):
      by = y0 + s["bar_h"] + s["pad_top"] + geo["lh"] * i + s["font_size"]
      c = C(s["text"] if kind == "code" else s["dim"])
      out.append(f'<text x="{x0 + s["pad_x"]}" y="{by}" font-family="{s["font"]}" font-size="{s["font_size"]}" fill="{c}" xml:space="preserve">{html.escape(t)}</text>')
    return "".join(out)
  if sh == "arrow":
    a_ = st["arrow"]
    p0, c, p1 = geo["p0"], geo["c"], geo["p1"]
    ang = math.atan2(p1[1] - c[1], p1[0] - c[0])
    h = [(p1[0] - a_["head_len"] * math.cos(ang + k), p1[1] - a_["head_len"] * math.sin(ang + k)) for k in (a_["head_angle"], -a_["head_angle"])]
    flow = l.get("flow", "forward")
    if flow not in s["flows"]:
      sys.exit(f"error: arrow flow는 {list(s['flows'])} 중 하나다")
    col = C(s["flows"][flow])
    filt = f' filter="url(#{a_["filter"]})"' if a_["filter"] else ""
    if a_["head"] == "solid":  # 곧은 실선 + 채운 삼각 화살촉. 선은 화살촉 밑에서 멈춘다
      bx, by = p1[0] - a_["head_len"] * 0.8 * math.cos(ang), p1[1] - a_["head_len"] * 0.8 * math.sin(ang)
      return (f'<g{filt}><path d="M{p0[0]:.0f} {p0[1]:.0f} Q{c[0]:.0f} {c[1]:.0f} {bx:.0f} {by:.0f}" fill="none" stroke="{col}" stroke-width="{a_["stroke"]}" stroke-linecap="round"/>'
              f'<path d="M{h[0][0]:.0f} {h[0][1]:.0f} L{p1[0]:.0f} {p1[1]:.0f} L{h[1][0]:.0f} {h[1][1]:.0f} Z" fill="{col}"/></g>')
    return (f'<g{filt} fill="none" stroke="{col}" stroke-width="{a_["stroke"]}" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M{p0[0]:.0f} {p0[1]:.0f} Q{c[0]:.0f} {c[1]:.0f} {p1[0]:.0f} {p1[1]:.0f}"/><path d="M{h[0][0]:.0f} {h[0][1]:.0f} L{p1[0]:.0f} {p1[1]:.0f} L{h[1][0]:.0f} {h[1][1]:.0f}"/></g>')
  if sh in ("dashed-box", "code-mark"):
    x0, y0, x1, y1 = geo["bbox"]
    d = st["dashed"] if sh == "dashed-box" else s
    return f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{x1 - x0:.0f}" height="{y1 - y0:.0f}" rx="{d["rx"]}" fill="none" stroke="{C(s["color"])}" stroke-width="{d["stroke"]}" stroke-dasharray="{d["dash"]}"/>'
  if sh == "tag":
    x, y = geo["xy"]
    w = text_width(l["text"], s["font_size"]) + 2 * s["pad_x"]
    return (f'<g filter="url(#tag-shadow)"><rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{s["height"]}" fill="{C(s["bg"])}" fill-opacity="{s["bg_opacity"]}"/>'
            f'<rect x="{x:.0f}" y="{y + s["height"] - s["underline"]:.0f}" width="{w:.0f}" height="{s["underline"]}" fill="{C(s["line"])}"/>'
            f'<text x="{x + s["pad_x"]:.0f}" y="{y + s["base"]:.0f}" font-family="{s["font"]}" font-weight="{s["font_weight"]}" font-size="{s["font_size"]}" fill="{C(s["text_color"])}">{html.escape(l["text"])}</text></g>')
  if sh == "cross":
    (mx, my), d, cr = geo["m"], s["size"] / 2, st["cross"]
    filt = f' filter="url(#{cr["filter"]})"' if cr["filter"] else ""
    return (f'<g{filt} stroke="{C(s["color"])}" stroke-width="{cr["stroke"]}" stroke-linecap="round">'
            f'<path d="M{mx - d:.0f} {my - d:.0f} L{mx + d:.0f} {my + d:.0f}"/><path d="M{mx + d:.0f} {my - d:.0f} L{mx - d:.0f} {my + d:.0f}"/></g>')
  raise ValueError(sh)


def scene_svg(spec):
  g = layout(spec)
  sub = spec["subs"][-1][2] if spec["subs"] else ""
  body = "\n".join(f'  <g data-layer="{l["name"]}" data-shape="{l["shape"]}">{draw(spec, l, g)}</g>' for l in spec["layers"])
  th = spec["theme"]
  return (f'<svg xmlns="{NS}" viewBox="0 0 1920 1080" data-bg="flat:{color(spec, "BG")}" data-theme="{th["palette"]}/{th["shape"]}" '
          f'data-subtitle="" data-preview-subtitle="{html.escape(sub)}">\n{body}\n</svg>\n')


def renderer():
  spec = importlib.util.spec_from_file_location("render_gouache", RENDER)
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod


def build(spec_path, out):
  spec, out = load_spec(spec_path), Path(out)
  out.mkdir(parents=True, exist_ok=True)
  svg = out / f"{spec['id']}.svg"
  svg.write_text(scene_svg(spec))
  r = renderer()
  still = out / f"{spec['id']}_still.png"
  r.render(svg, still, out / f"{spec['id']}_layers")
  sub = spec["subs"][-1][2] if spec["subs"] else ""
  if sub:  # 미리보기 자막은 팔레트 SUB 색(Resolve 자막 트랙 Color와 같은 값)
    from PIL import Image
    t = r.raster(f'<svg xmlns="{NS}" viewBox="0 0 1920 1080"><text x="960" y="950" text-anchor="middle" font-family="Pretendard" font-weight="500" font-size="42" fill="{color(spec, "SUB")}">{html.escape(sub)}</text></svg>')
    Image.alpha_composite(Image.open(still).convert("RGBA"), t).convert("RGB").save(still)
  print(f"built {svg}")


# ---------- 자막 시각 ----------

def syllables(text):
  """한글·숫자 1자 = 1음절, 대문자 약어 = 글자 수 × 1.3(올림), 그 밖의 영문 단어 = 모음 묶음 수(최소 1)."""
  n = sum(1 for c in text if "가" <= c <= "힣" or c.isdigit())
  for w in re.findall(r"[A-Za-z]+", text):
    n += math.ceil(len(w) * 1.3) if w.isupper() else max(1, len(re.findall(r"[aeiouy]+", w.lower())))
  return n


def timing(texts):
  """자막 문장 → [[시작, 끝, 문장]]. 길이 = 음절 / 5.5 + 0.4초(0.1초 올림), 자막 사이 0.1초."""
  out, t = [], 0.0
  for x in texts:
    end = round(t + math.ceil((syllables(x) / 5.5 + 0.4) * 10) / 10, 1)
    out.append([round(t, 1), end, x])
    t = end + 0.1
  return out


# ---------- 채점 ----------

def punch_zoom(meta, names):
  bb = [l["bbox"] for l in meta["layers"] if l["name"] in names]
  x0, y0 = min(b[0] for b in bb), min(b[1] for b in bb)
  x1, y1 = max(b[2] for b in bb), max(b[3] for b in bb)
  cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
  if cy >= 860:
    return 0, (0.5, 0.5)
  m = min(cx / (cx - x0 + 40), (1920 - cx) / (x1 - cx + 40), cy / (cy - y0 + 40), (1080 - cy) / (y1 - cy + 40), (860 - cy) / (y1 - cy))
  return round(min(1.8, m), 2), (round(cx / 1920, 4), round(1 - cy / 1080, 4))


def gap(a, b):
  return max(b[0] - a[2], a[0] - b[2], b[1] - a[3], a[1] - b[3])


def check_scene(spec, out):
  sid = spec["id"]
  svg_text = (out / f"{sid}.svg").read_text()
  root = ET.fromstring(svg_text)
  meta = json.loads((out / f"{sid}_layers/layers.json").read_text())
  groups = [el for el in root if el.get("data-layer")]
  starts = [s[0] for s in spec["subs"]]
  ats = [l["at"] for l in spec["layers"]]
  geo = layout(spec)
  objs = [geo[l["name"]]["bbox"] for l in spec["layers"] if SHAPES[l["shape"]].get("object")]
  onames = [l["name"] for l in spec["layers"] if SHAPES[l["shape"]].get("object")]
  r, why = {}, {}
  th = spec["theme"]
  r["S01"] = root.get("data-bg") == f"flat:{color(spec, 'BG')}"
  ok2 = True
  for g_, l in zip(groups, spec["layers"]):
    if l["shape"] == "tag":
      rects = list(g_.iter(f"{{{NS}}}rect"))
      txts = list(g_.iter(f"{{{NS}}}text"))
      ok2 &= len(rects) == 2 and len(txts) == 1 and rects[0].get("height") == str(SHAPES["tag"]["height"]) and txts[0].get("font-size") == str(SHAPES["tag"]["font_size"])
  r["S02"] = ok2
  r["S03"] = root.get("data-theme") == f"{th['palette']}/{th['shape']}"
  r["S04"] = not re.search(r"url\(#(glow|halo|spot)", svg_text) and not any(l["name"].endswith("-halo") for l in spec["layers"])
  pal = {v.upper() for v in PALETTES[th["palette"]]["colors"].values()}
  r["S05"] = all(c.upper() in pal for c in re.findall(r"#[0-9A-Fa-f]{6}\b", svg_text))
  r["S06"] = [g.get("data-shape") for g in groups] == [l["shape"] for l in spec["layers"]] and all(l["shape"] in SHAPES for l in spec["layers"])
  ok7 = True
  for g, l in zip(groups, spec["layers"]):
    s = SHAPES.get(l["shape"], {})
    if s.get("kind") != "static":
      continue
    inner = g[0]
    m = re.fullmatch(r"translate\(([-\d.]+) ([-\d.]+)\)", inner.get("transform", ""))
    fills = [e for e in inner.iter() if e.tag.split("}")[1] in ("circle", "path") and e.get("fill", "").startswith("#")]
    want_fill = color(spec, s["color"]).upper()
    want = [(p["t"], {k: str(v) for k, v in p.items() if k != "t"}) for p in s["prims"]]
    got = [(e.tag.split("}")[1], {k: e.get(k) for k in w[1]}) for e, w in zip(fills, want)]
    ok7 &= bool(m) and got == want and len(fills) == len(want) and all(e.get("fill").upper() == want_fill for e in fills)
  r["S07"] = ok7
  subs = spec["subs"]
  r["S08"] = all(len(t) <= 24 and "\n" not in t and a < b <= spec["dur"] + 1e-6 for a, b, t in subs) and all(subs[i][1] <= subs[i + 1][0] for i in range(len(subs) - 1))
  r["S09"] = all(a == -1 or any(abs(a - (st + 0.3 * k)) <= 0.01 for st in starts for k in range(4)) for a in ats)
  r["S10"] = all(sum(abs(b - a) <= 0.01 for b in ats if b != -1) <= 2 for a in ats if a != -1)
  p = spec.get("punch")
  if p:
    zoom, _ = punch_zoom(meta, p["targets"])
    names = {l["name"] for l in spec["layers"]}
    r["S11"] = set(p["targets"]) <= names and p["at"] <= spec["dur"] - 1.0 + 1e-6 and zoom >= 1.3
    why["S11"] = f"펀치 인 {p['at']}초(장면 끝 1.0초 전 이하여야 함, 장면 {spec['dur']}초), 배율 {zoom}(1.3 이상)"
  else:
    r["S11"] = True
  why["S12"] = [m["name"] for m in meta["layers"] if not (40 <= m["bbox"][0] and m["bbox"][2] <= 1880 and 40 <= m["bbox"][1] and m["bbox"][3] <= 860)]
  why["S09"] = [l["name"] for l in spec["layers"] if not (l["at"] == -1 or any(abs(l["at"] - (st + 0.3 * k)) <= 0.01 for st in starts for k in range(4)))]
  r["S12"] = all(40 <= m["bbox"][0] and m["bbox"][2] <= 1880 and 40 <= m["bbox"][1] and m["bbox"][3] <= 860 for m in meta["layers"])
  near = [(onames[i], onames[j], gap(objs[i], objs[j])) for i in range(len(objs)) for j in range(i + 1, len(objs)) if gap(objs[i], objs[j]) < 120]
  r["S13"] = 1 <= len(objs) <= 4 and not near
  why["S13"] = f"object {len(objs)}개, 120px 미만 간격 {near}"
  ok14 = True
  for l in spec["layers"]:
    if l["shape"] != "code-card":
      continue
    f = spec["_dir"] / l["file"]
    src = f.read_text().splitlines()
    texts = [t.text or "" for t in root.iter(f"{{{NS}}}text") if t.get("font-family") == SHAPES["code-card"]["font"]]
    a, b = l["lines"]
    want = [f"$ cat {f.name}"] + (["..."] if a > 1 else []) + src[a - 1:b] + (["..."] if b < len(src) else [])
    ok14 &= texts == want
  for l in spec["layers"]:
    if l["shape"] == "code-mark":
      card = next(c for c in spec["layers"] if c["name"] == l["card"])
      src = (spec["_dir"] / card["file"]).read_text().splitlines()
      ok14 &= card["lines"][0] <= l["line"] <= card["lines"][1] and src[l["line"] - 1].strip() not in ("", "{", "}")
  r["S14"] = ok14
  r["S15"] = [m["name"] for m in meta["layers"]] == [l["name"] for l in spec["layers"]]
  last = max(b for _, b, _ in subs)
  r["S16"] = spec.get("timed") != "recording" or last - 1e-6 <= spec["dur"] <= last + 0.5 + 1e-6
  g = geo
  walls = [g[l["name"]]["bbox"] for l in spec["layers"] if SHAPES[l["shape"]].get("object") or l["shape"] == "dashed-box"]
  inside = lambda pt, b: b[0] < pt[0] < b[2] and b[1] < pt[1] < b[3]
  want = timing([t for _, _, t in subs])
  r["S18"] = spec.get("timed") == "recording" or (all(abs(a - c) <= 0.01 and abs(b - d) <= 0.01 for (a, b, _), (c, d, _) in zip(subs, want)) and abs(spec["dur"] - want[-1][1]) <= 0.01)
  why["S18"] = f"scene.py timing 결과 {[(a, b) for a, b, _ in want]}, dur {want[-1][1]}"
  cross_ = [l["name"] for l in spec["layers"] if l["shape"] == "arrow" and any(inside(pt, b) for pt in curve(g[l["name"]]["p0"], g[l["name"]]["c"], g[l["name"]]["p1"]) for b in walls)]
  r["S17"] = not cross_
  why["S17"] = f"object·점선 상자를 지나는 화살표 {cross_}"
  return r, meta, why


def check(out, spec_paths):
  out = Path(out)
  specs = [load_spec(p) for p in spec_paths]
  ids = [c["id"] for c in CHECKS]
  results, metas, fails, whys = {}, {}, [], {}
  for s in specs:
    r, metas[s["id"]], why = check_scene(s, out)
    results[s["id"]] = r
    whys[s["id"]] = why
  x = {}
  roots = [ET.parse(out / f"{s['id']}.svg").getroot() for s in specs]
  x["X01"] = len({(r.get("data-bg"), r.get("data-theme")) for r in roots}) == 1
  seen, ok2 = {}, True
  for s in specs:
    for l, m in zip(s["layers"], metas[s["id"]]["layers"]):
      if l["shape"] in ("box", "db"):
        key = (l["shape"], l.get("label", l["name"]))
        val = (l.get("role"), tuple(size_of(l)))
        ok2 &= seen.setdefault(key, val) == val
  x["X02"] = ok2
  cys = set()
  for s in specs:
    for l, m in zip(s["layers"], metas[s["id"]]["layers"]):
      if l["name"] in s.get("row", []):
        cys.add(round((m["bbox"][1] + m["bbox"][3]) / 2 / 10))  # 10px 단위(질감 필터의 가장자리 흔들림 흡수)
  x["X03"] = len(cys) <= 1
  ok4 = True
  for s in specs:
    if "_base" in s and s["_base"]["id"] in metas:
      base = {m["name"]: m["bbox"] for m in metas[s["_base"]["id"]]["layers"]}
      ok4 &= all(m["bbox"] == base[m["name"]] for l, m in zip(s["layers"], metas[s["id"]]["layers"]) if l.get("_inherited"))
  x["X04"] = ok4
  assert set(ids) == {k for r in results.values() for k in r} | set(x), "checklist.jsonl과 구현이 다르다"
  lines, worst = [], 1.0
  for sid, r in list(results.items()) + [("set", x)]:
    score = sum(r.values()) / len(r)
    worst = min(worst, score)
    bad = [k for k, v in r.items() if not v]
    lines.append(f"{sid}: {sum(r.values())}/{len(r)} = {score:.0%}" + (f"  실패 {bad}" if bad else ""))
    lines += [f"  {k}: {whys.get(sid, {}).get(k, CHECK_TEXT[k])}" for k in bad]
    fails += [(sid, k) for k in bad]
  print("\n".join(lines))
  print(f"최저 {worst:.0%} (기준 95%)")
  return worst >= 0.95, fails


# ---------- Resolve comp ----------

COMP = """Composition {{
\tCurrentTime = 0,
\tRenderRange = {{ 0, {last} }},
\tGlobalRange = {{ 0, {last} }},
\tCurrentID = 2,
\tHiQ = true,
\tPlaybackUpdateMode = 0,
\tVersion = "DaVinci Resolve Studio 21.1.1.0010",
\tSavedOutputs = 0,
\tHeldTools = 0,
\tDisabledTools = 0,
\tLockedTools = 0,
\tAudioOffset = 0,
\tResumable = true,
\tOutputClips = {{
\t}},
\tCustomData = {{
\t\tTEMPLATE_ID = "Fusion Generator"
\t}},
\tTools = {{
\t\t{tools}
\t}},
\tFrames = {{
\t}},
\tPrefs = {{
\t\tComp = {{
\t\t\tFrameFormat = {{ Rate = {fps}, GuideRatio = 1.77777777777778, DepthFull = 3, DepthPreview = 3, DepthInteractive = 3, }},
\t\t\tUnsorted = {{ GlobalEnd = {last} }},
\t\t}}
\t}},
}}
"""


def q(n, d, at="At"):
  return f"min(1, max(0, (time - (comp.RenderStart + Timing.{at}{n} * {FPS})) / ({d} * {FPS})))"


def motion_expr(n, motion):
  if motion == "pop":
    k = f"({q(n, 0.3)} - 1)"
    return f"0.6 + 0.4 * (1 + 2.70158*{k}*{k}*{k} + 1.70158*{k}*{k})", f"Timing.On{n} * {q(n, 0.12)}"
  if motion == "draw":
    k = f"(1 - {q(n, 0.25)})"
    return f"0.85 + 0.15*(1 - {k}*{k})", f"Timing.On{n} * {q(n, 0.2)}"
  return None, f"Timing.On{n} * {q(n, 0.25)}"


def ctl(key, name, kind, default, lo=0, hi=10):
  if kind == "check":
    return f'{key} = {{ LINKS_Name = "{name}", LINKID_DataType = "Number", INPID_InputControl = "CheckboxControl", INP_Default = {default}, INP_Integer = true, CBC_TriState = false, ICS_ControlPage = "Controls", }},'
  return f'{key} = {{ LINKS_Name = "{name}", LINKID_DataType = "Number", INPID_InputControl = "SliderControl", INP_Default = {default}, INP_MinScale = {lo}, INP_MaxScale = {hi}, INP_MinAllowed = -1, INP_MaxAllowed = 100, ICS_ControlPage = "Controls", }},'


def comp(spec_path, out):
  spec, out = load_spec(spec_path), Path(out)
  d = (out / f"{spec['id']}_layers").resolve()
  meta = json.loads((d / "layers.json").read_text())
  frames = round(spec["dur"] * FPS)
  by_name = {l["name"]: l for l in spec["layers"]}
  tools, uc, vals, inst = [], [], [], []

  def loader(name, png, y):  # 한글 노드 이름은 ["..."] 키로 써야 Resolve가 읽는다
    tools.append(f'["{name}"] = Loader {{ Clips = {{ Clip {{ ID = "Clip1", Filename = "{png}", FormatID = "PNGFormat", StartFrame = -1, LengthSetManually = true, TrimIn = 0, TrimOut = 0, ExtendFirst = 0, ExtendLast = {frames}, Loop = 0, AspectMode = 0, Depth = 0, TimeCode = 0, GlobalStart = 0, GlobalEnd = {frames - 1} }} }}, Inputs = {{ ["Clip1.PNGFormat.PostMultiply"] = Input {{ Value = 1, }}, }}, ViewInfo = OperatorInfo {{ Pos = {{ 0, {y} }} }}, }},')

  loader("배경", d / meta["background"], 0)
  mm, order = ['Background = Input { SourceOp = "배경", Source = "Output", },'], []
  for n, L in enumerate(meta["layers"], 1):
    key, l = L["name"].replace("-", "_"), by_name[L["name"]]
    size, blend = motion_expr(n, SHAPES[l["shape"]]["motion"])
    loader(f"그림_{key}", d / L["file"], 33 * n)
    px, py = L["pivot"]  # Center를 같이 바꾸면 그림이 옮겨진다. Pivot만 준다
    size_in = f'Size = Input {{ Expression = "{size}", }},' if size else ""
    tools.append(f'["등장_{key}"] = Transform {{ Inputs = {{ Pivot = Input {{ Value = {{ {px}, {py} }}, }}, {size_in} Input = Input {{ SourceOp = "그림_{key}", Source = "Output", }}, }}, ViewInfo = OperatorInfo {{ Pos = {{ 110, {33 * n} }} }}, }},')
    mm += [f'["Layer{n}.Foreground"] = Input {{ SourceOp = "등장_{key}", Source = "Output", }},', f'["Layer{n}.Blend"] = Input {{ Expression = "{blend}", }},', f'LayerName{n} = Input {{ Value = "{L["name"]}", }},']
    order.append(str(n))
    uc += [ctl(f"On{n}", f"보이기 · {L['name']}", "check", 1), ctl(f"At{n}", f"등장 시점(초) · {L['name']}", "slider", l["at"], -1, spec["dur"])]
    vals += [f"On{n} = Input {{ Value = 1, }},", f"At{n} = Input {{ Value = {l['at']}, }},"]
    inst += [(f"On{n}", f"보이기 · {L['name']}", 1), (f"At{n}", f"등장 시점(초) · {L['name']}", l["at"])]
  tools.append(f'["레이어_합성"] = MultiMerge {{ Inputs = {{ LayerOrder = Input {{ Value = ScriptVal {{ {{ [0] = {", ".join(order)} }} }}, }}, {" ".join(mm)} }}, ViewInfo = OperatorInfo {{ Pos = {{ 220, 0 }} }}, }},')
  zoom, piv, pat = 1, (0.5, 0.5), 99
  if spec.get("punch"):
    zoom, piv = punch_zoom(meta, spec["punch"]["targets"])
    pat = spec["punch"]["at"]
  k = f"(1 - {q('', 0.2, 'PunchAt')})"
  tools.append(f'["레이어_목록"] = Transform {{ Inputs = {{ Pivot = Input {{ Value = {{ {piv[0]}, {piv[1]} }}, }}, Size = Input {{ Expression = "1 + (Timing.PunchZoom - 1) * (1 - {k}*{k}*{k})", }}, Input = Input {{ SourceOp = "레이어_합성", Source = "Output", }}, }}, ViewInfo = OperatorInfo {{ Pos = {{ 330, 0 }} }}, }},')
  uc += [ctl("PunchAt", "펀치 인 시점(초)", "slider", pat, 0, spec["dur"]), ctl("PunchZoom", "펀치 인 배율", "slider", zoom, 1, 2)]
  vals += [f"PunchAt = Input {{ Value = {pat}, }},", f"PunchZoom = Input {{ Value = {zoom}, }},"]
  inst += [("PunchAt", "펀치 인 시점(초)", pat), ("PunchZoom", "펀치 인 배율", zoom)]
  tools.append(f'Timing = Background {{ CtrlWZoom = false, Inputs = {{ Width = Input {{ Value = 1920, }}, Height = Input {{ Value = 1080, }}, {" ".join(vals)} }}, ViewInfo = OperatorInfo {{ Pos = {{ 330, -66 }} }}, UserControls = ordered() {{ {" ".join(uc)} }}, }},')
  ii = " ".join(f'Input{i} = InstanceInput {{ SourceOp = "Timing", Source = "{key}", Name = "{nm}", Default = {dv}, }},' for i, (key, nm, dv) in enumerate(inst, 1))
  macro = (f'Template = MacroOperator {{ CtrlWZoom = false, Inputs = ordered() {{ {ii} }}, Outputs = {{ MainOutput1 = InstanceOutput {{ SourceOp = "레이어_목록", Source = "Output", }}, }}, '
           f'ViewInfo = GroupInfo {{ Pos = {{ 0, 0 }} }}, Tools = ordered() {{ {chr(10).join(tools)} }}, }},\n'
           '\t\tMediaOut1 = Saver { Inputs = { Index = Input { Value = "0", }, Input = Input { SourceOp = "레이어_목록", Source = "Output", }, }, ViewInfo = OperatorInfo { Pos = { 550, 0 } }, }')
  path = out / f"{spec['id']}.comp"
  path.write_text(COMP.format(last=frames - 1, tools=macro, fps=FPS))
  print(f"comp {path} punch {zoom}")


# ---------- selftest ----------

def selftest():
  assert syllables("PHP가 크기 한도를") == 10 and syllables("Cache") == 2, syllables("PHP가 크기 한도를")
  for pid, p in PALETTES.items():
    assert set(p["colors"]) == set(PAL_KEYS), f"{pid} 팔레트 키가 _keys와 다르다"
  ex = REF / "example"
  specs = sorted(ex.glob("*/s*.json"))
  assert specs, "references/example/*/s*.json이 없다"
  with tempfile.TemporaryDirectory() as d:
    for group in sorted({p.parent for p in specs}):
      for pid in PALETTES:
        for sid in STYLES:
          src = Path(d) / f"spec-{group.name}-{pid}-{sid}"  # 같은 spec을 팔레트·도형 스타일마다 빌드
          src.mkdir()
          for f in group.iterdir():
            t = f.read_text()
            if f.name.startswith("s") and f.suffix == ".json":
              j = json.loads(t)
              if "extends" not in j:
                j["theme"] = {"palette": pid, "shape": sid}
              t = json.dumps(j, ensure_ascii=False)
            (src / f.name).write_text(t)
          out = Path(d) / f"out-{group.name}-{pid}-{sid}"
          paths = sorted(src.glob("s*.json"))
          for p in paths:
            build(p, out)
            comp(p, out)
            assert (out / f"{load_spec(p)['id']}.comp").read_text().count("Loader") >= 2
          ok, fails = check(out, paths)
          assert ok and not fails, (group.name, pid, sid, fails)
    for group in sorted({p.parent for p in specs}):
      out = Path(d) / group.name
      paths = sorted(group.glob("s*.json"))
      for p in paths:
        build(p, out)
    # 망가뜨린 SVG는 떨어져야 한다
    g = sorted({p.parent for p in specs})[0]
    out = Path(d) / g.name
    first = sorted(g.glob("s*.json"))[0]
    svg = out / f"{load_spec(first)['id']}.svg"
    svg.write_text(svg.read_text().replace('r="84"', 'r="70"', 1).replace("</svg>", '<g data-layer="x"><circle r="9" fill="url(#glow)"/></g></svg>'))
    _, fails = check(out, [first])
    assert {k for _, k in fails} >= {"S04", "S07"}, fails
  print("selftest ok")


if __name__ == "__main__":
  ap = argparse.ArgumentParser()
  ap.add_argument("cmd", nargs="?", choices=["build", "check", "comp", "timing"])
  ap.add_argument("args", nargs="*")
  ap.add_argument("--selftest", action="store_true")
  a = ap.parse_args()
  if a.selftest:
    selftest()
  elif a.cmd == "build":
    build(a.args[0], a.args[1])
  elif a.cmd == "comp":
    comp(a.args[0], a.args[1])
  elif a.cmd == "timing":
    subs = timing(a.args)
    print(json.dumps({"subs": subs, "dur": subs[-1][1]}, ensure_ascii=False))
  elif a.cmd == "check":
    ok, _ = check(a.args[0], a.args[1:])
    sys.exit(0 if ok else 1)
  else:
    ap.error("build|check|comp 또는 --selftest")
