"""Lightweight task-state and scheduler kernel for the lab.

This is a root-layer orchestration surface: it records what should run next,
not a daemon that runs agents. The scheduler is intentionally deterministic and
small so Codex and Claude can both read the same task state without slowing the
default edit loop.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
TASKS_REL = "registry/tasks/tasks.json"
VALID_STATES = {"pending", "running", "blocked", "review", "verified", "done", "cancelled"}
TERMINAL_STATES = {"done", "cancelled"}
TRANSITIONS = {
    None: {"pending"},
    "pending": {"running", "blocked", "cancelled"},
    "running": {"blocked", "review", "cancelled"},
    "blocked": {"pending", "cancelled"},
    "review": {"running", "blocked", "verified", "cancelled"},
    "verified": {"done", "running", "cancelled"},
    "done": set(),
    "cancelled": set(),
}


def _parse_time(value: Any, field_name: str, errors: list[str], task_id: str = "registry") -> datetime | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{task_id}: {field_name} must be a non-empty ISO timestamp string")
        return None
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        errors.append(f"{task_id}: {field_name} is not a valid ISO timestamp")
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def validate_task_registry(data: Any) -> list[str]:
    """Return validation errors for a task registry. Empty means valid."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["registry must be a JSON object"]
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")

    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        errors.append("tasks must be a list")
        return errors

    seen: set[str] = set()
    task_by_id: dict[str, dict[str, Any]] = {}
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"tasks[{index}] must be an object")
            continue
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id:
            errors.append(f"tasks[{index}]: id must be a non-empty string")
            task_id = f"tasks[{index}]"
        elif task_id in seen:
            errors.append(f"{task_id}: duplicate task id")
        else:
            seen.add(task_id)
            task_by_id[task_id] = task

        for field in ("title", "lane"):
            if not isinstance(task.get(field), str) or not task.get(field):
                errors.append(f"{task_id}: {field} must be a non-empty string")
        state = task.get("state")
        if state not in VALID_STATES:
            errors.append(f"{task_id}: state must be one of {sorted(VALID_STATES)}")
        priority = task.get("priority")
        if not isinstance(priority, int):
            errors.append(f"{task_id}: priority must be an integer")
        depends_on = task.get("depends_on")
        if not isinstance(depends_on, list) or not all(isinstance(item, str) for item in depends_on):
            errors.append(f"{task_id}: depends_on must be a list of task ids")
        _parse_time(task.get("created_at"), "created_at", errors, task_id)
        _parse_time(task.get("updated_at"), "updated_at", errors, task_id)
        if "lease_expires_at" in task:
            _parse_time(task.get("lease_expires_at"), "lease_expires_at", errors, task_id)
        _validate_history(task, str(task_id), errors)

    for task in tasks:
        if not isinstance(task, dict):
            continue
        task_id = str(task.get("id", "unknown"))
        depends_on = task.get("depends_on")
        if not isinstance(depends_on, list):
            continue
        for dep in depends_on:
            if dep not in task_by_id:
                errors.append(f"{task_id}: unknown dependency {dep}")
            elif dep == task_id:
                errors.append(f"{task_id}: task cannot depend on itself")
    return errors


def _validate_history(task: dict[str, Any], task_id: str, errors: list[str]) -> None:
    history = task.get("history")
    if not isinstance(history, list) or not history:
        errors.append(f"{task_id}: history must be a non-empty list")
        return
    previous_to: str | None = None
    for index, item in enumerate(history):
        if not isinstance(item, dict):
            errors.append(f"{task_id}: history[{index}] must be an object")
            continue
        from_state = item.get("from")
        to_state = item.get("to")
        if from_state != previous_to:
            errors.append(f"{task_id}: history[{index}] from must match previous state")
        if from_state not in TRANSITIONS:
            errors.append(f"{task_id}: history[{index}] unknown from state {from_state}")
        if to_state not in VALID_STATES:
            errors.append(f"{task_id}: history[{index}] unknown to state {to_state}")
        elif to_state not in TRANSITIONS.get(from_state, set()):
            errors.append(f"{task_id}: invalid transition {from_state}->{to_state}")
        _parse_time(item.get("at"), f"history[{index}].at", errors, task_id)
        previous_to = to_state if isinstance(to_state, str) else previous_to
    if task.get("state") in VALID_STATES and previous_to != task.get("state"):
        errors.append(f"{task_id}: current state must match last history state")


def _task_map(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {task["id"]: task for task in data.get("tasks", []) if isinstance(task, dict) and isinstance(task.get("id"), str)}


def _dependency_done(task: dict[str, Any], task_by_id: dict[str, dict[str, Any]]) -> bool:
    for dep in task.get("depends_on", []):
        if task_by_id.get(dep, {}).get("state") != "done":
            return False
    return True


def runnable_tasks(data: dict[str, Any]) -> list[dict[str, Any]]:
    task_by_id = _task_map(data)
    tasks = [
        task
        for task in data.get("tasks", [])
        if isinstance(task, dict)
        and task.get("state") == "pending"
        and isinstance(task.get("priority"), int)
        and _dependency_done(task, task_by_id)
    ]
    return sorted(tasks, key=lambda task: (-int(task["priority"]), str(task.get("created_at", "")), str(task["id"])))


def next_runnable_task(data: dict[str, Any]) -> dict[str, Any] | None:
    tasks = runnable_tasks(data)
    return tasks[0] if tasks else None


def task_state_report(data: Any, now: str | None = None) -> dict[str, Any]:
    errors = validate_task_registry(data)
    now_errors: list[str] = []
    now_dt = _parse_time(now, "now", now_errors) if now else datetime.now(timezone.utc)
    stale_running: list[str] = []
    tasks = data.get("tasks", []) if isinstance(data, dict) else []
    if not errors and not now_errors:
        for task in tasks:
            if task.get("state") != "running" or not task.get("lease_expires_at"):
                continue
            lease_dt = _parse_time(task.get("lease_expires_at"), "lease_expires_at", errors, str(task.get("id")))
            if lease_dt and lease_dt < now_dt:
                stale_running.append(str(task.get("id")))

    runnable = runnable_tasks(data) if isinstance(data, dict) and not errors else []
    counts = Counter(task.get("state") for task in tasks if isinstance(task, dict))
    issues = [{"code": "INVALID_TASK_REGISTRY", "message": error} for error in errors + now_errors]
    issues.extend({"code": "STALE_RUNNING_TASK", "task_id": task_id} for task_id in stale_running)
    status = "fail" if errors or now_errors else "warn" if stale_running else "pass"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "summary": {
            "task_count": len(tasks) if isinstance(tasks, list) else 0,
            "pending_count": counts.get("pending", 0),
            "running_count": counts.get("running", 0),
            "blocked_count": counts.get("blocked", 0),
            "review_count": counts.get("review", 0),
            "verified_count": counts.get("verified", 0),
            "done_count": counts.get("done", 0),
            "cancelled_count": counts.get("cancelled", 0),
            "runnable_count": len(runnable),
            "stale_running_count": len(stale_running),
        },
        "next_task": next_runnable_task(data) if isinstance(data, dict) and not errors else None,
        "issues": issues,
    }


def read_task_registry(root: Path) -> dict[str, Any]:
    path = root / TASKS_REL
    return json_load(path)


def json_load(path: Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))
