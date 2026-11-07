"""R2B Phase A: all tests are synthetic; real GET is NEVER performed."""
from dataclasses import FrozenInstanceError, replace
import hashlib
import http.client
import json
import pathlib
import socket
import ssl
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import source_admission_r2b as r2b
from source_admission_r2a import SyntheticHttpResponse, SyntheticTransportFailure

FIXTURE_ISSUE_ID = 900_013
FIXTURE_NODE_ID = "I_SYNTHETIC_R2B_987"


def dump(obj):
    text = json.dumps(obj, sort_keys=True, ensure_ascii=False) + "\n"
    try:
        return text.encode("utf-8")
    except UnicodeEncodeError:
        # An escaped JSON lone surrogate can be syntactically valid JSON.
        return (json.dumps(obj, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


class _NetworkForbidden(BaseException):
    """A test sentry intentionally OUTSIDE adapter's except Exception."""


@pytest.fixture(autouse=True)
def block_any_real_network(monkeypatch):
    def fail(*args, **kwargs):
        raise _NetworkForbidden("NETWORK_FORBIDDEN_IN_R2B_PHASE_A")
    # A real network escape must fail the test, not be classified as an
    # expected BLOCKED_PROVIDER_UNAVAILABLE by run_fixed_real_get.
    monkeypatch.setattr(r2b.http.client, "HTTPSConnection", fail)
    monkeypatch.setattr(socket, "create_connection", fail)
    monkeypatch.setattr(socket, "getaddrinfo", fail)
    monkeypatch.setattr(socket.socket, "connect", fail)
    monkeypatch.setattr(socket.socket, "connect_ex", fail)
    monkeypatch.setattr(socket.socket, "sendto", fail)
    monkeypatch.setattr(ssl.SSLContext, "wrap_socket", fail)


@pytest.fixture
def issue_data():
    return {
        "id": FIXTURE_ISSUE_ID,
        "number": 13,
        "node_id": FIXTURE_NODE_ID,
        "state": "open",
        "repository_url": r2b.FIXED_REPO_URL,
        "url": r2b.FIXED_API_URL,
        "html_url": r2b.FIXED_HTML_URL,
        "title": "Synthetic issue: read-only parser",
        "body": "Requirement X must remain confirmed.\nNo mutation of source registry.\n",
        "updated_at": "2026-11-07T08:00:00Z",
    }


@pytest.fixture
def synthetic_response(issue_data):
    return SyntheticHttpResponse(
        status=200,
        headers={"Content-Type": "application/json; charset=utf-8"},
        body=dump(issue_data),
    )


def assert_blocked(result, status):
    assert type(result) is r2b.R2BResult
    assert result.status is status
    assert result.issue is None
    assert result.origin_authenticated is False
    assert result.human_approval_verified is False
    assert result.semantic_approval_verified is False
    assert result.effect_authority == "NONE"
    assert result.activation == "NOT_ACTIVE_NOT_PUBLISHED"


def assert_synthetic_unbound(result, issue_data):
    assert result.status is r2b.R2BStatus.SYNTHETIC_PROVIDER_RESPONSE_UNBOUND
    assert result.issue is not None
    assert result.issue.number == 13
    assert result.issue.id == issue_data["id"]
    assert result.issue.node_id == issue_data["node_id"]
    assert result.issue.body_sha256 == hashlib.sha256(issue_data["body"].encode()).hexdigest()
    assert result.issue.title_sha256 == hashlib.sha256(issue_data["title"].encode()).hexdigest()
    assert result.origin_authenticated is False
    assert result.human_approval_verified is False
    assert result.effect_authority == "NONE"
    assert result.activation == "NOT_ACTIVE_NOT_PUBLISHED"


def mutated(issue_data, key, value):
    copy = dict(issue_data)
    if value == "__DELETE__":
        copy.pop(key)
    else:
        copy[key] = value
    return SyntheticHttpResponse(200, {"content-type": "application/json"}, dump(copy))


class FakeHTTPResponse:
    def __init__(self, status, headers, body, *, failure=None, dribble=False):
        self.status = status
        self.headers = list(headers)
        self.body = body
        self.read_calls = []
        self.failure = failure
        self.dribble = dribble
        self.pos = 0

    def getheaders(self):
        return self.headers

    def read(self, size):
        raise AssertionError("REAL_ADAPTER_SHOULD_USE_READ1_NOT_READ")

    def read1(self, size):
        self.read_calls.append(size)
        if self.failure is not None:
            raise self.failure
        if self.pos >= len(self.body):
            return b""
        n = min(size, 1 if self.dribble else len(self.body) - self.pos)
        part = self.body[self.pos:self.pos + n]
        self.pos += len(part)
        return part


class FakeConnection:
    def __init__(self, response, log):
        self.response = response
        self.log = log

    def request(self, method, path, *, headers):
        self.log.append(("request", method, path, dict(headers)))

    def getresponse(self):
        self.log.append(("getresponse",))
        return self.response

    def close(self):
        self.log.append(("close",))


def simulated_real_path(monkeypatch, response, *, expected_failure=None):
    """Monkeypatch concrete http.client path; SIMULATED, NOT an actual GET."""
    log = []
    context = type("FakeSSLContext", (), {
        "check_hostname": True, "verify_mode": ssl.CERT_REQUIRED,
    })()

    def ctor(host, *, port, timeout, context):
        log.append(("connect", host, port, timeout, context.check_hostname,
                    context.verify_mode))
        if expected_failure is not None:
            raise expected_failure
        return FakeConnection(response, log)

    monkeypatch.setattr(r2b.ssl, "create_default_context", lambda: context)
    monkeypatch.setattr(r2b.http.client, "HTTPSConnection", ctor)
    return log


def test_synthetic_success_is_unbound_not_provider_proof(synthetic_response, issue_data):
    assert_synthetic_unbound(r2b.evaluate_injected_response(synthetic_response), issue_data)


def test_injected_metadata_cannot_claim_real_observation(synthetic_response, issue_data):
    payload = dict(issue_data)
    payload["authenticated"] = True
    payload["host_observed"] = True
    event = replace(synthetic_response,
                    body=dump(payload),
                    headers={**synthetic_response.headers,
                             "X-GitHub-Request-Id": "synthetic", "ETag": 'W/"fake"'})
    assert_synthetic_unbound(r2b.evaluate_injected_response(event), issue_data)


def test_real_observation_result_constructor_is_guarded(synthetic_response, issue_data):
    synthetic = r2b.evaluate_injected_response(synthetic_response)
    with pytest.raises(ValueError, match="REAL_READ_CONSTRUCTOR_ONLY"):
        r2b.R2BResult(r2b.R2BStatus.OPERATOR_ENV_GITHUB_ISSUE_OBSERVED_UNBOUND,
                      synthetic.issue)
    with pytest.raises(ValueError):
        r2b.R2BResult("OPERATOR_ENV_GITHUB_ISSUE_OBSERVED_UNBOUND")
    with pytest.raises(TypeError):
        r2b.R2BResult(r2b.R2BStatus.SYNTHETIC_PROVIDER_RESPONSE_UNBOUND,
                      synthetic.issue, origin_authenticated=True)


def test_live_get_is_disabled_by_default_and_never_opens_socket():
    assert_blocked(r2b.run_fixed_real_get(),
                   r2b.R2BStatus.BLOCKED_LIVE_GATE_REQUIRED)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=1),
                   r2b.R2BStatus.BLOCKED_LIVE_GATE_REQUIRED)


