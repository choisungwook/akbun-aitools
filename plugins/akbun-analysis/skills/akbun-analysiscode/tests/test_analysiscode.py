from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from analysis_artifacts import flatten_bundle, render_drawio, render_html  # noqa: E402
from analysis_common import analysis_status, project_paths, validate_analysis  # noqa: E402


class AnalysisCodeTest(unittest.TestCase):
  def setUp(self) -> None:
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.base = Path(self.temp.name)
    self.repo = self.base / "order-platform"
    self.store = self.base / "store"
    self.repo.mkdir()
    (self.repo / "services/order-api/repository").mkdir(parents=True)
    (self.repo / "internal/order/usecase").mkdir(parents=True)
    (self.repo / "deploy").mkdir()
    (self.repo / "services/order-api/main.go").write_text(
      "package main\n" * 17 + "func main() {}\n",
      encoding="utf-8",
    )
    (self.repo / "services/order-api/repository/order.go").write_text(
      "package repository\n" * 41 + "func insertOrder() {}\n" * 7,
      encoding="utf-8",
    )
    (self.repo / "internal/order/usecase/place_order.go").write_text(
      "package usecase\n" * 23 + "func PlaceOrder() {}\n" * 5,
      encoding="utf-8",
    )
    (self.repo / "deploy/docker-compose.yml").write_text(
      "services:\n" + "  # filler\n" * 29 + "  orders-db:\n",
      encoding="utf-8",
    )
    self.git("init")
    self.git("config", "user.email", "test@example.com")
    self.git("config", "user.name", "Test")
    self.git("add", ".")
    self.git("commit", "-m", "initial")
    self.previous_home = os.environ.get("AKBUN_ANALYSIS_HOME")
    os.environ["AKBUN_ANALYSIS_HOME"] = str(self.store)
    self.addCleanup(self.restore_environment)

  def restore_environment(self) -> None:
    if self.previous_home is None:
      os.environ.pop("AKBUN_ANALYSIS_HOME", None)
    else:
      os.environ["AKBUN_ANALYSIS_HOME"] = self.previous_home

  def git(self, *args: str) -> str:
    result = subprocess.run(
      ["git", "-C", str(self.repo), *args],
      capture_output=True,
      text=True,
      check=True,
    )
    return result.stdout.strip()

  def analysis(self) -> dict:
    return {
      "schema_version": 2,
      "project": {
        "id": "pending-project",
        "name": "order-platform",
        "root_path": str(self.repo),
        "remote": None,
        "analyzed_commit": "pending",
        "analyzed_at": "pending",
        "worktree_fingerprint": "pending",
      },
      "summary": "주문을 접수하고 저장한다.",
      "related_project_ids": [],
      "businesses": [
        {
          "id": "order",
          "name": "주문",
          "description": "주문을 접수하고 확정한다.",
          "flows": [
            {
              "id": "order.create",
              "name": "주문 생성",
              "description": "주문 요청을 받아 저장한다.",
              "trigger": "POST /orders",
              "entry": "order-api",
              "steps": ["order-api-calls-place-order", "place-order-writes-orders-db"],
            }
          ],
        }
      ],
      "apis": [
        {
          "id": "post-orders",
          "name": "주문 생성",
          "protocol": "http",
          "method": "POST",
          "path": "/orders",
          "provider": "order-api",
          "entrypoint": True,
          "flow_ids": ["order.create"],
          "evidence": [
            {
              "path": "services/order-api/main.go",
              "line": 5,
              "description": "POST /orders 라우트",
            }
          ],
        }
      ],
      "components": [
        {
          "id": "order-api",
          "name": "Order API",
          "kind": "service",
          "layer": "entrypoint",
          "origin": {"type": "git", "label": "order-platform"},
          "capacity": {
            "replicas": 3,
            "cpu_millicores": 1000,
            "memory_mib": 1024,
            "source": "manifest",
          },
          "role": "주문을 접수한다.",
          "importance": "core",
          "owned_paths": ["services/order-api"],
          "evidence": [
            {
              "path": "services/order-api/main.go",
              "line": 18,
              "description": "서버 엔트리포인트",
            }
          ],
        },
        {
          "id": "place-order",
          "name": "주문 확정 유스케이스",
          "kind": "module",
          "layer": "application",
          "origin": {"type": "code", "label": "internal/order/usecase"},
          "role": "주문 확정 여부를 결정한다.",
          "importance": "core",
          "owned_paths": ["internal/order/usecase"],
          "evidence": [
            {
              "path": "internal/order/usecase/place_order.go",
              "line": 24,
              "description": "PlaceOrder 유스케이스",
            }
          ],
        },
        {
          "id": "orders-db",
          "name": "Orders DB",
          "kind": "datastore",
          "layer": "external",
          "origin": {"type": "database", "engine": "rds", "label": "orders"},
          "role": "주문 상태를 저장한다.",
          "importance": "core",
          "owned_paths": ["deploy"],
          "evidence": [
            {
              "path": "deploy/docker-compose.yml",
              "line": 31,
              "description": "DB 정의",
            }
          ],
        },
      ],
      "relationships": [
        {
          "id": "order-api-calls-place-order",
          "source": "order-api",
          "target": "place-order",
          "kind": "code-call",
          "label": "주문 확정 요청",
          "details": {"function": "PlaceOrder"},
          "evidence": [
            {
              "path": "services/order-api/main.go",
              "line": 12,
              "description": "PlaceOrder 호출",
            }
          ],
        },
        {
          "id": "place-order-writes-orders-db",
          "source": "place-order",
          "target": "orders-db",
          "kind": "db-write",
          "label": "주문 저장",
          "details": {"database": "orders", "table": "orders"},
          "load": {
            "fan_out": 4,
            "fan_out_note": "주문 항목마다 INSERT 를 반복한다.",
            "sync": True,
            "crypto": "tls",
          },
          "evidence": [
            {
              "path": "services/order-api/repository/order.go",
              "line": 42,
              "end_line": 48,
              "description": "주문 INSERT",
            }
          ],
        },
      ],
    }

  def run_script(self, name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
      [sys.executable, str(SCRIPTS / name), *args],
      capture_output=True,
      text=True,
      env={**os.environ, "AKBUN_ANALYSIS_HOME": str(self.store)},
      check=False,
    )

  def test_validation_checks_real_evidence_ranges(self) -> None:
    data = self.analysis()
    receipt = validate_analysis(data, self.repo)
    self.assertTrue(receipt["ok"], receipt)
    data["relationships"][0]["evidence"][0]["line"] = 99
    receipt = validate_analysis(data, self.repo)
    self.assertFalse(receipt["ok"])
    self.assertTrue(any("exceeds" in error["message"] for error in receipt["errors"]))

  def test_business_and_service_views_are_built(self) -> None:
    graph = flatten_bundle([self.analysis()])
    service = graph["views"]["service"]
    # 서비스 화면은 module 을 접어 order-api -> orders-db 한 줄만 남긴다.
    self.assertEqual(len(service["nodes"]), 2)
    self.assertEqual(len(service["edges"]), 1)
    edge = service["edges"][0]
    self.assertTrue(edge["derived"])
    self.assertEqual(edge["kind"], "db-write")
    self.assertEqual(len(edge["relationship_uids"]), 2)

    flow_view = next(view for key, view in graph["views"].items() if key.startswith("flow:"))
    self.assertEqual(flow_view["depth"], 3)
    self.assertEqual([edge["step"] for edge in flow_view["edges"]], [1, 2])
    self.assertEqual(len(graph["businesses"][0]["flows"]), 1)

  def test_api_view_and_load_inputs(self) -> None:
    graph = flatten_bundle([self.analysis()])
    api_view = graph["views"]["api"]
    self.assertEqual(len(api_view["edges"]), 0)  # 이 예제에는 API 를 부르는 관계가 없다
    self.assertEqual(graph["apis"][0]["address"], "POST /orders")
    self.assertTrue(graph["apis"][0]["entrypoint"])

    # 부하 화면은 서비스 화면과 같은 위상을 쓰고 접힌 관계의 fan-out 은 곱해진다.
    load_view = graph["views"]["load"]
    self.assertEqual(load_view["nodes"], graph["views"]["service"]["nodes"])
    self.assertEqual(load_view["edges"][0]["load"]["fan_out"], 4)
    self.assertEqual(load_view["edges"][0]["load"]["crypto"], "tls")
    order_api = next(item for item in graph["components"] if item["id"] == "order-api")
    self.assertEqual(order_api["capacity"]["source"], "manifest")

  def test_fan_out_above_one_needs_a_note(self) -> None:
    data = self.analysis()
    data["relationships"][1]["load"] = {"fan_out": 4}
    receipt = validate_analysis(data, self.repo)
    self.assertFalse(receipt["ok"])
    self.assertTrue(any("what repeats the call" in error["message"] for error in receipt["errors"]))

    data = self.analysis()
    data["apis"][0]["provider"] = "missing-service"
    receipt = validate_analysis(data, self.repo)
    self.assertFalse(receipt["ok"])
    self.assertTrue(any("provider component not found" in error["message"] for error in receipt["errors"]))

  def test_flow_depth_and_step_order_are_validated(self) -> None:
    data = self.analysis()
    flow = data["businesses"][0]["flows"][0]
    flow["steps"] = list(reversed(flow["steps"]))
    receipt = validate_analysis(data, self.repo)
    self.assertFalse(receipt["ok"])
    self.assertTrue(any("not yet reached" in error["message"] for error in receipt["errors"]))

    data = self.analysis()
    data["businesses"][0]["flows"][0]["trigger"] = 42
    receipt = validate_analysis(data, self.repo)
    self.assertFalse(receipt["ok"])
    self.assertTrue(any(error["subject"].endswith(".trigger") for error in receipt["errors"]))

    data = self.analysis()
    data["components"][1]["layer"] = "nowhere"
    receipt = validate_analysis(data, self.repo)
    self.assertFalse(receipt["ok"])
    self.assertTrue(any(error["subject"].endswith(".layer") for error in receipt["errors"]))

    data = self.analysis()
    data["components"][2]["origin"] = {"type": "database", "label": "orders"}
    receipt = validate_analysis(data, self.repo)
    self.assertFalse(receipt["ok"])
    self.assertTrue(any("requires an engine" in error["message"] for error in receipt["errors"]))

  def test_html_and_drawio_are_self_contained_and_editable(self) -> None:
    data = self.analysis()
    document = render_html([data])
    self.assertIn("analysis-data", document)
    self.assertNotIn("https://", document)
    self.assertIn("서비스 관계도", document)
    self.assertIn("주문 생성", document)
    drawio = render_drawio([data])
    root = ET.fromstring(drawio)
    self.assertEqual(root.tag, "mxfile")
    self.assertEqual(root.attrib["compressed"], "false")
    # 서비스 관계도 1장 + 업무 흐름 1장
    self.assertEqual(len(root.findall("diagram")), 2)
    self.assertEqual(len(root.findall(".//mxCell[@edge='1']")), 3)
    if shutil.which("node"):
      script = document.rsplit("<script>", 1)[1].split("</script>", 1)[0]
      result = subprocess.run(
        ["node", "--check", "-"],
        input=script,
        capture_output=True,
        text=True,
        check=False,
      )
      self.assertEqual(result.returncode, 0, result.stderr)

  def test_commit_status_incremental_and_drawio_overwrite(self) -> None:
    candidate = self.base / "candidate.json"
    candidate.write_text(json.dumps(self.analysis(), ensure_ascii=False), encoding="utf-8")
    result = self.run_script("commit_analysis.py", str(self.repo), str(candidate))
    self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
    paths = project_paths(self.repo)
    self.assertTrue(paths["analysis"].is_file())
    self.assertTrue(paths["html"].is_file())
    self.assertFalse(paths["drawio"].exists())

    result = self.run_script("export_drawio.py", str(paths["analysis"]), str(paths["drawio"]))
    self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
    paths["drawio"].write_text("human edit", encoding="utf-8")
    with (self.repo / "services/order-api/main.go").open("a", encoding="utf-8") as stream:
      stream.write("// changed\n")
    unicode_file = self.repo / "services/order-api/주문 메모.md"
    unicode_file.write_text("변경\n", encoding="utf-8")
    status = analysis_status(self.repo)
    self.assertEqual(status["mode"], "incremental")
    self.assertEqual(status["affected_component_ids"], ["order-api", "place-order"])
    self.assertEqual(status["affected_flow_ids"], ["order.create"])
    self.assertIn("services/order-api/주문 메모.md", status["changed_files"])

    current = json.loads(paths["analysis"].read_text(encoding="utf-8"))
    candidate.write_text(json.dumps(current, ensure_ascii=False), encoding="utf-8")
    result = self.run_script("commit_analysis.py", str(self.repo), str(candidate))
    self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
    self.assertTrue(paths["drawio"].read_text(encoding="utf-8").startswith("<?xml"))
    self.assertEqual(analysis_status(self.repo)["mode"], "reuse")
    stored = json.loads(paths["analysis"].read_text(encoding="utf-8"))
    stored["project"]["analyzed_commit"] = "deadbeef"
    paths["analysis"].write_text(json.dumps(stored), encoding="utf-8")
    self.assertEqual(analysis_status(self.repo)["mode"], "full")

  def test_trace_impact_reverses_synchronous_dependency(self) -> None:
    candidate = self.base / "candidate.json"
    candidate.write_text(json.dumps(self.analysis(), ensure_ascii=False), encoding="utf-8")
    result = self.run_script("commit_analysis.py", str(self.repo), str(candidate))
    self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
    analysis_path = project_paths(self.repo)["analysis"]
    result = self.run_script("trace_impact.py", str(analysis_path), "orders-db")
    self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
    receipt = json.loads(result.stdout)
    # DB 가 바뀌면 그 위 계층을 거쳐 진입점까지 거슬러 올라간다.
    self.assertEqual(
      [(item["name"], item["hops"]) for item in receipt["possible_affected"]],
      [("주문 확정 유스케이스", 1), ("Order API", 2)],
    )
    self.assertEqual([item["flow"] for item in receipt["possible_affected_flows"]], ["주문 생성"])

  def test_selected_related_project_is_combined_in_html(self) -> None:
    payment_repo = self.base / "payment-platform"
    (payment_repo / "services/payment-api").mkdir(parents=True)
    (payment_repo / "services/payment-api/main.go").write_text(
      "package main\nfunc main() {}\n",
      encoding="utf-8",
    )
    for args in (
      ("init",),
      ("config", "user.email", "test@example.com"),
      ("config", "user.name", "Test"),
      ("add", "."),
      ("commit", "-m", "initial"),
    ):
      subprocess.run(
        ["git", "-C", str(payment_repo), *args],
        capture_output=True,
        text=True,
        check=True,
      )
    payment_candidate = self.base / "payment.json"
    payment_candidate.write_text(json.dumps({
      "schema_version": 2,
      "project": {
        "id": "pending-payment",
        "name": "payment-platform",
        "root_path": str(payment_repo),
        "remote": None,
        "analyzed_commit": "pending",
        "analyzed_at": "pending",
        "worktree_fingerprint": "pending",
      },
      "summary": "결제 승인을 처리한다.",
      "related_project_ids": [],
      "businesses": [],
      "components": [{
        "id": "payment-api",
        "name": "Payment API",
        "kind": "service",
        "layer": "entrypoint",
        "origin": {"type": "git", "label": "payment-platform"},
        "role": "결제 승인을 처리한다.",
        "importance": "core",
        "owned_paths": ["services/payment-api"],
        "evidence": [{
          "path": "services/payment-api/main.go",
          "line": 2,
          "description": "결제 서버 엔트리포인트",
        }],
      }],
      "relationships": [],
    }), encoding="utf-8")
    result = self.run_script("commit_analysis.py", str(payment_repo), str(payment_candidate))
    self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
    payment_id = json.loads(project_paths(payment_repo)["analysis"].read_text(encoding="utf-8"))["project"]["id"]

    order = self.analysis()
    order["related_project_ids"] = [payment_id]
    order["relationships"].append({
      "id": "order-calls-payment",
      "source": "order-api",
      "target": "payment-api",
      "target_project_id": payment_id,
      "kind": "grpc",
      "label": "결제 승인",
      "details": {"grpc_service": "PaymentService", "grpc_method": "Charge"},
      "evidence": [{
        "path": "services/order-api/repository/order.go",
        "line": 42,
        "description": "PaymentService.Charge 호출",
      }],
    })
    order_candidate = self.base / "order.json"
    order_candidate.write_text(json.dumps(order), encoding="utf-8")
    result = self.run_script("commit_analysis.py", str(self.repo), str(order_candidate))
    self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
    html_output = project_paths(self.repo)["html"].read_text(encoding="utf-8")
    self.assertIn("Payment API", html_output)
    self.assertIn("결제 승인", html_output)

  def test_saved_layout_survives_a_candidate_without_one(self) -> None:
    candidate = self.base / "candidate.json"
    first = self.analysis()
    first["layout"] = {"service": {"order-api": {"x": 400, "y": 120}}}
    candidate.write_text(json.dumps(first, ensure_ascii=False), encoding="utf-8")
    result = self.run_script("commit_analysis.py", str(self.repo), str(candidate))
    self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    # 증분 갱신은 layout 을 아예 넘기지 않는다. 이때 저장된 배치는 남아야 한다.
    incremental = self.analysis()
    self.assertNotIn("layout", incremental)
    candidate.write_text(json.dumps(incremental, ensure_ascii=False), encoding="utf-8")
    result = self.run_script("commit_analysis.py", str(self.repo), str(candidate))
    self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
    stored = json.loads(project_paths(self.repo)["analysis"].read_text(encoding="utf-8"))
    self.assertEqual(stored["layout"], {"service": {"order-api": {"x": 400, "y": 120}}})

    # 빈 layout 을 직접 넣은 candidate 는 배치를 지우겠다는 뜻이므로 되살리지 않는다.
    reset = self.analysis()
    reset["layout"] = {}
    candidate.write_text(json.dumps(reset, ensure_ascii=False), encoding="utf-8")
    result = self.run_script("commit_analysis.py", str(self.repo), str(candidate))
    self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
    stored = json.loads(project_paths(self.repo)["analysis"].read_text(encoding="utf-8"))
    self.assertEqual(stored["layout"], {})

  def test_outdated_schema_forces_full_reanalysis(self) -> None:
    candidate = self.base / "candidate.json"
    candidate.write_text(json.dumps(self.analysis(), ensure_ascii=False), encoding="utf-8")
    self.run_script("commit_analysis.py", str(self.repo), str(candidate))
    paths = project_paths(self.repo)
    stored = json.loads(paths["analysis"].read_text(encoding="utf-8"))
    stored["schema_version"] = 1
    paths["analysis"].write_text(json.dumps(stored, ensure_ascii=False), encoding="utf-8")
    self.assertEqual(analysis_status(self.repo)["mode"], "full")


if __name__ == "__main__":
  unittest.main()
