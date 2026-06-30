import shutil
import subprocess
import unittest
import os
import tempfile
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]


class WorkspaceContractTests(unittest.TestCase):
    def test_new_workspace_declares_scenario_boundary_and_agent_amplification(self):
        test_root = LAB_ROOT / ".tmp" / "tests"
        test_root.mkdir(parents=True, exist_ok=True)
        tmp_root = Path(tempfile.mkdtemp(prefix="workspace-contract-", dir=test_root))
        self.addCleanup(shutil.rmtree, tmp_root, ignore_errors=True)
        env = os.environ.copy()
        env["WORKSPACE_ROOT"] = str(tmp_root)

        result = subprocess.run(
            [str(LAB_ROOT / "scripts" / "new-workspace"), "contract-test"],
            cwd=LAB_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        workspace = Path(result.stdout.strip().splitlines()[-1])
        self.addCleanup(shutil.rmtree, workspace, ignore_errors=True)

        self.assertTrue(workspace.is_dir())
        self.assertEqual(workspace.parent, tmp_root)

        agents_text = (workspace / "AGENTS.md").read_text(encoding="utf-8")
        claude_text = (workspace / "CLAUDE.md").read_text(encoding="utf-8")
        package_readme_text = (workspace / "agents" / "README.md").read_text(encoding="utf-8")
        brief_text = (workspace / "brief.md").read_text(encoding="utf-8")
        gitignore_text = (workspace / ".gitignore").read_text(encoding="utf-8")

        self.assertIn("## Rule Inheritance", agents_text)
        self.assertIn("## Scenario Boundary", agents_text)
        self.assertIn("## Codex Claude Amplification", agents_text)
        self.assertIn("docs/rule-inheritance.md", agents_text)
        self.assertIn("Root lab `CLAUDE.md`", claude_text)
        self.assertIn("package-local", claude_text)
        self.assertIn("small agent package", package_readme_text)
        self.assertIn("Scenario type: TBD", brief_text)
        self.assertIn("Codex/Claude amplification", brief_text)
        self.assertIn("Rule inheritance", brief_text)
        self.assertIn(".omx/", gitignore_text)
        self.assertIn(".codex-home/auth.json", gitignore_text)

    def test_new_workspace_rejects_roots_outside_lab(self):
        outside_root = LAB_ROOT.parent / "codex-agent-lab-outside-workspace-test"
        shutil.rmtree(outside_root, ignore_errors=True)
        self.addCleanup(shutil.rmtree, outside_root, ignore_errors=True)
        env = os.environ.copy()
        env["WORKSPACE_ROOT"] = str(outside_root)

        result = subprocess.run(
            [str(LAB_ROOT / "scripts" / "new-workspace"), "outside-test"],
            cwd=LAB_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("WORKSPACE_ROOT must stay inside the lab root", result.stderr)
        self.assertFalse(outside_root.exists())


if __name__ == "__main__":
    unittest.main()
