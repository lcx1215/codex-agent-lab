import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP_ROOT = LAB_ROOT / ".tmp" / "tests"


class SideEffectGateTests(unittest.TestCase):
    def make_dir(self) -> Path:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
        root = Path(tempfile.mkdtemp(prefix="side-effects-", dir=TEST_TMP_ROOT))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return root

    def write_script(self, root: Path, name: str, body: str) -> Path:
        path = root / name
        path.write_text("#!/usr/bin/env bash\n" + body, encoding="utf-8")
        path.chmod(0o755)
        return path

    def run_gate(self, target: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(LAB_ROOT / "scripts" / "check-side-effects"), str(target)],
            cwd=LAB_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_known_dangerous_commands_fail(self):
        cases = {
            "flyctl-secrets": "flyctl secrets set KEY=value\n",
            "fly-destroy": "fly destroy app\n",
            "force-push": "git push --force origin main\n",
            "kubectl": "kubectl apply -f deploy.yaml\n",
            "terraform": "terraform destroy\n",
            "aws": "aws s3 rm s3://bucket --recursive\n",
            "rm-fr": "rm -fr target\n",
            "rm-Rf": "rm -Rf target\n",
        }
        for name, body in cases.items():
            with self.subTest(name=name):
                root = self.make_dir()
                script = self.write_script(root, name, body)
                result = self.run_gate(script)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("MUTATION_UNGATED", result.stdout)

    def test_force_token_does_not_self_whitelist_force_push(self):
        root = self.make_dir()
        script = self.write_script(
            root,
            "push",
            "# side-effects: gated\n"
            "git push --force origin main\n",
        )

        result = self.run_gate(script)

        self.assertNotEqual(result.returncode, 0)

    def test_explicit_apply_gate_passes(self):
        root = self.make_dir()
        script = self.write_script(
            root,
            "deploy",
            "# side-effects: gated\n"
            "APPLY_CHANGES=false\n"
            'case "${1:-}" in --apply) APPLY_CHANGES=true ;; esac\n'
            'if [ "$APPLY_CHANGES" != true ]; then exit 0; fi\n'
            "kubectl apply -f deploy.yaml\n",
        )

        result = self.run_gate(script)

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_local_bounded_delete_passes(self):
        root = self.make_dir()
        script = self.write_script(
            root,
            "cleanup",
            "# side-effects: local-bounded\n"
            'rm -rf "$TMPDIR/fixture"\n',
        )

        result = self.run_gate(script)

        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
