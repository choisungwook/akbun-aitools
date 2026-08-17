#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_VERSION = 2
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
COMPONENT_KINDS = {
  "service",
  "module",
  "component",
  "datastore",
  "message-broker",
  "external-system",
}
# entrypoint 부터 external 까지가 하나의 업무 흐름에서 나올 수 있는 최대 5단계다.
LAYERS = ["entrypoint", "application", "domain", "infrastructure", "external"]
LAYER_INDEX = {layer: index for index, layer in enumerate(LAYERS)}
MAX_DEPTH = len(LAYERS)
ORIGIN_TYPES = {"git", "database", "code"}
ORIGIN_ENGINES = {
  "postgres",
  "mysql",
  "rds",
  "aurora",
  "redis",
  "dynamodb",
  "mongodb",
  "elasticsearch",
  "s3",
  "kafka",
  "rabbitmq",
  "sqs",
  "sns",
  "other",
}
RELATIONSHIP_KINDS = {
  "code-call",
  "http",
  "grpc",
  "db-read",
  "db-write",
  "external-api",
  "event-publish",
  "event-subscribe",
  "queue-produce",
  "queue-consume",
}
IMPORTANCE_VALUES = {"core", "supporting"}
API_PROTOCOLS = {"http", "grpc", "graphql", "event", "queue"}
CAPACITY_SOURCES = {"manifest", "assumed"}
CRYPTO_KINDS = {"none", "tls", "mtls", "field", "kms"}
DETAIL_FIELDS = {
  "method",
  "path",
  "grpc_service",
  "grpc_method",
  "database",
  "table",
  "broker",
  "topic",
  "queue",
  "provider",
  "endpoint",
  "function",
}


def utc_now() -> str:
  return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_git(root: Path, *args: str) -> str | None:
  try:
    result = subprocess.run(
      ["git", "-C", str(root), *args],
      capture_output=True,
      text=True,
      timeout=20,
      check=False,
    )
  except (OSError, subprocess.TimeoutExpired):
    return None
  if result.returncode != 0:
    return None
  return result.stdout.rstrip("\r\n")


def store_root() -> Path:
  override = os.environ.get("AKBUN_ANALYSIS_HOME")
  if override:
    return Path(override).expanduser()
  system = platform.system()
  if system == "Darwin":
    return Path.home() / "Library" / "Application Support" / "akbun-analysis"
  if system == "Windows":
    base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    return base / "akbun-analysis"
  base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
  return base.expanduser() / "akbun-analysis"


def repo_name_from_remote(remote: str) -> str | None:
  tail = remote.rstrip("/")
  if "://" not in tail and ":" in tail:
    tail = tail.rsplit(":", 1)[-1]
  tail = tail.rsplit("/", 1)[-1]
  if tail.endswith(".git"):
    tail = tail[:-4]
  return tail or None


def project_identity(root: Path) -> dict[str, str | None]:
  resolved = root.expanduser().resolve()
  remote = run_git(resolved, "remote", "get-url", "origin")
  seed = remote or str(resolved)
  digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8]
  name = (repo_name_from_remote(remote) if remote else None) or resolved.name
  slug = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-.").lower() or "project"
  return {
    "id": f"{slug}-{digest}",
    "name": slug,
    "root_path": str(resolved),
    "remote": remote,
  }


def project_paths(root: Path) -> dict[str, Path]:
  identity = project_identity(root)
  project_dir = store_root() / "projects" / str(identity["id"])
  return {
    "store_root": store_root(),
    "project_dir": project_dir,
    "analysis": project_dir / "analysis.json",
    "html": project_dir / "analysis.html",
    "drawio": project_dir / "analysis.drawio",
    "registry": store_root() / "projects.json",
  }


def load_json(path: Path) -> dict[str, Any] | None:
  if not path.exists():
    return None
  try:
    data = json.loads(path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError):
    return None
  return data if isinstance(data, dict) else None


def atomic_write_text(path: Path, content: str) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  candidate = path.with_name(f".{path.name}.candidate-{os.getpid()}")
  candidate.write_text(content, encoding="utf-8")
  os.replace(candidate, path)


def write_json(path: Path, data: dict[str, Any]) -> None:
  atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def register_project(root: Path) -> dict[str, Any]:
  identity = project_identity(root)
  paths = project_paths(root)
  paths["project_dir"].mkdir(parents=True, exist_ok=True)
  registry = load_json(paths["registry"]) or {"schema_version": 1, "projects": []}
  projects = registry.get("projects")
  if not isinstance(projects, list):
    projects = []
    registry["projects"] = projects
  entry = next(
    (
      item
      for item in projects
      if item.get("id") == identity["id"] or item.get("project_id") == identity["id"]
    ),
    None,
  )
  if entry is None:
    entry = {"id": identity["id"], "registered_at": utc_now()}
    projects.append(entry)
  entry.update(identity)
  entry["analysis_path"] = str(paths["analysis"])
  entry["updated_at"] = utc_now()
  write_json(paths["registry"], registry)
  return identity


