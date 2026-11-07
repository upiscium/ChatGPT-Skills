"""R2A synthetic-only tests. No live GitHub access, Plugin updates or authority."""
from dataclasses import replace
import hashlib
import inspect
import json
import pathlib
import stat
import sys
import tempfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from source_admission import PROVENANCE_UNVERIFIED, AdmissionBlocked
from source_admission_r1 import CAPTURE_VERSION, preflight_capture, verify_bundle, _record_bytes
from source_admission_r2a import (
    R2AStatus, SourceTarget, R1BundleBytes, SyntheticHttpResponse,
    SyntheticTransportFailure, evaluate_synthetic,
)

SYNTHETIC_NUMERIC_ISSUE_ID = 900_013
SOURCE_ID = "BP-GH-R2A-TEST/r1"
REPO = "synthetic/fixture-project"
ISSUE_NUMBER = 13
NODE = "I_SYNTHETIC_R2A_987"
UPDATED = "2026-11-07T01:23:45Z"


def dump(value, *, canonical=False):
    if canonical:
        return _record_bytes(value)
    text = json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n"
    try:
        return text.encode("utf-8")
    except UnicodeEncodeError:
        # Valid JSON can contain a lone surrogate via an escaped code point.
        return (json.dumps(value, ensure_ascii=True, sort_keys=True) + "\n").encode("utf-8")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def assert_synthetic(result, expected):
    assert result.status is expected
    assert result.origin_authenticated is False
    assert result.human_approval_verified is False
    assert result.semantic_approval_verified is False
    assert result.effect_authority == "NONE"
    assert result.activation == "NOT_ACTIVE_NOT_PUBLISHED"
    assert result.accepted is (expected is R2AStatus.SYNTHETIC_SOURCE_MATCH_NOT_PROVIDER_OBSERVED)


@pytest.fixture
def example(tmp_path, monkeypatch):
    # R1 schema validation writes ONLY inside this disposable private TMPDIR.
    scratch = tmp_path / "scratch"
    scratch.mkdir(mode=0o700)
    monkeypatch.setattr(tempfile, "tempdir", str(scratch))
    sample = json.loads((ROOT / "fixtures/snapshots/BP-NC-ROOM-ALL__r1.json").read_text())
    sample["source_id"] = SOURCE_ID
    sample["approval_provenance"] = PROVENANCE_UNVERIFIED
    lines = [sample["original_goal"]]
    lines.extend(x["text"] for x in sample["source_claims"])
    lines.extend(sample["project_non_goals"])
    for item in sample["human_decisions"]:
        lines += [item["question"], item["impact"]]
    body = "\n".join(lines) + "\n"
    raw = body.encode()
    snapshot = dump(sample)
    title = "Synthetic Issue: safe offline requirements"
    capture = dict(
        schema_version=CAPTURE_VERSION, provider="github", repository=REPO,
        issue_number=ISSUE_NUMBER, node_id=NODE, updated_at=UPDATED,
        html_url=f"https://github.com/{REPO}/issues/{ISSUE_NUMBER}",
        api_url=f"https://api.github.com/repos/{REPO}/issues/{ISSUE_NUMBER}",
        title=title, body=body,
    )
    root = tmp_path / "registry"
    root.mkdir(mode=0o700)
    original = {
        "capture_file": tmp_path / "capture.json",
        "raw_source": tmp_path / "raw.txt",
        "curated_snapshot": tmp_path / "snapshot.json",
    }
    original["capture_file"].write_bytes(dump(capture))
    original["raw_source"].write_bytes(raw)
    original["curated_snapshot"].write_bytes(snapshot)
    kwargs = dict(
        **original, expected_capture_sha256=sha(dump(capture)),
        expected_raw_sha256=sha(raw),
        expected_snapshot_sha256=sha(snapshot),
        source_id=SOURCE_ID, repository=REPO, issue_number=ISSUE_NUMBER,
        node_id=NODE, updated_at=UPDATED, registry_root=root, stage=True,
    )
    assert preflight_capture(**kwargs)["status"] == "STAGED_INACTIVE_OPERATOR_REVIEW_REQUIRED"
    entry = root / SOURCE_ID.replace("/", "__")
    bundle = R1BundleBytes(
        source_id=SOURCE_ID, capture=(entry / "capture.json").read_bytes(),
        raw=(entry / "raw.txt").read_bytes(), snapshot=(entry / "snapshot.json").read_bytes(),
        receipt=(entry / "receipt.json").read_bytes(),
    )
    target = SourceTarget(
        repository_full_name=REPO, issue_number=ISSUE_NUMBER,
        expected_issue_id=SYNTHETIC_NUMERIC_ISSUE_ID,
        expected_node_id=NODE, expected_updated_at=UPDATED,
        expected_title=title, expected_body_sha256=sha(raw),
        source_id=SOURCE_ID,
    )
    response = dict(
        id=SYNTHETIC_NUMERIC_ISSUE_ID, number=ISSUE_NUMBER, node_id=NODE,
        state="open", repository_url=f"https://api.github.com/repos/{REPO}",
        url=capture["api_url"], html_url=capture["html_url"],
        title=title, body=body, updated_at=UPDATED,
    )
    event = SyntheticHttpResponse(
        status=200, headers={"Content-Type": "application/json; charset=utf-8"},
        body=dump(response),
    )
    assert verify_bundle(registry_root=root, source_id=SOURCE_ID)["status"] == "STAGED_VERIFIED_INACTIVE"
    assert not list(scratch.iterdir())
    return dict(target=target, bundle=bundle, response=response,
                event=event, root=root, entry=entry, scratch=scratch)


