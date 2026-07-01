import unittest

from lab_agents.rule_ack import (
    acknowledgment_ok,
    can_start,
    required_layers,
)


class RuleAckTests(unittest.TestCase):
    def _task(self, layer, acked, state="pending"):
        return {
            "id": f"task_{layer}",
            "layer": layer,
            "state": state,
            "rule_ack": list(acked),
        }

    def test_required_layers_per_layer_type(self):
        self.assertEqual(required_layers({"layer": "root"}), ["root", "protocol"])
        self.assertEqual(
            required_layers({"layer": "workspace"}),
            ["root", "workspace", "protocol"],
        )
        self.assertEqual(
            required_layers({"layer": "package"}),
            ["root", "workspace", "package", "protocol"],
        )

    def test_full_ack_passes_for_each_layer_type(self):
        for layer in ("root", "workspace", "package"):
            task = self._task(layer, required_layers({"layer": layer}))
            ok, missing = acknowledgment_ok(task)
            self.assertTrue(ok, f"{layer} should pass with full ack")
            self.assertEqual(missing, [])

    def test_package_needs_all_four_layers(self):
        task = self._task("package", ["root", "workspace", "package", "protocol"])
        ok, missing = acknowledgment_ok(task)
        self.assertTrue(ok)
        self.assertEqual(missing, [])

        # Drop one layer -> fail with that layer named.
        partial = self._task("package", ["root", "workspace", "package"])
        ok, missing = acknowledgment_ok(partial)
        self.assertFalse(ok)
        self.assertEqual(missing, ["protocol"])

    def test_missing_a_layer_fails_with_missing_name(self):
        task = self._task("workspace", ["root", "protocol"])
        ok, missing = acknowledgment_ok(task)
        self.assertFalse(ok)
        self.assertEqual(missing, ["workspace"])

    def test_missing_rule_ack_fails_closed(self):
        task = {"id": "t", "layer": "package", "state": "pending"}
        ok, missing = acknowledgment_ok(task)
        self.assertFalse(ok)
        self.assertEqual(missing, ["no rule acknowledgment"])

    def test_can_start_allows_fully_acked_pending_task(self):
        task = self._task("package", ["root", "workspace", "package", "protocol"])
        ok, reasons = can_start(task)
        self.assertTrue(ok)
        self.assertEqual(reasons, [])

    def test_can_start_blocks_from_non_pending(self):
        task = self._task(
            "package",
            ["root", "workspace", "package", "protocol"],
            state="running",
        )
        ok, reasons = can_start(task)
        self.assertFalse(ok)
        self.assertTrue(any("pending" in reason for reason in reasons))

    def test_can_start_blocks_when_acknowledgment_missing(self):
        task = {"id": "t", "layer": "root", "state": "pending"}
        ok, reasons = can_start(task)
        self.assertFalse(ok)
        self.assertIn("no rule acknowledgment", reasons)


if __name__ == "__main__":
    unittest.main()
