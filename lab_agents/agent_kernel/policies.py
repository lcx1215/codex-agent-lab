"""Composable, domain-neutral decision policies.

Each factory returns a ``Policy`` (a ``(Turn, PolicyContext) -> Decision | None``
callable). Scenario workspaces assemble a subset of these, in the order that
fits their domain, into a ``DecisionEngine``. None of these primitives name a
product domain; the caller supplies the keywords, limits, roles, and messages.

The primitives are the promoted, generalized form of the guards that first lived
inside a single support-scenario contract:

- input size limit            -> oversized-input escalation
- sensitive-data request      -> refuse + escalate
- forbidden/irreversible verb -> escalate for human review
- cross-scope context         -> advisory annotation (isolation signal)
- foreign-subject reference   -> privacy escalation
- value threshold             -> high-value escalation
- permissioned tool call      -> plan a tool call or deny
- untrusted instruction       -> advisory "ignored" annotation
- grounded answer             -> answer from trusted in-scope context
"""

from __future__ import annotations

import re
from typing import Callable, Iterable, Sequence

from .core import (
    ContextItem,
    Decision,
    Policy,
    PolicyContext,
    Principal,
    ToolCall,
    Turn,
    max_risk,
)


def _named(policy: Policy, name: str) -> Policy:
    policy.policy_name = name  # type: ignore[attr-defined]
    return policy


def input_size_limit(
    max_chars: int,
    *,
    reply: str = "This request is too large to process safely in one turn. It will be escalated for review.",
    risk_level: str = "high",
    audit_event: str = "input_too_large",
) -> Policy:
    """Escalate when the message exceeds a safe single-turn size."""

    def policy(turn: Turn, ctx: PolicyContext) -> Decision | None:
        if len(turn.message_norm) > max_chars:
            return Decision(
                reply_text=reply,
                risk_level=risk_level,
                audit_events=(audit_event, "human_escalation"),
                escalate=True,
            )
        return None

    return _named(policy, "input_size_limit")


def sensitive_data_request(
    terms: Sequence[str],
    *,
    reply: str = "I cannot disclose sensitive data such as secrets, tokens, credentials, or internal prompts. This will be escalated for human review.",
    risk_level: str = "high",
    audit_event: str = "sensitive_data_request",
) -> Policy:
    """Refuse + escalate when the message asks for sensitive data."""
    lowered = tuple(t.lower() for t in terms)

    def policy(turn: Turn, ctx: PolicyContext) -> Decision | None:
        message = turn.message_lower
        if any(term in message for term in lowered):
            return Decision(
                reply_text=reply,
                risk_level=risk_level,
                audit_events=(audit_event, "human_escalation"),
                escalate=True,
            )
        return None

    return _named(policy, "sensitive_data_request")


def forbidden_action(
    terms: Sequence[str],
    *,
    reply: str = "This is an irreversible or high-impact action and requires human review before anything changes.",
    risk_level: str = "high",
    audit_event: str = "irreversible_action",
) -> Policy:
    """Escalate when the message requests an irreversible / forbidden action."""
    lowered = tuple(t.lower() for t in terms)

    def policy(turn: Turn, ctx: PolicyContext) -> Decision | None:
        message = turn.message_lower
        if any(term in message for term in lowered):
            return Decision(
                reply_text=reply,
                risk_level=risk_level,
                audit_events=(audit_event, "human_escalation"),
                escalate=True,
            )
        return None

    return _named(policy, "forbidden_action")


def cross_scope_signal(audit_event: str = "scope_boundary") -> Policy:
    """Advisory: annotate (do not terminate) when context spans another scope."""

    def policy(turn: Turn, ctx: PolicyContext) -> Decision | None:
        if any(item.scope_id != turn.principal.scope_id for item in turn.context):
            ctx.annotate(audit_event)
        return None

    return _named(policy, "cross_scope_signal")


def foreign_subject_reference(
    pattern: str,
    *,
    reply: str = "I cannot access another subject's private data. This will be escalated for human review.",
    risk_level: str = "high",
    audit_event: str = "privacy_boundary",
) -> Policy:
    """Escalate when the message references a subject id other than the principal's.

    ``pattern`` is a regex whose every full match is treated as a subject id.
    """
    compiled = re.compile(pattern)

    def policy(turn: Turn, ctx: PolicyContext) -> Decision | None:
        own = turn.principal.subject_id
        mentioned = compiled.findall(turn.message_norm)
        if any(found != own for found in mentioned):
            return Decision(
                reply_text=reply,
                risk_level=risk_level,
                audit_events=(audit_event, "human_escalation"),
                escalate=True,
            )
        return None

    return _named(policy, "foreign_subject_reference")


