"""haru 스타일 다이어그램 이미지 생성 프롬프트를 spec(JSON)에서 조립하고 채점한다.

  build <spec.json> [-o prompt.txt]   채점 후 100점이면 프롬프트를 쓴다(없으면 stdout)
  check <spec.json>                   채점표만 출력
  spec과 같은 폴더의 shapes.jsonl·palettes.jsonl은 라이브러리에 더한다(새 id만)
  center <in.png> [-o out.png]        그림 덩어리를 캔버스 가운데로 옮기고 전후 여백을 출력(Pillow 필요)
  --selftest                          자체 검사
"""
import json
import re
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"

# 모델이 쓴 글에 나오면 안 되는 말(복수형 포함). 상표·캐릭터와 스타일을 깨는 표현.
BANNED = ("logo", "trademark", "mascot", "3d", "isometric", "photorealistic", "realistic", "gradient", "neon", "shadow")
BANNED_RE = re.compile(rf"\b({'|'.join(BANNED)})s?\b", re.I)

# spec에 쓸 수 있는 키. 이 밖의 키(예: icon)는 감점한다.
KEYS = {
  "spec": {"palette", "layout", "subject", "titles", "nodes", "edges", "notes", "groups", "spans"},
  "groups": {"id", "label", "members"},
  "nodes": {"id", "label", "shape", "same"},
  "edges": {"from", "to", "kind", "label", "step", "chip", "wait"},
  "notes": {"node", "edge", "text"},
  "spans": {"first", "last", "label"},
}


def load(name):
  lines = (REF / f"{name}.jsonl").read_text(encoding="utf-8").splitlines()
  return {r["id"]: r for r in map(json.loads, filter(None, lines))}


LIB = {name: load(name) for name in ("style", "palettes", "layouts", "shapes", "edges", "groups")}
# 배치 라우팅은 layouts.jsonl이 정한다. 줄에 key가 있으면 모든 도형이 그 키(values 중 하나)로 칸을 고른다.
LAYOUT_KEYS = sorted({l["key"] for l in LIB["layouts"].values() if "key" in l})
KEYS["nodes"] |= set(LAYOUT_KEYS)
# 작업 폴더에서 더할 수 있는 라이브러리와 줄마다 있어야 하는 필드.
LOCAL = {"shapes": {"id", "ko", "prompt"}, "palettes": {"id", "use", "ink", "bg", "chips"}}


def extend(folder):
  """spec 폴더의 shapes.jsonl·palettes.jsonl 줄을 LIB에 더한다. 기존 id를 덮거나 필드가 틀리면 멈춘다."""
  for lib, need in LOCAL.items():
    path = Path(folder) / f"{lib}.jsonl"
    if not path.exists():
      continue
    for r in map(json.loads, filter(None, path.read_text(encoding="utf-8").splitlines())):
      typed = all(isinstance(v, dict if k == "chips" else str) for k, v in r.items()) and all(isinstance(v, str) for v in r.get("chips", {}).values())
      if r.get("id") in LIB[lib] or set(r) != need or not typed:
        sys.exit(f"{path}: id {r.get('id')}는 새 id여야 하고 필드는 {sorted(need)}(chips는 색 이름→hex 객체, 나머지는 글자)")
      LIB[lib][r["id"]] = r


def text_ok(s, hi):
  """1~hi자(공백 포함), 영어(ASCII)·한글만, 큰따옴표 없음."""
  return isinstance(s, str) and 1 <= len(s) <= hi and '"' not in s and all(ch.isascii() or "가" <= ch <= "힣" for ch in s)


def name(node):
  return " ".join(node.get("label", []))


def unknown_keys(spec):
  found = set(spec) - KEYS["spec"]
  for part in ("nodes", "edges", "notes", "groups", "spans"):
    for item in spec.get(part, []):
      found |= {f"{part}.{k}" for k in set(item) - KEYS[part]}
  return sorted(found)


def lay_of(spec):
  return LIB["layouts"].get(spec.get("layout"), {})


def key_ok(nodes, key, lay):
  """배치 줄의 key가 이 key면 모든 도형이 values 중 하나를 갖고 2칸 이상으로 나뉜다. 아니면 key가 없다."""
  if lay.get("key") != key:
    return not any(key in n for n in nodes)
  return all(n.get(key) in lay["values"] and type(n[key]) is not bool for n in nodes) and len({n[key] for n in nodes}) >= 2


def titles_ok(spec):
  """배치 줄에 title이 있으면 titles가 values 칸마다 제목(각 1~20자)이고, 없으면 titles가 없다."""
  lay = lay_of(spec)
  if "title" not in lay:
    return "titles" not in spec
  titles = spec.get("titles")
  return (isinstance(titles, dict) and set(titles) == set(lay["values"])
          and all(isinstance(t, str) and text_ok(t, 20) for t in titles.values()))


def chips_ok(spec):
  """chip은 이름 붙은 화살표에만, 팔레트 chips의 색 이름 하나."""
  chips = LIB["palettes"].get(spec.get("palette"), {}).get("chips", {})
  return all(e.get("label") and isinstance(e["chip"], str) and e["chip"] in chips for e in spec.get("edges", []) if "chip" in e)


