"""Domain-neutral batch eval harness for kernel-based agents.

Any agent family that exposes a ``DecisionEngine`` (or a ``decide(turn) ->
Decision`` callable) can be evaluated here. Scenarios are JSONL lines mapping a
neutral ``Turn`` to expected ``Decision`` fields, so eval is not tied to any one
domain. This is the promoted form of the per-scenario eval runner that first
lived inside a support workspace.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from .core import (
    ContextItem,
    Decision,
    Principal,
    Tool,
    Turn,
)

DecideFn = Callable[[Turn], Decision]

# A fixture may request an oversized message without embedding the characters.
# REPEAT_<n> expands to n 'a' characters at load time.
_REPEAT_PREFIX = "REPEAT_"


def _expand_message(message: str) -> str:
    if message.startswith(_REPEAT_PREFIX):
        try:
            return "a" * int(message.split("_", 1)[1])
        except ValueError:
            return message
    return message


def build_turn(raw: Mapping[str, Any]) -> Turn:
    """Build a neutral Turn from a fixture dict."""
    p = raw["principal"]
    return Turn(
        message=_expand_message(raw["message"]),
        principal=Principal(
            subject_id=p["subject_id"],
            scope_id=p["scope_id"],
            authenticated=p.get("authenticated", False),
            roles=tuple(p.get("roles", [])),
        ),
        context=tuple(
            ContextItem(
                item_id=c["item_id"],
                scope_id=c["scope_id"],
                title=c.get("title", ""),
                text=c.get("text", ""),
                trusted=c.get("trusted", False),
                tags=tuple(c.get("tags", [])),
            )
            for c in raw.get("context", [])
        ),
        tools=tuple(
            Tool(
                name=t["name"],
                required_role=t["required_role"],
                allowed_risks=tuple(t["allowed_risks"]),
                description=t.get("description", ""),
            )
            for t in raw.get("tools", [])
        ),
        history=tuple(raw.get("history", [])),
    )


@dataclass(frozen=True)
class ScenarioOutcome:
    scenario_id: str
    passed: bool
    failures: tuple[str, ...]
    planned_tool: bool
    escalated: bool


def check_expectations(expect: Mapping[str, Any], result: Decision) -> tuple[str, ...]:
    failures: list[str] = []
    if "risk_level" in expect and result.risk_level != expect["risk_level"]:
        failures.append(f"risk_level={result.risk_level!r} != {expect['risk_level']!r}")
    if "escalate" in expect and result.escalate != expect["escalate"]:
        failures.append(f"escalate={result.escalate} != {expect['escalate']}")
    if "tool_call_name" in expect:
        got = result.tool_call.name if result.tool_call else None
        if got != expect["tool_call_name"]:
            failures.append(f"tool_call={got!r} != {expect['tool_call_name']!r}")
    if "evidence_refs" in expect and list(result.evidence_refs) != expect["evidence_refs"]:
        failures.append(f"evidence_refs={list(result.evidence_refs)} != {expect['evidence_refs']}")
    for event in expect.get("audit_events_include", []):
        if event not in result.audit_events:
            failures.append(f"missing audit event {event!r} in {list(result.audit_events)}")
    if "decided_by" in expect and result.decided_by != expect["decided_by"]:
        failures.append(f"decided_by={result.decided_by!r} != {expect['decided_by']!r}")
    return tuple(failures)


def run_scenarios(decide: DecideFn, lines: Iterable[str]) -> list[ScenarioOutcome]:
    outcomes: list[ScenarioOutcome] = []
    for line_no, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        raw = json.loads(line)
        result = decide(build_turn(raw["input"]))
        failures = check_expectations(raw.get("expect", {}), result)
        outcomes.append(
            ScenarioOutcome(
                scenario_id=raw.get("id", f"line-{line_no}"),
                passed=not failures,
                failures=failures,
                planned_tool=result.tool_call is not None,
                escalated=result.escalate,
            )
        )
    return outcomes


def run_file(decide: DecideFn, path: str | Path) -> list[ScenarioOutcome]:
    text = Path(path).read_text(encoding="utf-8")
    return run_scenarios(decide, text.splitlines())


def disposition_matrix(outcomes: Iterable[ScenarioOutcome]) -> dict[str, int]:
    """Tool-planning vs escalation, the two main agent dispositions."""
    matrix = {
        "tool_planned_and_escalated": 0,
        "tool_planned_not_escalated": 0,
        "no_tool_and_escalated": 0,
        "no_tool_not_escalated": 0,
    }
    for o in outcomes:
        if o.planned_tool and o.escalated:
            matrix["tool_planned_and_escalated"] += 1
        elif o.planned_tool:
            matrix["tool_planned_not_escalated"] += 1
        elif o.escalated:
            matrix["no_tool_and_escalated"] += 1
        else:
            matrix["no_tool_not_escalated"] += 1
    return matrix


def summarize(outcomes: list[ScenarioOutcome]) -> dict[str, Any]:
    passed = sum(1 for o in outcomes if o.passed)
    return {
        "total": len(outcomes),
        "passed": passed,
        "failed": len(outcomes) - passed,
        "disposition_matrix": disposition_matrix(outcomes),
        "scenarios": [
            {"id": o.scenario_id, "passed": o.passed, "failures": list(o.failures)}
            for o in outcomes
        ],
    }
