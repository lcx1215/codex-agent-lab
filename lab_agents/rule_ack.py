"""Gate 1 rule-acknowledgment门禁 for the lab.

A task in the 3-layer lab (root -> workspace -> package) must declare that it
loaded the required rule layers before it is allowed to start. This module is a
pure, deterministic gate: it does not read files or run agents, it only checks
what a task dict claims it acknowledged so Codex and Claude can both apply the
same fail-closed门禁 without slowing the edit loop.
"""
from __future__ import annotations

from typing import Any


# Rule layers each task-layer must acknowledge before it may start.
# "protocol" is the shared collaboration protocol layer every task inherits.
REQUIRED_BY_LAYER: dict[str, list[str]] = {
    "root": ["root", "protocol"],
    "workspace": ["root", "workspace", "protocol"],
    "package": ["root", "workspace", "package", "protocol"],
}


def required_layers(task: dict[str, Any]) -> list[str]:
    """Return the rule-layer keys a task MUST acknowledge before starting.

    Unknown or missing `layer` fails closed to the strictest set (package).
    """
    layer = task.get("layer")
    return list(REQUIRED_BY_LAYER.get(layer, REQUIRED_BY_LAYER["package"]))


def acknowledgment_ok(task: dict[str, Any]) -> tuple[bool, list[str]]:
    """Check that every required rule layer is present in `rule_ack`.

    Returns (True, []) when complete. Missing `rule_ack` entirely fails closed
    with ["no rule acknowledgment"]; otherwise returns (False, [missing layers]).
    """
    if "rule_ack" not in task:
        return False, ["no rule acknowledgment"]
    acked = task.get("rule_ack")
    if not isinstance(acked, list):
        return False, ["no rule acknowledgment"]
    acked_set = {item for item in acked if isinstance(item, str)}
    missing = [layer for layer in required_layers(task) if layer not in acked_set]
    if missing:
        return False, missing
    return True, []


def can_start(task: dict[str, Any]) -> tuple[bool, list[str]]:
    """Decide whether a task may transition pending -> running.

    Allowed only when acknowledgment is complete AND state == "pending".
    Returns (bool, reasons) where reasons is empty on success.
    """
    reasons: list[str] = []
    ok, missing = acknowledgment_ok(task)
    if not ok:
        reasons.extend(missing)
    state = task.get("state")
    if state != "pending":
        reasons.append(f"state must be 'pending' to start, got {state!r}")
    return (not reasons), reasons
