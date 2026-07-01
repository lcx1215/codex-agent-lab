import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from lab_agents.task_state import (
    next_runnable_task,
    task_state_report,
    validate_task_registry,
)


LAB_ROOT = Path(__file__).resolve().parents[1]


class TaskStateTests(unittest.TestCase):
    def _registry(self):
        return {
            "schema_version": 1,
            "tasks": [
                {
                    "id": "task_foundation",
                    "title": "Foundation first",
                    "state": "done",
                    "lane": "codex",
                    "priority": 20,
                    "depends_on": [],
                    "created_at": "2026-07-01T01:00:00Z",
                    "updated_at": "2026-07-01T02:00:00Z",
                    "history": [
                        {"from": None, "to": "pending", "at": "2026-07-01T01:00:00Z"},
                        {"from": "pending", "to": "running", "at": "2026-07-01T01:10:00Z"},
                        {"from": "running", "to": "review", "at": "2026-07-01T01:20:00Z"},
                        {"from": "review", "to": "verified", "at": "2026-07-01T01:30:00Z"},
                        {"from": "verified", "to": "done", "at": "2026-07-01T01:40:00Z"},
                    ],
                },
                {
                    "id": "task_low",
                    "title": "Lower priority runnable",
                    "state": "pending",
                    "lane": "claude",
                    "priority": 10,
                    "depends_on": ["task_foundation"],
                    "created_at": "2026-07-01T03:00:00Z",
                    "updated_at": "2026-07-01T03:00:00Z",
                    "history": [{"from": None, "to": "pending", "at": "2026-07-01T03:00:00Z"}],
                },
                {
                    "id": "task_high",
                    "title": "Higher priority runnable",
                    "state": "pending",
                    "lane": "codex",
                    "priority": 90,
                    "depends_on": ["task_foundation"],
                    "created_at": "2026-07-01T04:00:00Z",
                    "updated_at": "2026-07-01T04:00:00Z",
                    "history": [{"from": None, "to": "pending", "at": "2026-07-01T04:00:00Z"}],
                },
                {
                    "id": "task_blocked_by_dependency",
                    "title": "Dependency not done",
                    "state": "pending",
                    "lane": "codex",
                    "priority": 100,
                    "depends_on": ["task_high"],
                    "created_at": "2026-07-01T05:00:00Z",
                    "updated_at": "2026-07-01T05:00:00Z",
                    "history": [{"from": None, "to": "pending", "at": "2026-07-01T05:00:00Z"}],
                },
            ],
        }

    def test_registry_validates_and_selects_highest_priority_runnable_task(self):
        registry = self._registry()

        self.assertEqual(validate_task_registry(registry), [])

        task = next_runnable_task(registry)
        self.assertIsNotNone(task)
        self.assertEqual(task["id"], "task_high")

    def test_registry_rejects_duplicate_ids_unknown_dependencies_and_bad_transitions(self):
        registry = self._registry()
        registry["tasks"][1]["id"] = "task_foundation"
        registry["tasks"][2]["depends_on"] = ["missing-task"]
        registry["tasks"][3]["history"].append(
            {"from": "pending", "to": "done", "at": "2026-07-01T05:10:00Z"}
        )

        errors = validate_task_registry(registry)

        self.assertTrue(any("duplicate task id" in error for error in errors))
        self.assertTrue(any("unknown dependency" in error for error in errors))
        self.assertTrue(any("invalid transition" in error for error in errors))

    def test_report_marks_stale_running_task_as_issue_without_hiding_pending_work(self):
        registry = self._registry()
        registry["tasks"].append(
            {
                "id": "task_stale",
                "title": "Stale running task",
                "state": "running",
                "lane": "claude",
                "priority": 50,
                "depends_on": [],
                "created_at": "2026-07-01T01:00:00Z",
                "updated_at": "2026-07-01T01:10:00Z",
                "lease_expires_at": "2026-07-01T01:30:00Z",
                "history": [
                    {"from": None, "to": "pending", "at": "2026-07-01T01:00:00Z"},
                    {"from": "pending", "to": "running", "at": "2026-07-01T01:10:00Z"},
                ],
            }
        )

        report = task_state_report(registry, now="2026-07-01T02:00:00Z")

        self.assertEqual(report["status"], "warn")
        self.assertEqual(report["summary"]["runnable_count"], 2)
        self.assertEqual(report["summary"]["stale_running_count"], 1)
        self.assertEqual(report["next_task"]["id"], "task_high")

    def test_check_task_state_script_reports_structured_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tasks_dir = root / "registry" / "tasks"
            tasks_dir.mkdir(parents=True)
            (tasks_dir / "tasks.json").write_text(json.dumps(self._registry()), encoding="utf-8")

            result = subprocess.run(
                [str(LAB_ROOT / "scripts" / "check-task-state"), "--root", str(root), "--json"],
                cwd=LAB_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["next_task"]["id"], "task_high")


if __name__ == "__main__":
    unittest.main()