def sequence_ok(spec):
  """sequence 배치면 묶음·step·sync-pair·도형 메모 없이 wait·spans(겹치지 않게)·화살표 메모를 쓸 수 있고, 다른 배치면 셋 다 없다."""
  es, spans, notes = spec.get("edges", []), spec.get("spans", []), spec.get("notes", [])
  edge_notes = [x for x in notes if "edge" in x]
  if not lay_of(spec).get("sequence"):
    return not spans and not edge_notes and not any("wait" in e for e in es)
  n = len(es)
  ranges = sorted((x.get("first"), x.get("last")) for x in spans if type(x.get("first")) is int and type(x.get("last")) is int)
  return (not spec.get("groups") and not any("step" in e or e.get("kind") == "sync-pair" for e in es)
          and len(edge_notes) == len(notes) and all(a[1] < b[0] for a, b in zip(ranges, ranges[1:]))
          and all(text_ok(e["wait"], 14) for e in es if "wait" in e)
          and len(spans) <= 2 and all(type(x.get("first")) is int and type(x.get("last")) is int and 1 <= x["first"] < x["last"] <= n
                                      and isinstance(x.get("label"), list) and 1 <= len(x["label"]) <= 2 and all(text_ok(l, 14) for l in x["label"]) for x in spans)
          and all(type(x["edge"]) is int and 1 <= x["edge"] <= n for x in edge_notes))


def side_of(spec):
  """판이 있는 배치에서 도형·묶음 id → 판. 묶음은 안에 든 도형의 판이고, 두 판에 걸치면 None."""
  lay = lay_of(spec)
  side = {n.get("id"): n.get(lay.get("key")) for n in spec.get("nodes", [])}
  gs = spec.get("groups", [])
  for _ in gs:  # 중첩 묶음까지 퍼지도록 묶음 수만큼 반복
    for g in gs:
      vals = {side.get(m) for m in g.get("members", [])}
      side[g.get("id")] = vals.pop() if len(vals) == 1 else None
  return side


def panels_ok(spec):
  """판이 있는 배치면 묶음이 한 판 안에만 있다(두 판에 걸친 경계는 판 테두리와 충돌)."""
  if "title" not in lay_of(spec):
    return True
  side = side_of(spec)
  return all(side.get(g.get("id")) is not None for g in spec.get("groups", []))


def same_ok(spec):
  """same은 판이 있는 배치에서만, 다른 판에 있는 같은 도형·같은 이름의 도형 id를 가리킨다."""
  nodes, lay = spec.get("nodes", []), lay_of(spec)
  by_id = {n.get("id"): n for n in nodes}
  for n in nodes:
    if "same" not in n:
      continue
    t, key = by_id.get(n["same"]), lay.get("key")
    if "same" not in lay or not t or t is n or t.get(key) == n.get(key) or t.get("shape") != n.get("shape") or t.get("label") != n.get("label") or "same" in t:
      return False
  return True


def steps_ok(spec):
  """step은 그림 전체에서 1부터 빠짐없이 잇거나, 판이 있는 배치면 판마다 1부터 다시 시작해도 된다(판 = from 도형의 판)."""
  es, lay = spec.get("edges", []), lay_of(spec)

  def run(steps):
    return all(type(n) is int for n in steps) and sorted(steps) == list(range(1, len(steps) + 1))

  steps = [e["step"] for e in es if "step" in e]
  if len(steps) == 1:
    return False
  if run(steps):
    return True
  if "title" not in lay:
    return False
  side = side_of(spec)
  per = [[e["step"] for e in es if "step" in e and side.get(e.get("from")) == v] for v in lay["values"]]
  return sum(map(len, per)) == len(steps) and all(len(p) != 1 and run(p) for p in per)


def groups_ok(spec):
  """묶음 0~4개. 멤버는 도형·다른 묶음 id, 각각 한 묶음에만 속하고, 순환 없이 3단계까지 중첩된다."""
  gs = spec.get("groups", [])
  node_ids = {n.get("id") for n in spec.get("nodes", [])}
  gids = [g.get("id") for g in gs]
  members = [m for g in gs for m in g.get("members", [])]
  if len(gs) > 4 or len(set(gids)) != len(gids) or set(gids) & node_ids or len(set(members)) != len(members):
    return False
  if not all(g.get("members") and set(g["members"]) <= node_ids | set(gids) and g["id"] not in g["members"] for g in gs):
    return False
  if not all(isinstance(g.get("label"), list) and len(g["label"]) == 1 and text_ok(g["label"][0], 20) for g in gs):
    return False
  parent = {m: g["id"] for g in gs for m in g["members"]}
  for gid in gids:
    depth, cur = 1, gid
    while cur in parent:
      cur, depth = parent[cur], depth + 1
      if depth > 3:
        return False
  return True


def ancestors(spec, item):
  parent = {m: g["id"] for g in spec.get("groups", []) for m in g.get("members", [])}
  out = []
  while item in parent and len(out) < 4:
    item = parent[item]
    out.append(item)
  return out