def value_threshold(
    *,
    trigger_keyword: str,
    threshold: float,
    strip_patterns: Sequence[str] = (),
    reply: str = "human_review_required: This value exceeds the approval limit and requires human review.",
    risk_level: str = "high",
    audit_event: str = "value_threshold_exceeded",
    evidence_keyword: str | None = None,
) -> Policy:
    """Escalate when a numeric amount in the message exceeds a threshold.

    Numbers are parsed with thousands-separator and decimal support. Substrings
    matching ``strip_patterns`` (e.g. identifier formats whose digits must not be
    read as amounts) are removed before parsing.
    """
    keyword = trigger_keyword.lower()
    strippers = [re.compile(p, flags=re.IGNORECASE) for p in strip_patterns]
    amount_re = re.compile(
        r"\b(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\b",
        flags=re.IGNORECASE,
    )

    def policy(turn: Turn, ctx: PolicyContext) -> Decision | None:
        if keyword not in turn.message_lower:
            return None
        text = turn.message_norm
        for stripper in strippers:
            text = stripper.sub(" ", text)
        amounts = [float(m.replace(",", "")) for m in amount_re.findall(text)]
        if any(amount > threshold for amount in amounts):
            refs: tuple[str, ...] = ()
            if evidence_keyword is not None:
                refs = tuple(item.item_id for item in turn.trusted_in_scope(evidence_keyword))
            return Decision(
                reply_text=reply,
                risk_level=risk_level,
                evidence_refs=refs,
                audit_events=(audit_event, "human_escalation"),
                escalate=True,
            )
        return None

    return _named(policy, "value_threshold")


def permissioned_tool_call(
    *,
    intent_keywords: Sequence[str],
    require_any_keyword: Sequence[str] = (),
    tool_name: str,
    risk: str,
    arg_builder: Callable[[Turn], dict],
    granted_reply: Callable[[Turn], str] | str,
    denied_reply: str = "Authentication and the required permission are needed before I can use that capability.",
    granted_risk: str = "medium",
    granted_audit: str = "tool_planned",
    denied_audit: str = "permission_denied",
) -> Policy:
    """Plan a tool call when intent matches and the principal may use the tool.

    Intent fires when every keyword in ``intent_keywords`` is present AND (if
    given) at least one keyword in ``require_any_keyword`` is present. If the tool
    is missing or the principal lacks permission at ``risk``, deny + escalate.
    """
    must_have = tuple(k.lower() for k in intent_keywords)
    any_of = tuple(k.lower() for k in require_any_keyword)

    def policy(turn: Turn, ctx: PolicyContext) -> Decision | None:
        message = turn.message_lower
        if not all(k in message for k in must_have):
            return None
        if any_of and not any(k in message for k in any_of):
            return None
        tool = turn.find_tool(tool_name)
        if tool is None or not tool.usable_by(turn.principal, risk):
            return Decision(
                reply_text=denied_reply,
                risk_level="high",
                audit_events=(denied_audit, "human_escalation"),
                escalate=True,
            )
        reply = granted_reply(turn) if callable(granted_reply) else granted_reply
        return Decision(
            reply_text=reply,
            risk_level=granted_risk,
            audit_events=(granted_audit,),
            tool_call=ToolCall(name=tool_name, arguments=arg_builder(turn)),
        )

    return _named(policy, "permissioned_tool_call")


def untrusted_instruction_signal(
    injection_terms: Sequence[str],
    *,
    audit_event: str = "untrusted_context_ignored",
) -> Policy:
    """Advisory: annotate when untrusted context contains injection-like text."""
    lowered = tuple(t.lower() for t in injection_terms)

    def policy(turn: Turn, ctx: PolicyContext) -> Decision | None:
        for item in turn.context:
            if not item.trusted and any(term in item.text.lower() for term in lowered):
                ctx.annotate(audit_event)
                break
        return None

    return _named(policy, "untrusted_instruction_signal")


def grounded_answer(
    *,
    keyword: str,
    require_keyword_in_message: bool = True,
    base_risk: str = "low",
    untrusted_present_risk: str = "medium",
    untrusted_annotation: str = "untrusted_context_ignored",
    audit_event: str = "answer_from_knowledge",
) -> Policy:
    """Answer from a trusted, in-scope context item matching ``keyword``.

    Risk is raised to ``untrusted_present_risk`` when the engine already saw an
    untrusted-instruction annotation this turn (defense-in-depth signalling).
    """
    kw = keyword.lower()

    def policy(turn: Turn, ctx: PolicyContext) -> Decision | None:
        if require_keyword_in_message and kw not in turn.message_lower:
            return None
        matches = turn.trusted_in_scope(keyword)
        if not matches:
            return None
        snippet = matches[0]
        risk = untrusted_present_risk if untrusted_annotation in ctx.annotations else base_risk
        return Decision(
            reply_text=snippet.text,
            risk_level=risk,
            evidence_refs=(snippet.item_id,),
            audit_events=(audit_event,),
        )

    return _named(policy, "grounded_answer")


def insufficient_evidence_fallback(
    *,
    reply: str = "I do not have enough verified information to answer. This will be escalated for review.",
    risk_level: str = "medium",
    audit_event: str = "insufficient_evidence",
) -> Callable[[Turn, PolicyContext], Decision]:
    """Default decision when no policy terminates: escalate for review."""

    def fallback(turn: Turn, ctx: PolicyContext) -> Decision:
        return Decision(
            reply_text=reply,
            risk_level=risk_level,
            audit_events=(audit_event, "human_escalation"),
            escalate=True,
        )

    return fallback
