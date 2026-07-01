"""Lightweight git-worktree isolation plus ordered merge queue for the lab.

The kernel is intentionally small and headless: each work stream gets a git
worktree under a gitignored project-local root, while merge-back is serialized
through a registry-backed queue. A pre-merge conflict check runs before the real
merge and refuses the queue item on any conflict or checker failure.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
import subprocess
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
STATE_REL = "registry/worktree-merge-queue/state.json"
DEFAULT_WORKTREE_ROOT = ".worktrees/merge-queue"
VALID_STREAM_STATUSES = {"active", "merged", "refused"}
VALID_QUEUE_STATUSES = {"queued", "merged", "refused"}
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")


class MergeQueueError(RuntimeError):
    """Raised when worktree or merge-queue operations fail closed."""


@dataclass(frozen=True)
class GitResult:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str


# ---------------------------------------------------------------------------
# State helpers


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def state_path(root: Path) -> Path:
    return Path(root).expanduser().resolve() / STATE_REL


def default_state(worktree_root: str = DEFAULT_WORKTREE_ROOT) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "worktree_root": worktree_root,
        "streams": [],
        "queue": [],
        "events": [],
    }


def read_state(root: Path) -> dict[str, Any]:
    path = state_path(root)
    if not path.exists():
        return default_state()
    return json.loads(path.read_text(encoding="utf-8"))


def write_state(root: Path, state: dict[str, Any]) -> Path:
    path = state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def init_state(root: Path, worktree_root: str = DEFAULT_WORKTREE_ROOT) -> dict[str, Any]:
    state = default_state(worktree_root)
    write_state(root, state)
    return state


# ---------------------------------------------------------------------------
# Git helpers


def _run_git(root: Path, args: list[str], check: bool = False) -> GitResult:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(root),
        text=True,
        capture_output=True,
    )
    result = GitResult(args=args, returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
    if check and result.returncode != 0:
        raise MergeQueueError(_format_git_failure(result))
    return result


def _format_git_failure(result: GitResult) -> str:
    detail = (result.stderr or result.stdout).strip()
    return f"git {' '.join(result.args)} failed with exit {result.returncode}: {detail}"


def _git_output(root: Path, args: list[str]) -> str:
    result = _run_git(root, args, check=True)
    return result.stdout.strip()


def _branch_head(root: Path, branch: str) -> str:
    return _git_output(root, ["rev-parse", "--verify", branch])


def _is_gitignored(root: Path, relative_path: str) -> bool:
    # Directory ignore patterns such as ".worktrees/" only match a child path
    # when the directory does not exist yet. Probe a directory sentinel as well
    # as the literal path so the validator stays fast without requiring mkdir.
    candidates = [relative_path.rstrip("/"), relative_path.rstrip("/") + "/", relative_path.rstrip("/") + "/.probe"]
    return any(_run_git(root, ["check-ignore", "-q", candidate]).returncode == 0 for candidate in candidates)


def ensure_worktree_root_ignored(root: Path, worktree_root: str) -> None:
    if not _is_relative_path(worktree_root):
        raise MergeQueueError("worktree_root must be a relative path inside the repository")
    if not _is_gitignored(root, worktree_root):
        raise MergeQueueError(
            f"worktree root {worktree_root!r} is not gitignored; add .worktrees/ to .gitignore before creating worktrees"
        )


# ---------------------------------------------------------------------------
# Validation


def validate_merge_queue_state(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["state must be a JSON object"]
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")

    worktree_root = data.get("worktree_root")
    if not isinstance(worktree_root, str) or not worktree_root:
        errors.append("worktree_root must be a non-empty string")
        worktree_root = ""
    elif not _is_relative_path(worktree_root):
        errors.append("worktree_root must be a relative path")

    streams = data.get("streams")
    queue = data.get("queue")
    events = data.get("events")
    if not isinstance(streams, list):
        errors.append("streams must be a list")
        streams = []
    if not isinstance(queue, list):
        errors.append("queue must be a list")
        queue = []
    if not isinstance(events, list):
        errors.append("events must be a list")
        events = []

    stream_ids: set[str] = set()
    for index, stream in enumerate(streams):
        if not isinstance(stream, dict):
            errors.append(f"streams[{index}] must be an object")
            continue
        stream_id = stream.get("id")
        if not isinstance(stream_id, str) or not stream_id:
            errors.append(f"streams[{index}].id must be a non-empty string")
            stream_id = f"streams[{index}]"
        elif stream_id in stream_ids:
            errors.append(f"{stream_id}: duplicate stream id")
        else:
            stream_ids.add(stream_id)
        if not isinstance(stream.get("branch"), str) or not stream.get("branch"):
            errors.append(f"{stream_id}: branch must be a non-empty string")
        if stream.get("status") not in VALID_STREAM_STATUSES:
            errors.append(f"{stream_id}: status must be one of {sorted(VALID_STREAM_STATUSES)}")
        path = stream.get("path")
        if not isinstance(path, str) or not path:
            errors.append(f"{stream_id}: path must be a non-empty string")
        elif worktree_root and not _path_stays_under(path, worktree_root):
            errors.append(f"{stream_id}: path stays under worktree_root is required")
        for field in ("created_at", "updated_at"):
            _validate_iso(stream.get(field), f"{stream_id}: {field}", errors)

    queued_streams: set[str] = set()
    for index, item in enumerate(queue):
        if not isinstance(item, dict):
            errors.append(f"queue[{index}] must be an object")
            continue
        stream_id = item.get("stream_id")
        if not isinstance(stream_id, str) or not stream_id:
            errors.append(f"queue[{index}].stream_id must be a non-empty string")
            stream_id = f"queue[{index}]"
        elif stream_id not in stream_ids:
            errors.append(f"queue[{index}]: unknown stream {stream_id}")
        status = item.get("status")
        if status not in VALID_QUEUE_STATUSES:
            errors.append(f"queue[{index}]: status must be one of {sorted(VALID_QUEUE_STATUSES)}")
        elif status == "queued":
            if stream_id in queued_streams:
                errors.append(f"queue[{index}]: duplicate queued stream {stream_id}")
            queued_streams.add(str(stream_id))
        _validate_iso(item.get("enqueued_at"), f"queue[{index}]: enqueued_at", errors)
        if status == "refused" and not isinstance(item.get("refusal"), dict):
            errors.append(f"queue[{index}]: refused item must include refusal object")
        if status == "merged" and not item.get("merge_commit"):
            errors.append(f"queue[{index}]: merged item must include merge_commit")

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            errors.append(f"events[{index}] must be an object")
            continue
        if not isinstance(event.get("type"), str) or not event.get("type"):
            errors.append(f"events[{index}].type must be a non-empty string")
        _validate_iso(event.get("at"), f"events[{index}]: at", errors)
    return errors


def merge_queue_report(root: Path) -> dict[str, Any]:
    root = Path(root).expanduser().resolve()
    path = state_path(root)
    issues: list[dict[str, str]] = []
    try:
        if not path.exists():
            state = default_state()
            issues.append({"code": "MERGE_QUEUE_STATE_MISSING", "message": f"{path} is missing"})
        else:
            state = read_state(root)
    except (OSError, json.JSONDecodeError) as exc:
        state = default_state()
        issues.append({"code": "MERGE_QUEUE_UNREADABLE", "message": f"{path}: {exc}"})

    for error in validate_merge_queue_state(state):
        issues.append({"code": "INVALID_MERGE_QUEUE_STATE", "message": error})

    worktree_root = state.get("worktree_root") if isinstance(state, dict) else None
    if isinstance(worktree_root, str) and worktree_root and not _is_gitignored(root, worktree_root):
        issues.append({"code": "WORKTREE_ROOT_NOT_IGNORED", "message": f"{worktree_root} is not gitignored"})

    streams = state.get("streams", []) if isinstance(state, dict) else []
    queue = state.get("queue", []) if isinstance(state, dict) else []
    summary = {
        "stream_count": len(streams) if isinstance(streams, list) else 0,
        "active_count": sum(1 for item in streams if isinstance(item, dict) and item.get("status") == "active"),
        "queued_count": sum(1 for item in queue if isinstance(item, dict) and item.get("status") == "queued"),
        "merged_count": sum(1 for item in queue if isinstance(item, dict) and item.get("status") == "merged"),
        "refused_count": sum(1 for item in queue if isinstance(item, dict) and item.get("status") == "refused"),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "fail" if issues else "pass",
        "state_path": str(path),
        "summary": summary,
        "issues": issues,
    }


# ---------------------------------------------------------------------------
# Operations


def create_stream_worktree(root: Path, stream_id: str, branch: str | None = None) -> dict[str, Any]:
    """Create an isolated worktree for one stream and record it in state."""
    root = Path(root).expanduser().resolve()
    _validate_stream_id(stream_id)
    state = read_state(root)
    errors = validate_merge_queue_state(state)
    if errors:
        raise MergeQueueError("invalid merge queue state: " + "; ".join(errors))
    worktree_root = str(state.get("worktree_root") or DEFAULT_WORKTREE_ROOT)
    ensure_worktree_root_ignored(root, worktree_root)

    if _stream_by_id(state, stream_id):
        raise MergeQueueError(f"stream already exists: {stream_id}")

    branch = branch or f"merge-queue/{stream_id}"
    _validate_branch(branch)
    relative_path = f"{worktree_root.rstrip('/')}/{stream_id}"
    path = root / relative_path
    _assert_resolves_inside(root / worktree_root, path)
    if path.exists():
        raise MergeQueueError(f"worktree path already exists: {relative_path}")

    result = _run_git(root, ["worktree", "add", "-b", branch, str(path)])
    if result.returncode != 0:
        raise MergeQueueError(_format_git_failure(result))
    now = _now_iso()
    head = _branch_head(root, branch)
    stream = {
        "id": stream_id,
        "branch": branch,
        "path": relative_path,
        "base": head,
        "head": head,
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }
    state["streams"].append(stream)
    _event(state, "worktree_created", stream_id, {"branch": branch, "path": relative_path})
    write_state(root, state)
    return dict(stream)


def enqueue_stream(root: Path, stream_id: str) -> dict[str, Any]:
    """Append an active stream to the ordered merge queue."""
    root = Path(root).expanduser().resolve()
    state = read_state(root)
    errors = validate_merge_queue_state(state)
    if errors:
        raise MergeQueueError("invalid merge queue state: " + "; ".join(errors))
    stream = _stream_by_id(state, stream_id)
    if not stream:
        raise MergeQueueError(f"unknown stream: {stream_id}")
    if stream.get("status") != "active":
        raise MergeQueueError(f"stream is not active: {stream_id}")
    if any(item.get("stream_id") == stream_id and item.get("status") == "queued" for item in state["queue"]):
        raise MergeQueueError(f"stream already queued: {stream_id}")

    stream["head"] = _branch_head(root, str(stream["branch"]))
    stream["updated_at"] = _now_iso()
    item = {
        "stream_id": stream_id,
        "branch": stream["branch"],
        "enqueued_at": _now_iso(),
        "status": "queued",
    }
    state["queue"].append(item)
    _event(state, "stream_queued", stream_id, {"branch": stream["branch"]})
    write_state(root, state)
    return state


def merge_next(root: Path) -> dict[str, Any] | None:
    """Merge the next queued stream into the current branch, or refuse it.

    The pre-merge conflict checker uses ``git merge-tree --write-tree`` and any
    non-zero result is treated as a closed gate: state is marked refused and no
    merge is attempted.
    """
    root = Path(root).expanduser().resolve()
    state = read_state(root)
    errors = validate_merge_queue_state(state)
    if errors:
        raise MergeQueueError("invalid merge queue state: " + "; ".join(errors))
    item = next((entry for entry in state["queue"] if entry.get("status") == "queued"), None)
    if item is None:
        return None
    stream = _stream_by_id(state, str(item["stream_id"]))
    if not stream:
        _refuse(state, item, None, "unknown_stream", "queued stream is missing from streams registry")
        write_state(root, state)
        raise MergeQueueError("queued stream is missing from streams registry")

    branch = str(stream["branch"])
    stream["head"] = _branch_head(root, branch)
    precheck = _run_git(root, ["merge-tree", "--write-tree", "HEAD", branch])
    if precheck.returncode != 0:
        message = _trim((precheck.stdout + "\n" + precheck.stderr).strip())
        _refuse(state, item, stream, "pre_merge_conflict", message or "pre-merge conflict detected")
        write_state(root, state)
        raise MergeQueueError(f"pre-merge conflict refused for {stream['id']}: {message}")

    result = _run_git(root, ["merge", "--no-ff", "--no-edit", branch])
    if result.returncode != 0:
        _run_git(root, ["merge", "--abort"])
        message = _trim((result.stdout + "\n" + result.stderr).strip())
        _refuse(state, item, stream, "merge_failed", message or "git merge failed after precheck")
        write_state(root, state)
        raise MergeQueueError(f"merge failed closed for {stream['id']}: {message}")

    merge_commit = _git_output(root, ["rev-parse", "HEAD"])
    now = _now_iso()
    item["status"] = "merged"
    item["merged_at"] = now
    item["merge_commit"] = merge_commit
    stream["status"] = "merged"
    stream["updated_at"] = now
    _event(state, "stream_merged", str(stream["id"]), {"merge_commit": merge_commit})
    write_state(root, state)
    return dict(item)


# ---------------------------------------------------------------------------
# Internal helpers


def _validate_stream_id(stream_id: str) -> None:
    if not isinstance(stream_id, str) or not _ID_RE.fullmatch(stream_id):
        raise MergeQueueError("stream id must start with an alphanumeric character and contain only alnum, dot, underscore, or dash")


def _validate_branch(branch: str) -> None:
    if not isinstance(branch, str) or not branch or branch.startswith("-") or ".." in branch:
        raise MergeQueueError("branch must be a non-empty safe git ref name")
    result = subprocess.run(["git", "check-ref-format", "--branch", branch], text=True, capture_output=True)
    if result.returncode != 0:
        raise MergeQueueError(f"invalid branch name: {branch}")


def _stream_by_id(state: dict[str, Any], stream_id: str) -> dict[str, Any] | None:
    for stream in state.get("streams", []):
        if isinstance(stream, dict) and stream.get("id") == stream_id:
            return stream
    return None


def _event(state: dict[str, Any], event_type: str, stream_id: str, details: dict[str, Any] | None = None) -> None:
    state.setdefault("events", []).append(
        {"at": _now_iso(), "type": event_type, "stream_id": stream_id, "details": details or {}}
    )


def _refuse(
    state: dict[str, Any],
    item: dict[str, Any],
    stream: dict[str, Any] | None,
    reason: str,
    message: str,
) -> None:
    now = _now_iso()
    item["status"] = "refused"
    item["refused_at"] = now
    item["refusal"] = {"reason": reason, "message": _trim(message)}
    if stream is not None:
        stream["status"] = "refused"
        stream["updated_at"] = now
        stream_id = str(stream.get("id"))
    else:
        stream_id = str(item.get("stream_id"))
    _event(state, "stream_refused", stream_id, {"reason": reason})


def _trim(text: str, cap: int = 1200) -> str:
    text = text.strip()
    if len(text) <= cap:
        return text
    return text[:cap] + "\n[...truncated...]"


def _validate_iso(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be a non-empty ISO timestamp string")
        return
    try:
        datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        errors.append(f"{label} must be a valid ISO timestamp")


def _is_relative_path(path: str) -> bool:
    p = Path(path)
    return not p.is_absolute() and ".." not in p.parts


def _path_stays_under(path: str, parent: str) -> bool:
    if not _is_relative_path(path):
        return False
    parent_parts = Path(parent).parts
    path_parts = Path(path).parts
    return len(path_parts) >= len(parent_parts) and path_parts[: len(parent_parts)] == parent_parts


def _assert_resolves_inside(parent: Path, child: Path) -> None:
    parent_resolved = parent.resolve(strict=False)
    child_resolved = child.resolve(strict=False)
    try:
        child_resolved.relative_to(parent_resolved)
    except ValueError as exc:
        raise MergeQueueError(f"worktree path must stay under {parent}") from exc
