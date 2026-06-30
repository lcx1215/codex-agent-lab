"""Ordered decision engine for the agent behavior kernel.

The engine runs an ordered list of policies against a turn. The first policy
that returns a terminating ``Decision`` wins; advisory annotations recorded by
earlier non-terminating policies are folded into the final decision's audit
trail. A ``fallback`` produces the decision when no policy terminates.

This mirrors the "first matching guard wins, in priority order" shape that a
single scenario hard-coded as a chain of ``if`` statements, but makes the order
explicit, inspectable, and reusable across agent families.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from .core import Decision, Policy, PolicyContext, Turn, policy_name


@dataclass(frozen=True)
class Trace:
    """Which policies ran, which one terminated, and the advisory annotations."""

    evaluated: tuple[str, ...]
    terminated_by: str
    annotations: tuple[str, ...]


class DecisionEngine:
    """Compose neutral policies into one auditable decision function."""

    def __init__(
        self,
        policies: Sequence[Policy],
        fallback: Callable[[Turn, PolicyContext], Decision],
        name: str = "agent",
    ) -> None:
        if not policies:
            raise ValueError("DecisionEngine requires at least one policy")
        self._policies = tuple(policies)
        self._fallback = fallback
        self.name = name

    @property
    def policy_names(self) -> tuple[str, ...]:
        return tuple(policy_name(p) for p in self._policies)

    def decide(self, turn: Turn) -> Decision:
        decision, _ = self.decide_with_trace(turn)
        return decision

    def decide_with_trace(self, turn: Turn) -> tuple[Decision, Trace]:
        ctx = PolicyContext()
        evaluated: list[str] = []
        for policy in self._policies:
            name = policy_name(policy)
            evaluated.append(name)
            decision = policy(turn, ctx)
            if decision is not None:
                final = self._finalize(decision, ctx, name)
                return final, Trace(
                    evaluated=tuple(evaluated),
                    terminated_by=name,
                    annotations=tuple(ctx.annotations),
                )
        final = self._finalize(self._fallback(turn, ctx), ctx, "fallback")
        return final, Trace(
            evaluated=tuple(evaluated + ["fallback"]),
            terminated_by="fallback",
            annotations=tuple(ctx.annotations),
        )

    def _finalize(self, decision: Decision, ctx: PolicyContext, decided_by: str) -> Decision:
        # Stamp who decided (unless a policy set it explicitly) and fold advisory
        # annotations into the audit trail without losing the policy's own events.
        stamped = decision
        if not stamped.decided_by:
            stamped = Decision(
                reply_text=stamped.reply_text,
                risk_level=stamped.risk_level,
                evidence_refs=stamped.evidence_refs,
                audit_events=stamped.audit_events,
                tool_call=stamped.tool_call,
                escalate=stamped.escalate,
                decided_by=decided_by,
            )
        if ctx.annotations:
            # Annotations precede the terminating policy's own events so the audit
            # trail reads in the order things were observed.
            ordered = list(ctx.annotations)
            for event in stamped.audit_events:
                if event not in ordered:
                    ordered.append(event)
            stamped = Decision(
                reply_text=stamped.reply_text,
                risk_level=stamped.risk_level,
                evidence_refs=stamped.evidence_refs,
                audit_events=tuple(ordered),
                tool_call=stamped.tool_call,
                escalate=stamped.escalate,
                decided_by=stamped.decided_by,
            )
        return stamped
