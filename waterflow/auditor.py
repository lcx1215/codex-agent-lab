from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tomllib
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_AGENT_FIELDS = ("name", "description", "developer_instructions")
REQUIRED_CORE_PATHS = (
    "AGENTS.md",
    "README.md",
    ".codex/agents",
    ".agents/skills",
    "scripts",
    "registry",
    "registry/current-progress.md",
    "registry/VALIDATION.md",
    "workspaces",
)
TEXT_SUFFIXES = {".md", ".toml", ".py", ".sh", ".bash", ".json", ".yaml", ".yml", ""}
EXCLUDED_DIRS = {".git", ".codex-home", "__pycache__"}
EXCLUDED_SKILL_DIRS = {".system"}


@dataclass(frozen=True)
class Node:
    id: str
    kind: str
    path: str
    label: str
    metadata: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "path": self.path,
            "label": self.label,
            "metadata": self.metadata,
        }


def scan_lab(root: str | Path) -> dict[str, Any]:
    lab_root = Path(root).expanduser().resolve()
    nodes: list[Node] = []
    edges: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    def add_node(kind: str, path: Path, label: str | None = None, **metadata: Any) -> Node:
        rel = _rel(path, lab_root)
        node = Node(
            id=f"{kind}:{rel}",
            kind=kind,
            path=rel,
            label=label or path.name or rel,
            metadata=metadata,
        )
        nodes.append(node)
        edges.append({"source": "lab-root", "target": node.id, "type": "contains", "evidence": rel})
        return node

    nodes.append(Node("lab-root", "root", ".", lab_root.name, {"absolute_path": str(lab_root)}))

    for required in REQUIRED_CORE_PATHS:
        path = lab_root / required
        if not path.exists():
            findings.append(
                _finding(
                    "P1",
                    "MISSING_CORE_PATH",
                    f"Required core path is missing: {required}",
                    [required],
                    f"Create `{required}` or update the lab contract if this path is intentionally removed.",
                )
            )

    for rel, kind in (("AGENTS.md", "rules"), ("README.md", "readme")):
        path = lab_root / rel
        if path.exists():
            add_node(kind, path, hash=_file_hash(path), size=_safe_size(path))

    _scan_agents(lab_root, add_node, edges, findings)
    _scan_skills(lab_root, add_node, findings)
    _scan_scripts(lab_root, add_node, findings)
    _scan_registry(lab_root, add_node, findings)
    _scan_support_files(lab_root, add_node)
    _scan_workspaces(lab_root, add_node)
    _scan_cross_project_references(lab_root, findings)

    validation_text = _read_text(lab_root / "registry" / "VALIDATION.md")
    progress_text = _read_text(lab_root / "registry" / "current-progress.md")
    if progress_text and re.search(r"\b(done|complete|completed|passed)\b", progress_text, re.I):
        if not validation_text or len(validation_text.strip()) < 30:
            findings.append(
                _finding(
                    "P2",
                    "PROGRESS_WITHOUT_VALIDATION",
                    "Progress claims completion-like state but validation evidence is missing or too thin.",
                    ["registry/current-progress.md", "registry/VALIDATION.md"],
                    "Run the relevant verification commands and record exact evidence in `registry/VALIDATION.md`.",
                )
            )

    report = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lab_root": str(lab_root),
        "summary": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "path_count": len(nodes),
            "finding_count": len(findings),
            "finding_counts_by_severity": _severity_counts(findings),
        },
        "graph": {
            "nodes": [node.as_dict() for node in nodes],
            "edges": edges,
        },
        "findings": findings,
    }
    return report


def build_markdown_report(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Waterflow Auditor Report",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Lab root: `{report['lab_root']}`",
        f"- Nodes: `{summary['node_count']}`",
        f"- Edges: `{summary['edge_count']}`",
        f"- Findings: `{summary['finding_count']}`",
        "",
        "## Findings",
        "",
    ]
    if not report["findings"]:
        lines.append("No findings.")
    for finding in report["findings"]:
        lines.extend(
            [
                f"### {finding['severity']} {finding['code']}",
                "",
                finding["message"],
                "",
                "Evidence:",
                *[f"- `{item}`" for item in finding["evidence"]],
                "",
                "Repair brief:",
                "",
                finding["repair_brief"],
                "",
            ]
        )

    lines.extend(
        [
            "## Graph Summary",
            "",
            "| Kind | Count |",
            "| --- | ---: |",
        ]
    )
    for kind, count in sorted(_kind_counts(report["graph"]["nodes"]).items()):
        lines.append(f"| `{kind}` | {count} |")
    lines.append("")
    if "path_diff" in report:
        lines.extend([build_diff_markdown(report["path_diff"]), ""])
    return "\n".join(lines)


