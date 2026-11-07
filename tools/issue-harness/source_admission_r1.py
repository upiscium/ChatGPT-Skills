"""Operator-only Source Admission R1 for an offline GitHub Issue capture.

No network requests, LLM/tool registration, GitHub writes, authorization claims,
or activation of the installed Claude plugin. A matching operator-supplied
GitHub capture is NOT independent provider authentication or Human approval.
The record is a private, fail-closed staging receipt, not a trusted signature.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Any

from source_admission import (
    AdmissionBlocked, MAX_RAW_BYTES, _json_unique,
    _read_regular_no_symlink, _require_operator_directory, preflight,
)
from arca_issue_harness.core import MAX_SNAPSHOT_BYTES, SHA_RE, SNAPSHOT_RE

CAPTURE_VERSION = "arca.issue-harness.github-issue-capture.v1"
REGISTRY_VERSION = "arca.issue-harness.source-registry.v1"
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}$")
NODE_RE = re.compile(r"^I_[A-Za-z0-9_-]{4,128}$")
MAX_CAPTURE_BYTES = MAX_RAW_BYTES + 16_384
EXPECTED_FILES = frozenset({"capture.json", "raw.txt", "snapshot.json", "receipt.json"})
RECEIPT_KEYS = frozenset({
    "schema_version", "status", "source_id", "github_repository",
    "github_issue_number", "github_node_id", "github_updated_at",
    "github_html_url", "capture_sha256", "raw_sha256", "snapshot_sha256",
    "origin_authenticated", "semantic_approval_verified", "operator_review",
    "activation", "effect_authority",
})
CAPTURE_KEYS = frozenset({
    "schema_version", "provider", "repository", "issue_number", "node_id",
    "updated_at", "html_url", "api_url", "title", "body",
})
STAGE_STATUS = "STAGED_INACTIVE_OPERATOR_REVIEW_REQUIRED"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _ensure_hash(value: str, label: str) -> None:
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        raise AdmissionBlocked("INVALID_" + label + "_SHA")


def _read_capture(path: Path, expected_digest: str) -> tuple[dict[str, Any], bytes]:
    _ensure_hash(expected_digest, "CAPTURE")
    raw = _read_regular_no_symlink(path, MAX_CAPTURE_BYTES)
    if sha(raw) != expected_digest:
        raise AdmissionBlocked("CAPTURE_DRIFT")
    capture = _json_unique(raw)
    if set(capture) != CAPTURE_KEYS:
        raise AdmissionBlocked("CAPTURE_SCHEMA")
    if capture.get("schema_version") != CAPTURE_VERSION or capture.get("provider") != "github":
        raise AdmissionBlocked("CAPTURE_SCHEMA")
    repo = capture.get("repository")
    num = capture.get("issue_number")
    node = capture.get("node_id")
    updated = capture.get("updated_at")
    if not isinstance(repo, str) or not REPOSITORY_RE.fullmatch(repo):
        raise AdmissionBlocked("INVALID_PROVIDER_IDENTITY")
    if type(num) is not int or not (1 <= num <= 2**31 - 1):
        raise AdmissionBlocked("INVALID_PROVIDER_IDENTITY")
    if not isinstance(node, str) or not NODE_RE.fullmatch(node):
        raise AdmissionBlocked("INVALID_PROVIDER_IDENTITY")
    if not isinstance(updated, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", updated
    ):
        raise AdmissionBlocked("INVALID_PROVIDER_REVISION")
    try:
        moment = datetime.fromisoformat(updated.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AdmissionBlocked("INVALID_PROVIDER_REVISION") from exc
    if moment.tzinfo != timezone.utc:
        raise AdmissionBlocked("INVALID_PROVIDER_REVISION")
    if capture.get("html_url") != f"https://github.com/{repo}/issues/{num}":
        raise AdmissionBlocked("INVALID_PROVIDER_URL")
    if capture.get("api_url") != f"https://api.github.com/repos/{repo}/issues/{num}":
        raise AdmissionBlocked("INVALID_PROVIDER_URL")
    title = capture.get("title")
    body = capture.get("body")
    if not isinstance(title, str) or not (1 <= len(title) <= 1024) or any(
        ord(x) < 32 for x in title
    ):
        raise AdmissionBlocked("INVALID_CAPTURE_TEXT")
    if not isinstance(body, str) or not body:
        raise AdmissionBlocked("INVALID_CAPTURE_TEXT")
    try:
        byte_length = len(body.encode("utf-8"))
    except UnicodeEncodeError as exc:
        raise AdmissionBlocked("INVALID_CAPTURE_TEXT") from exc
    if byte_length > MAX_RAW_BYTES:
        raise AdmissionBlocked("INVALID_CAPTURE_TEXT")
    # Explicitly normalized, operator-supplied capture. An actual GitHub API
    # fetch MUST occur separately under an approved trusted provider connector.
    return capture, raw


def _identity_matches(
    capture: dict[str, Any], *, repository: str, issue_number: int,
    node_id: str, updated_at: str,
) -> None:
    if (capture["repository"], capture["issue_number"], capture["node_id"]) != (
        repository, issue_number, node_id
    ):
        raise AdmissionBlocked("PROVIDER_IDENTITY_MISMATCH")
    if capture["updated_at"] != updated_at:
        raise AdmissionBlocked("SOURCE_STALE")


def _write_once(folder: Path, name: str, data: bytes) -> None:
    # Directory is exclusively created by this operator call (0700).
    path = folder / name
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o400)
    try:
        with os.fdopen(fd, "wb", closefd=True) as handle:
            handle.write(data)
            handle.flush()
            os.fchmod(handle.fileno(), 0o400)
            os.fsync(handle.fileno())
    except BaseException:
        # Leave incomplete bundle without receipt: verify_bundle MUST block it.
        raise


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _entry_dir(root: Path, source_id: str) -> Path:
    if not isinstance(source_id, str) or not SNAPSHOT_RE.fullmatch(source_id):
        raise AdmissionBlocked("INVALID_SOURCE_ID")
    return root / source_id.replace("/", "__")


def _check_registry_revision(
    *, registry_root: Path, source_id: str, repository: str,
    issue_number: int, node_id: str, updated_at: str,
) -> None:
    """Prevent accidental provider aliases and nonmonotonic source revisions.

    Existing entries must themselves verify. This makes an interrupted staged
    record block subsequent admission until an operator resolves it explicitly.
    This check does NOT authenticate remote GitHub state or make stage atomic
    against malicious same-user concurrent writers.
    """
    new_prefix, new_rev = source_id.rsplit("/r", 1)
    versions: list[tuple[int, str]] = []
    for path in sorted(registry_root.iterdir()):
        if path.name.startswith(".r6-schema-check-"):
            continue
        if not path.is_dir() or path.is_symlink():
            raise AdmissionBlocked("REGISTRY_UNKNOWN_ENTRY")
        match = re.fullmatch(r"(BP-[A-Za-z0-9_-]{2,60})__r([1-9][0-9]*)", path.name)
        if match is None:
            raise AdmissionBlocked("REGISTRY_UNKNOWN_ENTRY")
        entry_id = match.group(1) + "/r" + match.group(2)
        if entry_id == source_id:
            raise AdmissionBlocked("SOURCE_ALREADY_STAGED")
        known = verify_bundle(registry_root=registry_root, source_id=entry_id)
        same_prefix = match.group(1) == new_prefix
        same_node = known["github_node_id"] == node_id
        same_issue = (known["github_repository"] == repository and
                      known["github_issue_number"] == issue_number)
        same_provider = same_issue and same_node
        if same_prefix and not same_provider:
            raise AdmissionBlocked("SOURCE_IDENTITY_CONFLICT")
        if (same_node or same_issue) and not same_prefix:
            raise AdmissionBlocked("PROVIDER_IDENTITY_ALREADY_BOUND")
        if same_provider:
            versions.append((int(match.group(2)), known["github_updated_at"]))
    if versions:
        latest, previous_updated = max(versions)
        if int(new_rev) != latest + 1 or updated_at <= previous_updated:
            raise AdmissionBlocked("SOURCE_REVISION_CONFLICT")
    elif int(new_rev) != 1:
        raise AdmissionBlocked("SOURCE_REVISION_FIRST_MUST_BE_R1")


@contextmanager
def _exclusive_registry_lock(registry_root: Path):
    """Linux advisory lock on the private registry directory itself.

    All R1 operator writers must use this entrypoint. The lock is held from
    alias/revision scan through receipt fsync; no lockfile is introduced into
    the registry that would invalidate the entry inventory. It does not
    defend against same-user non-cooperative writers or a malicious Host.
    """
    _require_operator_directory(registry_root)
    try:
        fd = os.open(registry_root, os.O_RDONLY | os.O_DIRECTORY |
                     os.O_NOFOLLOW | os.O_CLOEXEC)
    except OSError as exc:
        raise AdmissionBlocked("REGISTRY_LOCK_FAILED") from exc
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
        except OSError as exc:
            raise AdmissionBlocked("REGISTRY_LOCK_FAILED") from exc
        try:
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def _preflight_capture_unlocked(
    *, raw_source: Path, curated_snapshot: Path, capture_file: Path,
    expected_capture_sha256: str, expected_raw_sha256: str,
    expected_snapshot_sha256: str, source_id: str,
    repository: str, issue_number: int, node_id: str, updated_at: str,
    registry_root: Path, stage: bool = False,
) -> dict[str, Any]:
    """Validate operator pins, optionally prepare an immutable-by-convention local bundle.

    These pins are not remotely authenticated by this module. An operator MUST
    separately fetch and review original Issue content and verify its revision.
    """
    _require_operator_directory(registry_root)
    entry = _entry_dir(registry_root, source_id)
    _ensure_hash(expected_raw_sha256, "RAW")
    _ensure_hash(expected_snapshot_sha256, "SNAPSHOT")
    capture, capture_raw = _read_capture(capture_file, expected_capture_sha256)
    _identity_matches(capture, repository=repository, issue_number=issue_number,
                      node_id=node_id, updated_at=updated_at)
    raw = _read_regular_no_symlink(raw_source, MAX_RAW_BYTES)
    if sha(raw) != expected_raw_sha256:
        raise AdmissionBlocked("RAW_SOURCE_DRIFT")
    if raw != capture["body"].encode("utf-8"):
        raise AdmissionBlocked("CAPTURE_BODY_MISMATCH")
    snapshot_raw = _read_regular_no_symlink(curated_snapshot, MAX_SNAPSHOT_BYTES)
    if sha(snapshot_raw) != expected_snapshot_sha256:
        raise AdmissionBlocked("SNAPSHOT_DRIFT")
    if entry.exists() or entry.is_symlink():
        raise AdmissionBlocked("SOURCE_ALREADY_STAGED")
    _check_registry_revision(
        registry_root=registry_root, source_id=source_id,
        repository=repository, issue_number=issue_number,
        node_id=node_id, updated_at=updated_at
    )
    result = preflight(
        raw_source=raw_source, curated_snapshot=curated_snapshot,
        expected_raw_sha256=expected_raw_sha256,
        source_id=source_id, operator_staging_dir=registry_root, prepare=False
    )
    if result["snapshot_sha256"] != expected_snapshot_sha256:
        raise AdmissionBlocked("SNAPSHOT_DRIFT")
    record: dict[str, Any] = {
        "schema_version": REGISTRY_VERSION,
        "status": STAGE_STATUS if stage else "PREFLIGHT_PASS_NOT_STAGED",
        "source_id": source_id,
        "github_repository": repository,
        "github_issue_number": issue_number,
        "github_node_id": node_id,
        "github_updated_at": updated_at,
        "github_html_url": capture["html_url"],
        "capture_sha256": expected_capture_sha256,
        "raw_sha256": expected_raw_sha256,
        "snapshot_sha256": expected_snapshot_sha256,
        "origin_authenticated": False,
        "semantic_approval_verified": False,
        "operator_review": "REQUIRED_NOT_RECORDED",
        "activation": "NOT_ACTIVE_NOT_PUBLISHED",
        "effect_authority": "NONE",
    }
    if stage:
        try:
            entry.mkdir(mode=0o700)
        except FileExistsError as exc:
            raise AdmissionBlocked("SOURCE_ALREADY_STAGED") from exc
        # Receipt is written LAST. An interrupted operation is blocked by
        # verify_bundle and cannot be interpreted as a complete admission.
        try:
            _write_once(entry, "capture.json", capture_raw)
            _write_once(entry, "raw.txt", raw)
            _write_once(entry, "snapshot.json", snapshot_raw)
            _write_once(entry, "receipt.json", _record_bytes(record))
            dirfd = os.open(entry, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                os.fsync(dirfd)
            finally:
                os.close(dirfd)
        except OSError as exc:
            raise AdmissionBlocked("STAGING_WRITE_FAILED") from exc
    return record


def preflight_capture(
    *, raw_source: Path, curated_snapshot: Path, capture_file: Path,
    expected_capture_sha256: str, expected_raw_sha256: str,
    expected_snapshot_sha256: str, source_id: str,
    repository: str, issue_number: int, node_id: str, updated_at: str,
    registry_root: Path, stage: bool = False,
) -> dict[str, Any]:
    """Operator entrypoint with registry-wide exclusive staging transaction."""
    kwargs = dict(raw_source=raw_source, curated_snapshot=curated_snapshot,
                  capture_file=capture_file,
                  expected_capture_sha256=expected_capture_sha256,
                  expected_raw_sha256=expected_raw_sha256,
                  expected_snapshot_sha256=expected_snapshot_sha256,
                  source_id=source_id, repository=repository,
                  issue_number=issue_number, node_id=node_id,
                  updated_at=updated_at, registry_root=registry_root, stage=stage)
    if stage:
        with _exclusive_registry_lock(registry_root):
            return _preflight_capture_unlocked(**kwargs)
    return _preflight_capture_unlocked(**kwargs)


def verify_bundle(*, registry_root: Path, source_id: str,
                  current_capture: Path | None = None,
                  expected_current_capture_sha256: str | None = None) -> dict[str, Any]:
    """Verify a staged bundle; reject any drift or stale *operator-supplied* observation.

    An offline comparison cannot authenticate the current GitHub state.
    """
    _require_operator_directory(registry_root)
    entry = _entry_dir(registry_root, source_id)
    if entry.is_symlink() or not entry.is_dir():
        raise AdmissionBlocked("SOURCE_NOT_STAGED")
    if entry.stat().st_uid != os.geteuid() or stat.S_IMODE(entry.stat().st_mode) & 0o077:
        raise AdmissionBlocked("STAGED_DIRECTORY_NOT_PRIVATE")
    if {x.name for x in entry.iterdir()} != EXPECTED_FILES:
        raise AdmissionBlocked("STAGED_BUNDLE_INCOMPLETE")
    for filename in EXPECTED_FILES:
        path = entry / filename
        if path.is_symlink() or not path.is_file():
            raise AdmissionBlocked("STAGED_BUNDLE_INVALID")
        if path.stat().st_uid != os.geteuid() or stat.S_IMODE(path.stat().st_mode) != 0o400:
            raise AdmissionBlocked("STAGED_FILE_NOT_READONLY")
    record_raw = _read_regular_no_symlink(entry / "receipt.json", 16_384)
    record = _json_unique(record_raw)
    if set(record) != RECEIPT_KEYS or record.get("schema_version") != REGISTRY_VERSION:
        raise AdmissionBlocked("REGISTRY_SCHEMA")
    if record.get("source_id") != source_id or record.get("status") != STAGE_STATUS:
        raise AdmissionBlocked("REGISTRY_STATE")
    if type(record.get("github_issue_number")) is not int:
        raise AdmissionBlocked("REGISTRY_SCHEMA")
    if record.get("origin_authenticated") is not False or (
        record.get("semantic_approval_verified") is not False or
        record.get("activation") != "NOT_ACTIVE_NOT_PUBLISHED" or
        record.get("effect_authority") != "NONE" or
        record.get("operator_review") != "REQUIRED_NOT_RECORDED"
    ):
        raise AdmissionBlocked("REGISTRY_AUTHORITY")
    if record_raw != _record_bytes(record):
        raise AdmissionBlocked("REGISTRY_NONCANONICAL")
    stored_capture = _read_regular_no_symlink(entry / "capture.json", MAX_CAPTURE_BYTES)
    stored_raw = _read_regular_no_symlink(entry / "raw.txt", MAX_RAW_BYTES)
    stored_snapshot = _read_regular_no_symlink(entry / "snapshot.json", MAX_SNAPSHOT_BYTES)
    for name, contents in (
        ("capture", stored_capture), ("raw", stored_raw),
        ("snapshot", stored_snapshot)
    ):
        if sha(contents) != record.get(name + "_sha256"):
            raise AdmissionBlocked("STAGED_" + name.upper() + "_DRIFT")
    capture = _json_unique(stored_capture)
    # Revalidate all captured fields, not only the bytes in the receipt.
    parsed, _ = _read_capture(entry / "capture.json", record["capture_sha256"])
    _identity_matches(parsed, repository=record["github_repository"],
                      issue_number=record["github_issue_number"],
                      node_id=record["github_node_id"],
                      updated_at=record["github_updated_at"])
    if parsed["html_url"] != record["github_html_url"]:
        raise AdmissionBlocked("STAGED_PROVIDER_URL_MISMATCH")
    if stored_raw != parsed["body"].encode("utf-8"):
        raise AdmissionBlocked("STAGED_BODY_MISMATCH")
    snapshot = _json_unique(stored_snapshot)
    if snapshot.get("source_id") != source_id:
        raise AdmissionBlocked("STAGED_SOURCE_ID_MISMATCH")
    if (current_capture is None) != (expected_current_capture_sha256 is None):
        raise AdmissionBlocked("CURRENT_CAPTURE_PIN_REQUIRED")
    if current_capture is not None:
        observation, _ = _read_capture(current_capture, expected_current_capture_sha256)
        _identity_matches(observation, repository=record["github_repository"],
                          issue_number=record["github_issue_number"],
                          node_id=record["github_node_id"],
                          updated_at=record["github_updated_at"])
        if sha(observation["body"].encode("utf-8")) != record["raw_sha256"]:
            raise AdmissionBlocked("SOURCE_STALE")
    return {
        "status": "STAGED_VERIFIED_INACTIVE",
        "source_id": source_id,
        "snapshot_sha256": record["snapshot_sha256"],
        "github_repository": record["github_repository"],
        "github_issue_number": record["github_issue_number"],
        "github_node_id": record["github_node_id"],
        "github_updated_at": record["github_updated_at"],
        "origin_authenticated": False,
        "semantic_approval_verified": False,
        "effect_authority": "NONE",
        "activation": "NOT_ACTIVE_NOT_PUBLISHED",
        "current_capture_compared": current_capture is not None,
    }
