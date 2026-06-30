"""Core domain-neutral data types for the agent behavior kernel.

These types deliberately avoid any single-domain vocabulary (for example,
end-user, order, or refund terms). A scenario workspace maps its domain onto these:

- ``Principal``   - whoever the agent is acting for / on behalf of, plus the
                     authorization facts the agent can rely on.
- ``ContextItem`` - a unit of retrieved/provided context (knowledge, document,
                     memory, tool output) carrying trust + isolation metadata.
- ``Tool``        - a capability the agent may invoke, with the role and risk
                     levels it is allowed to operate at.
- ``Turn``        - one decision request: a message plus the principal, context,
                     and tools available for this turn.
- ``Decision``    - the structured, auditable result of one turn.
- ``Policy``      - a single composable decision rule.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

# Ordered risk ladder shared across the kernel. Higher index = higher risk.
RISK_LEVELS: tuple[str, ...] = ("none", "low", "medium", "high", "critical")


def risk_rank(level: str) -> int:
    """Return the ordinal of a risk level; unknown levels rank as 'critical'."""
    try:
        return RISK_LEVELS.index(level)
    except ValueError:
        return len(RISK_LEVELS) - 1


def max_risk(*levels: str) -> str:
    """Return the highest risk level among the arguments ('none' if empty)."""
    if not levels:
        return "none"
    return max(levels, key=risk_rank)


@dataclass(frozen=True)
class Principal:
    """The entity the agent is acting for, plus authorization facts.

    ``subject_id`` is the isolation key for "whose private data is this" checks.
    ``scope_id`` is the multi-tenant / workspace boundary key.
    """

    subject_id: str
    scope_id: str
    authenticated: bool = False
    roles: tuple[str, ...] = ()

    def has_role(self, role: str) -> bool:
        return role in self.roles


@dataclass(frozen=True)
class ContextItem:
    """A unit of context available to the agent this turn."""

    item_id: str
    scope_id: str
    title: str
    text: str
    trusted: bool = False
    tags: tuple[str, ...] = ()

    @property
    def searchable(self) -> str:
        return f"{self.title} {self.text}".lower()


@dataclass(frozen=True)
class Tool:
    """A capability the agent may plan a call to."""

    name: str
    required_role: str
    allowed_risks: tuple[str, ...]
    description: str = ""

    def usable_by(self, principal: Principal, risk: str) -> bool:
        return (
            principal.authenticated
            and principal.has_role(self.required_role)
            and risk in self.allowed_risks
        )


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: Mapping[str, Any]


@dataclass(frozen=True)
class Turn:
    """One decision request handed to the engine."""

    message: str
    principal: Principal
    context: tuple[ContextItem, ...] = ()
    tools: tuple[Tool, ...] = ()
    history: tuple[str, ...] = ()

    @property
    def message_norm(self) -> str:
        return self.message.strip()

    @property
    def message_lower(self) -> str:
        return self.message_norm.lower()

    def find_tool(self, name: str) -> Tool | None:
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def trusted_in_scope(self, keyword: str) -> tuple[ContextItem, ...]:
        kw = keyword.lower()
        return tuple(
            item
            for item in self.context
            if item.trusted
            and item.scope_id == self.principal.scope_id
            and kw in item.searchable
        )


@dataclass(frozen=True)
class Decision:
    """Structured, auditable outcome of one turn."""

    reply_text: str
    risk_level: str = "none"
    evidence_refs: tuple[str, ...] = ()
    audit_events: tuple[str, ...] = ()
    tool_call: ToolCall | None = None
    escalate: bool = False
    decided_by: str = ""

    def with_audit(self, *events: str) -> "Decision":
        """Return a copy with extra audit events appended (de-duplicated, ordered)."""
        merged = list(self.audit_events)
        for event in events:
            if event not in merged:
                merged.append(event)
        return Decision(
            reply_text=self.reply_text,
            risk_level=self.risk_level,
            evidence_refs=self.evidence_refs,
            audit_events=tuple(merged),
            tool_call=self.tool_call,
            escalate=self.escalate,
            decided_by=self.decided_by,
        )


@dataclass(frozen=True)
class PolicyContext:
    """Mutable-ish scratch passed alongside the turn through the policy chain.

    Policies that do not terminate the turn can still record an advisory audit
    event (e.g. "untrusted_context_ignored") into ``annotations``; the engine
    folds these into the final decision's audit trail.
    """

    annotations: list[str] = field(default_factory=list)

    def annotate(self, event: str) -> None:
        if event not in self.annotations:
            self.annotations.append(event)


# A policy inspects the turn and either returns a terminating Decision or None
# (meaning "I do not apply, continue to the next policy"). It may annotate the
# shared PolicyContext as a side effect.
Policy = Callable[[Turn, PolicyContext], "Decision | None"]


def policy_name(policy: Policy) -> str:
    return getattr(policy, "policy_name", getattr(policy, "__name__", "policy"))