def git_head(root: Path) -> str | None:
  return run_git(root, "rev-parse", "HEAD")


def git_commit_exists(root: Path, commit: str) -> bool:
  return run_git(root, "cat-file", "-e", f"{commit}^{{commit}}") is not None


def working_tree_files(root: Path) -> list[str]:
  paths: set[str] = set()
  commands = [
    ("diff", "--name-only", "-z", "HEAD"),
    ("diff", "--name-only", "-z", "--cached", "HEAD"),
    ("ls-files", "--others", "--exclude-standard", "-z"),
  ]
  for command in commands:
    output = run_git(root, *command)
    if output:
      paths.update(item for item in output.split("\0") if item)
  return sorted(paths)


def worktree_fingerprint(root: Path) -> str:
  digest = hashlib.sha256()
  changed = working_tree_files(root)
  digest.update("\n".join(changed).encode("utf-8"))
  tracked_diff = run_git(root, "diff", "--binary", "HEAD") or ""
  staged_diff = run_git(root, "diff", "--binary", "--cached", "HEAD") or ""
  digest.update(tracked_diff.encode("utf-8"))
  digest.update(staged_diff.encode("utf-8"))
  for relative in changed:
    path = root / relative
    if path.is_file() and run_git(root, "ls-files", "--error-unmatch", relative) is None:
      digest.update(relative.encode("utf-8"))
      try:
        digest.update(path.read_bytes())
      except OSError:
        pass
  return digest.hexdigest()


def changed_files(root: Path, analyzed_commit: str | None) -> list[str]:
  paths = set(working_tree_files(root))
  if analyzed_commit:
    output = run_git(root, "diff", "--name-only", f"{analyzed_commit}..HEAD")
    if output:
      paths.update(output.splitlines())
  return sorted(path for path in paths if path)


def path_matches(changed: str, owned: str) -> bool:
  normalized = owned.rstrip("/")
  return changed == normalized or changed.startswith(f"{normalized}/")


def affected_flows(data: dict[str, Any], relationship_ids: set[str], component_ids: set[str]) -> list[str]:
  """근거가 바뀐 관계나 컴포넌트를 지나는 업무 흐름을 찾는다."""
  found: set[str] = set()
  for business in data.get("businesses", []):
    if not isinstance(business, dict):
      continue
    for flow in business.get("flows", []):
      if not isinstance(flow, dict):
        continue
      steps = flow.get("steps", [])
      if flow.get("entry") in component_ids or any(step in relationship_ids for step in steps):
        found.add(flow.get("id"))
  return sorted(item for item in found if isinstance(item, str))


def affected_components(data: dict[str, Any], files: list[str]) -> tuple[list[str], list[str], list[str]]:
  affected: set[str] = set()
  affected_relationships: set[str] = set()
  matched_files: set[str] = set()
  for component in data.get("components", []):
    owned_paths = component.get("owned_paths", [])
    evidence_paths = [item.get("path") for item in component.get("evidence", [])]
    known_paths = [path for path in [*owned_paths, *evidence_paths] if isinstance(path, str)]
    for changed in files:
      if any(path_matches(changed, known) for known in known_paths):
        affected.add(component.get("id"))
        matched_files.add(changed)
  for relationship in data.get("relationships", []):
    evidence_paths = [item.get("path") for item in relationship.get("evidence", [])]
    for changed in files:
      if changed in evidence_paths:
        affected.add(relationship.get("source"))
        affected_relationships.add(relationship.get("id"))
        if not relationship.get("target_project_id"):
          affected.add(relationship.get("target"))
        matched_files.add(changed)
  component_ids = {item for item in affected if item}
  return (
    sorted(component_ids),
    sorted(set(files) - matched_files),
    affected_flows(data, affected_relationships, component_ids),
  )


def valid_relative_path(value: str) -> bool:
  path = PurePosixPath(value)
  return bool(value) and not path.is_absolute() and ".." not in path.parts


def file_line_count(path: Path) -> int:
  try:
    with path.open("rb") as stream:
      return sum(1 for _ in stream)
  except OSError:
    return 0


