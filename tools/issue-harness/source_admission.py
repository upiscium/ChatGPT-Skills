"""Isolated operator-only R0 source admission. Not an MCP tool or approval authority.

Only accepts an operator-curated R6 snapshot whose goal, source claims, and
project non-goals appear verbatim in the explicitly selected UTF-8 raw source.
No URL fetching, model-chosen paths, GitHub writes, or installed plugin changes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
from typing import Any

from arca_issue_harness.core import Harness, MAX_SNAPSHOT_BYTES, SHA_RE, SNAPSHOT_RE

MAX_RAW_BYTES = 262_144
PROVENANCE_UNVERIFIED = "operator-curated lexical transcription; NOT independently verified"


class AdmissionBlocked(Exception):
    """Fail-closed operator admission (not a security authorization decision)."""


def _read_regular_no_symlink(path: Path, limit: int) -> bytes:
    if not path.is_absolute():
        raise AdmissionBlocked("INPUT_PATH_NOT_ABSOLUTE")
    if any(x.is_symlink() for x in (path, *path.parents)):
        raise AdmissionBlocked("INPUT_SYMLINK")
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    except OSError as exc:
        raise AdmissionBlocked("INPUT_UNAVAILABLE") from exc
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise AdmissionBlocked("INPUT_NOT_REGULAR")
        data = bytearray()
        while len(data) <= limit:
            piece = os.read(fd, min(65_536, limit + 1 - len(data)))
            if not piece:
                break
            data.extend(piece)
        if len(data) > limit:
            raise AdmissionBlocked("OVERSIZE")
        return bytes(data)
    finally:
        os.close(fd)


def _json_unique(raw: bytes) -> dict[str, Any]:
    def pairs_unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for k, value in pairs:
            if k in result:
                raise AdmissionBlocked("DUPLICATE_JSON_KEY")
            result[k] = value
        return result

    def invalid_constant(_: str) -> Any:
        raise AdmissionBlocked("NONFINITE_JSON")

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs_unique,
                           parse_constant=invalid_constant)
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise AdmissionBlocked("INVALID_SNAPSHOT_JSON") from exc
    if not isinstance(value, dict):
        raise AdmissionBlocked("SNAPSHOT_NOT_OBJECT")
    return value


def _require_operator_directory(target: Path) -> None:
    if not target.is_absolute() or any(p.is_symlink() for p in (target, *target.parents)):
        raise AdmissionBlocked("TARGET_SYMLINK_OR_RELATIVE")
    try:
        s = target.stat()
    except OSError as exc:
        raise AdmissionBlocked("TARGET_UNAVAILABLE") from exc
    if not stat.S_ISDIR(s.st_mode) or s.st_uid != os.geteuid() or stat.S_IMODE(s.st_mode) & 0o077:
        raise AdmissionBlocked("TARGET_NOT_PRIVATE_OWNED_DIRECTORY")


def require_literal_source_lines(raw_text: str) -> None:
    """Reject controls that can hide conditions inside a rendered source line.

    Only CR, LF and TAB are legitimate ASCII controls for this offline source
    contract. Treat Unicode visual line separators and C1 controls as invalid
    rather than letting str.splitlines()/strip() reinterpret source boundaries.
    """
    if any(
        (ord(char) < 32 and char not in "\t\r\n")
        or 0x7F <= ord(char) <= 0x9F
        or char in "\u2028\u2029"
        for char in raw_text
    ):
        raise AdmissionBlocked("RAW_SOURCE_CONTROL_CHAR")


def _lexical_source_binding(raw_text: str, snap: dict[str, Any]) -> None:
    require_literal_source_lines(raw_text)
    # Exact *line* matching (with an optional Markdown list marker) prevents
    # silently dropping a condition from the end of a quoted requirement.
    # Still NOT semantic proof: the line may be negated or superseded elsewhere.
    lines = set()
    for line in raw_text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        item = line.strip()
        item = re.sub(r"^(?:[-*+]\s+|[0-9]{1,3}[.)]\s+)", "", item)
        if item:
            lines.add(item)
    quoted: list[tuple[Any, int]] = [(snap.get("original_goal"), 12)]
    claims = snap.get("source_claims", [])
    exclusions = snap.get("project_non_goals", [])
    decisions = snap.get("human_decisions", [])
    if not all(isinstance(x, list) for x in (claims, exclusions, decisions)):
        raise AdmissionBlocked("SNAPSHOT_SOURCE_SHAPE")
    for x in claims:
        if not isinstance(x, dict):
            raise AdmissionBlocked("SNAPSHOT_SOURCE_SHAPE")
        quoted.append((x.get("text"), 12))
    for goal in exclusions:
        # Short project non-goal names (e.g. the Japanese term for billing)
        # are valid only when they occupy a whole original-source line.
        quoted.append((goal, 2))
    for item in decisions:
        if not isinstance(item, dict):
            raise AdmissionBlocked("SNAPSHOT_SOURCE_SHAPE")
        quoted.append((item.get("question"), 8))
        quoted.append((item.get("impact"), 8))
    if not quoted or any(
        not isinstance(value, str) or len(value) < minimum or
        value != value.strip() or value not in lines
        for value, minimum in quoted
    ):
        raise AdmissionBlocked("UNVERIFIED_SOURCE_QUOTE")


def _atomic_link_readonly(folder: Path, filename: str, contents: bytes) -> Path:
    final = folder / filename
    if final.exists() or final.is_symlink():
        raise AdmissionBlocked("DESTINATION_EXISTS")
    fd, temporary = tempfile.mkstemp(dir=folder, prefix=".pending-r6-", suffix=".tmp")
    tmp = Path(temporary)
    try:
        with os.fdopen(fd, "wb", closefd=True) as file:
            file.write(contents)
            file.flush()
            os.fchmod(file.fileno(), 0o400)
            os.fsync(file.fileno())
        try:
            os.link(tmp, final, follow_symlinks=False)
        except FileExistsError as exc:
            raise AdmissionBlocked("DESTINATION_EXISTS") from exc
        return final
    finally:
        tmp.unlink(missing_ok=True)


def validate_snapshot_against_raw(
    *, raw: bytes, snapshot_raw: bytes, source_id: str,
) -> dict[str, Any]:
    """Recheck a pinned pair without writing to the Source Registry.

    Reuse exactly the same lexical, provenance and R6 schema rules at initial
    preflight and later registry verify; only a disposable temp copy is made.
    This is NOT an approval, authentic provider read or activation operation.
    """
    if not isinstance(source_id, str) or not SNAPSHOT_RE.fullmatch(source_id):
        raise AdmissionBlocked("INVALID_SOURCE_ID")
    if len(raw) > MAX_RAW_BYTES or len(snapshot_raw) > MAX_SNAPSHOT_BYTES:
        raise AdmissionBlocked("OVERSIZE")
    try:
        raw_text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AdmissionBlocked("RAW_SOURCE_NOT_UTF8") from exc
    snapshot = _json_unique(snapshot_raw)
    if snapshot.get("source_id") != source_id:
        raise AdmissionBlocked("SNAPSHOT_ID_MISMATCH")
    if snapshot.get("approval_provenance") != PROVENANCE_UNVERIFIED:
        raise AdmissionBlocked("APPROVAL_PROVENANCE_UNSAFE")
    _lexical_source_binding(raw_text, snapshot)
    digest = hashlib.sha256(snapshot_raw).hexdigest()
    filename = source_id.replace("/", "__") + ".json"
    # Isolated private scratch directory: do not create temporary entries
    # inside the persistent registry, even on verification failure.
    with tempfile.TemporaryDirectory(prefix=".r6-schema-check-") as sandbox:
        checked = Path(sandbox) / filename
        checked.write_bytes(snapshot_raw)
        try:
            validated, findings = Harness(Path(sandbox))._load_snapshot(source_id, digest)
        except (TypeError, ValueError, KeyError, AttributeError, OSError, RecursionError) as exc:
            raise AdmissionBlocked("SOURCE_SCHEMA_REJECTED") from exc
        if validated is None or findings:
            raise AdmissionBlocked("SOURCE_SCHEMA_REJECTED")
    return {
        "snapshot_sha256": digest,
        "lexical_source_claims_checked": len(snapshot["source_claims"]),
        "lexical_non_goals_checked": len(snapshot["project_non_goals"]),
    }


def preflight(
    *,
    raw_source: Path,
    curated_snapshot: Path,
    expected_raw_sha256: str,
    source_id: str,
    operator_staging_dir: Path,
    prepare: bool,
) -> dict[str, Any]:
    if not SNAPSHOT_RE.fullmatch(source_id):
        raise AdmissionBlocked("INVALID_SOURCE_ID")
    if not SHA_RE.fullmatch(expected_raw_sha256):
        raise AdmissionBlocked("INVALID_EXPECTED_RAW_SHA")
    _require_operator_directory(operator_staging_dir)
    raw = _read_regular_no_symlink(raw_source, MAX_RAW_BYTES)
    if hashlib.sha256(raw).hexdigest() != expected_raw_sha256:
        raise AdmissionBlocked("RAW_SOURCE_DRIFT")
    snapshot_raw = _read_regular_no_symlink(curated_snapshot, MAX_SNAPSHOT_BYTES)
    validated = validate_snapshot_against_raw(
        raw=raw, snapshot_raw=snapshot_raw, source_id=source_id
    )
    digest = validated["snapshot_sha256"]
    filename = source_id.replace("/", "__") + ".json"
    final = operator_staging_dir / filename
    if final.exists() or final.is_symlink():
        raise AdmissionBlocked("DESTINATION_EXISTS")
    record: dict[str, Any] = {
        "status": "PREPARED_OPERATOR_ONLY" if prepare else "PREFLIGHT_PASS_NO_ADMISSION",
        "source_id": source_id,
        "raw_sha256": expected_raw_sha256,
        "snapshot_sha256": digest,
        "snapshot_filename": filename,
        "lexical_source_claims_checked": validated["lexical_source_claims_checked"],
        "lexical_non_goals_checked": validated["lexical_non_goals_checked"],
        "origin_authenticated": False,
        "semantic_approval_verified": False,
        "authority": "none-issued; explicit Human approval still required for any write",
        "mcp_tools_added": 0,
    }
    if prepare:
        _atomic_link_readonly(operator_staging_dir, filename, snapshot_raw)
        # Do not auto-activate the new source in the running Claude plugin.
        record["activation"] = "NOT_ACTIVE_NOT_PUBLISHED"
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Operator-only, local R6 snapshot preflight")
    parser.add_argument("--raw-source", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--expected-raw-sha256", required=True)
    parser.add_argument("--staging-dir", type=Path, required=True)
    parser.add_argument("--prepare", action="store_true", help="Write private, inactive snapshot only")
    args = parser.parse_args()
    try:
        output = preflight(
            raw_source=args.raw_source, curated_snapshot=args.snapshot,
            expected_raw_sha256=args.expected_raw_sha256,
            source_id=args.source_id,
            operator_staging_dir=args.staging_dir,
            prepare=args.prepare,
        )
    except AdmissionBlocked as exc:
        print(json.dumps({"status": "BLOCKED", "code": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