def check(spec):
  """(항목, 통과 여부, 이유) 목록. 항목 하나 = 1점, 점수 = 통과 수 / 항목 수 × 100(내림)."""
  pal, lay, shapes, kinds = (LIB[n] for n in ("palettes", "layouts", "shapes", "edges"))
  layout, this = spec.get("layout"), lay_of(spec)
  lo, hi = lay[layout]["nodes"] if layout in lay else (0, 0)
  # ponytail: 묶음이 도형을 덩어리로 나눠 읽기 부담을 덜므로 묶음이 있으면 도형 상한을 3개 올린다
  hi += 3 if spec.get("groups") else 0
  nodes, es, notes = spec.get("nodes", []), spec.get("edges", []), spec.get("notes", [])
  subject = spec.get("subject", "")
  ids = [n.get("id") for n in nodes]
  ends = set(ids) | {g.get("id") for g in spec.get("groups", [])}
  labeled = [e for e in es if e.get("label")]
  steps = [e["step"] for e in es if "step" in e]
  linked = {e.get("from") for e in es} | {e.get("to") for e in es}
  words = len(subject.split())
  titles = spec.get("titles")
  free = " ".join([subject] + [str(e.get("wait", "")) for e in es] + [" ".join(x.get("label", [])) for x in spec.get("spans", []) if isinstance(x.get("label"), list)] + [str(t) for t in (titles.values() if isinstance(titles, dict) else [])] + [name(n) for n in nodes] + [name(g) for g in spec.get("groups", [])] + [e.get("label", "") for e in es] + [x.get("text", "") for x in notes])
  extra = unknown_keys(spec)
  return [
    ("keys", not extra, f"쓸 수 없는 키: {extra}"),
    ("palette", spec.get("palette") in pal, f"palettes.jsonl id: {sorted(pal)}"),
    ("layout", layout in lay, f"layouts.jsonl id: {sorted(lay)}"),
    ("node count", lo <= len(nodes) <= hi, f"도형 {len(nodes)}개, 배치 허용 {lo}~{hi}개(경계 포함)"),
    ("node ids", len(set(ids)) == len(ids) and all(ids), f"id 중복·빈 값 없이: {ids}"),
    ("shapes", all(n.get("shape") in shapes for n in nodes), f"shapes.jsonl id: {sorted(shapes)}"),
    ("labels", all(isinstance(n.get("label"), list) and 1 <= len(n["label"]) <= 2 and all(text_ok(l, 12) for l in n["label"]) for n in nodes),
     "도형 이름 1~2줄, 줄마다 1~12자(공백 포함), 영어·한글"),
    *[(key, key_ok(nodes, key, this), f"layouts.jsonl에서 key가 {key}인 배치면 모든 도형에 {key}(그 줄의 values), 2칸 이상, 아니면 {key} 없음")
      for key in LAYOUT_KEYS],
    ("titles", titles_ok(spec), "layouts.jsonl 줄에 title이 있으면 titles에 values 칸마다 제목(각 1~20자, 영어·한글), 아니면 titles 없음"),
    ("chips", chips_ok(spec), "chip은 이름 붙은 화살표에만, 팔레트 chips 색 이름 하나"),
    ("sequence", sequence_ok(spec), "sequence 배치면 groups·step 없음, wait 1~14자, spans 0~2개(first<last, 이름 1~2줄 각 1~14자), 메모 edge는 화살표 번호. 다른 배치면 wait·spans·edge 메모 없음"),
    ("panel groups", panels_ok(spec), "판이 있는 배치면 묶음은 한 판 안의 도형만 감쌈"),
    ("same", same_ok(spec), "same은 layouts.jsonl 줄에 same이 있을 때만, 다른 판의 같은 도형·이름 도형 id"),
    ("edge count", 1 <= len(es) <= 12, f"화살표 {len(es)}개, 1~12개"),
    ("edge ends", all(e.get("from") in ends and e.get("to") in ends and e["from"] != e["to"]
                      and e["to"] not in ancestors(spec, e["from"]) and e["from"] not in ancestors(spec, e["to"]) for e in es),
     "from·to는 서로 다른 도형·묶음 id, 자기를 감싼 묶음과는 잇지 않음"),
    ("groups", groups_ok(spec), "묶음 0~4개, 이름 1줄 1~20자, 멤버는 도형·묶음 id로 한 곳에만, 3단계 중첩까지"),
    ("edge kinds", all(e.get("kind") in kinds for e in es), f"edges.jsonl id: {sorted(kinds)}"),
    ("edge labels", len(labeled) <= 5 and all(text_ok(e["label"], 14) for e in labeled),
     f"이름 붙은 화살표 {len(labeled)}개, 0~5개, 각 1~14자"),
    ("steps", steps_ok(spec),
     f"step {steps}: 없거나, 2개 이상이면 1부터 빠짐없이 이어지는 정수(판이 있는 배치는 판마다 1부터도 됨)"),
    ("all linked", all(i in linked or set(ancestors(spec, i)) & linked for i in ids),
     f"화살표가 닿지 않은 도형(속한 묶음에도 닿지 않음): {sorted(i for i in ids if i not in linked and not set(ancestors(spec, i)) & linked)}"),
    ("notes", len(notes) <= 2 and all(("node" in x) != ("edge" in x) and x.get("node", ids[0] if ids else None) in ids and text_ok(x.get("text", ""), 32) for x in notes),
     "메모 0~2개, node(도형 id) 또는 edge(sequence의 화살표 번호) 하나, 각 1~32자"),
    ("subject", 6 <= words <= 30 and subject.isascii(), f"subject {words}단어, 6~30단어, 영어"),
    ("no banned words", not BANNED_RE.search(free), f"{'·'.join(BANNED)} 금지"),
  ]