def check(example, *, target=None, bundle=None, event=None, expect=None):
    return evaluate_synthetic(
        target if target is not None else example["target"],
        bundle if bundle is not None else example["bundle"],
        event if event is not None else example["event"],
    )


def response_event(example, modifier, headers=None):
    value = example["response"].copy()
    modifier(value)
    return SyntheticHttpResponse(200, headers or {"content-type": "application/json"}, dump(value))


def changed_bundle(example, *, capture=None, raw=None, snapshot=None, receipt=None):
    old = example["bundle"]
    return replace(old,
                   capture=old.capture if capture is None else capture,
                   raw=old.raw if raw is None else raw,
                   snapshot=old.snapshot if snapshot is None else snapshot,
                   receipt=old.receipt if receipt is None else receipt)


def refreshed_bundle(example, *, capture=None, snapshot=None, raw=None):
    old = example["bundle"]
    c = old.capture if capture is None else capture
    s = old.snapshot if snapshot is None else snapshot
    b = old.raw if raw is None else raw
    rec = json.loads(old.receipt)
    rec.update(capture_sha256=sha(c), snapshot_sha256=sha(s), raw_sha256=sha(b))
    return changed_bundle(example, capture=c, raw=b, snapshot=s, receipt=dump(rec, canonical=True))


def put_staged(example, bundle):
    entry = example["entry"]
    for name, value in (("capture.json", bundle.capture), ("raw.txt", bundle.raw),
                        ("snapshot.json", bundle.snapshot), ("receipt.json", bundle.receipt)):
        p = entry / name
        p.chmod(0o600)
        p.write_bytes(value)
        p.chmod(0o400)


def test_positive_is_explicitly_synthetic_and_never_authority(example):
    result = check(example)
    assert_synthetic(result, R2AStatus.SYNTHETIC_SOURCE_MATCH_NOT_PROVIDER_OBSERVED)
    assert list(example["scratch"].iterdir()) == []


def test_legacy_r1_registry_is_not_modified(example):
    entry = example["entry"]
    before = {x.name: (x.read_bytes(), stat.S_IMODE(x.stat().st_mode)) for x in entry.iterdir()}
    check(example)
    after = {x.name: (x.read_bytes(), stat.S_IMODE(x.stat().st_mode)) for x in entry.iterdir()}
    assert after == before
    assert not list(example["scratch"].iterdir())


