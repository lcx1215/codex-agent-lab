import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP_ROOT = LAB_ROOT / ".tmp" / "tests"


def lab_temp_dir(prefix: str) -> Path:
    TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=TEST_TMP_ROOT))


class GateFailClosedTests(unittest.TestCase):
    def fake_rg_env(self) -> tuple[dict[str, str], Path]:
        root = lab_temp_dir("gate-fail-closed-")
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        fake_rg = root / "rg"
        fake_rg.write_text(
            "#!/usr/bin/env bash\n"
            "printf 'fake rg scanner failure\\n' >&2\n"
            "exit 2\n",
            encoding="utf-8",
        )
        fake_rg.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = f"{root}:{env.get('PATH', '')}"
        env.pop("RIPGREP_CONFIG_PATH", None)
        return env, root

    def test_check_secrets_fails_closed_when_rg_errors(self):
        env, _ = self.fake_rg_env()

        result = subprocess.run(
            [str(LAB_ROOT / "scripts" / "check-secrets")],
            cwd=LAB_ROOT,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("OK:", result.stdout)
        self.assertIn("ripgrep", result.stderr)

    def test_check_sandbox_fails_closed_when_rg_errors(self):
        baseline = subprocess.run(
            [str(LAB_ROOT / "scripts" / "check-sandbox")],
            cwd=LAB_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if "writable_roots must contain only the lab root" in baseline.stderr:
            self.skipTest("check-sandbox config is bound to the primary lab root")

        env, _ = self.fake_rg_env()

        result = subprocess.run(
            [str(LAB_ROOT / "scripts" / "check-sandbox")],
            cwd=LAB_ROOT,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("OK:", result.stdout)
        self.assertIn("ripgrep", result.stderr)


if __name__ == "__main__":
    unittest.main()
