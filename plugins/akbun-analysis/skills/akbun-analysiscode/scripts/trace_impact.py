#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import defaultdict, deque
from pathlib import Path

from analysis_artifacts import flatten_bundle
from analysis_common import load_analysis_bundle

MESSAGE_KINDS = {"event-publish", "event-subscribe", "queue-produce", "queue-consume"}


def main() -> int:
  if len(sys.argv) != 3:
    print("usage: trace_impact.py ANALYSIS_JSON COMPONENT_ID", file=sys.stderr)
    return 2
  source = Path(sys.argv[1]).expanduser().resolve()
  component_id = sys.argv[2]
  try:
    graph = flatten_bundle(load_analysis_bundle(source))
  except ValueError as error:
    print(json.dumps({"ok": False, "error": str(error)}))
    return 1
  nodes = {item["uid"]: item for item in graph["components"]}
  matches = [uid for uid, item in nodes.items() if uid == component_id or item["id"] == component_id]
  if len(matches) != 1:
    print(json.dumps({"ok": False, "error": "component id is missing or ambiguous", "matches": matches}, ensure_ascii=False, indent=2))
    return 1
  origin = matches[0]
  propagation: dict[str, list[tuple[str, dict]]] = defaultdict(list)
  for relationship in graph["relationships"]:
    if relationship["kind"] in MESSAGE_KINDS:
      source_uid, target_uid = relationship["source_uid"], relationship["target_uid"]
    else:
      source_uid, target_uid = relationship["target_uid"], relationship["source_uid"]
    propagation[source_uid].append((target_uid, relationship))
  queue = deque([(origin, 0)])
  seen = {origin}
  affected: list[dict] = []
  while queue:
    current, depth = queue.popleft()
    for target, relationship in propagation[current]:
      if target in seen:
        continue
      seen.add(target)
      queue.append((target, depth + 1))
      affected.append({
        "component": target,
        "name": nodes.get(target, {}).get("name", target),
        "hops": depth + 1,
        "via_relationship": relationship["uid"],
        "kind": relationship["kind"],
        "evidence": relationship["evidence"],
      })
  touched = seen | {origin}
  business_flows = [
    {"business": business["name"], "flow": flow["name"], "flow_id": flow["uid"]}
    for business in graph["businesses"]
    for flow in business["flows"]
    if any(uid in touched for uid in graph["views"][flow["view_id"]]["nodes"])
  ]
  print(json.dumps({
    "ok": True,
    "origin": origin,
    "possible_affected": affected,
    "possible_affected_flows": business_flows,
    "warning": "그래프 도달 가능성은 장애 범위나 실제 리스크를 증명하지 않는다. 결론 전에 변경 코드와 관계 근거를 확인한다.",
  }, ensure_ascii=False, indent=2))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