def test_pr_is_rejected_before_pr_node_id_schema(example):
    event = response_event(example, lambda obj: obj.update(
        pull_request={"url": "https://api.github.com/fixture"}, node_id="PR_SYNTHETIC"
    ))
    assert_synthetic(check(example, event=event), R2AStatus.BLOCKED_PR_NOT_ISSUE)


@pytest.mark.parametrize("field,value,expected", [
    ("id", 999_999, R2AStatus.BLOCKED_SOURCE_IDENTITY),
    ("number", 14, R2AStatus.BLOCKED_SOURCE_IDENTITY),
    ("node_id", "I_WRONG_NODE_001", R2AStatus.BLOCKED_SOURCE_IDENTITY),
    ("repository_url", "https://api.github.com/repos/other/project", R2AStatus.BLOCKED_SOURCE_IDENTITY),
    ("url", "https://api.github.com/repos/other/project/issues/13", R2AStatus.BLOCKED_SOURCE_IDENTITY),
    ("html_url", "https://github.com/other/project/issues/13", R2AStatus.BLOCKED_SOURCE_IDENTITY),
    ("state", "closed", R2AStatus.BLOCKED_PROVIDER_STATE),
    ("title", "Changed title only", R2AStatus.BLOCKED_SOURCE_STALE),
    ("updated_at", "2026-11-07T01:23:46Z", R2AStatus.BLOCKED_SOURCE_STALE),
    ("body", "Changed body only", R2AStatus.BLOCKED_SOURCE_STALE),
])
def test_provider_identity_state_and_stale_fields(example, field, value, expected):
    event = response_event(example, lambda obj: obj.update({field: value}))
    assert_synthetic(check(example, event=event), expected)


@pytest.mark.parametrize("field,value", [
    ("body", None), ("body", ""), ("body", 17),
    ("title", "\ud800"), ("title", "line\u2028boundary"),
    ("title", "bad\u007fchar"), ("body", "raw\u2028control"),
    ("body", "line\x85control"), ("id", True), ("id", -1),
    ("number", True), ("number", -1), ("updated_at", "2026-11-07T01:23:45.000Z"),
    ("updated_at", "2026-11-07T10:23:45+09:00"),
    ("node_id", "PR_123"), ("state", 42),
])
def test_provider_payload_schema_and_text_fail_closed(example, field, value):
    event = response_event(example, lambda obj: obj.update({field: value}))
    assert_synthetic(check(example, event=event), R2AStatus.BLOCKED_PROVIDER_SCHEMA)


@pytest.mark.parametrize("field", ["id","number","node_id","state","repository_url",
                                   "url","html_url","title","body","updated_at"])
def test_required_provider_fields_missing(example, field):
    event = response_event(example, lambda obj: obj.pop(field))
    assert_synthetic(check(example, event=event), R2AStatus.BLOCKED_PROVIDER_SCHEMA)


def test_duplicate_json_keys(example):
    b = example["event"].body
    assert b'"id":' in b
    dupe = b.replace(b'"id":', b'"id": 22, "id":', 1)
    event = replace(example["event"], body=dupe)
    assert_synthetic(check(example, event=event), R2AStatus.BLOCKED_PROVIDER_SCHEMA)


def test_deep_json_and_nonfinite_floats_fail_closed(example):
    for obj in (
        b'{"extra":' + (b'[' * 100) + b'0' + (b']' * 100) + b'}',
        example["event"].body[:-2] + b', "infinite": 1e999}\n',
    ):
        assert_synthetic(check(example, event=replace(example["event"], body=obj)),
                         R2AStatus.BLOCKED_PROVIDER_SCHEMA)


