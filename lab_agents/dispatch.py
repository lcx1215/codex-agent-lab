"""Dispatch pipeline: the middle gate that decides which tasks may start now.

This ties the three lifecycle gates together (see docs/proposal-subagent-gates.md):
- Gate 1 (rule_ack.can_start): a task must have acknowledged its required rule
  layers before it may go pending -> running.
- Gate 2 (here): pick the next runnable tasks by dependency+priority, but never
  release more than a concurrency cap, and only release tasks that clear Gate 1.
- Gate 3 (task_verify): a task may only reach verified/done with passing checks.

Pure/testable: this module DECIDES what to dispatch; it does not itself run
subprocesses or call omx-api. The operator script wires that.
"""
from __future__ import annotations

from typing import Any

from lab_agents.rule_ack import can_start
from lab_agents.task_state import runnable_tasks

DEFAULT_CONCURRENCY = 2


def running_count(data: dict[str, Any]) -> int:
    """How many tasks are already occupying a run slot."""
    return sum(
        1
        for task in data.get("tasks", [])
        if isinstance(task, dict) and task.get("state") == "running"
    )


def dispatch_plan(data: dict[str, Any], concurrency: int = DEFAULT_CONCURRENCY) -> dict[str, Any]:
    """Decide which pending tasks to release now, fail-closed on Gate 1.

    Returns a plan dict:
      - releasable: tasks that pass Gate 1 and fit under the concurrency cap
      - blocked:    runnable-but-Gate-1-failing tasks, with reasons (not released)
      - free_slots: how many run slots remain
      - held:       runnable + Gate-1-ok tasks that did NOT fit under the cap
    """
    if not isinstance(concurrency, int) or concurrency < 1:
        raise ValueError("concurrency must be a positive integer")

    free_slots = max(0, concurrency - running_count(data))
    candidates = runnable_tasks(data)  # pending, deps done, sorted by priority

    releasable: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    held: list[dict[str, Any]] = []

    for task in candidates:
        ok, reasons = can_start(task)
        if not ok:
            blocked.append({"id": task.get("id"), "reasons": reasons})
            continue
        if len(releasable) < free_slots:
            releasable.append(task)
        else:
            held.append({"id": task.get("id")})

    return {
        "concurrency": concurrency,
        "running_before": running_count(data),
        "free_slots": free_slots,
        "releasable": releasable,
        "blocked": blocked,
        "held": held,
    }
