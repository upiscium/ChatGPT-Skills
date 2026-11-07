"""R2A offline-only evaluation of *synthetic* GitHub Issue HTTP responses.

This is NOT a trusted provider reader, host attestation, Human approval,
source publisher, GitHub client, MCP tool, or runtime activation path.
The input bundle and HTTP event are caller-supplied bytes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import math
import re
from typing import Any

from arca_issue_harness.core import SHA_RE, SNAPSHOT_RE, MAX_SNAPSHOT_BYTES
from source_admission import (
    AdmissionBlocked, MAX_RAW_BYTES, _json_unique,
    require_literal_source_lines, validate_snapshot_against_raw,
)
from source_admission_r1 import (
    CAPTURE_KEYS, CAPTURE_VERSION, MAX_CAPTURE_BYTES, NODE_RE,
    RECEIPT_KEYS, REGISTRY_VERSION, REPOSITORY_RE, STAGE_STATUS, _record_bytes,
)

MAX_HTTP_BODY = 1_048_576
MAX_JSON_DEPTH = 64
MAX_RECEIPT_BYTES = 16_384


class R2AStatus(str, Enum):
    SYNTHETIC_SOURCE_MATCH_NOT_PROVIDER_OBSERVED = "SYNTHETIC_SOURCE_MATCH_NOT_PROVIDER_OBSERVED"
    BLOCKED_TARGET_INVALID = "BLOCKED_TARGET_INVALID"
    BLOCKED_STAGED_SOURCE = "BLOCKED_STAGED_SOURCE"
    BLOCKED_PROVIDER_REDIRECT = "BLOCKED_PROVIDER_REDIRECT"
    BLOCKED_PROVIDER_NOT_FULL_RESPONSE = "BLOCKED_PROVIDER_NOT_FULL_RESPONSE"
    BLOCKED_PROVIDER_AUTH = "BLOCKED_PROVIDER_AUTH"
    BLOCKED_PROVIDER_RATE_LIMIT = "BLOCKED_PROVIDER_RATE_LIMIT"
    BLOCKED_PROVIDER_RESOURCE = "BLOCKED_PROVIDER_RESOURCE"
    BLOCKED_PROVIDER_UNAVAILABLE = "BLOCKED_PROVIDER_UNAVAILABLE"
    BLOCKED_PROVIDER_HTTP_STATUS = "BLOCKED_PROVIDER_HTTP_STATUS"
    BLOCKED_PROVIDER_SCHEMA = "BLOCKED_PROVIDER_SCHEMA"
    BLOCKED_PR_NOT_ISSUE = "BLOCKED_PR_NOT_ISSUE"
    BLOCKED_SOURCE_IDENTITY = "BLOCKED_SOURCE_IDENTITY"
    BLOCKED_PROVIDER_STATE = "BLOCKED_PROVIDER_STATE"
    BLOCKED_SOURCE_STALE = "BLOCKED_SOURCE_STALE"


@dataclass(frozen=True, slots=True)
class SourceTarget:
    repository_full_name: str
    issue_number: int
    expected_issue_id: int  # Caller-supplied; NOT stored or authenticated by R1.
    expected_node_id: str
    expected_updated_at: str
    expected_title: str
    expected_body_sha256: str
    source_id: str
    required_state: str = "open"


@dataclass(frozen=True, slots=True)
class R1BundleBytes:
    source_id: str
    capture: bytes
    raw: bytes
    snapshot: bytes
    receipt: bytes


@dataclass(frozen=True, slots=True)
class SyntheticHttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes


@dataclass(frozen=True, slots=True)
class SyntheticTransportFailure:
    kind: str


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    status: R2AStatus
    origin_authenticated: bool = field(default=False, init=False)
    human_approval_verified: bool = field(default=False, init=False)
    semantic_approval_verified: bool = field(default=False, init=False)
    effect_authority: str = field(default="NONE", init=False)
    activation: str = field(default="NOT_ACTIVE_NOT_PUBLISHED", init=False)

    def __post_init__(self) -> None:
        if type(self.status) is not R2AStatus:
            raise ValueError("Invalid result status")

    @property
    def accepted(self) -> bool:
        return self.status is R2AStatus.SYNTHETIC_SOURCE_MATCH_NOT_PROVIDER_OBSERVED


class _Rejected(Exception):
    def __init__(self, status: R2AStatus):
        self.status = status
        super().__init__(status.value)


def _reject(code: R2AStatus) -> None:
    raise _Rejected(code)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _utc_second(value: Any) -> bool:
    if type(value) is not str or re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value
    ) is None:
        return False
    try:
        date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return date.tzinfo == timezone.utc


def _valid_repo(value: Any) -> bool:
    return (type(value) is str and REPOSITORY_RE.fullmatch(value) is not None
            and all(part not in (".", "..") and not part.startswith("-")
                    for part in value.split("/")))


def _valid_title(value: Any) -> bool:
    if type(value) is not str or not 1 <= len(value) <= 1024:
        return False
    if any(ord(char) < 32 or 0x7f <= ord(char) <= 0x9f
           or char in "\u2028\u2029" for char in value):
        return False
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _check_depth(obj: Any, max_depth: int = MAX_JSON_DEPTH) -> None:
    pending = [(obj, 0)]
    while pending:
        value, depth = pending.pop()
        if depth > max_depth:
            raise ValueError("JSON_DEPTH_EXCEEDED")
        if type(value) is float and not math.isfinite(value):
            raise ValueError("NONFINITE")
        if type(value) is dict:
            pending.extend((child, depth + 1) for child in value.values())
        elif type(value) is list:
            pending.extend((child, depth + 1) for child in value)


def _parse_bounded_object(raw: bytes, limit: int) -> dict[str, Any]:
    if type(raw) is not bytes or len(raw) > limit:
        raise ValueError("BYTE_SHAPE")
    value = _json_unique(raw)  # R1 duplicate-key, NaN and recursive JSON controls.
    _check_depth(value)
    return value


def _check_target(target: SourceTarget, bundle: R1BundleBytes, event: Any) -> None:
    if type(target) is not SourceTarget or type(bundle) is not R1BundleBytes:
        _reject(R2AStatus.BLOCKED_TARGET_INVALID)
    if any(type(x) is not bytes for x in (
        bundle.capture, bundle.raw, bundle.snapshot, bundle.receipt
    )):
        _reject(R2AStatus.BLOCKED_TARGET_INVALID)
    if type(bundle.source_id) is not str or not SNAPSHOT_RE.fullmatch(bundle.source_id):
        _reject(R2AStatus.BLOCKED_TARGET_INVALID)
    if not _valid_repo(target.repository_full_name):
        _reject(R2AStatus.BLOCKED_TARGET_INVALID)
    if type(target.issue_number) is not int or not 1 <= target.issue_number <= 2**31 - 1:
        _reject(R2AStatus.BLOCKED_TARGET_INVALID)
    if type(target.expected_issue_id) is not int or not 1 <= target.expected_issue_id <= 2**63 - 1:
        _reject(R2AStatus.BLOCKED_TARGET_INVALID)
    if (type(target.expected_node_id) is not str
            or NODE_RE.fullmatch(target.expected_node_id) is None):
        _reject(R2AStatus.BLOCKED_TARGET_INVALID)
    if not _utc_second(target.expected_updated_at):
        _reject(R2AStatus.BLOCKED_TARGET_INVALID)
    if not _valid_title(target.expected_title):
        _reject(R2AStatus.BLOCKED_TARGET_INVALID)
    if (type(target.expected_body_sha256) is not str
            or SHA_RE.fullmatch(target.expected_body_sha256) is None
            or type(target.source_id) is not str
            or SNAPSHOT_RE.fullmatch(target.source_id) is None
            or type(target.required_state) is not str
            or target.required_state != "open"):
        _reject(R2AStatus.BLOCKED_TARGET_INVALID)
    if type(event) is SyntheticTransportFailure:
        if type(event.kind) is not str or event.kind not in ("DNS", "CONNECT", "TLS", "TIMEOUT"):
            _reject(R2AStatus.BLOCKED_TARGET_INVALID)
    elif type(event) is SyntheticHttpResponse:
        if (type(event.status) is not int or not 100 <= event.status <= 599
                or type(event.body) is not bytes or type(event.headers) is not dict
                or len(event.headers) > 64):
            _reject(R2AStatus.BLOCKED_TARGET_INVALID)
        if any(type(key) is not str or type(val) is not str
               or not key or len(key) > 128 or len(val) > 8192
               or not key.isascii()
               or any(ord(c) < 33 or ord(c) > 126 for c in key)
               or any(c in val for c in "\r\n\x00")
               for key, val in event.headers.items()):
            _reject(R2AStatus.BLOCKED_TARGET_INVALID)
    else:
        _reject(R2AStatus.BLOCKED_TARGET_INVALID)


def _validate_capture_bytes(raw: bytes) -> dict[str, Any]:
    cap = _parse_bounded_object(raw, MAX_CAPTURE_BYTES)
    if set(cap) != CAPTURE_KEYS or cap.get("schema_version") != CAPTURE_VERSION or cap.get("provider") != "github":
        raise ValueError("CAPTURE_SCHEMA")
    repo = cap.get("repository")
    number = cap.get("issue_number")
    node = cap.get("node_id")
    updated = cap.get("updated_at")
    if (not _valid_repo(repo) or type(number) is not int
            or not 1 <= number <= 2**31 - 1
            or type(node) is not str or NODE_RE.fullmatch(node) is None
            or not _utc_second(updated)):
        raise ValueError("CAPTURE_IDENTITY")
    if (cap.get("html_url") != f"https://github.com/{repo}/issues/{number}"
            or cap.get("api_url") != f"https://api.github.com/repos/{repo}/issues/{number}"):
        raise ValueError("CAPTURE_URL")
    title, body = cap.get("title"), cap.get("body")
    if not _valid_title(title) or type(body) is not str or not body:
        raise ValueError("CAPTURE_TEXT")
    body_bytes = body.encode("utf-8")
    if len(body_bytes) > MAX_RAW_BYTES:
        raise ValueError("CAPTURE_OVERSIZE")
    require_literal_source_lines(body)
    return cap


def _verify_memory_bundle(bundle: R1BundleBytes) -> tuple[dict[str, Any], dict[str, Any]]:
    # Bound all caller-owned buffers before hashing or parsing.
    if (len(bundle.capture) > MAX_CAPTURE_BYTES
            or len(bundle.raw) > MAX_RAW_BYTES
            or len(bundle.snapshot) > MAX_SNAPSHOT_BYTES
            or len(bundle.receipt) > MAX_RECEIPT_BYTES):
        raise ValueError("BUNDLE_OVERSIZE")
    receipt = _parse_bounded_object(bundle.receipt, MAX_RECEIPT_BYTES)
    if set(receipt) != RECEIPT_KEYS or receipt.get("schema_version") != REGISTRY_VERSION:
        raise ValueError("RECEIPT_SCHEMA")
    if (receipt.get("source_id") != bundle.source_id
            or receipt.get("status") != STAGE_STATUS
            or type(receipt.get("github_issue_number")) is not int):
        raise ValueError("RECEIPT_IDENTITY")
    if (receipt.get("origin_authenticated") is not False
            or receipt.get("semantic_approval_verified") is not False
            or receipt.get("activation") != "NOT_ACTIVE_NOT_PUBLISHED"
            or receipt.get("effect_authority") != "NONE"
            or receipt.get("operator_review") != "REQUIRED_NOT_RECORDED"):
        raise ValueError("RECEIPT_AUTHORITY")
    if bundle.receipt != _record_bytes(receipt):
        raise ValueError("RECEIPT_NONCANONICAL")
    for name, value in (
        ("capture", bundle.capture),
        ("raw", bundle.raw),
        ("snapshot", bundle.snapshot),
    ):
        digest = receipt.get(f"{name}_sha256")
        if type(digest) is not str or SHA_RE.fullmatch(digest) is None or _sha(value) != digest:
            raise ValueError("RECEIPT_DIGEST")
    cap = _validate_capture_bytes(bundle.capture)
    if (cap["repository"] != receipt.get("github_repository")
            or cap["issue_number"] != receipt.get("github_issue_number")
            or cap["node_id"] != receipt.get("github_node_id")
            or cap["updated_at"] != receipt.get("github_updated_at")
            or cap["html_url"] != receipt.get("github_html_url")
            or bundle.raw != cap["body"].encode("utf-8")):
        raise ValueError("BUNDLE_MISMATCH")
    checked = validate_snapshot_against_raw(
        raw=bundle.raw, snapshot_raw=bundle.snapshot, source_id=bundle.source_id,
    )
    if checked["snapshot_sha256"] != receipt["snapshot_sha256"]:
        raise ValueError("BUNDLE_SNAPSHOT")
    return cap, receipt


def _check_target_bind(target: SourceTarget, bundle: R1BundleBytes,
                       cap: dict[str, Any], receipt: dict[str, Any]) -> None:
    if bundle.source_id != target.source_id:
        _reject(R2AStatus.BLOCKED_STAGED_SOURCE)
    if (target.repository_full_name != cap["repository"]
            or target.issue_number != cap["issue_number"]
            or target.expected_node_id != cap["node_id"]
            or target.expected_updated_at != cap["updated_at"]
            or target.expected_title != cap["title"]
            or target.expected_body_sha256 != receipt["raw_sha256"]):
        _reject(R2AStatus.BLOCKED_STAGED_SOURCE)


def _normalized_headers(raw: dict[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name, value in raw.items():
        norm = name.lower()
        if norm in result:
            _reject(R2AStatus.BLOCKED_PROVIDER_SCHEMA)
        result[norm] = value
    return result


def _classify_event(event: SyntheticHttpResponse | SyntheticTransportFailure) -> bytes:
    if type(event) is SyntheticTransportFailure:
        _reject(R2AStatus.BLOCKED_PROVIDER_UNAVAILABLE)
    headers = _normalized_headers(event.headers)
    status = event.status
    if status == 304:
        _reject(R2AStatus.BLOCKED_PROVIDER_NOT_FULL_RESPONSE)
    if 300 <= status < 400:
        _reject(R2AStatus.BLOCKED_PROVIDER_REDIRECT)
    if status == 401:
        _reject(R2AStatus.BLOCKED_PROVIDER_AUTH)
    if status == 403:
        if "retry-after" in headers:
            _reject(R2AStatus.BLOCKED_PROVIDER_RATE_LIMIT)
        remaining = headers.get("x-ratelimit-remaining")
        if remaining is not None:
            if re.fullmatch(r"[0-9]+", remaining, flags=re.ASCII) is None:
                _reject(R2AStatus.BLOCKED_PROVIDER_HTTP_STATUS)
            # Avoid converting an untrusted gigantic decimal to int; Python
            # imposes version-dependent integer string-digit limits.
            if remaining.lstrip("0") == "":
                _reject(R2AStatus.BLOCKED_PROVIDER_RATE_LIMIT)
        _reject(R2AStatus.BLOCKED_PROVIDER_AUTH)
    if status == 429:
        _reject(R2AStatus.BLOCKED_PROVIDER_RATE_LIMIT)
    if status in (404, 410):
        _reject(R2AStatus.BLOCKED_PROVIDER_RESOURCE)
    if 500 <= status <= 599:
        _reject(R2AStatus.BLOCKED_PROVIDER_UNAVAILABLE)
    if status != 200:
        _reject(R2AStatus.BLOCKED_PROVIDER_HTTP_STATUS)
    ct = headers.get("content-type")
    if ct is None or re.fullmatch(
        r"[ 	]*application/json[ 	]*(?:;[ 	]*charset=utf-8[ 	]*)?",
        ct, re.IGNORECASE | re.ASCII
    ) is None:
        _reject(R2AStatus.BLOCKED_PROVIDER_SCHEMA)
    ce = headers.get("content-encoding")
    if ce is not None and ce.strip().lower() != "identity":
        _reject(R2AStatus.BLOCKED_PROVIDER_SCHEMA)
    if len(event.body) > MAX_HTTP_BODY:
        _reject(R2AStatus.BLOCKED_PROVIDER_SCHEMA)
    return event.body


def _check_issue_response(body: bytes, target: SourceTarget,
                          staged: dict[str, Any]) -> None:
    issue = _parse_bounded_object(body, MAX_HTTP_BODY)
    if "pull_request" in issue:
        _reject(R2AStatus.BLOCKED_PR_NOT_ISSUE)
    required = {
        "id", "number", "node_id", "state", "repository_url",
        "url", "html_url", "title", "body", "updated_at",
    }
    if not required.issubset(issue):
        _reject(R2AStatus.BLOCKED_PROVIDER_SCHEMA)
    if (type(issue["id"]) is not int or not 1 <= issue["id"] <= 2**63 - 1
            or type(issue["number"]) is not int or not 1 <= issue["number"] <= 2**31 - 1
            or type(issue["node_id"]) is not str or NODE_RE.fullmatch(issue["node_id"]) is None
            or type(issue["state"]) is not str
            or not _valid_title(issue["title"])
            or type(issue["body"]) is not str or not issue["body"]
            or not _utc_second(issue["updated_at"])):
        _reject(R2AStatus.BLOCKED_PROVIDER_SCHEMA)
    try:
        body_bytes = issue["body"].encode("utf-8")
        require_literal_source_lines(issue["body"])
    except (AdmissionBlocked, UnicodeEncodeError):
        _reject(R2AStatus.BLOCKED_PROVIDER_SCHEMA)
    if len(body_bytes) > MAX_RAW_BYTES:
        _reject(R2AStatus.BLOCKED_PROVIDER_SCHEMA)
    repo = target.repository_full_name
    num = target.issue_number
    canonical = (
        f"https://api.github.com/repos/{repo}",
        f"https://api.github.com/repos/{repo}/issues/{num}",
        f"https://github.com/{repo}/issues/{num}",
    )
    if any(type(issue[key]) is not str for key in ("repository_url", "url", "html_url")):
        _reject(R2AStatus.BLOCKED_PROVIDER_SCHEMA)
    if (issue["repository_url"], issue["url"], issue["html_url"]) != canonical:
        _reject(R2AStatus.BLOCKED_SOURCE_IDENTITY)
    if (issue["id"] != target.expected_issue_id
            or issue["number"] != num
            or issue["node_id"] != target.expected_node_id):
        _reject(R2AStatus.BLOCKED_SOURCE_IDENTITY)
    if issue["state"] != "open":
        _reject(R2AStatus.BLOCKED_PROVIDER_STATE)
    if (issue["updated_at"] != staged["updated_at"]
            or issue["title"] != staged["title"]
            or _sha(body_bytes) != target.expected_body_sha256):
        _reject(R2AStatus.BLOCKED_SOURCE_STALE)


def _freeze_inputs(
    target: SourceTarget, bundle: R1BundleBytes,
    event: SyntheticHttpResponse | SyntheticTransportFailure,
) -> tuple[SourceTarget, R1BundleBytes,
           SyntheticHttpResponse | SyntheticTransportFailure]:
    """Copy caller-controlled attributes once; never re-read a mutable header map."""
    if type(target) is not SourceTarget or type(bundle) is not R1BundleBytes:
        _reject(R2AStatus.BLOCKED_TARGET_INVALID)
    pinned = SourceTarget(
        repository_full_name=target.repository_full_name,
        issue_number=target.issue_number,
        expected_issue_id=target.expected_issue_id,
        expected_node_id=target.expected_node_id,
        expected_updated_at=target.expected_updated_at,
        expected_title=target.expected_title,
        expected_body_sha256=target.expected_body_sha256,
        source_id=target.source_id,
        required_state=target.required_state,
    )
    frozen = R1BundleBytes(
        source_id=bundle.source_id,
        capture=bundle.capture,
        raw=bundle.raw,
        snapshot=bundle.snapshot,
        receipt=bundle.receipt,
    )
    if type(event) is SyntheticHttpResponse:
        if type(event.headers) is not dict:
            _reject(R2AStatus.BLOCKED_TARGET_INVALID)
        # A plain new dict holds copies of immutable, validated header strings.
        copied_event = SyntheticHttpResponse(
            status=event.status, headers=dict(event.headers), body=event.body,
        )
    elif type(event) is SyntheticTransportFailure:
        copied_event = SyntheticTransportFailure(kind=event.kind)
    else:
        _reject(R2AStatus.BLOCKED_TARGET_INVALID)
    return pinned, frozen, copied_event


def evaluate_synthetic(target: SourceTarget, bundle: R1BundleBytes,
                       event: SyntheticHttpResponse | SyntheticTransportFailure) -> EvaluationResult:
    """Only deterministic checks; never an origin witness or action approval.

    All unexpected ordinary input/parser exceptions are converted to a
    closed-enum fail-closed result. KeyboardInterrupt/SystemExit are not caught.
    """
    try:
        target, bundle, event = _freeze_inputs(target, bundle, event)
        _check_target(target, bundle, event)
    except _Rejected as rejected:
        return EvaluationResult(rejected.status)
    except Exception:
        return EvaluationResult(R2AStatus.BLOCKED_TARGET_INVALID)

    try:
        staged, receipt = _verify_memory_bundle(bundle)
    except Exception:
        return EvaluationResult(R2AStatus.BLOCKED_STAGED_SOURCE)

    try:
        _check_target_bind(target, bundle, staged, receipt)
    except _Rejected as rejected:
        return EvaluationResult(rejected.status)
    except Exception:
        return EvaluationResult(R2AStatus.BLOCKED_STAGED_SOURCE)

    try:
        response = _classify_event(event)
    except _Rejected as rejected:
        return EvaluationResult(rejected.status)
    except Exception:
        return EvaluationResult(R2AStatus.BLOCKED_PROVIDER_SCHEMA)

    try:
        _check_issue_response(response, target, staged)
    except _Rejected as rejected:
        return EvaluationResult(rejected.status)
    except Exception:
        return EvaluationResult(R2AStatus.BLOCKED_PROVIDER_SCHEMA)

    return EvaluationResult(R2AStatus.SYNTHETIC_SOURCE_MATCH_NOT_PROVIDER_OBSERVED)
