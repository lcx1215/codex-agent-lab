import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = LAB_ROOT / "scripts" / "open-workbench"
TEST_TMP_ROOT = LAB_ROOT / ".tmp" / "tests"
FAKE_CMUX = r"""#!/usr/bin/env python3
import json
import os
import pathlib
import sys

state_path = pathlib.Path(os.environ["FAKE_CMUX_STATE"])
log_path = pathlib.Path(os.environ["FAKE_CMUX_LOG"])
args = sys.argv[1:]
with log_path.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(args) + "\n")

def load():
    if state_path.exists():
        return json.loads(state_path.read_text(encoding="utf-8"))
    return {"running": False, "next": 1, "workspaces": []}

def save(state):
    state_path.write_text(json.dumps(state), encoding="utf-8")

def option(name):
    index = args.index(name)
    return args[index + 1]

def panes_from_layout(node, counter):
    if "pane" in node:
        surfaces = []
        for surface in node["pane"].get("surfaces", []):
            surfaces.append({
                "id": f"surface-{counter[0]}",
                "ref": f"surface:{counter[0]}",
                "type": surface.get("type", "terminal"),
                "title": surface.get("name", ""),
                "tty": f"/dev/ttys{counter[0]:03d}",
                "focused": bool(surface.get("focus")),
            })
            counter[0] += 1
        return [{"surfaces": surfaces}]
    panes = []
    for child in node.get("children", []):
        panes.extend(panes_from_layout(child, counter))
    return panes

state = load()
if args == ["--version"]:
    print("cmux 0.64.20 (100) [test]")
    raise SystemExit(0)
if args == ["new-workspace", "--help"]:
    print("new-workspace --layout <json>")
    raise SystemExit(0)
if args == ["tree", "--help"]:
    print("tree --json")
    raise SystemExit(0)
if args == ["workspace", "--help"]:
    print("workspace create")
    raise SystemExit(0)
if args == ["ping"]:
    if state["running"]:
        print("PONG")
        raise SystemExit(0)
    print("Error: Failed to connect to socket (Connection refused)", file=sys.stderr)
    raise SystemExit(1)
if len(args) == 1 and pathlib.Path(args[0]).is_dir():
    state["running"] = True
    number = state["next"]
    state["next"] += 1
    state["workspaces"] = [{
        "id": f"uuid-{number}",
        "ref": f"workspace:{number}",
        "title": os.environ.get("FAKE_CMUX_BOOTSTRAP_TITLE", pathlib.Path(args[0]).name),
        "description": None,
        "selected": True,
        "panes": [{
            "surfaces": [{
                "id": f"surface-bootstrap-{number}",
                "ref": f"surface:{number}",
                "type": "terminal",
                "title": "Shell",
                "tty": f"/dev/ttys{number:03d}",
                "focused": True,
            }]
        }],
    }]
    save(state)
    print("OK")
    raise SystemExit(0)

json_mode = False
if args and args[0] == "--json":
    json_mode = True
    args = args[1:]

if args and args[0] == "tree":
    rows = state["workspaces"]
    if "--workspace" in args:
        target = option("--workspace")
        rows = [row for row in rows if target in (row["id"], row["ref"])]
    print(json.dumps({
        "windows": [{
            "id": "window-1",
            "ref": "window:1",
            "workspaces": rows,
        }]
    }))
    raise SystemExit(0)

if args[:2] == ["workspace", "create"]:
    if os.environ.get("FAKE_CMUX_CREATE_FAIL") == "1":
        print("create failed", file=sys.stderr)
        raise SystemExit(1)
    number = state["next"]
    state["next"] += 1
    layout = json.loads(option("--layout"))
    workspace = {
        "id": f"uuid-{number}",
        "ref": f"workspace:{number}",
        "title": option("--name"),
        "description": option("--description"),
        "selected": True,
        "panes": panes_from_layout(layout, [number * 10]),
    }
    state["workspaces"].append(workspace)
    save(state)
    print(json.dumps({"workspace_id": workspace["id"], "workspace_ref": workspace["ref"]}))
    raise SystemExit(0)

if args[:2] == ["workspace", "close"]:
    target = args[2]
    state["workspaces"] = [
        row for row in state["workspaces"] if target not in (row["id"], row["ref"])
    ]
    save(state)
    print("OK")
    raise SystemExit(0)

if args and args[0] in ("focus-window", "select-workspace"):
    print("OK")
    raise SystemExit(0)

print("unsupported fake cmux command: " + repr(args), file=sys.stderr)
raise SystemExit(2)
"""