def test_operator_watchdog_argv_never_executes_process():
    assert r2b.watchdog_argv("/usr/bin/python3", "/tmp/fixed-one-shot.py") == (
        "timeout", "--signal=TERM", "--kill-after=2s", "10s",
        "/usr/bin/python3", "/tmp/fixed-one-shot.py",
    )
    with pytest.raises(ValueError):
        r2b.watchdog_argv("python3", "/tmp/fixed-one-shot.py")
    assert "subprocess" not in pathlib.Path(r2b.__file__).read_text()


def test_fixed_route_const_and_no_generic_url_configuration():
    assert r2b.FIXED_HOST == "api.github.com"
    assert r2b.FIXED_PATH == "/repos/upiscium/ChatGPT-Skills/issues/13"
    assert r2b.FIXED_ISSUE_NUMBER == 13
    assert r2b.FIXED_HTML_URL.endswith("/issues/13")


@pytest.mark.parametrize("key,value,code", [
    ("id", -1, r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ("id", True, r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ("number", True, r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ("number", 14, r2b.R2BStatus.BLOCKED_SOURCE_IDENTITY),
    ("node_id", "PR_bad", r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ("repository_url", "https://api.github.com/repos/other/x",
     r2b.R2BStatus.BLOCKED_SOURCE_IDENTITY),
    ("url", "https://api.github.com/repos/other/x/issues/13",
     r2b.R2BStatus.BLOCKED_SOURCE_IDENTITY),
    ("html_url", "https://github.com/other/x/issues/13",
     r2b.R2BStatus.BLOCKED_SOURCE_IDENTITY),
    ("state", "closed", r2b.R2BStatus.BLOCKED_PROVIDER_STATE),
    ("state", 17, r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ("title", None, r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ("title", "\ud800", r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ("title", "bad\u2028sep", r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ("body", None, r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ("body", "", r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ("body", "A\u2028B", r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ("body", "text\u0085break", r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ("updated_at", "2026-11-07T08:00:00.000Z",
     r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ("updated_at", "2026-11-07T09:00:00+01:00",
     r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ("body", "__DELETE__", r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
])
def test_injected_schema_identity_state_negative(issue_data, key, value, code):
    event = mutated(issue_data, key, value)
    assert_blocked(r2b.evaluate_injected_response(event), code)


def test_pr_presence_even_null_preempts_missing_fields(issue_data):
    obj = {"pull_request": None, "number": 13}
    event = SyntheticHttpResponse(200, {"content-type": "application/json"}, dump(obj))
    assert_blocked(r2b.evaluate_injected_response(event), r2b.R2BStatus.BLOCKED_PR_NOT_ISSUE)


@pytest.mark.parametrize("status,headers,expected", [
    (301, {}, r2b.R2BStatus.BLOCKED_PROVIDER_REDIRECT),
    (302, {}, r2b.R2BStatus.BLOCKED_PROVIDER_REDIRECT),
    (307, {}, r2b.R2BStatus.BLOCKED_PROVIDER_REDIRECT),
    (308, {}, r2b.R2BStatus.BLOCKED_PROVIDER_REDIRECT),
    (304, {}, r2b.R2BStatus.BLOCKED_PROVIDER_NOT_FULL_RESPONSE),
    (401, {}, r2b.R2BStatus.BLOCKED_PROVIDER_AUTH),
    (403, {}, r2b.R2BStatus.BLOCKED_PROVIDER_AUTH),
    (403, {"x-ratelimit-remaining": "10"}, r2b.R2BStatus.BLOCKED_PROVIDER_AUTH),
    (403, {"x-ratelimit-remaining": "00"}, r2b.R2BStatus.BLOCKED_PROVIDER_RATE_LIMIT),
    (403, {"Retry-After": "1"}, r2b.R2BStatus.BLOCKED_PROVIDER_RATE_LIMIT),
    (403, {"Retry-After": "1", "x-ratelimit-remaining": "garbage"}, r2b.R2BStatus.BLOCKED_PROVIDER_RATE_LIMIT),
    (403, {"x-ratelimit-remaining": "garbage"}, r2b.R2BStatus.BLOCKED_PROVIDER_HTTP_STATUS),
    (404, {}, r2b.R2BStatus.BLOCKED_PROVIDER_RESOURCE),
    (410, {}, r2b.R2BStatus.BLOCKED_PROVIDER_RESOURCE),
    (429, {}, r2b.R2BStatus.BLOCKED_PROVIDER_RATE_LIMIT),
    (500, {}, r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE),
    (503, {}, r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE),
    (204, {}, r2b.R2BStatus.BLOCKED_PROVIDER_HTTP_STATUS),
    (206, {}, r2b.R2BStatus.BLOCKED_PROVIDER_HTTP_STATUS),
    (422, {}, r2b.R2BStatus.BLOCKED_PROVIDER_HTTP_STATUS),
    (451, {}, r2b.R2BStatus.BLOCKED_PROVIDER_HTTP_STATUS),
])
def test_synthetic_http_status_table(status, headers, expected):
    event = SyntheticHttpResponse(status, headers, b"")
    assert_blocked(r2b.evaluate_injected_response(event), expected)


@pytest.mark.parametrize("kind", ["DNS", "CONNECT", "TLS", "TIMEOUT"])
def test_synthetic_transport_error_table(kind):
    assert_blocked(r2b.evaluate_injected_response(SyntheticTransportFailure(kind)),
                   r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE)


@pytest.mark.parametrize("headers,expected", [
    ({}, r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ({"content-type": "text/html"}, r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ({"content-type": "application/json", "Content-Type": "application/json"},
     r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ({"content-type": "application/json", "Content-Encoding": "gzip"},
     r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ({"content-type": "application/json", "Content-Encoding": "identity, gzip"},
     r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ({"content-type": "application/json; charset=utf-8"},
     r2b.R2BStatus.SYNTHETIC_PROVIDER_RESPONSE_UNBOUND),
    ({"content-type": "application/json", "Content-Encoding": "IDENTITY"},
     r2b.R2BStatus.SYNTHETIC_PROVIDER_RESPONSE_UNBOUND),
    ({"Content-Type": "application/json \u2028"}, r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    ({"Content-Type": "application/j\u017fon"}, r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
])
def test_synthetic_header_content_rules(synthetic_response, issue_data, headers, expected):
    got = r2b.evaluate_injected_response(replace(synthetic_response, headers=headers))
    if expected is r2b.R2BStatus.SYNTHETIC_PROVIDER_RESPONSE_UNBOUND:
        assert_synthetic_unbound(got, issue_data)
    else:
        assert_blocked(got, expected)


@pytest.mark.parametrize("body", [
    b'{"a":1, "a":2}',
    b'{"json":"unterminated',
    b'not json',
    b'{"bad": NaN}',
    b'{"bad": 1e999}',
    b'["wrong root"]',
    b"\xff\xfe",
    b" " * 1_048_577,
])
def test_injected_json_failures(synthetic_response, body):
    assert_blocked(r2b.evaluate_injected_response(replace(synthetic_response, body=body)),
                   r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA)


def test_injected_deep_json_proper_rejection(synthetic_response, issue_data):
    extra = 1
    for _ in range(70):
        extra = [extra]
    obj = dict(issue_data, extra=extra)
    assert_blocked(r2b.evaluate_injected_response(replace(synthetic_response, body=dump(obj))),
                   r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA)


def test_unbound_numeric_and_node_ids_are_observations_not_independent_pins(
    synthetic_response, issue_data,
):
    different = dict(issue_data, id=777_777, node_id="I_OTHER_SYNTHETIC_987")
    result = r2b.evaluate_injected_response(replace(synthetic_response, body=dump(different)))
    assert_synthetic_unbound(result, different)


def test_injected_cannot_be_relabelled_via_claimed_flags(synthetic_response):
    result = r2b.evaluate_injected_response(synthetic_response)
    assert result.status is not r2b.R2BStatus.OPERATOR_ENV_GITHUB_ISSUE_OBSERVED_UNBOUND
    with pytest.raises(FrozenInstanceError):
        result.status = r2b.R2BStatus.OPERATOR_ENV_GITHUB_ISSUE_OBSERVED_UNBOUND


# Simulations of the concrete fixed GET path. These are NOT live GitHub requests.
def test_SIMULATED_REAL_PATH_one_get_and_no_credential_headers(
    monkeypatch, synthetic_response, issue_data,
):
    monkeypatch.setenv("GH_TOKEN", "should-not-be-read")
    response = FakeHTTPResponse(200, [("Content-Type", "application/json")],
                                synthetic_response.body)
    log = simulated_real_path(monkeypatch, response)
    got = r2b.run_fixed_real_get(operator_one_shot_allow=True)
    assert got.status is r2b.R2BStatus.OPERATOR_ENV_GITHUB_ISSUE_OBSERVED_UNBOUND
    assert got.origin_authenticated is False
    assert got.issue.id == issue_data["id"]
    assert log[0][:4] == ("connect", r2b.FIXED_HOST, 443, 3)
    assert log[1][:3] == ("request", "GET", r2b.FIXED_PATH)
    headers = log[1][3]
    assert headers == {
        "Host": "api.github.com",
        "User-Agent": "arca-issue-handoff-r2b-read-only-canary",
        "Accept": r2b.MEDIA_TYPE,
        "X-GitHub-Api-Version": r2b.API_VERSION,
        "Accept-Encoding": "identity",
    }
    assert "Authorization" not in headers and "Cookie" not in headers
    assert len([item for item in log if item[0] == "request"]) == 1
    assert log[-1] == ("close",)
    assert all(size <= r2b.CHUNK_SIZE for size in response.read_calls)


def test_SIMULATED_REAL_PATH_no_content_length_chunked_like_success(
    monkeypatch, synthetic_response,
):
    response = FakeHTTPResponse(200, [("Content-Type", "application/json")],
                                synthetic_response.body, dribble=True)
    simulated_real_path(monkeypatch, response)
    got = r2b.run_fixed_real_get(operator_one_shot_allow=True)
    assert got.status is r2b.R2BStatus.OPERATOR_ENV_GITHUB_ISSUE_OBSERVED_UNBOUND
    assert len(response.read_calls) > 4


def test_SIMULATED_REAL_PATH_content_length_oversized_blocks_before_read(
    monkeypatch, synthetic_response,
):
    response = FakeHTTPResponse(200, [
        ("Content-Type", "application/json"),
        ("Content-Length", str(r2b.MAX_TRANSFER_DECODED_BODY + 1)),
    ], synthetic_response.body)
    log = simulated_real_path(monkeypatch, response)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA)
    assert response.read_calls == []
    assert log[-1] == ("close",)


def test_SIMULATED_REAL_PATH_oversize_no_content_length_fails_closed(
    monkeypatch,
):
    response = FakeHTTPResponse(200, [("Content-Type", "application/json")],
                                b"x" * (r2b.MAX_TRANSFER_DECODED_BODY + 1))
    simulated_real_path(monkeypatch, response)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA)


def test_SIMULATED_REAL_PATH_wrong_header_duplicates_caught_before_collapse(
    monkeypatch, synthetic_response,
):
    response = FakeHTTPResponse(200, [
        ("Content-Type", "application/json"),
        ("content-type", "application/json"),
    ], synthetic_response.body)
    simulated_real_path(monkeypatch, response)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA)


def test_SIMULATED_REAL_PATH_redirect_not_followed(monkeypatch):
    response = FakeHTTPResponse(301, [("Location", "https://evil.example/redirect")],
                                b"")
    log = simulated_real_path(monkeypatch, response)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PROVIDER_REDIRECT)
    assert len([x for x in log if x[0] == "request"]) == 1
    assert not response.read_calls


@pytest.mark.parametrize("failure,expected", [
    (socket.gaierror("fake DNS failure"), r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE),
    (ConnectionRefusedError("fake refused"), r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE),
    (ConnectionResetError("fake reset"), r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE),
    (TimeoutError("fake timeout"), r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE),
    (ssl.SSLError("fake certificate"), r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE),
    (http.client.IncompleteRead(b"prefix"), r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE),
    (http.client.BadStatusLine("bad status"), r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    (http.client.LineTooLong("bad header"), r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA),
    (RuntimeError("unexpected transport"), r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE),
])
def test_SIMULATED_REAL_PATH_transport_error_classification(
    monkeypatch, failure, expected,
):
    response = FakeHTTPResponse(200, [("Content-Type", "application/json")],
                                b"", failure=failure)
    simulated_real_path(monkeypatch, response)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True), expected)


@pytest.mark.parametrize("failure,expected", [
    (socket.gaierror("fake DNS failure"), r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE),
    (TimeoutError("fake connect timeout"), r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE),
    (ssl.SSLError("fake handshake"), r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE),
])
def test_SIMULATED_REAL_PATH_constructor_failure_never_retries(
    monkeypatch, failure, expected,
):
    response = FakeHTTPResponse(200, [], b"")
    log = simulated_real_path(monkeypatch, response, expected_failure=failure)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True), expected)
    assert len([x for x in log if x[0] == "connect"]) == 1


def test_SIMULATED_REAL_PATH_insecure_ssl_context_blocks_before_connect(monkeypatch):
    fake_context = type("InsecureContext", (), {
        "check_hostname": False, "verify_mode": ssl.CERT_NONE,
    })()
    calls = []
    def record_if_called(*args, **kwargs):
        calls.append((args, kwargs))
        raise _NetworkForbidden("INSECURE_CONTEXT_REACHED_NETWORK")
    monkeypatch.setattr(r2b.ssl, "create_default_context", lambda: fake_context)
    monkeypatch.setattr(r2b.http.client, "HTTPSConnection", record_if_called)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE)
    assert calls == [], "TLS verification MUST stop before HTTPSConnection"


def test_SIMULATED_REAL_PATH_unsupported_content_encoding_fails(monkeypatch, synthetic_response):
    response = FakeHTTPResponse(200, [
        ("Content-Type", "application/json"), ("Content-Encoding", "gzip"),
    ], synthetic_response.body)
    simulated_real_path(monkeypatch, response)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA)
    assert response.read_calls == []


def test_SIMULATED_REAL_PATH_content_length_truncation_fails_closed(
    monkeypatch, synthetic_response,
):
    response = FakeHTTPResponse(200, [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(synthetic_response.body) + 5)),
    ], synthetic_response.body)
    simulated_real_path(monkeypatch, response)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE)


def test_SIMULATED_REAL_PATH_soft_monotonic_timeout_is_not_hard_guarantee(
    monkeypatch, synthetic_response,
):
    response = FakeHTTPResponse(200, [("Content-Type", "application/json")],
                                synthetic_response.body)
    simulated_real_path(monkeypatch, response)
    moments = iter((0.0, 0.1, 10.1))
    monkeypatch.setattr(r2b.time, "monotonic", lambda: next(moments, 11.0))
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE)
    assert response.read_calls == [r2b.CHUNK_SIZE]


def test_real_path_does_not_export_generic_fetch_or_third_mcp_tool():
    core = (ROOT / "arca_issue_harness" / "server.py").read_text()
    assert core.count("@mcp.tool()") == 2
    source = pathlib.Path(r2b.__file__).read_text()
    assert "file_issue(" not in source
    assert "admit_source(" not in source
    assert "import subprocess" not in source
    assert "os.environ" not in source
    assert "import os" not in source
    assert "source_admission_r1.verify_bundle" not in source
    assert "OPERATOR_ENV_GITHUB_READ_MATCH_UNATTESTED" not in source


# Additional adversarial and real HTTPResponse framing simulations (no sockets).

def test_injected_uninitialised_event_is_closed_blocked():
    event = object.__new__(SyntheticHttpResponse)
    assert_blocked(r2b.evaluate_injected_response(event),
                   r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA)


def test_injected_transport_failure_uninitialised_does_not_escape():
    failure = object.__new__(SyntheticTransportFailure)
    assert_blocked(r2b.evaluate_injected_response(failure),
                   r2b.R2BStatus.BLOCKED_TARGET_INVALID)


def test_caller_owned_header_and_body_mutation_cannot_affect_frozen_copy(
    monkeypatch, synthetic_response, issue_data,
):
    external_headers = {"Content-Type": "application/json"}
    event = replace(synthetic_response, headers=external_headers)
    original = r2b._parse_unbound_issue

    def mutate_after_freeze(body):
        external_headers["Content-Type"] = "text/html"
        external_headers["X-Injected"] = "malicious"
        object.__setattr__(event, "body", b"malicious")
        return original(body)

    monkeypatch.setattr(r2b, "_parse_unbound_issue", mutate_after_freeze)
    assert_synthetic_unbound(r2b.evaluate_injected_response(event), issue_data)


@pytest.mark.parametrize("headers", [
    {"content-type": "application/json", "Content-Type": "application/json"},
    {"content-type": "application/json", "bad:name": "x"},
    {"content-type": "application/json", "X-Test": "\n"},
    {"content-type": "application/json", "X-Test": "\x01"},
    {"content-type": "application/json", "X-Test": "x" * 8193},
    {f"X-Long-{i}": "1" for i in range(65)},
])
def test_untrusted_header_safety_enforced_on_injected(synthetic_response, headers):
    got = r2b.evaluate_injected_response(replace(synthetic_response, headers=headers))
    assert_blocked(got, r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA)


def test_SIMULATED_REAL_PATH_too_many_raw_headers(monkeypatch, synthetic_response):
    header_pairs = [("Content-Type", "application/json")]
    header_pairs += [(f"X-Test-{i}", "A") for i in range(64)]
    response = FakeHTTPResponse(200, header_pairs, synthetic_response.body)
    simulated_real_path(monkeypatch, response)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA)


def test_SIMULATED_REAL_PATH_malformed_content_length_rejected_before_body_read(
    monkeypatch, synthetic_response,
):
    response = FakeHTTPResponse(200, [
        ("Content-Type", "application/json"),
        ("Content-Length", "-42"),
    ], synthetic_response.body)
    simulated_real_path(monkeypatch, response)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA)
    assert response.read_calls == []


def test_SIMULATED_REAL_PATH_exact_length_matches(monkeypatch, synthetic_response):
    response = FakeHTTPResponse(200, [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(synthetic_response.body))),
    ], synthetic_response.body)
    simulated_real_path(monkeypatch, response)
    assert r2b.run_fixed_real_get(
        operator_one_shot_allow=True
    ).status is r2b.R2BStatus.OPERATOR_ENV_GITHUB_ISSUE_OBSERVED_UNBOUND


def test_SIMULATED_REAL_PATH_pr_like_response_blocked(monkeypatch, issue_data):
    payload = dict(issue_data, pull_request=None, node_id="PR_example")
    response = FakeHTTPResponse(200, [("Content-Type", "application/json")],
                                dump(payload))
    simulated_real_path(monkeypatch, response)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PR_NOT_ISSUE)


class _FakeSocketFromBytes:
    def __init__(self, data: bytes):
        self.data = data

    def makefile(self, mode: str):
        import io
        assert mode == "rb"
        return io.BytesIO(self.data)


def _http_response_from_raw_bytes(raw: bytes):
    response = http.client.HTTPResponse(_FakeSocketFromBytes(raw))
    response.begin()
    return response


def test_SIMULATED_REAL_PATH_actual_httpresponse_chunked_decoding(
    monkeypatch, synthetic_response,
):
    body = synthetic_response.body
    mid = len(body) // 2
    encoded = (
        b"HTTP/1.1 200 OK\r\n"
        b"Transfer-Encoding: chunked\r\n"
        b"Content-Type: application/json\r\n\r\n"
        + ("%x\r\n" % mid).encode() + body[:mid] + b"\r\n"
        + ("%x\r\n" % (len(body) - mid)).encode() + body[mid:] + b"\r\n"
        + b"0\r\n\r\n"
    )
    response = _http_response_from_raw_bytes(encoded)
    simulated_real_path(monkeypatch, response)
    got = r2b.run_fixed_real_get(operator_one_shot_allow=True)
    assert got.status is r2b.R2BStatus.OPERATOR_ENV_GITHUB_ISSUE_OBSERVED_UNBOUND
    assert got.issue.response_sha256 == hashlib.sha256(body).hexdigest()
    assert got.origin_authenticated is False


def test_SIMULATED_REAL_PATH_malformed_chunk_framing_fails_closed(
    monkeypatch,
):
    encoded = (
        b"HTTP/1.1 200 OK\r\n"
        b"Transfer-Encoding: chunked\r\n"
        b"Content-Type: application/json\r\n\r\n"
        b"ZZNOTHEX\r\n"
    )
    response = _http_response_from_raw_bytes(encoded)
    simulated_real_path(monkeypatch, response)
    result = r2b.run_fixed_real_get(operator_one_shot_allow=True)
    assert result.status in (
        r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA,
        r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE,
    )
    assert result.issue is None


def test_real_and_fake_use_same_closed_non_200_classes(monkeypatch):
    bad = FakeHTTPResponse(403, [("X-RateLimit-Remaining", "0")], b"")
    simulated_real_path(monkeypatch, bad)
    real = r2b.run_fixed_real_get(operator_one_shot_allow=True)
    synthetic = r2b.evaluate_injected_response(
        SyntheticHttpResponse(403, {"X-RateLimit-Remaining": "0"}, b"")
    )
    assert_blocked(real, r2b.R2BStatus.BLOCKED_PROVIDER_RATE_LIMIT)
    assert_blocked(synthetic, r2b.R2BStatus.BLOCKED_PROVIDER_RATE_LIMIT)


# P2 reviewer corrections: validate real stdlib read1 dribble and hard
# test-sentry failure rather than only the behaviour of a toy fake.read.

def test_SIMULATED_REAL_PATH_network_sentry_exception_is_not_swallowed(
    monkeypatch,
):
    secure_context = type("FakeSecureContext", (), {
        "check_hostname": True, "verify_mode": ssl.CERT_REQUIRED,
    })()
    monkeypatch.setattr(r2b.ssl, "create_default_context", lambda: secure_context)
    # HTTPSConnection remains the _NetworkForbidden autouse sentry.
    with pytest.raises(_NetworkForbidden, match="NETWORK_FORBIDDEN"):
        r2b.run_fixed_real_get(operator_one_shot_allow=True)


class _DribbleReader:
    """A socket-like io.RawIOBase reader returning exactly one body byte per
    underlying system-call simulation; emits the header in one operation."""
    def __init__(self, payload: bytes, header_len: int, clock: list[float]):
        import io
        self.data = payload
        self.header_len = header_len
        self.pos = 0
        self.clock = clock
        self.body_reads = 0

    def readable(self):
        return True

    def readinto(self, buffer):
        if self.pos >= len(self.data):
            return 0
        if self.pos < self.header_len:
            n = min(len(buffer), self.header_len - self.pos)
        else:
            n = 1
            self.body_reads += 1
            self.clock[0] += 0.75
        buffer[:n] = self.data[self.pos:self.pos+n]
        self.pos += n
        return n


class _DribbleSock:
    def __init__(self, raw):
        self.raw = raw

    def makefile(self, mode):
        import io
        assert mode == "rb"
        class Adapter(io.RawIOBase):
            def readable(self):
                return True
            def readinto(self, buffer):
                return raw.readinto(buffer)
        raw = self.raw
        return io.BufferedReader(Adapter(), buffer_size=8192)


def test_SIMULATED_REAL_PATH_actual_httpresponse_dribble_uses_read1_and_soft_deadline(
    monkeypatch, synthetic_response,
):
    # This runs the real HTTPResponse parser against an in-memory fake socket,
    # NOT a real network. read(8192) would internally accumulate hundreds of
    # 1-byte raw reads before returning; read1(8192) yields after one.
    header = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
    clock = [0.0]
    raw = _DribbleReader(header + synthetic_response.body, len(header), clock)
    response = http.client.HTTPResponse(_DribbleSock(raw))
    response.begin()
    simulated_real_path(monkeypatch, response)
    monkeypatch.setattr(r2b.time, "monotonic", lambda: clock[0])
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PROVIDER_UNAVAILABLE)
    assert 10 < raw.body_reads < 30
    assert clock[0] >= r2b.SOFT_ELAPSED_SECONDS


def test_SIMULATED_REAL_PATH_overflow_consumes_at_most_cap_plus_one(monkeypatch):
    response = FakeHTTPResponse(
        200, [("Content-Type", "application/json")],
        b"x" * (r2b.MAX_TRANSFER_DECODED_BODY + 30_000),
    )
    simulated_real_path(monkeypatch, response)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA)
    assert response.pos == r2b.MAX_TRANSFER_DECODED_BODY + 1


def test_SIMULATED_REAL_PATH_transfer_encoding_plus_content_length_is_rejected(
    monkeypatch, synthetic_response,
):
    response = FakeHTTPResponse(200, [
        ("Content-Type", "application/json"),
        ("Transfer-Encoding", "chunked"),
        ("Content-Length", str(len(synthetic_response.body))),
    ], synthetic_response.body)
    simulated_real_path(monkeypatch, response)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA)
    assert response.read_calls == []


def test_SIMULATED_REAL_PATH_unsupported_transfer_encoding_fails(
    monkeypatch, synthetic_response,
):
    response = FakeHTTPResponse(200, [
        ("Content-Type", "application/json"),
        ("Transfer-Encoding", "gzip, chunked"),
    ], synthetic_response.body)
    simulated_real_path(monkeypatch, response)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA)
    assert response.read_calls == []


def test_SIMULATED_REAL_PATH_actual_chunked_overflow_fails_closed(monkeypatch):
    body = b"x" * (r2b.MAX_TRANSFER_DECODED_BODY + 1)
    prefix = (
        b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n"
        b"Content-Type: application/json\r\n\r\n"
    )
    frame = (prefix + ("%x\r\n" % len(body)).encode() + body +
             b"\r\n0\r\n\r\n")
    response = _http_response_from_raw_bytes(frame)
    simulated_real_path(monkeypatch, response)
    assert_blocked(r2b.run_fixed_real_get(operator_one_shot_allow=True),
                   r2b.R2BStatus.BLOCKED_PROVIDER_SCHEMA)


@pytest.mark.parametrize("status,expected", [
    (100, r2b.R2BStatus.BLOCKED_PROVIDER_HTTP_STATUS),
    (103, r2b.R2BStatus.BLOCKED_PROVIDER_HTTP_STATUS),
    (206, r2b.R2BStatus.BLOCKED_PROVIDER_HTTP_STATUS),
])
def test_additional_synthetic_http_statuses_are_not_success(status, expected):
    assert_blocked(r2b.evaluate_injected_response(
        SyntheticHttpResponse(status, {}, b"")
    ), expected)
