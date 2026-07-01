from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Iterable


# Structural health gate that this audit treats as the "verification suite".
# It is a bash script whose exit code (0 = green) is the real signal, not its
# mere presence on disk.
LAB_GATE_REL = "scripts/check-lab"
LAB_GATE_TIMEOUT_SECONDS = 300

# The lab gate shells out to `rg`. In some environments (see the Claude/Codex
# lane notes) `rg` is only a shell function or lives inside the Codex.app
# bundle, so a bare subprocess PATH cannot find it and the gate would fail for
# an environment reason rather than a real lab regression. These are the known
# fallback locations for a real `rg` binary.
_RG_FALLBACK_DIRS = (
    "/Applications/Codex.app/Contents/Resources",
    "/opt/homebrew/bin",
    "/usr/local/bin",
)

# A live model-backed proof artifact is only meaningful if it is recent and has
# real content, not just a matching filename.
MODEL_PROOF_MAX_AGE_DAYS = 21
MODEL_PROOF_MIN_LINES = 8
MODEL_PROOF_MARKERS = ("## Summary", "Verdict", "Evidence")


DIMENSION_ORDER = (
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
)

DIMENSION_LABELS = {
    "intake": "Task intake",
    "context": "Context discipline",
    "architecture": "Architecture readiness",
    "runtime": "Runtime execution",
    "delegation": "Delegation and parallelism",
    "tooling": "Tools and skills",
    "verification": "Verification gates",
    "observability": "Observability and dashboard",
    "safety": "Safety and secret boundary",
    "handoff": "Durable handoff",
    "performance": "Performance and latency",
    "model-proof": "Model-backed proof",
}

RISK_PRIORITY = {
    "safety": 0,
    "delegation": 1,
    "runtime": 2,
    "verification": 3,
    "model-proof": 4,
    "handoff": 5,
    "observability": 6,
    "performance": 7,
    "architecture": 8,
    "context": 9,
    "intake": 10,
    "tooling": 11,
}

STATUS_SCORE = {
    "pass": 1.0,
    "mixed": 0.5,
    "fail": 0.0,
    "missing": 0.0,
}


@dataclass(frozen=True)
class CapabilitySignal:
    dimension: str
    source: str
    status: str
    evidence: str

    def __post_init__(self) -> None:
        if self.status not in {"pass", "mixed", "fail"}:
            raise ValueError(f"unsupported signal status: {self.status}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "source": self.source,
            "status": self.status,
            "evidence": self.evidence,
        }


def evaluate_large_agent_readiness(signals: Iterable[CapabilitySignal]) -> dict[str, Any]:
    signal_list = list(signals)
    if not signal_list:
        raise ValueError("at least one capability signal is required")

    dimensions: dict[str, dict[str, Any]] = {}
    for dimension in DIMENSION_ORDER:
        matching = [signal for signal in signal_list if signal.dimension == dimension]
        if not matching:
            dimensions[dimension] = {
                "label": DIMENSION_LABELS[dimension],
                "status": "missing",
                "sources": [],
                "evidence": ["No signal collected for this dimension."],
            }
            continue

        status = _rollup_status(matching)
        dimensions[dimension] = {
            "label": DIMENSION_LABELS[dimension],
            "status": status,
            "sources": [signal.source for signal in matching],
            "evidence": [signal.evidence for signal in matching],
        }

    status_counts = {
        status: sum(1 for item in dimensions.values() if item["status"] == status)
        for status in ("pass", "mixed", "fail", "missing")
    }
    readiness_score = round(
        100
        * sum(STATUS_SCORE[item["status"]] for item in dimensions.values())
        / len(DIMENSION_ORDER)
    )

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "dimension_count": len(DIMENSION_ORDER),
            "signal_count": len(signal_list),
            "pass_count": status_counts["pass"],
            "mixed_count": status_counts["mixed"],
            "fail_count": status_counts["fail"],
            "missing_count": status_counts["missing"],
            "readiness_score": readiness_score,
            "status": _overall_status(readiness_score, status_counts),
            "independent_verdict": _independent_verdict(readiness_score, status_counts),
        },
        "dimensions": dimensions,
        "top_risks": _top_risks(dimensions),
        "external_reviewer_notes": _external_reviewer_notes(dimensions),
        "recommended_next_actions": _recommended_next_actions(dimensions),
    }


