"""Gate 3 "collect/verify" filter for the lab task kernel.

This is the pure decision layer behind the收工闸 auto-review: it decides
whether a review-state task has satisfied its declared verification checks and may
be promoted to ``verified``. It does NOT execute real gates; callers pass the
check results in on the task dict so the logic stays deterministic and unit
testable. The default posture is FAIL CLOSED: a task with no declared
verification is never eligible for promotion.
"""
from __future__ import annotations

from typing import Any


def verification_ok(task: dict[str, Any]) -> tuple[bool, list[str]]:
    """Return (True, []) only if every declared check passed.

    ``task["verification"]`` must be a dict with ``checks``: a list of
    ``{"name": str, "passed": bool}``. Missing verification or empty checks
    fail closed with ``["no verification declared"]``. Any check that did not
    pass contributes its name to the failure list.
    """
    verification = task.get("verification")
    if not isinstance(verification, dict):
        return False, ["no verification declared"]
    checks = verification.get("checks")
    if not isinstance(checks, list) or not checks:
        return False, ["no verification declared"]

    failed: list[str] = []
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            failed.append(f"check[{index}] is not an object")
            continue
        name = check.get("name")
        name = name if isinstance(name, str) and name else f"check[{index}]"
        if check.get("passed") is not True:
            failed.append(name)
    return (not failed), failed


def can_promote_to_verified(task: dict[str, Any]) -> tuple[bool, list[str]]:
    """A task may go review->verified only if it is under review and verified_ok."""
    reasons: list[str] = []
    if task.get("state") != "review":
        reasons.append(f"state must be review, got {task.get('state')!r}")
    ok, failed = verification_ok(task)
    if not ok:
        reasons.extend(failed)
    return (not reasons), reasons


def promote(task: dict[str, Any], now: str) -> dict[str, Any]:
    """Return a NEW task dict promoted review->verified.

    Raises ValueError if the task is not eligible. The original dict is not
    mutated; history is copied with a new ``review->verified`` entry appended.
    """
    ok, reasons = can_promote_to_verified(task)
    if not ok:
        raise ValueError(f"cannot promote to verified: {'; '.join(reasons)}")

    promoted = dict(task)
    history = list(task.get("history", []))
    history.append({"from": "review", "to": "verified", "at": now})
    promoted["history"] = history
    promoted["state"] = "verified"
    promoted["updated_at"] = now
    return promoted
