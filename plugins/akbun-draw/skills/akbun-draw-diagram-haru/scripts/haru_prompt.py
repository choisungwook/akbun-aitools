"""haru 스타일 다이어그램 이미지 생성 프롬프트를 spec(JSON)에서 조립하고 채점한다.

  build <spec.json> [-o prompt.txt]   채점 후 100점이면 프롬프트를 쓴다(없으면 stdout)
  check <spec.json>                   채점표만 출력
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
  "spec": {"palette", "layout", "subject", "nodes", "edges", "notes", "groups"},
  "groups": {"id", "label", "members"},
  "nodes": {"id", "label", "shape", "half", "tier", "col"},
  "edges": {"from", "to", "kind", "label", "step"},
  "notes": {"node", "text"},
}


def load(name):
  lines = (REF / f"{name}.jsonl").read_text(encoding="utf-8").splitlines()
  return {r["id"]: r for r in map(json.loads, filter(None, lines))}


LIB = {name: load(name) for name in ("style", "palettes", "layouts", "shapes", "edges", "groups")}


def text_ok(s, hi):
  """1~hi자(공백 포함), 영어(ASCII)·한글만, 큰따옴표 없음."""
  return 1 <= len(s) <= hi and '"' not in s and all(ch.isascii() or "가" <= ch <= "힣" for ch in s)


def name(node):
  return " ".join(node.get("label", []))


def unknown_keys(spec):
  found = set(spec) - KEYS["spec"]
  for part in ("nodes", "edges", "notes", "groups"):
    for item in spec.get(part, []):
      found |= {f"{part}.{k}" for k in set(item) - KEYS[part]}
  return sorted(found)


def group_ok(nodes, key, allowed, min_groups, used):
  """배치가 key를 쓰면 모든 도형이 allowed 값을 갖고 min_groups개 이상으로 나뉜다. 안 쓰면 key가 없다."""
  if not used:
    return not any(key in n for n in nodes)
  return all(n.get(key) in allowed for n in nodes) and len({n[key] for n in nodes}) >= min_groups


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
  layout = spec.get("layout")
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
  free = " ".join([subject] + [name(n) for n in nodes] + [name(g) for g in spec.get("groups", [])] + [e.get("label", "") for e in es] + [x.get("text", "") for x in notes])
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
    ("halves", group_ok(nodes, "half", ("left", "right"), 2, layout == "split"),
     "split이면 모든 도형에 half(left·right), 두 판 모두 사용, 아니면 half 없음"),
    ("tiers", group_ok(nodes, "tier", (1, 2, 3, 4), 2, layout == "layers"),
     "layers면 모든 도형에 tier(1~4, 1이 맨 위), 2개 층 이상, 아니면 tier 없음"),
    ("cols", group_ok(nodes, "col", (1, 2, 3, 4), 2, layout == "columns"),
     "columns면 모든 도형에 col(1~4, 1이 맨 왼쪽), 2개 열 이상, 아니면 col 없음"),
    ("edge count", 1 <= len(es) <= 12, f"화살표 {len(es)}개, 1~12개"),
    ("edge ends", all(e.get("from") in ends and e.get("to") in ends and e["from"] != e["to"] for e in es),
     "from·to는 서로 다른 도형·묶음 id"),
    ("groups", groups_ok(spec), "묶음 0~4개, 이름 1줄 1~20자, 멤버는 도형·묶음 id로 한 곳에만, 3단계 중첩까지"),
    ("edge kinds", all(e.get("kind") in kinds for e in es), f"edges.jsonl id: {sorted(kinds)}"),
    ("edge labels", len(labeled) <= 5 and all(text_ok(e["label"], 14) for e in labeled),
     f"이름 붙은 화살표 {len(labeled)}개, 0~5개, 각 1~14자"),
    ("steps", all(type(n) is int for n in steps) and sorted(steps) == list(range(1, len(steps) + 1)) and len(steps) != 1,
     f"step {steps}: 없거나, 2개 이상이면 1부터 빠짐없이 이어지는 정수"),
    ("all linked", all(i in linked or set(ancestors(spec, i)) & linked for i in ids),
     f"화살표가 닿지 않은 도형(속한 묶음에도 닿지 않음): {sorted(i for i in ids if i not in linked and not set(ancestors(spec, i)) & linked)}"),
    ("notes", len(notes) <= 2 and all(x.get("node") in ids and text_ok(x.get("text", ""), 32) for x in notes),
     "메모 0~2개, node는 도형 id, 각 1~32자"),
    ("subject", 6 <= words <= 30 and subject.isascii(), f"subject {words}단어, 6~30단어, 영어"),
    ("no banned words", not BANNED_RE.search(free), f"{'·'.join(BANNED)} 금지"),
  ]


def score(rows):
  return sum(ok for _, ok, _ in rows) * 100 // len(rows)


def build(spec):
  style = LIB["style"]
  p = LIB["palettes"][spec["palette"]]
  nodes = spec["nodes"]
  num = {n["id"]: i for i, n in enumerate(nodes, 1)}
  by_id = {n["id"]: n for n in nodes}

  groups = spec.get("groups", [])
  gnum = {g["id"]: chr(65 + i) for i, g in enumerate(groups)}
  gby = {g["id"]: g for g in groups}

  def ref(node_id):
    if node_id in gnum:
      return f'the outline of group {gnum[node_id]} ("{name(gby[node_id])}")'
    return f'shape {num[node_id]} ("{name(by_id[node_id])}")'

  def shape(n):
    text = " over ".join(f'"{l}"' for l in n["label"]) + (" on two lines" if len(n["label"]) == 2 else "")
    where = (f" in the {n['half']} half" if "half" in n else f" in tier {n['tier']} from the top" if "tier" in n
             else f" in column {n['col']} from the left" if "col" in n else "")
    return f"{num[n['id']]}. {LIB['shapes'][n['shape']]['prompt']}{where} named {text}."

  def arrow(i, e):
    out = f"{i}. from {ref(e['from'])} to {ref(e['to'])}: {LIB['edges'][e['kind']]['prompt'].format(**p)}"
    if "step" in e:
      out += f', with a small hollow {p["accent"]} circle holding the number "{e["step"]}" in {p["accent"]} near the middle of the line'
    if e.get("label"):
      out += f', labeled "{e["label"]}" in small {p["accent"]} lettering beside the line'
    return out + "."

  def group(g):
    inner = [f"group {gnum[m]}" if m in gnum else f"shape {num[m]}" for m in g["members"]]
    return (f'{gnum[g["id"]]}. {LIB["groups"]["boundary"]["prompt"].format(label=g["label"][0], **p)}. '
            f'It encloses {" and ".join([", ".join(inner[:-1]), inner[-1]] if len(inner) > 1 else inner)} fully inside it with clear padding.')

  notes = [f'Just below {ref(x["node"])}, a small note in {p["accent"]} lettering reads "{x["text"]}".' for x in spec.get("notes", [])]
  parts = [
    style["medium"]["prompt"],
    f"LAYOUT: {LIB['layouts'][spec['layout']]['prompt']}",
    f"SUBJECT: {spec['subject']}",
    f"SHAPES ({len(nodes)}): " + " ".join(map(shape, nodes)),
    (f"GROUPS ({len(groups)}): " + " ".join(map(group, groups)) +
     " Group outlines only enclose their members: a group inside another group sits wholly within it, and no group outline crosses a shape or another group." if groups else ""),
    f"ARROWS ({len(spec['edges'])}): " + " ".join(arrow(i, e) for i, e in enumerate(spec["edges"], 1)),
    "NOTES: " + " ".join(notes) if notes else "",
    "TEXT: The only words in the image are the quoted texts above, spelled exactly.",
    f"COLOR PALETTE: background {p['bg']}; ink {p['ink']}; accent {p['accent']}. Use no other colors.",
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
    "palette": "ink-blue", "layout": "loop",
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
  assert '"Desired" over "State" on two lines' in out and "#4A90D0" in out and "{" not in out
  assert 'from shape 2 ("Controller") to shape 3 ("etcd")' in out and '"watch"' in out
  assert '"실제 상태 저장"' in out and "#2E9E6B" in build(dict(good, palette="ink-green"))
  assert "NOTES" not in build(dict(good, notes=[])) and "\n\n\n" not in build(dict(good, notes=[]))

  # 화살표는 모두 강조색이고 검정 주 흐름 화살표·아이콘이 없다. 그림은 화면 가운데에 놓인다.
  arrows = out.split("ARROWS")[1].split("NOTES")[0]
  assert "#1E1E1E" not in arrows and " dot " not in out and "no arrow is black" in out
  assert "main" not in LIB["edges"] and failed(dict(good, edges=[dict(good["edges"][0], kind="main")] + good["edges"][1:])) == {"edge kinds"}
  assert " icon " not in out and "no icons or pictograms" in out
  assert "centered on the canvas both horizontally and vertically" in out
  assert out.rstrip().endswith(LIB["style"]["avoid"]["prompt"]) and out.count("DO NOT") == 1
  assert all(set(p) == {"id", "use", "ink", "accent", "bg"} for p in LIB["palettes"].values())
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
  twin = dict(good, layout="split", nodes=[dict(n, half=h) for n, h in zip(twin_nodes, ("left", "left", "left", "right"))],
              edges=good["edges"] + [{"from": "ctl", "to": "db2", "kind": "sync"}])
  assert score(check(twin)) == 100, check(twin)
  assert "cylinder in the right half" in build(twin) and 'to shape 4 ("etcd")' in build(twin)
  assert "halves" in failed(dict(twin, nodes=good["nodes"] + [twin["nodes"][3]]))
  assert "halves" in failed(dict(twin, nodes=[dict(n, half="left") for n in twin["nodes"]]))
  assert "halves" in failed(dict(twin, layout="hub"))

  tiered = dict(good, layout="layers", nodes=[dict(n, tier=t) for n, t in zip(good["nodes"] + [cache], (1, 2, 3, 3))],
                edges=good["edges"] + [{"from": "ctl", "to": "x", "kind": "call"}])
  assert score(check(tiered)) == 100, check(tiered)
  assert "cylinder in tier 3 from the top" in build(tiered)
  assert "tiers" in failed(dict(tiered, layout="hub"))
  assert "tiers" in failed(dict(tiered, nodes=[dict(n, tier=1) for n in tiered["nodes"]]))

  numbered = dict(good, edges=[dict(e, step=i) for i, e in enumerate(good["edges"][:2], 1)] + good["edges"][2:])
  assert score(check(numbered)) == 100, check(numbered)
  assert 'circle holding the number "2"' in build(numbered) and "circle holding" not in out
  assert "#1E1E1E" not in build(numbered).split("ARROWS")[1].split("NOTES")[0]
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
  assert "GROUPS" not in out and nb.count('"Storage"') == 2 and "named \"Storage\"" not in nb

  cols = dict(tiered, layout="columns", nodes=[{**{k: v for k, v in n.items() if k != "tier"}, "col": n["tier"]} for n in tiered["nodes"]])
  assert score(check(cols)) == 100, failed(cols)
  assert "in column 3 from the left" in build(cols) and "cols" in failed(dict(cols, layout="hub"))
  assert "cols" in failed(dict(cols, nodes=[dict(n, col=5) for n in cols["nodes"]]))

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