@pytest.mark.parametrize("status,headers,code", [
    (301, {}, R2AStatus.BLOCKED_PROVIDER_REDIRECT),
    (302, {}, R2AStatus.BLOCKED_PROVIDER_REDIRECT),
    (307, {}, R2AStatus.BLOCKED_PROVIDER_REDIRECT),
    (308, {}, R2AStatus.BLOCKED_PROVIDER_REDIRECT),
    (304, {}, R2AStatus.BLOCKED_PROVIDER_NOT_FULL_RESPONSE),
    (401, {}, R2AStatus.BLOCKED_PROVIDER_AUTH),
    (403, {}, R2AStatus.BLOCKED_PROVIDER_AUTH),
    (403, {"x-ratelimit-remaining": "5"}, R2AStatus.BLOCKED_PROVIDER_AUTH),
    (403, {"x-ratelimit-remaining": "0"}, R2AStatus.BLOCKED_PROVIDER_RATE_LIMIT),
    (403, {"Retry-After": "60"}, R2AStatus.BLOCKED_PROVIDER_RATE_LIMIT),
    (403, {"x-ratelimit-remaining": "wrong"}, R2AStatus.BLOCKED_PROVIDER_HTTP_STATUS),
    (404, {}, R2AStatus.BLOCKED_PROVIDER_RESOURCE),
    (410, {}, R2AStatus.BLOCKED_PROVIDER_RESOURCE),
    (429, {}, R2AStatus.BLOCKED_PROVIDER_RATE_LIMIT),
    (500, {}, R2AStatus.BLOCKED_PROVIDER_UNAVAILABLE),
    (503, {}, R2AStatus.BLOCKED_PROVIDER_UNAVAILABLE),
    (599, {}, R2AStatus.BLOCKED_PROVIDER_UNAVAILABLE),
    (204, {}, R2AStatus.BLOCKED_PROVIDER_HTTP_STATUS),
    (400, {}, R2AStatus.BLOCKED_PROVIDER_HTTP_STATUS),
    (422, {}, R2AStatus.BLOCKED_PROVIDER_HTTP_STATUS),
    (451, {}, R2AStatus.BLOCKED_PROVIDER_HTTP_STATUS),
])
def test_synthetic_http_code_table(example, status, headers, code):
    event = SyntheticHttpResponse(status, headers, b"")
    assert_synthetic(check(example, event=event), code)


@pytest.mark.parametrize("kind", ["DNS","CONNECT","TLS","TIMEOUT"])
def test_synthetic_transport_failures_are_not_provider_proof(example, kind):
    assert_synthetic(check(example, event=SyntheticTransportFailure(kind)),
                     R2AStatus.BLOCKED_PROVIDER_UNAVAILABLE)


@pytest.mark.parametrize("headers", [
    {},
    {"Content-Type": "text/html"},
    {"content-type": "application/json; charset=latin1"},
    {"content-type": "application/json; extra=foo"},
    {"content-type": "application/json", "Content-Type": "application/json"},
    {"content-type": "application/json", "content-encoding": "gzip"},
    {"content-type": "application/json", "content-encoding": "br"},
])
def test_invalid_success_headers_blocked(example, headers):
    assert_synthetic(check(example, event=replace(example["event"], headers=headers)),
                     R2AStatus.BLOCKED_PROVIDER_SCHEMA)


def test_header_case_folding_duplicate_applies_for_error_status(example):
    event = SyntheticHttpResponse(403, {"Retry-After": "1", "retry-after": "1"}, b"")
    assert_synthetic(check(example, event=event), R2AStatus.BLOCKED_PROVIDER_SCHEMA)


def test_github_metadata_and_claimed_authentication_never_create_proof(example):
    event = response_event(example, lambda obj: obj.update(
        authenticated=True, x_github_request_id="made-up"
    ), headers={"Content-Type": "application/json", "ETag": 'W/"synthetic"',
                "X-GitHub-Request-Id": "made-up"})
    assert_synthetic(check(example, event=event),
                     R2AStatus.SYNTHETIC_SOURCE_MATCH_NOT_PROVIDER_OBSERVED)
    assert not hasattr(check(example, event=event), "provider_observed_by_host")


@pytest.mark.parametrize("field,value", [
    ("expected_issue_id", True), ("expected_issue_id", 0),
    ("issue_number", True), ("expected_title", "\ud800"),
    ("source_id", "BP-../../bad"), ("required_state", "closed"),
    ("expected_updated_at", "2026-11-07T01:23:45.123Z"),
])
def test_invalid_target_is_closed_blocked(example, field, value):
    target = replace(example["target"], **{field: value})
    assert_synthetic(check(example, target=target), R2AStatus.BLOCKED_TARGET_INVALID)


