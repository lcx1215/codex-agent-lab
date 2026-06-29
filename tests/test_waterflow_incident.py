import tempfile
import unittest
from pathlib import Path

from waterflow.incident import INCIDENT_EXPECTED_CODES, run_incident_suite


class WaterflowIncidentTests(unittest.TestCase):
    def test_complex_incident_generates_codex_claude_handoff(self):
        output_root = Path(tempfile.mkdtemp(prefix="waterflow-incident-"))

        results = run_incident_suite(output_root, validation_timeout_seconds=1)

        self.assertEqual(results["status"], "pass")
        self.assertEqual(results["baseline"]["finding_count"], 0)
        self.assertEqual(results["incident"]["missing_expected_codes"], [])
        self.assertTrue(INCIDENT_EXPECTED_CODES.issubset(set(results["incident"]["detected_codes"])))
        self.assertGreaterEqual(results["incident"]["finding_count"], len(INCIDENT_EXPECTED_CODES))
        self.assertGreater(results["path_diff"]["added_count"], 0)
        self.assertGreater(results["path_diff"]["removed_count"], 0)
        self.assertGreater(results["path_diff"]["changed_count"], 0)
        self.assertGreaterEqual(results["route_index"]["route_count"], 5)
        self.assertEqual(results["route_index"]["max_risk"], "P1")
        self.assertEqual(results["validation_runner"]["check_count"], 3)
        self.assertEqual(results["validation_runner"]["passed_count"], 1)
        self.assertEqual(results["validation_runner"]["failed_count"], 2)
        self.assertEqual(results["validation_runner"]["timed_out_count"], 1)
        self.assertEqual(results["validation_runner"]["max_exit_code"], 124)

        handoff_path = Path(results["artifacts"]["codex_claude_handoff"])
        self.assertTrue(handoff_path.exists())
        handoff = handoff_path.read_text(encoding="utf-8")
        self.assertIn("Codex or Claude", handoff)
        self.assertIn("Repair Order", handoff)
        self.assertIn("AGENT_TOML_INVALID", handoff)
        self.assertIn("SCRIPT_NOT_EXECUTABLE", handoff)
        self.assertIn("PROGRESS_WITHOUT_VALIDATION", handoff)
        self.assertIn("exit_code", handoff)
        self.assertIn("timed_out", handoff)

        incident_report_path = Path(results["artifacts"]["incident_report_markdown"])
        self.assertTrue(incident_report_path.exists())
        incident_report = incident_report_path.read_text(encoding="utf-8")
        self.assertIn("pass definition", incident_report.lower())
        self.assertIn("not mean", incident_report)


if __name__ == "__main__":
    unittest.main()
