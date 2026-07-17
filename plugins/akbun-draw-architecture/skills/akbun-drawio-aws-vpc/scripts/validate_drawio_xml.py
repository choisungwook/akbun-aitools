#!/usr/bin/env python3
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


CIDR_PATTERN = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}/\d{1,2}\b")
HTML_PATTERN = re.compile(r"<[^>]+>")
PORT_PATTERN = re.compile(r":\d{2,5}\b")


def fail(message):
  print(f"FAIL: {message}", file=sys.stderr)
  raise SystemExit(1)


def child_elements(parent, name):
  return [child for child in list(parent) if child.tag == name]


def visible_label(cell):
  return cell.attrib.get("value", "")


def style(cell):
  return cell.attrib.get("style", "")


def style_contains(cell, fragment):
  return fragment.lower() in style(cell).lower()


def cell_id(cell):
  return cell.attrib.get("id", "")


def parent_id(cell):
  return cell.attrib.get("parent", "")


def is_vertex(cell):
  return cell.attrib.get("vertex") == "1"


def is_edge(cell):
  return cell.attrib.get("edge") == "1"


def has_cidr(cell):
  return bool(CIDR_PATTERN.search(visible_label(cell)))


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


def size(cell):
  item = geometry(cell)
  if not item:
    return None

  return item[2], item[3]


def is_background(cell):
  return (
    is_vertex(cell)
    and cell_id(cell).startswith("bg-")
    and style_contains(cell, "fillcolor=#f5f5f5")
    and style_contains(cell, "rounded=1")
  )


def is_title(cell):
  return is_vertex(cell) and cell_id(cell).startswith("txt-")


def is_cloud_group(cell):
  return (
    is_vertex(cell)
    and cell_id(cell).startswith("grp-cloud")
    and style_contains(cell, "container=1")
    and style_contains(cell, "shape=mxgraph.aws4.group")
    and style_contains(cell, "group_aws_cloud")
  )


def is_vpc_group(cell):
  return (
    is_vertex(cell)
    and cell_id(cell).startswith("grp-vpc")
    and style_contains(cell, "container=1")
    and style_contains(cell, "shape=mxgraph.aws4.group")
    and style_contains(cell, "group_vpc")
  )


def is_az_group(cell):
  return (
    is_vertex(cell)
    and cell_id(cell).startswith("grp-az")
    and style_contains(cell, "container=1")
    and style_contains(cell, "dashed=1")
  )


def is_subnet_group(cell):
  return (
    is_vertex(cell)
    and cell_id(cell).startswith("grp-subnet")
    and style_contains(cell, "container=1")
    and style_contains(cell, "shape=mxgraph.aws4.group")
  )


def is_public_subnet(cell):
  text = f"{cell_id(cell)} {visible_label(cell)}".lower()
  return "public" in text or "pub" in text


def is_nat_gateway(cell):
  return (
    is_vertex(cell)
    and cell_id(cell).startswith("svc-nat")
    and style_contains(cell, "shape=mxgraph.aws4.nat_gateway")
  )


def is_internet_gateway(cell):
  return (
    is_vertex(cell)
    and cell_id(cell).startswith("svc-igw")
    and style_contains(cell, "shape=mxgraph.aws4.internet_gateway")
  )


def is_aws_resource_icon(cell):
  if not is_vertex(cell):
    return False
  if "mxgraph.aws4" not in style(cell):
    return False
  if style_contains(cell, "shape=mxgraph.aws4.group"):
    return False
  if style_contains(cell, "shape=mxgraph.aws4.groupcenter"):
    return False
  return style_contains(cell, "shape=mxgraph.aws4.")


def validate_labels(cells):
  for cell in cells:
    label = visible_label(cell)
    if HTML_PATTERN.search(label):
      fail(f"visible label must be plain text: id={cell_id(cell)} value={label!r}")
    if "\n" in label or "\r" in label:
      fail(f"visible label must stay on one line: id={cell_id(cell)} value={label!r}")
    if PORT_PATTERN.search(label):
      fail(f"visible label contains port detail: id={cell_id(cell)} value={label!r}")


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


