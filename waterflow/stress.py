from __future__ import annotations

import argparse
import json
import re
import stat
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .auditor import (
    build_fix_briefs,
    build_markdown_report,
    build_validation_results_markdown,
    run_validation_plan,
    scan_lab,
)


EXPECTED_PROBLEM_CODES = {
    "AGENT_MISSING_FIELD",
    "AGENT_TOML_INVALID",
    "CROSS_PROJECT_REFERENCE",
    "DUPLICATE_AGENT_NAME",
    "DUPLICATE_SKILL_NAME",
    "EMPTY_REGISTRY_FILE",
    "MISSING_CORE_PATH",
    "PROGRESS_WITHOUT_VALIDATION",
    "SCRIPT_NOT_EXECUTABLE",
    "SCRIPT_WITHOUT_VALIDATION_REFERENCE",
    "SKILL_MISSING_ENTRYPOINT",
    "SKILL_MISSING_FIELD",
}
NEEDLE_PROBLEM_CODES = {
    "EMPTY_REGISTRY_FILE",
    "SCRIPT_NOT_EXECUTABLE",
    "SCRIPT_WITHOUT_VALIDATION_REFERENCE",
    "SKILL_MISSING_FIELD",
}

HARNESS_PHILOSOPHY = {
    "purpose": "Turn Waterflow confidence into falsifiable evidence by injecting known defects, clean scale, and expected command failures.",
    "pass_definition": "A stress pass means expected defects were detected, clean scale produced no unexpected findings, and expected validation failures/timeouts were recorded.",
    "non_goal": "A stress pass is not a claim that the real lab, a product, or a live agent workflow has no defects.",
    "isolation": "Generated fixtures stay under outputs/shared/waterflow/stress so negative evidence cannot contaminate the real lab graph.",
}