def validate_evidence(
  evidence: Any,
  subject: str,
  repo_root: Path | None,
  errors: list[dict[str, str]],
) -> None:
  if not isinstance(evidence, list) or not evidence:
    errors.append({"subject": subject, "message": "evidence must contain at least one file:line"})
    return
  for index, item in enumerate(evidence):
    item_subject = f"{subject}.evidence[{index}]"
    if not isinstance(item, dict):
      errors.append({"subject": item_subject, "message": "evidence must be an object"})
      continue
    unknown = set(item) - {"path", "line", "end_line", "description"}
    if unknown:
      errors.append({"subject": item_subject, "message": f"unknown fields: {sorted(unknown)}"})
    path = item.get("path")
    line = item.get("line")
    description = item.get("description")
    if not isinstance(path, str) or not valid_relative_path(path):
      errors.append({"subject": item_subject, "message": "path must be a project-relative path"})
      continue
    if not isinstance(line, int) or isinstance(line, bool) or line < 1:
      errors.append({"subject": item_subject, "message": "line must be a positive integer"})
      continue
    end_line = item.get("end_line", line)
    if not isinstance(end_line, int) or isinstance(end_line, bool) or end_line < line:
      errors.append({"subject": item_subject, "message": "end_line must be at least line"})
    if not isinstance(description, str) or not description.strip():
      errors.append({"subject": item_subject, "message": "description is required"})
    if repo_root:
      source = repo_root / path
      if not source.is_file():
        errors.append({"subject": item_subject, "message": f"evidence file not found: {path}"})
      else:
        count = file_line_count(source)
        if line > count or end_line > count:
          errors.append({"subject": item_subject, "message": f"line range exceeds {path} ({count} lines)"})


def validate_origin(origin: Any, subject: str, errors: list[dict[str, str]]) -> None:
  if not isinstance(origin, dict):
    errors.append({"subject": subject, "message": "origin must be an object"})
    return
  unknown = set(origin) - {"type", "label", "engine"}
  if unknown:
    errors.append({"subject": subject, "message": f"unknown fields: {sorted(unknown)}"})
  if origin.get("type") not in ORIGIN_TYPES:
    errors.append({"subject": f"{subject}.type", "message": f"must be one of {sorted(ORIGIN_TYPES)}"})
  if not isinstance(origin.get("label"), str) or not origin.get("label", "").strip():
    errors.append({"subject": f"{subject}.label", "message": "non-empty string required"})
  engine = origin.get("engine")
  if origin.get("type") == "database" and engine is None:
    errors.append({"subject": f"{subject}.engine", "message": "database origin requires an engine"})
  if engine is not None and engine not in ORIGIN_ENGINES:
    errors.append({"subject": f"{subject}.engine", "message": f"must be one of {sorted(ORIGIN_ENGINES)}"})


def validate_capacity(capacity: Any, subject: str, errors: list[dict[str, str]]) -> None:
  if capacity is None:
    return
  if not isinstance(capacity, dict):
    errors.append({"subject": subject, "message": "capacity must be an object"})
    return
  allowed = {"replicas", "cpu_millicores", "memory_mib", "max_replicas", "source"}
  unknown = set(capacity) - allowed
  if unknown:
    errors.append({"subject": subject, "message": f"unknown fields: {sorted(unknown)}"})
  for field in ("replicas", "cpu_millicores", "memory_mib"):
    value = capacity.get(field)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
      errors.append({"subject": f"{subject}.{field}", "message": "positive integer required"})
  max_replicas = capacity.get("max_replicas")
  if max_replicas is not None:
    if not isinstance(max_replicas, int) or isinstance(max_replicas, bool) or max_replicas < 1:
      errors.append({"subject": f"{subject}.max_replicas", "message": "positive integer required"})
    elif isinstance(capacity.get("replicas"), int) and max_replicas < capacity["replicas"]:
      errors.append({"subject": f"{subject}.max_replicas", "message": "must be at least replicas"})
  if capacity.get("source") not in CAPACITY_SOURCES:
    errors.append({"subject": f"{subject}.source", "message": f"must be one of {sorted(CAPACITY_SOURCES)}"})


def validate_load(load: Any, subject: str, errors: list[dict[str, str]]) -> None:
  if load is None:
    return
  if not isinstance(load, dict):
    errors.append({"subject": subject, "message": "load must be an object"})
    return
  unknown = set(load) - {"fan_out", "fan_out_note", "sync", "crypto"}
  if unknown:
    errors.append({"subject": subject, "message": f"unknown fields: {sorted(unknown)}"})
  fan_out = load.get("fan_out")
  if fan_out is not None:
    if not isinstance(fan_out, (int, float)) or isinstance(fan_out, bool) or fan_out < 0:
      errors.append({"subject": f"{subject}.fan_out", "message": "must be a number of 0 or more"})
    elif fan_out > 1 and not isinstance(load.get("fan_out_note"), str):
      errors.append({
        "subject": f"{subject}.fan_out_note",
        "message": "fan_out above 1 needs a note explaining what repeats the call",
      })
  if load.get("sync") is not None and not isinstance(load.get("sync"), bool):
    errors.append({"subject": f"{subject}.sync", "message": "must be a boolean"})
  if load.get("crypto") is not None and load.get("crypto") not in CRYPTO_KINDS:
    errors.append({"subject": f"{subject}.crypto", "message": f"must be one of {sorted(CRYPTO_KINDS)}"})


