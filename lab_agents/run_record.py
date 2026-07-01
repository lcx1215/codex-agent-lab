"""Structured per-run records for the agent development environment.

This is the headless "Run Recorder" seam described in
``registry/ORCHESTRATION_LAYER_STATE.md``: capture each meaningful agent run as
one JSON record (prompt -> commands -> stdout/err -> file diffs -> result ->
git SHAs) so it can later be queried, diffed, or rendered by a UI. See
``docs/run-record-schema.md`` for the field contract.

Root-layer orchestration surface. No desktop UI. Owner lane: claude (v1).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import re
import subprocess
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
RUNS_DIR_REL = "registry/runs"
OUTPUT_BYTE_CAP = 4000
_GIT_OBJECT_RE = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
_SECRET_VALUE_RE = re.compile(
    r"(sk-[a-z0-9_-]{8,}|sk_(?:live|test)_[a-z0-9_-]+|pk_(?:live|test)_[a-z0-9_-]+|server_secret_[a-z0-9_-]+)",
    re.IGNORECASE,
)

# Markers whose presence means a step is carrying material it must not. The
# writer scrubs these lines rather than trusting callers. Mirrors the lab's
# secret-boundary rule (see AGENTS.md / CLAUDE.md).
_SECRET_MARKERS = (
    "auth.json",
    "api_key",
    "api-key",
    "apikey",
    "authorization:",
    "bearer ",
    "secret",
    "password",
    "token=",
    "-----begin",
    "cookie:",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _scrub(text: str) -> str:
    """Redact any line that looks like it carries secret material."""
    out = []
    for line in text.splitlines():
        low = line.lower()
        if any(marker in low for marker in _SECRET_MARKERS) or _SECRET_VALUE_RE.search(line):
            out.append("[redacted: possible secret]")
        else:
            out.append(line)
    return "\n".join(out)


def _cap(text: str, cap: int = OUTPUT_BYTE_CAP) -> str:
    encoded = text.encode("utf-8", errors="replace")
    if len(encoded) <= cap:
        return text
    return encoded[:cap].decode("utf-8", errors="ignore") + "\n[...truncated...]"


def _git_head(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug[:32] or "run").rstrip("-")


@dataclass
class RunRecord:
    """Incremental builder for one structured run record."""

    lane: str
    agent: str
    task: str
    repo_root: Path
    run_id: str = ""
    started_at: str = field(default_factory=_now_iso)
    ended_at: str | None = None
    head_before: str | None = None
    head_after: str | None = None
    steps: list[dict[str, Any]] = field(default_factory=list)
    files_changed: list[dict[str, Any]] = field(default_factory=list)
    outcome: str | None = None
    summary: str = ""

    def __post_init__(self) -> None:
        self.repo_root = Path(self.repo_root).expanduser().resolve()
        if not self.run_id:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            self.run_id = f"{stamp}-{_slugify(self.lane)}-{_slugify(self.task)}"
        if self.head_before is None:
            self.head_before = _git_head(self.repo_root)

    def _next_index(self) -> int:
        return len(self.steps)

    def add_prompt(self, text: str) -> "RunRecord":
        self.steps.append({"index": self._next_index(), "kind": "prompt", "text": _scrub(text)})
        return self

    def add_note(self, text: str) -> "RunRecord":
        self.steps.append({"index": self._next_index(), "kind": "note", "text": _scrub(text)})
        return self

    def add_result(self, text: str) -> "RunRecord":
        self.steps.append({"index": self._next_index(), "kind": "result", "text": _scrub(text)})
        return self

    def add_command(self, command: list[str] | str, exit_code: int, stdout: str = "", stderr: str = "") -> "RunRecord":
        cmd = command if isinstance(command, str) else " ".join(command)
        self.steps.append(
            {
                "index": self._next_index(),
                "kind": "command",
                "command": cmd,
                "exit_code": exit_code,
                "stdout": _cap(_scrub(stdout)),
                "stderr": _cap(_scrub(stderr)),
            }
        )
        return self

    def capture_command(self, command: list[str], timeout: int = 300, env: dict[str, str] | None = None) -> int:
        """Run a subprocess, append a command step, and return the exit code."""
        try:
            completed = subprocess.run(
                command,
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )
            self.add_command(command, completed.returncode, completed.stdout, completed.stderr)
            return completed.returncode
        except subprocess.TimeoutExpired:
            self.add_command(command, 124, "", f"timed out after {timeout}s")
            return 124
        except OSError as exc:
            self.add_command(command, 127, "", str(exc))
            return 127

    def record_file_change(self, path: str, change_type: str, before_sha: str | None = None, after_sha: str | None = None) -> "RunRecord":
        if change_type not in {"added", "modified", "deleted"}:
            raise ValueError(f"invalid change_type: {change_type}")
        _validate_blob_sha(before_sha, "before_sha")
        _validate_blob_sha(after_sha, "after_sha")
        self.files_changed.append(
            {"path": path, "change_type": change_type, "before_sha": before_sha, "after_sha": after_sha}
        )
        return self

    def finalize(self, outcome: str, summary: str) -> "RunRecord":
        if outcome not in {"success", "failure", "aborted"}:
            raise ValueError(f"invalid outcome: {outcome}")
        self.outcome = outcome
        self.summary = summary
        self.ended_at = _now_iso()
        self.head_after = _git_head(self.repo_root)
        return self

    def to_dict(self) -> dict[str, Any]:
        if self.outcome is None:
            raise ValueError("record must be finalized before serialization")
        return {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.run_id,
            "lane": self.lane,
            "agent": self.agent,
            "task": self.task,
            "repo_root": str(self.repo_root),
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "git": {"head_before": self.head_before, "head_after": self.head_after},
            "steps": self.steps,
            "files_changed": self.files_changed,
            "outcome": self.outcome,
            "summary": self.summary,
        }


def write_run_record(record: RunRecord, runs_root: Path | None = None) -> Path:
    """Write a finalized record to registry/runs/<run_id>/record.json + latest.json."""
    root = Path(runs_root) if runs_root else record.repo_root / RUNS_DIR_REL
    run_dir = root / record.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record.to_dict(), ensure_ascii=False, indent=2) + "\n"
    record_path = run_dir / "record.json"
    record_path.write_text(payload, encoding="utf-8")
    (root / "latest.json").write_text(payload, encoding="utf-8")
    return record_path


def _validate_blob_sha(value: str | None, field_name: str) -> None:
    if value is None:
        return
    if not _GIT_OBJECT_RE.fullmatch(value):
        raise ValueError(f"{field_name} must be a git object SHA or null")


_VALID_OUTCOMES = {"success", "failure", "aborted"}
_VALID_CHANGE_TYPES = {"added", "modified", "deleted"}
_VALID_STEP_KINDS = {"prompt", "command", "note", "result"}
_REQUIRED_TOP_FIELDS = (
    "schema_version", "run_id", "lane", "agent", "task", "repo_root",
    "started_at", "ended_at", "git", "steps", "files_changed", "outcome", "summary",
)


def validate_record(data: Any) -> list[str]:
    """Validate a parsed run record against schema v1. Returns a list of error
    strings; empty means valid. Used by scripts/check-run-records."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["record is not a JSON object"]

    for field_name in _REQUIRED_TOP_FIELDS:
        if field_name not in data:
            errors.append(f"missing required field: {field_name}")

    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if data.get("outcome") not in _VALID_OUTCOMES:
        errors.append(f"outcome must be one of {sorted(_VALID_OUTCOMES)}")
    for str_field in ("run_id", "lane", "agent", "task", "repo_root", "started_at", "ended_at", "summary"):
        if str_field in data and not isinstance(data[str_field], str):
            errors.append(f"{str_field} must be a string")

    git = data.get("git")
    if not isinstance(git, dict) or "head_before" not in git or "head_after" not in git:
        errors.append("git must be an object with head_before and head_after")
    else:
        for sha_field in ("head_before", "head_after"):
            val = git[sha_field]
            if val is not None and not _GIT_OBJECT_RE.fullmatch(str(val)):
                errors.append(f"git.{sha_field} must be a git object SHA or null")

    steps = data.get("steps")
    if not isinstance(steps, list):
        errors.append("steps must be a list")
    else:
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                errors.append(f"steps[{i}] is not an object")
                continue
            if step.get("index") != i:
                errors.append(f"steps[{i}].index must equal {i}")
            if step.get("kind") not in _VALID_STEP_KINDS:
                errors.append(f"steps[{i}].kind invalid")
            elif step["kind"] == "command":
                for cf in ("command", "exit_code", "stdout", "stderr"):
                    if cf not in step:
                        errors.append(f"steps[{i}] command missing {cf}")

    files = data.get("files_changed")
    if not isinstance(files, list):
        errors.append("files_changed must be a list")
    else:
        for i, fc in enumerate(files):
            if not isinstance(fc, dict):
                errors.append(f"files_changed[{i}] is not an object")
                continue
            if fc.get("change_type") not in _VALID_CHANGE_TYPES:
                errors.append(f"files_changed[{i}].change_type invalid")
            for sha_field in ("before_sha", "after_sha"):
                val = fc.get(sha_field)
                if val is not None and not _GIT_OBJECT_RE.fullmatch(str(val)):
                    errors.append(f"files_changed[{i}].{sha_field} must be a git object SHA or null")
    return errors