@pytest.mark.parametrize("field,value", [
    ("expected_issue_id", 999_999),  # Not bound to R1, checked against response.
])
def test_numeric_id_mismatch_is_provider_identity_not_r1_bundle(example, field, value):
    target = replace(example["target"], **{field: value})
    assert_synthetic(check(example, target=target), R2AStatus.BLOCKED_SOURCE_IDENTITY)


@pytest.mark.parametrize("field,value", [
    ("repository_full_name", "other/project"),
    ("issue_number", 16), ("expected_node_id", "I_MISMATCHED_NODE_345"),
    ("expected_updated_at", "2026-11-07T01:23:50Z"),
    ("expected_title", "Different expected title"),
    ("expected_body_sha256", "a" * 64), ("source_id", "BP-GH-OTHER/r1"),
])
def test_target_pins_must_match_r1_bundle_first(example, field, value):
    target = replace(example["target"], **{field: value})
    assert_synthetic(check(example, target=target), R2AStatus.BLOCKED_STAGED_SOURCE)


@pytest.mark.parametrize("field,value", [
    ("capture", bytearray(b"a")), ("raw", memoryview(b"a")),
    ("receipt", "not bytes"), ("snapshot", None),
])
def test_mutable_or_non_byte_bundle_is_input_invalid(example, field, value):
    bundle = replace(example["bundle"], **{field: value})
    assert_synthetic(check(example, bundle=bundle), R2AStatus.BLOCKED_TARGET_INVALID)


@pytest.mark.parametrize("event", [
    SyntheticTransportFailure("made-up"),
    SyntheticHttpResponse(True, {}, b""),
    SyntheticHttpResponse(600, {}, b""),
    SyntheticHttpResponse(200, {"content-type": "\n"}, b""),
    SyntheticHttpResponse(200, {}, bytearray(b"x")),
])
def test_invalid_synthetic_http_event_input(example, event):
    assert_synthetic(check(example, event=event), R2AStatus.BLOCKED_TARGET_INVALID)


def test_oversized_http_response_rejected_before_parse(example):
    event = replace(example["event"], body=b" " * 1_048_577)
    assert_synthetic(check(example, event=event), R2AStatus.BLOCKED_PROVIDER_SCHEMA)


@pytest.mark.parametrize("attack,code", [
    ("authority", R2AStatus.BLOCKED_STAGED_SOURCE),
    ("receipt", R2AStatus.BLOCKED_STAGED_SOURCE),
    ("snapshot_claim", R2AStatus.BLOCKED_STAGED_SOURCE),
    ("snapshot_provenance", R2AStatus.BLOCKED_STAGED_SOURCE),
    ("capture_mismatch", R2AStatus.BLOCKED_STAGED_SOURCE),
    ("capture_control", R2AStatus.BLOCKED_STAGED_SOURCE),
])
def test_self_consistent_bundle_tampering_is_blocked(example, attack, code):
    old = example["bundle"]
    if attack == "authority":
        rec = json.loads(old.receipt)
        rec["semantic_approval_verified"] = True
        bundle = changed_bundle(example, receipt=dump(rec, canonical=True))
    elif attack == "receipt":
        rec = json.loads(old.receipt)
        rec["github_node_id"] = "I_FORGED_ID_123"
        bundle = changed_bundle(example, receipt=dump(rec, canonical=True))
    elif attack.startswith("snapshot_"):
        snapshot = json.loads(old.snapshot)
        if attack == "snapshot_provenance":
            snapshot["approval_provenance"] = "Human approved"
        else:
            snapshot["source_claims"][0]["text"] = "This text is absent from raw Issue"
        bundle = refreshed_bundle(example, snapshot=dump(snapshot))
    else:
        cap = json.loads(old.capture)
        if attack == "capture_mismatch":
            cap["title"] = "Forged stored title"
        else:
            cap["body"] += "\u2028untrusted"
        bundle = refreshed_bundle(example, capture=dump(cap))
    assert_synthetic(check(example, bundle=bundle), code)