def run_stress_suite(
    output_root: str | Path,
    scale_paths: int = 1000,
    validation_timeout_seconds: int = 1,
) -> dict[str, Any]:
    output_root = Path(output_root).expanduser().resolve()
    run_id = datetime.now(timezone.utc).strftime("stress-%Y%m%dT%H%M%SZ")
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    problem_root = run_dir / "problem-lab"
    scale_root = run_dir / "scale-lab"
    needle_root = run_dir / "needle-lab"
    create_problem_lab(problem_root)
    create_scale_lab(scale_root, scale_paths=scale_paths)
    create_needle_lab(needle_root, scale_paths=scale_paths)

    problem_report = scan_lab(problem_root)
    scale_scan_started = datetime.now(timezone.utc)
    scale_report = scan_lab(scale_root)
    scale_scan_finished = datetime.now(timezone.utc)
    needle_report = scan_lab(needle_root)
    validation_results = run_validation_plan(
        _validation_stress_plan(run_dir),
        root=run_dir,
        timeout_seconds=validation_timeout_seconds,
        max_output_chars=4000,
    )

    problem_codes = sorted({finding["code"] for finding in problem_report["findings"]})
    implemented_codes = sorted(implemented_finding_codes())
    missing_problem_codes = sorted(EXPECTED_PROBLEM_CODES - set(problem_codes))
    uncovered_implemented_codes = sorted(set(implemented_codes) - set(problem_codes))
    expected_without_implementation = sorted(EXPECTED_PROBLEM_CODES - set(implemented_codes))
    unexpected_scale_findings = scale_report["summary"]["finding_count"]
    needle_codes = sorted({finding["code"] for finding in needle_report["findings"]})
    missing_needle_codes = sorted(NEEDLE_PROBLEM_CODES - set(needle_codes))
    validation_summary = validation_results["summary"]
    validation_expected = (
        validation_summary["check_count"] == 3
        and validation_summary["passed_count"] == 1
        and validation_summary["failed_count"] == 2
        and validation_summary["timed_out_count"] == 1
        and validation_summary["max_exit_code"] == 124
    )
    scale_expected = (
        scale_report["summary"]["node_count"] >= scale_paths
        and unexpected_scale_findings == 0
    )
    criteria = [
        _criterion(
            "expected_problem_codes_detected",
            not missing_problem_codes,
            "Problem fixture must detect every expected defect family.",
            missing_problem_codes,
        ),
        _criterion(
            "implemented_detector_codes_covered",
            not uncovered_implemented_codes and not expected_without_implementation,
            "Every implemented detector code must have a matching injected problem, and every expected injected problem must map to a detector.",
            uncovered_implemented_codes + expected_without_implementation,
        ),
        _criterion(
            "clean_scale_stays_clean",
            scale_expected,
            "Scale fixture must reach the requested node count without unexpected findings.",
            [] if scale_expected else [f"nodes={scale_report['summary']['node_count']}", f"findings={unexpected_scale_findings}"],
        ),
        _criterion(
            "needle_defects_found_in_large_graph",
            needle_report["summary"]["node_count"] >= scale_paths and not missing_needle_codes,
            "Needle fixture must find small injected defects inside a large otherwise-clean graph.",
            missing_needle_codes
            if missing_needle_codes
            else [f"nodes={needle_report['summary']['node_count']}", f"findings={needle_report['summary']['finding_count']}"],
        ),
        _criterion(
            "validation_failures_are_recorded",
            validation_expected,
            "Validation stress must record one pass, one failing command, and one timeout.",
            [] if validation_expected else [json.dumps(validation_summary, sort_keys=True)],
        ),
        _criterion(
            "fixtures_are_generated_evidence",
            problem_root.is_relative_to(run_dir)
            and scale_root.is_relative_to(run_dir)
            and needle_root.is_relative_to(run_dir),
            "Problem, scale, and needle fixtures must stay inside the generated stress run directory.",
            []
            if problem_root.is_relative_to(run_dir)
            and scale_root.is_relative_to(run_dir)
            and needle_root.is_relative_to(run_dir)
            else [str(problem_root), str(scale_root), str(needle_root)],
        ),
    ]
    status = "pass" if all(item["passed"] for item in criteria) else "fail"

    results = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "harness_philosophy": HARNESS_PHILOSOPHY,
        "harness_criteria": criteria,
        "detector_coverage": {
            "implemented_codes": implemented_codes,
            "expected_problem_codes": sorted(EXPECTED_PROBLEM_CODES),
            "detected_problem_codes": problem_codes,
            "uncovered_implemented_codes": uncovered_implemented_codes,
            "expected_without_implementation": expected_without_implementation,
        },
        "run_dir": str(run_dir),
        "problem_lab": {
            "root": str(problem_root),
            "finding_count": problem_report["summary"]["finding_count"],
            "detected_codes": problem_codes,
            "detected_code_counts": dict(Counter(finding["code"] for finding in problem_report["findings"])),
            "missing_expected_codes": missing_problem_codes,
        },
        "scale_lab": {
            "root": str(scale_root),
            "requested_scale_paths": scale_paths,
            "node_count": scale_report["summary"]["node_count"],
            "edge_count": scale_report["summary"]["edge_count"],
            "finding_count": unexpected_scale_findings,
            "scan_started_at": scale_scan_started.isoformat(),
            "scan_finished_at": scale_scan_finished.isoformat(),
        },
        "needle_lab": {
            "root": str(needle_root),
            "requested_scale_paths": scale_paths,
            "node_count": needle_report["summary"]["node_count"],
            "edge_count": needle_report["summary"]["edge_count"],
            "finding_count": needle_report["summary"]["finding_count"],
            "detected_codes": needle_codes,
            "missing_expected_codes": missing_needle_codes,
        },
        "validation_runner": validation_summary,
        "artifacts": {},
    }

    artifacts = _write_stress_artifacts(run_dir, results, problem_report, scale_report, validation_results)
    results["artifacts"] = artifacts
    (run_dir / "waterflow-stress-results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (run_dir / "waterflow-stress-results.md").write_text(
        build_stress_markdown(results),
        encoding="utf-8",
    )
    return results


def implemented_finding_codes(source_path: str | Path | None = None) -> set[str]:
    source = Path(source_path) if source_path else Path(__file__).with_name("auditor.py")
    text = source.read_text(encoding="utf-8")
    return set(re.findall(r'_finding\(\s*["\']P[0-3]["\']\s*,\s*["\']([A-Z0-9_]+)["\']', text, re.S))


