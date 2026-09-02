import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP_ROOT = LAB_ROOT / ".tmp" / "tests"


class CheckLabTests(unittest.TestCase):
    def make_lab(self) -> tuple[Path, dict[str, str]]:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
        root = Path(tempfile.mkdtemp(prefix="check-lab-", dir=TEST_TMP_ROOT))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)

        for directory in ("scripts", "tests", "workspaces", ".worktrees"):
            (root / directory).mkdir(parents=True)
        for name in ("AGENTS.md", "CLAUDE.md", "README.md", "SECURITY.md"):
            (root / name).write_text(f"# {name}\n", encoding="utf-8")
        (root / ".current-agent").write_text("workspaces/example\n", encoding="utf-8")
        (root / ".gitignore").write_text(".tmp/\nworkspaces/*\n", encoding="utf-8")

        for name in (
            "check-current-agent",
            "check-lab",
            "check-native-parity",
            "check-secrets",
            "check-side-effects",
            "lab",
            "open-workbench",
        ):
            shutil.copy2(LAB_ROOT / "scripts" / name, root / "scripts" / name)
            (root / "scripts" / name).chmod(0o755)

        subprocess.run(["git", "init", "-q"], cwd=root, check=True)

        home = root / "home"
        claude_home = home / ".claude"
        codex_home = home / ".codex"
        claude_home.mkdir(parents=True)
        codex_home.mkdir(parents=True)
        (claude_home / "CLAUDE.md").write_text("# Machine Claude\n", encoding="utf-8")
        (codex_home / "AGENTS.md").write_text("# Machine Codex\n", encoding="utf-8")
        (claude_home / "settings.json").write_text(
            json.dumps({"env": {}, "model": "native", "permissions": {}}),
            encoding="utf-8",
        )
        (codex_home / "config.toml").write_text(
            "[features]\nmemories = true\nmulti_agent = true\n",
            encoding="utf-8",
        )

        fake_bin = root / "fake-bin"
        fake_bin.mkdir()
        versions = {
            "cmux": "cmux 0.64.20",
            "codex": "codex-cli test",
            "claude": "claude test",
        }
        for name, version in versions.items():
            command = fake_bin / name
            command.write_text(
                "#!/usr/bin/env bash\n"
                f"printf '%s\\n' {version!r}\n",
                encoding="utf-8",
            )
            command.chmod(0o755)

        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        env["HOME"] = str(home)
        env.pop("CODEX_HOME", None)
        env.pop("CLAUDE_CONFIG_DIR", None)
        return root, env

    def run_check(self, root: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(root / "scripts" / "check-lab")],
            cwd=root,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    def test_minimal_lab_passes(self):
        root, env = self.make_lab()

        result = self.run_check(root, env)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("native-first Agent Lab is valid", result.stdout)

    def test_bridge_automation_and_injection_fail_closed(self):
        cases = {
            "codex auto-start": '\nsubprocess.run(["codex"])\n',
            "claude auto-start": '\nsubprocess.run(["claude"])\n',
            "alternate home": '\nCODEX_HOME = "/tmp/client"\n',
            "api key": '\nVENDOR_API_KEY = "fake"\n',
            "cmux command": '\nFORBIDDEN = "--command"\n',
            "cmux send": '\nFORBIDDEN = "send"\n',
            "git write": '\nFORBIDDEN = "git push origin main"\n',
        }
        for name, payload in cases.items():
            with self.subTest(name=name):
                root, env = self.make_lab()
                bridge = root / "scripts" / "open-workbench"
                bridge.write_text(
                    bridge.read_text(encoding="utf-8") + payload,
                    encoding="utf-8",
                )

                result = self.run_check(root, env)

                self.assertNotEqual(result.returncode, 0)

    def test_project_cmux_config_is_rejected(self):
        root, env = self.make_lab()
        config = root / ".cmux" / "cmux.json"
        config.parent.mkdir()
        config.write_text("{}\n", encoding="utf-8")

        result = self.run_check(root, env)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("project-level", result.stderr)

    def test_layout_drift_is_rejected(self):
        root, env = self.make_lab()
        bridge = root / "scripts" / "open-workbench"
        bridge.write_text(
            bridge.read_text(encoding="utf-8").replace(
                '"name": "Claude Code"',
                '"name": "Claude Agent"',
                1,
            ),
            encoding="utf-8",
        )

        result = self.run_check(root, env)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("script structure", result.stderr)


if __name__ == "__main__":
    unittest.main()
