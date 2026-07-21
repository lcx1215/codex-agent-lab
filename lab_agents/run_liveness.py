"""Run-record liveness analysis for the agent development environment.

The task-state kernel already detects stale *tasks* (a `running` task whose
`lease_expires_at` has passed — see ``lab_agents/task_state.py``). The symmetric
gap on the *run-record* side had no detector: a run can be written with
``started_at`` set and ``ended_at = None`` (unfinished), and nothing flagged a
run that started and then never finished — a hung or abandoned run. The
``registry/ORCHESTRATION_LAYER_STATE.md`` gap list calls this out: no scheduler
with timeout/liveness.

This module is the headless liveness seam for run records. It reads finalized
records under ``registry/runs/*/record.json`` (it does NOT execute or kill
anything — the lab has no live runtime to signal) and reports:

- ``unfinished`` runs: ``ended_at`` is null/missing.
- ``stale`` runs: unfinished AND ``started_at`` older than a deadline.
- ``ill_formed`` runs: ``ended_at`` precedes ``started_at``, or timestamps are
  unparseable.

Root-layer orchestration surface. No desktop UI. Owner lane: claude.
Mirrors the report shape of ``task_state.task_state_report`` so the dashboard
and a future gate can consume both the same way.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
RUNS_DIR_REL = "registry/runs"
# A run unfinished longer than this is considered stale/hung. Conservative
# default; the lab's real runs finalize in seconds to minutes.
DEFAULT_STALE_AFTER_SECONDS = 3600


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    # Support a trailing 'Z' as UTC (datetime.fromisoformat handles it on 3.11+,
    # but normalize defensively for older interpreters).
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def analyze_record(
    data: Any,
    *,
    now: datetime,
    stale_after_seconds: int = DEFAULT_STALE_AFTER_SECONDS,
) -> dict[str, Any]:
    """Classify a single run record. Returns {run_id, state, reason, age_seconds}.

    state is one of: finished, unfinished, stale, ill_formed.
    """
    run_id = data.get("run_id") if isinstance(data, dict) else None
    run_id = str(run_id) if run_id else "<unknown>"
    started_raw = data.get("started_at") if isinstance(data, dict) else None
    ended_raw = data.get("ended_at") if isinstance(data, dict) else None

    started = _parse_time(started_raw)
    if started is None:
        return {"run_id": run_id, "state": "ill_formed",
                "reason": "started_at missing or unparseable", "age_seconds": None}

    if ended_raw is None or (isinstance(ended_raw, str) and not ended_raw.strip()):
        age = (now - started).total_seconds()
        if age > stale_after_seconds:
            return {"run_id": run_id, "state": "stale",
                    "reason": f"unfinished for {int(age)}s (> {stale_after_seconds}s deadline)",
                    "age_seconds": int(age)}
        return {"run_id": run_id, "state": "unfinished",
                "reason": "ended_at not set yet", "age_seconds": int(age)}

    ended = _parse_time(ended_raw)
    if ended is None:
        return {"run_id": run_id, "state": "ill_formed",
                "reason": "ended_at unparseable", "age_seconds": None}
    if ended < started:
        return {"run_id": run_id, "state": "ill_formed",
                "reason": "ended_at precedes started_at", "age_seconds": None}
    return {"run_id": run_id, "state": "finished",
            "reason": "", "age_seconds": int((ended - started).total_seconds())}


def _iter_records(runs_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(runs_dir.glob("*/record.json")):
        try:
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            records.append({"run_id": path.parent.name, "started_at": None})
    return records


def run_liveness_report(
    runs_dir: Path,
    *,
    now: datetime | None = None,
    stale_after_seconds: int = DEFAULT_STALE_AFTER_SECONDS,
) -> dict[str, Any]:
    """Aggregate liveness across all run records under runs_dir.

    Report shape mirrors ``task_state.task_state_report``: a status
    (pass/warn/fail), a summary of counts, and a list of issues. ``stale`` and
    ``ill_formed`` runs are fail-worthy; ``unfinished`` (young) runs are warn.
    """
    now_dt = now or datetime.now(timezone.utc)
    analyses = [
        analyze_record(rec, now=now_dt, stale_after_seconds=stale_after_seconds)
        for rec in _iter_records(runs_dir)
    ]
    counts: dict[str, int] = {"finished": 0, "unfinished": 0, "stale": 0, "ill_formed": 0}
    for item in analyses:
        counts[item["state"]] = counts.get(item["state"], 0) + 1

    issues = [
        {"code": f"{item['state'].upper()}_RUN", "run_id": item["run_id"], "reason": item["reason"]}
        for item in analyses
        if item["state"] in ("stale", "ill_formed")
    ]
    if counts["stale"] or counts["ill_formed"]:
        status = "fail"
    elif counts["unfinished"]:
        status = "warn"
    else:
        status = "pass"

    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "summary": {
            "run_count": len(analyses),
            "finished_count": counts["finished"],
            "unfinished_count": counts["unfinished"],
            "stale_count": counts["stale"],
            "ill_formed_count": counts["ill_formed"],
            "stale_after_seconds": stale_after_seconds,
        },
        "issues": issues,
    }
