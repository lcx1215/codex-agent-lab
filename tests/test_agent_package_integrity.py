import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP_ROOT = LAB_ROOT / ".tmp" / "tests"


def temp_lab() -> Path:
    TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="agent-package-lab-", dir=TEST_TMP_ROOT))
    package = root / "workspaces" / "demo" / "agents" / "support"
    package.mkdir(parents=True)
    manifest = {
        "id": "support/triage",
        "name": "Triage",
        "version": 1,
    }
    (package / "triage.agent.json").write_text(json.dumps(manifest), encoding="utf-8")
    registry = {
        "version": 1,
        "agent_packages": [
            {"id": "support", "path": "agents/support", "entry_agent": "support/triage"}
        ],
        "agents": [
            {
                "id": "support/triage",
                "package": "support",
                "path": "agents/support/triage.agent.json",
                "role": "Routes support requests.",
            }
        ],
    }
    (root / "workspaces" / "demo" / "agents" / "registry.json").write_text(
        json.dumps(registry),
        encoding="utf-8",
    )
    return root


def add_nested_subagent_registry(root: Path) -> None:
    nested_package = root / "workspaces" / "demo" / "agents" / "support" / "subagents" / "refund"
    nested_package.mkdir(parents=True)
    manifest = {
        "id": "refund/approver",
        "name": "Refund Approver",
        "version": 1,
    }
    (nested_package / "approver.agent.json").write_text(json.dumps(manifest), encoding="utf-8")
    registry = {
        "version": 1,
        "default_agent": "refund/approver",
        "agent_packages": [
            {"id": "refund", "path": "subagents/refund", "entry_agent": "refund/approver"}
        ],
        "agents": [
            {
                "id": "refund/approver",
                "package": "refund",
                "path": "subagents/refund/approver.agent.json",
                "role": "Approves refund decisions inside the parent agent package.",
            }
        ],
    }
    (root / "workspaces" / "demo" / "agents" / "support" / "subagents" / "registry.json").write_text(
        json.dumps(registry),
        encoding="utf-8",
    )


def run_check(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(LAB_ROOT / "scripts" / "check-agent-packages"), "--root", str(root), "--json"],
        cwd=LAB_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class AgentPackageIntegrityTests(unittest.TestCase):
    def test_valid_registry_and_manifest_pass(self):
        root = temp_lab()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)

        result = run_check(root)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["summary"]["package_count"], 1)
        self.assertEqual(report["summary"]["agent_count"], 1)

    def test_unregistered_manifest_fails(self):
        root = temp_lab()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        extra = {"id": "support/billing", "name": "Billing", "version": 1}
        (root / "workspaces" / "demo" / "agents" / "support" / "billing.agent.json").write_text(
            json.dumps(extra),
            encoding="utf-8",
        )

        result = run_check(root)

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("AGENT_MANIFEST_UNREGISTERED", codes)

    def test_manifest_id_mismatch_fails(self):
        root = temp_lab()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        bad = {"id": "support/not-triage", "name": "Triage", "version": 1}
        (root / "workspaces" / "demo" / "agents" / "support" / "triage.agent.json").write_text(
            json.dumps(bad),
            encoding="utf-8",
        )

        result = run_check(root)

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("AGENT_MANIFEST_ID_MISMATCH", codes)

    def test_nested_subagent_registry_passes(self):
        root = temp_lab()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        add_nested_subagent_registry(root)

        result = run_check(root)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["summary"]["registry_count"], 2)
        self.assertEqual(report["summary"]["package_count"], 2)
        self.assertEqual(report["summary"]["agent_count"], 2)

    def test_nested_subagent_without_registry_fails(self):
        root = temp_lab()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        nested_package = root / "workspaces" / "demo" / "agents" / "support" / "subagents" / "refund"
        nested_package.mkdir(parents=True)
        manifest = {"id": "refund/approver", "name": "Refund Approver", "version": 1}
        (nested_package / "approver.agent.json").write_text(json.dumps(manifest), encoding="utf-8")

        result = run_check(root)

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("AGENT_REGISTRY_MISSING", codes)


if __name__ == "__main__":
    unittest.main()
