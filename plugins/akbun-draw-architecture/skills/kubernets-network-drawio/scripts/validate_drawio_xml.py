#!/usr/bin/env python3
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


HTML_PATTERN = re.compile(r"<[^>]+>")
STYLE_ITEM_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*(?:=[^;]+)?$")


def fail(message):
  print(f"FAIL: {message}", file=sys.stderr)
  raise SystemExit(1)


def child_elements(parent, name):
  return [child for child in list(parent) if child.tag == name]


def cell_id(cell):
  return cell.attrib.get("id", "")


def parent_id(cell):
  return cell.attrib.get("parent", "")


def visible_label(cell):
  return cell.attrib.get("value", "")


def style(cell):
  return cell.attrib.get("style", "")


def style_contains(cell, fragment):
  return fragment.lower() in style(cell).lower()


def is_vertex(cell):
  return cell.attrib.get("vertex") == "1"


def is_edge(cell):
  return cell.attrib.get("edge") == "1"


def is_cluster(cell):
  return is_vertex(cell) and cell_id(cell).startswith("grp-cluster")


def is_namespace(cell):
  return is_vertex(cell) and cell_id(cell).startswith("grp-namespace")


def is_lb(cell):
  return is_vertex(cell) and cell_id(cell).startswith("net-lb")


def is_ingress_controller(cell):
  return is_vertex(cell) and cell_id(cell).startswith("k8s-ingress-controller")


def is_service(cell):
  return (
    is_vertex(cell)
    and cell_id(cell).startswith("k8s-service")
    and style_contains(cell, "pricon=svc")
  )


def is_pod(cell):
  return (
    is_vertex(cell)
    and cell_id(cell).startswith("k8s-pod")
    and style_contains(cell, "pricon=pod")
  )


def is_workload(cell):
  return (
    is_vertex(cell)
    and cell_id(cell).startswith("k8s-workload")
    and is_kubernetes_icon(cell)
  )


def is_route_target(cell):
  return is_pod(cell) or is_workload(cell)


def is_kubernetes_icon(cell):
  return is_vertex(cell) and style_contains(cell, "shape=mxgraph.kubernetes.icon2")


def is_external_system(cell):
  return is_vertex(cell) and cell_id(cell).startswith("ext-")


def is_main_flow(cell):
  return is_edge(cell) and cell_id(cell).startswith("flow-main-")


def geometry(cell):
  geometries = child_elements(cell, "mxGeometry")
  if not geometries:
    return None

  item = geometries[0]
  try:
    x = float(item.attrib.get("x", "0"))
    y = float(item.attrib.get("y", "0"))
    width = float(item.attrib.get("width", "0"))
    height = float(item.attrib.get("height", "0"))
  except ValueError:
    return None

  return x, y, width, height


def center(cell, cells_by_id):
  x = 0.0
  y = 0.0
  current = cell

  while current is not None and cell_id(current) not in {"0", "1"}:
    item_geometry = geometry(current)
    if item_geometry is None:
      fail(f"cell {cell_id(current)} needs mxGeometry")
    item_x, item_y, width, height = item_geometry
    x += item_x
    y += item_y
    parent = cells_by_id.get(parent_id(current))
    if parent is None or cell_id(parent) == "1":
      break
    current = parent

  item_geometry = geometry(cell)
  if item_geometry is None:
    fail(f"cell {cell_id(cell)} needs mxGeometry")
  _, _, width, height = item_geometry
  return x + width / 2, y + height / 2


def validate_structure(root):
  if root.tag == "mxfile":
    diagrams = child_elements(root, "diagram")
    if not diagrams:
      fail("mxfile must contain at least one diagram")
    ids = set()
    models = []
    for diagram in diagrams:
      diagram_id = diagram.attrib.get("id", "")
      if not diagram_id:
        fail("diagram needs id")
      if diagram_id in ids:
        fail(f"duplicate diagram id: {diagram_id}")
      ids.add(diagram_id)
      models.extend(child_elements(diagram, "mxGraphModel"))
    if not models:
      fail("diagram must contain mxGraphModel")
    return models

  if root.tag == "mxGraphModel":
    return [root]

  fail(f"unsupported root element: {root.tag}")


def validate_unique_ids(cells):
  seen = set()
  for cell in cells:
    item_id = cell_id(cell)
    if not item_id:
      fail("mxCell without id")
    if item_id in seen:
      fail(f"duplicate mxCell id: {item_id}")
    seen.add(item_id)
  return seen


def validate_style_format(cells):
  for cell in cells:
    item_style = style(cell)
    if not item_style:
      continue
    for item in [part for part in item_style.split(";") if part]:
      if STYLE_ITEM_PATTERN.match(item):
        continue
      if item.startswith("points="):
        continue
      fail(f"invalid style item in {cell_id(cell)}: {item!r}")


def validate_labels(cells):
  for cell in cells:
    label = visible_label(cell)
    if HTML_PATTERN.search(label):
      fail(f"visible label must be plain text: id={cell_id(cell)} value={label!r}")
    if "\n" in label or "\r" in label:
      fail(f"visible label must stay on one line: id={cell_id(cell)} value={label!r}")


