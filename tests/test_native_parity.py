import json
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = LAB_ROOT / "scripts" / "check-native-parity"
TEST_TMP_ROOT = LAB_ROOT / ".tmp" / "tests"


class NativeParityTests(unittest.TestCase):
    @staticmethod
    def load_module():
        loader = SourceFileLoader("native_parity_test_module", str(SCRIPT))
        spec = spec_from_loader(loader.name, loader)
        assert spec is not None
        module = module_from_spec(spec)
        loader.exec_module(module)
        return module

    def make_environment(self) -> tuple[Path, Path, dict[str, str]]:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
        root = Path(tempfile.mkdtemp(prefix="native-parity-", dir=TEST_TMP_ROOT))
        self.addCleanup(shutil.rmtree, root, True)
        lab = root / "lab"
        home = root / "home"
        fake_bin = root / "bin"
        lab.mkdir()
        home.mkdir()
        fake_bin.mkdir()

        (lab / "AGENTS.md").write_text("# Agent Lab\n", encoding="utf-8")
        (lab / "CLAUDE.md").write_text("# Claude Lab\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=lab, check=True)

        claude_home = home / ".claude"
        codex_home = home / ".codex"
        claude_home.mkdir()
        codex_home.mkdir()
        (claude_home / "CLAUDE.md").write_text("# Machine Claude\n", encoding="utf-8")
        (codex_home / "AGENTS.md").write_text("# Machine Codex\n", encoding="utf-8")
        (claude_home / "settings.json").write_text(
            json.dumps(
                {
                    "env": {"ANTHROPIC_AUTH_TOKEN": "must-not-appear"},
                    "model": "native",
                    "permissions": {},
                }
            ),
            encoding="utf-8",
        )
        (codex_home / "config.toml").write_text(
            "[features]\nmemories = true\nmulti_agent = true\n",
            encoding="utf-8",
        )
        for name, version in (("codex", "codex-cli test"), ("claude", "claude test")):
            command = fake_bin / name
            command.write_text(
                f"#!/usr/bin/env bash\nprintf '%s\\n' {version!r}\n",
                encoding="utf-8",
            )
            command.chmod(0o755)

        env = os.environ.copy()
        env["HOME"] = str(home)
        env["AGENT_LAB_ROOT"] = str(lab)
        env["PATH"] = f"{fake_bin}:{Path(sys.executable).parent}:/usr/bin:/bin"
        return lab, home, env

    def run_check(self, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(SCRIPT), "--json"],
            cwd=env["AGENT_LAB_ROOT"],
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_static_native_parity_passes_without_exposing_env_values(self):
        _, _, env = self.make_environment()

        result = self.run_check(env)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["static"]["schema"], "agent-lab.native-parity.v2")
        self.assertNotIn("must-not-appear", result.stdout)
        self.assertEqual(payload["static"]["clients"]["codex"]["version"], "codex-cli test")
        self.assertEqual(payload["static"]["clients"]["claude"]["version"], "claude test")

    def test_parent_claude_instruction_fails_closed(self):
        _, home, env = self.make_environment()
        (home / "CLAUDE.md").write_text("# stale parent context\n", encoding="utf-8")

        result = self.run_check(env)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertIn(
            "path-triggered parent Claude instructions",
            "\n".join(payload["static"]["errors"]),
        )

    def test_skill_overrides_fail_closed(self):
        _, home, env = self.make_environment()
        settings = home / ".claude" / "settings.json"
        data = json.loads(settings.read_text(encoding="utf-8"))
        data["skillOverrides"] = {"team": "off"}
        settings.write_text(json.dumps(data), encoding="utf-8")

        result = self.run_check(env)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertIn(
            "Claude skillOverrides suppress native Skills",
            payload["static"]["errors"],
        )

    def test_project_client_configuration_fails_closed(self):
        lab, _, env = self.make_environment()
        (lab / ".claude").mkdir()

        result = self.run_check(env)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertIn(".claude", payload["static"]["lab"]["forbidden_paths"])

    def test_context_budget_is_absolute_and_dirty_state_does_not_bypass_it(self):
        module = self.load_module()

        self.assertTrue(module.context_ok(12048, 10000))
        self.assertFalse(module.context_ok(12049, 10000))
        self.assertTrue(module.cmux_context_ok(10128, 10000))
        self.assertFalse(module.cmux_context_ok(10129, 10000))


if __name__ == "__main__":
    unittest.main()
