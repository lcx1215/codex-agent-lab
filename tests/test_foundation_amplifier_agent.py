import tomllib
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
AGENT_PATH = LAB_ROOT / ".codex" / "agents" / "foundation-amplifier.toml"


class FoundationAmplifierAgentTests(unittest.TestCase):
    def test_foundation_amplifier_agent_contract_is_registered(self):
        self.assertTrue(AGENT_PATH.exists(), "foundation-amplifier agent file is missing")

        agent = tomllib.loads(AGENT_PATH.read_text(encoding="utf-8"))
        instructions = agent["developer_instructions"]

        self.assertEqual(agent["name"], "foundation-amplifier")
        self.assertIn("Task Intake", instructions)
        self.assertIn("Capability Routing", instructions)
        self.assertIn("Amplification Plan", instructions)
        self.assertIn("Verification Backtest", instructions)
        self.assertIn("Non-Replacement Rule", instructions)
        self.assertIn("Do not read, print, copy, or migrate secrets", instructions)

        for path in (
            LAB_ROOT / "AGENTS.md",
            LAB_ROOT / "README.md",
            LAB_ROOT / "registry" / "AGENT_REGISTRY.md",
        ):
            self.assertIn("foundation-amplifier", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
