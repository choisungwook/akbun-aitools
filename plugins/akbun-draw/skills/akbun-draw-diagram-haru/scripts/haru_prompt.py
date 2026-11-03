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

# 모델이 쓴 글에 나오면 안 되는 말. 상표·캐릭터와 스타일을 깨는 표현.
BANNED = r"\b(logos?|trademarks?|mascots?|3d|isometric|photorealistic|realistic|gradients?|neon|shadows?)\b"
DO_NOT = ("DO NOT: no colored fills, no 3D, no drop shadows, no gradients, no real product logos or brand marks, "
          "no characters, mascots or decorative doodles, no title or heading, no legend, no watermark.")


def load(name):
    return {r["id"]: r for r in map(json.loads, (REF / name).read_text(encoding="utf-8").splitlines()) if r}


def text_ok(s, hi):
    """1~hi자(공백 포함), 영어(ASCII)·한글만, 큰따옴표 없음."""
    return 1 <= len(s) <= hi and '"' not in s and all(ch.isascii() or "가" <= ch <= "힣" for ch in s)


def name(node):
    return " ".join(node.get("label", []))


def check(spec):
    """(항목, 통과 여부, 이유) 목록. 항목 하나 = 1점, 점수 = 통과 수 / 항목 수 × 100(내림)."""
    pal, lay, shapes, edges, icons = (load(n) for n in ("palettes.jsonl", "layouts.jsonl", "shapes.jsonl", "edges.jsonl", "icons.jsonl"))
    lo, hi = lay[spec["layout"]]["nodes"] if spec.get("layout") in lay else (0, 0)
    nodes, es, notes = spec.get("nodes", []), spec.get("edges", []), spec.get("notes", [])
    ids = [n.get("id") for n in nodes]
    names = [name(n) for n in nodes]
    labeled = [e for e in es if e.get("label")]
    linked = {e.get("from") for e in es} | {e.get("to") for e in es}
    words = len(spec.get("subject", "").split())
    free = " ".join([spec.get("subject", "")] + names + [e.get("label", "") for e in es] + [x.get("text", "") for x in notes])
    return [
        ("palette", spec.get("palette") in pal, f"palettes.jsonl id: {sorted(pal)}"),
        ("layout", spec.get("layout") in lay, f"layouts.jsonl id: {sorted(lay)}"),
        ("node count", lo <= len(nodes) <= hi, f"도형 {len(nodes)}개, 배치 허용 {lo}~{hi}개(경계 포함)"),
        ("node ids", len(set(ids)) == len(ids) and all(ids), f"id 중복·빈 값 없이: {ids}"),
        ("shapes", all(n.get("shape") in shapes for n in nodes), f"shapes.jsonl id: {sorted(shapes)}"),
        ("labels", all(isinstance(n.get("label"), list) and 1 <= len(n["label"]) <= 2 and all(text_ok(l, 12) for l in n["label"]) for n in nodes),
         "도형 이름 1~2줄, 줄마다 1~12자(공백 포함), 영어·한글"),
        ("halves", [n.get("half") for n in nodes].count(None) == 0 and {n["half"] for n in nodes} == {"left", "right"}
         if spec.get("layout") == "split" else not any("half" in n for n in nodes),
         "split이면 모든 도형에 half(left·right), 두 판 모두 사용, 아니면 half 없음"),
        ("tiers", all(n.get("tier") in (1, 2, 3, 4) for n in nodes) and len({n["tier"] for n in nodes}) >= 2
         if spec.get("layout") == "layers" else not any("tier" in n for n in nodes),
         "layers면 모든 도형에 tier(1~4, 1이 맨 위), 2개 층 이상, 아니면 tier 없음"),
        ("node icons", sum("icon" in n for n in nodes) <= 3 and all(n["icon"] in icons for n in nodes if "icon" in n),
         f"도형 아이콘 0~3개, icons.jsonl id: {sorted(icons)}"),
        ("edge count", 1 <= len(es) <= 12, f"화살표 {len(es)}개, 1~12개"),
        ("edge ends", all(e.get("from") in ids and e.get("to") in ids and e["from"] != e["to"] for e in es),
         "from·to는 서로 다른 도형 id"),
        ("edge kinds", all(e.get("kind") in edges for e in es), f"edges.jsonl id: {sorted(edges)}"),
        ("main count", 1 <= sum(e.get("kind") == "main" for e in es) <= 3, "main 화살표 1~3개(경계 포함)"),
        ("edge labels", len(labeled) <= 5 and all(text_ok(e["label"], 14) for e in labeled),
         f"이름 붙은 화살표 {len(labeled)}개, 0~5개, 각 1~14자"),
        ("edge icons", all(e.get("label") and e["icon"] in icons for e in es if "icon" in e), "화살표 아이콘은 label이 있을 때만, icons.jsonl id"),
        ("all linked", set(ids) <= linked, f"화살표가 닿지 않은 도형: {sorted(set(ids) - linked)}"),
        ("notes", len(notes) <= 2 and all(x.get("node") in ids and text_ok(x.get("text", ""), 32) for x in notes),
         "메모 0~2개, node는 도형 id, 각 1~32자"),
        ("subject", 6 <= words <= 30 and spec.get("subject", "").isascii(), f"subject {words}단어, 6~30단어, 영어"),
        ("no banned words", not re.search(BANNED, free, re.I), "logo·trademark·mascot·3d·isometric·photorealistic·realistic·gradient·neon·shadow 금지"),
    ]


