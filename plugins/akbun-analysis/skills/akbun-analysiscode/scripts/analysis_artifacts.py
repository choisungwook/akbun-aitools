#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from collections import defaultdict, deque
from typing import Any
from xml.etree import ElementTree as ET

from analysis_common import LAYER_INDEX, LAYERS, api_address

KIND_COLORS = {
  "service": "#0f766e",
  "module": "#1d4ed8",
  "component": "#2563eb",
  "datastore": "#7c3aed",
  "message-broker": "#c2410c",
  "external-system": "#475569",
}
RELATION_COLORS = {
  "code-call": "#0f766e",
  "http": "#0ea5e9",
  "grpc": "#2563eb",
  "db-read": "#7c3aed",
  "db-write": "#9333ea",
  "external-api": "#64748b",
  "event-publish": "#ea580c",
  "event-subscribe": "#f97316",
  "queue-produce": "#ca8a04",
  "queue-consume": "#eab308",
}
LAYER_LABELS = {
  "entrypoint": "진입점",
  "application": "응용",
  "domain": "도메인",
  "infrastructure": "인프라",
  "external": "외부",
}
# origin.engine 별 아이콘 색과 화면 표기. 아이콘 모양은 family 로 갈린다.
ENGINE_STYLES = {
  "postgres": {"color": "#336791", "short": "Postgres", "family": "db"},
  "mysql": {"color": "#00758f", "short": "MySQL", "family": "db"},
  "rds": {"color": "#527fff", "short": "RDS", "family": "db"},
  "aurora": {"color": "#2e73b8", "short": "Aurora", "family": "db"},
  "redis": {"color": "#dc382d", "short": "Redis", "family": "cache"},
  "dynamodb": {"color": "#4053d6", "short": "DynamoDB", "family": "db"},
  "mongodb": {"color": "#13aa52", "short": "MongoDB", "family": "db"},
  "elasticsearch": {"color": "#f0a03a", "short": "Elasticsearch", "family": "search"},
  "s3": {"color": "#3f8624", "short": "S3", "family": "bucket"},
  "kafka": {"color": "#c2410c", "short": "Kafka", "family": "queue"},
  "rabbitmq": {"color": "#f4682a", "short": "RabbitMQ", "family": "queue"},
  "sqs": {"color": "#d9538a", "short": "SQS", "family": "queue"},
  "sns": {"color": "#d9538a", "short": "SNS", "family": "queue"},
  "other": {"color": "#64748b", "short": "Store", "family": "db"},
}
CRYPTO_LABELS = {
  "none": "",
  "tls": "TLS",
  "mtls": "mTLS",
  "field": "필드 암호화",
  "kms": "KMS",
}
# 컴포넌트 종류별 요청 1건당 기본 비용. capacity 가 없거나 사용자가 조절하기 전의 출발값이다.
DEFAULT_COST = {
  "service": {"cpu_ms": 8, "mem_kib": 256},
  "module": {"cpu_ms": 4, "mem_kib": 128},
  "component": {"cpu_ms": 6, "mem_kib": 192},
  "datastore": {"cpu_ms": 3, "mem_kib": 512},
  "message-broker": {"cpu_ms": 1, "mem_kib": 128},
  "external-system": {"cpu_ms": 1, "mem_kib": 64},
}
DEFAULT_CAPACITY = {"replicas": 1, "cpu_millicores": 1000, "memory_mib": 1024, "source": "assumed"}
# 암복호화 종류별 요청 1건당 추가 CPU 시간(ms). 화면에서 조절한다.
DEFAULT_CRYPTO_MS = {"none": 0, "tls": 0.4, "mtls": 1.2, "field": 3.0, "kms": 12.0}
NODE_WIDTH = 180
NODE_HEIGHT = 58
COLUMN_STEP = 264
ROW_STEP = 88
MARGIN = 56


def component_uid(project_id: str, component_id: str) -> str:
  return f"{project_id}::{component_id}"


