import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = LAB_ROOT / "scripts" / "lab"
TEST_TMP_ROOT = LAB_ROOT / ".tmp" / "tests"


class LabCliTests(unittest.TestCase):
    def make_dir(self, prefix: str) -> Path:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
        root = Path(tempfile.mkdtemp(prefix=prefix, dir=TEST_TMP_ROOT))
        self.addCleanup(shutil.rmtree, root, True)
        return root

    def make_lab(self, root: Path) -> Path:
        scripts = root / "lab-root" / "scripts"
        scripts.mkdir(parents=True)
        cli = scripts / "lab"
        shutil.copy2(SCRIPT, cli)
        cli.chmod(0o755)
        return cli

    def make_fake_bin(self, root: Path) -> tuple[Path, dict[str, str]]:
        fake_bin = root / "fake-bin"
        fake_bin.mkdir()
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}:{Path(sys.executable).parent}:/usr/bin:/bin"
        return fake_bin, env

    def run_cli(
        self,
        cli: Path,
        args: list[str],
        *,
        cwd: Path,
        env: dict[str, str],
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(cli), *args],
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_open_delegates_arguments_without_starting_clients(self):
        root = self.make_dir("lab-cli-open-")
        cli = self.make_lab(root)
        log = root / "open.log"
        opener = cli.parent / "open-workbench"
        opener.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, pathlib, sys\n"
            "pathlib.Path(os.environ['LAB_OPEN_LOG']).write_text("
            "json.dumps(sys.argv[1:]), encoding='utf-8')\n",
            encoding="utf-8",
        )
        opener.chmod(0o755)
        _, env = self.make_fake_bin(root)
        env["LAB_OPEN_LOG"] = str(log)

        result = self.run_cli(
            cli,
            ["open", "--current-agent", "--dry-run"],
            cwd=root,
            env=env,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(log.read_text(encoding="utf-8")),
            ["--current-agent", "--dry-run"],
        )

    def test_status_reports_tracked_dirty_and_matching_cmux_workspace(self):
        root = self.make_dir("lab-cli-status-")
        cli = self.make_lab(root)
        target = root / "project with spaces"
        target.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=target, check=True)
        tracked = target / "tracked.txt"
        tracked.write_text("before\n", encoding="utf-8")
        subprocess.run(["git", "add", "tracked.txt"], cwd=target, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Agent Lab",
                "-c",
                "user.email=agent-lab@example.invalid",
                "commit",
                "-qm",
                "fixture",
            ],
            cwd=target,
            check=True,
        )
        tracked.write_text("after\n", encoding="utf-8")

        fake_bin, env = self.make_fake_bin(root)
        cmux = fake_bin / "cmux"
        cmux.write_text(
            f"#!{sys.executable}\n"
            "import json, os, sys\n"
            "args = sys.argv[1:]\n"
            "if args == ['ping']:\n"
            "    print('PONG')\n"
            "elif args == ['--json', 'tree', '--all']:\n"
            "    print(json.dumps({'windows': [{'ref': 'window:1', 'workspaces': [{"
            "'ref': 'workspace:7', 'title': 'project with spaces'"
            "}]}]}))\n"
            "elif args == ['workspace', 'list', '--json', '--window', 'window:1']:\n"
            "    print(json.dumps({'window_ref': 'window:1', 'workspaces': [{"
            "'ref': 'workspace:7', 'title': 'project with spaces', "
            "'current_directory': os.environ['LAB_WORKSPACE_CWD']"
            "}]}))\n"
            "else:\n"
            "    raise SystemExit(2)\n",
            encoding="utf-8",
        )
        cmux.chmod(0o755)
        env["LAB_WORKSPACE_CWD"] = str(target.resolve())

        result = self.run_cli(
            cli,
            ["status", "--json", str(target)],
            cwd=root,
            env=env,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["target"], str(target.resolve()))
        self.assertEqual(payload["git"]["tracked_dirty"], "dirty")
        self.assertEqual(payload["git"]["tracked_dirty_count"], 1)
        self.assertEqual(payload["cmux"]["matches"][0]["ref"], "workspace:7")

    def test_status_supports_non_git_directory_without_cmux(self):
        root = Path(tempfile.mkdtemp(prefix="lab-cli-plain-"))
        self.addCleanup(shutil.rmtree, root, True)
        cli = self.make_lab(root)
        target = root / "plain"
        target.mkdir()
        _, env = self.make_fake_bin(root)

        result = self.run_cli(
            cli,
            ["status", "--json", str(target)],
            cwd=root,
            env=env,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["git"]["is_repo"])
        self.assertFalse(payload["cmux"]["installed"])

    def test_status_current_agent_uses_validated_path(self):
        root = self.make_dir("lab-cli-current-")
        cli = self.make_lab(root)
        target = root / "agent"
        target.mkdir()
        checker = cli.parent / "check-current-agent"
        checker.write_text(
            "#!/usr/bin/env bash\n"
            "[[ \"${1:-}\" == --print-path ]] || exit 2\n"
            f"printf '%s\\n' {str(target)!r}\n",
            encoding="utf-8",
        )
        checker.chmod(0o755)
        _, env = self.make_fake_bin(root)

        result = self.run_cli(
            cli,
            ["status", "--current-agent", "--json"],
            cwd=root,
            env=env,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["target"], str(target.resolve()))

    def test_status_git_timeout_is_unknown_and_non_blocking(self):
        root = self.make_dir("lab-cli-timeout-")
        cli = self.make_lab(root)
        target = root / "target"
        target.mkdir()
        fake_bin, env = self.make_fake_bin(root)
        git = fake_bin / "git"
        git.write_text(
            f"#!{sys.executable}\n"
            "import time\n"
            "time.sleep(10)\n",
            encoding="utf-8",
        )
        git.chmod(0o755)

        started = time.monotonic()
        result = self.run_cli(
            cli,
            ["status", "--json", str(target)],
            cwd=root,
            env=env,
        )
        elapsed = time.monotonic() - started

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["git"]["tracked_dirty"], "unknown")
        self.assertIn("timed out", payload["git"]["error"])
        self.assertLess(elapsed, 4)

    def test_doctor_json_runs_native_parity_once_and_checks_cmux(self):
        root = self.make_dir("lab-cli-doctor-")
        cli = self.make_lab(root)
        fake_bin, env = self.make_fake_bin(root)
        cmux = fake_bin / "cmux"
        cmux.write_text(
            f"#!{sys.executable}\n"
            "import sys\n"
            "args = sys.argv[1:]\n"
            "if args == ['--version']:\n"
            "    print('cmux 0.64.20')\n"
            "elif args == ['new-workspace', '--help']:\n"
            "    print('--layout')\n"
            "elif args == ['tree', '--help']:\n"
            "    print('--json')\n"
            "elif args == ['workspace', '--help']:\n"
            "    print('create')\n"
            "else:\n"
            "    raise SystemExit(2)\n",
            encoding="utf-8",
        )
        cmux.chmod(0o755)

        parity_log = root / "parity.log"
        parity = cli.parent / "check-native-parity"
        parity.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, pathlib, sys\n"
            "path = pathlib.Path(os.environ['LAB_PARITY_LOG'])\n"
            "rows = path.read_text().splitlines() if path.exists() else []\n"
            "rows.append(json.dumps(sys.argv[1:]))\n"
            "path.write_text('\\n'.join(rows) + '\\n')\n"
            "print(json.dumps({'ok': True, 'static': {'ok': True}}))\n",
            encoding="utf-8",
        )
        parity.chmod(0o755)
        env["LAB_PARITY_LOG"] = str(parity_log)

        result = self.run_cli(
            cli,
            ["doctor", "--live", "--json"],
            cwd=root,
            env=env,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["cmux"]["ok"])
        self.assertEqual(
            [json.loads(line) for line in parity_log.read_text().splitlines()],
            [["--json", "--live"]],
        )


if __name__ == "__main__":
    unittest.main()
