import tomllib
import unittest
from datetime import datetime, timezone
from pathlib import Path

from lab_agents.large_agent_readiness import (
    CapabilitySignal,
    collect_large_agent_readiness_signals,
    evaluate_large_agent_readiness,
    render_large_agent_readiness_markdown,
    _model_proof_signal,
    _run_lab_gate,
    _verification_signal,
)


LAB_ROOT = Path(__file__).resolve().parents[1]
AGENT_PATH = LAB_ROOT / ".codex" / "agents" / "third-party-large-agent-auditor.toml"
DOC_PATH = LAB_ROOT / "docs" / "third-party-large-agent-auditor.md"


class LargeAgentReadinessAuditorTests(unittest.TestCase):
    def test_agent_contract_is_registered_as_third_party_auditor(self):
        self.assertTrue(AGENT_PATH.exists(), "third-party-large-agent-auditor agent file is missing")
        self.assertTrue(DOC_PATH.exists(), "third-party auditor docs are missing")

        agent = tomllib.loads(AGENT_PATH.read_text(encoding="utf-8"))
        instructions = agent["developer_instructions"]

        self.assertEqual(agent["name"], "third-party-large-agent-auditor")
        self.assertEqual(agent["model"], "gpt-5.5")
        self.assertIn("Third-Party Posture", instructions)
        self.assertIn("Large-Agent Capability Dimensions", instructions)
        self.assertIn("Failure Bias", instructions)
        self.assertIn("Do not read, print, copy, or migrate secrets", instructions)

        for path in (
            LAB_ROOT / "AGENTS.md",
            LAB_ROOT / "README.md",
            LAB_ROOT / "registry" / "AGENT_REGISTRY.md",
        ):
            self.assertIn("third-party-large-agent-auditor", path.read_text(encoding="utf-8"))

    def test_evaluation_scores_large_agent_lifecycle_and_flags_mixed_dimensions(self):
        signals = [
            CapabilitySignal("intake", "docs/scenario-workspace-contract.md", "pass", "Scenario boundaries exist."),
            CapabilitySignal("context", "AGENTS.md", "pass", "Rules are discoverable."),
            CapabilitySignal("architecture", "docs/agent-lab-mission.md", "pass", "Mission and quality bar exist."),
            CapabilitySignal("runtime", "scripts/start-api-relay", "pass", "Runtime entrypoint exists."),
            CapabilitySignal("delegation", ".codex/agents", "mixed", "Official team mode remains unproven."),
            CapabilitySignal("tooling", ".agents/skills", "pass", "Skill surface exists."),
            CapabilitySignal("verification", "scripts/check-lab", "pass", "Health gate exists."),
            CapabilitySignal("observability", "scripts/lab-dashboard", "pass", "Dashboard exists."),
            CapabilitySignal("safety", "scripts/check-secrets", "pass", "Secret gate exists."),
            CapabilitySignal("handoff", "registry/current-progress.md", "pass", "Progress is durable."),
            CapabilitySignal("performance", "outputs/shared/benchmarks/ide-loop/history.md", "mixed", "Model smoke is slow."),
            CapabilitySignal("model-proof", "outputs/shared/development-experience-auditor/live-model-review.md", "pass", "Live proof exists."),
        ]

        report = evaluate_large_agent_readiness(signals)

        self.assertEqual(report["summary"]["dimension_count"], 12)
        self.assertEqual(report["summary"]["mixed_count"], 2)
        self.assertGreaterEqual(report["summary"]["readiness_score"], 80)
        self.assertEqual(report["dimensions"]["delegation"]["status"], "mixed")
        self.assertEqual(report["top_risks"][0]["dimension"], "delegation")
        self.assertIn("Official team mode", report["top_risks"][0]["evidence"])

    def test_markdown_report_looks_like_independent_external_assessment(self):
        report = evaluate_large_agent_readiness(
            [
                CapabilitySignal("intake", "brief.md", "pass", "Brief exists."),
                CapabilitySignal("safety", "scripts/check-secrets", "fail", "Secret gate missing."),
            ]
        )

        markdown = render_large_agent_readiness_markdown(report)

        self.assertIn("# Third-Party Large Agent Readiness Report", markdown)
        self.assertIn("Independent verdict", markdown)
        self.assertIn("## Capability Matrix", markdown)
        self.assertIn("## Top Risks", markdown)
        self.assertIn("Secret gate missing.", markdown)
        self.assertIn("## External Reviewer Notes", markdown)

    def test_collects_real_lab_large_agent_signals_without_secret_paths(self):
        signals = collect_large_agent_readiness_signals(LAB_ROOT)

        dimensions = {signal.dimension for signal in signals}
        sources = "\n".join(signal.source for signal in signals)

        self.assertTrue(
            {
                "intake",
                "context",
                "architecture",
                "runtime",
                "delegation",
                "tooling",
                "verification",
                "observability",
                "safety",
                "handoff",
                "performance",
                "model-proof",
            }.issubset(dimensions)
        )
        self.assertIn("docs/scenario-workspace-contract.md", sources)
        self.assertIn("scripts/lab-dashboard", sources)
        self.assertNotIn("auth.json", sources)
        self.assertNotIn("config.toml", sources)

    def test_verification_fails_when_the_suite_is_red(self):
        # A red gate (non-zero exit) must NOT score as ready just because the
        # gate file exists on disk.
        signal = _verification_signal(
            LAB_ROOT,
            gate_runner=lambda root: ("fail", "scripts/check-lab exited 1; verification suite is red: boom"),
        )
        self.assertEqual(signal.dimension, "verification")
        self.assertEqual(signal.status, "fail")
        self.assertIn("red", signal.evidence)

    def test_verification_passes_only_when_the_suite_is_green(self):
        signal = _verification_signal(
            LAB_ROOT,
            gate_runner=lambda root: ("pass", "scripts/check-lab ran green (exit 0)"),
        )
        self.assertEqual(signal.status, "pass")
        self.assertIn("green", signal.evidence)

    def test_verification_missing_gate_fails(self):
        # Point at a directory with no gate; the real runner must fail closed.
        status, evidence = _run_lab_gate(LAB_ROOT / "docs")
        self.assertEqual(status, "fail")
        self.assertIn("check-lab", evidence)

    def test_model_proof_flags_thin_or_stale_artifacts(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proof_dir = root / "outputs" / "shared" / "foo"
            proof_dir.mkdir(parents=True)

            # Thin placeholder: matching name but no real content/markers.
            thin = proof_dir / "live-model-review.md"
            thin.write_text("# live model\n\ntouch\n", encoding="utf-8")
            self.assertEqual(_model_proof_signal(root).status, "mixed")

            # Substantial and recent artifact passes.
            body = "\n".join(
                ["# Live Model Review", "", "## Summary", "Verdict: usable.", "", "## Evidence Read"]
                + [f"- point {i}" for i in range(6)]
            )
            thin.write_text(body, encoding="utf-8")
            self.assertEqual(_model_proof_signal(root).status, "pass")

    def test_model_proof_requires_all_markers(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proof_dir = root / "outputs" / "shared" / "foo"
            proof_dir.mkdir(parents=True)
            proof = proof_dir / "live-model-review.md"
            body = "\n".join(
                ["# Live Model Review", "", "## Summary", "Only one marker is not enough."]
                + [f"- point {i}" for i in range(8)]
            )
            proof.write_text(body, encoding="utf-8")

            signal = _model_proof_signal(root)
            self.assertEqual(signal.status, "mixed")
            self.assertIn("missing markers", signal.evidence)


if __name__ == "__main__":
    unittest.main()
