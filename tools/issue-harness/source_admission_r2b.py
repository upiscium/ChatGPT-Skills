"""R2B Phase A: fixed-route read-only GitHub Issues adapter, NOT activated.

This module intentionally contains a real network implementation but DOES NOT
execute it on import. No live GET is authorized in Phase A. The pure injected
path is always SYNTHETIC; the operator-network path is additionally gated and
its result is still UNATTESTED and UNBOUND.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import http.client
import re
import socket
import ssl
import time
from typing import Any

from source_admission import AdmissionBlocked, _json_unique, require_literal_source_lines
from source_admission_r1 import NODE_RE
from source_admission_r2a import (
    R2AStatus, MAX_HTTP_BODY, MAX_JSON_DEPTH, MAX_RAW_BYTES,
    SyntheticHttpResponse, SyntheticTransportFailure,
)

FIXED_HOST = "api.github.com"
FIXED_REPOSITORY = "upiscium/ChatGPT-Skills"
FIXED_ISSUE_NUMBER = 13
FIXED_PATH = "/repos/upiscium/ChatGPT-Skills/issues/13"
FIXED_REPO_URL = "https://api.github.com/repos/upiscium/ChatGPT-Skills"
FIXED_API_URL = FIXED_REPO_URL + "/issues/13"
FIXED_HTML_URL = "https://github.com/upiscium/ChatGPT-Skills/issues/13"
API_VERSION = "2026-03-10"  # Live support must be checked at a separately approved gate.
MEDIA_TYPE = "application/vnd.github.raw+json"
MAX_TRANSFER_DECODED_BODY = 1_048_576
CHUNK_SIZE = 8192
SOCKET_TIMEOUT_SECONDS = 3
SOFT_ELAPSED_SECONDS = 10  # Best-effort; cannot bound DNS or a blocking socket call.
MAX_HEADER_COUNT = 64
MAX_HEADER_NAME = 128
MAX_HEADER_VALUE = 8192
# Future separate, one-shot live process MUST be supervised outside Python:
# GNU timeout --signal=TERM --kill-after=2s 10s (roughly 10–12s).
WATCHDOG_ARGS = ("timeout", "--signal=TERM", "--kill-after=2s", "10s")

_REAL_READ_CAPABILITY = object()  # Prevent *accidental* synthetic->real relabelling.
_HEADER_NAME = re.compile(r"[!#$%&'*+\-.^_\x60|~0-9A-Za-z]+", re.ASCII)
_CONTENT_TYPE = re.compile(
    r"[ \t]*application/json[ \t]*(?:;[ \t]*charset=utf-8[ \t]*)?",
    re.ASCII | re.IGNORECASE,
)
_CONTENT_ENCODING = re.compile(r"[ \t]*identity[ \t]*", re.ASCII | re.IGNORECASE)
_TIMESTAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", re.ASCII)


class R2BStatus(str, Enum):
    SYNTHETIC_PROVIDER_RESPONSE_UNBOUND = "SYNTHETIC_PROVIDER_RESPONSE_UNBOUND"
    OPERATOR_ENV_GITHUB_ISSUE_OBSERVED_UNBOUND = "OPERATOR_ENV_GITHUB_ISSUE_OBSERVED_UNBOUND"
    BLOCKED_LIVE_GATE_REQUIRED = "BLOCKED_LIVE_GATE_REQUIRED"
    BLOCKED_TARGET_INVALID = R2AStatus.BLOCKED_TARGET_INVALID.value
    BLOCKED_PROVIDER_UNAVAILABLE = R2AStatus.BLOCKED_PROVIDER_UNAVAILABLE.value
    BLOCKED_PROVIDER_SCHEMA = R2AStatus.BLOCKED_PROVIDER_SCHEMA.value
    BLOCKED_PROVIDER_REDIRECT = R2AStatus.BLOCKED_PROVIDER_REDIRECT.value
    BLOCKED_PROVIDER_NOT_FULL_RESPONSE = R2AStatus.BLOCKED_PROVIDER_NOT_FULL_RESPONSE.value
    BLOCKED_PROVIDER_AUTH = R2AStatus.BLOCKED_PROVIDER_AUTH.value
    BLOCKED_PROVIDER_RATE_LIMIT = R2AStatus.BLOCKED_PROVIDER_RATE_LIMIT.value
    BLOCKED_PROVIDER_RESOURCE = R2AStatus.BLOCKED_PROVIDER_RESOURCE.value
    BLOCKED_PROVIDER_HTTP_STATUS = R2AStatus.BLOCKED_PROVIDER_HTTP_STATUS.value
    BLOCKED_PR_NOT_ISSUE = R2AStatus.BLOCKED_PR_NOT_ISSUE.value
    BLOCKED_SOURCE_IDENTITY = R2AStatus.BLOCKED_SOURCE_IDENTITY.value
    BLOCKED_PROVIDER_STATE = R2AStatus.BLOCKED_PROVIDER_STATE.value


@dataclass(frozen=True, slots=True)
class ObservedIssueSummary:
    """Metadata only. No title/body text or trusted approval/provenance."""
    id: int
    number: int
    node_id: str
    updated_at: str
    title_sha256: str
    body_sha256: str
    response_sha256: str
    response_length: int


@dataclass(frozen=True, slots=True, init=False)
class R2BResult:
    status: R2BStatus
    issue: ObservedIssueSummary | None
    origin_authenticated: bool = field(default=False, init=False)
    human_approval_verified: bool = field(default=False, init=False)
    semantic_approval_verified: bool = field(default=False, init=False)
    effect_authority: str = field(default="NONE", init=False)
    activation: str = field(default="NOT_ACTIVE_NOT_PUBLISHED", init=False)

    def __init__(
        self,
        status: R2BStatus,
        issue: ObservedIssueSummary | None = None,
        *,
        _real_key: object | None = None,
    ) -> None:
        if type(status) is not R2BStatus:
            raise ValueError("INVALID_RESULT_STATUS")
        if status is R2BStatus.OPERATOR_ENV_GITHUB_ISSUE_OBSERVED_UNBOUND:
            if _real_key is not _REAL_READ_CAPABILITY:
                raise ValueError("REAL_READ_CONSTRUCTOR_ONLY")
        if status in (
            R2BStatus.OPERATOR_ENV_GITHUB_ISSUE_OBSERVED_UNBOUND,
            R2BStatus.SYNTHETIC_PROVIDER_RESPONSE_UNBOUND,
        ) and type(issue) is not ObservedIssueSummary:
            raise ValueError("MISSING_ISSUE_SUMMARY")
        if status not in (
            R2BStatus.OPERATOR_ENV_GITHUB_ISSUE_OBSERVED_UNBOUND,
            R2BStatus.SYNTHETIC_PROVIDER_RESPONSE_UNBOUND,
        ) and issue is not None:
            raise ValueError("BLOCKED_RESULT_CANNOT_INCLUDE_ISSUE")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "issue", issue)
        object.__setattr__(self, "origin_authenticated", False)
        object.__setattr__(self, "human_approval_verified", False)
        object.__setattr__(self, "semantic_approval_verified", False)
        object.__setattr__(self, "effect_authority", "NONE")
        object.__setattr__(self, "activation", "NOT_ACTIVE_NOT_PUBLISHED")


class _Stop(Exception):
    def __init__(self, status: R2BStatus):
        self.status = status
        super().__init__(status.value)


def _block(status: R2BStatus) -> None:
    raise _Stop(status)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _headers_from_pairs(pairs: Any) -> dict[str, str]:
    if type(pairs) not in (tuple, list) or len(pairs) > MAX_HEADER_COUNT:
        _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
    normalized: dict[str, str] = {}
    for pair in pairs:
        if type(pair) not in (tuple, list) or len(pair) != 2:
            _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
        name, value = pair
        if (type(name) is not str or type(value) is not str
                or len(name) > MAX_HEADER_NAME or len(value) > MAX_HEADER_VALUE
                or _HEADER_NAME.fullmatch(name) is None
                or any((ord(c) < 32 and c != "\t") or ord(c) == 127 for c in value)):
            _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
        lower = name.lower()
        if lower in normalized:
            _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
        normalized[lower] = value
    return normalized


def _headers_from_injected(raw: Any) -> dict[str, str]:
    if type(raw) is not dict:
        _block(R2BStatus.BLOCKED_TARGET_INVALID)
    if len(raw) > MAX_HEADER_COUNT:
        _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
    # Freeze only bounded caller-owned entries in one pass.
    try:
        copied = tuple(raw.items())
    except Exception:
        _block(R2BStatus.BLOCKED_TARGET_INVALID)
    return _headers_from_pairs(copied)


def _classify_status(status: Any, headers: dict[str, str]) -> None:
    if type(status) is not int or not 100 <= status <= 599:
        _block(R2BStatus.BLOCKED_TARGET_INVALID)
    if status == 304:
        _block(R2BStatus.BLOCKED_PROVIDER_NOT_FULL_RESPONSE)
    if 300 <= status < 400:
        _block(R2BStatus.BLOCKED_PROVIDER_REDIRECT)
    if status == 401:
        _block(R2BStatus.BLOCKED_PROVIDER_AUTH)
    if status == 403:
        if "retry-after" in headers:
            _block(R2BStatus.BLOCKED_PROVIDER_RATE_LIMIT)
        remaining = headers.get("x-ratelimit-remaining")
        if remaining is not None:
            if re.fullmatch(r"[0-9]+", remaining, re.ASCII) is None:
                _block(R2BStatus.BLOCKED_PROVIDER_HTTP_STATUS)
            if not remaining.lstrip("0"):
                _block(R2BStatus.BLOCKED_PROVIDER_RATE_LIMIT)
        _block(R2BStatus.BLOCKED_PROVIDER_AUTH)
    if status == 429:
        _block(R2BStatus.BLOCKED_PROVIDER_RATE_LIMIT)
    if status in (404, 410):
        _block(R2BStatus.BLOCKED_PROVIDER_RESOURCE)
    if 500 <= status <= 599:
        _block(R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE)
    if status != 200:
        _block(R2BStatus.BLOCKED_PROVIDER_HTTP_STATUS)


def _check_media(headers: dict[str, str]) -> None:
    if _CONTENT_TYPE.fullmatch(headers.get("content-type", "")) is None:
        _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
    encoding = headers.get("content-encoding")
    if encoding is not None and _CONTENT_ENCODING.fullmatch(encoding) is None:
        _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)


def _utc_seconds(value: Any) -> bool:
    if type(value) is not str or _TIMESTAMP.fullmatch(value) is None:
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo == timezone.utc
    except ValueError:
        return False


def _bounded_json(raw: bytes) -> dict[str, Any]:
    if type(raw) is not bytes or len(raw) > MAX_HTTP_BODY:
        _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
    try:
        value = _json_unique(raw)  # R1 duplicate keys/NaN/RecursionError guard
        todo = [(value, 0)]
        while todo:
            obj, depth = todo.pop()
            if depth > MAX_JSON_DEPTH:
                _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
            if type(obj) is float and (obj != obj or abs(obj) == float("inf")):
                _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
            if type(obj) is dict:
                todo.extend((v, depth + 1) for v in obj.values())
            if type(obj) is list:
                todo.extend((v, depth + 1) for v in obj)
        return value
    except _Stop:
        raise
    except (AdmissionBlocked, ValueError, OverflowError, RecursionError, TypeError):
        _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)


def _parse_unbound_issue(raw: bytes) -> ObservedIssueSummary:
    obj = _bounded_json(raw)
    # GitHub Issues endpoint returns PRs too; the key's presence is decisive.
    if "pull_request" in obj:
        _block(R2BStatus.BLOCKED_PR_NOT_ISSUE)
    required = {"id", "number", "node_id", "state", "repository_url", "url",
                "html_url", "title", "body", "updated_at"}
    if not required.issubset(obj):
        _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
    num = obj["number"]
    issue_id = obj["id"]
    node = obj["node_id"]
    state = obj["state"]
    title = obj["title"]
    body = obj["body"]
    updated = obj["updated_at"]
    if (type(issue_id) is not int or not 1 <= issue_id <= 2**63 - 1
            or type(num) is not int or not 1 <= num <= 2**31 - 1
            or type(node) is not str or NODE_RE.fullmatch(node) is None
            or type(state) is not str or type(title) is not str
            or not 1 <= len(title) <= 1024
            or type(body) is not str or not body or not _utc_seconds(updated)):
        _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
    try:
        if any(ord(ch) < 32 or 0x7f <= ord(ch) <= 0x9f
               or ch in "\u2028\u2029" for ch in title):
            _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
        title_raw = title.encode("utf-8")
        body_raw = body.encode("utf-8")
        require_literal_source_lines(body)
    except _Stop:
        raise
    except (AdmissionBlocked, UnicodeError):
        _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
    if len(body_raw) > MAX_RAW_BYTES:
        _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
    urls = (obj["repository_url"], obj["url"], obj["html_url"])
    if any(type(u) is not str for u in urls):
        _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
    if (num != FIXED_ISSUE_NUMBER or urls !=
            (FIXED_REPO_URL, FIXED_API_URL, FIXED_HTML_URL)):
        _block(R2BStatus.BLOCKED_SOURCE_IDENTITY)
    if state != "open":
        _block(R2BStatus.BLOCKED_PROVIDER_STATE)
    return ObservedIssueSummary(
        id=issue_id, number=num, node_id=node, updated_at=updated,
        title_sha256=_sha(title_raw), body_sha256=_sha(body_raw),
        response_sha256=_sha(raw), response_length=len(raw),
    )


def _evaluate_unbound(event: SyntheticHttpResponse | SyntheticTransportFailure,
                      *, real_key: object | None = None) -> R2BResult:
    if type(event) is SyntheticTransportFailure:
        try:
            kind = event.kind
        except Exception:
            return R2BResult(R2BStatus.BLOCKED_TARGET_INVALID)
        if type(kind) is not str or kind not in ("DNS", "CONNECT", "TLS", "TIMEOUT"):
            return R2BResult(R2BStatus.BLOCKED_TARGET_INVALID)
        return R2BResult(R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE)
    if type(event) is not SyntheticHttpResponse:
        return R2BResult(R2BStatus.BLOCKED_TARGET_INVALID)
    try:
        # Take exactly one local snapshot before schema validation; a caller
        # modifying its frozen dataclass via object.__setattr__ cannot change
        # the bytes or header map we actually classify afterward.
        status = event.status
        body = event.body
        incoming_headers = event.headers
        headers = _headers_from_injected(incoming_headers)
        _classify_status(status, headers)
        _check_media(headers)
        if type(body) is not bytes:
            _block(R2BStatus.BLOCKED_TARGET_INVALID)
        if len(body) > MAX_TRANSFER_DECODED_BODY:
            _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
        issue = _parse_unbound_issue(body)
        status = (R2BStatus.OPERATOR_ENV_GITHUB_ISSUE_OBSERVED_UNBOUND
                  if real_key is _REAL_READ_CAPABILITY
                  else R2BStatus.SYNTHETIC_PROVIDER_RESPONSE_UNBOUND)
        return R2BResult(status, issue, _real_key=real_key)
    except _Stop as exc:
        return R2BResult(exc.status)
    except Exception:
        return R2BResult(R2BStatus.BLOCKED_PROVIDER_SCHEMA)


def evaluate_injected_response(
    event: SyntheticHttpResponse | SyntheticTransportFailure,
) -> R2BResult:
    """PURE synthetic evaluation, never OPERATOR_ENV or Host provenance."""
    return _evaluate_unbound(event)


def watchdog_argv(python_binary: str, module_script: str) -> tuple[str, ...]:
    """Return (but NEVER EXECUTE) the separate live-canary watchdog argv."""
    if (type(python_binary) is not str or not python_binary.startswith("/")
            or type(module_script) is not str or not module_script.startswith("/")):
        raise ValueError("EXPECTED_ABSOLUTE_EXECUTABLE_AND_SCRIPT")
    return WATCHDOG_ARGS + (python_binary, module_script)


def _real_read_once() -> SyntheticHttpResponse:
    """A concrete fixed single GET. NEVER call during Phase A except patched tests."""
    context = ssl.create_default_context()
    if context.check_hostname is not True or context.verify_mode != ssl.CERT_REQUIRED:
        _block(R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE)
    connection: http.client.HTTPSConnection | None = None
    started = time.monotonic()
    try:
        connection = http.client.HTTPSConnection(
            FIXED_HOST, port=443, timeout=SOCKET_TIMEOUT_SECONDS, context=context,
        )
        connection.request("GET", FIXED_PATH, headers={
            "Host": FIXED_HOST,
            "User-Agent": "arca-issue-handoff-r2b-read-only-canary",
            "Accept": MEDIA_TYPE,
            "X-GitHub-Api-Version": API_VERSION,
            "Accept-Encoding": "identity",
        })
        response = connection.getresponse()
        status = response.status
        pairs = response.getheaders()
        headers = _headers_from_pairs(pairs)
        _classify_status(status, headers)
        _check_media(headers)
        transfer_encoding = headers.get("transfer-encoding")
        if transfer_encoding is not None:
            # Reject ambiguous TE+CL framing and any unsupported
            # transfer-coding; http.client removes chunked framing itself.
            if (re.fullmatch(r"[ \t]*chunked[ \t]*", transfer_encoding,
                             re.ASCII | re.IGNORECASE) is None
                    or "content-length" in headers):
                _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
        reported_size = headers.get("content-length")
        if reported_size is not None:
            if (re.fullmatch(r"[0-9]+", reported_size, re.ASCII) is None
                    or len(reported_size) > 12):
                _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
            if int(reported_size) > MAX_TRANSFER_DECODED_BODY:
                _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
        size = 0
        chunks: list[bytes] = []
        while True:
            if time.monotonic() - started > SOFT_ELAPSED_SECONDS:
                _block(R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE)
            # HTTPResponse.read(n) can loop internally until n bytes are
            # accumulated even if each socket recv makes a little progress.
            # read1(n) avoids that body-read amplification (except chunk
            # framing, headers and DNS); the external watchdog remains the
            # ONLY future canary wall-clock boundary.
            part = response.read1(min(CHUNK_SIZE, MAX_TRANSFER_DECODED_BODY + 1 - size))
            if type(part) is not bytes:
                _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
            if not part:
                break
            size += len(part)
            if size > MAX_TRANSFER_DECODED_BODY:
                _block(R2BStatus.BLOCKED_PROVIDER_SCHEMA)
            chunks.append(part)
            if time.monotonic() - started > SOFT_ELAPSED_SECONDS:
                _block(R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE)
        if reported_size is not None and int(reported_size) != size:
            _block(R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE)
        return SyntheticHttpResponse(status=status, headers=headers, body=b"".join(chunks))
    finally:
        if connection is not None:
            connection.close()


def _classify_transport_error(exc: Exception) -> R2BStatus:
    if isinstance(exc, _Stop):
        return exc.status
    if isinstance(exc, (socket.gaierror, TimeoutError, ConnectionError, ssl.SSLError,
                        http.client.IncompleteRead)):
        return R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE
    if isinstance(exc, (http.client.HTTPException, ValueError)):
        # A ValueError raised by HTTPResponse chunk framing is malformed
        # response syntax; do not mistake it for an authenticated issue.
        return R2BStatus.BLOCKED_PROVIDER_SCHEMA
    return R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE


def run_fixed_real_get(*, operator_one_shot_allow: bool = False) -> R2BResult:
    """Explicitly gated operator-side read. NOT an authentication or Human grant.

    Phase A MUST NOT call with the real network implementation. Tests may
    patch HTTPSConnection and must label that path SIMULATED_REAL_PATH.
    """
    if operator_one_shot_allow is not True:
        return R2BResult(R2BStatus.BLOCKED_LIVE_GATE_REQUIRED)
    try:
        read_event = _real_read_once()  # Concrete fixed GET (no injected URL).
    except Exception as exc:
        return R2BResult(_classify_transport_error(exc))
    return _evaluate_unbound(read_event, real_key=_REAL_READ_CAPABILITY)
