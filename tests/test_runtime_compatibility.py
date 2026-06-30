import json
import subprocess
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]


class RuntimeCompatibilityTests(unittest.TestCase):
    def test_runtime_compatibility_script_reports_structured_status(self):
        result = subprocess.run(
            [str(LAB_ROOT / "scripts" / "check-runtime-compatibility"), "--json"],
            cwd=LAB_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        report = json.loads(result.stdout)

        self.assertIn(report["status"], {"pass", "warn"})
        self.assertEqual(report["summary"]["failed_count"], 0)
        self.assertGreater(report["summary"]["check_count"], 10)

        names = {item["name"] for item in report["checks"]}
        self.assertIn("python version", names)
        self.assertIn("script executability", names)
        self.assertIn("gitignore: .omc/state/example.json", names)
        self.assertIn("gitignore: .omc/skills/example/SKILL.md", names)


if __name__ == "__main__":
    unittest.main()
