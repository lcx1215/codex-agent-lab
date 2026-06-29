from __future__ import annotations

import argparse
import json
import stat
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .auditor import (
    build_change_briefs,
    build_fix_briefs,
    build_markdown_report,
    build_path_index,
    build_route_index,
    build_route_index_markdown,
    build_validation_results_markdown,
    diff_path_indexes,
    run_validation_plan,
    scan_lab,
)


INCIDENT_EXPECTED_CODES = {
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

INCIDENT_PHILOSOPHY = {
    "purpose": "Exercise the full Waterflow incident loop: inject a realistic multi-route failure, detect it, capture failing command evidence, and produce a handoff for Codex or Claude.",
    "pass_definition": "An incident pass means the intentionally broken fixture was detected and reported with actionable evidence; it does not mean the fixture or the real lab is repaired.",
    "isolation": "The broken fixture is generated under outputs/shared/waterflow/incidents and is not part of the real lab source graph.",
}

REPAIR_ORDER = [
    {
        "priority": 1,
        "title": "Restore hard blockers first",
        "codes": ["MISSING_CORE_PATH", "AGENT_TOML_INVALID", "AGENT_MISSING_FIELD", "SKILL_MISSING_ENTRYPOINT"],
        "reason": "Codex and Claude cannot route work reliably while core surfaces, agent metadata, or skill entrypoints are broken.",
    },
    {
        "priority": 2,
        "title": "Remove ambiguous routing",
        "codes": ["DUPLICATE_AGENT_NAME", "DUPLICATE_SKILL_NAME"],
        "reason": "Duplicate names make delegation nondeterministic and can send repair work to the wrong route.",
    },
    {
        "priority": 3,
        "title": "Repair execution and boundary evidence",
        "codes": [
            "SCRIPT_NOT_EXECUTABLE",
            "SCRIPT_WITHOUT_VALIDATION_REFERENCE",
            "CROSS_PROJECT_REFERENCE",
            "PROGRESS_WITHOUT_VALIDATION",
            "EMPTY_REGISTRY_FILE",
            "SKILL_MISSING_FIELD",
        ],
        "reason": "After routing is unblocked, make commands runnable, remove cross-boundary leakage, and replace claims with evidence.",
    },
    {
        "priority": 4,
        "title": "Run the smallest verification spine",
        "codes": [],
        "reason": "Re-run the incident harness, unit tests, and the normal Waterflow scan before claiming repair completion.",
    },
]


def run_incident_suite(
    output_root: str | Path,
    validation_timeout_seconds: int = 1,
) -> dict[str, Any]:
    output_root = Path(output_root).expanduser().resolve()
    run_id = datetime.now(timezone.utc).strftime("incident-%Y%m%dT%H%M%SZ")
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    baseline_root = run_dir / "baseline-lab"
    incident_root = run_dir / "incident-lab"
    create_clean_baseline_lab(baseline_root)
    create_complex_incident_lab(incident_root)

    baseline_report = scan_lab(baseline_root)
    incident_report = scan_lab(incident_root)
    previous_index = build_path_index(baseline_report)
    current_index = build_path_index(incident_report)
    path_diff = diff_path_indexes(previous_index, current_index)
    incident_report["path_diff"] = path_diff
    route_index = build_route_index(incident_report)
    validation_plan = _incident_validation_plan(run_dir)
    validation_results = run_validation_plan(
        validation_plan,
        root=run_dir,
        timeout_seconds=validation_timeout_seconds,
        max_output_chars=4000,
    )

    finding_codes = sorted({finding["code"] for finding in incident_report["findings"]})
    missing_expected_codes = sorted(INCIDENT_EXPECTED_CODES - set(finding_codes))
    validation_summary = validation_results["summary"]
    validation_expected = (
        validation_summary["check_count"] == 3
        and validation_summary["passed_count"] == 1
        and validation_summary["failed_count"] == 2
        and validation_summary["timed_out_count"] == 1
        and validation_summary["max_exit_code"] == 124
    )
    diff_expected = (
        path_diff["summary"]["added_count"] > 0
        and path_diff["summary"]["removed_count"] > 0
        and path_diff["summary"]["changed_count"] > 0
    )

    criteria = [
        _criterion(
            "baseline_starts_clean",
            baseline_report["summary"]["finding_count"] == 0,
            "The comparison baseline should be clean so diff and finding evidence point to the injected incident.",
            [] if baseline_report["summary"]["finding_count"] == 0 else [str(baseline_report["summary"]["finding_count"])],
        ),
        _criterion(
            "expected_incident_codes_detected",
            not missing_expected_codes,
            "The complex fixture should trigger every expected Waterflow defect family.",
            missing_expected_codes,
        ),
        _criterion(
            "diff_contains_added_removed_changed_paths",
            diff_expected,
            "The incident should create a realistic changed-path surface, not just a static bad snapshot.",
            []
            if diff_expected
            else [json.dumps(path_diff["summary"], sort_keys=True)],
        ),
        _criterion(
            "validation_failures_are_captured",
            validation_expected,
            "The incident validation plan should record one pass, one failing command, and one timeout.",
            [] if validation_expected else [json.dumps(validation_summary, sort_keys=True)],
        ),
        _criterion(
            "route_index_prioritizes_repair_surface",
            route_index["summary"]["route_count"] >= 5 and route_index["summary"]["max_risk"] in {"P0", "P1"},
            "The route index should collapse the incident into route families with a high-risk summary.",
            []
            if route_index["summary"]["route_count"] >= 5 and route_index["summary"]["max_risk"] in {"P0", "P1"}
            else [json.dumps(route_index["summary"], sort_keys=True)],
        ),
        _criterion(
            "fixtures_are_isolated",
            baseline_root.is_relative_to(run_dir) and incident_root.is_relative_to(run_dir),
            "Broken incident fixtures must stay inside the generated incident run directory.",
            []
            if baseline_root.is_relative_to(run_dir) and incident_root.is_relative_to(run_dir)
            else [str(baseline_root), str(incident_root)],
        ),
    ]
    status = "pass" if all(item["passed"] for item in criteria) else "fail"

    artifacts = _artifact_paths(run_dir)
    results = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "incident_philosophy": INCIDENT_PHILOSOPHY,
        "harness_criteria": criteria,
        "run_dir": str(run_dir),
        "baseline": {
            "root": str(baseline_root),
            "finding_count": baseline_report["summary"]["finding_count"],
            "node_count": baseline_report["summary"]["node_count"],
        },
        "incident": {
            "root": str(incident_root),
            "finding_count": incident_report["summary"]["finding_count"],
            "detected_codes": finding_codes,
            "detected_code_counts": dict(Counter(finding["code"] for finding in incident_report["findings"])),
            "missing_expected_codes": missing_expected_codes,
            "finding_counts_by_severity": incident_report["summary"]["finding_counts_by_severity"],
        },
        "path_diff": path_diff["summary"],
        "route_index": route_index["summary"],
        "validation_runner": validation_summary,
        "repair_order": REPAIR_ORDER,
        "artifacts": artifacts,
    }
    _write_incident_artifacts(
        artifacts,
        results,
        baseline_report,
        incident_report,
        route_index,
        validation_plan,
        validation_results,
    )
    return results