@pytest.mark.parametrize("mutation", [
    "approval", "lexical_claim", "snapshot_schema", "capture_control",
    "receipt_auth", "receipt_schema", "body_mismatch",
])
def test_r2a_content_parity_with_real_r1_verifier(example, mutation):
    old = example["bundle"]
    if mutation == "approval":
        value = json.loads(old.snapshot)
        value["approval_provenance"] = "Human approved"
        changed = refreshed_bundle(example, snapshot=dump(value))
    elif mutation == "lexical_claim":
        value = json.loads(old.snapshot)
        value["source_claims"][0]["text"] = "Invented phrase nowhere in source"
        changed = refreshed_bundle(example, snapshot=dump(value))
    elif mutation == "snapshot_schema":
        value = json.loads(old.snapshot)
        value["draft_scope"] = "write-enabled"
        changed = refreshed_bundle(example, snapshot=dump(value))
    elif mutation == "capture_control":
        value = json.loads(old.capture)
        value["body"] += "\u2028phantom"
        changed = refreshed_bundle(example, capture=dump(value))
    elif mutation == "receipt_auth":
        value = json.loads(old.receipt)
        value["origin_authenticated"] = True
        changed = replace(old, receipt=dump(value, canonical=True))
    elif mutation == "receipt_schema":
        value = json.loads(old.receipt)
        value["injected_key"] = True
        changed = replace(old, receipt=dump(value, canonical=True))
    else:
        changed = refreshed_bundle(example, raw=old.raw + b"tail")
    put_staged(example, changed)
    with pytest.raises(AdmissionBlocked):
        verify_bundle(registry_root=example["root"], source_id=SOURCE_ID)
    assert_synthetic(check(example, bundle=changed), R2AStatus.BLOCKED_STAGED_SOURCE)
    assert not list(example["scratch"].iterdir())


def test_valid_content_parity_with_real_r1_verifier(example):
    assert verify_bundle(registry_root=example["root"], source_id=SOURCE_ID)["status"] == "STAGED_VERIFIED_INACTIVE"
    assert_synthetic(check(example), R2AStatus.SYNTHETIC_SOURCE_MATCH_NOT_PROVIDER_OBSERVED)


def test_exact_mcp_tools_unchanged_and_r2a_not_wired():
    from arca_issue_harness.server import build_server
    source = inspect.getsource(build_server)
    assert source.count("@mcp.tool()") == 2
    assert "def validate_issue_draft(" in source
    assert "def render_issue_draft(" in source
    assert "source_admission_r2a" not in source
    r2_source = inspect.getsource(sys.modules[evaluate_synthetic.__module__])
    assert "HOST_OBSERVED" not in r2_source
    assert "provider_observed_by_host" not in r2_source
    assert "subprocess" not in r2_source
    assert "import requests" not in r2_source
    assert "import httpx" not in r2_source
    assert "import socket" not in r2_source
    assert "import urllib" not in r2_source
    assert "os.environ" not in r2_source
    assert "def file_issue(" not in r2_source
    assert "def admit_source(" not in r2_source


def test_long_403_rate_limit_header_cannot_raise_valueerror(example):
    event = SyntheticHttpResponse(
        status=403, headers={"x-ratelimit-remaining": "0" * 8000}, body=b""
    )
    assert_synthetic(check(example, event=event), R2AStatus.BLOCKED_PROVIDER_RATE_LIMIT)


def test_excessive_header_value_is_rejected_as_invalid_input(example):
    event = SyntheticHttpResponse(
        status=403, headers={"x-ratelimit-remaining": "0" * 9000}, body=b""
    )
    assert_synthetic(check(example, event=event), R2AStatus.BLOCKED_TARGET_INVALID)


# ---- Independent-review correction regressions ----

class _ForgedOpen(str):
    def __ne__(self, other):
        return False


def test_required_state_subclass_cannot_accept_closed_issue(example):
    target = replace(example["target"], required_state=_ForgedOpen("open"))
    event = response_event(example, lambda obj: obj.update(state="closed"))
    assert_synthetic(check(example, target=target, event=event),
                     R2AStatus.BLOCKED_TARGET_INVALID)