def strongly_connected_components(nodes: list[str], edges: list[tuple[str, str]]) -> list[list[str]]:
  adjacency: dict[str, list[str]] = defaultdict(list)
  node_set = set(nodes)
  for source, target in edges:
    if source in node_set and target in node_set:
      adjacency[source].append(target)
  index = 0
  indexes: dict[str, int] = {}
  lowlinks: dict[str, int] = {}
  stack: list[str] = []
  on_stack: set[str] = set()
  groups: list[list[str]] = []

  def visit(start: str) -> None:
    nonlocal index
    # 깊은 그래프에서 재귀 한계를 넘지 않도록 명시적 스택으로 순회한다.
    work: list[tuple[str, int]] = [(start, 0)]
    while work:
      node, child = work[-1]
      if child == 0:
        indexes[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
      targets = adjacency[node]
      if child < len(targets):
        work[-1] = (node, child + 1)
        target = targets[child]
        if target not in indexes:
          work.append((target, 0))
        elif target in on_stack:
          lowlinks[node] = min(lowlinks[node], indexes[target])
        continue
      work.pop()
      if work:
        parent = work[-1][0]
        lowlinks[parent] = min(lowlinks[parent], lowlinks[node])
      if lowlinks[node] == indexes[node]:
        group: list[str] = []
        while stack:
          item = stack.pop()
          on_stack.remove(item)
          group.append(item)
          if item == node:
            break
        groups.append(group)

  for node in nodes:
    if node not in indexes:
      visit(node)
  return groups


def rank_nodes(nodes: list[str], edges: list[tuple[str, str]]) -> dict[str, int]:
  """순환을 묶어 접은 뒤 각 노드의 열 번호를 정한다."""
  groups = strongly_connected_components(nodes, edges)
  group_by_node = {node: index for index, group in enumerate(groups) for node in group}
  outgoing: dict[int, set[int]] = defaultdict(set)
  indegree = {index: 0 for index in range(len(groups))}
  for source, target in edges:
    if source not in group_by_node or target not in group_by_node:
      continue
    source_group = group_by_node[source]
    target_group = group_by_node[target]
    if source_group == target_group or target_group in outgoing[source_group]:
      continue
    outgoing[source_group].add(target_group)
    indegree[target_group] += 1
  queue = deque(index for index, degree in indegree.items() if degree == 0)
  group_rank = {index: 0 for index in range(len(groups))}
  while queue:
    source = queue.popleft()
    for target in outgoing[source]:
      group_rank[target] = max(group_rank[target], group_rank[source] + 1)
      indegree[target] -= 1
      if indegree[target] == 0:
        queue.append(target)
  return {node: group_rank[group_by_node[node]] for node in nodes if node in group_by_node}


def grid_positions(
  ranks: dict[str, int],
  component_by_uid: dict[str, dict[str, Any]],
) -> dict[str, dict[str, int]]:
  columns: dict[int, list[str]] = defaultdict(list)
  for uid, rank in ranks.items():
    columns[rank].append(uid)
  positions: dict[str, dict[str, int]] = {}
  for rank, uids in columns.items():
    ordered = sorted(
      uids,
      key=lambda uid: (
        LAYER_INDEX.get(component_by_uid.get(uid, {}).get("layer", "external"), 9),
        component_by_uid.get(uid, {}).get("importance") != "core",
        component_by_uid.get(uid, {}).get("name", ""),
      ),
    )
    for row, uid in enumerate(ordered):
      positions[uid] = {"x": MARGIN + rank * COLUMN_STEP, "y": MARGIN + row * ROW_STEP}
  return positions


def canvas_size(positions: dict[str, dict[str, int]]) -> dict[str, int]:
  if not positions:
    return {"width": 900, "height": 480}
  return {
    "width": max(900, max(item["x"] for item in positions.values()) + NODE_WIDTH + MARGIN),
    "height": max(420, max(item["y"] for item in positions.values()) + NODE_HEIGHT + MARGIN),
  }


def endpoint_of(relationship: dict[str, Any], api_by_uid: dict[str, dict[str, Any]]) -> str:
  """이 호출이 어떤 주소로 나가는지. 다른 repo 를 부를 때 특히 중요하다."""
  api = api_by_uid.get(relationship.get("api_uid", ""))
  if api:
    return api["address"]
  details = relationship.get("details", {})
  if details.get("grpc_service") and details.get("grpc_method"):
    return f"{details['grpc_service']}/{details['grpc_method']}"
  if details.get("path"):
    return f"{details.get('method', '')} {details['path']}".strip()
  if details.get("endpoint"):
    provider = details.get("provider")
    return f"{provider} {details['endpoint']}".strip() if provider else details["endpoint"]
  if details.get("topic"):
    return f"topic:{details['topic']}"
  if details.get("queue"):
    return f"queue:{details['queue']}"
  return ""


def edge_load(relationship: dict[str, Any]) -> dict[str, Any]:
  load = relationship.get("load") or {}
  asynchronous = relationship["kind"] in {
    "event-publish", "event-subscribe", "queue-produce", "queue-consume",
  }
  return {
    "fan_out": load.get("fan_out", 1),
    "fan_out_note": load.get("fan_out_note"),
    "sync": load.get("sync", not asynchronous),
    "crypto": load.get("crypto", "none"),
  }


def merge_load(parts: list[dict[str, Any]]) -> dict[str, Any]:
  """접힌 경로의 부하 특성은 곱해서 합친다. 중간이 하나라도 비동기면 전체가 비동기다."""
  merged = {"fan_out": 1.0, "sync": True, "crypto": "none", "fan_out_note": None}
  for part in parts:
    load = edge_load(part)
    merged["fan_out"] *= load["fan_out"]
    merged["sync"] = merged["sync"] and load["sync"]
    if load["crypto"] != "none":
      merged["crypto"] = load["crypto"]
    if load["fan_out_note"] and not merged["fan_out_note"]:
      merged["fan_out_note"] = load["fan_out_note"]
  return merged


def collapse_modules(
  components: list[dict[str, Any]],
  relationships: list[dict[str, Any]],
) -> list[dict[str, Any]]:
  """서비스 관계도용. module 노드를 지나가는 경로를 서비스 사이의 한 관계로 접는다."""
  module_uids = {item["uid"] for item in components if item["kind"] == "module"}
  outgoing: dict[str, list[dict[str, Any]]] = defaultdict(list)
  for relationship in relationships:
    outgoing[relationship["source_uid"]].append(relationship)

  collapsed: dict[tuple[str, str, str], dict[str, Any]] = {}

  def walk(origin_uid: str, current: dict[str, Any], chain: list[str], seen: set[str]) -> None:
    target = current["target_uid"]
    if target not in module_uids:
      key = (origin_uid, target, current["kind"])
      existing = collapsed.get(key)
      path = [*chain, current["uid"]]
      if existing is None:
        collapsed[key] = {
          "uid": f"collapsed::{origin_uid}::{target}::{current['kind']}",
          "source_uid": origin_uid,
          "target_uid": target,
          "kind": current["kind"],
          "label": current["label"],
          "derived": len(path) > 1,
          "relationship_uids": path,
        }
      else:
        for uid in path:
          if uid not in existing["relationship_uids"]:
            existing["relationship_uids"].append(uid)
      return
    if target in seen:
      return
    for following in outgoing[target]:
      walk(origin_uid, following, [*chain, current["uid"]], seen | {target})

  for relationship in relationships:
    if relationship["source_uid"] in module_uids:
      continue
    walk(relationship["source_uid"], relationship, [], {relationship["source_uid"]})
  return list(collapsed.values())


def build_service_view(
  components: list[dict[str, Any]],
  relationships: list[dict[str, Any]],
) -> dict[str, Any]:
  visible = [item for item in components if item["kind"] != "module"]
  node_uids = {item["uid"] for item in visible}
  edges = [
    edge
    for edge in collapse_modules(components, relationships)
    if edge["source_uid"] in node_uids and edge["target_uid"] in node_uids
  ]
  component_by_uid = {item["uid"]: item for item in visible}
  ranks = rank_nodes(sorted(node_uids), [(edge["source_uid"], edge["target_uid"]) for edge in edges])
  positions = grid_positions(ranks, component_by_uid)
  return {
    "id": "service",
    "mode": "service",
    "title": "서비스 관계도",
    "description": "module 을 접어 서비스·저장소·외부 시스템 사이의 관계만 남긴 화면이다.",
    "nodes": sorted(node_uids),
    "edges": edges,
    "ranks": ranks,
    "positions": positions,
    "canvas": canvas_size(positions),
  }


def build_flow_view(
  view_id: str,
  title: str,
  description: str,
  entry_uids: list[str],
  step_uids: list[str],
  component_by_uid: dict[str, dict[str, Any]],
  relationship_by_uid: dict[str, dict[str, Any]],
) -> dict[str, Any]:
  """업무 흐름 한 개(또는 도메인 전체)를 진입점부터 좌→우 체인으로 편다."""
  edges: list[dict[str, Any]] = []
  depth: dict[str, int] = {uid: 0 for uid in entry_uids}
  for step_number, step_uid in enumerate(step_uids, start=1):
    relationship = relationship_by_uid.get(step_uid)
    if relationship is None:
      continue
    source = relationship["source_uid"]
    target = relationship["target_uid"]
    depth.setdefault(source, 0)
    depth[target] = max(depth.get(target, 0), depth[source] + 1)
    edges.append({
      "uid": relationship["uid"],
      "source_uid": source,
      "target_uid": target,
      "kind": relationship["kind"],
      "label": relationship["label"],
      "step": step_number,
      "derived": False,
      "relationship_uids": [relationship["uid"]],
    })
  node_uids = sorted(depth)
  positions = grid_positions(depth, component_by_uid)
  return {
    "id": view_id,
    "mode": "business",
    "title": title,
    "description": description,
    "nodes": node_uids,
    "edges": edges,
    "ranks": depth,
    "positions": positions,
    "canvas": canvas_size(positions),
    "depth": (max(depth.values()) + 1) if depth else 0,
  }


def enrich_edges(
  view: dict[str, Any],
  relationship_by_uid: dict[str, dict[str, Any]],
  api_by_uid: dict[str, dict[str, Any]],
) -> None:
  """화면이 쓸 주소와 부하 특성을 엣지에 붙인다."""
  for edge in view["edges"]:
    parts = [relationship_by_uid[uid] for uid in edge["relationship_uids"] if uid in relationship_by_uid]
    endpoints = [text for text in (endpoint_of(part, api_by_uid) for part in parts) if text]
    edge["endpoint"] = endpoints[-1] if endpoints else ""
    edge["cross_project"] = any(part.get("target_project_id") for part in parts)
    edge["load"] = merge_load(parts)


def build_api_view(
  apis: list[dict[str, Any]],
  relationships: list[dict[str, Any]],
  component_by_uid: dict[str, dict[str, Any]],
) -> dict[str, Any]:
  """API 로만 본 관계도. 어떤 컴포넌트가 어떤 주소를 부르고 누가 그 주소를 제공하는지만 남긴다."""
  edges: list[dict[str, Any]] = []
  node_uids: set[str] = set()
  for api in apis:
    if api["provider_uid"] in component_by_uid:
      node_uids.add(api["provider_uid"])
  for relationship in relationships:
    api = None
    if relationship.get("api_uid"):
      api = next((item for item in apis if item["uid"] == relationship["api_uid"]), None)
    elif relationship["kind"] not in {"http", "grpc", "external-api"}:
      continue
    source = relationship["source_uid"]
    target = relationship["target_uid"]
    if source not in component_by_uid or target not in component_by_uid:
      continue
    node_uids.add(source)
    node_uids.add(target)
    edges.append({
      "uid": relationship["uid"],
      "source_uid": source,
      "target_uid": target,
      "kind": relationship["kind"],
      "label": relationship["label"],
      "api_uid": api["uid"] if api else None,
      "step": None,
      "derived": False,
      "relationship_uids": [relationship["uid"]],
    })
  ranks = rank_nodes(sorted(node_uids), [(edge["source_uid"], edge["target_uid"]) for edge in edges])
  positions = grid_positions(ranks, component_by_uid)
  return {
    "id": "api",
    "mode": "api",
    "title": "API 관계도",
    "description": "호출 주소가 확인된 관계만 남긴 화면이다. 왼쪽 목록이 이 프로젝트가 제공하고 부르는 API 전체다.",
    "nodes": sorted(node_uids),
    "edges": edges,
    "ranks": ranks,
    "positions": positions,
    "canvas": canvas_size(positions),
  }


def build_load_view(service_view: dict[str, Any]) -> dict[str, Any]:
  """부하분석은 배포 단위로 본다. 서비스 관계도와 같은 위상에 원형 배치만 다르게 준다."""
  # 원형 노드는 라벨이 아래로 붙어 사각형보다 더 넓은 간격이 필요하다.
  positions = {
    uid: {
      "x": int((point["x"] + NODE_WIDTH / 2) * 1.15),
      "y": int((point["y"] + NODE_HEIGHT / 2) * 1.7),
    }
    for uid, point in service_view["positions"].items()
  }
  return {
    "id": "load",
    "mode": "load",
    "title": "부하 전파",
    "description": "진입점 요청량을 올리면 fan-out 배수를 따라 하류로 증폭된 부하를 계산한다.",
    "nodes": list(service_view["nodes"]),
    "edges": json.loads(json.dumps(service_view["edges"])),
    "ranks": dict(service_view["ranks"]),
    "positions": positions,
    "canvas": canvas_size(positions),
  }


def flatten_bundle(bundle: list[dict[str, Any]]) -> dict[str, Any]:
  projects: list[dict[str, Any]] = []
  components: list[dict[str, Any]] = []
  relationships: list[dict[str, Any]] = []
  businesses: list[dict[str, Any]] = []
  component_uids: set[str] = set()

  for analysis in bundle:
    project = analysis["project"]
    project_id = project["id"]
    projects.append({
      "id": project_id,
      "name": project["name"],
      "summary": analysis["summary"],
      "analyzed_commit": project["analyzed_commit"],
      "analyzed_at": project["analyzed_at"],
      "root_path": project["root_path"],
    })
    for component in analysis["components"]:
      item = json.loads(json.dumps(component))
      item["uid"] = component_uid(project_id, component["id"])
      item["project_id"] = project_id
      item["project_name"] = project["name"]
      component_uids.add(item["uid"])
      components.append(item)

  for analysis in bundle:
    project_id = analysis["project"]["id"]
    for relationship in analysis["relationships"]:
      item = json.loads(json.dumps(relationship))
      target_project = relationship.get("target_project_id", project_id)
      item["uid"] = component_uid(project_id, relationship["id"])
      item["project_id"] = project_id
      item["source_uid"] = component_uid(project_id, relationship["source"])
      item["target_uid"] = component_uid(target_project, relationship["target"])
      item["api_uid"] = component_uid(project_id, relationship["api"]) if relationship.get("api") else None
      relationships.append(item)
      if item["target_uid"] in component_uids:
        continue
      component_uids.add(item["target_uid"])
      components.append({
        "id": relationship["target"],
        "uid": item["target_uid"],
        "project_id": target_project,
        "project_name": target_project,
        "name": f"{target_project} / {relationship['target']}",
        "kind": "external-system",
        "layer": "external",
        "origin": {"type": "git", "label": target_project},
        "role": "선택되지 않은 외부 프로젝트의 컴포넌트",
        "importance": "core",
        "owned_paths": [],
        "evidence": relationship["evidence"],
        "placeholder": True,
      })

  apis: list[dict[str, Any]] = []
  for analysis in bundle:
    project_id = analysis["project"]["id"]
    for api in analysis.get("apis", []):
      item = json.loads(json.dumps(api))
      item["uid"] = component_uid(project_id, api["id"])
      item["project_id"] = project_id
      item["project_name"] = analysis["project"]["name"]
      item["address"] = api_address(api)
      item["provider_uid"] = component_uid(
        api.get("provider_project_id", project_id), api["provider"]
      )
      item["flow_uids"] = [component_uid(project_id, flow) for flow in api.get("flow_ids", [])]
      apis.append(item)

  component_by_uid = {item["uid"]: item for item in components}
  relationship_by_uid = {item["uid"]: item for item in relationships}
  api_by_uid = {item["uid"]: item for item in apis}
  service_view = build_service_view(components, relationships)
  views: dict[str, Any] = {
    "service": service_view,
    "api": build_api_view(apis, relationships, component_by_uid),
    "load": build_load_view(service_view),
  }

  for analysis in bundle:
    project_id = analysis["project"]["id"]
    for business in analysis.get("businesses", []):
      business_uid = f"{project_id}::{business['id']}"
      flow_entries: list[str] = []
      flow_steps: list[str] = []
      flows: list[dict[str, Any]] = []
      for flow in business["flows"]:
        flow_uid = f"{project_id}::{flow['id']}"
        entry_uid = component_uid(project_id, flow["entry"])
        step_uids = [component_uid(project_id, step) for step in flow["steps"]]
        view_id = f"flow:{flow_uid}"
        views[view_id] = build_flow_view(
          view_id,
          flow["name"],
          flow["description"],
          [entry_uid],
          step_uids,
          component_by_uid,
          relationship_by_uid,
        )
        flows.append({
          "uid": flow_uid,
          "view_id": view_id,
          "name": flow["name"],
          "description": flow["description"],
          "trigger": flow.get("trigger"),
          "depth": views[view_id]["depth"],
          "step_count": len(step_uids),
        })
        flow_entries.append(entry_uid)
        flow_steps.extend(uid for uid in step_uids if uid not in flow_steps)
      business_view_id = f"business:{business_uid}"
      views[business_view_id] = build_flow_view(
        business_view_id,
        business["name"],
        business["description"],
        flow_entries,
        flow_steps,
        component_by_uid,
        relationship_by_uid,
      )
      businesses.append({
        "uid": business_uid,
        "view_id": business_view_id,
        "project_id": project_id,
        "project_name": analysis["project"]["name"],
        "name": business["name"],
        "description": business["description"],
        "flows": flows,
      })

  layout: dict[str, Any] = {}
  for analysis in bundle:
    project_id = analysis["project"]["id"]
    for view_id, saved in (analysis.get("layout") or {}).items():
      target = layout.setdefault(view_id if view_id == "service" else _qualify_view(view_id, project_id), {})
      for component_id, position in saved.items():
        target[component_uid(project_id, component_id)] = position

  for current in views.values():
    enrich_edges(current, relationship_by_uid, api_by_uid)
  for component in components:
    component.setdefault("capacity", None)
    component["cost"] = DEFAULT_COST.get(component["kind"], DEFAULT_COST["service"])

  return {
    "projects": projects,
    "businesses": businesses,
    "apis": apis,
    "components": components,
    "relationships": relationships,
    "views": views,
    "layout": layout,
    "layers": LAYERS,
    "layer_labels": LAYER_LABELS,
    "defaults": {
      "capacity": DEFAULT_CAPACITY,
      "crypto_ms": DEFAULT_CRYPTO_MS,
      "crypto_labels": CRYPTO_LABELS,
    },
  }


def _qualify_view(view_id: str, project_id: str) -> str:
  prefix, _, rest = view_id.partition(":")
  return f"{prefix}:{project_id}::{rest}" if rest else view_id


def json_for_html(data: dict[str, Any]) -> str:
  return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def render_html(bundle: list[dict[str, Any]]) -> str:
  graph = flatten_bundle(bundle)
  title = bundle[0]["project"]["name"]
  return (
    HTML_TEMPLATE
    .replace("__TITLE__", html.escape(title))
    .replace("__SUMMARY__", html.escape(bundle[0]["summary"]))
    .replace("__RELATION_COLORS__", json.dumps(RELATION_COLORS, ensure_ascii=False))
    .replace("__COMPONENT_COLORS__", json.dumps(KIND_COLORS, ensure_ascii=False))
    .replace("__ENGINE_STYLES__", json.dumps(ENGINE_STYLES, ensure_ascii=False))
    .replace("__NODE_WIDTH__", str(NODE_WIDTH))
    .replace("__NODE_HEIGHT__", str(NODE_HEIGHT))
    .replace("__DATA__", json_for_html(graph))
  )


HTML_TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ 코드 관계도</title>
<style>
:root{color-scheme:light dark;--bg:#f6f8fb;--panel:#fff;--sunk:#eef2f7;--ink:#0f172a;--muted:#64748b;
 --border:#d5dde7;--accent:#0f766e;--accent-ink:#fff;--tabbar:#1b1b1f;--tabink:#8b8b93}
@media(prefers-color-scheme:dark){:root{--bg:#070d18;--panel:#0f172a;--sunk:#131f33;--ink:#e2e8f0;
 --muted:#94a3b8;--border:#2b3a51;--accent:#2dd4bf;--accent-ink:#04231f;--tabbar:#000;--tabink:#6b7280}}
*{box-sizing:border-box}
body{margin:0;height:100vh;display:flex;flex-direction:column;overflow:hidden;
 font:13px/1.5 ui-sans-serif,system-ui,-apple-system,"Noto Sans KR",sans-serif;background:var(--bg);color:var(--ink)}
header{padding:10px 18px;border-bottom:1px solid var(--border);background:var(--panel);flex:none}
h1{margin:0;font-size:15px}
header p{margin:2px 0 0;color:var(--muted);font-size:12px}
.app{flex:1;min-height:0;display:grid;grid-template-columns:252px minmax(0,1fr)}
.sidebar{background:var(--panel);border-right:1px solid var(--border);display:flex;flex-direction:column;
 overflow:hidden;min-height:0}
.modes{display:flex;padding:8px;gap:0;border-bottom:1px solid var(--border);flex:none}
.modes button{flex:1;padding:6px 4px;font:inherit;font-size:12px;font-weight:600;cursor:pointer;
 color:var(--muted);background:var(--sunk);border:1px solid var(--border)}
.modes button:first-child{border-radius:7px 0 0 7px}
.modes button:last-child{border-radius:0 7px 7px 0}
.modes button+button{border-left:0}
.modes button[aria-pressed=true]{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.side-search{padding:8px 10px 0;flex:none}
input[type=search],select,input[type=number]{width:100%;padding:6px 9px;border:1px solid var(--border);
 border-radius:7px;background:var(--bg);color:var(--ink);font:inherit}
#toc{padding:8px;overflow:auto;flex:1;min-height:0}
.toc-group{margin-bottom:8px}
.toc-item{display:block;width:100%;text-align:left;padding:6px 9px;border:0;border-radius:7px;cursor:pointer;
 font:inherit;background:none;color:var(--ink)}
.toc-item:hover{background:var(--sunk)}
.toc-item[aria-current=true]{background:var(--accent);color:var(--accent-ink)}
.toc-item.domain{font-weight:700}
.toc-item.flow{padding-left:20px;font-size:12px;color:var(--muted)}
.toc-item.flow[aria-current=true]{color:var(--accent-ink)}
.toc-item small{display:block;font-weight:400;font-size:11px;opacity:.78}
.toc-title{padding:10px 9px 4px;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.knob{padding:6px 9px}
.knob label{display:flex;justify-content:space-between;font-size:11.5px;color:var(--muted);margin-bottom:2px}
.knob label b{color:var(--ink);font-variant-numeric:tabular-nums}
.knob input[type=range]{width:100%;margin:0;accent-color:var(--accent)}
.stage{display:flex;flex-direction:column;min-width:0;min-height:0}
.stagebar{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:baseline;padding:8px 14px;flex:none;
 border-bottom:1px solid var(--border);background:var(--panel)}
.stagebar b{font-size:13px}
.stagebar .desc{color:var(--muted);font-size:11.5px;margin-right:auto}
.chips{display:flex;flex-wrap:wrap;gap:4px}
.chip{padding:2px 8px;border:1px solid var(--border);border-radius:99px;font-size:11px;cursor:pointer;
 background:var(--sunk);color:var(--muted);user-select:none}
.chip[aria-pressed=true]{color:var(--ink);border-color:currentColor}
.chip i{display:inline-block;width:7px;height:7px;border-radius:99px;margin-right:4px;vertical-align:1px}
.tool{padding:4px 9px;border:1px solid var(--border);border-radius:7px;background:var(--sunk);color:var(--ink);
 font:inherit;font-size:11px;cursor:pointer}
.canvas-wrap{flex:1;min-height:0;position:relative;background:var(--panel);margin:10px 14px;
 border:1px solid var(--border);border-radius:10px;overflow:hidden}
#graph{display:block;width:100%;height:100%;touch-action:none;cursor:grab}
#graph.panning{cursor:grabbing}
.tabbar svg{display:block}
.node{cursor:grab}
.node rect.box,.node circle.box{stroke-width:1.5;stroke:#ffffff5c}
.node .title{fill:#fff;font-size:12.5px;font-weight:700}
.node .sub{fill:#ffffffc4;font-size:9.5px}
.node.round .title{fill:var(--ink);font-size:11.5px;text-anchor:middle}
.node.round .sub{fill:var(--muted);font-size:10px;text-anchor:middle}
.node.dim{opacity:.14}
.node.selected rect.box,.node.selected circle.box{stroke:#f59e0b;stroke-width:3}
.edge path{fill:none;stroke-width:1.9}
.edge .hit{stroke:transparent;stroke-width:14;cursor:pointer}
.edge text{font-size:10.5px;fill:var(--ink);paint-order:stroke;stroke:var(--panel);stroke-width:4px;
 stroke-linejoin:round}
.edge .endpoint{font-size:9.5px;fill:var(--muted);font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.edge.dim{opacity:.07}
.edge.selected path:not(.hit){stroke-width:4}
.step circle{fill:var(--panel);stroke-width:1.5}
.step text{font-size:9.5px;font-weight:700;stroke:none;fill:var(--ink)}
.dock{flex:none;border-top:1px solid var(--border);background:var(--panel);display:flex;flex-direction:column;
 max-height:44vh}
.dock-bar{display:flex;align-items:center;gap:8px;padding:6px 14px;cursor:pointer;flex:none}
.dock-bar strong{font-size:12px}
.dock-bar span{color:var(--muted);font-size:11.5px;margin-right:auto}
.dock-body{padding:0 14px 12px;overflow:auto;min-height:0}
.dock[data-open=false] .dock-body{display:none}
.dock-cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:0 22px}
.dock h3{margin:12px 0 4px;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.badge{display:inline-block;padding:1px 7px;margin:0 4px 4px 0;border:1px solid var(--border);
 border-radius:99px;font-size:11px}
.badge.hot{border-color:#ef4444;color:#ef4444}
.relation{padding:5px 0;border-bottom:1px solid var(--border);cursor:pointer;font-size:12px}
.relation:hover{color:var(--accent)}
.evidence{padding:5px 0;font-size:12px}
code{overflow-wrap:anywhere;color:#0ea5e9;font-size:11.5px;
 font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.empty{color:var(--muted)}
table{border-collapse:collapse;width:100%;font-size:11.5px;font-variant-numeric:tabular-nums}
th,td{text-align:right;padding:3px 6px;border-bottom:1px solid var(--border);white-space:nowrap}
th:first-child,td:first-child{text-align:left}
th{color:var(--muted);font-weight:600}
.tabbar{flex:none;display:flex;justify-content:center;gap:2px;background:var(--tabbar);
 border-top:1px solid #000}
.tabbar button{width:132px;padding:9px 0 7px;border:0;border-top:2px solid transparent;background:none;
 color:var(--tabink);font:inherit;font-size:11px;cursor:pointer;display:flex;flex-direction:column;
 align-items:center;gap:3px}
.tabbar button[aria-pressed=true]{color:#fff;background:#0000004d;border-top-color:#ff4d4d}
@media(max-width:1180px){.app{grid-template-columns:212px minmax(0,1fr)}}
@media(max-width:900px){
 body{height:auto;overflow:auto}
 .app{grid-template-columns:1fr}
 .sidebar{border-right:0;border-bottom:1px solid var(--border);max-height:44vh}
 .canvas-wrap{height:60vh}
 .tabbar{position:sticky;bottom:0}
}
</style>
</head>
<body>
<header>
  <h1>__TITLE__ 코드 관계도</h1>
  <p>__SUMMARY__</p>
</header>
<div class="app">
  <nav class="sidebar">
    <div class="modes" id="modes"></div>
    <div class="side-search"><input id="search" type="search" placeholder="검색"></div>
    <div id="toc"></div>
  </nav>
  <div class="stage">
    <div class="stagebar">
      <b id="view-title"></b>
      <span class="desc" id="view-desc"></span>
      <label id="depth-box">깊이 <select id="depth"></select></label>
      <div id="filters" class="chips"></div>
      <button id="reset" class="tool" type="button">자동 배치</button>
      <button id="copy" class="tool" type="button">배치 복사</button>
    </div>
    <div class="canvas-wrap"><svg id="graph" role="img" aria-label="코드 관계도"></svg></div>
    <div class="dock" id="dock" data-open="false">
      <div class="dock-bar" id="dock-bar">
        <strong id="dock-title">상세</strong>
        <span id="dock-hint">컴포넌트나 관계를 클릭하세요</span>
        <button class="tool" type="button" id="dock-toggle">열기</button>
      </div>
      <div class="dock-body" id="detail"></div>
    </div>
  </div>
</div>
<nav class="tabbar">
  <button id="tab-analysis" type="button" aria-pressed="true">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
      <circle cx="5" cy="12" r="2.4"/><circle cx="19" cy="6" r="2.4"/><circle cx="19" cy="18" r="2.4"/>
      <path d="M7.2 11 16.8 6.8M7.2 13 16.8 17.2"/></svg>
    분석
  </button>
  <button id="tab-load" type="button" aria-pressed="false">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
      <path d="M3.5 17a9 9 0 1 1 17 0" stroke-linecap="round"/>
      <path d="M12 17 16.5 9.8" stroke-linecap="round"/><circle cx="12" cy="17" r="1.6" fill="currentColor"/></svg>
    부하분석
  </button>
</nav>
<script id="analysis-data" type="application/json">__DATA__</script>
<script>
const DATA=JSON.parse(document.getElementById('analysis-data').textContent);
const RELATION_COLORS=__RELATION_COLORS__;
const COMPONENT_COLORS=__COMPONENT_COLORS__;
const ENGINE_STYLES=__ENGINE_STYLES__;
const NODE={w:__NODE_WIDTH__,h:__NODE_HEIGHT__,r:34};
const NS='http://www.w3.org/2000/svg';
const svg=document.getElementById('graph');
const detail=document.getElementById('detail');
const dock=document.getElementById('dock');
const nodeById=new Map(DATA.components.map(item=>[item.uid,item]));
const relById=new Map(DATA.relationships.map(item=>[item.uid,item]));
const apiById=new Map(DATA.apis.map(item=>[item.uid,item]));
const layout=DATA.layout||{};
const activeKinds=new Set(Object.keys(RELATION_COLORS));
const edgeGroups=new Map();
const MODES={
  analysis:[['business','비즈니스'],['service','서비스'],['api','API']],
  load:[['load','부하 전파']]
};
let tab='analysis';
let mode='business';
let viewId=null;
let selected=null;
let maxDepth=DATA.layers.length;
let camera=null;

const esc=value=>String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const el=(name,attrs)=>{const node=document.createElementNS(NS,name);
  for(const key in attrs||{})node.setAttribute(key,attrs[key]);return node;};
const view=()=>DATA.views[viewId];
const clip=(text,max)=>String(text||'').length>max?String(text).slice(0,max-1)+'…':String(text||'');
const num=(value,digits)=>Number(value||0).toLocaleString('ko-KR',{maximumFractionDigits:digits??0});

/* ---------- 부하 모델 ---------- */
const loadState={rps:{},cost:{},cap:{},crypto:{...DATA.defaults.crypto_ms}};
function capOf(uid){
  if(loadState.cap[uid])return loadState.cap[uid];
  const item=nodeById.get(uid);
  const base=(item&&item.capacity)||DATA.defaults.capacity;
  loadState.cap[uid]={replicas:base.replicas,cpu_millicores:base.cpu_millicores,memory_mib:base.memory_mib};
  return loadState.cap[uid];
}
function costOf(uid){
  if(loadState.cost[uid])return loadState.cost[uid];
  const item=nodeById.get(uid);
  loadState.cost[uid]={...((item&&item.cost)||{cpu_ms:8,mem_kib:256})};
  return loadState.cost[uid];
}
function entryApis(){return DATA.apis.filter(api=>api.entrypoint);}
function rpsOf(apiUid){return loadState.rps[apiUid]??100;}
function computeLoad(){
  const current=DATA.views.load;
  const rank=uid=>current.ranks[uid]||0;
  const rps={},edgeRps={};
  const entries=entryApis().filter(api=>current.nodes.includes(api.provider_uid));
  if(entries.length){
    entries.forEach(api=>{rps[api.provider_uid]=(rps[api.provider_uid]||0)+rpsOf(api.uid);});
  }else{
    // 진입점 API 가 없으면 들어오는 관계가 없는 노드를 진입점으로 본다.
    const hasIncoming=new Set(current.edges.map(edge=>edge.target_uid));
    current.nodes.filter(uid=>!hasIncoming.has(uid)).forEach(uid=>{rps[uid]=100;});
  }
  // ponytail: 위상 순서 한 번만 훑는다. 되돌아가는 관계는 하류로 다시 퍼뜨리지 않는다.
  const forward=current.nodes.slice().sort((a,b)=>rank(a)-rank(b));
  forward.forEach(uid=>{
    current.edges.filter(edge=>edge.source_uid===uid).forEach(edge=>{
      const flow=(rps[uid]||0)*(edge.load.fan_out??1);
      edgeRps[edge.uid]=(edgeRps[edge.uid]||0)+flow;
      rps[edge.target_uid]=(rps[edge.target_uid]||0)+flow;
    });
  });
  const metrics={};
  current.nodes.forEach(uid=>{
    const cap=capOf(uid),cost=costOf(uid),requests=rps[uid]||0;
    let cryptoMsPerSec=0;
    current.edges.forEach(edge=>{
      if(edge.source_uid!==uid&&edge.target_uid!==uid)return;
      cryptoMsPerSec+=(loadState.crypto[edge.load.crypto]||0)*(edgeRps[edge.uid]||0);
    });
    const cpuMsPerSec=requests*cost.cpu_ms+cryptoMsPerSec;
    const availableMsPerSec=cap.replicas*cap.cpu_millicores;
    metrics[uid]={
      rps:requests,
      cryptoMs:requests?cryptoMsPerSec/requests:0,
      serviceMs:cost.cpu_ms+(requests?cryptoMsPerSec/requests:0),
      cpuUtil:availableMsPerSec?cpuMsPerSec/availableMsPerSec:0,
      cap,cost
    };
  });
  // 대기시간은 하류부터 거슬러 올라오며 합친다. 이게 부하가 선형이 아닌 이유다.
  current.nodes.slice().sort((a,b)=>rank(b)-rank(a)).forEach(uid=>{
    const m=metrics[uid];
    const used=Math.min(m.cpuUtil,0.995);
    m.waitMs=m.serviceMs*used/(1-used);
    m.selfMs=m.serviceMs+m.waitMs;
    m.downstreamMs=current.edges
      .filter(edge=>edge.source_uid===uid&&edge.load.sync&&metrics[edge.target_uid])
      .reduce((total,edge)=>total+(edge.load.fan_out??1)*(metrics[edge.target_uid].totalMs||0),0);
    m.totalMs=m.selfMs+m.downstreamMs;
  });
  current.nodes.forEach(uid=>{
    const m=metrics[uid];
    m.inFlight=m.rps*m.totalMs/1000;
    m.memMib=m.inFlight*m.cost.mem_kib/1024;
    const memCap=m.cap.replicas*m.cap.memory_mib;
    m.memUtil=memCap?m.memMib/memCap:0;
    m.stress=Math.max(m.cpuUtil,m.memUtil);
  });
  return {rps,edgeRps,metrics};
}
function stressColor(stress){
  const t=Math.min(stress,1.3)/1.3;
  return 'hsl('+(145-145*Math.min(t/0.78,1))+' '+(50+40*t)+'% '+(stress>=1?40:52)+'%)';
}
let loadResult=null;

/* ---------- 왼쪽 ---------- */
function buildModes(){
  const container=document.getElementById('modes');
  container.replaceChildren();
  container.style.display=MODES[tab].length>1?'':'none';
  MODES[tab].forEach(entry=>{
    const button=document.createElement('button');
    button.type='button';
    button.textContent=entry[1];
    button.setAttribute('aria-pressed',String(mode===entry[0]));
    button.addEventListener('click',()=>setMode(entry[0]));
    container.append(button);
  });
}
function tocButton(parent,className,label,note,id,onClick){
  const button=document.createElement('button');
  button.type='button';
  button.className='toc-item '+className;
  button.innerHTML=esc(label)+(note?'<small>'+esc(note)+'</small>':'');
  if(id)button.setAttribute('aria-current',String(viewId===id));
  button.addEventListener('click',onClick);
  parent.append(button);
  return button;
}
function knob(parent,label,value,unit,min,max,step,onInput){
  const box=document.createElement('div');
  box.className='knob';
  box.innerHTML='<label><span>'+esc(label)+'</span><b>'+num(value,2)+esc(unit)+'</b></label>';
  const range=document.createElement('input');
  range.type='range';range.min=min;range.max=max;range.step=step;range.value=value;
  range.addEventListener('input',()=>{
    box.querySelector('b').textContent=num(Number(range.value),2)+unit;
    onInput(Number(range.value));
  });
  box.append(range);
  parent.append(box);
}
function buildToc(){
  const container=document.getElementById('toc');
  const query=document.getElementById('search').value.trim().toLowerCase();
  const hit=text=>!query||String(text||'').toLowerCase().includes(query);
  container.replaceChildren();
  if(tab==='load')return buildLoadToc(container,hit);
  if(mode==='business')return buildBusinessToc(container,hit);
  if(mode==='api')return buildApiToc(container,hit);
  return buildServiceToc(container,hit);
}
function buildBusinessToc(container,hit){
  if(!DATA.businesses.length){
    container.innerHTML='<p class="empty" style="padding:8px 9px">기록된 비즈니스 흐름이 없습니다.</p>';
    return;
  }
  DATA.businesses.forEach(business=>{
    const flows=business.flows.filter(flow=>hit(flow.name)||hit(flow.description)||hit(business.name));
    if(!flows.length&&!hit(business.name)&&!hit(business.description))return;
    const group=document.createElement('div');
    group.className='toc-group';
    tocButton(group,'domain',business.name,business.description,business.view_id,
      ()=>selectView(business.view_id));
    flows.forEach(flow=>tocButton(group,'flow',flow.name,
      (flow.trigger?flow.trigger+' · ':'')+flow.depth+'단계 '+flow.step_count+'스텝',
      flow.view_id,()=>selectView(flow.view_id)));
    container.append(group);
  });
}
function buildServiceToc(container,hit){
  const group=document.createElement('div');
  group.className='toc-group';
  tocButton(group,'domain','전체 서비스 관계도','module 을 접은 배포 단위 화면','service',
    ()=>selectView('service'));
  DATA.views.service.nodes.map(uid=>nodeById.get(uid))
    .filter(item=>item&&(hit(item.name)||hit(item.role)))
    .sort((a,b)=>a.name.localeCompare(b.name))
    .forEach(item=>tocButton(group,'flow',item.name,
      DATA.layer_labels[item.layer]+' · '+item.kind,null,
      ()=>{selectView('service');selectComponent(item.uid);}));
  container.append(group);
}
function buildApiToc(container,hit){
  const group=document.createElement('div');
  group.className='toc-group';
  tocButton(group,'domain','API 관계도',DATA.apis.length+'개 API','api',()=>selectView('api'));
  if(!DATA.apis.length){
    container.innerHTML+='<p class="empty" style="padding:8px 9px">기록된 API 가 없습니다.</p>';
    container.append(group);
    return;
  }
  ['진입점','내부 호출'].forEach(section=>{
    const wanted=section==='진입점';
    const list=DATA.apis.filter(api=>Boolean(api.entrypoint)===wanted
      &&(hit(api.name)||hit(api.address)||hit(api.protocol)));
    if(!list.length)return;
    const title=document.createElement('div');
    title.className='toc-title';
    title.textContent=section;
    group.append(title);
    list.sort((a,b)=>a.address.localeCompare(b.address)).forEach(api=>
      tocButton(group,'flow',api.address,
        api.name+' · '+(nodeById.get(api.provider_uid)?.name||api.provider),null,
        ()=>{selectView('api');selectApi(api.uid);}));
  });
  container.append(group);
}
function buildLoadToc(container,hit){
  const entries=entryApis();
  const title=document.createElement('div');
  title.className='toc-title';
  title.textContent=entries.length?'진입점 요청량 (rps)':'진입점 API 없음';
  container.append(title);
  if(!entries.length){
    const note=document.createElement('p');
    note.className='empty';
    note.style.padding='0 9px';
    note.textContent='들어오는 관계가 없는 컴포넌트를 100 rps 로 가정합니다.';
    container.append(note);
  }
  entries.filter(api=>hit(api.name)||hit(api.address)).forEach(api=>
    knob(container,api.address,rpsOf(api.uid),' rps',0,5000,10,value=>{
      loadState.rps[api.uid]=value;paint();
    }));

  const cryptoTitle=document.createElement('div');
  cryptoTitle.className='toc-title';
  cryptoTitle.textContent='암복호화 비용 (요청 1건당 CPU ms)';
  container.append(cryptoTitle);
  ['tls','mtls','field','kms'].forEach(kind=>
    knob(container,DATA.defaults.crypto_labels[kind],loadState.crypto[kind],' ms',0,50,0.1,value=>{
      loadState.crypto[kind]=value;paint();
    }));

  const target=selected&&nodeById.has(selected)?selected:null;
  const pickTitle=document.createElement('div');
  pickTitle.className='toc-title';
  pickTitle.textContent=target?nodeById.get(target).name+' 자원':'컴포넌트를 클릭하면 자원 조절';
  container.append(pickTitle);
  if(!target)return;
  const cap=capOf(target),cost=costOf(target);
  const item=nodeById.get(target);
  if(item.capacity){
    const note=document.createElement('p');
    note.className='empty';
    note.style.padding='0 9px';
    note.style.fontSize='11px';
    note.textContent=item.capacity.source==='manifest'
      ?'매니페스트에서 읽은 값이 기본값입니다.'
      :'근거 없는 가정값이 기본값입니다.';
    container.append(note);
  }
  knob(container,'서버 수 (replicas)',cap.replicas,'대',1,200,1,value=>{cap.replicas=value;paint();});
  knob(container,'CPU (millicores/대)',cap.cpu_millicores,'m',50,16000,50,value=>{
    cap.cpu_millicores=value;paint();});
  knob(container,'메모리 (MiB/대)',cap.memory_mib,'MiB',64,65536,64,value=>{
    cap.memory_mib=value;paint();});
  knob(container,'요청당 CPU',cost.cpu_ms,'ms',0.1,500,0.1,value=>{cost.cpu_ms=value;paint();});
  knob(container,'요청당 메모리',cost.mem_kib,'KiB',1,20000,1,value=>{cost.mem_kib=value;paint();});
}

/* ---------- 아이콘 ---------- */
function originIcon(component,offset){
  const origin=component.origin||{type:'code',label:''};
  const style=ENGINE_STYLES[origin.engine]||{color:'#e2e8f0',family:'db'};
  const group=el('g',{transform:'translate('+offset[0]+' '+offset[1]+')'});
  const paint=origin.type==='database'?style.color:(offset[2]||'#ffffff');
  if(origin.type==='git'){
    [[3,3],[3,11],[11,7]].forEach(point=>group.append(
      el('circle',{cx:point[0],cy:point[1],r:'2.1',fill:paint})));
    group.append(el('path',{d:'M3 3 V11 M3 7 H11',stroke:paint,'stroke-width':'1.3',fill:'none'}));
  }else if(origin.type==='code'){
    group.append(el('path',{d:'M5 3 L1 7 L5 11 M9 3 L13 7 L9 11',stroke:paint,'stroke-width':'1.6',
      fill:'none','stroke-linecap':'round','stroke-linejoin':'round'}));
  }else if(style.family==='bucket'){
    group.append(el('path',{d:'M1.5 3 H12.5 L11 12 H3 Z',stroke:paint,'stroke-width':'1.4',fill:'none'}));
    group.append(el('path',{d:'M2 6.5 H12',stroke:paint,'stroke-width':'1.2'}));
  }else if(style.family==='queue'){
    [1,5.2,9.4].forEach(y=>group.append(el('rect',{x:'1.5',y:String(y),width:'11',height:'3',rx:'1',
      fill:'none',stroke:paint,'stroke-width':'1.3'})));
  }else if(style.family==='cache'){
    group.append(el('path',{d:'M7 1 L12.5 7 L7 13 L1.5 7 Z',stroke:paint,'stroke-width':'1.4',fill:'none'}));
  }else if(style.family==='search'){
    group.append(el('circle',{cx:'6',cy:'6',r:'4.2',fill:'none',stroke:paint,'stroke-width':'1.4'}));
    group.append(el('path',{d:'M9.3 9.3 L12.5 12.5',stroke:paint,'stroke-width':'1.6','stroke-linecap':'round'}));
  }else{
    group.append(el('ellipse',{cx:'7',cy:'3',rx:'5.5',ry:'2',fill:'none',stroke:paint,'stroke-width':'1.4'}));
    group.append(el('path',{d:'M1.5 3 V11 A5.5 2 0 0 0 12.5 11 V3',fill:'none',stroke:paint,'stroke-width':'1.4'}));
    group.append(el('path',{d:'M1.5 7 A5.5 2 0 0 0 12.5 7',fill:'none',stroke:paint,'stroke-width':'1.1'}));
  }
  const label=el('title');
  label.textContent=origin.type+' · '+origin.label+(origin.engine?' ('+origin.engine+')':'');
  group.append(label);
  return group;
}
function originText(component){
  const origin=component.origin||{};
  const engine=origin.engine?(ENGINE_STYLES[origin.engine]||{}).short||origin.engine:null;
  return [engine,origin.label].filter(Boolean).join(' · ');
}

/* ---------- 기하 ---------- */
const isRound=()=>tab==='load';
const halfW=()=>isRound()?NODE.r:NODE.w/2;
const halfH=()=>isRound()?NODE.r:NODE.h/2;
function boxOf(uid){
  const point=positionOf(uid);
  return isRound()
    ?{x:point.x-NODE.r,y:point.y-NODE.r,w:NODE.r*2,h:NODE.r*2,cx:point.x,cy:point.y}
    :{x:point.x,y:point.y,w:NODE.w,h:NODE.h,cx:point.x+NODE.w/2,cy:point.y+NODE.h/2};
}
function positionOf(uid){
  const saved=(layout[viewId]||{})[uid];
  return saved||view().positions[uid]||{x:0,y:0};
}
function setPosition(uid,point){
  if(!layout[viewId])layout[viewId]={};
  layout[viewId][uid]={x:Math.round(point.x),y:Math.round(point.y)};
}
function visibleParts(){
  const current=view();
  const query=document.getElementById('search').value.trim().toLowerCase();
  const nodes=new Set(current.nodes.filter(uid=>(current.ranks[uid]||0)<maxDepth));
  let edges=current.edges.filter(edge=>
    activeKinds.has(edge.kind)&&nodes.has(edge.source_uid)&&nodes.has(edge.target_uid));
  if(query&&(mode==='service'||mode==='api')&&tab==='analysis'){
    const matched=new Set([...nodes].filter(uid=>{
      const item=nodeById.get(uid);
      return item&&(item.name+' '+item.role).toLowerCase().includes(query);
    }));
    edges.forEach(edge=>{
      if(matched.has(edge.source_uid))matched.add(edge.target_uid);
      if(matched.has(edge.target_uid))matched.add(edge.source_uid);
    });
    [...nodes].forEach(uid=>{if(!matched.has(uid))nodes.delete(uid);});
    edges=edges.filter(edge=>nodes.has(edge.source_uid)&&nodes.has(edge.target_uid));
  }
  return {nodes,edges};
}
function edgeSlots(edges){
  // 노드 테두리에서 나가고 들어오는 접점을 상대 노드의 높이 순서대로 나눠 배치한다.
  const out=new Map(),into=new Map(),lane=new Map();
  const groups=new Map(),pairs=new Map();
  edges.forEach(edge=>{
    if(!groups.has(edge.source_uid))groups.set(edge.source_uid,{out:[],in:[]});
    if(!groups.has(edge.target_uid))groups.set(edge.target_uid,{out:[],in:[]});
    groups.get(edge.source_uid).out.push(edge);
    groups.get(edge.target_uid).in.push(edge);
    const key=[edge.source_uid,edge.target_uid].sort().join('|');
    pairs.set(key,(pairs.get(key)||[]).concat([edge.uid]));
  });
  groups.forEach(slot=>{
    ['out','in'].forEach(side=>{
      const list=slot[side].slice().sort((a,b)=>{
        const other=edge=>boxOf(side==='out'?edge.target_uid:edge.source_uid).cy;
        return other(a)-other(b);
      });
      list.forEach((edge,index)=>
        (side==='out'?out:into).set(edge.uid,(index+1)/(list.length+1)));
    });
  });
  pairs.forEach(uids=>uids.forEach((uid,index)=>lane.set(uid,index-(uids.length-1)/2)));
  return {out,in:into,lane};
}
function edgePath(edge,slots){
  const from=boxOf(edge.source_uid),to=boxOf(edge.target_uid);
  const lane=slots.lane.get(edge.uid)||0;
  const out=slots.out.get(edge.uid)??0.5,into=slots.in.get(edge.uid)??0.5;
  const backwards=to.cx<from.cx;
  const sx=backwards?from.x:from.x+from.w;
  const tx=backwards?to.x+to.w:to.x;
  const sy=isRound()?from.cy+(out-0.5)*from.h*0.7:from.y+from.h*out;
  const ty=isRound()?to.cy+(into-0.5)*to.h*0.7:to.y+to.h*into;
  // 같은 노드쌍에 여러 관계가 있거나 열을 건너뛰면 제어점을 어긋나게 해 선이 포개지지 않게 한다.
  const span=Math.max(1,Math.abs(tx-sx)/240);
  const bend=Math.min(200,Math.max(56,Math.abs(tx-sx)*0.45))*(backwards?-1:1);
  const drop=lane*22+(span>1.6?(lane>=0?1:-1)*span*14:0);
  return 'M '+sx+' '+sy+' C '+(sx+bend)+' '+(sy+drop)+', '+(tx-bend)+' '+(ty+drop)+', '+tx+' '+ty;
}

/* ---------- 그리기 ---------- */
function paint(){
  const current=view();
  if(!current)return;
  if(tab==='load')loadResult=computeLoad();
  const {nodes,edges}=visibleParts();
  svg.replaceChildren();
  const defs=el('defs');
  Object.keys(RELATION_COLORS).forEach(kind=>{
    const marker=el('marker',{id:'arrow-'+kind,viewBox:'0 0 10 10',refX:'9',refY:'5',
      markerWidth:'6',markerHeight:'6',orient:'auto-start-reverse'});
    marker.append(el('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:RELATION_COLORS[kind]}));
    defs.append(marker);
  });
  svg.append(defs);
  const edgeLayer=el('g',{id:'edges'}),nodeLayer=el('g',{id:'nodes'});
  svg.append(edgeLayer,nodeLayer);
  edgeGroups.clear();
  const slots=edgeSlots(edges);
  const peakRps=tab==='load'
    ?Math.max(1,...edges.map(edge=>loadResult.edgeRps[edge.uid]||0)):1;
  edges.forEach(edge=>{
    const d=edgePath(edge,slots);
    const group=el('g',{class:'edge','data-id':edge.uid});
    const flow=tab==='load'?(loadResult.edgeRps[edge.uid]||0):0;
    group.append(el('path',{class:'hit',d}));
    group.append(el('path',{d,stroke:RELATION_COLORS[edge.kind],
      'stroke-width':tab==='load'?String(1.2+3.4*Math.sqrt(flow/peakRps)):'1.9',
      'marker-end':'url(#arrow-'+edge.kind+')','stroke-dasharray':edge.derived?'6 4':'none'}));
    group.addEventListener('click',event=>{event.stopPropagation();selectEdge(edge);});
    edgeGroups.set(edge.uid,group);
    edgeLayer.append(group);
  });
  nodes.forEach(uid=>{
    const item=nodeById.get(uid);
    if(!item)return;
    const box=boxOf(uid);
    const group=el('g',{class:'node'+(isRound()?' round':''),'data-id':uid});
    if(isRound()){
      const metric=loadResult&&loadResult.metrics[uid];
      group.setAttribute('transform','translate('+box.cx+' '+box.cy+')');
      group.append(el('circle',{class:'box',r:NODE.r,
        fill:metric?stressColor(metric.stress):'#94a3b8','fill-opacity':'0.9'}));
      group.append(originIcon(item,[-7,-18,'#ffffff']));
      const name=el('text',{class:'title',y:'9'});
      name.textContent=clip(item.name,7);
      const sub=el('text',{class:'sub',y:NODE.r+14});
      sub.textContent=metric?num(metric.rps)+' rps · '+num(metric.stress*100)+'%':'';
      const full=el('title');
      full.textContent=item.name+(metric?' · '+num(metric.stress*100)+'%':'');
      group.append(name,sub,full);
    }else{
      group.setAttribute('transform','translate('+box.x+' '+box.y+')');
      group.append(el('rect',{class:'box',width:NODE.w,height:NODE.h,
        rx:item.kind==='datastore'?'18':item.kind==='module'?'6':'10',
        fill:COMPONENT_COLORS[item.kind]||'#475569',
        'stroke-dasharray':item.placeholder?'6 4':'none'}));
      group.append(originIcon(item,[10,9,'#ffffff']));
      const name=el('text',{class:'title',x:'32',y:'21'});
      name.textContent=clip(item.name,18);
      const sub=el('text',{class:'sub',x:'12',y:'40'});
      sub.textContent=clip(DATA.layer_labels[item.layer]+' · '+originText(item),32);
      group.append(name,sub);
    }
    group.addEventListener('click',event=>{event.stopPropagation();selectComponent(uid);});
    group.addEventListener('pointerdown',event=>startDrag(event,uid,group));
    nodeLayer.append(group);
  });
  labelEdges(edges,slots);
  // 카메라를 맞추기 전에 dock 을 먼저 채운다. 나중에 채우면 캔버스가 줄어들어 그래프가 작아진다.
  if(tab==='load')refreshDock();
  if(!camera)fitCamera(nodes);
  applyCamera();
  applySelection();
}
function refreshDock(){
  // 부하 수치는 슬라이더를 움직일 때마다 바뀌므로 열려 있는 상세도 같이 다시 그린다.
  // 이때 ToC 는 건드리지 않는다. 드래그 중인 슬라이더가 통째로 교체되면 조작이 끊긴다.
  if(selected&&nodeById.has(selected))selectComponent(selected,true);
  else if(selected){
    const edge=view().edges.find(item=>item.uid===selected);
    if(edge)selectEdge(edge); else showViewSummary();
  }else showViewSummary();
}
function labelEdges(edges,slots){
  // 경로 위 위치를 조금씩 다르게 잡아 배지와 글자가 서로 겹치지 않게 한다.
  const spread=new Map();
  edges.forEach(edge=>{
    const group=edgeGroups.get(edge.uid);
    if(!group)return;
    const path=group.querySelector('path:not(.hit)');
    const total=path.getTotalLength?path.getTotalLength():0;
    if(!total)return;
    const seen=(spread.get(edge.source_uid)||0);
    spread.set(edge.source_uid,seen+1);
    const point=path.getPointAtLength(total*(0.42+0.09*(seen%3)));
    if(edge.step){
      const badge=el('g',{class:'step',transform:'translate('+point.x+' '+point.y+')'});
      badge.append(el('circle',{r:'9',stroke:RELATION_COLORS[edge.kind]}));
      const number=el('text',{'text-anchor':'middle',y:'3.4'});
      number.textContent=edge.step;
      badge.append(number);
      group.append(badge);
      return;
    }
    const primary=tab==='load'
      ?num(loadResult.edgeRps[edge.uid])+' rps'+((edge.load.fan_out??1)!==1?' ×'+edge.load.fan_out:'')
      :(mode==='api'&&edge.endpoint?edge.endpoint:clip(edge.label,20));
    const label=el('text',{class:'lbl',x:point.x,y:point.y-6,'text-anchor':'middle'});
    label.textContent=primary;
    group.append(label);
    const extra=tab==='load'
      ?(edge.load.crypto!=='none'?DATA.defaults.crypto_labels[edge.load.crypto]:'')
      :(mode!=='api'&&edge.endpoint?edge.endpoint:'');
    if(!extra)return;
    const second=el('text',{class:'lbl endpoint',x:point.x,y:point.y+7,'text-anchor':'middle'});
    second.textContent=clip(extra,26);
    group.append(second);
  });
}
function fitCamera(nodes){
  const boxes=[...nodes].map(uid=>boxOf(uid));
  if(!boxes.length){camera={x:0,y:0,w:900,h:520};return;}
  const pad=isRound()?86:64;
  const minX=Math.min(...boxes.map(box=>box.x))-pad;
  const minY=Math.min(...boxes.map(box=>box.y))-pad;
  const maxX=Math.max(...boxes.map(box=>box.x+box.w))+pad;
  const maxY=Math.max(...boxes.map(box=>box.y+box.h))+pad;
  const rect=svg.getBoundingClientRect();
  const boxWidth=rect.width||1200,boxHeight=rect.height||600;
  let width=maxX-minX,height=maxY-minY;
  // 화면 비율에 맞춰 부족한 쪽을 늘려야 가로세로가 늘어나 보이지 않는다.
  if(width/height<boxWidth/boxHeight)width=height*boxWidth/boxHeight; else height=width*boxHeight/boxWidth;
  // 내용이 화면보다 작으면 확대하지 않는다. 노드 몇 개가 화면을 가득 채우면 오히려 읽기 나쁘다.
  if(width<boxWidth){width=boxWidth;height=boxHeight;}
  camera={x:(minX+maxX)/2-width/2,y:(minY+maxY)/2-height/2,w:width,h:height};
}
function applyCamera(){svg.setAttribute('viewBox',camera.x+' '+camera.y+' '+camera.w+' '+camera.h);}
function toSvgPoint(event){
  const rect=svg.getBoundingClientRect();
  return {x:camera.x+(event.clientX-rect.left)/rect.width*camera.w,
          y:camera.y+(event.clientY-rect.top)/rect.height*camera.h};
}

/* ---------- 이동 ---------- */
function startDrag(event,uid,group){
  if(event.button!==0)return;
  event.stopPropagation();
  const start=toSvgPoint(event),origin=positionOf(uid);
  const offset={x:start.x-origin.x,y:start.y-origin.y};
  let moved=false;
  group.setPointerCapture(event.pointerId);
  const move=next=>{
    const point=toSvgPoint(next);
    moved=true;
    setPosition(uid,{x:point.x-offset.x,y:point.y-offset.y});
    const box=boxOf(uid);
    group.setAttribute('transform','translate('+(isRound()?box.cx:box.x)+' '+(isRound()?box.cy:box.y)+')');
    redrawEdges();
  };
  const stop=()=>{
    group.releasePointerCapture(event.pointerId);
    group.removeEventListener('pointermove',move);
    group.removeEventListener('pointerup',stop);
    group.removeEventListener('pointercancel',stop);
    if(moved)paint();
  };
  group.addEventListener('pointermove',move);
  group.addEventListener('pointerup',stop);
  group.addEventListener('pointercancel',stop);
}
function redrawEdges(){
  const {edges}=visibleParts();
  const slots=edgeSlots(edges);
  edges.forEach(edge=>{
    const group=edgeGroups.get(edge.uid);
    if(!group)return;
    const d=edgePath(edge,slots);
    group.querySelectorAll('path').forEach(path=>path.setAttribute('d',d));
  });
}
svg.addEventListener('pointerdown',event=>{
  if(event.target.closest('.node')||event.button!==0)return;
  const start={x:event.clientX,y:event.clientY},from={x:camera.x,y:camera.y};
  const rect=svg.getBoundingClientRect();
  svg.classList.add('panning');
  let moved=false;
  const move=next=>{
    moved=true;
    camera.x=from.x-(next.clientX-start.x)/rect.width*camera.w;
    camera.y=from.y-(next.clientY-start.y)/rect.height*camera.h;
    applyCamera();
  };
  const stop=()=>{
    svg.classList.remove('panning');
    window.removeEventListener('pointermove',move);
    window.removeEventListener('pointerup',stop);
    if(!moved){selected=null;showViewSummary();applySelection();if(tab==='load')buildToc();}
  };
  window.addEventListener('pointermove',move);
  window.addEventListener('pointerup',stop);
});
svg.addEventListener('wheel',event=>{
  event.preventDefault();
  const point=toSvgPoint(event);
  const ratio=Math.min(9000,Math.max(280,camera.w*(event.deltaY>0?1.12:1/1.12)))/camera.w;
  camera.h*=ratio;
  camera.x=point.x-(point.x-camera.x)*ratio;
  camera.y=point.y-(point.y-camera.y)*ratio;
  camera.w*=ratio;
  applyCamera();
},{passive:false});
window.addEventListener('resize',()=>{camera=null;paint();});

/* ---------- 아래 상세 ---------- */
function openDock(title,hint,html){
  document.getElementById('dock-title').textContent=title;
  document.getElementById('dock-hint').textContent=hint;
  detail.innerHTML=html;
  dock.dataset.open='true';
  document.getElementById('dock-toggle').textContent='닫기';
}
function evidenceHtml(items){
  return (items||[]).map(item=>'<div class="evidence"><code>'+esc(item.path)+':'+item.line+
    (item.end_line?'-'+item.end_line:'')+'</code><br>'+esc(item.description)+'</div>').join('');
}
function relationRows(edges){
  if(!edges.length)return '<p class="empty">없음</p>';
  return edges.map(edge=>'<div class="relation" data-edge="'+esc(edge.uid)+'">'+
    (edge.step?'<strong>'+edge.step+'.</strong> ':'')+'<strong>'+esc(edge.kind)+'</strong> · '+
    esc(edge.label)+(edge.endpoint?' <code>'+esc(edge.endpoint)+'</code>':'')+
    '<br><span class="empty">'+esc(nodeById.get(edge.source_uid)?.name)+' → '+
    esc(nodeById.get(edge.target_uid)?.name)+'</span></div>').join('');
}
function bindRelationRows(){
  const edges=new Map(view().edges.map(edge=>[edge.uid,edge]));
  detail.querySelectorAll('[data-edge]').forEach(row=>
    row.addEventListener('click',()=>selectEdge(edges.get(row.dataset.edge))));
}
function showViewSummary(){
  const current=view();
  if(tab==='load'&&loadResult){
    const rows=current.nodes.map(uid=>({uid,m:loadResult.metrics[uid]}))
      .sort((a,b)=>b.m.stress-a.m.stress).slice(0,8);
    const table='<table><tr><th>컴포넌트</th><th>rps</th><th>CPU</th><th>메모리</th>'+
      '<th>지연</th><th>동시</th></tr>'+
      rows.map(row=>'<tr><td>'+esc(nodeById.get(row.uid)?.name)+'</td><td>'+num(row.m.rps)+
        '</td><td>'+num(row.m.cpuUtil*100)+'%</td><td>'+num(row.m.memUtil*100)+'%</td><td>'+
        num(row.m.totalMs,1)+'ms</td><td>'+num(row.m.inFlight)+'</td></tr>').join('')+'</table>';
    const hot=rows.filter(row=>row.m.stress>=1).map(row=>nodeById.get(row.uid)?.name);
    openDock('부하 순위',hot.length?'포화: '+hot.join(', '):'포화된 컴포넌트 없음',
      '<h3>부하가 높은 순서</h3>'+table+
      '<h3>읽는 법</h3><p class="empty">CPU·메모리는 사용률이고 지연은 하류 대기까지 합친 값이다. '+
      '사용률이 1에 가까워지면 대기가 급격히 늘어 지연이 선형이 아니게 커진다. '+
      '요청당 CPU·메모리는 측정값이 아니라 조절 가능한 가정값이다.</p>');
    return;
  }
  detail.innerHTML='<p class="empty">'+esc(current.description)+'</p>';
  document.getElementById('dock-title').textContent=current.title;
  document.getElementById('dock-hint').textContent=
    '노드 '+current.nodes.length+' · 관계 '+current.edges.length+
    (current.depth?' · 깊이 '+current.depth:'');
}
function selectComponent(uid,keepToc){
  selected=uid;
  const item=nodeById.get(uid);
  if(!item)return;
  const current=view();
  const origin=item.origin||{};
  const provides=DATA.apis.filter(api=>api.provider_uid===uid);
  let head='<div class="dock-cols"><div><h3>역할</h3><p>'+esc(item.role)+'</p>'+
    '<span class="badge">'+esc(item.kind)+'</span>'+
    '<span class="badge">'+esc(DATA.layer_labels[item.layer]||item.layer)+'</span>'+
    '<span class="badge">'+esc(origin.type||'')+' · '+esc(origin.label||'')+
    (origin.engine?' ('+esc(origin.engine)+')':'')+'</span>'+
    (item.capacity?'<span class="badge">'+item.capacity.replicas+'대 · '+
      item.capacity.cpu_millicores+'m · '+item.capacity.memory_mib+'MiB ('+
      esc(item.capacity.source)+')</span>':'')+
    (provides.length?'<h3>제공하는 API</h3>'+provides.map(api=>
      '<div class="relation"><code>'+esc(api.address)+'</code> '+esc(api.name)+'</div>').join(''):'')+
    '</div>';
  if(tab==='load'&&loadResult){
    const m=loadResult.metrics[uid];
    head+='<div><h3>부하</h3><table>'+
      '<tr><th>요청량</th><td>'+num(m.rps)+' rps</td></tr>'+
      '<tr><th>CPU 사용률</th><td>'+num(m.cpuUtil*100)+'% ('+num(m.cap.replicas)+'대 × '+
        num(m.cap.cpu_millicores)+'m)</td></tr>'+
      '<tr><th>메모리 사용률</th><td>'+num(m.memUtil*100)+'% ('+num(m.memMib)+' / '+
        num(m.cap.replicas*m.cap.memory_mib)+' MiB)</td></tr>'+
      '<tr><th>자체 처리</th><td>'+num(m.serviceMs,2)+' ms</td></tr>'+
      '<tr><th>대기</th><td>'+num(m.waitMs,2)+' ms</td></tr>'+
      '<tr><th>하류 대기</th><td>'+num(m.downstreamMs,2)+' ms</td></tr>'+
      '<tr><th>응답 지연</th><td>'+num(m.totalMs,2)+' ms</td></tr>'+
      '<tr><th>암복호화</th><td>'+num(m.cryptoMs,2)+' ms/요청</td></tr>'+
      '<tr><th>동시 처리</th><td>'+num(m.inFlight)+' 건</td></tr></table></div>';
  }
  head+='<div><h3>나가는 관계</h3>'+relationRows(current.edges.filter(e=>e.source_uid===uid))+
    '<h3>들어오는 관계</h3>'+relationRows(current.edges.filter(e=>e.target_uid===uid))+'</div>'+
    '<div><h3>근거</h3>'+evidenceHtml(item.evidence)+'</div></div>';
  openDock(item.name,DATA.layer_labels[item.layer]+' · '+(item.project_name||''),head);
  bindRelationRows();
  applySelection();
  if(tab==='load'&&!keepToc)buildToc();
}
function selectEdge(edge){
  if(!edge)return;
  selected=edge.uid;
  const source=nodeById.get(edge.source_uid),target=nodeById.get(edge.target_uid);
  const parts=(edge.relationship_uids||[]).map(uid=>relById.get(uid)).filter(Boolean);
  const api=edge.api_uid?apiById.get(edge.api_uid):null;
  const body=parts.map(relationship=>{
    const details=Object.entries(relationship.details||{})
      .map(entry=>'<span class="badge">'+esc(entry[0])+': '+esc(entry[1])+'</span>').join('');
    return '<h3>'+esc(relationship.label)+' ('+esc(relationship.kind)+')</h3>'+details+
      evidenceHtml(relationship.evidence);
  }).join('');
  const load=edge.load||{};
  openDock(edge.label,esc(source?.name)+' → '+esc(target?.name),
    '<div class="dock-cols"><div>'+
    '<span class="badge">'+esc(edge.kind)+'</span>'+
    (edge.endpoint?'<span class="badge"><code>'+esc(edge.endpoint)+'</code></span>':'')+
    (edge.cross_project?'<span class="badge hot">다른 프로젝트 호출</span>':'')+
    (edge.step?'<span class="badge">'+edge.step+'번째 단계</span>':'')+
    (edge.derived?'<span class="badge">module 을 접은 관계</span>':'')+
    (api?'<h3>API</h3><p><code>'+esc(api.address)+'</code> · '+esc(api.name)+' · 제공 '+
      esc(nodeById.get(api.provider_uid)?.name||api.provider)+'</p>':'')+
    '<h3>부하</h3><table>'+
    '<tr><th>fan-out</th><td>×'+num(load.fan_out??1,2)+'</td></tr>'+
    '<tr><th>호출 방식</th><td>'+(load.sync?'동기':'비동기')+'</td></tr>'+
    '<tr><th>암복호화</th><td>'+(DATA.defaults.crypto_labels[load.crypto]||'없음')+'</td></tr>'+
    (tab==='load'?'<tr><th>통과 요청량</th><td>'+num(loadResult.edgeRps[edge.uid])+' rps</td></tr>':'')+
    '</table>'+(load.fan_out_note?'<p class="empty">'+esc(load.fan_out_note)+'</p>':'')+
    '</div><div>'+body+'</div></div>');
  applySelection();
}
function selectApi(uid){
  const api=apiById.get(uid);
  if(!api)return;
  const callers=view().edges.filter(edge=>edge.api_uid===uid);
  selected=api.provider_uid;
  openDock(api.address,api.name+' · '+(api.entrypoint?'진입점':'내부 호출'),
    '<div class="dock-cols"><div><h3>제공</h3><p>'+
    esc(nodeById.get(api.provider_uid)?.name||api.provider)+'</p>'+
    '<span class="badge">'+esc(api.protocol)+'</span>'+
    (api.entrypoint?'<span class="badge">진입점</span>':'')+
    '</div><div><h3>부르는 곳</h3>'+relationRows(callers)+
    '</div><div><h3>근거</h3>'+evidenceHtml(api.evidence)+'</div></div>');
  bindRelationRows();
  applySelection();
}
function applySelection(){
  const related=new Set();
  if(selected){
    if(nodeById.has(selected)){
      related.add(selected);
      view().edges.forEach(edge=>{
        if(edge.source_uid===selected||edge.target_uid===selected){
          related.add(edge.uid);related.add(edge.source_uid);related.add(edge.target_uid);
        }
      });
    }else{
      const edge=view().edges.find(item=>item.uid===selected);
      if(edge){related.add(edge.uid);related.add(edge.source_uid);related.add(edge.target_uid);}
    }
  }
  svg.querySelectorAll('.node,.edge').forEach(item=>{
    item.classList.toggle('selected',selected===item.dataset.id);
    item.classList.toggle('dim',Boolean(selected)&&!related.has(item.dataset.id));
  });
}

/* ---------- 도구 ---------- */
const filters=document.getElementById('filters');
Object.keys(RELATION_COLORS).forEach(kind=>{
  const chip=document.createElement('button');
  chip.type='button';
  chip.className='chip';
  chip.setAttribute('aria-pressed','true');
  chip.style.color=RELATION_COLORS[kind];
  chip.innerHTML='<i style="background:'+RELATION_COLORS[kind]+'"></i>'+kind;
  chip.addEventListener('click',()=>{
    const on=chip.getAttribute('aria-pressed')!=='true';
    chip.setAttribute('aria-pressed',String(on));
    on?activeKinds.add(kind):activeKinds.delete(kind);
    paint();
  });
  filters.append(chip);
});
const depth=document.getElementById('depth');
DATA.layers.forEach((_,index)=>{
  const option=document.createElement('option');
  option.value=String(index+1);
  option.textContent=(index+1)+'단계';
  depth.append(option);
});
depth.value=String(DATA.layers.length);
depth.addEventListener('change',()=>{maxDepth=Number(depth.value);paint();});
document.getElementById('search').addEventListener('input',()=>{buildToc();paint();});
document.getElementById('reset').addEventListener('click',()=>{delete layout[viewId];camera=null;paint();});
document.getElementById('copy').addEventListener('click',async()=>{
  const button=document.getElementById('copy');
  const text=JSON.stringify(exportLayout(),null,2);
  try{await navigator.clipboard.writeText(text);button.textContent='복사됨';}
  catch(error){window.prompt('analysis.json 의 layout 에 넣으세요',text);button.textContent='배치 복사';}
  setTimeout(()=>{button.textContent='배치 복사';},1600);
});
document.getElementById('dock-bar').addEventListener('click',event=>{
  if(event.target.tagName==='A')return;
  const open=dock.dataset.open!=='true';
  dock.dataset.open=String(open);
  document.getElementById('dock-toggle').textContent=open?'닫기':'열기';
});
function exportLayout(){
  // uid 는 "projectId::componentId" 라 analysis.json 이 쓰는 componentId 로 되돌린다.
  const result={};
  Object.keys(layout).forEach(id=>{
    const positions={};
    Object.keys(layout[id]).forEach(uid=>{positions[uid.split('::').pop()]=layout[id][uid];});
    result[id.replace(/:[^:]+::/,':')]=positions;
  });
  return result;
}
function defaultView(){
  if(tab==='load')return 'load';
  if(mode==='service')return 'service';
  if(mode==='api')return 'api';
  const business=DATA.businesses[0];
  if(!business)return 'service';
  return business.flows.length?business.flows[0].view_id:business.view_id;
}
function selectView(id){
  if(!DATA.views[id])return;
  viewId=id;
  selected=null;
  camera=null;
  const current=view();
  document.getElementById('view-title').textContent=current.title;
  document.getElementById('view-desc').textContent=current.description;
  document.getElementById('depth-box').style.display=current.mode==='service'?'':'none';
  document.getElementById('filters').style.display=tab==='load'?'none':'';
  buildToc();
  paint();
  showViewSummary();
}
function setMode(next){
  mode=next;
  buildModes();
  selectView(defaultView());
}
function setTab(next){
  tab=next;
  document.getElementById('tab-analysis').setAttribute('aria-pressed',String(next==='analysis'));
  document.getElementById('tab-load').setAttribute('aria-pressed',String(next==='load'));
  // 캔버스 크기를 재기 전에 dock 을 열어야 카메라가 실제 남은 공간에 맞춰진다.
  dock.dataset.open=String(next==='load');
  document.getElementById('dock-toggle').textContent=next==='load'?'닫기':'열기';
  setMode(MODES[next][0][0]);
}
document.getElementById('tab-analysis').addEventListener('click',()=>setTab('analysis'));
document.getElementById('tab-load').addEventListener('click',()=>setTab('load'));
mode=DATA.businesses.length?'business':'service';
setTab('analysis');
</script>
</body>
</html>
"""


def drawio_style(component: dict[str, Any]) -> str:
  kind = component["kind"]
  color = KIND_COLORS.get(kind, "#475569")
  shape = "rounded=1;arcSize=14;"
  if kind == "datastore":
    shape = "shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=15;"
  elif kind == "message-broker":
    shape = "shape=hexagon;perimeter=hexagonPerimeter2;fixedSize=1;"
  elif kind == "external-system":
    shape = "rounded=1;arcSize=14;dashed=1;"
  elif kind == "module":
    shape = "rounded=0;"
  if component.get("placeholder"):
    shape += "dashed=1;"
  return f"{shape}whiteSpace=wrap;html=1;fillColor={color};strokeColor=#ffffff;fontColor=#ffffff;fontStyle=1;"


def evidence_text(items: list[dict[str, Any]]) -> str:
  return " | ".join(f"{item['path']}:{item['line']}" for item in items)


def render_drawio(bundle: list[dict[str, Any]]) -> str:
  graph = flatten_bundle(bundle)
  component_by_uid = {item["uid"]: item for item in graph["components"]}
  relationship_by_uid = {item["uid"]: item for item in graph["relationships"]}
  root = ET.Element("mxfile", {
    "host": "app.diagrams.net",
    "agent": "akbun-analysiscode",
    "version": "24.7.17",
    "compressed": "false",
  })
  cell_ids: dict[tuple[str, str], str] = {}
  counter = 2

  def add_page(view: dict[str, Any], name: str) -> None:
    nonlocal counter
    diagram = ET.SubElement(root, "diagram", {"id": view["id"], "name": name})
    model = ET.SubElement(diagram, "mxGraphModel", {
      "dx": "1200", "dy": "800", "grid": "1", "gridSize": "10", "guides": "1",
      "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1",
      "pageScale": "1", "pageWidth": "1169", "pageHeight": "827", "math": "0", "shadow": "0",
    })
    cells = ET.SubElement(model, "root")
    ET.SubElement(cells, "mxCell", {"id": "0"})
    ET.SubElement(cells, "mxCell", {"id": "1", "parent": "0"})
    saved = graph["layout"].get(view["id"], {})
    for uid in view["nodes"]:
      component = component_by_uid.get(uid)
      if component is None:
        continue
      counter += 1
      cell_id = f"n{counter}"
      cell_ids[(view["id"], uid)] = cell_id
      origin = component.get("origin", {})
      subtitle = " · ".join(
        part for part in [LAYER_LABELS.get(component["layer"], ""), origin.get("engine"), origin.get("label")] if part
      )
      value = (
        f"<b>{html.escape(component['name'])}</b>"
        f"<br><font style=\"font-size:10px\">{html.escape(subtitle)}</font>"
      )
      cell = ET.SubElement(cells, "mxCell", {
        "id": cell_id,
        "value": value,
        "style": drawio_style(component),
        "vertex": "1",
        "parent": "1",
        "akbunKind": component["kind"],
        "akbunLayer": component["layer"],
        "akbunOrigin": json.dumps(origin, ensure_ascii=False),
        "akbunRole": component["role"],
        "akbunEvidence": evidence_text(component["evidence"]),
      })
      position = saved.get(uid) or view["positions"].get(uid, {"x": 0, "y": 0})
      ET.SubElement(cell, "mxGeometry", {
        "x": str(int(position["x"])),
        "y": str(int(position["y"])),
        "width": str(NODE_WIDTH),
        "height": str(NODE_HEIGHT),
        "as": "geometry",
      })
    for edge in view["edges"]:
      source = cell_ids.get((view["id"], edge["source_uid"]))
      target = cell_ids.get((view["id"], edge["target_uid"]))
      if not source or not target:
        continue
      counter += 1
      color = RELATION_COLORS[edge["kind"]]
      parts = [relationship_by_uid[uid] for uid in edge["relationship_uids"] if uid in relationship_by_uid]
      label = f"{edge['step']}. {edge['label']}" if edge.get("step") else edge["label"]
      cell = ET.SubElement(cells, "mxCell", {
        "id": f"e{counter}",
        "value": label,
        "style": (
          "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;"
          f"strokeWidth=2;strokeColor={color};endArrow=block;endFill=1;"
          + ("dashed=1;" if edge.get("derived") else "")
        ),
        "edge": "1",
        "parent": "1",
        "source": source,
        "target": target,
        "akbunKind": edge["kind"],
        "akbunEvidence": " | ".join(evidence_text(item["evidence"]) for item in parts),
        "akbunDetails": json.dumps([item.get("details", {}) for item in parts], ensure_ascii=False),
      })
      ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})

  add_page(graph["views"]["service"], "서비스 관계도")
  for business in graph["businesses"]:
    for flow in business["flows"]:
      add_page(graph["views"][flow["view_id"]], f"{business['name']} / {flow['name']}")
  ET.indent(root, space="  ")
  return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"