def validate_structure(root):
  if root.tag == "mxfile":
    diagrams = child_elements(root, "diagram")
    if not diagrams:
      fail("mxfile must contain at least one diagram")
    models = []
    for diagram in diagrams:
      models.extend(child_elements(diagram, "mxGraphModel"))
    if not models:
      fail("diagram must contain mxGraphModel")
    return models

  if root.tag == "mxGraphModel":
    return [root]

  fail(f"unsupported root element: {root.tag}")


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

    item_id = cell_id(cell)
    source = cell.attrib.get("source")
    target = cell.attrib.get("target")
    if source and source not in vertices:
      fail(f"edge {item_id} has invalid source {source!r}")
    if target and target not in vertices:
      fail(f"edge {item_id} has invalid target {target!r}")
    geometries = child_elements(cell, "mxGeometry")
    if not geometries or geometries[0].attrib.get("relative") != "1":
      fail(f"edge {item_id} needs mxGeometry relative=\"1\"")

  validate_labels(cells)
  return cells


def validate_aws_icon_pack(cells):
  aws_cells = [
    cell for cell in cells
    if "mxgraph.aws4" in style(cell)
  ]
  if not aws_cells:
    fail("diagram does not use mxgraph.aws4 AWS icon pack")


def validate_no_background(cells):
  backgrounds = [cell_id(cell) for cell in cells if is_background(cell)]
  if backgrounds:
    fail(f"diagram must not contain a background rectangle: {', '.join(backgrounds)}")


def validate_no_cloud_group(cells):
  cloud_groups = [cell_id(cell) for cell in cells if is_cloud_group(cell)]
  if cloud_groups:
    fail(f"diagram must not contain an AWS Cloud group: {', '.join(cloud_groups)}")


def validate_no_edges(cells):
  edges = [cell_id(cell) for cell in cells if is_edge(cell)]
  if edges:
    fail(f"VPC subnet foundation diagrams must not contain traffic edges: {', '.join(edges)}")


def validate_allowed_vertices(cells):
  allowed = (
    is_title,
    is_vpc_group,
    is_az_group,
    is_subnet_group,
    is_nat_gateway,
    is_internet_gateway,
  )

  for cell in cells:
    if cell_id(cell) in {"0", "1"} or not is_vertex(cell):
      continue
    if any(check(cell) for check in allowed):
      continue
    fail(f"out-of-scope visible cell: id={cell_id(cell)} value={visible_label(cell)!r}")


def validate_resource_icons(cells):
  for cell in cells:
    if not is_aws_resource_icon(cell):
      continue
    if is_nat_gateway(cell) or is_internet_gateway(cell):
      continue
    fail(f"out-of-scope AWS resource icon: id={cell_id(cell)} value={visible_label(cell)!r}")


def validate_group_sizes(cells):
  for cell in cells:
    item_size = size(cell)
    if item_size is None:
      if cell_id(cell) not in {"0", "1"}:
        fail(f"cell {cell_id(cell)} needs mxGeometry width and height")
      continue

    width, height = item_size
    if is_vpc_group(cell) and (width < 700 or height < 620):
      fail(f"VPC group {cell_id(cell)} is smaller than 700x620")
    if is_az_group(cell) and (width < 300 or height < 520):
      fail(f"AZ container {cell_id(cell)} is smaller than 300x520")
    if is_subnet_group(cell) and (width < 240 or height < 100):
      fail(f"subnet group {cell_id(cell)} is smaller than 240x100")
    if (is_nat_gateway(cell) or is_internet_gateway(cell)) and (width != 48 or height != 48):
      fail(f"resource icon {cell_id(cell)} must be 48x48, got {width:g}x{height:g}")


def validate_group_fonts(cells):
  for cell in cells:
    if is_vpc_group(cell) and not style_contains(cell, "fontsize=10"):
      fail(f"VPC group {cell_id(cell)} must use fontSize=10 for CIDR label")
    if is_az_group(cell) and not style_contains(cell, "fontsize=12"):
      fail(f"AZ container {cell_id(cell)} must use fontSize=12")
    if is_subnet_group(cell) and not style_contains(cell, "fontsize=10"):
      fail(f"subnet group {cell_id(cell)} must use fontSize=10 for CIDR label")
    if (is_vpc_group(cell) or is_az_group(cell) or is_subnet_group(cell)) and not style_contains(cell, "fontstyle=1"):
      fail(f"group {cell_id(cell)} must use bold label fontStyle=1")


def validate_cidr_labels(cells):
  for cell in cells:
    if is_vpc_group(cell) and not has_cidr(cell):
      fail(f"VPC group label must include CIDR: id={cell_id(cell)} value={visible_label(cell)!r}")
    if is_subnet_group(cell) and not has_cidr(cell):
      fail(f"subnet group label must include CIDR: id={cell_id(cell)} value={visible_label(cell)!r}")


