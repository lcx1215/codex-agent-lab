import tomllib
import unittest
from pathlib import Path

from lab_agents.development_experience import (
    ComfortSignal,
    collect_lab_comfort_signals,
    evaluate_development_experience,
    render_development_experience_markdown,
    latest_model_seconds_from_history,
)


LAB_ROOT = Path(__file__).resolve().parents[1]
AGENT_PATH = LAB_ROOT / ".codex" / "agents" / "development-experience-auditor.toml"
DOC_PATH = LAB_ROOT / "docs" / "development-experience-auditor-agent.md"


class DevelopmentExperienceAuditorTests(unittest.TestCase):
    def test_agent_contract_is_registered_and_safety_bounded(self):
        self.assertTrue(AGENT_PATH.exists(), "development-experience-auditor agent file is missing")
        self.assertTrue(DOC_PATH.exists(), "development-experience-auditor docs are missing")

        agent = tomllib.loads(AGENT_PATH.read_text(encoding="utf-8"))
        instructions = agent["developer_instructions"]

        self.assertEqual(agent["name"], "development-experience-auditor")
        self.assertEqual(agent["model"], "gpt-5.5")
        self.assertIn("Comfort Dimensions", instructions)
        self.assertIn("Evidence Sources", instructions)
        self.assertIn("Friction Report", instructions)
        self.assertIn("Do not read, print, copy, or migrate secrets", instructions)

        for path in (
            LAB_ROOT / "AGENTS.md",
            LAB_ROOT / "README.md",
            LAB_ROOT / "registry" / "AGENT_REGISTRY.md",
        ):
            self.assertIn("development-experience-auditor", path.read_text(encoding="utf-8"))

    def test_evaluation_scores_comfort_and_prioritizes_blockers(self):
        signals = [
            ComfortSignal("context", "AGENTS.md", True, "Rules are discoverable."),
            ComfortSignal("runtime", "scripts/benchmark-ide-loop", True, "Model smoke exists."),
            ComfortSignal("runtime", "outputs/shared/benchmarks/ide-loop/run.md", False, "Model smoke too slow."),
            ComfortSignal("verification", "scripts/check-lab", True, "Health gate exists."),
            ComfortSignal("handoff", "registry/current-progress.md", True, "Progress is durable."),
            ComfortSignal("safety", "scripts/check-secrets", True, "Secret gate exists."),
        ]

        report = evaluate_development_experience(signals)

        self.assertEqual(report["summary"]["signal_count"], 6)
        self.assertEqual(report["summary"]["failing_count"], 1)
        self.assertGreaterEqual(report["summary"]["comfort_score"], 80)
        self.assertEqual(report["dimensions"]["runtime"]["status"], "mixed")
        self.assertEqual(report["top_friction"][0]["dimension"], "runtime")
        self.assertIn("Model smoke too slow", report["top_friction"][0]["evidence"])

    def test_markdown_report_is_restartable_and_actionable(self):
        report = evaluate_development_experience(
            [
                ComfortSignal("context", "AGENTS.md", True, "Rules are discoverable."),
                ComfortSignal("runtime", "scripts/start-api-relay", True, "Runtime entrypoint exists."),
                ComfortSignal("verification", "scripts/check-lab", False, "Health gate is slow."),
            ]
        )

        markdown = render_development_experience_markdown(report)

        self.assertIn("# Development Experience Auditor Report", markdown)
        self.assertIn("Comfort score", markdown)
        self.assertIn("## Dimension Breakdown", markdown)
        self.assertIn("## Top Friction", markdown)
        self.assertIn("Health gate is slow.", markdown)
        self.assertIn("## Recommended Next Actions", markdown)

    def test_collects_real_lab_signals_without_reading_secret_paths(self):
        signals = collect_lab_comfort_signals(LAB_ROOT)

        dimensions = {signal.dimension for signal in signals}
        sources = "\n".join(signal.source for signal in signals)

        self.assertTrue({"context", "runtime", "verification", "handoff", "safety"}.issubset(dimensions))
        self.assertIn("AGENTS.md", sources)
        self.assertIn("scripts/benchmark-ide-loop", sources)
        self.assertIn("scripts/check-secrets", sources)
        self.assertNotIn("auth.json", sources)
        self.assertNotIn("config.toml", sources)

    def test_parses_latest_model_seconds_from_benchmark_history(self):
        history = """# IDE Benchmark History

| Run | Status | OMX | Total | Local | Gates | Waterflow | Model | Curve |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 20260630T035103Z | pass | yes | 103.590s | 0.356s | 9.969s | 8.306s | 84.959s | `##################` |
"""

        self.assertEqual(latest_model_seconds_from_history(history), 84.959)


if __name__ == "__main__":
    unittest.main()
