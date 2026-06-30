"""Neutrality proof: two unrelated agent domains, one kernel.

This is the evidence that the kernel is genuinely scenario-neutral and not a
support-scenario engine in disguise. The two chains are built inline (no
resident demo package) so the lab keeps only the kernel, not example products.
If the kernel were domain-bound, these two chains could not both be expressed.
"""

import unittest

from lab_agents.agent_kernel import ContextItem, DecisionEngine, Principal, Tool, Turn, policies


def _infra_ops_engine() -> DecisionEngine:
    """Infra-ops agent: secrets refusal, destructive-op + cross-team escalation,
    replica-scale limit, permissioned metrics lookup, runbook grounding."""
    chain = [
        policies.sensitive_data_request(terms=("vault token", "private key")),
        policies.forbidden_action(terms=("delete the cluster", "wipe the volume")),
        policies.foreign_subject_reference(
            pattern=r"\bsvc-[a-z0-9-]+\b", audit_event="ownership_boundary"
        ),
        policies.value_threshold(
            trigger_keyword="scale", threshold=50,
            strip_patterns=(r"\bsvc-[a-z0-9-]+\b",), audit_event="scale_limit_exceeded",
        ),
        policies.permissioned_tool_call(
            intent_keywords=("metrics",), require_any_keyword=("check", "get"),
            tool_name="read_metrics", risk="medium",
            arg_builder=lambda t: {"namespace": t.principal.scope_id},
            granted_reply="read-only metrics",
        ),
        policies.grounded_answer(keyword="runbook"),
    ]
    return DecisionEngine(chain, policies.insufficient_evidence_fallback(), name="infra-ops")


def _research_engine() -> DecisionEngine:
    """Research agent: credential refusal, cross-project boundary, permissioned
    corpus search, source grounding, no-source refusal. Deliberately omits
    value_threshold and forbidden_action -> the chain is a free composition."""
    chain = [
        policies.sensitive_data_request(terms=("api key", "s3 credentials")),
        policies.foreign_subject_reference(
            pattern=r"\bproj-[a-z0-9-]+\b", audit_event="project_boundary"
        ),
        policies.permissioned_tool_call(
            intent_keywords=("search",), require_any_keyword=("find", "search"),
            tool_name="search_corpus", risk="low",
            arg_builder=lambda t: {"project": t.principal.scope_id},
            granted_reply="cited corpus search",
        ),
        policies.grounded_answer(keyword="summary"),
    ]
    return DecisionEngine(chain, policies.insufficient_evidence_fallback(), name="research")


class InfraOpsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = _infra_ops_engine()
        self.oncall = Principal("svc-payments", "ns-payments", authenticated=True, roles=("oncall",))

    def test_destructive_action_escalates(self) -> None:
        d = self.engine.decide(Turn("delete the cluster to fix it", self.oncall))
        self.assertTrue(d.escalate)
        self.assertIn("irreversible_action", d.audit_events)

    def test_cross_team_service_escalates(self) -> None:
        d = self.engine.decide(Turn("restart svc-billing now", self.oncall))
        self.assertIn("ownership_boundary", d.audit_events)

    def test_scale_above_limit_escalates(self) -> None:
        d = self.engine.decide(Turn("scale to 200 replicas", self.oncall))
        self.assertIn("scale_limit_exceeded", d.audit_events)

    def test_metrics_tool_planned_for_oncall(self) -> None:
        tool = Tool("read_metrics", required_role="oncall", allowed_risks=("medium",))
        d = self.engine.decide(Turn("check metrics for svc-payments", self.oncall, tools=(tool,)))
        self.assertEqual(d.tool_call.name, "read_metrics")
        self.assertEqual(d.tool_call.arguments["namespace"], "ns-payments")

    def test_runbook_answer_from_trusted_doc(self) -> None:
        doc = ContextItem("rb-1", "ns-payments", "Runbook", "Restart the pod.", trusted=True)
        d = self.engine.decide(Turn("what does the runbook say", self.oncall, context=(doc,)))
        self.assertEqual(d.evidence_refs, ("rb-1",))


class ResearchTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = _research_engine()
        self.member = Principal("proj-alpha", "proj-alpha", authenticated=True, roles=("member",))

    def test_cross_project_escalates(self) -> None:
        d = self.engine.decide(Turn("summarize notes from proj-beta", self.member))
        self.assertIn("project_boundary", d.audit_events)

    def test_search_tool_planned(self) -> None:
        tool = Tool("search_corpus", required_role="member", allowed_risks=("low",))
        d = self.engine.decide(Turn("search for transformer papers", self.member, tools=(tool,)))
        self.assertEqual(d.tool_call.arguments["project"], "proj-alpha")

    def test_no_source_refuses(self) -> None:
        d = self.engine.decide(Turn("tell me anything", self.member))
        self.assertTrue(d.escalate)
        self.assertIn("insufficient_evidence", d.audit_events)


class NeutralityTest(unittest.TestCase):
    def test_chains_share_backbone_but_differ(self) -> None:
        infra, research = _infra_ops_engine(), _research_engine()
        self.assertIn("value_threshold", infra.policy_names)
        self.assertIn("forbidden_action", infra.policy_names)
        self.assertNotIn("value_threshold", research.policy_names)
        self.assertNotIn("forbidden_action", research.policy_names)
        for shared in ("sensitive_data_request", "permissioned_tool_call", "grounded_answer"):
            self.assertIn(shared, infra.policy_names)
            self.assertIn(shared, research.policy_names)


if __name__ == "__main__":
    unittest.main()