def score(rows):
    return sum(ok for _, ok, _ in rows) * 100 // len(rows)


def build(spec):
    style, pal, lay, shapes, edges, icons = (load(n) for n in ("style.jsonl", "palettes.jsonl", "layouts.jsonl", "shapes.jsonl", "edges.jsonl", "icons.jsonl"))
    p = pal[spec["palette"]]
    by_id = {n["id"]: n for n in spec["nodes"]}
    num = {n["id"]: i for i, n in enumerate(spec["nodes"], 1)}
    q = lambda n: f'shape {num[n["id"]]} ("{name(n)}")'

    def shape(i, n):
        lines = " over ".join(f'"{l}"' for l in n["label"])
        text = lines + (" on two lines" if len(n["label"]) == 2 else "")
        icon = f", with a tiny flat {icons[n['icon']]['prompt']} icon left of the name" if "icon" in n else ""
        half = f" in the {n['half']} half" if "half" in n else f" in tier {n['tier']} from the top" if "tier" in n else ""
        return f"{i}. {shapes[n['shape']]['prompt']}{half} named {text}{icon}."

    def arrow(i, e):
        line = edges[e["kind"]]["prompt"].format(**p)
        out = f"{i}. from {q(by_id[e['from']])} to {q(by_id[e['to']])}: {line}"
        if e.get("label"):
            out += f', labeled "{e["label"]}" in small {p["accent"]} lettering beside the line'
            if "icon" in e:
                out += f", with a tiny grey line-drawn {icons[e['icon']]['prompt']} icon just above the label"
        return out + "."

    parts = [
        style["medium"]["prompt"],
        f"LAYOUT: {lay[spec['layout']]['prompt']}",
        f"SUBJECT: {spec['subject']}",
        f"SHAPES ({len(spec['nodes'])}): " + " ".join(shape(i, n) for i, n in enumerate(spec["nodes"], 1)),
        f"ARROWS ({len(spec['edges'])}): " + " ".join(arrow(i, e) for i, e in enumerate(spec["edges"], 1)),
    ]
    if spec.get("notes"):
        parts.append("NOTES: " + " ".join(
            f'Just below {q(by_id[x["node"]])}, a small note in {p["accent"]} lettering reads "{x["text"]}".' for x in spec["notes"]))
    parts += [
        "TEXT: The only words in the image are the quoted texts above, spelled exactly.",
        f"COLOR PALETTE: background {p['bg']}; ink {p['ink']}; accent {p['accent']}; icon {p['icon']}; grey {p['muted']}. Use no other colors.",
        "STYLE: " + " ".join(style[k]["prompt"].format(**p) for k in style if k != "medium"),
        DO_NOT,
    ]
    return "\n\n".join(parts)