def validate_apis(
  apis: Any,
  component_ids: set[str],
  flow_ids: set[str],
  errors: list[dict[str, str]],
  warnings: list[dict[str, str]],
) -> set[str]:
  if not isinstance(apis, list):
    errors.append({"subject": "apis", "message": "apis must be an array"})
    return set()
  allowed = {
    "id", "name", "protocol", "method", "path", "grpc_service", "grpc_method",
    "topic", "provider", "provider_project_id", "entrypoint", "flow_ids", "evidence",
  }
  seen: set[str] = set()
  addresses: dict[str, str] = {}
  for index, api in enumerate(apis):
    subject = f"apis[{index}]"
    if not isinstance(api, dict):
      errors.append({"subject": subject, "message": "api must be an object"})
      continue
    unknown = set(api) - allowed
    if unknown:
      errors.append({"subject": subject, "message": f"unknown fields: {sorted(unknown)}"})
    api_id = api.get("id")
    if not isinstance(api_id, str) or not ID_PATTERN.fullmatch(api_id):
      errors.append({"subject": f"{subject}.id", "message": "invalid identifier"})
    elif api_id in seen:
      errors.append({"subject": f"{subject}.id", "message": "duplicate api id"})
    else:
      seen.add(api_id)
    if not isinstance(api.get("name"), str) or not api.get("name", "").strip():
      errors.append({"subject": f"{subject}.name", "message": "non-empty string required"})
    protocol = api.get("protocol")
    if protocol not in API_PROTOCOLS:
      errors.append({"subject": f"{subject}.protocol", "message": f"must be one of {sorted(API_PROTOCOLS)}"})
    if protocol in {"http", "graphql"} and not isinstance(api.get("path"), str):
      errors.append({"subject": f"{subject}.path", "message": f"{protocol} api needs a path"})
    if protocol == "grpc" and not (api.get("grpc_service") and api.get("grpc_method")):
      errors.append({"subject": f"{subject}.grpc_service", "message": "grpc api needs service and method"})
    if protocol in {"event", "queue"} and not isinstance(api.get("topic"), str):
      errors.append({"subject": f"{subject}.topic", "message": f"{protocol} api needs a topic"})
    if api.get("provider_project_id") is None and api.get("provider") not in component_ids:
      errors.append({"subject": f"{subject}.provider", "message": "provider component not found"})
    if not isinstance(api.get("entrypoint"), bool):
      errors.append({"subject": f"{subject}.entrypoint", "message": "must be a boolean"})
    unknown_flows = [item for item in api.get("flow_ids", []) if item not in flow_ids]
    if unknown_flows:
      errors.append({"subject": f"{subject}.flow_ids", "message": f"unknown flow ids: {unknown_flows}"})
    validate_evidence(api.get("evidence"), subject, None, errors)
    address = api_address(api)
    if address and address in addresses:
      warnings.append({"subject": subject, "message": f"same address as {addresses[address]}: {address}"})
    elif address:
      addresses[address] = str(api_id)
  if isinstance(apis, list) and apis and not any(
    isinstance(api, dict) and api.get("entrypoint") for api in apis
  ):
    warnings.append({"subject": "apis", "message": "no entrypoint api; the load view has nothing to drive"})
  return seen


def api_address(api: dict[str, Any]) -> str:
  """API 를 화면과 목록에서 부를 한 줄짜리 주소."""
  protocol = api.get("protocol")
  if protocol == "grpc":
    return f"{api.get('grpc_service', '')}/{api.get('grpc_method', '')}"
  if protocol in {"event", "queue"}:
    return f"{protocol}:{api.get('topic', '')}"
  method = api.get("method")
  path = api.get("path", "")
  return f"{method} {path}".strip() if method else path


def flow_depth(entry: str, step_ids: list[str], relationships_by_id: dict[str, dict[str, Any]]) -> int:
  """진입점에서 각 관계를 따라갔을 때 나오는 최대 홉 수를 센다."""
  depth_by_component = {entry: 1}
  reached = 1
  for step_id in step_ids:
    relationship = relationships_by_id.get(step_id)
    if not relationship:
      continue
    source_depth = depth_by_component.get(relationship.get("source"))
    if source_depth is None:
      continue
    target = relationship.get("target")
    target_depth = max(depth_by_component.get(target, 0), source_depth + 1)
    depth_by_component[target] = target_depth
    reached = max(reached, target_depth)
  return reached


