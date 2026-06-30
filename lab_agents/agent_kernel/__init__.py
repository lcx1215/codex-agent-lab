"""Domain-neutral agent behavior kernel.

This package holds the scenario-neutral core that any large agent family in this
lab can build on: typed turn/decision contracts, a small library of composable
safety and decision policies, and an ordered decision engine. It is the promoted,
reusable form of the safety primitives that first appeared inside a single
support scenario (input-size limits, sensitive-data refusal, irreversible
action escalation, tenant/principal isolation, value-threshold escalation,
permissioned tool calls, untrusted-context handling, evidence-grounded answers,
and insufficient-evidence escalation).

The kernel does not encode any single product domain. Scenario workspaces compose
these primitives into a concrete agent contract; the lab keeps the primitives.
"""

from .core import (
    ContextItem,
    Decision,
    Policy,
    PolicyContext,
    Principal,
    Tool,
    ToolCall,
    Turn,
)
from .engine import DecisionEngine
from . import policies

__all__ = [
    "ContextItem",
    "Decision",
    "DecisionEngine",
    "Policy",
    "PolicyContext",
    "Principal",
    "Tool",
    "ToolCall",
    "Turn",
    "policies",
]