def score(rows):
  return sum(ok for _, ok, _ in rows) * 100 // len(rows)


def build(spec):
  p = LIB["palettes"][spec["palette"]]
  style = LIB["style"]
  layout = LIB["layouts"][spec["layout"]]
  seq = layout.get("sequence")
  nodes = spec["nodes"]
  num = {n["id"]: i for i, n in enumerate(nodes, 1)}
  by_id = {n["id"]: n for n in nodes}

  groups = spec.get("groups", [])
  gnum = {g["id"]: chr(65 + i) for i, g in enumerate(groups)}
  gby = {g["id"]: g for g in groups}

  def ref(node_id):
    if node_id in gnum:
      return f'the outline of group {gnum[node_id]} ("{name(gby[node_id])}")'
    return f'{"the lifeline of " if seq else ""}shape {num[node_id]} ("{name(by_id[node_id])}")'

  def shape(n):
    text = " over ".join(f'"{l}"' for l in n["label"]) + (" on two lines" if len(n["label"]) == 2 else "")
    where = layout["where"].format(v=n[layout["key"]]) if "key" in layout else ""
    return f"{num[n['id']]}. {LIB['shapes'][n['shape']]['prompt']}{where} named {text}."

  def arrow(i, e):
    out = f"{i}. from {ref(e['from'])} to {ref(e['to'])}: {LIB['edges'][e['kind']]['prompt'].format(**p)}"
    if "wait" in e:
      out += f', drawn after extra empty vertical space above it, with "{e["wait"]}" in small {p["ink"]} lettering centered in that space'
    if "step" in e:
      out += f', with a small white circle outlined in {p["ink"]} holding the number "{e["step"]}" in {p["ink"]}, ' + ("placed just before its label" if e.get("label") else "beside the middle of the line")
    if e.get("label"):
      chip = f' on a flat pale rounded chip of {p["chips"][e["chip"]]} behind the text' if "chip" in e else ""
      out += f', labeled "{e["label"]}" in small {p["ink"]} lettering{chip} {"just above" if seq else "beside"} the line'
    return out + "."

  def group(g):
    inner = [f"group {gnum[m]}" if m in gnum else f"shape {num[m]}" for m in g["members"]]
    return (f'{gnum[g["id"]]}. {LIB["groups"]["boundary"]["prompt"].format(label=g["label"][0], **p)}. '
            f'It encloses {" and ".join([", ".join(inner[:-1]), inner[-1]] if len(inner) > 1 else inner)} fully inside it with clear padding.')

  def note(x):
    if "edge" in x:
      return f'Far to the right of the whole diagram, beyond any bracket and its name, level with arrow {x["edge"]}, a small note in {p["ink"]} lettering reads "{x["text"]}".'
    return f'Just below {ref(x["node"])}, a small note in {p["ink"]} lettering reads "{x["text"]}".'

  def span(x):
    text = " over ".join(f'"{l}"' for l in x["label"])
    return (f'A tall thin {p["ink"]} square bracket stands to the right of the rightmost lifeline, opening toward it and spanning from arrow {x["first"]} down to arrow {x["last"]}, '
            f'with {text} written in {p["ink"]} beside the bracket, outside it.')

  chips = sorted({e["chip"] for e in spec["edges"] if "chip" in e})
  titles = [layout["title"].format(v=v, text=spec["titles"][v], **p) for v in layout["values"]] if "titles" in spec else []
  same = [layout["same"].format(a=num[n["same"]], b=num[n["id"]], **p) for n in nodes if "same" in n]
  parts = [
    style["medium"]["prompt"],
    f"LAYOUT: {layout['prompt'].format(**p)}",
    f"SUBJECT: {spec['subject']}",
    "TITLES: " + " ".join(titles) if titles else "",
    f"SHAPES ({len(nodes)}): " + " ".join(map(shape, nodes)) + "".join(" " + x for x in same),
    (f"GROUPS ({len(groups)}): " + " ".join(map(group, groups)) +
     " Group outlines only enclose their members: a group inside another group sits wholly within it, and no group outline crosses a shape or another group." if groups else ""),
    f"ARROWS ({len(spec['edges'])}): " + " ".join(arrow(i, e) for i, e in enumerate(spec["edges"], 1)),
    "SPANS: " + " ".join(map(span, spec["spans"])) if spec.get("spans") else "",
    "NOTES: " + " ".join(map(note, spec["notes"])) if spec.get("notes") else "",
    "TEXT: The only words in the image are the quoted texts above, spelled exactly.",
    f"COLOR PALETTE: background {p['bg']}; ink {p['ink']} for every outline, arrow and letter" +
    (f"; pale label chips {', '.join(p['chips'][c] for c in chips)} only behind the arrow labels named with them, the same chip color for the same role" if chips else "") + ". Use no other colors.",
    "STYLE: " + " ".join(style[k]["prompt"].format(**p) for k in style if k not in ("medium", "avoid")),
    style["avoid"]["prompt"],
  ]
  return "\n\n".join(filter(None, parts))