def validate_businesses(
  businesses: Any,
  component_ids: set[str],
  relationships: list[Any],
  errors: list[dict[str, str]],
  warnings: list[dict[str, str]],
) -> None:
  if not isinstance(businesses, list):
    errors.append({"subject": "businesses", "message": "businesses must be an array"})
    return
  relationships_by_id = {
    item["id"]: item
    for item in relationships
    if isinstance(item, dict) and isinstance(item.get("id"), str)
  }
  business_ids: set[str] = set()
  flow_ids: set[str] = set()
  for index, business in enumerate(businesses):
    subject = f"businesses[{index}]"
    if not isinstance(business, dict):
      errors.append({"subject": subject, "message": "business must be an object"})
      continue
    unknown = set(business) - {"id", "name", "description", "flows"}
    if unknown:
      errors.append({"subject": subject, "message": f"unknown fields: {sorted(unknown)}"})
    business_id = business.get("id")
    if not isinstance(business_id, str) or not ID_PATTERN.fullmatch(business_id):
      errors.append({"subject": f"{subject}.id", "message": "invalid identifier"})
    elif business_id in business_ids:
      errors.append({"subject": f"{subject}.id", "message": "duplicate business id"})
    else:
      business_ids.add(business_id)
    for field in ("name", "description"):
      if not isinstance(business.get(field), str) or not business.get(field, "").strip():
        errors.append({"subject": f"{subject}.{field}", "message": "non-empty string required"})
    flows = business.get("flows")
    if not isinstance(flows, list) or not flows:
      errors.append({"subject": f"{subject}.flows", "message": "at least one flow is required"})
      continue
    for flow_index, flow in enumerate(flows):
      flow_subject = f"{subject}.flows[{flow_index}]"
      if not isinstance(flow, dict):
        errors.append({"subject": flow_subject, "message": "flow must be an object"})
        continue
      unknown = set(flow) - {"id", "name", "description", "trigger", "entry", "steps"}
      if unknown:
        errors.append({"subject": flow_subject, "message": f"unknown fields: {sorted(unknown)}"})
      flow_id = flow.get("id")
      if not isinstance(flow_id, str) or not ID_PATTERN.fullmatch(flow_id):
        errors.append({"subject": f"{flow_subject}.id", "message": "invalid identifier"})
      elif flow_id in flow_ids:
        errors.append({"subject": f"{flow_subject}.id", "message": "duplicate flow id"})
      else:
        flow_ids.add(flow_id)
      for field in ("name", "description"):
        if not isinstance(flow.get(field), str) or not flow.get(field, "").strip():
          errors.append({"subject": f"{flow_subject}.{field}", "message": "non-empty string required"})
      trigger = flow.get("trigger")
      if trigger is not None and (not isinstance(trigger, str) or not trigger.strip()):
        errors.append({"subject": f"{flow_subject}.trigger", "message": "must be a non-empty string"})
      entry = flow.get("entry")
      if entry not in component_ids:
        errors.append({"subject": f"{flow_subject}.entry", "message": "entry component not found"})
      steps = flow.get("steps")
      if not isinstance(steps, list) or not steps:
        errors.append({"subject": f"{flow_subject}.steps", "message": "at least one step is required"})
        continue
      missing = [step for step in steps if step not in relationships_by_id]
      if missing:
        errors.append({"subject": f"{flow_subject}.steps", "message": f"unknown relationship ids: {missing}"})
        continue
      if len(steps) != len(set(steps)):
        errors.append({"subject": f"{flow_subject}.steps", "message": "step relationship ids must be unique"})
      if not isinstance(entry, str):
        continue
      reachable = {entry}
      for step in steps:
        relationship = relationships_by_id[step]
        if relationship.get("source") not in reachable:
          errors.append({
            "subject": f"{flow_subject}.steps",
            "message": f"{step} starts from a component not yet reached in this flow",
          })
          break
        reachable.add(relationship.get("target"))
      depth = flow_depth(entry, steps, relationships_by_id)
      if depth > MAX_DEPTH:
        errors.append({
          "subject": f"{flow_subject}.steps",
          "message": f"flow depth {depth} exceeds the {MAX_DEPTH} layer limit",
        })
      elif depth < 2:
        warnings.append({"subject": flow_subject, "message": "flow has no downstream step"})


