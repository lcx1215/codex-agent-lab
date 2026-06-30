"""Tests for the agent code quality auditor (scripts/audit-agent-code).

These lock the auditor's two non-negotiable behaviors:
- it FAILS on the fail-open auth / empty-secret anti-pattern family;
- it does NOT false-positive on clean code.

The auditor is a script, not a module, so we load it by path.
"""

import sys
import tempfile
import types
import unittest
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = LAB_ROOT / "scripts" / "audit-agent-code"

# The auditor is an extension-less script; exec its source into a module namespace.
# Register in sys.modules first so @dataclass can resolve cls.__module__.
aac = types.ModuleType("audit_agent_code")
aac.__file__ = str(SCRIPT)
sys.modules["audit_agent_code"] = aac
exec(compile(SCRIPT.read_text(encoding="utf-8"), str(SCRIPT), "exec"), aac.__dict__)


def _pkg(files: dict[str, str]) -> Path:
    tmp = Path(tempfile.mkdtemp())
    for rel, content in files.items():
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return tmp


class AuditorTest(unittest.TestCase):
    def test_flags_fail_open_auth(self):
        pkg = _pkg({"src/security/sig.mjs": (
            "export function verify({ secret }) {\n"
            "  if (!secret) return { ok: true, reason: 'no_secret' };\n"
            "  return { ok: false };\n"
            "}\n"
        )})
        report = aac.audit(pkg)
        codes = {f["code"] for f in report["findings"]}
        self.assertIn("FAIL_OPEN_AUTH", codes)
        self.assertEqual(report["status"], "fail")

    def test_flags_empty_secret_call(self):
        pkg = _pkg({"src/server.mjs": (
            "import { verify } from './security/sig.mjs';\n"
            "const r = verify({ rawBody: b, headers: h, secret: '' });\n"
        )})
        report = aac.audit(pkg)
        codes = {f["code"] for f in report["findings"]}
        self.assertIn("EMPTY_SECRET", codes)
        self.assertEqual(report["status"], "fail")

    def test_clean_code_passes(self):
        pkg = _pkg({
            "src/util.mjs": "export const add = (a, b) => a + b;\n",
            "test/util.test.mjs": "import { add } from '../src/util.mjs';\n",
        })
        report = aac.audit(pkg)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["counts"]["fail"], 0)

    def test_missing_tests_warns(self):
        pkg = _pkg({"src/only.mjs": "export const x = 1;\n"})
        report = aac.audit(pkg)
        codes = {f["code"] for f in report["findings"]}
        self.assertIn("NO_TESTS", codes)

    def test_exit_semantics_fail_only_on_fail(self):
        # warn-only package -> status warn, but a clean one -> pass
        warn_pkg = _pkg({"src/a.mjs": "for await (const chunk of req) { body += chunk; }\n"})
        self.assertEqual(aac.audit(warn_pkg)["status"], "warn")


if __name__ == "__main__":
    unittest.main()
