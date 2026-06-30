from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


DIMENSION_ORDER = ("context", "runtime", "verification", "handoff", "safety")
DIMENSION_LABELS = {
    "context": "Context loading",
    "runtime": "Runtime ergonomics",
    "verification": "Verification loop",
    "handoff": "Durable handoff",
    "safety": "Safety boundary",
}


@dataclass(frozen=True)
class ComfortSignal:
    dimension: str
    source: str
    passed: bool
    evidence: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "source": self.source,
            "passed": self.passed,
            "evidence": self.evidence,
        }


def evaluate_development_experience(signals: Iterable[ComfortSignal]) -> dict[str, Any]:
    signal_list = list(signals)
    if not signal_list:
        raise ValueError("at least one comfort signal is required")

    dimensions: dict[str, dict[str, Any]] = {}
    for dimension in DIMENSION_ORDER:
        matching = [signal for signal in signal_list if signal.dimension == dimension]
        if not matching:
            dimensions[dimension] = {
                "label": DIMENSION_LABELS[dimension],
                "status": "missing",
                "passed": 0,
                "failed": 0,
                "sources": [],
                "friction": ["No signal collected for this dimension."],
            }
            continue

        passed = [signal for signal in matching if signal.passed]
        failed = [signal for signal in matching if not signal.passed]
        dimensions[dimension] = {
            "label": DIMENSION_LABELS[dimension],
            "status": _dimension_status(passed, failed),
            "passed": len(passed),
            "failed": len(failed),
            "sources": [signal.source for signal in matching],
            "friction": [signal.evidence for signal in failed],
        }

    failed_signals = [signal for signal in signal_list if not signal.passed]
    missing_count = sum(1 for dimension in dimensions.values() if dimension["status"] == "missing")
    total_penalty = len(failed_signals) + missing_count
    denominator = len(signal_list) + missing_count
    comfort_score = round(100 * max(0, denominator - total_penalty) / denominator)

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "signal_count": len(signal_list),
            "failing_count": len(failed_signals),
            "missing_dimension_count": missing_count,
            "comfort_score": comfort_score,
            "status": _overall_status(comfort_score, failed_signals, missing_count),
        },
        "dimensions": dimensions,
        "top_friction": _top_friction(failed_signals, dimensions),
        "recommended_next_actions": _recommended_next_actions(failed_signals, dimensions),
    }


def render_development_experience_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Development Experience Auditor Report",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Status: `{summary['status']}`",
        f"- Comfort score: `{summary['comfort_score']}`",
        f"- Signals: `{summary['signal_count']}`",
        f"- Failing signals: `{summary['failing_count']}`",
        f"- Missing dimensions: `{summary['missing_dimension_count']}`",
        "",
        "## Dimension Breakdown",
        "",
        "| Dimension | Status | Passed | Failed | Sources |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for dimension in DIMENSION_ORDER:
        item = report["dimensions"][dimension]
        sources = ", ".join(f"`{source}`" for source in item["sources"]) or "-"
        lines.append(
            f"| {item['label']} | `{item['status']}` | {item['passed']} | {item['failed']} | {sources} |"
        )

    lines.extend(["", "## Top Friction", ""])
    if report["top_friction"]:
        for item in report["top_friction"]:
            lines.append(f"- `{item['dimension']}` from `{item['source']}`: {item['evidence']}")
    else:
        lines.append("- No blocking friction found in collected signals.")

    lines.extend(["", "## Recommended Next Actions", ""])
    for action in report["recommended_next_actions"]:
        lines.append(f"- {action}")
    return "\n".join(lines) + "\n"