def validate_layout(layout: Any, component_ids: set[str], errors: list[dict[str, str]]) -> None:
  if layout is None:
    return
  if not isinstance(layout, dict):
    errors.append({"subject": "layout", "message": "layout must be an object"})
    return
  for view, positions in layout.items():
    subject = f"layout[{view}]"
    if not isinstance(positions, dict):
      errors.append({"subject": subject, "message": "view layout must be an object"})
      continue
    for component_id, position in positions.items():
      if component_id not in component_ids:
        errors.append({"subject": f"{subject}.{component_id}", "message": "unknown component id"})
        continue
      if not isinstance(position, dict) or set(position) != {"x", "y"}:
        errors.append({"subject": f"{subject}.{component_id}", "message": "position needs exactly x and y"})
        continue
      if any(not isinstance(value, (int, float)) or isinstance(value, bool) for value in position.values()):
        errors.append({"subject": f"{subject}.{component_id}", "message": "x and y must be numbers"})


def validate_analysis(data: Any, repo_root: Path | None = None) -> dict[str, Any]:
  errors: list[dict[str, str]] = []
  warnings: list[dict[str, str]] = []
  if not isinstance(data, dict):
    return {"ok": False, "errors": [{"subject": "$", "message": "root must be an object"}], "warnings": []}

  allowed_top = {
    "schema_version", "project", "summary", "related_project_ids",
    "businesses", "apis", "components", "relationships", "layout",
  }
  unknown_top = set(data) - allowed_top
  if unknown_top:
    errors.append({"subject": "$", "message": f"unknown fields: {sorted(unknown_top)}"})
  if data.get("schema_version") != SCHEMA_VERSION:
    errors.append({"subject": "schema_version", "message": f"must be {SCHEMA_VERSION}"})

  project = data.get("project")
  project_allowed = {
    "id", "name", "root_path", "remote", "analyzed_commit", "analyzed_at", "worktree_fingerprint"
  }
  if not isinstance(project, dict):
    errors.append({"subject": "project", "message": "project must be an object"})
    project = {}
  else:
    unknown_project = set(project) - project_allowed
    if unknown_project:
      errors.append({"subject": "project", "message": f"unknown fields: {sorted(unknown_project)}"})
  for field in ("id", "name", "root_path", "analyzed_commit", "analyzed_at", "worktree_fingerprint"):
    if not isinstance(project.get(field), str) or not project.get(field):
      errors.append({"subject": f"project.{field}", "message": "non-empty string required"})
  if project.get("id") and not ID_PATTERN.fullmatch(project["id"]):
    errors.append({"subject": "project.id", "message": "invalid identifier"})
  if project.get("remote") is not None and not isinstance(project.get("remote"), str):
    errors.append({"subject": "project.remote", "message": "must be a string or null"})
  if not isinstance(data.get("summary"), str) or not data.get("summary", "").strip():
    errors.append({"subject": "summary", "message": "non-empty string required"})

  related = data.get("related_project_ids", [])
  if not isinstance(related, list) or any(not isinstance(item, str) or not ID_PATTERN.fullmatch(item) for item in related):
    errors.append({"subject": "related_project_ids", "message": "must contain valid project ids"})
  elif len(related) != len(set(related)):
    errors.append({"subject": "related_project_ids", "message": "project ids must be unique"})

  components = data.get("components")
  component_ids: set[str] = set()
  if not isinstance(components, list) or not components:
    errors.append({"subject": "components", "message": "at least one component is required"})
    components = []
  component_allowed = {
    "id", "name", "kind", "layer", "origin", "capacity",
    "role", "importance", "owned_paths", "evidence",
  }
  for index, component in enumerate(components):
    subject = f"components[{index}]"
    if not isinstance(component, dict):
      errors.append({"subject": subject, "message": "component must be an object"})
      continue
    unknown = set(component) - component_allowed
    if unknown:
      errors.append({"subject": subject, "message": f"unknown fields: {sorted(unknown)}"})
    component_id = component.get("id")
    if not isinstance(component_id, str) or not ID_PATTERN.fullmatch(component_id):
      errors.append({"subject": f"{subject}.id", "message": "invalid identifier"})
    elif component_id in component_ids:
      errors.append({"subject": f"{subject}.id", "message": "duplicate component id"})
    else:
      component_ids.add(component_id)
    for field in ("name", "role"):
      if not isinstance(component.get(field), str) or not component.get(field, "").strip():
        errors.append({"subject": f"{subject}.{field}", "message": "non-empty string required"})
    if component.get("kind") not in COMPONENT_KINDS:
      errors.append({"subject": f"{subject}.kind", "message": f"must be one of {sorted(COMPONENT_KINDS)}"})
    if component.get("layer") not in LAYER_INDEX:
      errors.append({"subject": f"{subject}.layer", "message": f"must be one of {LAYERS}"})
    validate_origin(component.get("origin"), f"{subject}.origin", errors)
    validate_capacity(component.get("capacity"), f"{subject}.capacity", errors)
    if component.get("importance") not in IMPORTANCE_VALUES:
      errors.append({"subject": f"{subject}.importance", "message": "must be core or supporting"})
    owned_paths = component.get("owned_paths")
    if not isinstance(owned_paths, list) or any(not isinstance(path, str) or not valid_relative_path(path) for path in owned_paths):
      errors.append({"subject": f"{subject}.owned_paths", "message": "must contain project-relative paths"})
    validate_evidence(component.get("evidence"), subject, repo_root, errors)

  relationships = data.get("relationships")
  relationship_ids: set[str] = set()
  if not isinstance(relationships, list):
    errors.append({"subject": "relationships", "message": "relationships must be an array"})
    relationships = []
  relationship_allowed = {
    "id", "source", "target", "target_project_id", "kind", "label",
    "api", "details", "load", "evidence",
  }
  for index, relationship in enumerate(relationships):
    subject = f"relationships[{index}]"
    if not isinstance(relationship, dict):
      errors.append({"subject": subject, "message": "relationship must be an object"})
      continue
    unknown = set(relationship) - relationship_allowed
    if unknown:
      errors.append({"subject": subject, "message": f"unknown fields: {sorted(unknown)}"})
    relationship_id = relationship.get("id")
    if not isinstance(relationship_id, str) or not ID_PATTERN.fullmatch(relationship_id):
      errors.append({"subject": f"{subject}.id", "message": "invalid identifier"})
    elif relationship_id in relationship_ids:
      errors.append({"subject": f"{subject}.id", "message": "duplicate relationship id"})
    else:
      relationship_ids.add(relationship_id)
    source = relationship.get("source")
    target = relationship.get("target")
    target_project_id = relationship.get("target_project_id")
    if source not in component_ids:
      errors.append({"subject": f"{subject}.source", "message": "source component not found"})
    if target_project_id is None and target not in component_ids:
      errors.append({"subject": f"{subject}.target", "message": "target component not found"})
    if target_project_id is not None:
      if not isinstance(target_project_id, str) or not ID_PATTERN.fullmatch(target_project_id):
        errors.append({"subject": f"{subject}.target_project_id", "message": "invalid project id"})
      if not isinstance(target, str) or not ID_PATTERN.fullmatch(target):
        errors.append({"subject": f"{subject}.target", "message": "invalid cross-project component id"})
    if relationship.get("kind") not in RELATIONSHIP_KINDS:
      errors.append({"subject": f"{subject}.kind", "message": f"must be one of {sorted(RELATIONSHIP_KINDS)}"})
    if not isinstance(relationship.get("label"), str) or not relationship.get("label", "").strip():
      errors.append({"subject": f"{subject}.label", "message": "non-empty string required"})
    details = relationship.get("details", {})
    if not isinstance(details, dict):
      errors.append({"subject": f"{subject}.details", "message": "must be an object"})
    elif set(details) - DETAIL_FIELDS:
      errors.append({"subject": f"{subject}.details", "message": f"unknown fields: {sorted(set(details) - DETAIL_FIELDS)}"})
    elif any(not isinstance(value, str) or not value.strip() for value in details.values()):
      errors.append({"subject": f"{subject}.details", "message": "detail values must be non-empty strings"})
    validate_load(relationship.get("load"), f"{subject}.load", errors)
    validate_evidence(relationship.get("evidence"), subject, repo_root, errors)

  businesses = data.get("businesses", [])
  validate_businesses(businesses, component_ids, relationships, errors, warnings)
  flow_ids = {
    flow.get("id")
    for business in businesses if isinstance(business, dict)
    for flow in business.get("flows", []) if isinstance(flow, dict)
  }
  apis = data.get("apis", [])
  api_ids = validate_apis(apis, component_ids, flow_ids, errors, warnings)
  for index, relationship in enumerate(relationships):
    if not isinstance(relationship, dict):
      continue
    api_ref = relationship.get("api")
    if api_ref is not None and api_ref not in api_ids:
      errors.append({"subject": f"relationships[{index}].api", "message": "api not found"})
  validate_layout(data.get("layout"), component_ids, errors)

  if not any(component.get("importance") == "core" for component in components if isinstance(component, dict)):
    warnings.append({"subject": "components", "message": "no core component; the initial HTML view may be empty"})
  if isinstance(businesses, list) and not businesses:
    warnings.append({"subject": "businesses", "message": "no business flow; the business view will be empty"})
  flow_count = sum(
    len(business.get("flows", []))
    for business in businesses
    if isinstance(business, dict) and isinstance(business.get("flows"), list)
  )
  return {
    "ok": not errors,
    "errors": errors,
    "warnings": warnings,
    "counts": {
      "businesses": len(businesses) if isinstance(businesses, list) else 0,
      "flows": flow_count,
      "apis": len(apis) if isinstance(apis, list) else 0,
      "components": len(components),
      "relationships": len(relationships),
      "components_with_capacity": sum(
        1 for component in components
        if isinstance(component, dict) and isinstance(component.get("capacity"), dict)
      ),
    },
  }