def create_problem_lab(root: str | Path) -> Path:
    root = Path(root)
    _make_common_dirs(root)
    (root / "AGENTS.md").write_text(
        "# Rules\n"
        "This generated fixture intentionally contains a cross-project reference "
        "to /Users/liuchengxu/Desktop/lcx-s-openclaw for detector testing only.\n",
        encoding="utf-8",
    )
    (root / "registry" / "VALIDATION.md").write_text("# Validation\n", encoding="utf-8")
    (root / "registry" / "EMPTY.md").write_text("", encoding="utf-8")
    (root / "registry" / "current-progress.md").write_text(
        "# Progress\nCompleted all work.\n",
        encoding="utf-8",
    )
    (root / "docs" / "design.md").write_text("# Design\n", encoding="utf-8")
    (root / "waterflow" / "auditor.py").write_text("def placeholder():\n    return True\n", encoding="utf-8")
    (root / "tests" / "test_placeholder.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")

    (root / ".codex" / "agents" / "invalid-agent.toml").write_text(
        'name = "invalid-agent"\n'
        "developer_instructions = [\n",
        encoding="utf-8",
    )
    (root / ".codex" / "agents" / "missing-field.toml").write_text(
        'name = "missing-field"\n'
        'description = "Missing developer instructions."\n',
        encoding="utf-8",
    )
    for suffix in ("a", "b"):
        (root / ".codex" / "agents" / f"duplicate-{suffix}.toml").write_text(
            'name = "duplicate-agent"\n'
            'description = "Duplicate agent route."\n'
            'developer_instructions = """Read AGENTS.md."""\n',
            encoding="utf-8",
        )

    (root / ".agents" / "skills" / "missing-entrypoint").mkdir(parents=True)
    (root / ".agents" / "skills" / "missing-description").mkdir(parents=True)
    (root / ".agents" / "skills" / "missing-description" / "SKILL.md").write_text(
        "---\n"
        "name: missing-description\n"
        "---\n"
        "# Missing Description\n",
        encoding="utf-8",
    )
    for suffix in ("a", "b"):
        skill_dir = root / ".agents" / "skills" / f"duplicate-skill-{suffix}"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: duplicate-skill\n"
            "description: Use when testing duplicate skill routes.\n"
            "---\n"
            "# Duplicate Skill\n",
            encoding="utf-8",
        )

    script = root / "scripts" / "unvalidated-script"
    script.write_text("#!/usr/bin/env bash\necho unvalidated\n", encoding="utf-8")
    return root


def create_scale_lab(root: str | Path, scale_paths: int = 1000) -> Path:
    root = Path(root)
    _make_common_dirs(root)
    (root / "AGENTS.md").write_text("# Rules\nUse registry/current-progress.md.\n", encoding="utf-8")
    (root / "README.md").write_text("# Scale Lab\nSynthetic high-path Waterflow fixture.\n", encoding="utf-8")
    (root / "registry" / "current-progress.md").write_text("# Progress\nIn progress.\n", encoding="utf-8")
    (root / "waterflow" / "auditor.py").write_text("def placeholder():\n    return True\n", encoding="utf-8")
    (root / "tests" / "test_placeholder.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")
    (root / "docs" / "design.md").write_text("# Design\n", encoding="utf-8")

    counts = _scale_counts(scale_paths)
    for index in range(counts["agents"]):
        (root / ".codex" / "agents" / f"agent-{index:04d}.toml").write_text(
            f'name = "agent-{index:04d}"\n'
            f'description = "Synthetic scale agent {index}."\n'
            'developer_instructions = """Read AGENTS.md and registry/VALIDATION.md."""\n',
            encoding="utf-8",
        )
    for index in range(counts["skills"]):
        skill_dir = root / ".agents" / "skills" / f"skill-{index:04d}"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            f"name: skill-{index:04d}\n"
            f"description: Use when testing synthetic route {index}.\n"
            "---\n"
            f"# Skill {index:04d}\n",
            encoding="utf-8",
        )

    script_names: list[str] = []
    for index in range(counts["scripts"]):
        script_name = f"script-{index:04d}"
        script_names.append(script_name)
        script = root / "scripts" / script_name
        script.write_text("#!/usr/bin/env bash\nset -euo pipefail\necho ok\n", encoding="utf-8")
        script.chmod(script.stat().st_mode | stat.S_IXUSR)

    for index in range(counts["docs"]):
        (root / "docs" / f"doc-{index:04d}.md").write_text(f"# Doc {index:04d}\n", encoding="utf-8")
    for index in range(counts["tests"]):
        (root / "tests" / f"test_scale_{index:04d}.py").write_text(
            f"def test_scale_{index:04d}():\n    assert True\n",
            encoding="utf-8",
        )
    for index in range(counts["workspaces"]):
        (root / "workspaces" / f"task-{index:04d}").mkdir(parents=True)

    validation_lines = ["# Validation", "", "Synthetic script references:"]
    validation_lines.extend(f"- scripts/{name}" for name in script_names)
    (root / "registry" / "VALIDATION.md").write_text("\n".join(validation_lines) + "\n", encoding="utf-8")
    return root