def validate_geometry(cells):
  for cell in cells:
    if cell_id(cell) in {"0", "1"}:
      continue

    item_geometry = geometry(cell)
    if item_geometry is None:
      fail(f"cell {cell_id(cell)} needs mxGeometry")

    _, _, width, height = item_geometry
    if is_vertex(cell) and (width <= 0 or height <= 0):
      fail(f"vertex {cell_id(cell)} needs positive width and height")

    if is_edge(cell):
      geometries = child_elements(cell, "mxGeometry")
      if geometries[0].attrib.get("relative") != "1":
        fail(f"edge {cell_id(cell)} needs mxGeometry relative=\"1\"")


def validate_model(model):
  roots = child_elements(model, "root")
  if len(roots) != 1:
    fail("mxGraphModel must contain exactly one root")

  root = roots[0]
  cells = child_elements(root, "mxCell")
  ids = validate_unique_ids(cells)

  root_cell = root.find("mxCell[@id='0']")
  layer_cell = root.find("mxCell[@id='1']")
  if root_cell is None:
    fail('missing mxCell id="0"')
  if layer_cell is None or layer_cell.attrib.get("parent") != "0":
    fail('missing mxCell id="1" parent="0"')

  vertices = set()
  for cell in cells:
    item_id = cell_id(cell)
    item_parent = parent_id(cell)
    if item_id != "0" and item_parent not in ids:
      fail(f"cell {item_id} has invalid parent {item_parent!r}")

    has_vertex = is_vertex(cell)
    has_edge = is_edge(cell)
    if has_vertex and has_edge:
      fail(f"cell {item_id} has both vertex and edge")
    if item_id not in {"0", "1"} and not has_vertex and not has_edge:
      fail(f"visible cell {item_id} must be vertex or edge")
    if has_vertex:
      vertices.add(item_id)

  for cell in cells:
    if not is_edge(cell):
      continue

    source = cell.attrib.get("source")
    target = cell.attrib.get("target")
    if not source or source not in vertices:
      fail(f"edge {cell_id(cell)} has invalid source {source!r}")
    if not target or target not in vertices:
      fail(f"edge {cell_id(cell)} has invalid target {target!r}")

  validate_geometry(cells)
  validate_style_format(cells)
  validate_labels(cells)
  validate_perimeters(cells)
  return cells


def validate_perimeters(cells):
  required = {
    "rhombus": "perimeter=rhombusPerimeter",
    "triangle": "perimeter=trianglePerimeter",
    "hexagon": "perimeter=hexagonPerimeter2",
    "ellipse": "perimeter=ellipsePerimeter",
  }

  for cell in cells:
    item_style = style(cell)
    for shape_name, perimeter in required.items():
      has_shape = (
        f"shape={shape_name}" in item_style
        or item_style.startswith(f"{shape_name};")
        or f";{shape_name};" in item_style
      )
      if has_shape and perimeter not in item_style:
        fail(f"non-rectangular shape {cell_id(cell)} needs {perimeter}")


def validate_parenting(cells):
  by_id = {cell_id(cell): cell for cell in cells}
  cluster_ids = {cell_id(cell) for cell in cells if is_cluster(cell)}
  namespace_ids = {cell_id(cell) for cell in cells if is_namespace(cell)}

  for cell in cells:
    item_id = cell_id(cell)
    parent = by_id.get(parent_id(cell))

    if is_namespace(cell):
      if parent is None or not is_cluster(parent):
        fail(f"namespace {item_id} must be parented by a cluster")

    if is_service(cell) or is_pod(cell) or is_workload(cell) or is_ingress_controller(cell):
      if parent_id(cell) not in cluster_ids and parent_id(cell) not in namespace_ids:
        fail(f"Kubernetes component {item_id} must be inside a cluster or namespace")

    if is_lb(cell):
      if parent_id(cell) == "1":
        continue
      if parent_id(cell) in cluster_ids:
        continue
      if parent is not None and cell_id(parent).startswith("grp-provider"):
        continue
      fail(f"LB {item_id} must be outside cluster, inside provider, or explicitly inside cluster")


def validate_required_topology(cells):
  if not any(is_cluster(cell) for cell in cells):
    fail("diagram needs at least one Kubernetes cluster boundary")
  if not any(is_kubernetes_icon(cell) for cell in cells):
    fail("diagram needs at least one draw.io Kubernetes icon")
  if not any(is_lb(cell) for cell in cells):
    fail("diagram needs at least one LB entrypoint")
  if not any(is_service(cell) for cell in cells):
    fail("diagram needs at least one Kubernetes Service")
  if not any(is_route_target(cell) for cell in cells):
    fail("diagram needs at least one Kubernetes workload or Pod")


def edge_pairs(cells):
  by_id = {cell_id(cell): cell for cell in cells}
  for edge in cells:
    if not is_edge(edge):
      continue
    source = by_id[edge.attrib["source"]]
    target = by_id[edge.attrib["target"]]
    yield edge, source, target