def normalize_analysis(data: dict[str, Any], root: Path) -> dict[str, Any]:
  identity = project_identity(root)
  normalized = json.loads(json.dumps(data))
  project = normalized.setdefault("project", {})
  project.update(identity)
  project["analyzed_commit"] = git_head(root) or "unversioned"
  project["analyzed_at"] = utc_now()
  project["worktree_fingerprint"] = worktree_fingerprint(root)
  normalized.setdefault("related_project_ids", [])
  normalized.setdefault("businesses", [])
  normalized.setdefault("apis", [])
  normalized.setdefault("layout", {})
  return normalized


def registry_analysis_paths(main_path: Path, project_ids: list[str]) -> list[Path]:
  registry_path = main_path.parent.parent.parent / "projects.json"
  registry = load_json(registry_path) or {}
  entries = registry.get("projects", []) if isinstance(registry, dict) else []
  by_id = {
    entry.get("id", entry.get("project_id")): entry
    for entry in entries
    if isinstance(entry, dict)
  }
  paths: list[Path] = []
  for project_id in project_ids:
    entry = by_id.get(project_id)
    if not entry:
      continue
    path = Path(entry.get("analysis_path", ""))
    if path.is_file():
      paths.append(path)
  return paths


def load_analysis_bundle(main_path: Path) -> list[dict[str, Any]]:
  main = load_json(main_path)
  if main is None:
    raise ValueError(f"invalid analysis JSON: {main_path}")
  related_ids = main.get("related_project_ids", [])
  related_paths = registry_analysis_paths(main_path, related_ids if isinstance(related_ids, list) else [])
  bundle = [main]
  for path in related_paths:
    data = load_json(path)
    if data:
      bundle.append(data)
  return bundle