def render_large_agent_readiness_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Third-Party Large Agent Readiness Report",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Status: `{summary['status']}`",
        f"- Readiness score: `{summary['readiness_score']}`",
        f"- Dimensions: `{summary['dimension_count']}`",
        f"- Mixed dimensions: `{summary['mixed_count']}`",
        f"- Failed dimensions: `{summary['fail_count']}`",
        f"- Missing dimensions: `{summary['missing_count']}`",
        f"- Independent verdict: {summary['independent_verdict']}",
        "",
        "## Capability Matrix",
        "",
        "| Dimension | Status | Sources | Evidence |",
        "| --- | --- | --- | --- |",
    ]

    for dimension in DIMENSION_ORDER:
        item = report["dimensions"][dimension]
        sources = ", ".join(f"`{source}`" for source in item["sources"]) or "-"
        evidence = " ".join(item["evidence"])
        lines.append(f"| {item['label']} | `{item['status']}` | {sources} | {evidence} |")

    lines.extend(["", "## Top Risks", ""])
    if report["top_risks"]:
        for item in report["top_risks"]:
            lines.append(f"- `{item['dimension']}` from `{item['source']}`: {item['evidence']}")
    else:
        lines.append("- No top risks found by the collected signals.")

    lines.extend(["", "## External Reviewer Notes", ""])
    for note in report["external_reviewer_notes"]:
        lines.append(f"- {note}")

    lines.extend(["", "## Recommended Next Actions", ""])
    for action in report["recommended_next_actions"]:
        lines.append(f"- {action}")

    return "\n".join(lines) + "\n"