def validate_parenting(cells):
  by_id = {cell_id(cell): cell for cell in cells}

  for cell in cells:
    if is_vpc_group(cell):
      if parent_id(cell) != "1":
        fail(f"VPC group {cell_id(cell)} must be parented by the default layer")

    if is_az_group(cell):
      parent = by_id.get(parent_id(cell))
      if parent is None or not is_vpc_group(parent):
        fail(f"AZ container {cell_id(cell)} must be parented by a VPC group")
      az_geometry = geometry(cell)
      vpc_geometry = geometry(parent)
      if az_geometry is None or vpc_geometry is None:
        fail(f"AZ container {cell_id(cell)} and parent VPC need mxGeometry")
      _, az_y, _, az_height = az_geometry
      _, _, _, vpc_height = vpc_geometry
      if not (az_y < 0 and az_y + az_height > vpc_height):
        fail(f"AZ container {cell_id(cell)} must extend beyond the VPC top and bottom boundaries")

    if is_subnet_group(cell):
      parent = by_id.get(parent_id(cell))
      if parent is None or not is_az_group(parent):
        fail(f"subnet group {cell_id(cell)} must be parented by an AZ container")

    if is_nat_gateway(cell):
      parent = by_id.get(parent_id(cell))
      if parent is None or not is_subnet_group(parent):
        fail(f"NAT Gateway {cell_id(cell)} must be parented by a public subnet group")
      if not is_public_subnet(parent):
        fail(f"NAT Gateway {cell_id(cell)} must be placed in a public subnet")

    if is_internet_gateway(cell):
      parent = by_id.get(parent_id(cell))
      if parent is None or not is_vpc_group(parent):
        fail(f"Internet Gateway {cell_id(cell)} must be parented by a VPC group")
      item_geometry = geometry(cell)
      if item_geometry is None:
        fail(f"Internet Gateway {cell_id(cell)} needs mxGeometry")
      _, y, _, height = item_geometry
      if not y < 0 < y + height:
        fail(f"Internet Gateway {cell_id(cell)} must overlap the VPC top boundary")


def validate_required_topology(cells):
  vpc_groups = [cell for cell in cells if is_vpc_group(cell)]
  az_groups = [cell for cell in cells if is_az_group(cell)]
  subnet_groups = [cell for cell in cells if is_subnet_group(cell)]

  if not vpc_groups:
    fail("diagram needs at least one VPC group")
  if not az_groups:
    fail("diagram needs at least one AZ dashed container")
  if not subnet_groups:
    fail("diagram needs at least one subnet group")


def validate_igw_count(cells):
  igw_by_vpc = {}
  for cell in cells:
    if not is_internet_gateway(cell):
      continue
    igw_by_vpc.setdefault(parent_id(cell), []).append(cell_id(cell))

  for vpc_id, igw_ids in igw_by_vpc.items():
    if len(igw_ids) > 1:
      fail(f"VPC {vpc_id} has more than one Internet Gateway: {', '.join(igw_ids)}")


def validate_igw_clearance(cells):
  az_by_vpc = {}
  for cell in cells:
    if is_az_group(cell):
      az_by_vpc.setdefault(parent_id(cell), []).append(cell)

  for igw in cells:
    if not is_internet_gateway(igw):
      continue

    igw_geometry = geometry(igw)
    if igw_geometry is None:
      fail(f"Internet Gateway {cell_id(igw)} needs mxGeometry")
    igw_x, _, igw_width, _ = igw_geometry
    left = igw_x - 40
    right = igw_x + igw_width + 40

    for az in az_by_vpc.get(parent_id(igw), []):
      az_geometry = geometry(az)
      if az_geometry is None:
        fail(f"AZ container {cell_id(az)} needs mxGeometry")
      az_x, _, az_width, _ = az_geometry
      for boundary_x in (az_x, az_x + az_width):
        if left <= boundary_x <= right:
          fail(f"Internet Gateway {cell_id(igw)} overlaps AZ boundary of {cell_id(az)}")


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

  validate_aws_icon_pack(all_cells)
  validate_no_background(all_cells)
  validate_no_cloud_group(all_cells)
  validate_no_edges(all_cells)
  validate_allowed_vertices(all_cells)
  validate_resource_icons(all_cells)
  validate_required_topology(all_cells)
  validate_group_sizes(all_cells)
  validate_group_fonts(all_cells)
  validate_cidr_labels(all_cells)
  validate_parenting(all_cells)
  validate_igw_count(all_cells)
  validate_igw_clearance(all_cells)
  print("OK: draw.io XML is valid for AWS VPC subnet foundation rules")


if __name__ == "__main__":
  main()