def analysis_status(root: Path) -> dict[str, Any]:
  identity = register_project(root)
  paths = project_paths(root)
  data = load_json(paths["analysis"])
  head = git_head(root)
  current_fingerprint = worktree_fingerprint(root)
  if data is None:
    return {
      "mode": "initial",
      "project": identity,
      "paths": {key: str(value) for key, value in paths.items()},
      "head_commit": head,
      "stale": None,
      "changed_files": [],
      "affected_component_ids": [],
      "affected_flow_ids": [],
      "unmapped_changed_files": [],
      "drawio_exists": paths["drawio"].exists(),
      "legacy_store_detected": (paths["project_dir"] / "graph.sqlite").exists()
      or (paths["project_dir"] / "wiki").exists(),
    }
  if data.get("schema_version") != SCHEMA_VERSION:
    return {
      "mode": "full",
      "reason": f"stored schema_version {data.get('schema_version')} != {SCHEMA_VERSION}",
      "project": identity,
      "paths": {key: str(value) for key, value in paths.items()},
      "head_commit": head,
      "analyzed_commit": data.get("project", {}).get("analyzed_commit"),
      "stale": True,
      "changed_files": [],
      "affected_component_ids": [],
      "affected_flow_ids": [],
      "unmapped_changed_files": [],
      "drawio_exists": paths["drawio"].exists(),
    }
  analyzed = data.get("project", {}).get("analyzed_commit")
  analyzed_fingerprint = data.get("project", {}).get("worktree_fingerprint")
  history_available = (
    analyzed == "unversioned" and head is None
  ) or (
    isinstance(analyzed, str)
    and analyzed != "unversioned"
    and git_commit_exists(root, analyzed)
  )
  changed = changed_files(root, analyzed if history_available and analyzed != "unversioned" else None)
  stale = analyzed != (head or "unversioned") or analyzed_fingerprint != current_fingerprint
  affected, unmapped, flows = affected_components(data, changed)
  return {
    "mode": "full" if stale and not history_available else "incremental" if stale else "reuse",
    "project": identity,
    "paths": {key: str(value) for key, value in paths.items()},
    "head_commit": head,
    "analyzed_commit": analyzed,
    "stale": stale,
    "history_available": history_available,
    "changed_files": changed,
    "affected_component_ids": affected,
    "affected_flow_ids": flows,
    "unmapped_changed_files": unmapped,
    "drawio_exists": paths["drawio"].exists(),
    "legacy_store_detected": (paths["project_dir"] / "graph.sqlite").exists()
    or (paths["project_dir"] / "wiki").exists(),
    "related_project_ids": data.get("related_project_ids", []),
  }
