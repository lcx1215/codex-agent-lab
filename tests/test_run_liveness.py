"""Tests for run-record liveness analysis (lab_agents/run_liveness.py)."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

from lab_agents.run_liveness import (
    analyze_record,
    run_liveness_report,
    DEFAULT_STALE_AFTER_SECONDS,
)

NOW = datetime(2026, 7, 6, 12, 0, 0, tzinfo=timezone.utc)


def rec(run_id, started, ended):
    return {"run_id": run_id, "started_at": started, "ended_at": ended}


class AnalyzeRecordTests(unittest.TestCase):
    def test_finished_run_is_finished_with_age(self):
        out = analyze_record(
            rec("r1", "2026-07-06T11:00:00+00:00", "2026-07-06T11:05:00+00:00"),
            now=NOW,
        )
        self.assertEqual(out["state"], "finished")
        self.assertEqual(out["age_seconds"], 300)

    def test_young_unfinished_run_is_unfinished_not_stale(self):
        out = analyze_record(
            rec("r2", "2026-07-06T11:59:00+00:00", None), now=NOW
        )
        self.assertEqual(out["state"], "unfinished")
        self.assertEqual(out["age_seconds"], 60)

    def test_old_unfinished_run_is_stale(self):
        out = analyze_record(
            rec("r3", "2026-07-06T10:00:00+00:00", None), now=NOW
        )
        self.assertEqual(out["state"], "stale")
        self.assertGreater(out["age_seconds"], DEFAULT_STALE_AFTER_SECONDS)

    def test_ended_before_started_is_ill_formed(self):
        out = analyze_record(
            rec("r4", "2026-07-06T11:05:00+00:00", "2026-07-06T11:00:00+00:00"),
            now=NOW,
        )
        self.assertEqual(out["state"], "ill_formed")

    def test_missing_started_is_ill_formed(self):
        out = analyze_record(rec("r5", None, None), now=NOW)
        self.assertEqual(out["state"], "ill_formed")

    def test_unparseable_ended_is_ill_formed(self):
        out = analyze_record(
            rec("r6", "2026-07-06T11:00:00+00:00", "not-a-time"), now=NOW
        )
        self.assertEqual(out["state"], "ill_formed")

    def test_trailing_z_timestamp_parses(self):
        out = analyze_record(
            rec("r7", "2026-07-06T11:00:00Z", "2026-07-06T11:01:00Z"), now=NOW
        )
        self.assertEqual(out["state"], "finished")
        self.assertEqual(out["age_seconds"], 60)


class RunLivenessReportTests(unittest.TestCase):
    def _write_runs(self, tmp: Path, records):
        for r in records:
            d = tmp / r["run_id"]
            d.mkdir(parents=True)
            (d / "record.json").write_text(json.dumps(r), encoding="utf-8")

    def test_all_finished_is_pass(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            self._write_runs(tmp, [
                rec("a", "2026-07-06T11:00:00+00:00", "2026-07-06T11:01:00+00:00"),
            ])
            report = run_liveness_report(tmp, now=NOW)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["summary"]["finished_count"], 1)

    def test_stale_run_makes_report_fail(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            self._write_runs(tmp, [
                rec("a", "2026-07-06T11:00:00+00:00", "2026-07-06T11:01:00+00:00"),
                rec("b", "2026-07-06T09:00:00+00:00", None),  # stale
            ])
            report = run_liveness_report(tmp, now=NOW)
            self.assertEqual(report["status"], "fail")
            self.assertEqual(report["summary"]["stale_count"], 1)
            self.assertTrue(any(i["code"] == "STALE_RUN" for i in report["issues"]))

    def test_young_unfinished_makes_report_warn(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            self._write_runs(tmp, [
                rec("a", "2026-07-06T11:59:30+00:00", None),  # 30s, young
            ])
            report = run_liveness_report(tmp, now=NOW)
            self.assertEqual(report["status"], "warn")
            self.assertEqual(report["summary"]["unfinished_count"], 1)

    def test_corrupt_record_counts_as_ill_formed_fail(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            d = tmp / "bad"
            d.mkdir()
            (d / "record.json").write_text("{not json", encoding="utf-8")
            report = run_liveness_report(tmp, now=NOW)
            self.assertEqual(report["status"], "fail")
            self.assertEqual(report["summary"]["ill_formed_count"], 1)


if __name__ == "__main__":
    unittest.main()
