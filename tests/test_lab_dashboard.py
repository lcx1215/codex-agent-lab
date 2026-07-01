import importlib.util
import json
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

from lab_agents.run_record import RunRecord, write_run_record


LAB_ROOT = Path(__file__).resolve().parents[1]


def load_dashboard_module():
    path = LAB_ROOT / "scripts" / "lab-dashboard"
    loader = SourceFileLoader("lab_dashboard", str(path))
    spec = importlib.util.spec_from_loader("lab_dashboard", loader)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class LabDashboardTests(unittest.TestCase):
    def _write_record(self, root: Path, lane: str, run_id: str) -> None:
        rec = RunRecord(
            lane=lane,
            agent=f"{lane}-agent",
            task="dashboard run-record summary",
            repo_root=root,
            run_id=run_id,
        )
        rec.add_command(["true"], 0, "", "").finalize("success", "ok")
        write_run_record(rec, runs_root=root / "registry" / "runs")

    def test_run_record_summary_reports_both_lanes_and_latest(self):
        module = load_dashboard_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_record(root, "claude", "20260701T010000Z-claude-a")
            self._write_record(root, "codex", "20260701T020000Z-codex-b")

            summary = module.run_record_summary(root)

            self.assertEqual(summary["status"], "pass")
            self.assertEqual(summary["record_count"], 2)
            self.assertEqual(summary["lanes"], ["claude", "codex"])
            self.assertEqual(summary["latest_run_id"], "20260701T020000Z-codex-b")
            self.assertTrue(summary["latest_matches_newest"])

    def test_run_record_summary_fails_when_latest_is_stale(self):
        module = load_dashboard_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_record(root, "claude", "20260701T010000Z-claude-a")
            stale_latest = root / "registry" / "runs" / "latest.json"
            stale_latest.write_text(
                json.dumps(json.loads((root / "registry" / "runs" / "20260701T010000Z-claude-a" / "record.json").read_text())),
                encoding="utf-8",
            )
            self._write_record(root, "codex", "20260701T020000Z-codex-b")
            stale_latest.write_text(
                json.dumps(json.loads((root / "registry" / "runs" / "20260701T010000Z-claude-a" / "record.json").read_text())),
                encoding="utf-8",
            )

            summary = module.run_record_summary(root)

            self.assertEqual(summary["status"], "fail")
            self.assertFalse(summary["latest_matches_newest"])
            self.assertIn("latest.json does not point to newest run", summary["issues"])

    def test_render_markdown_includes_task_state_summary(self):
        module = load_dashboard_module()
        markdown = module.render_markdown(
            {
                "generated_at": "2026-07-01T00:00:00+00:00",
                "health": "ok",
                "issues": [],
                "benchmark": None,
                "waterflow": {},
                "compatibility": {},
                "run_records": {},
                "task_state": {
                    "status": "pass",
                    "summary": {
                        "task_count": 1,
                        "pending_count": 0,
                        "running_count": 1,
                        "blocked_count": 0,
                        "review_count": 0,
                        "verified_count": 0,
                        "done_count": 0,
                        "runnable_count": 0,
                        "stale_running_count": 0,
                    },
                    "next_task": None,
                },
                "workspace_safety": {},
                "async": {},
                "git": {},
            }
        )

        self.assertIn("## Task State", markdown)
        self.assertIn("- Status: `pass`", markdown)
        self.assertIn("- Tasks: `1`", markdown)
        self.assertIn("- Next: `-`", markdown)


if __name__ == "__main__":
    unittest.main()