def has_path(edges, starts, targets):
  queue = list(starts)
  seen = set(queue)

  while queue:
    current = queue.pop(0)
    if current in targets:
      return True
    for source, target in edges:
      if source != current or target in seen:
        continue
      seen.add(target)
      queue.append(target)

  return False


def validate_flows(cells):
  ids_by_role = {
    "lb": {cell_id(cell) for cell in cells if is_lb(cell)},
    "service": {cell_id(cell) for cell in cells if is_service(cell)},
    "target": {cell_id(cell) for cell in cells if is_route_target(cell)},
    "external": {cell_id(cell) for cell in cells if is_external_system(cell)},
  }
  edges = [(edge.attrib["source"], edge.attrib["target"]) for edge in cells if is_edge(edge)]

  if not has_path(edges, ids_by_role["lb"], ids_by_role["service"]):
    fail("diagram needs LB -> optional ingress controller -> Service path")
  if not has_path(edges, ids_by_role["lb"], ids_by_role["target"]):
    fail("diagram needs LB -> Service -> workload or Pod path")

  for service_id in ids_by_role["service"]:
    if not has_path(edges, {service_id}, ids_by_role["target"]):
      fail(f"service {service_id} must route to at least one workload or pod")

  if ids_by_role["external"]:
    target_to_external = any(
      source in ids_by_role["target"] and target in ids_by_role["external"]
      for source, target in edges
    )
    if not target_to_external:
      fail("external systems need at least one workload or Pod -> external system edge")


def validate_y_axis_alignment(cells):
  by_id = {cell_id(cell): cell for cell in cells}

  for edge, source, target in edge_pairs(cells):
    source_center = center(source, by_id)
    target_center = center(target, by_id)
    delta_y = abs(source_center[1] - target_center[1])

    if is_main_flow(edge) and delta_y > 2:
      fail(f"main flow edge {cell_id(edge)} is not y-axis aligned")

    if is_service(source) and is_route_target(target) and delta_y > 2:
      fail(f"Service -> workload/Pod edge {cell_id(edge)} is not y-axis aligned")

    if is_workload(source) and is_pod(target) and delta_y > 2:
      fail(f"Workload -> Pod edge {cell_id(edge)} is not y-axis aligned")


def is_y_axis_aligned(source, target, cells_by_id):
  source_center = center(source, cells_by_id)
  target_center = center(target, cells_by_id)
  return abs(source_center[1] - target_center[1]) <= 2


def validate_reference_similarity(cells):
  by_id = {cell_id(cell): cell for cell in cells}
  edges = [(edge.attrib["source"], edge.attrib["target"]) for edge in cells if is_edge(edge)]
  lb_ids = {cell_id(cell) for cell in cells if is_lb(cell)}
  service_ids = {cell_id(cell) for cell in cells if is_service(cell)}
  target_ids = {cell_id(cell) for cell in cells if is_route_target(cell)}
  external_ids = {cell_id(cell) for cell in cells if is_external_system(cell)}

  service_target_edges = [
    (source, target)
    for _, source, target in edge_pairs(cells)
    if is_service(source) and is_route_target(target)
  ]
  main_flow_edges = [
    (source, target)
    for edge, source, target in edge_pairs(cells)
    if is_main_flow(edge)
  ]
  target_external_edges = [
    (source, target)
    for source, target in edges
    if source in target_ids and target in external_ids
  ]

  checks = [
    any(is_cluster(cell) for cell in cells),
    any(is_lb(cell) for cell in cells),
    any(is_ingress_controller(cell) for cell in cells) or has_path(edges, lb_ids, service_ids),
    bool(service_ids),
    bool(target_ids),
    has_path(edges, lb_ids, service_ids),
    has_path(edges, lb_ids, target_ids),
    all(is_y_axis_aligned(source, target, by_id) for source, target in service_target_edges),
    all(is_y_axis_aligned(source, target, by_id) for source, target in main_flow_edges),
    not external_ids or bool(target_external_edges),
    any(is_kubernetes_icon(cell) for cell in cells),
  ]
  score = round(sum(1 for item in checks if item) / len(checks) * 100)
  if score < 95:
    fail(f"reference-like structure score must be >= 95%, got {score}%")
  return score


def main():
  if len(sys.argv) != 2:
    fail("usage: validate_drawio_xml.py <file.drawio>")

  path = Path(sys.argv[1])
  try:
    tree = ET.parse(path)
  except ET.ParseError as exc:
    fail(f"invalid XML: {exc}")

  all_cells = []
  for model in validate_structure(tree.getroot()):
    all_cells.extend(validate_model(model))

  validate_required_topology(all_cells)
  validate_parenting(all_cells)
  validate_flows(all_cells)
  validate_y_axis_alignment(all_cells)
  score = validate_reference_similarity(all_cells)
  print(f"OK: draw.io XML is valid for Kubernetes network rules; reference-like structure score={score}%")


if __name__ == "__main__":
  main()
