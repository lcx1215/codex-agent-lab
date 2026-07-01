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

    def test_check_secrets_does_not_flag_task_state_slug_as_openai_key(self):
        result = subprocess.run(
            [str(LAB_ROOT / "scripts" / "check-secrets")],
            cwd=LAB_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK:", result.stdout)

    def test_check_secrets_still_flags_synthetic_openai_key_shape(self):
        fixture = LAB_ROOT / "synthetic-secret-scan.txt"
        synthetic_key = "sk-" + ("A" * 24)
        try:
            fixture.write_text(f"fake={synthetic_key}\n", encoding="utf-8")

            result = subprocess.run(
                [str(LAB_ROOT / "scripts" / "check-secrets")],
                cwd=LAB_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        finally:
            fixture.unlink(missing_ok=True)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("secret-like token detected", result.stderr)
        self.assertNotIn(synthetic_key, result.stderr)

    def test_check_sandbox_fails_closed_when_rg_errors(self):
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