def collect_large_agent_readiness_signals(lab_root: str | Path) -> list[CapabilitySignal]:
    root = Path(lab_root).expanduser().resolve()
    signals = [
        _exists_signal(
            root,
            "intake",
            "docs/scenario-workspace-contract.md",
            "Scenario-neutral intake boundaries and workspace contract exist.",
        ),
        _contains_signal(
            root,
            "context",
            "AGENTS.md",
            "## Long-Horizon Work Contract",
            "Long-horizon operating context is explicit.",
        ),
        _exists_signal(
            root,
            "architecture",
            "docs/agent-lab-mission.md",
            "Mission, quality bar, and promotion rules are documented.",
        ),
        _exists_signal(
            root,
            "runtime",
            "scripts/start-api-relay",
            "API-relay OMX runtime entrypoint exists.",
        ),
        _delegation_signal(root),
        _skill_surface_signal(root),
        _verification_signal(root),
        _exists_signal(
            root,
            "observability",
            "scripts/lab-dashboard",
            "One-screen health dashboard exists.",
        ),
        _safety_signal(root),
        _exists_signal(
            root,
            "handoff",
            "registry/current-progress.md",
            "Durable progress registry exists.",
        ),
        _performance_signal(root),
        _model_proof_signal(root),
    ]
    return signals


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(args[0]).expanduser().resolve() if args else Path.cwd().resolve()
    output_root = root / "outputs" / "shared" / "large-agent-readiness-auditor"
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    report = evaluate_large_agent_readiness(collect_large_agent_readiness_signals(root))
    markdown = render_large_agent_readiness_markdown(report)
    json_text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"

    json_path = run_dir / "report.json"
    markdown_path = run_dir / "report.md"
    latest_json = output_root / "latest.json"
    latest_markdown = output_root / "latest.md"
    json_path.write_text(json_text, encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")
    latest_markdown.write_text(markdown, encoding="utf-8")

    print(f"json: {json_path.relative_to(root)}")
    print(f"markdown: {markdown_path.relative_to(root)}")
    print(f"latest_markdown: {latest_markdown.relative_to(root)}")
    print(f"readiness_score: {report['summary']['readiness_score']}")
    print(f"status: {report['summary']['status']}")
    return 0


def _rollup_status(signals: list[CapabilitySignal]) -> str:
    statuses = {signal.status for signal in signals}
    if "fail" in statuses:
        return "fail"
    if "mixed" in statuses:
        return "mixed"
    return "pass"


def _overall_status(readiness_score: int, counts: dict[str, int]) -> str:
    if counts["fail"] or counts["missing"]:
        return "needs_repair_before_large_agent_work"
    if readiness_score >= 90:
        return "ready_with_known_constraints"
    if readiness_score >= 75:
        return "usable_with_governance"
    return "not_ready"


def _independent_verdict(readiness_score: int, counts: dict[str, int]) -> str:
    if counts["fail"] or counts["missing"]:
        return "The lab should not be treated as ready for unsupervised large-agent development until failed or missing dimensions are repaired."
    if readiness_score >= 90 and counts["mixed"]:
        return "The lab can host large-agent development with explicit governance around the mixed dimensions."
    if readiness_score >= 90:
        return "The lab is ready for large-agent development under its documented safety boundaries."
    return "The lab is useful, but large-agent work needs additional supervision and narrower task slicing."


def _top_risks(dimensions: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    risks: list[dict[str, str]] = []
    for dimension, item in dimensions.items():
        if item["status"] == "pass":
            continue
        risks.append(
            {
                "dimension": dimension,
                "status": item["status"],
                "source": item["sources"][0] if item["sources"] else "not collected",
                "evidence": item["evidence"][0] if item["evidence"] else "No evidence recorded.",
            }
        )
    return sorted(
        risks,
        key=lambda item: (
            {"fail": 0, "missing": 1, "mixed": 2}.get(item["status"], 3),
            RISK_PRIORITY.get(item["dimension"], 99),
        ),
    )[:6]


def _external_reviewer_notes(dimensions: dict[str, dict[str, Any]]) -> list[str]:
    notes = [
        "This report judges retained artifacts and runnable checks, not claimed model-internal learning.",
        "A passing dashboard is treated as health evidence, not as proof that future large-agent work will succeed automatically.",
    ]
    if dimensions["delegation"]["status"] != "pass":
        notes.append("Delegation remains the largest scale risk until official team/tmux execution is freshly proven or deliberately bypassed.")
    if dimensions["performance"]["status"] != "pass":
        notes.append("Real model-backed proof is valuable, but slow model smoke tests should remain boundary checks instead of default edit-loop steps.")
    if dimensions["safety"]["status"] != "pass":
        notes.append("Safety failures outrank speed and ergonomics because this lab is intended for strict agent development.")
    return notes


def _recommended_next_actions(dimensions: dict[str, dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    if dimensions["delegation"]["status"] != "pass":
        actions.append("Keep direct `omx-api exec` as the proven worker path, and re-test official team mode only with a task that benefits from it.")
    if dimensions["performance"]["status"] != "pass":
        actions.append("Use `scripts/benchmark-ide-loop --skip-omx` for default health checks and reserve model smoke for boundary proof.")
    if dimensions["model-proof"]["status"] != "pass":
        actions.append("Create a short live model-backed review artifact after each promoted large-agent workflow change.")
    if dimensions["verification"]["status"] != "pass":
        actions.append("Repair the smallest failing gate before adding more orchestration surface.")
    if not actions:
        actions.append("Proceed with a real large-agent workspace pilot and re-run this audit after the first long-horizon handoff.")
    return actions


def _gate_environment(root: Path) -> dict[str, str]:
    """Return an environment for the lab gate with a real `rg` on PATH.

    The gate is a bash script that calls `rg`. When `rg` is only a shell
    function (Claude lane) or bundled inside Codex.app, a bare subprocess
    cannot find it and the gate fails for an environment reason. Prepend a
    directory that holds a real `rg` binary so the exit code reflects the lab,
    not the shell.
    """
    env = dict(os.environ)
    path = env.get("PATH", "")
    if shutil.which("rg", path=path):
        return env
    for candidate in _RG_FALLBACK_DIRS:
        if (Path(candidate) / "rg").exists():
            env["PATH"] = f"{candidate}{os.pathsep}{path}" if path else candidate
            return env
    return env


def _run_lab_gate(root: Path) -> tuple[str, str]:
    """Execute the lab health gate and return (status, evidence).

    status is 'pass' when the gate exits 0, 'fail' otherwise. This runs real
    verification instead of only checking that the gate file exists.
    """
    root = Path(root).expanduser().resolve()
    gate = root / LAB_GATE_REL
    if not gate.exists():
        return "fail", f"Missing verification gate: {LAB_GATE_REL}."
    if not os.access(gate, os.X_OK):
        return "fail", f"Verification gate is not executable: {LAB_GATE_REL}."
    env = _gate_environment(root)
    if not shutil.which("rg", path=env.get("PATH", "")):
        return (
            "mixed",
            f"`{LAB_GATE_REL}` exists and is executable, but no real `rg` binary "
            "was found to run it, so the suite could not be verified in this "
            "environment.",
        )
    try:
        completed = subprocess.run(
            ["bash", str(gate)],
            cwd=str(root),
            env=env,
            capture_output=True,
            text=True,
            timeout=LAB_GATE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return "fail", f"`{LAB_GATE_REL}` timed out after {LAB_GATE_TIMEOUT_SECONDS}s."
    except OSError as exc:
        return "fail", f"`{LAB_GATE_REL}` could not be executed: {exc}."
    if completed.returncode == 0:
        return "pass", f"`{LAB_GATE_REL}` ran green (exit 0); verification suite is passing."
    detail = (completed.stderr or completed.stdout or "").strip().splitlines()
    last = detail[-1] if detail else "no diagnostic output"
    return (
        "fail",
        f"`{LAB_GATE_REL}` exited {completed.returncode}; verification suite is red: {last}",
    )


def _verification_signal(root: Path, gate_runner: Callable[[Path], tuple[str, str]] | None = None) -> CapabilitySignal:
    runner = gate_runner or _run_lab_gate
    status, evidence = runner(root)
    return CapabilitySignal("verification", LAB_GATE_REL, status, evidence)


def _exists_signal(root: Path, dimension: str, rel_path: str, success: str) -> CapabilitySignal:
    path = root / rel_path
    return CapabilitySignal(
        dimension,
        rel_path,
        "pass" if path.exists() else "fail",
        success if path.exists() else f"Missing expected path: {rel_path}.",
    )


def _contains_signal(
    root: Path,
    dimension: str,
    rel_path: str,
    needle: str,
    success: str,
) -> CapabilitySignal:
    path = root / rel_path
    if not path.exists():
        return CapabilitySignal(dimension, rel_path, "fail", f"Missing expected path: {rel_path}.")
    text = path.read_text(encoding="utf-8", errors="replace")
    return CapabilitySignal(
        dimension,
        rel_path,
        "pass" if needle in text else "fail",
        success if needle in text else f"Expected marker not found in {rel_path}: {needle}.",
    )


def _delegation_signal(root: Path) -> CapabilitySignal:
    proof = root / "workspaces" / "20260629_210146-omx-team-tmux-proof" / "team-summary.md"
    agents_dir = root / ".codex" / "agents"
    if proof.exists():
        text = proof.read_text(encoding="utf-8", errors="replace").lower()
        if "failed" in text or "unproven" in text or "mixed" in text:
            return CapabilitySignal(
                "delegation",
                "workspaces/20260629_210146-omx-team-tmux-proof/team-summary.md",
                "mixed",
                "Official team mode remains mixed or unproven, while direct `omx-api exec` workers have proof artifacts.",
            )
    if agents_dir.exists():
        return CapabilitySignal(
            "delegation",
            ".codex/agents",
            "pass",
            "Custom agent registry exists for bounded delegation.",
        )
    return CapabilitySignal(
        "delegation",
        ".codex/agents",
        "fail",
        "No custom agent directory found for delegated large-agent work.",
    )


def _skill_surface_signal(root: Path) -> CapabilitySignal:
    skill_root = root / ".agents" / "skills"
    if not skill_root.exists():
        return CapabilitySignal("tooling", ".agents/skills", "fail", "Lab-local skill directory is missing.")
    count = sum(1 for _ in skill_root.glob("*/SKILL.md"))
    if count < 10:
        return CapabilitySignal("tooling", ".agents/skills", "mixed", f"Only {count} lab-local skills found.")
    return CapabilitySignal("tooling", ".agents/skills", "pass", f"{count} lab-local skills are available.")


def _safety_signal(root: Path) -> CapabilitySignal:
    check = root / "scripts" / "check-secrets"
    rules = root / "AGENTS.md"
    if not check.exists():
        return CapabilitySignal("safety", "scripts/check-secrets", "fail", "Secret scanning gate is missing.")
    if not rules.exists():
        return CapabilitySignal("safety", "AGENTS.md", "fail", "Local safety rules are missing.")
    text = rules.read_text(encoding="utf-8", errors="replace")
    marker = "Do not read, print, copy, rewrite, or migrate secrets"
    if marker not in text:
        return CapabilitySignal("safety", "AGENTS.md", "fail", "Secret boundary rule is missing from lab AGENTS.md.")
    return CapabilitySignal(
        "safety",
        "scripts/check-secrets",
        "pass",
        "Secret scan entrypoint and explicit secret boundary rule exist.",
    )


def _performance_signal(root: Path) -> CapabilitySignal:
    history_rel = "outputs/shared/benchmarks/ide-loop/history.md"
    history = root / history_rel
    if not history.exists():
        return CapabilitySignal(
            "performance",
            history_rel,
            "mixed",
            "No benchmark history found, so large-agent latency cannot be trended.",
        )
    seconds = _latest_model_seconds_from_history(history.read_text(encoding="utf-8", errors="replace"))
    if seconds is None:
        return CapabilitySignal(
            "performance",
            history_rel,
            "mixed",
            "Benchmark history exists, but the latest model smoke duration was not parsed.",
        )
    if seconds > 60:
        return CapabilitySignal(
            "performance",
            history_rel,
            "mixed",
            f"Latest OMX model smoke took {seconds:.3f}s; acceptable for boundary proof, too slow for the default edit loop.",
        )
    return CapabilitySignal(
        "performance",
        history_rel,
        "pass",
        f"Latest OMX model smoke took {seconds:.3f}s.",
    )


def _model_proof_signal(root: Path) -> CapabilitySignal:
    candidates = sorted(
        (root / "outputs" / "shared").glob("*/*live*model*.md"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        return CapabilitySignal(
            "model-proof",
            "outputs/shared",
            "mixed",
            "No live model-backed review artifact found.",
        )
    newest = candidates[0]
    rel = newest.relative_to(root).as_posix()
    try:
        text = newest.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return CapabilitySignal("model-proof", rel, "mixed", f"Model-proof artifact could not be read: {exc}.")

    line_count = len([line for line in text.splitlines() if line.strip()])
    present_markers = [marker for marker in MODEL_PROOF_MARKERS if marker in text]
    missing_markers = [marker for marker in MODEL_PROOF_MARKERS if marker not in text]
    age_days = (datetime.now(timezone.utc).timestamp() - newest.stat().st_mtime) / 86400

    if line_count < MODEL_PROOF_MIN_LINES or missing_markers:
        return CapabilitySignal(
            "model-proof",
            rel,
            "mixed",
            f"Model-proof artifact {rel} looks thin ({line_count} content lines, "
            f"present markers {present_markers or 'none'}, missing markers {missing_markers or 'none'}); "
            "it may be a placeholder rather than a real review.",
        )
    if age_days > MODEL_PROOF_MAX_AGE_DAYS:
        return CapabilitySignal(
            "model-proof",
            rel,
            "mixed",
            f"Newest model-proof artifact {rel} is {age_days:.0f} days old "
            f"(> {MODEL_PROOF_MAX_AGE_DAYS}); refresh a live review to keep proof current.",
        )
    return CapabilitySignal(
        "model-proof",
        rel,
        "pass",
        f"A recent live model-backed review artifact exists ({line_count} content lines, {age_days:.0f} days old).",
    )


def _latest_model_seconds_from_history(history_markdown: str) -> float | None:
    for line in reversed(history_markdown.splitlines()):
        if not line.startswith("| ") or line.startswith("| ---") or "Model" in line:
            continue
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        if len(cells) >= 8:
            model_cell = cells[7].removesuffix("s")
            if re.fullmatch(r"\d+(?:\.\d+)?", model_cell):
                return float(model_cell)
    return None


if __name__ == "__main__":
    raise SystemExit(main())