def create_needle_lab(root: str | Path, scale_paths: int = 1000) -> Path:
    root = create_scale_lab(root, scale_paths=scale_paths)
    (root / "registry" / "needle-empty.md").write_text("", encoding="utf-8")

    skill_dir = root / ".agents" / "skills" / "needle-missing-description"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: needle-missing-description\n"
        "---\n"
        "# Needle Missing Description\n",
        encoding="utf-8",
    )

    script = root / "scripts" / "needle-unvalidated-script"
    script.write_text("#!/usr/bin/env bash\necho needle\n", encoding="utf-8")
    return root


def build_stress_markdown(results: dict[str, Any]) -> str:
    problem = results["problem_lab"]
    scale = results["scale_lab"]
    needle = results["needle_lab"]
    validation = results["validation_runner"]
    lines = [
        "# Waterflow Stress Results",
        "",
        f"- Generated: `{results['generated_at']}`",
        f"- Status: `{results['status']}`",
        f"- Run dir: `{results['run_dir']}`",
        "",
        "## Harness Philosophy",
        "",
        f"- Purpose: {results['harness_philosophy']['purpose']}",
        f"- Pass definition: {results['harness_philosophy']['pass_definition']}",
        f"- Non-goal: {results['harness_philosophy']['non_goal']}",
        f"- Isolation: {results['harness_philosophy']['isolation']}",
        "",
        "## Harness Criteria",
        "",
    ]
    for criterion in results["harness_criteria"]:
        status = "pass" if criterion["passed"] else "fail"
        lines.extend(
            [
                f"### {criterion['name']}: {status}",
                "",
                criterion["description"],
                "",
            ]
        )
        if criterion["evidence"]:
            lines.extend(["Evidence:", *[f"- `{item}`" for item in criterion["evidence"]], ""])

    lines.extend(
        [
            "## Detector Coverage",
            "",
            f"- Implemented detector codes: `{len(results['detector_coverage']['implemented_codes'])}`",
            f"- Expected problem codes: `{len(results['detector_coverage']['expected_problem_codes'])}`",
            f"- Uncovered implemented codes: `{len(results['detector_coverage']['uncovered_implemented_codes'])}`",
            f"- Expected codes without implementation: `{len(results['detector_coverage']['expected_without_implementation'])}`",
            "",
        ]
    )
    lines.extend(
        [
        "## Problem Lab",
        "",
        f"- Findings: `{problem['finding_count']}`",
        f"- Missing expected codes: `{len(problem['missing_expected_codes'])}`",
        "",
        "Detected codes:",
        *[f"- `{code}`" for code in problem["detected_codes"]],
        "",
        "## Scale Lab",
        "",
        f"- Requested scale paths: `{scale['requested_scale_paths']}`",
        f"- Nodes: `{scale['node_count']}`",
        f"- Edges: `{scale['edge_count']}`",
        f"- Findings: `{scale['finding_count']}`",
        "",
        "## Needle Lab",
        "",
        f"- Requested scale paths: `{needle['requested_scale_paths']}`",
        f"- Nodes: `{needle['node_count']}`",
        f"- Edges: `{needle['edge_count']}`",
        f"- Findings: `{needle['finding_count']}`",
        f"- Missing expected needle codes: `{len(needle['missing_expected_codes'])}`",
        "",
        "Detected needle codes:",
        *[f"- `{code}`" for code in needle["detected_codes"]],
        "",
        "## Validation Runner",
        "",
        f"- Checks: `{validation['check_count']}`",
        f"- Passed: `{validation['passed_count']}`",
        f"- Failed: `{validation['failed_count']}`",
        f"- Timed out: `{validation['timed_out_count']}`",
        f"- Max exit code: `{validation['max_exit_code']}`",
        "",
        "## Artifacts",
        "",
        ]
    )
    lines.extend(f"- `{name}`: `{path}`" for name, path in sorted(results["artifacts"].items()))
    return "\n".join(lines) + "\n"


def stress_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run high-pressure Waterflow problem and scale fixtures.")
    parser.add_argument(
        "--output-dir",
        default="outputs/shared/waterflow/stress",
        help="Directory for generated stress fixtures and reports.",
    )
    parser.add_argument("--scale-paths", type=int, default=1000, help="Minimum node count for the scale fixture.")
    parser.add_argument("--timeout-seconds", type=int, default=1, help="Timeout for the validation-runner stress plan.")
    parser.add_argument("--json", action="store_true", help="Print stress results JSON.")
    args = parser.parse_args(argv)

    results = run_stress_suite(
        args.output_dir,
        scale_paths=args.scale_paths,
        validation_timeout_seconds=args.timeout_seconds,
    )
    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        print(f"status: {results['status']}")
        print(f"run_dir: {results['run_dir']}")
        print(f"problem_findings: {results['problem_lab']['finding_count']}")
        print(f"scale_nodes: {results['scale_lab']['node_count']}")
        print(f"needle_findings: {results['needle_lab']['finding_count']}")
        print(f"validation_failed_expected: {results['validation_runner']['failed_count']}")
        print(f"validation_timed_out_expected: {results['validation_runner']['timed_out_count']}")
    return 0 if results["status"] == "pass" else 1