class _RaisesOnCompare:
    def __ne__(self, other):
        raise RuntimeError("untrusted __ne__ must not execute")


def test_required_state_object_with_custom_comparison_rejected(example):
    target = replace(example["target"], required_state=_RaisesOnCompare())
    assert_synthetic(check(example, target=target), R2AStatus.BLOCKED_TARGET_INVALID)


@pytest.mark.parametrize("field", ["target", "bundle", "response", "failure"])
def test_uninitialized_slotted_instances_return_blocked(example, field):
    types = {
        "target": SourceTarget, "bundle": R1BundleBytes,
        "response": SyntheticHttpResponse, "failure": SyntheticTransportFailure,
    }
    broken = object.__new__(types[field])
    kwargs = {"target": example["target"], "bundle": example["bundle"],
              "event": example["event"]}
    kwargs[{"target": "target", "bundle": "bundle", "response": "event",
            "failure": "event"}[field]] = broken
    result = evaluate_synthetic(**kwargs)
    assert_synthetic(result, R2AStatus.BLOCKED_TARGET_INVALID)


def test_header_mutation_after_capture_is_not_reloaded(example, monkeypatch):
    import source_admission_r2a as module
    external_headers = {"content-type": "application/json"}
    event = replace(example["event"], headers=external_headers)
    verified = module._verify_memory_bundle

    def mutate_external_headers(bundle):
        external_headers["content-type"] = "application/json\r\n"
        external_headers["injected"] = "x"
        return verified(bundle)

    monkeypatch.setattr(module, "_verify_memory_bundle", mutate_external_headers)
    assert_synthetic(check(example, event=event),
                     R2AStatus.SYNTHETIC_SOURCE_MATCH_NOT_PROVIDER_OBSERVED)


def test_authority_result_fields_are_not_settable_by_constructor():
    from source_admission_r2a import EvaluationResult
    with pytest.raises(TypeError):
        EvaluationResult(R2AStatus.SYNTHETIC_SOURCE_MATCH_NOT_PROVIDER_OBSERVED,
                         origin_authenticated=True)
    with pytest.raises(ValueError):
        EvaluationResult("SYNTHETIC_SOURCE_MATCH_NOT_PROVIDER_OBSERVED")


@pytest.mark.parametrize("priority,code", [
    ("bad_bundle_http500", R2AStatus.BLOCKED_STAGED_SOURCE),
    ("bad_bundle_pr", R2AStatus.BLOCKED_STAGED_SOURCE),
    ("bad_target_http500", R2AStatus.BLOCKED_STAGED_SOURCE),
    ("invalid_target_pr", R2AStatus.BLOCKED_TARGET_INVALID),
    ("closed_and_stale", R2AStatus.BLOCKED_PROVIDER_STATE),
])
def test_deterministic_error_precedence(example, priority, code):
    target, bundle, event = example["target"], example["bundle"], example["event"]
    if priority.startswith("bad_bundle"):
        bundle = replace(bundle, raw=bundle.raw + b"tampered")
    if priority.endswith("http500"):
        event = SyntheticHttpResponse(500, {}, b"")
    if priority.endswith("_pr"):
        event = response_event(example, lambda x: x.update(pull_request={}))
    if priority == "bad_target_http500":
        target = replace(target, expected_body_sha256="a" * 64)
    if priority == "invalid_target_pr":
        target = replace(target, issue_number=True)
    if priority == "closed_and_stale":
        event = response_event(example, lambda x: x.update(
            state="closed", body="changed body", updated_at="2026-11-07T01:23:50Z"
        ))
    assert_synthetic(check(example, target=target, bundle=bundle, event=event), code)


