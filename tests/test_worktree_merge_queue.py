import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from lab_agents.worktree_merge_queue import (
    MergeQueueError,
    create_stream_worktree,
    enqueue_stream,
    merge_next,
    merge_queue_report,
    validate_merge_queue_state,
)


LAB_ROOT = Path(__file__).resolve().parents[1]


class WorktreeMergeQueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self._git("init", "-b", "main")
        self._git("config", "user.email", "lab@example.invalid")
        self._git("config", "user.name", "Lab Test")
        (self.root / ".gitignore").write_text(".worktrees/\n", encoding="utf-8")
        (self.root / "base.txt").write_text("base\n", encoding="utf-8")
        self._git("add", ".")
        self._git("commit", "-m", "base")

    def tearDown(self):
        self.tmp.cleanup()

    def _git(self, *args, cwd=None, check=True):
        return subprocess.run(
            ["git", *args],
            cwd=cwd or self.root,
            text=True,
            capture_output=True,
            check=check,
        )

    def _worktree_path(self, worktree_path):
        path = Path(worktree_path)
        return path if path.is_absolute() else self.root / path

    def _commit_in_worktree(self, worktree_path, relative_path, content, message):
        worktree_path = self._worktree_path(worktree_path)
        target = worktree_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        self._git("add", relative_path, cwd=worktree_path)
        self._git("commit", "-m", message, cwd=worktree_path)

    def test_two_parallel_worktrees_merge_back_in_fifo_order(self):
        alpha = create_stream_worktree(self.root, "alpha", branch="queue/alpha")
        beta = create_stream_worktree(self.root, "beta", branch="queue/beta")
        self._commit_in_worktree(alpha["path"], "alpha.txt", "alpha\n", "alpha edit")
        self._commit_in_worktree(beta["path"], "beta.txt", "beta\n", "beta edit")

        state = enqueue_stream(self.root, "alpha")
        state = enqueue_stream(self.root, "beta")
        first = merge_next(self.root)
        second = merge_next(self.root)

        self.assertEqual(first["stream_id"], "alpha")
        self.assertEqual(second["stream_id"], "beta")
        self.assertEqual((self.root / "alpha.txt").read_text(encoding="utf-8"), "alpha\n")
        self.assertEqual((self.root / "beta.txt").read_text(encoding="utf-8"), "beta\n")
        self.assertEqual([item["status"] for item in state["queue"]], ["queued", "queued"])
        report = merge_queue_report(self.root)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["summary"]["merged_count"], 2)

    def test_conflicting_worktree_is_refused_before_merge_and_queue_fails_closed(self):
        conflicting = create_stream_worktree(self.root, "conflict", branch="queue/conflict")
        self._commit_in_worktree(conflicting["path"], "base.txt", "stream change\n", "conflict edit")
        (self.root / "base.txt").write_text("main change\n", encoding="utf-8")
        self._git("add", "base.txt")
        self._git("commit", "-m", "main competing edit")
        enqueue_stream(self.root, "conflict")

        with self.assertRaises(MergeQueueError) as caught:
            merge_next(self.root)

        self.assertIn("conflict", str(caught.exception).lower())
        self.assertNotIn("<<<<<<<", (self.root / "base.txt").read_text(encoding="utf-8"))
        state = json.loads((self.root / "registry/worktree-merge-queue/state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["queue"][0]["status"], "refused")
        self.assertEqual(state["queue"][0]["refusal"]["reason"], "pre_merge_conflict")
        self.assertEqual((self.root / "base.txt").read_text(encoding="utf-8"), "main change\n")

    def test_state_validator_rejects_missing_worktree_branch_and_queue_shape(self):
        state = {
            "schema_version": 1,
            "worktree_root": ".worktrees/merge-queue",
            "streams": [{"id": "bad", "branch": "", "path": "../escape", "status": "active"}],
            "queue": [{"stream_id": "missing", "status": "queued"}],
            "events": [],
        }

        errors = validate_merge_queue_state(state)

        self.assertTrue(any("branch" in error for error in errors))
        self.assertTrue(any("stays under worktree_root" in error for error in errors))
        self.assertTrue(any("unknown stream" in error for error in errors))


    def test_check_merge_queue_fails_closed_when_state_file_is_missing(self):
        result = subprocess.run(
            [str(LAB_ROOT / "scripts" / "check-merge-queue"), "--root", str(self.root), "--json"],
            cwd=LAB_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any(issue["code"] == "MERGE_QUEUE_STATE_MISSING" for issue in report["issues"]))

    def test_check_merge_queue_script_reports_json_status(self):
        create_stream_worktree(self.root, "alpha", branch="queue/alpha")
        result = subprocess.run(
            [str(LAB_ROOT / "scripts" / "check-merge-queue"), "--root", str(self.root), "--json"],
            cwd=LAB_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["summary"]["stream_count"], 1)


if __name__ == "__main__":
    unittest.main()