def collect_lab_comfort_signals(lab_root: str | Path) -> list[ComfortSignal]:
    root = Path(lab_root).expanduser().resolve()
    return [
        _exists_signal(root, "context", "AGENTS.md", "Project overlay rules are discoverable."),
        _exists_signal(root, "context", "README.md", "Human start commands and framework map are discoverable."),
        _contains_signal(
            root,
            "context",
            "registry/AGENT_REGISTRY.md",
            "development-experience-auditor",
            "The auditor is registered for agent routing.",
        ),
        _exists_signal(root, "runtime", "scripts/start-api-relay", "API-relay runtime entrypoint exists."),
        _exists_signal(root, "runtime", "scripts/benchmark-ide-loop", "IDE-loop benchmark entrypoint exists."),
        _benchmark_signal(root),
        _exists_signal(root, "verification", "scripts/check-lab", "Lab health gate exists."),
        _exists_signal(root, "verification", "scripts/waterflow-verify", "Waterflow validation runner exists."),
        _exists_signal(root, "handoff", "registry/current-progress.md", "Durable progress registry exists."),
        _exists_signal(root, "handoff", "registry/VALIDATION.md", "Durable validation registry exists."),
        _exists_signal(root, "safety", "scripts/check-secrets", "Secret scanning gate exists."),
        _contains_signal(
            root,
            "safety",
            "AGENTS.md",
            "Do not read, print, copy, rewrite, or migrate secrets",
            "Credential boundary is explicit in local rules.",
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(args[0]).expanduser().resolve() if args else Path.cwd().resolve()
    output_root = root / "outputs" / "shared" / "development-experience-auditor"
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    report = evaluate_development_experience(collect_lab_comfort_signals(root))
    markdown = render_development_experience_markdown(report)
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
    print(f"comfort_score: {report['summary']['comfort_score']}")
    print(f"status: {report['summary']['status']}")
    return 0


def _dimension_status(passed: list[ComfortSignal], failed: list[ComfortSignal]) -> str:
    if passed and not failed:
        return "comfortable"
    if passed and failed:
        return "mixed"
    return "blocked"


def _overall_status(
    comfort_score: int,
    failed_signals: list[ComfortSignal],
    missing_count: int,
) -> str:
    if comfort_score >= 90 and not failed_signals and missing_count == 0:
        return "comfortable"
    if comfort_score >= 70:
        return "usable_with_friction"
    return "blocked"


def _top_friction(
    failed_signals: list[ComfortSignal],
    dimensions: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    friction = [
        {
            "dimension": signal.dimension,
            "source": signal.source,
            "evidence": signal.evidence,
        }
        for signal in failed_signals
    ]
    for dimension, item in dimensions.items():
        if item["status"] == "missing":
            friction.append(
                {
                    "dimension": dimension,
                    "source": "not collected",
                    "evidence": "No signal collected for this dimension.",
                }
            )
    return sorted(friction, key=lambda item: DIMENSION_ORDER.index(item["dimension"]))[:5]


def _recommended_next_actions(
    failed_signals: list[ComfortSignal],
    dimensions: dict[str, dict[str, Any]],
) -> list[str]:
    actions: list[str] = []
    failed_dimensions = {signal.dimension for signal in failed_signals}
    missing_dimensions = {
        dimension
        for dimension, item in dimensions.items()
        if item["status"] == "missing"
    }

    if "context" in failed_dimensions or "context" in missing_dimensions:
        actions.append("Tighten the task brief and context map before dispatching implementation work.")
    if "runtime" in failed_dimensions or "runtime" in missing_dimensions:
        actions.append("Measure the slow runtime path and decide whether it belongs in the active edit loop or a boundary benchmark.")
    if "verification" in failed_dimensions or "verification" in missing_dimensions:
        actions.append("Add or narrow the smallest verification command that proves the changed behavior.")
    if "handoff" in failed_dimensions or "handoff" in missing_dimensions:
        actions.append("Write a durable progress or handoff artifact before switching lanes or agents.")
    if "safety" in failed_dimensions or "safety" in missing_dimensions:
        actions.append("Run the secret and sandbox gates before promoting the workflow.")
    if not actions:
        actions.append("Keep using the current lab loop; re-run this audit after the next medium or large agent build.")
    return actions


def _exists_signal(root: Path, dimension: str, rel_path: str, success: str) -> ComfortSignal:
    path = root / rel_path
    return ComfortSignal(
        dimension,
        rel_path,
        path.exists(),
        success if path.exists() else f"Missing expected path: {rel_path}.",
    )


def _contains_signal(
    root: Path,
    dimension: str,
    rel_path: str,
    needle: str,
    success: str,
) -> ComfortSignal:
    path = root / rel_path
    if not path.exists():
        return ComfortSignal(dimension, rel_path, False, f"Missing expected path: {rel_path}.")
    text = path.read_text(encoding="utf-8", errors="replace")
    return ComfortSignal(
        dimension,
        rel_path,
        needle in text,
        success if needle in text else f"Expected marker not found in {rel_path}: {needle}.",
    )


def _benchmark_signal(root: Path) -> ComfortSignal:
    history = root / "outputs" / "shared" / "benchmarks" / "ide-loop" / "history.md"
    if not history.exists():
        return ComfortSignal(
            "runtime",
            "outputs/shared/benchmarks/ide-loop/history.md",
            False,
            "No benchmark history found, so runtime comfort cannot be trended.",
        )
    text = history.read_text(encoding="utf-8", errors="replace")
    omx_seconds = latest_model_seconds_from_history(text)
    if omx_seconds is None:
        return ComfortSignal(
            "runtime",
            "outputs/shared/benchmarks/ide-loop/history.md",
            True,
            "Benchmark history exists, but OMX smoke duration was not parsed.",
        )
    if omx_seconds > 60:
        return ComfortSignal(
            "runtime",
            "outputs/shared/benchmarks/ide-loop/history.md",
            False,
            f"Latest OMX model smoke took {omx_seconds:.3f}s; keep it as a boundary check, not the default edit loop.",
        )
    return ComfortSignal(
        "runtime",
        "outputs/shared/benchmarks/ide-loop/history.md",
        True,
        f"Latest OMX model smoke took {omx_seconds:.3f}s.",
    )


def latest_model_seconds_from_history(history_markdown: str) -> float | None:
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
