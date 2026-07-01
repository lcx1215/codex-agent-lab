import importlib.util
import importlib.machinery
import json
import tempfile
import unittest
from pathlib import Path

from lab_agents.task_state import validate_task_registry
from lab_agents.task_verify import (
    can_promote_to_verified,
    promote,
    verification_ok,
)


LAB_ROOT = Path(__file__).resolve().parents[1]


def _review_task(checks, state="review"):
    return {
        "id": "t1",
        "title": "demo",
        "state": state,
        "lane": "claude",
        "priority": 50,
        "depends_on": [],
        "created_at": "2026-07-01T00:00:00Z",
        "updated_at": "2026-07-01T00:00:00Z",
        "verification": {"checks": checks},
        "history": [
            {"from": None, "to": "pending", "at": "2026-07-01T00:00:00Z"},
            {"from": "pending", "to": "running", "at": "2026-07-01T00:00:00Z"},
            {"from": "running", "to": "review", "at": "2026-07-01T00:10:00Z"},
        ],
    }


class VerificationOkTests(unittest.TestCase):
    def test_all_pass(self):
        task = _review_task([
            {"name": "check-lab", "passed": True},
            {"name": "check-secrets", "passed": True},
        ])
        self.assertEqual(verification_ok(task), (True, []))

    def test_any_fail_lists_failed(self):
        task = _review_task([
            {"name": "check-lab", "passed": True},
            {"name": "check-secrets", "passed": False},
        ])
        self.assertEqual(verification_ok(task), (False, ["check-secrets"]))

    def test_missing_verification_fails_closed(self):
        task = {"id": "t1", "state": "running", "history": []}
        self.assertEqual(verification_ok(task), (False, ["no verification declared"]))

    def test_empty_checks_fails_closed(self):
        task = _review_task([])
        self.assertEqual(verification_ok(task), (False, ["no verification declared"]))


class PromoteGateTests(unittest.TestCase):
    def test_can_promote_all_pass(self):
        task = _review_task([{"name": "check-lab", "passed": True}])
        ok, reasons = can_promote_to_verified(task)
        self.assertTrue(ok)
        self.assertEqual(reasons, [])

    def test_refuses_on_failed_check(self):
        task = _review_task([{"name": "check-lab", "passed": False}])
        ok, reasons = can_promote_to_verified(task)
        self.assertFalse(ok)
        self.assertIn("check-lab", reasons)

    def test_refuses_from_non_review(self):
        task = _review_task([{"name": "check-lab", "passed": True}], state="running")
        ok, reasons = can_promote_to_verified(task)
        self.assertFalse(ok)
        self.assertTrue(any("state must be review" in r for r in reasons))


class PromoteTests(unittest.TestCase):
    def test_promote_all_pass(self):
        task = _review_task([{"name": "check-lab", "passed": True}])
        now = "2026-07-01T01:00:00Z"
        promoted = promote(task, now)
        self.assertEqual(promoted["state"], "verified")
        self.assertEqual(promoted["updated_at"], now)
        # original untouched
        self.assertEqual(task["state"], "review")

    def test_promote_appends_history_entry(self):
        task = _review_task([{"name": "check-lab", "passed": True}])
        now = "2026-07-01T01:00:00Z"
        promoted = promote(task, now)
        self.assertEqual(len(promoted["history"]), len(task["history"]) + 1)
        self.assertEqual(
            promoted["history"][-1],
            {"from": "review", "to": "verified", "at": now},
        )

    def test_promote_result_matches_task_state_machine(self):
        task = _review_task([{"name": "check-lab", "passed": True}])
        promoted = promote(task, "2026-07-01T01:00:00Z")
        registry = {"schema_version": 1, "tasks": [promoted]}
        self.assertEqual(validate_task_registry(registry), [])

    def test_promote_from_non_review_raises(self):
        task = _review_task([{"name": "check-lab", "passed": True}], state="running")
        with self.assertRaises(ValueError):
            promote(task, "2026-07-01T01:00:00Z")

    def test_promote_with_failed_check_raises(self):
        task = _review_task([{"name": "check-lab", "passed": False}])
        with self.assertRaises(ValueError):
            promote(task, "2026-07-01T01:00:00Z")


class CheckGatesHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        loader = importlib.machinery.SourceFileLoader("check_gates", str(LAB_ROOT / "scripts" / "check-gates"))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        cls.check_gates = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.check_gates)

    def test_gate1_applies_to_task_blocked_after_starting(self):
        task = {
            "id": "blocked_after_running",
            "state": "blocked",
            "history": [
                {"from": None, "to": "pending", "at": "2026-07-01T00:00:00Z"},
                {"from": "pending", "to": "running", "at": "2026-07-01T00:01:00Z"},
                {"from": "running", "to": "blocked", "at": "2026-07-01T00:02:00Z"},
            ],
        }
        self.assertTrue(self.check_gates.task_has_started(task))

    def test_gate3_applies_to_task_cancelled_after_verified(self):
        task = {
            "id": "cancelled_after_verified",
            "state": "cancelled",
            "history": [
                {"from": None, "to": "pending", "at": "2026-07-01T00:00:00Z"},
                {"from": "pending", "to": "running", "at": "2026-07-01T00:01:00Z"},
                {"from": "running", "to": "review", "at": "2026-07-01T00:02:00Z"},
                {"from": "review", "to": "verified", "at": "2026-07-01T00:03:00Z"},
                {"from": "verified", "to": "cancelled", "at": "2026-07-01T00:04:00Z"},
            ],
        }
        self.assertTrue(self.check_gates.task_reached_verification_gate(task))

    def test_check_gates_fails_closed_on_invalid_task_registry_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tasks_dir = root / "registry" / "tasks"
            tasks_dir.mkdir(parents=True)
            (tasks_dir / "tasks.json").write_text(
                json.dumps({"schema_version": 1, "tasks": "not-a-list"}),
                encoding="utf-8",
            )
            old_root = self.check_gates.LAB_ROOT
            self.check_gates.LAB_ROOT = root
            try:
                self.assertEqual(self.check_gates.main(), 1)
            finally:
                self.check_gates.LAB_ROOT = old_root


if __name__ == "__main__":
    unittest.main()