def build_fix_briefs(report: dict[str, Any]) -> str:
    lines = [
        "# Waterflow Repair Briefs",
        "",
        "Use these briefs with Codex or Claude. Keep fixes scoped to the cited evidence unless the user expands scope.",
        "",
    ]
    if not report["findings"]:
        lines.append("No repair briefs were generated because no findings were detected.")
        return "\n".join(lines) + "\n"
    for idx, finding in enumerate(report["findings"], start=1):
        evidence = "\n".join(f"- `{item}`" for item in finding["evidence"])
        lines.extend(
            [
                f"## Brief {idx}: {finding['code']}",
                "",
                f"Severity: `{finding['severity']}`",
                "",
                f"Problem: {finding['message']}",
                "",
                "Evidence:",
                evidence,
                "",
                "Requested fix:",
                finding["repair_brief"],
                "",
                "Verification:",
                "- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab`.",
                "- Confirm the finding is gone or explicitly documented as accepted risk.",
                "",
            ]
        )
    return "\n".join(lines)


def build_path_index(report: dict[str, Any]) -> dict[str, Any]:
    paths: dict[str, dict[str, Any]] = {}
    for node in report["graph"]["nodes"]:
        metadata = node.get("metadata", {})
        paths[node["path"]] = {
            "id": node["id"],
            "kind": node["kind"],
            "label": node["label"],
            "hash": metadata.get("hash", ""),
            "size": metadata.get("size", 0),
        }
    return {
        "schema_version": 1,
        "generated_at": report["generated_at"],
        "lab_root": report["lab_root"],
        "path_count": len(paths),
        "paths": dict(sorted(paths.items())),
    }


def build_route_index(report: dict[str, Any]) -> dict[str, Any]:
    routes: dict[str, dict[str, Any]] = {}
    command_index: dict[str, dict[str, Any]] = {}
    risk_index: dict[str, set[str]] = {"P0": set(), "P1": set(), "P2": set(), "P3": set()}

    for node in report["graph"]["nodes"]:
        path = node["path"]
        if path == "." or node["kind"] in {"root", "workspace-root", "workspace"}:
            continue
        impact = classify_path_impact(path)
        route = routes.setdefault(
            impact["kind"],
            {
                "kind": impact["kind"],
                "max_risk": impact["risk"],
                "paths": set(),
                "recommended_checks": set(),
                "changed_paths": set(),
                "finding_codes": set(),
            },
        )
        route["max_risk"] = _max_risk(route["max_risk"], impact["risk"])
        route["paths"].add(path)
        risk_index.setdefault(impact["risk"], set()).add(path)
        for command in impact["recommended_checks"]:
            route["recommended_checks"].add(command)
            command_entry = command_index.setdefault(
                command,
                {
                    "command": command,
                    "max_risk": impact["risk"],
                    "route_kinds": set(),
                    "paths": set(),
                },
            )
            command_entry["max_risk"] = _max_risk(command_entry["max_risk"], impact["risk"])
            command_entry["route_kinds"].add(impact["kind"])
            command_entry["paths"].add(path)

    for finding in report.get("findings", []):
        for evidence in finding.get("evidence", [])[:1]:
            route_kind = classify_path_impact(str(evidence))["kind"]
            route = routes.setdefault(
                route_kind,
                {
                    "kind": route_kind,
                    "max_risk": finding.get("severity", "P3"),
                    "paths": set(),
                    "recommended_checks": set(),
                    "changed_paths": set(),
                    "finding_codes": set(),
                },
            )
            route["max_risk"] = _max_risk(route["max_risk"], finding.get("severity", "P3"))
            route["finding_codes"].add(finding["code"])

    for path in _changed_paths(report):
        impact = report.get("path_diff", {}).get("impact", {}).get(path, classify_path_impact(path))
        route = routes.setdefault(
            impact["kind"],
            {
                "kind": impact["kind"],
                "max_risk": impact["risk"],
                "paths": set(),
                "recommended_checks": set(),
                "changed_paths": set(),
                "finding_codes": set(),
            },
        )
        route["max_risk"] = _max_risk(route["max_risk"], impact["risk"])
        route["changed_paths"].add(path)

    materialized_routes = {
        kind: {
            "kind": entry["kind"],
            "max_risk": entry["max_risk"],
            "path_count": len(entry["paths"]),
            "changed_path_count": len(entry["changed_paths"]),
            "finding_codes": sorted(entry["finding_codes"]),
            "recommended_checks": sorted(entry["recommended_checks"]),
            "paths": sorted(entry["paths"]),
            "changed_paths": sorted(entry["changed_paths"]),
        }
        for kind, entry in sorted(routes.items())
    }
    materialized_commands = {
        command: {
            "command": command,
            "max_risk": entry["max_risk"],
            "route_kinds": sorted(entry["route_kinds"]),
            "path_count": len(entry["paths"]),
            "paths": sorted(entry["paths"]),
        }
        for command, entry in sorted(command_index.items())
    }
    materialized_risk = {
        risk: sorted(paths)
        for risk, paths in sorted(risk_index.items(), key=lambda item: _risk_rank(item[0]))
        if paths
    }
    return {
        "schema_version": 1,
        "generated_at": report["generated_at"],
        "lab_root": report["lab_root"],
        "summary": {
            "route_count": len(materialized_routes),
            "path_count": sum(route["path_count"] for route in materialized_routes.values()),
            "changed_path_count": len(_changed_paths(report)),
            "finding_count": report["summary"]["finding_count"],
            "max_risk": _max_risk_many([route["max_risk"] for route in materialized_routes.values()]),
        },
        "routes": materialized_routes,
        "risk_index": materialized_risk,
        "validation_command_index": materialized_commands,
    }


