#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from collections import defaultdict, deque
from typing import Any
from xml.etree import ElementTree as ET

KIND_COLORS = {
  "service": "#0f766e",
  "component": "#2563eb",
  "datastore": "#7c3aed",
  "message-broker": "#c2410c",
  "external-system": "#475569",
}
RELATION_COLORS = {
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


def component_uid(project_id: str, component_id: str) -> str:
  return f"{project_id}::{component_id}"


def flatten_bundle(bundle: list[dict[str, Any]]) -> dict[str, Any]:
  projects: list[dict[str, Any]] = []
  components: list[dict[str, Any]] = []
  relationships: list[dict[str, Any]] = []
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
      relationships.append(item)
      if item["target_uid"] not in component_uids:
        placeholder = {
          "id": relationship["target"],
          "uid": item["target_uid"],
          "project_id": target_project,
          "project_name": target_project,
          "name": f"{target_project} / {relationship['target']}",
          "kind": "external-system",
          "role": "선택되지 않은 외부 프로젝트의 컴포넌트",
          "importance": "core",
          "owned_paths": [],
          "evidence": relationship["evidence"],
          "placeholder": True,
        }
        component_uids.add(item["target_uid"])
        components.append(placeholder)

  positions, width, height = layout_graph(components, relationships)
  for component in components:
    component["position"] = positions[component["uid"]]
  return {
    "projects": projects,
    "components": components,
    "relationships": relationships,
    "canvas": {"width": width, "height": height},
  }


def strongly_connected_components(nodes: list[str], edges: list[tuple[str, str]]) -> list[list[str]]:
  adjacency: dict[str, list[str]] = defaultdict(list)
  for source, target in edges:
    adjacency[source].append(target)
  index = 0
  indexes: dict[str, int] = {}
  lowlinks: dict[str, int] = {}
  stack: list[str] = []
  on_stack: set[str] = set()
  groups: list[list[str]] = []

  def visit(node: str) -> None:
    nonlocal index
    indexes[node] = index
    lowlinks[node] = index
    index += 1
    stack.append(node)
    on_stack.add(node)
    for target in adjacency[node]:
      if target not in indexes:
        visit(target)
        lowlinks[node] = min(lowlinks[node], lowlinks[target])
      elif target in on_stack:
        lowlinks[node] = min(lowlinks[node], indexes[target])
    if lowlinks[node] != indexes[node]:
      return
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


def layout_graph(
  components: list[dict[str, Any]],
  relationships: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, int]], int, int]:
  nodes = [component["uid"] for component in components]
  edges = [(item["source_uid"], item["target_uid"]) for item in relationships]
  groups = strongly_connected_components(nodes, edges)
  group_by_node = {node: index for index, group in enumerate(groups) for node in group}
  outgoing: dict[int, set[int]] = defaultdict(set)
  indegree = {index: 0 for index in range(len(groups))}
  for source, target in edges:
    source_group = group_by_node[source]
    target_group = group_by_node[target]
    if source_group == target_group or target_group in outgoing[source_group]:
      continue
    outgoing[source_group].add(target_group)
    indegree[target_group] += 1
  queue = deque(index for index, degree in indegree.items() if degree == 0)
  ranks = {index: 0 for index in range(len(groups))}
  while queue:
    source = queue.popleft()
    for target in outgoing[source]:
      ranks[target] = max(ranks[target], ranks[source] + 1)
      indegree[target] -= 1
      if indegree[target] == 0:
        queue.append(target)
  component_by_uid = {component["uid"]: component for component in components}
  columns: dict[int, list[str]] = defaultdict(list)
  for node in nodes:
    columns[ranks[group_by_node[node]]].append(node)
  positions: dict[str, dict[str, int]] = {}
  max_rows = 1
  for rank, column_nodes in columns.items():
    ordered = sorted(
      column_nodes,
      key=lambda uid: (
        component_by_uid[uid].get("importance") != "core",
        component_by_uid[uid].get("kind"),
        component_by_uid[uid].get("name"),
      ),
    )
    max_rows = max(max_rows, len(ordered))
    for row, uid in enumerate(ordered):
      positions[uid] = {"x": 80 + rank * 290, "y": 80 + row * 126}
  width = max(820, 370 + max(columns, default=0) * 290)
  height = max(420, 190 + max_rows * 126)
  return positions, width, height


