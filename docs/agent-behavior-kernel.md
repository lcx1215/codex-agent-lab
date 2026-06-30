# Agent Behavior Kernel

The agent behavior kernel is the lab's domain-neutral core for building large
agents of *any* family. It is the promoted, reusable form of the agent-behavior
primitives that first appeared inside a single support scenario. The
lab keeps the primitives; scenario workspaces compose them into a concrete agent.

Location: `lab_agents/agent_kernel/`. No part of it names a product domain.

## Why It Exists

Before this layer, the only runnable "agent behavior" asset in the lab was a
single scenario-specific hard-coded chain of `if` guards. The
guards themselves (input-size limit, sensitive-data refusal, irreversible-action
escalation, tenant/principal isolation, value-threshold escalation, permissioned
tool calls, untrusted-context handling, evidence-grounded answers,
insufficient-evidence escalation) are needs shared by every large agent, but they
were locked to one domain and one file. That made the lab able to *develop a
single scenario-specific agent*, not *develop any large agent*.

The kernel lifts those guards into composable, configurable primitives so a new
agent family is a short composition, not a re-implementation.

## Pieces

- `core.py` - neutral types: `Principal`, `ContextItem`, `Tool`, `ToolCall`,
  `Turn`, `Decision`, `PolicyContext`, plus the shared risk ladder. No single
  domain vocabulary.
- `policies.py` - a library of policy factories. Each returns a
  `(Turn, PolicyContext) -> Decision | None` callable. The caller supplies the
  keywords, limits, roles, tools, and messages.
- `engine.py` - `DecisionEngine`: runs an ordered policy chain, first terminating
  policy wins, advisory annotations fold into the audit trail, a `fallback`
  decides when nothing terminates. `decide_with_trace` returns which policies ran.
- `eval_harness.py` - a neutral JSONL batch eval runner + disposition matrix that
  works against any `decide(turn) -> Decision` callable.

## Policy Primitives

| Primitive | Purpose |
| --- | --- |
| `input_size_limit` | Escalate oversized single-turn input |
| `sensitive_data_request` | Refuse + escalate requests for secrets/tokens/etc. |
| `forbidden_action` | Escalate irreversible / high-impact verbs |
| `cross_scope_signal` | Advisory annotation when context spans another scope |
| `foreign_subject_reference` | Escalate references to another subject's data |
| `value_threshold` | Escalate amounts over a limit (separator/decimal aware, with id-stripping) |
| `permissioned_tool_call` | Plan a tool call when intent matches and the principal may use it, else deny |
| `untrusted_instruction_signal` | Advisory annotation when untrusted context carries injection text |
| `grounded_answer` | Answer only from a trusted, in-scope context item |
| `insufficient_evidence_fallback` | Default: refuse to answer without verified evidence |

## Building A Family

```python
from lab_agents.agent_kernel import DecisionEngine, policies

def build_engine() -> DecisionEngine:
    chain = [
        policies.input_size_limit(max_chars=4000),
        policies.sensitive_data_request(terms=("api key", "password")),
        policies.permissioned_tool_call(
            intent_keywords=("metrics",), require_any_keyword=("get", "check"),
            tool_name="read_metrics", risk="medium",
            arg_builder=lambda t: {"scope": t.principal.scope_id},
            granted_reply="I can pull read-only metrics.",
        ),
        policies.grounded_answer(keyword="runbook"),
    ]
    return DecisionEngine(chain, policies.insufficient_evidence_fallback(), name="infra-ops")
```

A scenario that needs a real agent builds its chain inside its own workspace
under `workspaces/`. The lab keeps the kernel, not example products.

## Proof Of Neutrality

`tests/test_kernel_neutrality.py` builds two unrelated agent chains inline and
shows both behave correctly on the same kernel:

- an infra-ops chain (secrets refusal, destructive-op escalation, cross-team
  ownership boundary, replica-scale limit, permissioned metrics lookup, runbook
  grounding), and
- a research chain (credential refusal, cross-project boundary, permissioned
  corpus search, source grounding, no-source refusal) that deliberately omits
  `value_threshold` and `forbidden_action` to show the chain is a free
  composition, not a fixed template.

Neither chain references any support-scenario code. If the kernel were a
scenario-specific engine in disguise, both could not be expressed on it. The
proof lives in a test, not in resident demo packages.

## Verification

- `tests/test_agent_kernel.py` - core types, engine ordering/annotation/fallback,
  and the neutral JSONL eval harness.
- `tests/test_kernel_policies.py` - each primitive in isolation.
- `tests/test_kernel_neutrality.py` - two inline domains + a neutrality assertion.

All three are pure Python (no `rg` / external-binary dependency), so they run in
any lane. Run them with `python3 -m pytest tests/test_agent_kernel.py
tests/test_kernel_policies.py tests/test_kernel_neutrality.py -q`.

## Boundary

The kernel is amplification, not replacement: it gives a family a verified safety
backbone and an audit trail, but the model agent still owns the actual reasoning,
the domain policy choices, the tool implementations, and the final answer. A
scenario that needs domain logic still lives in its own workspace under
`workspaces/` and only promotes a primitive back here when it proves cross-scenario
value (see `docs/scenario-workspace-contract.md`).