class OpenWorkbenchTests(unittest.TestCase):
    def make_dir(self, prefix: str) -> Path:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
        root = Path(tempfile.mkdtemp(prefix=prefix, dir=TEST_TMP_ROOT))
        self.addCleanup(shutil.rmtree, root, True)
        return root

    def fake_cmux_env(
        self,
        root: Path,
        *,
        running: bool = True,
        workspaces: list[dict] | None = None,
    ) -> tuple[dict[str, str], Path, Path]:
        fake_bin = root / "fake-bin"
        fake_bin.mkdir()
        log = root / "cmux.log"
        state = root / "cmux-state.json"
        state.write_text(
            json.dumps(
                {
                    "running": running,
                    "next": 20,
                    "workspaces": workspaces or [],
                }
            ),
            encoding="utf-8",
        )
        cmux = fake_bin / "cmux"
        cmux.write_text(FAKE_CMUX, encoding="utf-8")
        cmux.chmod(0o755)
        opener = fake_bin / "open"
        opener.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        opener.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}:{Path(sys.executable).parent}:/usr/bin:/bin"
        env["FAKE_CMUX_LOG"] = str(log)
        env["FAKE_CMUX_STATE"] = str(state)
        env["OPEN_WORKBENCH_OPEN_BIN"] = str(opener)
        return env, state, log

    def run_script(
        self,
        args: list[str],
        *,
        cwd: Path,
        env: dict[str, str],
        script: Path = SCRIPT,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(script), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    @staticmethod
    def marker(path: Path) -> str:
        return "agent-lab:v1:" + hashlib.sha256(os.fsencode(str(path.resolve()))).hexdigest()

    def healthy_workspace(self, path: Path, number: int = 3) -> dict:
        titles = ("Codex CLI", "Claude Code", "Shell")
        return {
            "id": f"uuid-{number}",
            "ref": f"workspace:{number}",
            "title": path.name,
            "description": self.marker(path),
            "selected": True,
            "panes": [
                {
                    "surfaces": [
                        {
                            "id": f"surface-{number}-{index}",
                            "ref": f"surface:{number}{index}",
                            "type": "terminal",
                            "title": title,
                            "tty": f"/dev/ttys{number}{index}",
                            "focused": title == "Shell",
                        }
                    ]
                }
                for index, title in enumerate(titles)
            ],
        }

    def test_default_cwd_creates_three_shells_without_repo_mutation(self):
        root = self.make_dir("workbench-default-")
        repo = root / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        before = subprocess.run(
            ["git", "status", "--porcelain=v1", "-uall"],
            cwd=repo,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        env, state_path, log_path = self.fake_cmux_env(root)

        result = self.run_script([], cwd=repo, env=env)

        after = subprocess.run(
            ["git", "status", "--porcelain=v1", "-uall"],
            cwd=repo,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        state = json.loads(state_path.read_text(encoding="utf-8"))
        workspace = state["workspaces"][0]
        titles = [
            pane["surfaces"][0]["title"]
            for pane in workspace["panes"]
        ]
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK: created", result.stdout)
        self.assertEqual(titles, ["Codex CLI", "Claude Code", "Shell"])
        self.assertEqual(workspace["description"], self.marker(repo))
        self.assertEqual(after, before)
        commands = [json.loads(line) for line in log_path.read_text().splitlines()]
        self.assertFalse(any("--help" in command for command in commands))
        self.assertFalse(any(command == ["--version"] for command in commands))

    def test_space_path_resolves_to_physical_directory(self):
        root = self.make_dir("workbench-space-")
        physical = root / "project with spaces"
        physical.mkdir()
        alias = root / "project-link"
        alias.symlink_to(physical, target_is_directory=True)
        env, state_path, _ = self.fake_cmux_env(root)

        result = self.run_script([str(alias)], cwd=root, env=env)

        state = json.loads(state_path.read_text(encoding="utf-8"))
        workspace = state["workspaces"][0]
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(workspace["title"], physical.name)
        self.assertEqual(workspace["description"], self.marker(physical))

    def test_dry_run_does_not_create_workspace(self):
        root = self.make_dir("workbench-dry-")
        target = root / "target"
        target.mkdir()
        env, state_path, _ = self.fake_cmux_env(root)

        result = self.run_script(["--dry-run", str(target)], cwd=root, env=env)

        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("workspace create", result.stdout)
        self.assertIn("--layout", result.stdout)
        self.assertEqual(state["workspaces"], [])

    def test_missing_directory_fails_closed(self):
        root = self.make_dir("workbench-missing-")
        env, state_path, _ = self.fake_cmux_env(root)

        result = self.run_script([str(root / "missing")], cwd=root, env=env)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("directory does not exist", result.stderr)
        self.assertEqual(json.loads(state_path.read_text())["workspaces"], [])

    def test_missing_cmux_fails_closed(self):
        root = self.make_dir("workbench-no-cmux-")
        env = os.environ.copy()
        env["PATH"] = f"{Path(sys.executable).parent}:/usr/bin:/bin"

        result = self.run_script([], cwd=root, env=env)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cmux is not installed", result.stderr)

    def test_current_agent_uses_validated_path(self):
        root = self.make_dir("workbench-current-")
        lab = root / "lab"
        scripts = lab / "scripts"
        scripts.mkdir(parents=True)
        bridge = scripts / "open-workbench"
        shutil.copy2(SCRIPT, bridge)
        bridge.chmod(0o755)
        agent = root / "current agent"
        agent.mkdir()
        checker = scripts / "check-current-agent"
        checker.write_text(
            "#!/usr/bin/env bash\n"
            "[[ \"${1:-}\" == --print-path ]] || exit 2\n"
            f"printf '%s\\n' {str(agent)!r}\n",
            encoding="utf-8",
        )
        checker.chmod(0o755)
        env, state_path, _ = self.fake_cmux_env(root)

        result = self.run_script(
            ["--current-agent"],
            cwd=lab,
            env=env,
            script=bridge,
        )

        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(state["workspaces"][0]["description"], self.marker(agent))

    def test_current_agent_validation_failure_does_not_create_workspace(self):
        root = self.make_dir("workbench-current-fail-")
        lab = root / "lab"
        scripts = lab / "scripts"
        scripts.mkdir(parents=True)
        bridge = scripts / "open-workbench"
        shutil.copy2(SCRIPT, bridge)
        bridge.chmod(0o755)
        checker = scripts / "check-current-agent"
        checker.write_text("#!/usr/bin/env bash\nexit 7\n", encoding="utf-8")
        checker.chmod(0o755)
        env, state_path, _ = self.fake_cmux_env(root)

        result = self.run_script(
            ["--current-agent"],
            cwd=lab,
            env=env,
            script=bridge,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("current Agent validation failed", result.stderr)
        self.assertEqual(json.loads(state_path.read_text())["workspaces"], [])

    def test_existing_healthy_workspace_is_reused(self):
        root = self.make_dir("workbench-reuse-")
        target = root / "target"
        target.mkdir()
        existing = self.healthy_workspace(target)
        env, state_path, log_path = self.fake_cmux_env(root, workspaces=[existing])

        result = self.run_script([str(target)], cwd=root, env=env)

        state = json.loads(state_path.read_text(encoding="utf-8"))
        log = log_path.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK: reused workspace:3", result.stdout)
        self.assertEqual(len(state["workspaces"]), 1)
        self.assertNotIn('"create"', log)

    def test_check_mode_is_read_only(self):
        root = self.make_dir("workbench-check-")
        target = root / "target"
        target.mkdir()
        existing = self.healthy_workspace(target)
        env, state_path, log_path = self.fake_cmux_env(root, workspaces=[existing])

        result = self.run_script(["--check", str(target)], cwd=root, env=env)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK: checked workspace:3", result.stdout)
        self.assertEqual(
            json.loads(state_path.read_text(encoding="utf-8"))["workspaces"],
            [existing],
        )
        log = log_path.read_text(encoding="utf-8")
        self.assertNotIn("focus-window", log)
        self.assertNotIn("select-workspace", log)

    def test_cold_start_replaces_only_bootstrap_workspace(self):
        root = self.make_dir("workbench-cold-")
        target = root / "target"
        target.mkdir()
        env, state_path, log_path = self.fake_cmux_env(root, running=False)

        result = self.run_script([str(target)], cwd=root, env=env)

        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(state["workspaces"]), 1)
        self.assertEqual(state["workspaces"][0]["description"], self.marker(target))
        commands = [json.loads(line) for line in log_path.read_text().splitlines()]
        self.assertIn([str(target.resolve())], commands)
        self.assertTrue(any(command[:2] == ["workspace", "close"] for command in commands))

    def test_cold_start_accepts_bootstrap_title_as_directory_path(self):
        root = self.make_dir("workbench-cold-path-title-")
        target = root / "target"
        target.mkdir()
        env, state_path, _ = self.fake_cmux_env(root, running=False)
        env["FAKE_CMUX_BOOTSTRAP_TITLE"] = str(target)

        result = self.run_script([str(target)], cwd=root, env=env)

        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(state["workspaces"]), 1)
        self.assertEqual(state["workspaces"][0]["description"], self.marker(target))

    def test_invalid_existing_workspace_is_focused_then_rejected(self):
        root = self.make_dir("workbench-drift-")
        target = root / "target"
        target.mkdir()
        invalid = self.healthy_workspace(target)
        invalid["panes"] = invalid["panes"][:1]
        env, state_path, log_path = self.fake_cmux_env(root, workspaces=[invalid])

        result = self.run_script([str(target)], cwd=root, env=env)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("existing workspace is invalid", result.stderr)
        self.assertEqual(len(json.loads(state_path.read_text())["workspaces"]), 1)
        log = log_path.read_text()
        self.assertIn("focus-window", log)
        self.assertNotIn('"create"', log)

    def test_duplicate_marker_fails_without_mutation(self):
        root = self.make_dir("workbench-duplicate-")
        target = root / "target"
        target.mkdir()
        first = self.healthy_workspace(target, 3)
        second = self.healthy_workspace(target, 4)
        env, state_path, _ = self.fake_cmux_env(
            root,
            workspaces=[first, second],
        )

        result = self.run_script([str(target)], cwd=root, env=env)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("multiple Agent Lab workspaces", result.stderr)
        self.assertEqual(len(json.loads(state_path.read_text())["workspaces"]), 2)

    def test_creation_failure_preserves_cold_start_bootstrap(self):
        root = self.make_dir("workbench-create-fail-")
        target = root / "target"
        target.mkdir()
        env, state_path, _ = self.fake_cmux_env(root, running=False)
        env["FAKE_CMUX_CREATE_FAIL"] = "1"

        result = self.run_script([str(target)], cwd=root, env=env)

        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(state["workspaces"]), 1)
        self.assertIsNone(state["workspaces"][0]["description"])

    def test_cold_start_does_not_claim_unproven_bootstrap_workspace(self):
        root = self.make_dir("workbench-bootstrap-drift-")
        target = root / "target"
        target.mkdir()
        env, state_path, log_path = self.fake_cmux_env(root, running=False)
        env["FAKE_CMUX_BOOTSTRAP_TITLE"] = "Restored Workspace"

        result = self.run_script([str(target)], cwd=root, env=env)

        state = json.loads(state_path.read_text(encoding="utf-8"))
        commands = [json.loads(line) for line in log_path.read_text().splitlines()]
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot prove ownership", result.stderr)
        self.assertEqual(len(state["workspaces"]), 1)
        self.assertFalse(any(command[:2] == ["workspace", "close"] for command in commands))


if __name__ == "__main__":
    unittest.main()
