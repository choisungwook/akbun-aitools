"""haru 스타일 다이어그램 이미지 생성 프롬프트를 spec(JSON)에서 조립하고 채점한다.

  build <spec.json> [-o prompt.txt]   채점 후 100점이면 프롬프트를 쓴다(없으면 stdout)
  check <spec.json>                   채점표만 출력
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
  "spec": {"palette", "layout", "subject", "nodes", "edges", "notes"},
  "nodes": {"id", "label", "shape", "half", "tier"},
  "edges": {"from", "to", "kind", "label", "step"},
  "notes": {"node", "text"},
}


def load(name):
  lines = (REF / f"{name}.jsonl").read_text(encoding="utf-8").splitlines()
  return {r["id"]: r for r in map(json.loads, filter(None, lines))}


LIB = {name: load(name) for name in ("style", "palettes", "layouts", "shapes", "edges")}


def text_ok(s, hi):
  """1~hi자(공백 포함), 영어(ASCII)·한글만, 큰따옴표 없음."""
  return 1 <= len(s) <= hi and '"' not in s and all(ch.isascii() or "가" <= ch <= "힣" for ch in s)


def name(node):
  return " ".join(node.get("label", []))


def unknown_keys(spec):
  found = set(spec) - KEYS["spec"]
  for part in ("nodes", "edges", "notes"):
    for item in spec.get(part, []):
      found |= {f"{part}.{k}" for k in set(item) - KEYS[part]}
  return sorted(found)


def group_ok(nodes, key, allowed, min_groups, used):
  """배치가 key를 쓰면 모든 도형이 allowed 값을 갖고 min_groups개 이상으로 나뉜다. 안 쓰면 key가 없다."""
  if not used:
    return not any(key in n for n in nodes)
  return all(n.get(key) in allowed for n in nodes) and len({n[key] for n in nodes}) >= min_groups


def check(spec):
  """(항목, 통과 여부, 이유) 목록. 항목 하나 = 1점, 점수 = 통과 수 / 항목 수 × 100(내림)."""
  pal, lay, shapes, kinds = (LIB[n] for n in ("palettes", "layouts", "shapes", "edges"))
  layout = spec.get("layout")
  lo, hi = lay[layout]["nodes"] if layout in lay else (0, 0)
  nodes, es, notes = spec.get("nodes", []), spec.get("edges", []), spec.get("notes", [])
  subject = spec.get("subject", "")
  ids = [n.get("id") for n in nodes]
  labeled = [e for e in es if e.get("label")]
  steps = [e["step"] for e in es if "step" in e]
  linked = {e.get("from") for e in es} | {e.get("to") for e in es}
  words = len(subject.split())
  free = " ".join([subject] + [name(n) for n in nodes] + [e.get("label", "") for e in es] + [x.get("text", "") for x in notes])
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
    ("edge count", 1 <= len(es) <= 12, f"화살표 {len(es)}개, 1~12개"),
    ("edge ends", all(e.get("from") in ids and e.get("to") in ids and e["from"] != e["to"] for e in es),
     "from·to는 서로 다른 도형 id"),
    ("edge kinds", all(e.get("kind") in kinds for e in es), f"edges.jsonl id: {sorted(kinds)}"),
    ("edge labels", len(labeled) <= 5 and all(text_ok(e["label"], 14) for e in labeled),
     f"이름 붙은 화살표 {len(labeled)}개, 0~5개, 각 1~14자"),
    ("steps", all(type(n) is int for n in steps) and sorted(steps) == list(range(1, len(steps) + 1)) and len(steps) != 1,
     f"step {steps}: 없거나, 2개 이상이면 1부터 빠짐없이 이어지는 정수"),
    ("all linked", set(ids) <= linked, f"화살표가 닿지 않은 도형: {sorted(set(ids) - linked)}"),
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

  def ref(node_id):
    return f'shape {num[node_id]} ("{name(by_id[node_id])}")'

  def shape(n):
    text = " over ".join(f'"{l}"' for l in n["label"]) + (" on two lines" if len(n["label"]) == 2 else "")
    where = f" in the {n['half']} half" if "half" in n else f" in tier {n['tier']} from the top" if "tier" in n else ""
    return f"{num[n['id']]}. {LIB['shapes'][n['shape']]['prompt']}{where} named {text}."

  def arrow(i, e):
    out = f"{i}. from {ref(e['from'])} to {ref(e['to'])}: {LIB['edges'][e['kind']]['prompt'].format(**p)}"
    if "step" in e:
      out += f', with a small hollow {p["ink"]} circle holding the number "{e["step"]}" in {p["ink"]} near the middle of the line'
    if e.get("label"):
      out += f', labeled "{e["label"]}" in small {p["accent"]} lettering beside the line'
    return out + "."

  notes = [f'Just below {ref(x["node"])}, a small note in {p["accent"]} lettering reads "{x["text"]}".' for x in spec.get("notes", [])]
  parts = [
    style["medium"]["prompt"],
    f"LAYOUT: {LIB['layouts'][spec['layout']]['prompt']}",
    f"SUBJECT: {spec['subject']}",
    f"SHAPES ({len(nodes)}): " + " ".join(map(shape, nodes)),
    f"ARROWS ({len(spec['edges'])}): " + " ".join(arrow(i, e) for i, e in enumerate(spec["edges"], 1)),
    "NOTES: " + " ".join(notes) if notes else "",
    "TEXT: The only words in the image are the quoted texts above, spelled exactly.",
    f"COLOR PALETTE: background {p['bg']}; ink {p['ink']}; accent {p['accent']}. Use no other colors.",
    "STYLE: " + " ".join(style[k]["prompt"].format(**p) for k in style if k not in ("medium", "avoid")),
    style["avoid"]["prompt"],
  ]
  return "\n\n".join(filter(None, parts))


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
  for bad_steps in ((1, 3), (2, 3), (1, 1), (1,)):
    e2 = [dict(e, step=n) for e, n in zip(good["edges"], bad_steps)] + good["edges"][len(bad_steps):]
    assert "steps" in failed(dict(good, edges=e2)), bad_steps

  # 저장된 예시 프롬프트가 지금 라이브러리로 조립한 결과와 같다.
  for path in sorted((REF / "example").glob("*.json")):
    spec = json.loads(path.read_text(encoding="utf-8"))
    assert score(check(spec)) == 100, (path.name, failed(spec))
    assert path.with_suffix(".txt").read_text(encoding="utf-8") == build(spec) + "\n", path.name
  print("selftest ok")


def main(argv):
  if argv[:1] == ["--selftest"]:
    return selftest()
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
