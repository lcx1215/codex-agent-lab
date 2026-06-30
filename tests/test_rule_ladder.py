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
    root = Path(tempfile.mkdtemp(prefix="rule-ladder-lab-", dir=TEST_TMP_ROOT))
    (root / "docs").mkdir()
    (root / "workspaces" / "demo" / "agents" / "demo-agent").mkdir(parents=True)
    root_rule = "Rule Inheritance\nParent lab rules still apply.\n"
    for rel in (
        "AGENTS.md",
        "CLAUDE.md",
        "docs/environment-layering.md",
        "docs/codex-claude-collaboration-protocol.md",
    ):
        (root / rel).write_text(root_rule, encoding="utf-8")
    (root / "docs" / "rule-inheritance.md").write_text(
        "# Rule Inheritance Contract\n\n## Effective Rule Chain\n", encoding="utf-8"
    )
    (root / "workspaces" / "demo" / "AGENTS.md").write_text(
        "# Workspace Rules\n\n## Rule Inheritance\n\nParent lab rules still apply.\n",
        encoding="utf-8",
    )
    (root / "workspaces" / "demo" / "agents" / "demo-agent" / "README.md").write_text(
        "# Demo Agent\n\n## Rule Inheritance\n\nParent lab rules still apply.\n",
        encoding="utf-8",
    )
    return root


def add_nested_subagent(root: Path, *, with_rule_marker: bool) -> Path:
    nested = root / "workspaces" / "demo" / "agents" / "demo-agent" / "subagents" / "reviewer"
    nested.mkdir(parents=True)
    text = "# Reviewer\n\n## Rule Inheritance\n\nParent lab rules still apply.\n"
    if not with_rule_marker:
        text = "# Reviewer\n\nLocal notes only.\n"
    (nested / "README.md").write_text(text, encoding="utf-8")
    (nested / "reviewer.agent.json").write_text(
        json.dumps({"id": "reviewer/check", "name": "Reviewer", "version": 1}),
        encoding="utf-8",
    )
    return nested


def run_ladder(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(LAB_ROOT / "scripts" / "check-rule-ladder"), "--root", str(root), "--json"],
        cwd=LAB_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class RuleLadderTests(unittest.TestCase):
    def test_complete_ladder_passes(self):
        root = temp_lab()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)

        result = run_ladder(root)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["summary"]["failed_count"], 0)
        self.assertEqual(report["summary"]["workspace_count"], 1)
        self.assertEqual(report["summary"]["package_count"], 1)

    def test_missing_workspace_ladder_fails(self):
        root = temp_lab()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        (root / "workspaces" / "demo" / "AGENTS.md").unlink()

        result = run_ladder(root)

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "fail")
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("RULE_LADDER_MISSING_SURFACE", codes)

    def test_package_without_parent_ladder_marker_fails(self):
        root = temp_lab()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        package_readme = root / "workspaces" / "demo" / "agents" / "demo-agent" / "README.md"
        package_readme.write_text("# Demo Agent\n\nLocal notes only.\n", encoding="utf-8")

        result = run_ladder(root)

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "fail")
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("RULE_LADDER_PACKAGE_UNDECLARED", codes)

    def test_nested_subagent_with_parent_ladder_marker_passes(self):
        root = temp_lab()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        add_nested_subagent(root, with_rule_marker=True)

        result = run_ladder(root)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["summary"]["agent_unit_count"], 2)

    def test_nested_subagent_without_parent_ladder_marker_fails(self):
        root = temp_lab()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        add_nested_subagent(root, with_rule_marker=False)

        result = run_ladder(root)

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("RULE_LADDER_PACKAGE_UNDECLARED", codes)


if __name__ == "__main__":
    unittest.main()