@pytest.mark.parametrize("mutation", [
    "noncanonical_receipt", "duplicate_receipt_key", "nonfinite_receipt",
    "bool_issue", "receipt_bad_status", "capture_extra_key", "raw_digest_drift",
    "receipt_oversized", "capture_surrogate", "capture_digest_drift",
])
def test_additional_r1_content_rejection_parity(example, mutation):
    old = example["bundle"]
    if mutation == "noncanonical_receipt":
        changed = replace(old, receipt=old.receipt + b" ")
    elif mutation == "duplicate_receipt_key":
        original = old.receipt
        assert b'"status":' in original
        changed = replace(old, receipt=original.replace(
            b'"status":', b'"status":"bad","status":', 1
        ))
    elif mutation == "nonfinite_receipt":
        original = old.receipt
        assert b'"github_issue_number":13' in original
        changed = replace(old, receipt=original.replace(
            b'"github_issue_number":13', b'"github_issue_number":1e999', 1
        ))
    elif mutation in ("bool_issue", "receipt_bad_status"):
        rec = json.loads(old.receipt)
        if mutation == "bool_issue":
            rec["github_issue_number"] = True
        else:
            rec["status"] = "ACTIVATED"
        changed = replace(old, receipt=dump(rec, canonical=True))
    elif mutation == "capture_extra_key":
        cap = json.loads(old.capture)
        cap["unsupported_key"] = "x"
        changed = refreshed_bundle(example, capture=dump(cap))
    elif mutation == "raw_digest_drift":
        rec = json.loads(old.receipt)
        rec["raw_sha256"] = "0" * 64
        changed = replace(old, receipt=dump(rec, canonical=True))
    elif mutation == "receipt_oversized":
        changed = replace(old, receipt=old.receipt + b" " * 20000)
    elif mutation == "capture_surrogate":
        cap = json.loads(old.capture)
        cap["title"] = "\ud800"
        forged_json = (json.dumps(cap, ensure_ascii=True, sort_keys=True) + "\n").encode()
        changed = refreshed_bundle(example, capture=forged_json)
    else:
        changed = replace(old, capture=old.capture + b" ")
    put_staged(example, changed)
    with pytest.raises((AdmissionBlocked, ValueError, TypeError, OverflowError,
                        RecursionError)):
        verify_bundle(registry_root=example["root"], source_id=SOURCE_ID)
    assert_synthetic(check(example, bundle=changed), R2AStatus.BLOCKED_STAGED_SOURCE)
    assert not list(example["scratch"].iterdir())


@pytest.mark.parametrize("kind", ["capture", "receipt"])
def test_deeply_nested_registry_json_is_blocked(kind, example):
    raw = b'{"x":' * 1000 + b'0' + b'}' * 1000
    bundle = replace(example["bundle"], **{kind: raw})
    assert_synthetic(check(example, bundle=bundle), R2AStatus.BLOCKED_STAGED_SOURCE)


def test_valid_provider_body_with_deep_unrelated_field_blocks_at_depth(example):
    event_body = example["response"].copy()
    nested = 1
    for _ in range(70):
        nested = {"nest": nested}
    event_body["deep_extra"] = nested
    assert_synthetic(check(example, event=replace(
        example["event"], body=dump(event_body)
    )), R2AStatus.BLOCKED_PROVIDER_SCHEMA)


@pytest.mark.parametrize("headers", [
    {"content-type": "application/json", "\n": "bad"},
    {"content-type": "application/json", "x-a": "\x00"},
    {"content-type": "application/json", "x-a": "\r\n"},
    {"content-type": "application/json", "x-a": "b" * 9000},
    {"x-" + str(i): "ok" for i in range(65)},
])
def test_untrusted_header_name_value_and_count_are_bounded(example, headers):
    assert_synthetic(check(example, event=replace(example["event"], headers=headers)),
                     R2AStatus.BLOCKED_TARGET_INVALID)


@pytest.mark.parametrize("content_type", [
    "application/json\u2028", "application/json\x85", "application/json\r\n",
    "application/j\u017fon",
])
def test_content_type_rejects_unicode_equivalents_and_invisible_separators(example, content_type):
    code = (R2AStatus.BLOCKED_TARGET_INVALID if "\r" in content_type or "\n" in content_type
            else R2AStatus.BLOCKED_PROVIDER_SCHEMA)
    assert_synthetic(check(example, event=replace(example["event"], headers={
        "Content-Type": content_type,
    })), code)
