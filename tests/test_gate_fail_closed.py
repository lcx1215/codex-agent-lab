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
    def secret_repo(self) -> Path:
        root = lab_temp_dir("secret-scan-")
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / "scripts").mkdir()
        (root / "README.md").write_text("# Fixture\n", encoding="utf-8")
        return root

    def run_secret_scan(
        self,
        root: Path,
        *,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(LAB_ROOT / "scripts" / "check-secrets"), "--root", str(root)],
            cwd=LAB_ROOT,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

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

    def test_check_secrets_ignores_broken_rg_and_scans_source(self):
        env, _ = self.fake_rg_env()
        root = self.secret_repo()
        (root / "scripts" / "clean.txt").write_text("ordinary source\n", encoding="utf-8")

        result = self.run_secret_scan(root, env=env)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK:", result.stdout)
        self.assertIn("source files scanned:", result.stdout)

    def test_check_secrets_does_not_flag_ordinary_sk_prefix_text(self):
        root = self.secret_repo()
        (root / "scripts" / "clean.txt").write_text("skipped-state\n", encoding="utf-8")

        result = self.run_secret_scan(root)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK:", result.stdout)

    def test_check_secrets_still_flags_synthetic_openai_key_shape(self):
        root = self.secret_repo()
        fixture = root / "scripts" / "synthetic-secret-scan.txt"
        synthetic_key = "sk-" + ("A" * 24)
        fixture.write_text(f"fake={synthetic_key}\n", encoding="utf-8")

        result = self.run_secret_scan(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("secret-like token detected", result.stderr)
        self.assertNotIn(synthetic_key, result.stderr)

if __name__ == "__main__":
    unittest.main()