def build_route_index_markdown(route_index: dict[str, Any]) -> str:
    summary = route_index["summary"]
    lines = [
        "# Waterflow Route Index",
        "",
        f"- Generated: `{route_index['generated_at']}`",
        f"- Lab root: `{route_index['lab_root']}`",
        f"- Routes: `{summary['route_count']}`",
        f"- Paths: `{summary['path_count']}`",
        f"- Changed paths: `{summary['changed_path_count']}`",
        f"- Findings: `{summary['finding_count']}`",
        f"- Max risk: `{summary['max_risk']}`",
        "",
        "## Routes",
        "",
        "| Route | Risk | Paths | Changed | Findings | Checks |",
        "| --- | --- | ---: | ---: | --- | ---: |",
    ]
    for route in route_index["routes"].values():
        findings = ", ".join(f"`{code}`" for code in route["finding_codes"]) or "-"
        lines.append(
            f"| `{route['kind']}` | `{route['max_risk']}` | {route['path_count']} | "
            f"{route['changed_path_count']} | {findings} | {len(route['recommended_checks'])} |"
        )
    lines.extend(["", "## Validation Commands", ""])
    for command in route_index["validation_command_index"].values():
        route_kinds = ", ".join(f"`{kind}`" for kind in command["route_kinds"])
        lines.append(
            f"- `{command['command']}` covers {command['path_count']} path(s), "
            f"risk `{command['max_risk']}`, routes {route_kinds}."
        )
    return "\n".join(lines) + "\n"


