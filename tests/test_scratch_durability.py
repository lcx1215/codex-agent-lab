from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from lab_agents.scratch_durability import scratch_durability_report, write_snapshot


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


class ScratchDurabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp(prefix="scratch-durability-"))
        self.addCleanup(shutil.rmtree, self.tmpdir, ignore_errors=True)
        self.scratch = self.tmpdir / "workspaces" / "agent-dev-workspace" / "external" / "scratch-main-agent"
        self.owner = self.tmpdir / "workspaces" / "agent-dev-workspace" / "external" / "owner-repo"
        (self.owner / ".git").mkdir(parents=True)
        (self.scratch / "scripts" / "deploy").mkdir(parents=True)
        (self.scratch / "scripts" / "deploy" / "verify.mjs").write_text("console.log('ok')\n", encoding="utf-8")
        write_json(self.tmpdir / "registry" / "scratch-durability" / "config.json", self.config())

    def config(self) -> dict:
        return {
            "schema": "scratch-durability/v1",
            "scratch_workspaces": [
                {
                    "id": "scratch-main-agent",
                    "path": "workspaces/agent-dev-workspace/external/scratch-main-agent",
                    "artifact_classes": [
                        {
                            "id": "deploy",
                            "owner_repo": "workspaces/agent-dev-workspace/external/owner-repo",
                            "required": True,
                            "copy_policy": "copy_text",
                            "includes": ["scripts/deploy/**/*"],
                            "excludes": [],
                        }
                    ],
                }
            ],
        }

    def test_snapshot_then_report_passes(self):
        report = write_snapshot(self.tmpdir, self.config(), "snap-1")
        self.assertEqual(report["status"], "pass")

        check = scratch_durability_report(self.tmpdir)
        self.assertEqual(check["status"], "pass")
        self.assertEqual(check["summary"]["file_count"], 1)

    def test_changed_file_fails_after_snapshot(self):
        write_snapshot(self.tmpdir, self.config(), "snap-1")
        (self.scratch / "scripts" / "deploy" / "verify.mjs").write_text("console.log('changed')\n", encoding="utf-8")

        check = scratch_durability_report(self.tmpdir)
        self.assertEqual(check["status"], "fail")
        codes = {issue["code"] for issue in check["issues"]}
        self.assertIn("SCRATCH_FILE_STALE_CAPTURE", codes)

    def test_new_file_fails_after_snapshot(self):
        write_snapshot(self.tmpdir, self.config(), "snap-1")
        (self.scratch / "scripts" / "deploy" / "new.mjs").write_text("console.log('new')\n", encoding="utf-8")

        check = scratch_durability_report(self.tmpdir)
        self.assertEqual(check["status"], "fail")
        codes = {issue["code"] for issue in check["issues"]}
        self.assertIn("SCRATCH_FILE_UNCAPTURED", codes)

    def test_secret_like_capture_is_fail_closed(self):
        (self.scratch / "scripts" / "deploy" / ".env").write_text("NO_SECRET_VALUE=1\n", encoding="utf-8")
        config = self.config()
        config["scratch_workspaces"][0]["artifact_classes"][0]["includes"] = ["scripts/deploy/.env"]

        report = write_snapshot(self.tmpdir, config, "snap-1")
        self.assertEqual(report["status"], "fail")
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("SCRATCH_SECRET_LIKE_CAPTURE", codes)


if __name__ == "__main__":
    unittest.main()