def _make_common_dirs(root: Path) -> None:
    for path in (
        root / ".codex" / "agents",
        root / ".agents" / "skills",
        root / "scripts",
        root / "registry",
        root / "waterflow",
        root / "tests",
        root / "docs",
        root / "workspaces",
        root / "outputs" / "shared",
    ):
        path.mkdir(parents=True, exist_ok=True)


def _scale_counts(scale_paths: int) -> dict[str, int]:
    scale_paths = max(scale_paths, 50)
    counts = {
        "agents": max(1, int(scale_paths * 0.12)),
        "skills": max(1, int(scale_paths * 0.34)),
        "scripts": max(1, int(scale_paths * 0.22)),
        "docs": max(1, int(scale_paths * 0.12)),
        "tests": max(1, int(scale_paths * 0.12)),
    }
    used = sum(counts.values())
    counts["workspaces"] = max(1, scale_paths - used)
    return counts


def _criterion(name: str, passed: bool, description: str, evidence: list[str]) -> dict[str, Any]:
    return {
        "name": name,
        "passed": passed,
        "description": description,
        "evidence": evidence,
    }


def _validation_stress_plan(run_dir: Path) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lab_root": str(run_dir),
        "summary": {"check_count": 3, "max_risk": "P2"},
        "checks": [
            {
                "command": "python3 -c 'print(\"stress-ok\")'",
                "risk": "P2",
                "route_kinds": ["stress"],
                "paths": ["validation/pass"],
            },
            {
                "command": "python3 -c 'import sys; print(\"stress-fail\"); sys.exit(7)'",
                "risk": "P2",
                "route_kinds": ["stress"],
                "paths": ["validation/fail"],
            },
            {
                "command": "python3 -c 'import time; print(\"stress-timeout\"); time.sleep(5)'",
                "risk": "P2",
                "route_kinds": ["stress"],
                "paths": ["validation/timeout"],
            },
        ],
    }


def _write_stress_artifacts(
    run_dir: Path,
    results: dict[str, Any],
    problem_report: dict[str, Any],
    scale_report: dict[str, Any],
    validation_results: dict[str, Any],
) -> dict[str, str]:
    artifacts = {
        "problem_report_json": str(run_dir / "problem-report.json"),
        "problem_report_markdown": str(run_dir / "problem-report.md"),
        "problem_repair_briefs": str(run_dir / "problem-repair-briefs.md"),
        "scale_report_json": str(run_dir / "scale-report.json"),
        "scale_report_markdown": str(run_dir / "scale-report.md"),
        "needle_report_json": str(run_dir / "needle-report.json"),
        "needle_report_markdown": str(run_dir / "needle-report.md"),
        "needle_repair_briefs": str(run_dir / "needle-repair-briefs.md"),
        "validation_results_json": str(run_dir / "validation-results.json"),
        "validation_results_markdown": str(run_dir / "validation-results.md"),
    }
    Path(artifacts["problem_report_json"]).write_text(
        json.dumps(problem_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(artifacts["problem_report_markdown"]).write_text(build_markdown_report(problem_report), encoding="utf-8")
    Path(artifacts["problem_repair_briefs"]).write_text(build_fix_briefs(problem_report), encoding="utf-8")
    Path(artifacts["scale_report_json"]).write_text(
        json.dumps(scale_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(artifacts["scale_report_markdown"]).write_text(build_markdown_report(scale_report), encoding="utf-8")
    needle_report = scan_lab(run_dir / "needle-lab")
    Path(artifacts["needle_report_json"]).write_text(
        json.dumps(needle_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(artifacts["needle_report_markdown"]).write_text(build_markdown_report(needle_report), encoding="utf-8")
    Path(artifacts["needle_repair_briefs"]).write_text(build_fix_briefs(needle_report), encoding="utf-8")
    Path(artifacts["validation_results_json"]).write_text(
        json.dumps(validation_results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(artifacts["validation_results_markdown"]).write_text(
        build_validation_results_markdown(validation_results),
        encoding="utf-8",
    )
    return artifacts


if __name__ == "__main__":
    sys.exit(stress_main())