def margins(box, size):
  """그림 덩어리 box(left, top, right, bottom)의 왼·오른·위·아래 여백(px)과 좌우·상하 차이(캔버스 대비 %)."""
  (l, t, r, b), (w, h) = box, size
  m = (l, w - r, t, h - b)
  return m, abs(m[0] - m[1]) * 100 / w, abs(m[2] - m[3]) * 100 / h


def center(src, dst):
  from PIL import Image, ImageChops
  im = Image.open(src).convert("RGB")
  bg = im.getpixel((0, 0))
  # ponytail: 모서리 픽셀을 배경으로 보고 20 넘게 다른 픽셀을 그림으로 본다. 모서리에 얼룩이 있으면 틀린다
  box = ImageChops.difference(im, Image.new("RGB", im.size, bg)).convert("L").point(lambda v: 255 if v > 20 else 0).getbbox()
  if not box:
    sys.exit("그림이 없는 빈 이미지")
  w, h = im.size
  x, y = (w - (box[2] - box[0])) // 2, (h - (box[3] - box[1])) // 2
  out = Image.new("RGB", im.size, bg)
  out.paste(im.crop(box), (x, y))
  out.save(dst)
  for tag, b in (("before", box), ("after", (x, y, x + box[2] - box[0], y + box[3] - box[1]))):
    m, dx, dy = margins(b, im.size)
    print(f"{tag:6} margin L{m[0]} R{m[1]} T{m[2]} B{m[3]} px, 좌우 차이 {dx:.1f}%, 상하 차이 {dy:.1f}%")


def report(rows):
  for n, ok, why in rows:
    print(f"{'PASS' if ok else 'FAIL'}  {n:16} {why}")
  print(f"score {score(rows)}")


def failed(spec):
  return {n for n, ok, _ in check(spec) if not ok}


