import unittest

from lab_agents.dispatch import dispatch_plan, running_count, DEFAULT_CONCURRENCY


def _task(tid, state="pending", priority=50, deps=None, ack=True, layer="root"):
    t = {
        "id": tid,
        "title": tid,
        "state": state,
        "priority": priority,
        "depends_on": deps or [],
        "layer": layer,
    }
    if ack:
        # full ack for a root task = ["root","protocol"]
        t["rule_ack"] = ["root", "workspace", "package", "protocol"]
    return t


class DispatchTests(unittest.TestCase):
    def test_running_count(self):
        data = {"tasks": [_task("a", "running"), _task("b", "running"), _task("c")]}
        self.assertEqual(running_count(data), 2)

    def test_concurrency_cap_limits_releasable(self):
        # 4 ready tasks, cap 2, nothing running -> only 2 released, 2 held
        data = {"tasks": [_task("a"), _task("b"), _task("c"), _task("d")]}
        plan = dispatch_plan(data, concurrency=2)
        self.assertEqual(len(plan["releasable"]), 2)
        self.assertEqual(len(plan["held"]), 2)
        self.assertEqual(plan["free_slots"], 2)

    def test_running_tasks_consume_slots(self):
        # cap 2, one already running -> only 1 free slot
        data = {"tasks": [_task("r", "running"), _task("a"), _task("b")]}
        plan = dispatch_plan(data, concurrency=2)
        self.assertEqual(plan["free_slots"], 1)
        self.assertEqual(len(plan["releasable"]), 1)

    def test_gate1_blocks_unacknowledged(self):
        # a ready task with no rule_ack must be blocked, not released
        bad = _task("bad", ack=False)
        data = {"tasks": [bad]}
        plan = dispatch_plan(data, concurrency=2)
        self.assertEqual(plan["releasable"], [])
        self.assertEqual(len(plan["blocked"]), 1)
        self.assertEqual(plan["blocked"][0]["id"], "bad")

    def test_priority_order_respected(self):
        data = {"tasks": [_task("low", priority=10), _task("high", priority=99)]}
        plan = dispatch_plan(data, concurrency=1)
        self.assertEqual(plan["releasable"][0]["id"], "high")

    def test_unmet_dependency_not_runnable(self):
        # b depends on a (still pending) -> b is not runnable
        data = {"tasks": [_task("a"), _task("b", deps=["a"])]}
        plan = dispatch_plan(data, concurrency=5)
        ids = {t["id"] for t in plan["releasable"]}
        self.assertIn("a", ids)
        self.assertNotIn("b", ids)

    def test_no_free_slots_holds_everything(self):
        data = {"tasks": [_task("r1", "running"), _task("r2", "running"), _task("a")]}
        plan = dispatch_plan(data, concurrency=2)
        self.assertEqual(plan["free_slots"], 0)
        self.assertEqual(plan["releasable"], [])
        self.assertEqual(len(plan["held"]), 1)

    def test_invalid_concurrency_raises(self):
        with self.assertRaises(ValueError):
            dispatch_plan({"tasks": []}, concurrency=0)

    def test_default_concurrency_is_conservative(self):
        self.assertLessEqual(DEFAULT_CONCURRENCY, 3)


if __name__ == "__main__":
    unittest.main()
