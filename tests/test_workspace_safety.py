import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP_ROOT = LAB_ROOT / ".tmp" / "tests"


def lab_temp_dir(prefix: str) -> Path:
    TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=TEST_TMP_ROOT))


class WorkspaceSafetyTests(unittest.TestCase):
    def test_current_lab_has_no_workspace_safety_failures(self):
        result = subprocess.run(
            [str(LAB_ROOT / "scripts" / "check-workspace-safety"), "--json"],
            cwd=LAB_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        report = json.loads(result.stdout)

        self.assertIn(report["status"], {"pass", "warn"})
        self.assertEqual(report["summary"]["failed_count"], 0)
        self.assertGreaterEqual(report["summary"]["workspace_count"], 1)

    def test_secret_like_workspace_file_is_a_hard_failure(self):
        root = lab_temp_dir("workspace-safety-lab-")
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        workspace = root / "workspaces" / "bad"
        workspace.mkdir(parents=True)
        (workspace / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
        (workspace / "brief.md").write_text("# Brief\n", encoding="utf-8")
        (workspace / "progress.md").write_text("# Progress\n", encoding="utf-8")
        (workspace / "auth.json").write_text("{}", encoding="utf-8")

        result = subprocess.run(
            [str(LAB_ROOT / "scripts" / "check-workspace-safety"), "--root", str(root), "--json"],
            cwd=LAB_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["summary"]["failed_count"], 1)

    def test_incomplete_workspace_is_warning_not_failure(self):
        root = lab_temp_dir("workspace-safety-lab-")
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        workspace = root / "workspaces" / "active"
        workspace.mkdir(parents=True)
        (workspace / "driver.mjs").write_text("console.log('active')\n", encoding="utf-8")

        result = subprocess.run(
            [str(LAB_ROOT / "scripts" / "check-workspace-safety"), "--root", str(root), "--json"],
            cwd=LAB_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "warn")
        codes = {
            issue["code"]
            for workspace_report in report["workspaces"]
            for issue in workspace_report["issues"]
        }
        self.assertIn("WORKSPACE_SCAFFOLD_INCOMPLETE", codes)

    def test_external_nested_checkout_is_not_deep_scanned(self):
        root = lab_temp_dir("workspace-safety-lab-")
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        workspace = root / "workspaces" / "active"
        external = workspace / "external" / "merchant-portal-refactor"
        external.mkdir(parents=True)
        (external / ".git").mkdir()
        (external / "node_modules").mkdir()
        (external / "local-path.txt").write_text(
            "/Users/example/should/not/be/scanned\n",
            encoding="utf-8",
        )
        (workspace / "AGENTS.md").write_text("# Parent Environment\n", encoding="utf-8")
        (workspace / "brief.md").write_text("# Brief\n", encoding="utf-8")
        (workspace / "progress.md").write_text("# Progress\n", encoding="utf-8")
        (workspace / ".gitignore").write_text("external/\n", encoding="utf-8")
        (workspace / "VALIDATION.md").write_text("# Validation\n", encoding="utf-8")

        result = subprocess.run(
            [str(LAB_ROOT / "scripts" / "check-workspace-safety"), "--root", str(root), "--json"],
            cwd=LAB_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        report = json.loads(result.stdout)
        codes = {
            issue["code"]
            for workspace_report in report["workspaces"]
            for issue in workspace_report["issues"]
        }
        self.assertNotIn("WORKSPACE_MACHINE_LOCAL_PATH", codes)


if __name__ == "__main__":
    unittest.main()