def create_clean_baseline_lab(root: str | Path) -> Path:
    root = Path(root)
    _make_common_dirs(root)
    (root / "AGENTS.md").write_text(
        "# Rules\nUse README.md, registry/current-progress.md, and registry/VALIDATION.md.\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "# Clean Baseline Lab\nThis baseline represents the last known good waterway state.\n",
        encoding="utf-8",
    )
    (root / "registry" / "current-progress.md").write_text("# Progress\nIn progress.\n", encoding="utf-8")
    (root / "registry" / "VALIDATION.md").write_text(
        "# Validation\n\n- scripts/smoke-check: pass in the clean baseline.\n",
        encoding="utf-8",
    )
    (root / ".codex" / "agents" / "handoff-owner.toml").write_text(
        'name = "handoff-owner"\n'
        'description = "Owns clean handoff routing."\n'
        'developer_instructions = """Read AGENTS.md, README.md, and registry/VALIDATION.md."""\n',
        encoding="utf-8",
    )
    skill_dir = root / ".agents" / "skills" / "handoff-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: handoff-skill\n"
        "description: Use when validating clean handoff routing.\n"
        "---\n"
        "# Handoff Skill\n",
        encoding="utf-8",
    )
    script = root / "scripts" / "smoke-check"
    script.write_text("#!/usr/bin/env bash\nset -euo pipefail\necho baseline-ok\n", encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    (root / "waterflow" / "auditor.py").write_text("def baseline():\n    return True\n", encoding="utf-8")
    (root / "tests" / "test_baseline.py").write_text("def test_baseline():\n    assert True\n", encoding="utf-8")
    (root / "docs" / "design.md").write_text("# Baseline Design\n", encoding="utf-8")
    (root / "workspaces" / "handoff-check").mkdir(parents=True)
    return root


def create_complex_incident_lab(root: str | Path) -> Path:
    root = Path(root)
    _make_common_dirs(root)
    (root / "AGENTS.md").write_text(
        "# Rules\n"
        "Incident fixture: a rushed handoff accidentally references "
        "/Users/liuchengxu/Desktop/lcx-s-openclaw and claims completion without proof.\n",
        encoding="utf-8",
    )
    (root / "registry" / "current-progress.md").write_text(
        "# Progress\nCompleted all routing repairs and passed release validation.\n",
        encoding="utf-8",
    )
    (root / "registry" / "VALIDATION.md").write_text("# Validation\n", encoding="utf-8")
    (root / "registry" / "empty-claim.md").write_text("", encoding="utf-8")
    (root / "waterflow" / "auditor.py").write_text("def incident():\n    return False\n", encoding="utf-8")
    (root / "tests" / "test_incident.py").write_text("def test_incident():\n    assert True\n", encoding="utf-8")
    (root / "docs" / "design.md").write_text("# Incident Design\nKnown-bad handoff for detector testing.\n", encoding="utf-8")
    (root / "workspaces" / "release-repair").mkdir(parents=True)

    (root / ".codex" / "agents" / "broken-syntax.toml").write_text(
        'name = "broken-syntax"\n'
        "developer_instructions = [\n",
        encoding="utf-8",
    )
    (root / ".codex" / "agents" / "missing-owner.toml").write_text(
        'name = "missing-owner"\n'
        'description = "Missing developer instructions after a rushed migration."\n',
        encoding="utf-8",
    )
    for suffix in ("a", "b"):
        (root / ".codex" / "agents" / f"duplicate-owner-{suffix}.toml").write_text(
            'name = "duplicate-owner"\n'
            'description = "Ambiguous owner route."\n'
            'developer_instructions = """Repair the same workflow route."""\n',
            encoding="utf-8",
        )

    (root / ".agents" / "skills" / "missing-entrypoint").mkdir(parents=True)
    missing_meta = root / ".agents" / "skills" / "missing-description"
    missing_meta.mkdir(parents=True)
    (missing_meta / "SKILL.md").write_text(
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
            "name: duplicate-repair-skill\n"
            "description: Use when testing duplicate repair skill routing.\n"
            "---\n"
            "# Duplicate Repair Skill\n",
            encoding="utf-8",
        )

    smoke = root / "scripts" / "smoke-check"
    smoke.write_text("#!/usr/bin/env bash\nset -euo pipefail\necho incident-smoke\n", encoding="utf-8")
    smoke.chmod(smoke.stat().st_mode | stat.S_IXUSR)
    release = root / "scripts" / "release-handoff"
    release.write_text("#!/usr/bin/env bash\necho release-handoff\n", encoding="utf-8")
    return root


def build_incident_markdown(results: dict[str, Any]) -> str:
    lines = [
        "# Waterflow Complex Incident Results",
        "",
        f"- Generated: `{results['generated_at']}`",
        f"- Status: `{results['status']}`",
        f"- Run dir: `{results['run_dir']}`",
        f"- Findings: `{results['incident']['finding_count']}`",
        f"- Missing expected codes: `{len(results['incident']['missing_expected_codes'])}`",
        "",
        "## Philosophy",
        "",
        f"- Purpose: {results['incident_philosophy']['purpose']}",
        f"- Pass definition: {results['incident_philosophy']['pass_definition']}",
        f"- Isolation: {results['incident_philosophy']['isolation']}",
        "",
        "## Criteria",
        "",
    ]
    for criterion in results["harness_criteria"]:
        status = "pass" if criterion["passed"] else "fail"
        lines.extend([f"### {criterion['name']}: {status}", "", criterion["description"], ""])
        if criterion["evidence"]:
            lines.extend(["Evidence:", *[f"- `{item}`" for item in criterion["evidence"]], ""])
    lines.extend(
        [
            "## Detected Codes",
            "",
            *[f"- `{code}`" for code in results["incident"]["detected_codes"]],
            "",
            "## Path Diff",
            "",
            f"- Added: `{results['path_diff']['added_count']}`",
            f"- Removed: `{results['path_diff']['removed_count']}`",
            f"- Changed: `{results['path_diff']['changed_count']}`",
            "",
            "## Validation Runner",
            "",
            f"- Checks: `{results['validation_runner']['check_count']}`",
            f"- Passed: `{results['validation_runner']['passed_count']}`",
            f"- Failed: `{results['validation_runner']['failed_count']}`",
            f"- Timed out: `{results['validation_runner']['timed_out_count']}`",
            f"- Max exit code: `{results['validation_runner']['max_exit_code']}`",
            "",
            "## Artifacts",
            "",
        ]
    )
    lines.extend(f"- `{name}`: `{path}`" for name, path in sorted(results["artifacts"].items()))
    return "\n".join(lines) + "\n"


def build_codex_claude_handoff(
    results: dict[str, Any],
    incident_report: dict[str, Any],
    route_index: dict[str, Any],
    validation_results: dict[str, Any],
) -> str:
    lines = [
        "# Waterflow Incident Handoff for Codex or Claude",
        "",
        "This is an actionable repair packet for a deliberately broken Waterflow incident fixture.",
        "Do not treat `status: pass` as repaired; it means Waterflow successfully detected and reported the incident.",
        "",
        "## Incident Summary",
        "",
        f"- Run dir: `{results['run_dir']}`",
        f"- Fixture root: `{results['incident']['root']}`",
        f"- Status: `{results['status']}`",
        f"- Findings: `{results['incident']['finding_count']}`",
        f"- Severity counts: `{json.dumps(results['incident']['finding_counts_by_severity'], sort_keys=True)}`",
        f"- Validation failures captured: `{results['validation_runner']['failed_count']}`",
        f"- Validation timeouts captured: `{results['validation_runner']['timed_out_count']}`",
        "",
        "## Route Families",
        "",
        "| Route | Risk | Paths | Findings | Checks |",
        "| --- | --- | ---: | --- | ---: |",
    ]
    for route in route_index["routes"].values():
        findings = ", ".join(f"`{code}`" for code in route["finding_codes"]) or "-"
        lines.append(
            f"| `{route['kind']}` | `{route['max_risk']}` | {route['path_count']} | "
            f"{findings} | {len(route['recommended_checks'])} |"
        )

    lines.extend(["", "## Findings", ""])
    for index, finding in enumerate(incident_report["findings"], start=1):
        evidence = ", ".join(f"`{item}`" for item in finding["evidence"])
        lines.extend(
            [
                f"### {index}. {finding['severity']} {finding['code']}",
                "",
                finding["message"],
                "",
                f"Evidence: {evidence}",
                "",
                f"Repair: {finding['repair_brief']}",
                "",
            ]
        )

    failed_checks = [check for check in validation_results["checks"] if not check["passed"]]
    lines.extend(["## Failed Validation Evidence", ""])
    for check in failed_checks:
        lines.extend(
            [
                f"### Check {check['index']}",
                "",
                f"- command: `{check['command']}`",
                f"- exit_code: `{check['exit_code']}`",
                f"- timed_out: `{str(check['timed_out']).lower()}`",
                f"- route_kinds: `{', '.join(check['route_kinds'])}`",
                "",
            ]
        )
        if check["stdout"]:
            lines.extend(["stdout:", "", "```text", check["stdout"].rstrip(), "```", ""])
        if check["stderr"]:
            lines.extend(["stderr:", "", "```text", check["stderr"].rstrip(), "```", ""])

    lines.extend(["## Repair Order", ""])
    for item in results["repair_order"]:
        codes = ", ".join(f"`{code}`" for code in item["codes"]) or "final verification"
        lines.extend(
            [
                f"{item['priority']}. {item['title']}",
                f"   Codes: {codes}",
                f"   Reason: {item['reason']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Minimal Verification Commands",
            "",
            "- `scripts/waterflow-incident --timeout-seconds 1`",
            "- `python3 -m unittest discover -s tests`",
            "- `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last`",
            "- `scripts/waterflow-verify`",
            "",
            "## Artifact Map",
            "",
        ]
    )
    lines.extend(f"- `{name}`: `{path}`" for name, path in sorted(results["artifacts"].items()))
    return "\n".join(lines) + "\n"


def incident_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a complex Waterflow incident fixture and handoff report.")
    parser.add_argument(
        "--output-dir",
        default="outputs/shared/waterflow/incidents",
        help="Directory for generated incident fixtures and reports.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=1, help="Timeout for the incident validation plan.")
    parser.add_argument("--json", action="store_true", help="Print incident results JSON.")
    args = parser.parse_args(argv)

    results = run_incident_suite(args.output_dir, validation_timeout_seconds=args.timeout_seconds)
    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        print(f"status: {results['status']}")
        print(f"run_dir: {results['run_dir']}")
        print(f"findings: {results['incident']['finding_count']}")
        print(f"missing_expected_codes: {len(results['incident']['missing_expected_codes'])}")
        print(f"validation_failed_expected: {results['validation_runner']['failed_count']}")
        print(f"validation_timed_out_expected: {results['validation_runner']['timed_out_count']}")
        print(f"handoff: {results['artifacts']['codex_claude_handoff']}")
    return 0 if results["status"] == "pass" else 1


def _write_incident_artifacts(
    artifacts: dict[str, str],
    results: dict[str, Any],
    baseline_report: dict[str, Any],
    incident_report: dict[str, Any],
    route_index: dict[str, Any],
    validation_plan: dict[str, Any],
    validation_results: dict[str, Any],
) -> None:
    Path(artifacts["baseline_report_json"]).write_text(
        json.dumps(baseline_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(artifacts["problem_report_json"]).write_text(
        json.dumps(incident_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(artifacts["problem_report_markdown"]).write_text(build_markdown_report(incident_report), encoding="utf-8")
    Path(artifacts["repair_briefs"]).write_text(build_fix_briefs(incident_report), encoding="utf-8")
    Path(artifacts["route_index_json"]).write_text(
        json.dumps(route_index, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(artifacts["route_index_markdown"]).write_text(build_route_index_markdown(route_index), encoding="utf-8")
    Path(artifacts["path_diff_json"]).write_text(
        json.dumps(incident_report["path_diff"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(artifacts["change_briefs"]).write_text(build_change_briefs(incident_report["path_diff"]), encoding="utf-8")
    Path(artifacts["validation_plan_json"]).write_text(
        json.dumps(validation_plan, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(artifacts["validation_results_json"]).write_text(
        json.dumps(validation_results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(artifacts["validation_results_markdown"]).write_text(
        build_validation_results_markdown(validation_results),
        encoding="utf-8",
    )
    Path(artifacts["incident_report_json"]).write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(artifacts["incident_report_markdown"]).write_text(build_incident_markdown(results), encoding="utf-8")
    Path(artifacts["codex_claude_handoff"]).write_text(
        build_codex_claude_handoff(results, incident_report, route_index, validation_results),
        encoding="utf-8",
    )


def _artifact_paths(run_dir: Path) -> dict[str, str]:
    return {
        "baseline_report_json": str(run_dir / "baseline-report.json"),
        "change_briefs": str(run_dir / "change-briefs.md"),
        "codex_claude_handoff": str(run_dir / "codex-claude-handoff.md"),
        "incident_report_json": str(run_dir / "incident-report.json"),
        "incident_report_markdown": str(run_dir / "incident-report.md"),
        "path_diff_json": str(run_dir / "path-diff.json"),
        "problem_report_json": str(run_dir / "problem-report.json"),
        "problem_report_markdown": str(run_dir / "problem-report.md"),
        "repair_briefs": str(run_dir / "repair-briefs.md"),
        "route_index_json": str(run_dir / "route-index.json"),
        "route_index_markdown": str(run_dir / "route-index.md"),
        "validation_plan_json": str(run_dir / "validation-plan.json"),
        "validation_results_json": str(run_dir / "validation-results.json"),
        "validation_results_markdown": str(run_dir / "validation-results.md"),
    }


def _incident_validation_plan(run_dir: Path) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lab_root": str(run_dir),
        "summary": {"check_count": 3, "max_risk": "P1"},
        "checks": [
            {
                "command": "python3 -c 'print(\"incident-pass: baseline evidence readable\")'",
                "risk": "P2",
                "route_kinds": ["incident"],
                "paths": ["validation/pass"],
            },
            {
                "command": "python3 -c 'import sys; print(\"incident-fail: broken handoff reproduced\"); sys.exit(9)'",
                "risk": "P1",
                "route_kinds": ["incident"],
                "paths": ["validation/fail"],
            },
            {
                "command": "python3 -c 'import time; print(\"incident-timeout: stuck repair loop\"); time.sleep(5)'",
                "risk": "P1",
                "route_kinds": ["incident"],
                "paths": ["validation/timeout"],
            },
        ],
    }


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


def _criterion(name: str, passed: bool, description: str, evidence: list[str]) -> dict[str, Any]:
    return {
        "name": name,
        "passed": passed,
        "description": description,
        "evidence": evidence,
    }


if __name__ == "__main__":
    sys.exit(incident_main())