def report(rows):
    for n, ok, why in rows:
        print(f"{'PASS' if ok else 'FAIL'}  {n:16} {why}")
    print(f"score {score(rows)}")


def selftest():
    good = {
        "palette": "ink-blue", "layout": "loop",
        "subject": "A controller keeps comparing desired state with actual state and fixes the difference.",
        "nodes": [{"id": "spec", "label": ["Desired", "State"], "shape": "box", "icon": "document"},
                  {"id": "ctl", "label": ["Controller"], "shape": "box"},
                  {"id": "db", "label": ["etcd"], "shape": "cylinder"}],
        "edges": [{"from": "spec", "to": "ctl", "kind": "main"},
                  {"from": "ctl", "to": "db", "kind": "call", "label": "watch", "icon": "eye"},
                  {"from": "db", "to": "spec", "kind": "sync-pair"}],
        "notes": [{"node": "db", "text": "실제 상태 저장"}],
    }
    assert score(check(good)) == 100, check(good)
    out = build(good)
    assert '"Desired" over "State" on two lines' in out and "#4A90D0" in out and "{" not in out
    assert 'from shape 2 ("Controller") to shape 3 ("etcd")' in out and '"watch"' in out and "grey line-drawn eye icon" in out
    assert '"실제 상태 저장"' in out and "#2E9E6B" in build(dict(good, palette="ink-green"))
    assert "NOTES" not in build(dict(good, notes=[]))
    bad = dict(good, layout="hub", palette="pink",
               nodes=good["nodes"] + [{"id": "ctl", "label": ["A very long label"], "shape": "hexagon"}],
               edges=good["edges"] + [{"from": "ctl", "to": "ctl", "kind": "arrow", "icon": "key"}],
               subject="Our logo in 3d.")
    failed = {n for n, ok, _ in check(bad) if not ok}
    assert {"palette", "node ids", "shapes", "labels", "edge ends", "edge kinds", "edge icons",
            "subject", "no banned words"} <= failed, failed
    lonely = dict(good, layout="row", nodes=good["nodes"] + [{"id": "x", "label": ["Cache"], "shape": "box"}])
    assert {n for n, ok, _ in check(lonely) if not ok} == {"all linked"}
    assert score(check(dict(good, nodes=[dict(good["nodes"][0], label=['Say "hi"'])] + good["nodes"][1:]))) < 100
    twin = dict(good, layout="split", nodes=[dict(n, half=h) for n, h in zip(good["nodes"] + [{"id": "db2", "label": ["etcd"], "shape": "cylinder"}], ("left", "left", "left", "right"))],
                edges=good["edges"] + [{"from": "ctl", "to": "db2", "kind": "sync"}])
    assert score(check(twin)) == 100, check(twin)
    assert "cylinder in the right half" in build(twin) and 'to shape 4 ("etcd")' in build(twin)
    assert "halves" in {n for n, ok, _ in check(dict(twin, nodes=good["nodes"] + [twin["nodes"][3]])) if not ok}
    tiered = dict(good, layout="layers", nodes=[dict(n, tier=t) for n, t in zip(good["nodes"] + [{"id": "x", "label": ["Cache"], "shape": "box"}], (1, 2, 3, 3))],
                  edges=good["edges"] + [{"from": "ctl", "to": "x", "kind": "call"}])
    assert score(check(tiered)) == 100, check(tiered)
    assert "cylinder in tier 3 from the top" in build(tiered)
    assert "tiers" in {n for n, ok, _ in check(dict(tiered, layout="hub"))  if not ok}
    assert "labels" in {n for n, ok, _ in check(dict(good, nodes=[dict(good["nodes"][1], label="DB")] + good["nodes"][2:] + good["nodes"][:1])) if not ok}
    assert "halves" in {n for n, ok, _ in check(dict(twin, nodes=[dict(n, half="left") for n in twin["nodes"]])) if not ok}
    assert "main count" in {n for n, ok, _ in check(dict(good, edges=[dict(e, kind="sync") for e in good["edges"]])) if not ok}
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
    main(sys.argv[1:])