def selftest():
  good = {
    "palette": "pastel", "layout": "loop",
    "subject": "A controller keeps comparing desired state with actual state and fixes the difference.",
    "nodes": [{"id": "spec", "label": ["Desired", "State"], "shape": "box"},
              {"id": "ctl", "label": ["Controller"], "shape": "box"},
              {"id": "db", "label": ["etcd"], "shape": "cylinder"}],
    "edges": [{"from": "spec", "to": "ctl", "kind": "call"},
              {"from": "ctl", "to": "db", "kind": "sync", "label": "watch"},
              {"from": "db", "to": "spec", "kind": "sync-pair"}],
    "notes": [{"node": "db", "text": "실제 상태 저장"}],
  }
  cache = {"id": "x", "label": ["Cache"], "shape": "box"}
  assert score(check(good)) == 100, check(good)
  out = build(good)
  assert '"Desired" over "State" on two lines' in out and "{" not in out
  assert 'from shape 2 ("Controller") to shape 3 ("etcd")' in out and '"watch"' in out
  assert '"실제 상태 저장"' in out
  assert "NOTES" not in build(dict(good, notes=[])) and "\n\n\n" not in build(dict(good, notes=[]))

  # 선·글자는 모두 잉크이고 색은 chip을 붙인 라벨 뒤에만 있다. 아이콘이 없고 그림은 화면 가운데에 놓인다.
  arrows = out.split("ARROWS")[1].split("NOTES")[0]
  assert "a straight solid #1E1E1E line" in arrows and " dot " not in out and "chip" not in arrows and "label chips #" not in out
  # 글자는 팔레트와 무관하게 모두 검정이고 강조색 글자가 없다.
  assert '"watch" in small #1E1E1E lettering beside the line' in out and "note in #1E1E1E lettering" in out
  assert "curved" not in arrows and "Arrows are straight lines" in out
  chipped = build(dict(good, edges=[good["edges"][0], dict(good["edges"][1], chip="pink")] + good["edges"][2:]))
  assert 'lettering on a flat pale rounded chip of #F7C6CC behind the text' in chipped and "pale label chips #F7C6CC only behind" in chipped
  assert failed(dict(good, edges=[dict(good["edges"][0], chip="pink")] + good["edges"][1:])) == {"chips"}
  assert failed(dict(good, edges=[good["edges"][0], dict(good["edges"][1], chip="purple")] + good["edges"][2:])) == {"chips"}
  assert "main" not in LIB["edges"] and failed(dict(good, edges=[dict(good["edges"][0], kind="main")] + good["edges"][1:])) == {"edge kinds"}
  assert " icon " not in out and "no icons or pictograms" in out
  assert "centered on the canvas both horizontally and vertically" in out
  assert "forming an X" in build(dict(good, edges=[dict(good["edges"][0], kind="blocked")] + good["edges"][1:]))
  assert out.rstrip().endswith(LIB["style"]["avoid"]["prompt"]) and out.count("DO NOT") == 1
  assert all(set(p) == LOCAL["palettes"] and isinstance(p["chips"], dict) for p in LIB["palettes"].values())
  # 배치 라우팅 필드: key가 있으면 values·where, title이 있으면 key, same이 있으면 title이 함께 있다.
  for l in LIB["layouts"].values():
    assert {"id", "pick", "ko", "nodes", "prompt"} <= set(l), l["id"]
    assert ("key" in l) == ("values" in l) == ("where" in l) and ("title" not in l or "key" in l) and ("same" not in l or "title" in l), l["id"]
  assert failed(dict(good, nodes=[dict(good["nodes"][0], icon="key")] + good["nodes"][1:])) == {"keys"}
  assert failed(dict(good, edges=[dict(good["edges"][1], icon="eye")] + good["edges"][:1] + good["edges"][2:])) == {"keys"}
  assert failed(dict(good, title="x")) == {"keys"}

  bad = dict(good, layout="hub", palette="pink",
             nodes=good["nodes"] + [{"id": "ctl", "label": ["A very long label"], "shape": "hexagon"}],
             edges=good["edges"] + [{"from": "ctl", "to": "ctl", "kind": "arrow"}],
             subject="Our logos in 3d.")
  assert {"palette", "node ids", "shapes", "labels", "edge ends", "edge kinds", "subject", "no banned words"} <= failed(bad), failed(bad)
  assert failed(dict(good, layout="row", nodes=good["nodes"] + [cache])) == {"all linked"}
  assert score(check(dict(good, nodes=[dict(good["nodes"][0], label=['Say "hi"'])] + good["nodes"][1:]))) < 100
  assert "labels" in failed(dict(good, nodes=[dict(good["nodes"][1], label="DB")] + good["nodes"][2:] + good["nodes"][:1]))

  twin_nodes = good["nodes"] + [{"id": "db2", "label": ["etcd"], "shape": "cylinder"}]
  twin = dict(good, layout="split", titles={"left": "Before", "right": "캐시 추가 후"}, nodes=[dict(n, half=h) for n, h in zip(twin_nodes, ("left", "left", "left", "right"))],
              edges=good["edges"] + [{"from": "ctl", "to": "db2", "kind": "sync"}])
  assert score(check(twin)) == 100, check(twin)
  assert "cylinder in the right half" in build(twin) and 'to shape 4 ("etcd")' in build(twin)
  assert "half" in failed(dict(twin, nodes=good["nodes"] + [twin["nodes"][3]]))
  assert "half" in failed(dict(twin, nodes=[dict(n, half="left") for n in twin["nodes"]]))
  assert {"half", "titles"} <= failed(dict(twin, layout="hub"))
  tb = build(twin)
  assert 'The left half has the title "Before" written in #1E1E1E' in tb and "at its top-left corner" in tb and 'The right half has the title "캐시 추가 후"' in tb and "{" not in tb
  assert "TITLES" not in out and "half has the title" not in out and "not quoted above" in out and failed(dict(good, titles={"left": "A", "right": "B"})) == {"titles"}
  assert failed(dict(good, titles=None)) == {"titles"} and not failed(dict(twin, titles={"left": "A", "right": "x" * 20}))
  untitled = {k: v for k, v in twin.items() if k != "titles"}
  assert failed(untitled) == {"titles"}
  for bad_titles in ({"left": "A"}, {"left": "A", "right": ""}, {"left": "A", "right": "B", "top": "C"}, {"left": "A", "right": "x" * 21}, {"left": "A", "right": 3}, {"left": "A", "right": 'Say "hi"'}, ["A", "B"], None):
    assert failed(dict(untitled, titles=bad_titles)) == {"titles"}, bad_titles
  assert failed(dict(twin, titles={"left": "A", "right": "3d"})) == {"no banned words"}

  tiered = dict(good, layout="layers", nodes=[dict(n, tier=t) for n, t in zip(good["nodes"] + [cache], (1, 2, 3, 3))],
                edges=good["edges"] + [{"from": "ctl", "to": "x", "kind": "call"}])
  assert score(check(tiered)) == 100, check(tiered)
  assert "cylinder in tier 3 from the top" in build(tiered)
  assert "tier" in failed(dict(tiered, layout="hub"))
  assert "tier" in failed(dict(tiered, nodes=[dict(n, tier=1) for n in tiered["nodes"]]))

  numbered = dict(good, edges=[dict(e, step=i) for i, e in enumerate(good["edges"][:2], 1)] + good["edges"][2:])
  assert score(check(numbered)) == 100, check(numbered)
  assert 'holding the number "2"' in build(numbered) and "holding the number" not in out
  assert 'outlined in #1E1E1E holding the number "1" in #1E1E1E' in build(numbered)
  for bad_steps in ((1, 3), (2, 3), (1, 1), (1,)):
    e2 = [dict(e, step=n) for e, n in zip(good["edges"], bad_steps)] + good["edges"][len(bad_steps):]
    assert "steps" in failed(dict(good, edges=e2)), bad_steps

  # 저장된 예시 프롬프트가 지금 라이브러리로 조립한 결과와 같다.
  for path in sorted((REF / "example").glob("*.json")):
    spec = json.loads(path.read_text(encoding="utf-8"))
    assert score(check(spec)) == 100, (path.name, failed(spec))
    assert path.with_suffix(".txt").read_text(encoding="utf-8") == build(spec) + "\n", path.name
  nested = dict(good, groups=[{"id": "outer", "label": ["Host"], "members": ["ctl", "inner"]},
                              {"id": "inner", "label": ["Storage"], "members": ["db"]}],
                edges=good["edges"][:2] + [{"from": "inner", "to": "spec", "kind": "sync"}])
  assert score(check(nested)) == 100, failed(nested)
  nb = build(nested)
  assert "encloses shape 2 and group B" in nb and 'outline of group B ("Storage")' in nb and "{" not in nb
  assert "groups" in failed(dict(nested, groups=nested["groups"] + [{"id": "x2", "label": ["X"], "members": ["db"]}]))
  assert "groups" in failed(dict(nested, groups=[dict(nested["groups"][0], members=["outer"])]))
  assert "edge ends" in failed(dict(nested, edges=good["edges"][:2] + [{"from": "nope", "to": "spec", "kind": "sync"}]))
  assert failed(dict(nested, edges=nested["edges"] + [{"from": "db", "to": "outer", "kind": "sync"}])) == {"edge ends"}
  assert "GROUPS" not in out and nb.count('"Storage"') == 2 and "named \"Storage\"" not in nb

  cols = dict(tiered, layout="columns", nodes=[{**{k: v for k, v in n.items() if k != "tier"}, "col": n["tier"]} for n in tiered["nodes"]])
  assert score(check(cols)) == 100, failed(cols)
  assert "in column 3 from the left" in build(cols) and "col" in failed(dict(cols, layout="hub"))
  assert "col" in failed(dict(cols, nodes=[dict(n, col=5) for n in cols["nodes"]]))

  # stack: 위·아래 판, same은 다른 판 같은 도형, step은 판마다 1부터도 된다.
  sides = ("top", "top", "bottom", "bottom")
  stack = dict(good, layout="stack", titles={"top": "Write", "bottom": "Read"},
               nodes=[dict(n, panel=v) for n, v in zip(twin_nodes, sides)],
               edges=[{"from": "spec", "to": "ctl", "kind": "call", "step": 1, "label": "send"},
                      {"from": "db", "to": "db2", "kind": "sync", "step": 2},
                      {"from": "db2", "to": "db", "kind": "sync", "step": 3}])
  stack["nodes"][3] = dict(stack["nodes"][3], label=["Desired", "State"], shape="box", same="spec")
  stack["nodes"][2]["label"] = ["etcd"]
  stack["nodes"][3]["same"] = "spec"
  stack["nodes"][0]["panel"] = "top"
  assert score(check(stack)) == 100, failed(stack)
  sb = build(stack)
  assert "in the bottom panel" in sb and 'The top panel has the title "Write"' in sb and "thin solid #1E1E1E rounded rectangle" in sb
  assert "focus" not in KEYS["nodes"] and "filled flat" not in sb and failed(dict(stack, nodes=[dict(stack["nodes"][0], focus=True)] + stack["nodes"][1:])) == {"keys"}
  assert "Shape 1 and shape 4 are the same component" in sb and "directly above the other" in sb
  assert "parallel straight lines" in sb and 'holding the number "1" in #1E1E1E, placed just before its label' in sb and "{" not in sb
  assert failed(dict(stack, groups=[{"id": "g", "label": ["Job"], "members": ["ctl", "db"]}])) == {"panel groups"}
  gstack = dict(stack, groups=[{"id": "g", "label": ["Job"], "members": ["ctl"]}],
                edges=[{"from": "spec", "to": "g", "kind": "call", "step": 1}, {"from": "g", "to": "spec", "kind": "sync", "step": 2},
                       {"from": "db", "to": "db2", "kind": "sync", "step": 1}, {"from": "db2", "to": "db", "kind": "sync", "step": 2}])
  assert failed(gstack) == set(), failed(gstack)
  assert "tier" in failed(dict(tiered, nodes=[dict(n, tier=True) for n in tiered["nodes"]]))
  assert failed(dict(stack, nodes=stack["nodes"][:3] + [dict(stack["nodes"][3], label=["Other"])])) == {"same"}
  assert "same" in failed(dict(stack, layout="hub"))
  restart = [dict(e, step=n) for e, n in zip(stack["edges"], (1, 1, 2))] + [{"from": "ctl", "to": "spec", "kind": "sync", "step": 2}]
  assert failed(dict(stack, edges=restart)) == set() and failed(dict(good, edges=[dict(e, step=n) for e, n in zip(good["edges"], (1, 1, 2))])) == {"steps"}
  assert failed(dict(stack, edges=[dict(e, step=n) for e, n in zip(stack["edges"], (1, 2, 2))])) == {"steps"}
  assert failed(dict(stack, titles={"left": "A", "right": "B"})) == {"titles"} and "panel" in failed(dict(stack, layout="split"))

  # sequence: 참여자 생명선, 시간순 가로 화살표, wait 여백, spans 대괄호, 화살표 높이 메모. 묶음·step은 쓰지 않는다.
  seq = {"palette": "pastel", "layout": "sequence", "subject": "A client opens one HTTP request and the server streams events back over the same response.",
         "nodes": [{"id": "c", "label": ["Client"], "shape": "box"}, {"id": "s", "label": ["Server"], "shape": "box"}],
         "edges": [{"from": "c", "to": "s", "kind": "call", "label": "GET /events", "chip": "blue"},
                   {"from": "s", "to": "c", "kind": "call", "label": "200 OK", "chip": "yellow"},
                   {"from": "s", "to": "c", "kind": "call", "label": "event 1", "chip": "pink", "wait": "Wait 2 s"}],
         "spans": [{"first": 2, "last": 3, "label": ["One HTTP", "response"]}],
         "notes": [{"edge": 2, "text": "Headers first"}]}
  assert failed(seq) == set(), failed(seq)
  qb = build(seq)
  assert "lifeline" in qb and 'from the lifeline of shape 1 ("Client") to the lifeline of shape 2 ("Server")' in qb and "just above the line" in qb
  assert 'extra empty vertical space above it, with "Wait 2 s"' in qb and "from arrow 2 down to arrow 3" in qb and "level with arrow 2" in qb
  assert "#BFE1FA" in qb and "#FBE9A6" in qb and "#F7C6CC" in qb and "{" not in qb
  for bad_seq in (dict(seq, edges=[dict(seq["edges"][0], step=1), dict(seq["edges"][1], step=2)] + seq["edges"][2:]),
                  dict(seq, spans=[{"first": 3, "last": 3, "label": ["x"]}]), dict(seq, notes=[{"edge": 9, "text": "x"}]),
                  dict(seq, groups=[{"id": "g", "label": ["G"], "members": ["s"]}]),
                  dict(seq, notes=[{"node": "c", "text": "x"}]), dict(seq, edges=seq["edges"][:2] + [dict(seq["edges"][2], kind="sync-pair")]),
                  dict(seq, spans=[{"first": 1, "last": 2, "label": ["a"]}, {"first": 2, "last": 3, "label": ["b"]}])):
    assert "sequence" in failed(bad_seq), bad_seq
  assert failed(dict(good, edges=[dict(good["edges"][0], wait="x")] + good["edges"][1:])) == {"sequence"}
  assert failed(dict(good, spans=[{"first": 1, "last": 2, "label": ["x"]}])) == {"sequence"}
  assert "sequence" in failed(dict(seq, edges=seq["edges"][:2] + [dict(seq["edges"][2], wait=5)])) and "chips" in failed(dict(seq, edges=[dict(seq["edges"][0], chip=["blue"])] + seq["edges"][1:]))
  assert "chip" not in out.split("COLOR PALETTE")[1] and "Except in a sequence diagram" in qb

  # 작업 폴더의 shapes·palettes는 새 id만 더하고, 덮거나 필드·타입이 틀리면 멈춘다.
  import tempfile
  with tempfile.TemporaryDirectory() as d:
    saved = {k: dict(LIB[k]) for k in LOCAL}
    Path(d, "shapes.jsonl").write_text('{"id": "queue", "ko": "q", "prompt": "a lying cylinder"}\n', encoding="utf-8")
    Path(d, "palettes.jsonl").write_text('{"id": "mint", "use": "u", "ink": "#111111", "bg": "#FFFFFF", "chips": {"mint": "#CFF3E6"}}\n', encoding="utf-8")
    extend(d)
    local = dict(good, palette="mint", nodes=good["nodes"][:2] + [dict(good["nodes"][2], shape="queue")], edges=[good["edges"][0], dict(good["edges"][1], chip="mint")] + good["edges"][2:])
    assert failed(local) == set() and "a lying cylinder" in build(local) and "#CFF3E6" in build(local)
    for bad_line in ('{"id": "box", "ko": "x", "prompt": "y"}', '{"id": "q2", "prompt": "y"}'):
      Path(d, "shapes.jsonl").write_text(bad_line + "\n", encoding="utf-8")
      try:
        extend(d)
        raise AssertionError(bad_line)
      except SystemExit:
        pass
    Path(d, "shapes.jsonl").unlink()
    Path(d, "palettes.jsonl").write_text('{"id": "p2", "use": "u", "ink": "#111111", "bg": "#FFFFFF", "chips": ["red"]}\n', encoding="utf-8")
    try:
      extend(d)
      raise AssertionError("list chips")
    except SystemExit:
      pass
    for k in LOCAL:
      LIB[k] = saved[k]

  assert margins((100, 50, 1100, 650), (1280, 720)) == ((100, 180, 50, 70), 6.25, 2.7777777777777777)
  print("selftest ok")


def main(argv):
  if argv[:1] == ["--selftest"]:
    return selftest()
  if argv[:1] == ["center"] and len(argv) >= 2:
    return center(argv[1], argv[argv.index("-o") + 1] if "-o" in argv else argv[1])
  if len(argv) < 2 or argv[0] not in ("build", "check"):
    sys.exit(__doc__)
  spec = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
  extend(Path(argv[1]).resolve().parent)
  rows = check(spec)
  report(rows)
  if argv[0] == "check":
    sys.exit(0 if score(rows) == 100 else 1)
  if score(rows) < 100:
    sys.exit("FAIL 항목을 고친 뒤 다시 build 하세요")
  out = build(spec)
  if "-o" in argv:
    Path(argv[argv.index("-o") + 1]).write_text(out + "\n", encoding="utf-8")
  else:
    print(out)


if __name__ == "__main__":
  main(argv=sys.argv[1:])
