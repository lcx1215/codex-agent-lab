import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

from waterflow.auditor import (
    build_change_briefs,
    build_markdown_report,
    build_path_index,
    build_route_index,
    build_validation_plan,
    build_validation_results_markdown,
    classify_path_impact,
    diff_path_indexes,
    run_validation_plan,
    scan_lab,
    write_outputs,
)


class WaterflowAuditorTests(unittest.TestCase):
    def make_lab(self) -> Path:
        root = Path(tempfile.mkdtemp(prefix="waterflow-lab-"))
        (root / ".codex" / "agents").mkdir(parents=True)
        (root / ".agents" / "skills" / "demo-skill").mkdir(parents=True)
        (root / "scripts").mkdir()
        (root / "registry").mkdir()
        (root / "waterflow").mkdir()
        (root / "tests").mkdir()
        (root / "docs").mkdir()
        (root / "workspaces" / "demo-task").mkdir(parents=True)
        (root / "outputs" / "shared").mkdir(parents=True)

        (root / "AGENTS.md").write_text("# Rules\nUse registry/current-progress.md.\n", encoding="utf-8")
        (root / "README.md").write_text("# Lab\nAgents in `.codex/agents`.\n", encoding="utf-8")
        (root / ".codex" / "agents" / "good-agent.toml").write_text(
            'name = "good-agent"\n'
            'description = "Checks waterflow."\n'
            'developer_instructions = """Read AGENTS.md and registry/VALIDATION.md."""\n',
            encoding="utf-8",
        )
        (root / ".agents" / "skills" / "demo-skill" / "SKILL.md").write_text(
            "---\n"
            "name: demo-skill\n"
            "description: Use when testing waterflow.\n"
            "---\n"
            "# Demo Skill\n",
            encoding="utf-8",
        )
        script = root / "scripts" / "demo-script"
        script.write_text("#!/usr/bin/env bash\nset -euo pipefail\n", encoding="utf-8")
        script.chmod(script.stat().st_mode | stat.S_IXUSR)
        (root / "waterflow" / "auditor.py").write_text("def demo():\n    return True\n", encoding="utf-8")
        (root / "tests" / "test_demo.py").write_text("def test_demo():\n    assert True\n", encoding="utf-8")
        (root / "docs" / "design.md").write_text("# Design\n", encoding="utf-8")
        (root / "registry" / "VALIDATION.md").write_text("# Validation\n", encoding="utf-8")
        (root / "registry" / "current-progress.md").write_text("# Progress\n", encoding="utf-8")
        return root

    def test_scan_lab_builds_graph_for_core_paths(self):
        root = self.make_lab()

        report = scan_lab(root)

        kinds = {node["kind"] for node in report["graph"]["nodes"]}
        self.assertIn("rules", kinds)
        self.assertIn("readme", kinds)
        self.assertIn("agent", kinds)
        self.assertIn("skill", kinds)
        self.assertIn("script", kinds)
        self.assertIn("registry", kinds)
        self.assertIn("auditor-code", kinds)
        self.assertIn("test", kinds)
        self.assertIn("doc", kinds)
        self.assertIn("workspace", kinds)
        self.assertGreaterEqual(report["summary"]["path_count"], 7)
        self.assertFalse(
            [finding for finding in report["findings"] if finding["severity"] in {"P0", "P1"}]
        )

    def test_scan_lab_flags_agent_missing_required_field(self):
        root = self.make_lab()
        (root / ".codex" / "agents" / "broken-agent.toml").write_text(
            'name = "broken-agent"\n'
            'description = "Missing developer instructions."\n',
            encoding="utf-8",
        )

        report = scan_lab(root)

        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("AGENT_MISSING_FIELD", codes)
        broken = [finding for finding in report["findings"] if finding["code"] == "AGENT_MISSING_FIELD"][0]
        self.assertIn("broken-agent.toml", broken["evidence"][0])
        self.assertIn("developer_instructions", broken["repair_brief"])

    def test_markdown_report_contains_findings_and_repair_briefs(self):
        root = self.make_lab()
        os.remove(root / "registry" / "VALIDATION.md")

        report = scan_lab(root)
        markdown = build_markdown_report(report)

        self.assertIn("# Waterflow Auditor Report", markdown)
        self.assertIn("MISSING_CORE_PATH", markdown)
        self.assertIn("Repair brief", markdown)

    def test_path_index_diff_detects_added_removed_and_changed_paths(self):
        root = self.make_lab()
        before = build_path_index(scan_lab(root))

        (root / "README.md").write_text("# Lab\nUpdated water path.\n", encoding="utf-8")
        (root / ".agents" / "skills" / "new-skill").mkdir()
        (root / ".agents" / "skills" / "new-skill" / "SKILL.md").write_text(
            "---\n"
            "name: new-skill\n"
            "description: Use when testing added paths.\n"
            "---\n"
            "# New Skill\n",
            encoding="utf-8",
        )
        os.remove(root / "scripts" / "demo-script")

        after = build_path_index(scan_lab(root))
        diff = diff_path_indexes(before, after)

        self.assertIn(".agents/skills/new-skill/SKILL.md", diff["added"])
        self.assertIn("scripts/demo-script", diff["removed"])
        self.assertIn("README.md", diff["changed"])
        self.assertGreater(diff["summary"]["unchanged_count"], 0)

    def test_path_impact_classifies_validation_for_key_waterways(self):
        cases = {
            ".codex/agents/waterflow-auditor.toml": ("agent", "P2", "scripts/check-lab"),
            ".agents/skills/waterflow-auditor/SKILL.md": ("skill", "P2", "debug prompt-input"),
            "scripts/waterflow-scan": ("script", "P2", "python3 -m unittest discover -s tests"),
            "registry/VALIDATION.md": ("registry", "P3", "scripts/waterflow-scan"),
            "README.md": ("documentation", "P3", "scripts/waterflow-scan"),
        }

        for path, (expected_kind, expected_risk, expected_check) in cases.items():
            with self.subTest(path=path):
                impact = classify_path_impact(path)
                self.assertEqual(impact["kind"], expected_kind)
                self.assertEqual(impact["risk"], expected_risk)
                self.assertIn(expected_check, "\n".join(impact["recommended_checks"]))

    def test_change_briefs_turn_diff_into_codex_claude_handoffs(self):
        root = self.make_lab()
        before = build_path_index(scan_lab(root))
        (root / ".codex" / "agents" / "good-agent.toml").write_text(
            'name = "good-agent"\n'
            'description = "Checks waterflow changes."\n'
            'developer_instructions = """Read AGENTS.md, README.md, and registry/VALIDATION.md."""\n',
            encoding="utf-8",
        )

        after = build_path_index(scan_lab(root))
        diff = diff_path_indexes(before, after)
        markdown = build_change_briefs(diff)

        self.assertIn("# Waterflow Change Briefs", markdown)
        self.assertIn(".codex/agents/good-agent.toml", markdown)
        self.assertIn("agent", markdown)
        self.assertIn("P2", markdown)
        self.assertIn("scripts/check-lab", markdown)
        self.assertIn("Codex or Claude", markdown)

    def test_validation_plan_deduplicates_checks_for_current_graph(self):
        root = self.make_lab()

        plan = build_validation_plan(scan_lab(root))

        commands = {check["command"] for check in plan["checks"]}
        self.assertIn("scripts/check-lab", commands)
        self.assertIn("python3 -m unittest discover -s tests", commands)
        self.assertIn("scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab", commands)
        self.assertEqual(plan["summary"]["max_risk"], "P2")
        self.assertGreaterEqual(plan["summary"]["check_count"], 3)

        test_check = [
            check for check in plan["checks"]
            if check["command"] == "python3 -m unittest discover -s tests"
        ][0]
        self.assertIn("tests/test_demo.py", test_check["paths"])
        self.assertIn("waterflow/auditor.py", test_check["paths"])

    def test_route_index_and_changed_plan_localize_large_graph_work(self):
        root = self.make_lab()
        before = build_path_index(scan_lab(root))

        (root / ".agents" / "skills" / "new-skill").mkdir()
        (root / ".agents" / "skills" / "new-skill" / "SKILL.md").write_text(
            "---\n"
            "name: new-skill\n"
            "description: Use when testing selective validation.\n"
            "---\n"
            "# New Skill\n",
            encoding="utf-8",
        )
        (root / "README.md").write_text("# Lab\nUpdated documentation route.\n", encoding="utf-8")

        after_report = scan_lab(root)
        after_report["path_diff"] = diff_path_indexes(before, build_path_index(after_report))
        route_index = build_route_index(after_report)
        changed_plan = build_validation_plan(after_report, scope="changed")

        self.assertIn("skill", route_index["routes"])
        self.assertIn("documentation", route_index["routes"])
        self.assertEqual(route_index["summary"]["changed_path_count"], 2)
        self.assertIn(".agents/skills/new-skill/SKILL.md", route_index["routes"]["skill"]["changed_paths"])
        self.assertEqual(changed_plan["summary"]["scope"], "changed")
        self.assertEqual(changed_plan["summary"]["changed_path_count"], 2)
        changed_paths = {path for check in changed_plan["checks"] for path in check["paths"]}
        self.assertEqual(changed_paths, {".agents/skills/new-skill/SKILL.md", "README.md"})
        self.assertIn("scripts/check-lab", {check["command"] for check in changed_plan["checks"]})

    def test_write_outputs_clears_stale_diff_when_scan_has_no_comparison(self):
        root = self.make_lab()
        output_dir = root / "outputs" / "shared" / "waterflow"
        before = build_path_index(scan_lab(root))
        (root / "README.md").write_text("# Lab\nChanged once.\n", encoding="utf-8")

        write_outputs(scan_lab(root), output_dir, previous_index=before)
        self.assertTrue((output_dir / "waterflow-path-diff.json").exists())

        write_outputs(scan_lab(root), output_dir)
        self.assertFalse((output_dir / "waterflow-path-diff.json").exists())
        self.assertFalse((output_dir / "waterflow-change-briefs.md").exists())
        changed_plan = json.loads((output_dir / "waterflow-validation-plan-changed.json").read_text())
        self.assertEqual(changed_plan["summary"]["scope"], "changed")
        self.assertEqual(changed_plan["summary"]["changed_path_count"], 0)
        self.assertEqual(changed_plan["summary"]["check_count"], 0)

    def test_validation_runner_records_real_exit_codes(self):
        root = self.make_lab()
        plan = {
            "schema_version": 1,
            "generated_at": "2026-06-29T00:00:00+00:00",
            "lab_root": str(root),
            "summary": {"check_count": 2, "max_risk": "P2"},
            "checks": [
                {
                    "command": "python3 -c 'print(\"ok-waterflow\")'",
                    "risk": "P2",
                    "route_kinds": ["test"],
                    "paths": ["tests/test_demo.py"],
                },
                {
                    "command": "python3 -c 'import sys; print(\"bad-waterflow\"); sys.exit(3)'",
                    "risk": "P2",
                    "route_kinds": ["test"],
                    "paths": ["tests/test_demo.py"],
                },
            ],
        }

        results = run_validation_plan(plan, root=root, timeout_seconds=10)
        markdown = build_validation_results_markdown(results)

        self.assertEqual(results["summary"]["check_count"], 2)
        self.assertEqual(results["summary"]["passed_count"], 1)
        self.assertEqual(results["summary"]["failed_count"], 1)
        self.assertEqual(results["summary"]["max_exit_code"], 3)
        self.assertIn("ok-waterflow", results["checks"][0]["stdout"])
        self.assertIn("bad-waterflow", results["checks"][1]["stdout"])
        self.assertIn("exit_code: `3`", markdown)


if __name__ == "__main__":
    unittest.main()