def json_for_html(data: dict[str, Any]) -> str:
  return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def render_html(bundle: list[dict[str, Any]]) -> str:
  graph = flatten_bundle(bundle)
  title = bundle[0]["project"]["name"]
  return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} 컴포넌트 관계도</title>
<style>
:root {{ color-scheme: light dark; --bg:#f8fafc; --panel:#fff; --ink:#0f172a; --muted:#64748b; --border:#cbd5e1; --selected:#fef3c7; }}
@media (prefers-color-scheme:dark) {{ :root {{ --bg:#07111f; --panel:#0f172a; --ink:#e2e8f0; --muted:#94a3b8; --border:#334155; --selected:#422006; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; min-height:100vh; display:flex; flex-direction:column; font:14px/1.5 ui-sans-serif,system-ui,-apple-system,"Noto Sans KR",sans-serif; background:var(--bg); color:var(--ink); }}
header {{ padding:20px 24px 12px; border-bottom:1px solid var(--border); background:var(--panel); }}
h1 {{ margin:0 0 4px; font-size:22px; }} .summary {{ color:var(--muted); max-width:1000px; }}
.toolbar {{ display:flex; flex-wrap:wrap; gap:10px 18px; align-items:center; padding:12px 24px; border-bottom:1px solid var(--border); background:var(--panel); }}
input[type=search] {{ width:min(360px,100%); padding:9px 12px; border:1px solid var(--border); border-radius:8px; background:var(--bg); color:var(--ink); }}
.filters {{ display:flex; flex-wrap:wrap; gap:8px 12px; }} label {{ white-space:nowrap; }}
main {{ display:grid; grid-template-columns:minmax(0,1fr) 340px; flex:1; min-height:0; }}
.canvas-wrap {{ overflow:auto; min-height:0; padding:18px; }} svg {{ display:block; width:max(100%,820px); height:auto; border:1px solid var(--border); border-radius:12px; background:var(--panel); }}
.node {{ cursor:pointer; }} .node rect {{ stroke-width:2; }} .node text {{ pointer-events:none; fill:#fff; }} .node .kind {{ font-size:10px; opacity:.78; letter-spacing:.08em; }}
.node.dim {{ opacity:.16; }} .node.selected rect {{ stroke:#f59e0b; stroke-width:4; }}
.edge {{ cursor:pointer; }} .edge path {{ fill:none; stroke-width:2.2; }} .edge text {{ font-size:11px; fill:var(--ink); paint-order:stroke; stroke:var(--panel); stroke-width:5px; stroke-linejoin:round; }}
.edge.dim {{ opacity:.09; }} .edge.selected path {{ stroke-width:5; }}
aside {{ border-left:1px solid var(--border); background:var(--panel); padding:20px; overflow:auto; }}
aside h2 {{ margin:0 0 8px; font-size:18px; }} aside h3 {{ margin:20px 0 6px; font-size:13px; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); }}
.badge {{ display:inline-block; padding:2px 7px; margin:0 4px 4px 0; border:1px solid var(--border); border-radius:99px; font-size:12px; }}
.relation {{ padding:8px 0; border-bottom:1px solid var(--border); cursor:pointer; }} .evidence {{ padding:8px 0; }} code {{ overflow-wrap:anywhere; color:#0ea5e9; }}
.empty {{ color:var(--muted); }}
@media (max-width:900px) {{ body {{ display:block; }} main {{ grid-template-columns:1fr; }} aside {{ border-left:0; border-top:1px solid var(--border); }} }}
</style>
</head>
<body>
<header><h1>{html.escape(title)} 컴포넌트 관계도</h1><div class="summary">{html.escape(bundle[0]['summary'])}</div></header>
<div class="toolbar">
  <input id="search" type="search" placeholder="컴포넌트 검색">
  <label><input id="supporting" type="checkbox"> supporting 표시</label>
  <div id="filters" class="filters"></div>
</div>
<main>
  <div class="canvas-wrap"><svg id="graph" role="img" aria-label="서비스와 컴포넌트 관계도"></svg></div>
  <aside id="detail"><p class="empty">컴포넌트나 관계를 선택하세요.</p></aside>
</main>
<script id="analysis-data" type="application/json">{json_for_html(graph)}</script>
<script>
const data=JSON.parse(document.getElementById('analysis-data').textContent);
const svg=document.getElementById('graph'), detail=document.getElementById('detail');
const NS='http://www.w3.org/2000/svg';
const relationColors={json.dumps(RELATION_COLORS, ensure_ascii=False)};
const componentColors={json.dumps(KIND_COLORS, ensure_ascii=False)};
const activeKinds=new Set(Object.keys(relationColors));
let selected=null;
const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,ch=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[ch]));
const evidenceHtml=items=>items.map(item=>`<div class="evidence"><code>${{escapeHtml(item.path)}}:${{item.line}}${{item.end_line?'-'+item.end_line:''}}</code><br>${{escapeHtml(item.description)}}</div>`).join('');
const nodeById=new Map(data.components.map(item=>[item.uid,item]));
const relById=new Map(data.relationships.map(item=>[item.uid,item]));
const filters=document.getElementById('filters');
Object.keys(relationColors).forEach(kind=>{{
  const label=document.createElement('label');
  label.innerHTML=`<input type="checkbox" checked data-kind="${{kind}}"> ${{kind}}`;
  label.querySelector('input').addEventListener('change',event=>{{event.target.checked?activeKinds.add(kind):activeKinds.delete(kind);render();}});
  filters.append(label);
}});
document.getElementById('search').addEventListener('input',render);
document.getElementById('supporting').addEventListener('change',render);
function el(name,attrs={{}}){{const node=document.createElementNS(NS,name);Object.entries(attrs).forEach(([key,value])=>node.setAttribute(key,value));return node;}}
function visibleNodes(){{
  const query=document.getElementById('search').value.trim().toLowerCase();
  const showSupporting=document.getElementById('supporting').checked;
  const matched=new Set(data.components.filter(item=>!query||`${{item.name}} ${{item.role}} ${{item.project_name}}`.toLowerCase().includes(query)).map(item=>item.uid));
  if(query) data.relationships.forEach(rel=>{{if(matched.has(rel.source_uid)||matched.has(rel.target_uid)){{matched.add(rel.source_uid);matched.add(rel.target_uid);}}}});
  return new Set(data.components.filter(item=>(showSupporting||item.importance==='core'||query&&matched.has(item.uid))&&(!query||matched.has(item.uid))).map(item=>item.uid));
}}
function render(){{
  const visible=visibleNodes(); svg.replaceChildren();
  svg.setAttribute('viewBox',`0 0 ${{data.canvas.width}} ${{data.canvas.height}}`);
  const defs=el('defs');
  Object.entries(relationColors).forEach(([kind,color])=>{{const marker=el('marker',{{id:`arrow-${{kind}}`,viewBox:'0 0 10 10',refX:'9',refY:'5',markerWidth:'7',markerHeight:'7',orient:'auto-start-reverse'}});marker.append(el('path',{{d:'M 0 0 L 10 5 L 0 10 z',fill:color}}));defs.append(marker);}});
  svg.append(defs);
  data.relationships.forEach(rel=>{{
    if(!activeKinds.has(rel.kind)||!visible.has(rel.source_uid)||!visible.has(rel.target_uid)) return;
    const source=nodeById.get(rel.source_uid), target=nodeById.get(rel.target_uid); if(!source||!target)return;
    const sx=source.position.x+210, sy=source.position.y+38, tx=target.position.x, ty=target.position.y+38;
    const backwards=tx<=sx, startX=backwards?source.position.x:sx, endX=backwards?target.position.x+210:tx;
    const bend=Math.max(60,Math.abs(endX-startX)*.45), d=`M ${{startX}} ${{sy}} C ${{startX+(backwards?-bend:bend)}} ${{sy}}, ${{endX+(backwards?bend:-bend)}} ${{ty}}, ${{endX}} ${{ty}}`;
    const group=el('g',{{class:'edge','data-id':rel.uid}}), path=el('path',{{d,stroke:relationColors[rel.kind],'marker-end':`url(#arrow-${{rel.kind}})`}});
    const text=el('text',{{x:(startX+endX)/2,y:(sy+ty)/2-7,'text-anchor':'middle'}});text.textContent=rel.label;
    group.append(path,text);group.addEventListener('click',event=>{{event.stopPropagation();selectRelationship(rel.uid);}});svg.append(group);
  }});
  data.components.forEach(item=>{{if(!visible.has(item.uid))return;const group=el('g',{{class:'node','data-id':item.uid,transform:`translate(${{item.position.x}} ${{item.position.y}})`}});const rect=el('rect',{{width:'210',height:'76',rx:item.kind==='datastore'?'28':'10',fill:componentColors[item.kind]||'#475569',stroke:item.placeholder?'#f59e0b':'#ffffff','stroke-dasharray':item.placeholder?'7 5':'none'}});const name=el('text',{{x:'14',y:'31','font-size':'14','font-weight':'700'}});name.textContent=item.name.length>25?item.name.slice(0,24)+'…':item.name;const kind=el('text',{{x:'14',y:'53',class:'kind'}});kind.textContent=`${{item.project_name}} · ${{item.kind}}`;group.append(rect,name,kind);group.addEventListener('click',event=>{{event.stopPropagation();selectComponent(item.uid);}});svg.append(group);}});
  applySelection();
}}
function applySelection(){{
  svg.querySelectorAll('.node,.edge').forEach(item=>item.classList.remove('selected','dim'));
  if(!selected)return;
  const related=new Set();
  if(nodeById.has(selected)){{related.add(selected);data.relationships.forEach(rel=>{{if(rel.source_uid===selected||rel.target_uid===selected){{related.add(rel.uid);related.add(rel.source_uid);related.add(rel.target_uid);}}}});}}
  else{{const rel=relById.get(selected);if(rel){{related.add(rel.uid);related.add(rel.source_uid);related.add(rel.target_uid);}}}}
  svg.querySelectorAll('.node,.edge').forEach(item=>{{item.classList.toggle('selected',item.dataset.id===selected);item.classList.toggle('dim',!related.has(item.dataset.id));}});
}}
function selectComponent(uid){{selected=uid;const item=nodeById.get(uid);const incoming=data.relationships.filter(rel=>rel.target_uid===uid), outgoing=data.relationships.filter(rel=>rel.source_uid===uid);detail.innerHTML=`<h2>${{escapeHtml(item.name)}}</h2><span class="badge">${{escapeHtml(item.kind)}}</span><span class="badge">${{escapeHtml(item.importance)}}</span><span class="badge">${{escapeHtml(item.project_name)}}</span><p>${{escapeHtml(item.role)}}</p><h3>나가는 관계</h3>${{relationshipList(outgoing)}}<h3>들어오는 관계</h3>${{relationshipList(incoming)}}<h3>근거</h3>${{evidenceHtml(item.evidence)}}`;bindRelationLinks();applySelection();}}
function relationshipList(items){{return items.length?items.map(rel=>`<div class="relation" data-rel="${{rel.uid}}"><strong>${{escapeHtml(rel.kind)}}</strong> · ${{escapeHtml(rel.label)}}<br><span class="empty">${{escapeHtml(nodeById.get(rel.source_uid)?.name)}} → ${{escapeHtml(nodeById.get(rel.target_uid)?.name)}}</span></div>`).join(''):'<p class="empty">없음</p>';}}
function bindRelationLinks(){{detail.querySelectorAll('[data-rel]').forEach(item=>item.addEventListener('click',()=>selectRelationship(item.dataset.rel)));}}
function selectRelationship(uid){{selected=uid;const rel=relById.get(uid),source=nodeById.get(rel.source_uid),target=nodeById.get(rel.target_uid);const details=Object.entries(rel.details||{{}}).map(([key,value])=>`<span class="badge">${{escapeHtml(key)}}: ${{escapeHtml(value)}}</span>`).join('');detail.innerHTML=`<h2>${{escapeHtml(rel.label)}}</h2><span class="badge">${{escapeHtml(rel.kind)}}</span><p><strong>${{escapeHtml(source?.name)}}</strong> → <strong>${{escapeHtml(target?.name)}}</strong></p><div>${{details}}</div><h3>근거</h3>${{evidenceHtml(rel.evidence)}}`;applySelection();}}
svg.addEventListener('click',()=>{{selected=null;detail.innerHTML='<p class="empty">컴포넌트나 관계를 선택하세요.</p>';applySelection();}});
render();
</script>
</body>
</html>
"""


def drawio_style(kind: str, placeholder: bool = False) -> str:
  color = KIND_COLORS.get(kind, "#475569")
  shape = "rounded=1;arcSize=14;"
  if kind == "datastore":
    shape = "shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=15;"
  elif kind == "message-broker":
    shape = "shape=hexagon;perimeter=hexagonPerimeter2;fixedSize=1;"
  elif kind == "external-system":
    shape = "rounded=1;arcSize=14;dashed=1;"
  if placeholder:
    shape += "dashed=1;"
  return f"{shape}whiteSpace=wrap;html=1;fillColor={color};strokeColor=#ffffff;fontColor=#ffffff;fontStyle=1;"


def evidence_text(items: list[dict[str, Any]]) -> str:
  return " | ".join(f"{item['path']}:{item['line']}" for item in items)


def render_drawio(bundle: list[dict[str, Any]]) -> str:
  graph = flatten_bundle(bundle)
  root = ET.Element("mxfile", {
    "host": "app.diagrams.net",
    "agent": "akbun-analysiscode",
    "version": "24.7.17",
    "compressed": "false",
  })
  diagram = ET.SubElement(root, "diagram", {"id": "akbun-analysis", "name": "Component relationships"})
  model = ET.SubElement(diagram, "mxGraphModel", {
    "dx": "1200", "dy": "800", "grid": "1", "gridSize": "10", "guides": "1",
    "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1",
    "pageScale": "1", "pageWidth": "1169", "pageHeight": "827", "math": "0", "shadow": "0",
  })
  cells = ET.SubElement(model, "root")
  ET.SubElement(cells, "mxCell", {"id": "0"})
  ET.SubElement(cells, "mxCell", {"id": "1", "parent": "0"})
  cell_ids: dict[str, str] = {}
  for index, component in enumerate(graph["components"], start=2):
    cell_id = f"n{index}"
    cell_ids[component["uid"]] = cell_id
    value = f"<b>{html.escape(component['name'])}</b><br><font style=\"font-size:10px\">{html.escape(component['project_name'])} · {html.escape(component['kind'])}</font>"
    cell = ET.SubElement(cells, "mxCell", {
      "id": cell_id,
      "value": value,
      "style": drawio_style(component["kind"], component.get("placeholder", False)),
      "vertex": "1",
      "parent": "1",
      "akbunKind": component["kind"],
      "akbunRole": component["role"],
      "akbunEvidence": evidence_text(component["evidence"]),
    })
    ET.SubElement(cell, "mxGeometry", {
      "x": str(component["position"]["x"]),
      "y": str(component["position"]["y"]),
      "width": "210",
      "height": "76",
      "as": "geometry",
    })
  for index, relationship in enumerate(graph["relationships"], start=2):
    if relationship["source_uid"] not in cell_ids or relationship["target_uid"] not in cell_ids:
      continue
    color = RELATION_COLORS[relationship["kind"]]
    cell = ET.SubElement(cells, "mxCell", {
      "id": f"e{index}",
      "value": relationship["label"],
      "style": f"edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor={color};endArrow=block;endFill=1;",
      "edge": "1",
      "parent": "1",
      "source": cell_ids[relationship["source_uid"]],
      "target": cell_ids[relationship["target_uid"]],
      "akbunKind": relationship["kind"],
      "akbunEvidence": evidence_text(relationship["evidence"]),
      "akbunDetails": json.dumps(relationship.get("details", {}), ensure_ascii=False),
    })
    ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
  ET.indent(root, space="  ")
  return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"
