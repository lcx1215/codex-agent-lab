import json
import tempfile
import unittest
from pathlib import Path

from lab_agents.run_record import (
    RunRecord,
    write_run_record,
    validate_record,
    _scrub,
    _cap,
    _slugify,
    SCHEMA_VERSION,
)

SHA_A = "a" * 40
SHA_B = "b" * 40


class RunRecordTests(unittest.TestCase):
    def _record(self, root: Path) -> RunRecord:
        return RunRecord(lane="claude", agent="test-agent", task="do a thing", repo_root=root)

    def test_run_id_is_sortable_and_slugged(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = self._record(Path(tmp))
            self.assertRegex(rec.run_id, r"^\d{8}T\d{6}Z-claude-do-a-thing$")

    def test_finalize_required_before_serialize(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = self._record(Path(tmp))
            with self.assertRaises(ValueError):
                rec.to_dict()
            rec.finalize("success", "done")
            self.assertEqual(rec.to_dict()["outcome"], "success")

    def test_invalid_outcome_and_change_type_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = self._record(Path(tmp))
            with self.assertRaises(ValueError):
                rec.finalize("done", "x")
            with self.assertRaises(ValueError):
                rec.record_file_change("a.py", "renamed")
            with self.assertRaises(ValueError):
                rec.record_file_change("a.py", "modified", before_sha="pending")

    def test_steps_are_ordered_and_typed(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = self._record(Path(tmp))
            rec.add_prompt("harden the audit").add_note("looked at gate").add_command(
                ["echo", "hi"], 0, "hi\n", ""
            ).add_result("green")
            kinds = [s["kind"] for s in rec.steps]
            self.assertEqual(kinds, ["prompt", "note", "command", "result"])
            self.assertEqual([s["index"] for s in rec.steps], [0, 1, 2, 3])

    def test_secret_material_is_scrubbed_from_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = self._record(Path(tmp))
            rec.add_command(
                ["cat", "cfg"],
                0,
                "line one\nAuthorization: Bearer sk-abc123\nline three\napi_key=zzz\n",
                "",
            )
            stdout = rec.steps[0]["stdout"]
            self.assertNotIn("sk-abc123", stdout)
            self.assertNotIn("zzz", stdout)
            self.assertIn("[redacted: possible secret]", stdout)
            self.assertIn("line one", stdout)
            self.assertIn("line three", stdout)

    def test_scrub_and_cap_helpers(self):
        self.assertIn("[redacted", _scrub("token=deadbeef"))
        synthetic_secret = "sk" + "-proj-example123456789"
        self.assertIn("[redacted", _scrub(f"value {synthetic_secret}"))
        self.assertEqual(_scrub("plain text"), "plain text")
        big = "x" * 9000
        capped = _cap(big, cap=100)
        self.assertLess(len(capped.encode("utf-8")), 200)
        self.assertIn("truncated", capped)

    def test_slugify_bounds_and_fallback(self):
        self.assertEqual(_slugify(""), "run")
        self.assertLessEqual(len(_slugify("a" * 100)), 32)
        self.assertEqual(_slugify("Make It Green!"), "make-it-green")

    def test_capture_command_runs_and_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = self._record(Path(tmp))
            code = rec.capture_command(["python3", "-c", "print('ok')"])
            self.assertEqual(code, 0)
            step = rec.steps[-1]
            self.assertEqual(step["kind"], "command")
            self.assertEqual(step["exit_code"], 0)
            self.assertIn("ok", step["stdout"])

    def test_capture_command_missing_binary_is_recorded_not_raised(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = self._record(Path(tmp))
            code = rec.capture_command(["definitely-not-a-real-binary-xyz"])
            self.assertEqual(code, 127)
            self.assertEqual(rec.steps[-1]["exit_code"], 127)

    def test_write_produces_record_and_latest_with_git_shas(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs_root = root / "registry" / "runs"
            rec = self._record(root)
            rec.record_file_change("lab_agents/x.py", "modified", SHA_A, SHA_B)
            rec.finalize("success", "did the thing")
            path = write_run_record(rec, runs_root=runs_root)

            self.assertTrue(path.exists())
            self.assertTrue((runs_root / "latest.json").exists())
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["schema_version"], SCHEMA_VERSION)
            self.assertEqual(data["outcome"], "success")
            self.assertEqual(data["files_changed"][0]["after_sha"], SHA_B)
            self.assertIn("git", data)
            # tmp dir is not a git repo -> head SHAs are null, not a crash.
            self.assertIsNone(data["git"]["head_before"])
            latest = json.loads((runs_root / "latest.json").read_text(encoding="utf-8"))
            self.assertEqual(latest["run_id"], data["run_id"])

    def _valid_record_dict(self, root: Path) -> dict:
        rec = self._record(root)
        rec.add_command(["echo", "hi"], 0, "hi\n", "")
        rec.record_file_change("a.py", "modified", SHA_A, SHA_B)
        rec.finalize("success", "ok")
        return rec.to_dict()

    def test_validate_accepts_a_real_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(validate_record(self._valid_record_dict(Path(tmp))), [])

    def test_validate_rejects_non_object(self):
        self.assertIn("not a JSON object", validate_record([1, 2, 3])[0])

    def test_validate_flags_missing_fields_and_bad_outcome(self):
        errs = validate_record({"schema_version": 1})
        self.assertTrue(any("missing required field" in e for e in errs))
        self.assertTrue(any("outcome must be one of" in e for e in errs))

    def test_validate_flags_bad_shas_and_step_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = self._valid_record_dict(Path(tmp))
            data["git"]["head_before"] = "not-a-sha"
            data["files_changed"][0]["after_sha"] = "pending"
            data["steps"][0]["index"] = 5
            errs = validate_record(data)
            self.assertTrue(any("git.head_before" in e for e in errs))
            self.assertTrue(any("files_changed[0].after_sha" in e for e in errs))
            self.assertTrue(any("steps[0].index" in e for e in errs))

    def test_validate_flags_command_step_missing_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = self._valid_record_dict(Path(tmp))
            del data["steps"][0]["exit_code"]
            self.assertTrue(any("command missing exit_code" in e for e in validate_record(data)))


if __name__ == "__main__":
    unittest.main()
