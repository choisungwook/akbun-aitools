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

from analysis_artifacts import render_drawio, render_html  # noqa: E402
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
    (self.repo / "deploy").mkdir()
    (self.repo / "services/order-api/main.go").write_text(
      "package main\n" * 17 + "func main() {}\n",
      encoding="utf-8",
    )
    (self.repo / "services/order-api/repository/order.go").write_text(
      "package repository\n" * 41 + "func insertOrder() {}\n" * 7,
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
      "schema_version": 1,
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
      "components": [
        {
          "id": "order-api",
          "name": "Order API",
          "kind": "service",
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
          "id": "orders-db",
          "name": "Orders DB",
          "kind": "datastore",
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
          "id": "order-api-writes-orders-db",
          "source": "order-api",
          "target": "orders-db",
          "kind": "db-write",
          "label": "주문 저장",
          "details": {"database": "orders", "table": "orders"},
          "evidence": [
            {
              "path": "services/order-api/repository/order.go",
              "line": 42,
              "end_line": 48,
              "description": "주문 INSERT",
            }
          ],
        }
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

  def test_html_and_drawio_are_self_contained_and_editable(self) -> None:
    data = self.analysis()
    document = render_html([data])
    self.assertIn("analysis-data", document)
    self.assertNotIn("https://", document)
    self.assertIn("supporting 표시", document)
    drawio = render_drawio([data])
    root = ET.fromstring(drawio)
    self.assertEqual(root.tag, "mxfile")
    self.assertEqual(root.attrib["compressed"], "false")
    self.assertEqual(len(root.findall(".//mxCell[@vertex='1']")), 2)
    self.assertEqual(len(root.findall(".//mxCell[@edge='1']")), 1)
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
    self.assertEqual(status["affected_component_ids"], ["order-api"])
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
    self.assertEqual(receipt["possible_affected"][0]["name"], "Order API")

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
      "schema_version": 1,
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
      "components": [{
        "id": "payment-api",
        "name": "Payment API",
        "kind": "service",
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


if __name__ == "__main__":
  unittest.main()