def diff_path_indexes(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    previous_paths = previous.get("paths", {})
    current_paths = current.get("paths", {})
    previous_keys = set(previous_paths)
    current_keys = set(current_paths)

    added = sorted(current_keys - previous_keys)
    removed = sorted(previous_keys - current_keys)
    changed = sorted(
        path
        for path in previous_keys & current_keys
        if _path_fingerprint(previous_paths[path]) != _path_fingerprint(current_paths[path])
    )
    unchanged_count = len(previous_keys & current_keys) - len(changed)
    impacted_paths = sorted(set(added + removed + changed))
    return {
        "schema_version": 1,
        "generated_at": current.get("generated_at"),
        "previous_generated_at": previous.get("generated_at"),
        "current_generated_at": current.get("generated_at"),
        "summary": {
            "added_count": len(added),
            "removed_count": len(removed),
            "changed_count": len(changed),
            "unchanged_count": unchanged_count,
        },
        "added": added,
        "removed": removed,
        "changed": changed,
        "impact": {path: classify_path_impact(path) for path in impacted_paths},
    }


def classify_path_impact(path: str) -> dict[str, Any]:
    if path.startswith(".codex/agents/") and path.endswith(".toml"):
        return _impact(
            "agent",
            "P2",
            [
                "scripts/check-lab",
                "CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input \"Verify agent discovery only.\"",
                "scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab",
            ],
        )
    if path.startswith(".agents/skills/") and path.endswith("/SKILL.md"):
        return _impact(
            "skill",
            "P2",
            [
                "scripts/check-lab",
                "CODEX_HOME=/Users/liuchengxu/Desktop/codex-agent-lab/.codex-home codex -C /Users/liuchengxu/Desktop/codex-agent-lab debug prompt-input \"Verify skill discovery only.\"",
                "scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab",
            ],
        )
    if path.startswith("scripts/"):
        return _impact(
            "script",
            "P2",
            [
                "python3 -m unittest discover -s tests",
                "scripts/check-lab",
                "scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab",
            ],
        )
    if path.startswith("registry/"):
        return _impact(
            "registry",
            "P3",
            [
                "scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab",
            ],
        )
    if path in {"AGENTS.md", "README.md"} or path.startswith("docs/"):
        return _impact(
            "documentation",
            "P3",
            [
                "scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab",
            ],
        )
    if path.startswith("waterflow/") or path.startswith("tests/"):
        return _impact(
            "auditor-code",
            "P2",
            [
                "python3 -m unittest discover -s tests",
                "scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab",
            ],
        )
    return _impact(
        "unknown",
        "P3",
        [
            "scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab",
        ],
    )


def write_outputs(
    report: dict[str, Any],
    output_dir: str | Path,
    previous_index: dict[str, Any] | None = None,
) -> dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path_index = build_path_index(report)
    if previous_index is not None:
        report["path_diff"] = diff_path_indexes(previous_index, path_index)
    json_path = out / "waterflow-report.json"
    markdown_path = out / "waterflow-report.md"
    briefs_path = out / "waterflow-repair-briefs.md"
    validation_plan = build_validation_plan(report)
    route_index = build_route_index(report)
    changed_validation_plan = build_validation_plan(report, scope="changed")
    validation_plan_json_path = out / "waterflow-validation-plan.json"
    validation_plan_markdown_path = out / "waterflow-validation-plan.md"
    changed_validation_plan_json_path = out / "waterflow-validation-plan-changed.json"
    changed_validation_plan_markdown_path = out / "waterflow-validation-plan-changed.md"
    route_index_json_path = out / "waterflow-route-index.json"
    route_index_markdown_path = out / "waterflow-route-index.md"
    index_path = out / "waterflow-path-index.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(build_markdown_report(report), encoding="utf-8")
    briefs_path.write_text(build_fix_briefs(report), encoding="utf-8")
    validation_plan_json_path.write_text(json.dumps(validation_plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validation_plan_markdown_path.write_text(build_validation_plan_markdown(validation_plan), encoding="utf-8")
    changed_validation_plan_json_path.write_text(
        json.dumps(changed_validation_plan, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    changed_validation_plan_markdown_path.write_text(
        build_validation_plan_markdown(changed_validation_plan),
        encoding="utf-8",
    )
    route_index_json_path.write_text(json.dumps(route_index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    route_index_markdown_path.write_text(build_route_index_markdown(route_index), encoding="utf-8")
    index_path.write_text(json.dumps(path_index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs = {
        "json": str(json_path),
        "markdown": str(markdown_path),
        "repair_briefs": str(briefs_path),
        "validation_plan_json": str(validation_plan_json_path),
        "validation_plan_markdown": str(validation_plan_markdown_path),
        "changed_validation_plan_json": str(changed_validation_plan_json_path),
        "changed_validation_plan_markdown": str(changed_validation_plan_markdown_path),
        "route_index_json": str(route_index_json_path),
        "route_index_markdown": str(route_index_markdown_path),
        "path_index": str(index_path),
    }
    if previous_index is not None:
        diff_path = out / "waterflow-path-diff.json"
        change_briefs_path = out / "waterflow-change-briefs.md"
        diff_path.write_text(json.dumps(report["path_diff"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
        change_briefs_path.write_text(build_change_briefs(report["path_diff"]), encoding="utf-8")
        outputs["path_diff"] = str(diff_path)
        outputs["change_briefs"] = str(change_briefs_path)
    else:
        for stale_name in ("waterflow-path-diff.json", "waterflow-change-briefs.md"):
            stale_path = out / stale_name
            if stale_path.exists():
                stale_path.unlink()
    return outputs


def load_path_index(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_diff_markdown(diff: dict[str, Any]) -> str:
    lines = [
        "## Path Diff",
        "",
        f"- Added: `{diff['summary']['added_count']}`",
        f"- Removed: `{diff['summary']['removed_count']}`",
        f"- Changed: `{diff['summary']['changed_count']}`",
        f"- Unchanged: `{diff['summary']['unchanged_count']}`",
        "",
    ]
    for key in ("added", "removed", "changed"):
        if not diff[key]:
            continue
        lines.extend([f"### {key.title()}", ""])
        for path in diff[key]:
            impact = diff.get("impact", {}).get(path, classify_path_impact(path))
            checks = "; ".join(f"`{check}`" for check in impact["recommended_checks"])
            lines.append(f"- `{path}` ({impact['kind']}, {impact['risk']}) checks: {checks}")
        lines.append("")
    return "\n".join(lines)


def build_change_briefs(diff: dict[str, Any]) -> str:
    lines = [
        "# Waterflow Change Briefs",
        "",
        "Use these briefs with Codex or Claude when changed paths need validation or scoped follow-up.",
        "",
    ]
    changed_paths: list[tuple[str, str]] = []
    for change_type in ("added", "removed", "changed"):
        changed_paths.extend((change_type, path) for path in diff.get(change_type, []))
    if not changed_paths:
        lines.append("No changed paths were detected.")
        return "\n".join(lines) + "\n"

    for index, (change_type, path) in enumerate(changed_paths, start=1):
        impact = diff.get("impact", {}).get(path, classify_path_impact(path))
        checks = "\n".join(f"- `{check}`" for check in impact["recommended_checks"])
        lines.extend(
            [
                f"## Brief {index}: {change_type.upper()} {path}",
                "",
                f"Route kind: `{impact['kind']}`",
                f"Risk: `{impact['risk']}`",
                "",
                "Task for Codex or Claude:",
                f"Validate the `{change_type}` path `{path}`. Keep any fix scoped to this route family unless validation proves wider impact.",
                "",
                "Recommended checks:",
                checks,
                "",
                "Completion evidence:",
                "- Record the command output or accepted-risk decision in `registry/VALIDATION.md`.",
                "- Re-run `scripts/waterflow-scan --root /Users/liuchengxu/Desktop/codex-agent-lab --compare-last` if comparing against the previous baseline matters.",
                "",
            ]
        )
    return "\n".join(lines)


def build_validation_plan(report: dict[str, Any], scope: str = "all") -> dict[str, Any]:
    if scope not in {"all", "changed"}:
        raise ValueError(f"Unsupported validation scope: {scope}")
    checks_by_command: dict[str, dict[str, Any]] = {}
    if scope == "all":
        for node in report["graph"]["nodes"]:
            path = node["path"]
            if path == "." or node["kind"] in {"root", "workspace-root", "workspace"}:
                continue
            _add_validation_checks(checks_by_command, path, classify_path_impact(path))

    if "path_diff" in report:
        for path, impact in report["path_diff"].get("impact", {}).items():
            _add_validation_checks(checks_by_command, path, impact)

    checks = [
        {
            "command": entry["command"],
            "risk": entry["risk"],
            "route_kinds": sorted(entry["route_kinds"]),
            "paths": sorted(entry["paths"]),
        }
        for entry in checks_by_command.values()
    ]
    checks.sort(key=lambda item: (_risk_rank(item["risk"]), item["command"]))
    max_risk = checks[0]["risk"] if checks else "P3"
    return {
        "schema_version": 1,
        "generated_at": report["generated_at"],
        "lab_root": report["lab_root"],
        "summary": {
            "check_count": len(checks),
            "max_risk": max_risk,
            "scope": scope,
            "changed_path_count": len(_changed_paths(report)),
        },
        "checks": checks,
    }


def build_validation_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Waterflow Validation Plan",
        "",
        f"- Generated: `{plan['generated_at']}`",
        f"- Lab root: `{plan['lab_root']}`",
        f"- Scope: `{plan['summary'].get('scope', 'all')}`",
        f"- Changed paths: `{plan['summary'].get('changed_path_count', 0)}`",
        f"- Checks: `{plan['summary']['check_count']}`",
        f"- Max risk: `{plan['summary']['max_risk']}`",
        "",
    ]
    if not plan["checks"]:
        lines.append("No validation checks were derived.")
        return "\n".join(lines) + "\n"
    for index, check in enumerate(plan["checks"], start=1):
        lines.extend(
            [
                f"## Check {index}: {check['risk']}",
                "",
                f"Command: `{check['command']}`",
                "",
                "Route kinds:",
                *[f"- `{kind}`" for kind in check["route_kinds"]],
                "",
                "Covered paths:",
                *[f"- `{path}`" for path in check["paths"][:20]],
                "",
            ]
        )
        if len(check["paths"]) > 20:
            lines.extend([f"...and {len(check['paths']) - 20} more paths.", ""])
    return "\n".join(lines)


def run_validation_plan(
    plan: dict[str, Any],
    root: str | Path | None = None,
    timeout_seconds: int = 120,
    max_output_chars: int = 12000,
) -> dict[str, Any]:
    lab_root = Path(root or plan.get("lab_root") or ".").expanduser().resolve()
    checks: list[dict[str, Any]] = []
    started_at = time.monotonic()

    for index, check in enumerate(plan.get("checks", []), start=1):
        command = str(check["command"])
        check_started_at = time.monotonic()
        timed_out = False
        try:
            completed = subprocess.run(
                command,
                cwd=lab_root,
                shell=True,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
            )
            exit_code = completed.returncode
            stdout = completed.stdout or ""
            stderr = completed.stderr or ""
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            exit_code = 124
            stdout = _coerce_process_text(exc.stdout)
            stderr = _coerce_process_text(exc.stderr)
            stderr = (stderr + "\n" if stderr else "") + f"Timed out after {timeout_seconds} seconds."

        duration_seconds = round(time.monotonic() - check_started_at, 3)
        checks.append(
            {
                "index": index,
                "command": command,
                "risk": check.get("risk", "P3"),
                "route_kinds": list(check.get("route_kinds", [])),
                "paths": list(check.get("paths", [])),
                "exit_code": exit_code,
                "passed": exit_code == 0,
                "timed_out": timed_out,
                "duration_seconds": duration_seconds,
                "stdout": _truncate_text(stdout, max_output_chars),
                "stderr": _truncate_text(stderr, max_output_chars),
            }
        )

    failed_count = sum(1 for check in checks if not check["passed"])
    max_exit_code = max((check["exit_code"] for check in checks), default=0)
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "plan_generated_at": plan.get("generated_at", ""),
        "lab_root": str(lab_root),
        "timeout_seconds": timeout_seconds,
        "summary": {
            "check_count": len(checks),
            "passed_count": len(checks) - failed_count,
            "failed_count": failed_count,
            "timed_out_count": sum(1 for check in checks if check["timed_out"]),
            "max_exit_code": max_exit_code,
            "duration_seconds": round(time.monotonic() - started_at, 3),
        },
        "checks": checks,
    }


def build_validation_results_markdown(results: dict[str, Any]) -> str:
    summary = results["summary"]
    lines = [
        "# Waterflow Validation Results",
        "",
        f"- Generated: `{results['generated_at']}`",
        f"- Lab root: `{results['lab_root']}`",
        f"- Checks: `{summary['check_count']}`",
        f"- Passed: `{summary['passed_count']}`",
        f"- Failed: `{summary['failed_count']}`",
        f"- Timed out: `{summary['timed_out_count']}`",
        f"- Max exit code: `{summary['max_exit_code']}`",
        f"- Duration seconds: `{summary['duration_seconds']}`",
        "",
    ]
    if not results["checks"]:
        lines.append("No validation checks were run.")
        return "\n".join(lines) + "\n"

    for check in results["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.extend(
            [
                f"## Check {check['index']}: {status}",
                "",
                f"command: `{check['command']}`",
                f"risk: `{check['risk']}`",
                f"exit_code: `{check['exit_code']}`",
                f"timed_out: `{str(check['timed_out']).lower()}`",
                f"duration_seconds: `{check['duration_seconds']}`",
                "",
                "route_kinds:",
                *[f"- `{kind}`" for kind in check["route_kinds"]],
                "",
                "covered_paths:",
                *[f"- `{path}`" for path in check["paths"][:20]],
                "",
            ]
        )
        if len(check["paths"]) > 20:
            lines.extend([f"...and {len(check['paths']) - 20} more paths.", ""])
        if check["stdout"]:
            lines.extend(["stdout:", "", "```text", check["stdout"].rstrip(), "```", ""])
        if check["stderr"]:
            lines.extend(["stderr:", "", "```text", check["stderr"].rstrip(), "```", ""])
    return "\n".join(lines)


def write_validation_outputs(results: dict[str, Any], output_dir: str | Path) -> dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "waterflow-validation-results.json"
    markdown_path = out / "waterflow-validation-results.md"
    json_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(build_validation_results_markdown(results), encoding="utf-8")
    return {
        "validation_results_json": str(json_path),
        "validation_results_markdown": str(markdown_path),
    }


def validation_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run real commands from a Waterflow validation plan.")
    parser.add_argument(
        "--plan",
        default="outputs/shared/waterflow/waterflow-validation-plan.json",
        help="Path to waterflow-validation-plan.json.",
    )
    parser.add_argument(
        "--root",
        help="Lab root to use as command cwd. Defaults to the plan's lab_root.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/shared/waterflow",
        help="Directory for validation result artifacts.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=120, help="Per-command timeout.")
    parser.add_argument("--json", action="store_true", help="Print validation results JSON to stdout.")
    args = parser.parse_args(argv)

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    lab_root = Path(args.root or plan.get("lab_root") or ".").expanduser().resolve()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = lab_root / output_dir

    results = run_validation_plan(plan, root=lab_root, timeout_seconds=args.timeout_seconds)
    outputs = write_validation_outputs(results, output_dir)
    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        for kind, path in outputs.items():
            print(f"{kind}: {path}")
        print(f"checks: {results['summary']['check_count']}")
        print(f"passed: {results['summary']['passed_count']}")
        print(f"failed: {results['summary']['failed_count']}")
    return 0 if results["summary"]["failed_count"] == 0 else 1


def _impact(kind: str, risk: str, recommended_checks: list[str]) -> dict[str, Any]:
    return {
        "kind": kind,
        "risk": risk,
        "recommended_checks": recommended_checks,
    }


def _path_fingerprint(item: dict[str, Any]) -> tuple[Any, ...]:
    return (item.get("id"), item.get("kind"), item.get("hash"), item.get("size"))


def _risk_rank(risk: str) -> int:
    return {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(risk, 3)


def _max_risk(left: str, right: str) -> str:
    return left if _risk_rank(left) <= _risk_rank(right) else right


def _max_risk_many(risks: list[str]) -> str:
    current = "P3"
    for risk in risks:
        current = _max_risk(current, risk)
    return current


def _changed_paths(report: dict[str, Any]) -> list[str]:
    diff = report.get("path_diff", {})
    return sorted(set(diff.get("added", []) + diff.get("removed", []) + diff.get("changed", [])))


def _add_validation_checks(
    checks_by_command: dict[str, dict[str, Any]],
    path: str,
    impact: dict[str, Any],
) -> None:
    for command in impact["recommended_checks"]:
        entry = checks_by_command.setdefault(
            command,
            {
                "command": command,
                "risk": impact["risk"],
                "route_kinds": set(),
                "paths": set(),
            },
        )
        entry["risk"] = _max_risk(entry["risk"], impact["risk"])
        entry["route_kinds"].add(impact["kind"])
        entry["paths"].add(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan the Codex Agent Lab waterflow graph.")
    parser.add_argument("--root", default=".", help="Lab root to scan.")
    parser.add_argument(
        "--output-dir",
        default="outputs/shared/waterflow",
        help="Directory for JSON, Markdown, and repair brief outputs.",
    )
    parser.add_argument(
        "--previous-index",
        help="Optional previous waterflow-path-index.json to diff against.",
    )
    parser.add_argument(
        "--compare-last",
        action="store_true",
        help="Diff against the existing waterflow-path-index.json in the output directory before overwriting it.",
    )
    parser.add_argument("--json", action="store_true", help="Print the JSON report to stdout.")
    args = parser.parse_args(argv)

    output_dir = Path(args.root) / args.output_dir
    previous_index = None
    if args.previous_index:
        previous_index = load_path_index(args.previous_index)
    elif args.compare_last:
        last_index = output_dir / "waterflow-path-index.json"
        if last_index.exists():
            previous_index = load_path_index(last_index)

    report = scan_lab(args.root)
    outputs = write_outputs(report, output_dir, previous_index=previous_index)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for kind, path in outputs.items():
            print(f"{kind}: {path}")
        print(f"findings: {report['summary']['finding_count']}")
    return 0


def _scan_agents(
    lab_root: Path,
    add_node: Any,
    edges: list[dict[str, Any]],
    findings: list[dict[str, Any]],
) -> None:
    agent_dir = lab_root / ".codex" / "agents"
    names: dict[str, str] = {}
    for path in sorted(agent_dir.glob("*.toml")):
        metadata: dict[str, Any] = {"hash": _file_hash(path), "size": _safe_size(path)}
        try:
            parsed = tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # TOML parse errors vary by Python version.
            findings.append(
                _finding(
                    "P1",
                    "AGENT_TOML_INVALID",
                    f"Agent TOML cannot be parsed: {_rel(path, lab_root)}",
                    [_rel(path, lab_root), str(exc)],
                    "Fix the TOML syntax, then rerun the waterflow scan.",
                )
            )
            parsed = {}
        missing = [field for field in REQUIRED_AGENT_FIELDS if not parsed.get(field)]
        if missing:
            findings.append(
                _finding(
                    "P1",
                    "AGENT_MISSING_FIELD",
                    f"Agent is missing required field(s): {', '.join(missing)}",
                    [_rel(path, lab_root)],
                    f"Add `{', '.join(missing)}` to `{_rel(path, lab_root)}` with narrow, role-specific content.",
                )
            )
        name = str(parsed.get("name") or path.stem)
        if name in names:
            findings.append(
                _finding(
                    "P2",
                    "DUPLICATE_AGENT_NAME",
                    f"Duplicate custom agent name: {name}",
                    [names[name], _rel(path, lab_root)],
                    "Rename one agent so Codex has an unambiguous custom-agent target.",
                )
            )
        names[name] = _rel(path, lab_root)
        node = add_node("agent", path, label=name, **metadata)
        for ref in _extract_lab_refs(path.read_text(encoding="utf-8", errors="ignore"), lab_root):
            edges.append(
                {
                    "source": node.id,
                    "target": f"path:{ref}",
                    "type": "references",
                    "evidence": _rel(path, lab_root),
                }
            )


def _scan_skills(lab_root: Path, add_node: Any, findings: list[dict[str, Any]]) -> None:
    skill_root = lab_root / ".agents" / "skills"
    names: dict[str, str] = {}
    if not skill_root.exists():
        return
    for skill_dir in sorted(path for path in skill_root.iterdir() if path.is_dir()):
        if skill_dir.name in EXCLUDED_SKILL_DIRS:
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            findings.append(
                _finding(
                    "P1",
                    "SKILL_MISSING_ENTRYPOINT",
                    f"Skill directory has no SKILL.md: {_rel(skill_dir, lab_root)}",
                    [_rel(skill_dir, lab_root)],
                    "Add `SKILL.md` with `name` and `description`, or remove the stale skill directory.",
                )
            )
            continue
        frontmatter = _skill_frontmatter(skill_file)
        name = frontmatter.get("name", skill_dir.name)
        missing = [field for field in ("name", "description") if not frontmatter.get(field)]
        if missing:
            findings.append(
                _finding(
                    "P2",
                    "SKILL_MISSING_FIELD",
                    f"Skill is missing required frontmatter field(s): {', '.join(missing)}",
                    [_rel(skill_file, lab_root)],
                    f"Add `{', '.join(missing)}` to the skill frontmatter.",
                )
            )
        if name in names:
            findings.append(
                _finding(
                    "P2",
                    "DUPLICATE_SKILL_NAME",
                    f"Duplicate skill name: {name}",
                    [names[name], _rel(skill_file, lab_root)],
                    "Rename or remove one skill so skill selection is unambiguous.",
                )
            )
        names[name] = _rel(skill_file, lab_root)
        add_node("skill", skill_file, label=name, hash=_file_hash(skill_file), size=_safe_size(skill_file))


def _scan_scripts(lab_root: Path, add_node: Any, findings: list[dict[str, Any]]) -> None:
    scripts_dir = lab_root / "scripts"
    if not scripts_dir.exists():
        return
    validation_text = _read_text(lab_root / "registry" / "VALIDATION.md")
    for path in sorted(item for item in scripts_dir.iterdir() if item.is_file()):
        add_node("script", path, hash=_file_hash(path), size=_safe_size(path))
        mode = path.stat().st_mode
        if not mode & stat.S_IXUSR:
            findings.append(
                _finding(
                    "P2",
                    "SCRIPT_NOT_EXECUTABLE",
                    f"Script is not user-executable: {_rel(path, lab_root)}",
                    [_rel(path, lab_root)],
                    f"Run `chmod +x {_rel(path, lab_root)}` or document why this script is not executable.",
                )
            )
        if validation_text and path.name not in validation_text:
            findings.append(
                _finding(
                    "P3",
                    "SCRIPT_WITHOUT_VALIDATION_REFERENCE",
                    f"Script has no explicit validation reference: {path.name}",
                    [_rel(path, lab_root), "registry/VALIDATION.md"],
                    f"Add the command or validation evidence for `{_rel(path, lab_root)}` to `registry/VALIDATION.md`.",
                )
            )


def _scan_registry(lab_root: Path, add_node: Any, findings: list[dict[str, Any]]) -> None:
    registry_dir = lab_root / "registry"
    if not registry_dir.exists():
        return
    for path in sorted(item for item in registry_dir.iterdir() if item.is_file()):
        add_node("registry", path, hash=_file_hash(path), size=_safe_size(path))
        if path.name.endswith(".md") and not path.read_text(encoding="utf-8", errors="ignore").strip():
            findings.append(
                _finding(
                    "P2",
                    "EMPTY_REGISTRY_FILE",
                    f"Registry file is empty: {_rel(path, lab_root)}",
                    [_rel(path, lab_root)],
                    "Add durable evidence or remove the empty registry artifact.",
                )
            )


def _scan_support_files(lab_root: Path, add_node: Any) -> None:
    for root_name, kind in (("waterflow", "auditor-code"), ("tests", "test"), ("docs", "doc")):
        root = lab_root / root_name
        if not root.exists():
            continue
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            if _is_excluded(path, lab_root):
                continue
            add_node(kind, path, hash=_file_hash(path), size=_safe_size(path))


def _scan_workspaces(lab_root: Path, add_node: Any) -> None:
    workspaces_dir = lab_root / "workspaces"
    if not workspaces_dir.exists():
        return
    add_node("workspace-root", workspaces_dir)
    for path in sorted(item for item in workspaces_dir.iterdir() if item.is_dir()):
        add_node("workspace", path)


def _scan_cross_project_references(lab_root: Path, findings: list[dict[str, Any]]) -> None:
    forbidden = "/Users/liuchengxu/Desktop/lcx-s-openclaw"
    evidence: list[str] = []
    scan_roots = [
        lab_root / "AGENTS.md",
        lab_root / "README.md",
        *sorted((lab_root / ".codex" / "agents").glob("*.toml")),
        *sorted((lab_root / "scripts").glob("*")),
    ]
    for path in scan_roots:
        if path.is_file() and forbidden in _read_text(path):
            evidence.append(_rel(path, lab_root))
    if evidence:
        findings.append(
            _finding(
                "P2",
                "CROSS_PROJECT_REFERENCE",
                "Lab workflow references lcx-s-openclaw even though the first Waterflow Auditor scope excludes it.",
                evidence,
                "Remove the reference or document why this path is allowed for this lab-only scan.",
            )
        )


def _finding(
    severity: str,
    code: str,
    message: str,
    evidence: list[str],
    repair_brief: str,
) -> dict[str, Any]:
    return {
        "severity": severity,
        "code": code,
        "message": message,
        "evidence": evidence,
        "repair_brief": repair_brief,
    }


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _file_hash(path: Path) -> str:
    if not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _read_text(path: Path) -> str:
    if not path.exists() or not path.is_file() or path.suffix not in TEXT_SUFFIXES:
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _coerce_process_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    omitted = len(text) - max_chars
    return text[:max_chars] + f"\n...[truncated {omitted} chars]"


def _skill_frontmatter(path: Path) -> dict[str, str]:
    text = _read_text(path)
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    frontmatter: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip("\"'")
    return frontmatter


def _extract_lab_refs(text: str, lab_root: Path) -> list[str]:
    candidates = set(re.findall(r"`([^`]+)`", text))
    refs: list[str] = []
    for candidate in candidates:
        if candidate.startswith("/"):
            path = Path(candidate)
        else:
            path = lab_root / candidate
        try:
            resolved = path.resolve()
            resolved.relative_to(lab_root)
        except (OSError, ValueError):
            continue
        if resolved.exists():
            refs.append(_rel(resolved, lab_root))
    return sorted(refs)


def _is_excluded(path: Path, lab_root: Path) -> bool:
    rel_parts = path.resolve().relative_to(lab_root).parts
    return any(part in EXCLUDED_DIRS for part in rel_parts)


def _severity_counts(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for finding in findings:
        counts[finding["severity"]] = counts.get(finding["severity"], 0) + 1
    return counts


def _kind_counts(nodes: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for node in nodes:
        counts[node["kind"]] = counts.get(node["kind"], 0) + 1
    return counts


if __name__ == "__main__":
    sys.exit(main())
