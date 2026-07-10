"""Scratch workspace durable-capture checks.

Scratch/assembly workspaces can be useful for integration speed, but they are
not durable source-of-truth repos. This module checks that configured
release-worthy files in a scratch workspace are captured by a registry snapshot
before a release is considered complete.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from fnmatch import fnmatch
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Any


SCHEMA = "scratch-durability/v1"
CONFIG_REL = "registry/scratch-durability/config.json"
CURRENT_REL = "registry/scratch-durability/current.json"
SNAPSHOTS_REL = "registry/scratch-durability/snapshots"
SECRET_PATH_PARTS = {
    ".env",
    ".run",
    "auth.json",
}
SECRET_NAME_SUFFIXES = (
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".token",
    ".secret",
)
BINARY_SUFFIXES = {
    ".db",
    ".ico",
    ".jpeg",
    ".jpg",
    ".png",
    ".sqlite",
    ".webp",
    ".zip",
}
DEFAULT_MAX_COPY_BYTES = 1024 * 1024


@dataclass
class ScratchIssue:
    severity: str
    code: str
    message: str
    evidence: list[str] = field(default_factory=list)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def is_secret_like_path(relative_path: str) -> bool:
    parts = set(Path(relative_path).parts)
    if parts & SECRET_PATH_PARTS:
        return True
    name = Path(relative_path).name
    return name.endswith(SECRET_NAME_SUFFIXES) or name.endswith("_token") or name.endswith("_secret")


def should_exclude(relative_path: str, patterns: list[str]) -> bool:
    return any(fnmatch(relative_path, pattern) for pattern in patterns)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_text_file(path: Path) -> bool:
    if path.suffix.lower() in BINARY_SUFFIXES:
        return False
    try:
        with path.open("rb") as fh:
            chunk = fh.read(4096)
    except OSError:
        return False
    return b"\0" not in chunk


def collect_class_files(scratch_root: Path, artifact_class: dict[str, Any]) -> tuple[list[Path], list[ScratchIssue]]:
    includes = artifact_class.get("includes", [])
    excludes = artifact_class.get("excludes", [])
    class_id = str(artifact_class.get("id", "unknown"))
    issues: list[ScratchIssue] = []
    files_by_rel: dict[str, Path] = {}

    if not isinstance(includes, list) or not includes:
        issues.append(
            ScratchIssue(
                "fail",
                "SCRATCH_CLASS_INCLUDES_MISSING",
                "Durability artifact class has no include globs.",
                [class_id],
            )
        )
        return [], issues

    for pattern in includes:
        if not isinstance(pattern, str) or not pattern:
            issues.append(
                ScratchIssue(
                    "fail",
                    "SCRATCH_CLASS_BAD_INCLUDE",
                    "Durability artifact class include glob must be a non-empty string.",
                    [class_id, repr(pattern)],
                )
            )
            continue
        for candidate in scratch_root.glob(pattern):
            if not candidate.is_file():
                continue
            relative = rel(candidate, scratch_root)
            if should_exclude(relative, excludes):
                continue
            if is_secret_like_path(relative):
                issues.append(
                    ScratchIssue(
                        "fail",
                        "SCRATCH_SECRET_LIKE_CAPTURE",
                        "Configured scratch durability source matches a secret-like path.",
                        [class_id, relative],
                    )
                )
                continue
            files_by_rel[relative] = candidate

    if artifact_class.get("required", True) and not files_by_rel:
        issues.append(
            ScratchIssue(
                "fail",
                "SCRATCH_CLASS_EMPTY",
                "Required scratch durability artifact class matched no files.",
                [class_id],
            )
        )

    return [files_by_rel[key] for key in sorted(files_by_rel)], issues


def collect_workspace_files(scratch_root: Path, workspace_config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[ScratchIssue]]:
    records: list[dict[str, Any]] = []
    issues: list[ScratchIssue] = []
    for artifact_class in workspace_config.get("artifact_classes", []):
        class_id = str(artifact_class.get("id", "unknown"))
        files, class_issues = collect_class_files(scratch_root, artifact_class)
        issues.extend(class_issues)
        copy_policy = str(artifact_class.get("copy_policy", "manifest_only"))
        max_copy_bytes = int(artifact_class.get("max_copy_bytes", DEFAULT_MAX_COPY_BYTES))
        for path in files:
            relative = rel(path, scratch_root)
            stat = path.stat()
            copy_content = (
                copy_policy == "copy_text"
                and stat.st_size <= max_copy_bytes
                and is_text_file(path)
            )
            records.append(
                {
                    "path": relative,
                    "artifact_class": class_id,
                    "sha256": sha256_file(path),
                    "size": stat.st_size,
                    "copy_policy": copy_policy,
                    "content_copied": copy_content,
                }
            )
    return records, issues


def validate_owner_repos(root: Path, workspace_config: dict[str, Any]) -> list[ScratchIssue]:
    issues: list[ScratchIssue] = []
    for artifact_class in workspace_config.get("artifact_classes", []):
        class_id = str(artifact_class.get("id", "unknown"))
        owner_repo = artifact_class.get("owner_repo")
        if not isinstance(owner_repo, str) or not owner_repo:
            issues.append(
                ScratchIssue(
                    "warn",
                    "SCRATCH_OWNER_REPO_UNDECLARED",
                    "Artifact class has no owning repo declared; snapshot is the only durability path.",
                    [class_id],
                )
            )
            continue
        if owner_repo.startswith("pending:"):
            issues.append(
                ScratchIssue(
                    "warn",
                    "SCRATCH_OWNER_REPO_PENDING",
                    "Artifact class reflux target is not a concrete git repo yet.",
                    [class_id, owner_repo],
                )
            )
            continue
        owner_path = (root / owner_repo).resolve()
        if not (owner_path / ".git").exists():
            issues.append(
                ScratchIssue(
                    "fail",
                    "SCRATCH_OWNER_REPO_MISSING",
                    "Artifact class owner repo is missing or is not a git checkout.",
                    [class_id, owner_repo],
                )
            )
    return issues


def load_current_snapshot_map(root: Path, current_path: Path | None = None) -> dict[str, str]:
    path = current_path or root / CURRENT_REL
    if not path.exists():
        return {}
    data = read_json(path)
    if data.get("schema") != SCHEMA:
        return {}
    current = data.get("current_snapshots", {})
    if not isinstance(current, dict):
        return {}
    return {str(key): str(value) for key, value in current.items()}


def snapshot_manifest_path(root: Path, workspace_id: str, snapshot_id: str) -> Path:
    return root / SNAPSHOTS_REL / workspace_id / snapshot_id / "manifest.json"


def build_snapshot_manifest(
    root: Path,
    workspace_config: dict[str, Any],
    snapshot_id: str,
    created_at: str | None = None,
) -> tuple[dict[str, Any], list[ScratchIssue]]:
    workspace_id = str(workspace_config["id"])
    scratch_root = (root / workspace_config["path"]).resolve()
    issues: list[ScratchIssue] = []
    if not scratch_root.exists():
        return {}, [
            ScratchIssue(
                "fail",
                "SCRATCH_WORKSPACE_MISSING",
                "Configured scratch workspace does not exist.",
                [workspace_id, str(scratch_root)],
            )
        ]
    issues.extend(validate_owner_repos(root, workspace_config))
    files, file_issues = collect_workspace_files(scratch_root, workspace_config)
    issues.extend(file_issues)
    if any(issue.severity == "fail" for issue in issues):
        return {}, issues
    return {
        "schema": SCHEMA,
        "snapshot_id": snapshot_id,
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
        "workspace": {
            "id": workspace_id,
            "path": workspace_config["path"],
            "scratch_has_git": (scratch_root / ".git").exists(),
        },
        "artifact_classes": workspace_config.get("artifact_classes", []),
        "files": files,
    }, issues


def copy_snapshot_files(root: Path, workspace_config: dict[str, Any], manifest: dict[str, Any]) -> None:
    scratch_root = (root / workspace_config["path"]).resolve()
    workspace_id = str(workspace_config["id"])
    snapshot_id = str(manifest["snapshot_id"])
    snapshot_root = root / SNAPSHOTS_REL / workspace_id / snapshot_id
    files_root = snapshot_root / "files"
    for record in manifest.get("files", []):
        if not record.get("content_copied"):
            continue
        relative = str(record["path"])
        src = scratch_root / relative
        dest = files_root / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)


def write_snapshot(
    root: Path,
    config: dict[str, Any],
    snapshot_id: str,
    workspace_filter: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    written: list[dict[str, Any]] = []
    current = load_current_snapshot_map(root)
    all_issues: list[ScratchIssue] = []
    for workspace_config in config.get("scratch_workspaces", []):
        workspace_id = str(workspace_config.get("id", ""))
        if workspace_filter and workspace_id != workspace_filter:
            continue
        manifest, issues = build_snapshot_manifest(root, workspace_config, snapshot_id, created_at)
        all_issues.extend(issues)
        if any(issue.severity == "fail" for issue in issues):
            continue
        manifest_path = snapshot_manifest_path(root, workspace_id, snapshot_id)
        write_json(manifest_path, manifest)
        copy_snapshot_files(root, workspace_config, manifest)
        current[workspace_id] = snapshot_id
        copied = sum(1 for item in manifest["files"] if item.get("content_copied"))
        written.append(
            {
                "workspace_id": workspace_id,
                "snapshot_id": snapshot_id,
                "manifest": rel(manifest_path, root),
                "files": len(manifest["files"]),
                "content_copied": copied,
            }
        )
    if written:
        write_json(
            root / CURRENT_REL,
            {
                "schema": SCHEMA,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "current_snapshots": current,
            },
        )
    status = "fail" if any(issue.severity == "fail" for issue in all_issues) else "pass"
    return {
        "schema": SCHEMA,
        "status": status,
        "written": written,
        "issues": [issue.__dict__ for issue in all_issues],
    }


def scratch_durability_report(root: Path, config_path: Path | None = None, current_path: Path | None = None) -> dict[str, Any]:
    config_file = config_path or root / CONFIG_REL
    issues: list[ScratchIssue] = []
    if not config_file.exists():
        return {
            "schema": SCHEMA,
            "status": "fail",
            "summary": {"workspace_count": 0, "file_count": 0, "fail_count": 1, "warn_count": 0},
            "workspaces": [],
            "issues": [
                {
                    "severity": "fail",
                    "code": "SCRATCH_CONFIG_MISSING",
                    "message": "Scratch durability config is missing.",
                    "evidence": [rel(config_file, root)],
                }
            ],
        }
    config = read_json(config_file)
    if config.get("schema") != SCHEMA:
        return {
            "schema": SCHEMA,
            "status": "fail",
            "summary": {"workspace_count": 0, "file_count": 0, "fail_count": 1, "warn_count": 0},
            "workspaces": [],
            "issues": [
                {
                    "severity": "fail",
                    "code": "SCRATCH_CONFIG_SCHEMA",
                    "message": "Scratch durability config has an unsupported schema.",
                    "evidence": [rel(config_file, root), str(config.get("schema"))],
                }
            ],
        }

    current = load_current_snapshot_map(root, current_path)
    workspace_reports: list[dict[str, Any]] = []
    file_count = 0

    for workspace_config in config.get("scratch_workspaces", []):
        workspace_id = str(workspace_config.get("id", ""))
        scratch_root = (root / workspace_config.get("path", "")).resolve()
        workspace_issues: list[ScratchIssue] = []
        workspace_issues.extend(validate_owner_repos(root, workspace_config))
        if not workspace_id:
            workspace_issues.append(ScratchIssue("fail", "SCRATCH_WORKSPACE_ID_MISSING", "Scratch workspace has no id."))
        if not scratch_root.exists():
            workspace_issues.append(
                ScratchIssue(
                    "fail",
                    "SCRATCH_WORKSPACE_MISSING",
                    "Configured scratch workspace does not exist.",
                    [workspace_id, str(scratch_root)],
                )
            )
            workspace_reports.append({"id": workspace_id, "status": "fail", "files": 0, "issues": [i.__dict__ for i in workspace_issues]})
            issues.extend(workspace_issues)
            continue

        records, collect_issues = collect_workspace_files(scratch_root, workspace_config)
        workspace_issues.extend(collect_issues)
        file_count += len(records)
        current_snapshot = current.get(workspace_id)
        manifest_records: dict[str, dict[str, Any]] = {}
        if not current_snapshot:
            workspace_issues.append(
                ScratchIssue(
                    "fail",
                    "SCRATCH_CURRENT_SNAPSHOT_MISSING",
                    "No current durability snapshot is recorded for this scratch workspace.",
                    [workspace_id],
                )
            )
        else:
            manifest_path = snapshot_manifest_path(root, workspace_id, current_snapshot)
            if not manifest_path.exists():
                workspace_issues.append(
                    ScratchIssue(
                        "fail",
                        "SCRATCH_SNAPSHOT_MANIFEST_MISSING",
                        "Current durability snapshot manifest is missing.",
                        [workspace_id, current_snapshot, rel(manifest_path, root)],
                    )
                )
            else:
                manifest = read_json(manifest_path)
                for record in manifest.get("files", []):
                    if isinstance(record, dict) and isinstance(record.get("path"), str):
                        manifest_records[str(record["path"])] = record

        for record in records:
            manifest_record = manifest_records.get(record["path"])
            if not manifest_record:
                workspace_issues.append(
                    ScratchIssue(
                        "fail",
                        "SCRATCH_FILE_UNCAPTURED",
                        "Scratch source file is not captured in the current durability snapshot.",
                        [workspace_id, record["artifact_class"], record["path"]],
                    )
                )
                continue
            if manifest_record.get("sha256") != record["sha256"]:
                workspace_issues.append(
                    ScratchIssue(
                        "fail",
                        "SCRATCH_FILE_STALE_CAPTURE",
                        "Scratch source file changed after the current durability snapshot.",
                        [workspace_id, record["artifact_class"], record["path"]],
                    )
                )

        current_paths = {record["path"] for record in records}
        for old_path in sorted(set(manifest_records) - current_paths):
            workspace_issues.append(
                ScratchIssue(
                    "warn",
                    "SCRATCH_SNAPSHOT_ORPHAN",
                    "Current durability snapshot records a file that is no longer matched by config.",
                    [workspace_id, old_path],
                )
            )

        workspace_status = "fail" if any(i.severity == "fail" for i in workspace_issues) else "warn" if any(i.severity == "warn" for i in workspace_issues) else "pass"
        workspace_reports.append(
            {
                "id": workspace_id,
                "path": workspace_config.get("path", ""),
                "status": workspace_status,
                "current_snapshot": current_snapshot,
                "files": len(records),
                "issues": [issue.__dict__ for issue in workspace_issues],
            }
        )
        issues.extend(workspace_issues)

    fail_count = sum(1 for issue in issues if issue.severity == "fail")
    warn_count = sum(1 for issue in issues if issue.severity == "warn")
    return {
        "schema": SCHEMA,
        "status": "fail" if fail_count else "warn" if warn_count else "pass",
        "summary": {
            "workspace_count": len(workspace_reports),
            "file_count": file_count,
            "fail_count": fail_count,
            "warn_count": warn_count,
        },
        "workspaces": workspace_reports,
        "issues": [issue.__dict__ for issue in issues],
    }


def load_config(root: Path, config_path: Path | None = None) -> dict[str, Any]:
    return read_json(config_path or root / CONFIG_REL)
