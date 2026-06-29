import tempfile
import unittest
from pathlib import Path

from waterflow.stress import (
    EXPECTED_PROBLEM_CODES,
    NEEDLE_PROBLEM_CODES,
    implemented_finding_codes,
    run_stress_suite,
)

LAB_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP_ROOT = LAB_ROOT / ".tmp" / "tests"


def lab_temp_dir(prefix: str) -> Path:
    TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=TEST_TMP_ROOT))


class WaterflowStressTests(unittest.TestCase):
    def test_stress_suite_detects_problem_families_and_validation_failures(self):
        output_root = lab_temp_dir("waterflow-stress-")

        results = run_stress_suite(output_root, scale_paths=120, validation_timeout_seconds=1)

        self.assertEqual(results["status"], "pass")
        self.assertIn("pass_definition", results["harness_philosophy"])
        self.assertIn("expected defects", results["harness_philosophy"]["pass_definition"])
        self.assertTrue(all(criterion["passed"] for criterion in results["harness_criteria"]))
        self.assertEqual(results["detector_coverage"]["uncovered_implemented_codes"], [])
        self.assertEqual(results["detector_coverage"]["expected_without_implementation"], [])
        detected_codes = set(results["problem_lab"]["detected_codes"])
        self.assertTrue(EXPECTED_PROBLEM_CODES.issubset(detected_codes))
        self.assertTrue(implemented_finding_codes().issubset(detected_codes))
        self.assertEqual(results["problem_lab"]["missing_expected_codes"], [])
        self.assertGreaterEqual(results["scale_lab"]["node_count"], 120)
        self.assertEqual(results["scale_lab"]["finding_count"], 0)
        self.assertGreaterEqual(results["needle_lab"]["node_count"], 120)
        self.assertTrue(NEEDLE_PROBLEM_CODES.issubset(set(results["needle_lab"]["detected_codes"])))
        self.assertEqual(results["needle_lab"]["missing_expected_codes"], [])
        self.assertEqual(results["validation_runner"]["check_count"], 3)
        self.assertEqual(results["validation_runner"]["passed_count"], 1)
        self.assertEqual(results["validation_runner"]["failed_count"], 2)
        self.assertEqual(results["validation_runner"]["timed_out_count"], 1)
        self.assertEqual(results["validation_runner"]["max_exit_code"], 124)
        self.assertTrue((Path(results["run_dir"]) / "waterflow-stress-results.md").exists())


if __name__ == "__main__":
    unittest.main()
