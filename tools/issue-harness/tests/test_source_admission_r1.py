"""Isolated R1 operator-only GitHub Issue capture + registry tests.

The fixture is entirely synthetic, NOT a GitHub-authenticated record or human
approval. Tests never call the network, GitHub writer, or installed Claude plugin.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from source_admission import AdmissionBlocked, PROVENANCE_UNVERIFIED  # noqa: E402
from source_admission_r1 import (  # noqa: E402
    CAPTURE_VERSION, STAGE_STATUS, preflight_capture, verify_bundle,
)


def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


@pytest.fixture()
def inputs(tmp_path):
    sample = json.loads((ROOT / "fixtures/snapshots/BP-NC-ROOM-ALL__r1.json").read_text())
    sample["source_id"] = "BP-GH-ISSUE-13/r1"
    sample["approval_provenance"] = PROVENANCE_UNVERIFIED
    # One verified full line per assertion, with questions and impacts explicit.
    lines = [sample["original_goal"]]
    lines.extend(x["text"] for x in sample["source_claims"])
    lines.extend(sample["project_non_goals"])
    for d in sample["human_decisions"]:
        lines.extend((d["question"], d["impact"]))
    body = "\n".join(lines) + "\n"
    raw = tmp_path / "source.txt"
    capture_file = tmp_path / "capture.json"
    snapshot = tmp_path / "snapshot.json"
    registry = tmp_path / "registry"
    registry.mkdir(mode=0o700)
    raw.write_text(body)
    snapshot.write_text(json.dumps(sample, ensure_ascii=False, indent=2) + "\n")
    capture = {
        "schema_version": CAPTURE_VERSION,
        "provider": "github",
        "repository": "upiscium/ChatGPT-Skills",
        "issue_number": 13,
        "node_id": "I_SYNTHETIC_FIXTURE_013",
        "updated_at": "2026-11-07T01:23:45Z",
        "html_url": "https://github.com/upiscium/ChatGPT-Skills/issues/13",
        "api_url": "https://api.github.com/repos/upiscium/ChatGPT-Skills/issues/13",
        "title": "Synthetic room booking issue for offline R1 verification",
        "body": body,
    }
    capture_file.write_text(json.dumps(capture, ensure_ascii=False, sort_keys=True) + "\n")
    kwargs = dict(
        raw_source=raw,
        curated_snapshot=snapshot,
        capture_file=capture_file,
        expected_capture_sha256=digest(capture_file.read_bytes()),
        expected_raw_sha256=digest(raw.read_bytes()),
        expected_snapshot_sha256=digest(snapshot.read_bytes()),
        source_id="BP-GH-ISSUE-13/r1",
        repository="upiscium/ChatGPT-Skills",
        issue_number=13,
        node_id="I_SYNTHETIC_FIXTURE_013",
        updated_at="2026-11-07T01:23:45Z",
        registry_root=registry,
        stage=False,
    )
    return kwargs


def blocked(kwargs, expected_code: str):
    with pytest.raises(AdmissionBlocked) as ex:
        preflight_capture(**kwargs)
    assert str(ex.value) == expected_code


def verify_blocked(kwargs, expected_code: str):
    with pytest.raises(AdmissionBlocked) as ex:
        verify_bundle(**kwargs)
    assert str(ex.value) == expected_code


def save_capture(kwargs, modifier):
    p = kwargs["capture_file"]
    x = json.loads(p.read_text())
    modifier(x)
    p.write_text(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n")
    return kwargs | {"expected_capture_sha256": digest(p.read_bytes())}


def save_snapshot(kwargs, modifier):
    p = kwargs["curated_snapshot"]
    x = json.loads(p.read_text())
    modifier(x)
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + "\n")
    return kwargs | {"expected_snapshot_sha256": digest(p.read_bytes())}


def stage(inputs):
    record = preflight_capture(**(inputs | {"stage": True}))
    assert record["status"] == STAGE_STATUS
    return record, inputs["registry_root"] / "BP-GH-ISSUE-13__r1"


def test_preflight_without_publishing_is_nonactivating(inputs):
    r = preflight_capture(**inputs)
    assert r["status"] == "PREFLIGHT_PASS_NOT_STAGED"
    assert r["origin_authenticated"] is False
    assert r["semantic_approval_verified"] is False
    assert r["activation"] == "NOT_ACTIVE_NOT_PUBLISHED"
    assert r["effect_authority"] == "NONE"
    assert not list(inputs["registry_root"].iterdir())


def test_stage_publishes_private_bundle_but_no_activation(inputs):
    r, entry = stage(inputs)
    assert sorted(x.name for x in entry.iterdir()) == sorted(
        ("capture.json", "raw.txt", "snapshot.json", "receipt.json")
    )
    assert stat.S_IMODE(entry.stat().st_mode) == 0o700
    for p in entry.iterdir():
        assert stat.S_IMODE(p.stat().st_mode) == 0o400
    verified = verify_bundle(registry_root=inputs["registry_root"], source_id=r["source_id"])
    assert verified["status"] == "STAGED_VERIFIED_INACTIVE"
    assert verified["origin_authenticated"] is False
    assert verified["semantic_approval_verified"] is False
    assert verified["snapshot_sha256"] == inputs["expected_snapshot_sha256"]
    assert verified["current_capture_compared"] is False


def test_current_operator_capture_identical_but_not_authenticity(inputs):
    stage(inputs)
    res = verify_bundle(
        registry_root=inputs["registry_root"],
        source_id=inputs["source_id"],
        current_capture=inputs["capture_file"],
        expected_current_capture_sha256=inputs["expected_capture_sha256"],
    )
    assert res["current_capture_compared"] is True
    assert res["origin_authenticated"] is False
    assert res["effect_authority"] == "NONE"


def test_stage_duplicate_id_never_overwrites(inputs):
    stage(inputs)
    blocked(inputs | {"stage": True}, "SOURCE_ALREADY_STAGED")


def test_stage_race_exclusive_creates_one_bundle(inputs):
    def attempt(_):
        try:
            return preflight_capture(**(inputs | {"stage": True}))["status"]
        except AdmissionBlocked as ex:
            return str(ex)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, range(2)))
    assert results.count(STAGE_STATUS) == 1
    assert results.count("SOURCE_ALREADY_STAGED") == 1
    assert verify_bundle(
        registry_root=inputs["registry_root"], source_id=inputs["source_id"]
    )["status"] == "STAGED_VERIFIED_INACTIVE"


def test_wrong_capture_sha_rejected(inputs):
    blocked(inputs | {"expected_capture_sha256": "0" * 64}, "CAPTURE_DRIFT")


def test_wrong_raw_sha_rejected(inputs):
    blocked(inputs | {"expected_raw_sha256": "0" * 64}, "RAW_SOURCE_DRIFT")


def test_wrong_snapshot_sha_rejected(inputs):
    blocked(inputs | {"expected_snapshot_sha256": "0" * 64}, "SNAPSHOT_DRIFT")


def test_capture_body_mismatch_with_local_raw(inputs):
    changed = save_capture(inputs, lambda x: x.update(body=x["body"] + "a new line\n"))
    blocked(changed, "CAPTURE_BODY_MISMATCH")


@pytest.mark.parametrize("arg,value", [
    ("repository", "someone/other"), ("issue_number", 14),
    ("node_id", "I_ANOTHER_ID_987"), ("updated_at", "2026-11-07T02:23:45Z"),
])
def test_operator_pinned_origin_mismatch_rejected(inputs, arg, value):
    blocked(inputs | {arg: value},
            "SOURCE_STALE" if arg == "updated_at" else "PROVIDER_IDENTITY_MISMATCH")


@pytest.mark.parametrize("field,value,code", [
    ("html_url", "https://evil.example/issue/13", "INVALID_PROVIDER_URL"),
    ("api_url", "https://evil.example/api/13", "INVALID_PROVIDER_URL"),
    ("issue_number", True, "INVALID_PROVIDER_IDENTITY"),
    ("issue_number", 0, "INVALID_PROVIDER_IDENTITY"),
    ("node_id", "fake_node", "INVALID_PROVIDER_IDENTITY"),
    ("updated_at", "2026-99-07T00:00:00Z", "INVALID_PROVIDER_REVISION"),
    ("updated_at", "2026-11-07T01:23:45+09:00", "INVALID_PROVIDER_REVISION"),
    ("body", "", "INVALID_CAPTURE_TEXT"),
    ("provider", "github-pr", "CAPTURE_SCHEMA"),
])
def test_invalid_capture_fields_fail_closed(inputs, field, value, code):
    modified = save_capture(inputs, lambda x: x.update({field: value}))
    blocked(modified, code)


def test_capture_unknown_field_rejected(inputs):
    modified = save_capture(inputs, lambda x: x.update({"pull_request": {}}))
    blocked(modified, "CAPTURE_SCHEMA")


def test_capture_duplicate_json_key_rejected(inputs):
    p = inputs["capture_file"]
    p.write_bytes(p.read_bytes().replace(b'"body": ', b'"body": "bad", "body": ', 1))
    blocked(inputs | {"expected_capture_sha256": digest(p.read_bytes())},
            "DUPLICATE_JSON_KEY")


def test_capture_symlink_rejected(inputs, tmp_path):
    link = tmp_path / "capture-link.json"
    link.symlink_to(inputs["capture_file"])
    blocked(inputs | {"capture_file": link}, "INPUT_SYMLINK")


def test_capture_bad_encoding_rejected(inputs):
    p = inputs["capture_file"]
    p.write_bytes(b"\xff\xfe")
    blocked(inputs | {"expected_capture_sha256": digest(p.read_bytes())},
            "INVALID_SNAPSHOT_JSON")


def test_snapshot_fake_human_approval_rejected(inputs):
    changed = save_snapshot(inputs, lambda x: x.update(
        approval_provenance="Human approved; operator-curated lexical transcription; NOT independently verified"
    ))
    blocked(changed, "APPROVAL_PROVENANCE_UNSAFE")


def test_missing_verbatim_human_decision_rejected(inputs):
    changed = save_snapshot(inputs, lambda x: x["human_decisions"][0].update(
        impact="Extra decision text that never appeared in the Issue body"
    ))
    blocked(changed, "UNVERIFIED_SOURCE_QUOTE")


def test_stage_capture_change_postpublication_rejected(inputs):
    _, entry = stage(inputs)
    p = entry / "capture.json"
    p.chmod(0o600)
    p.write_bytes(p.read_bytes() + b" ")
    p.chmod(0o400)
    verify_blocked(dict(registry_root=inputs["registry_root"],
                        source_id=inputs["source_id"]), "STAGED_CAPTURE_DRIFT")


def test_stage_snapshot_change_postpublication_rejected(inputs):
    _, entry = stage(inputs)
    p = entry / "snapshot.json"
    p.chmod(0o600)
    p.write_bytes(p.read_bytes() + b" ")
    p.chmod(0o400)
    verify_blocked(dict(registry_root=inputs["registry_root"],
                        source_id=inputs["source_id"]), "STAGED_SNAPSHOT_DRIFT")


def test_stage_receipt_can_not_forge_authority(inputs):
    _, entry = stage(inputs)
    p = entry / "receipt.json"
    v = json.loads(p.read_text())
    v["semantic_approval_verified"] = True
    p.chmod(0o600)
    p.write_text(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    p.chmod(0o400)
    verify_blocked(dict(registry_root=inputs["registry_root"],
                        source_id=inputs["source_id"]), "REGISTRY_AUTHORITY")


def test_missing_manifest_receipt_blocks(inputs):
    _, entry = stage(inputs)
    (entry / "receipt.json").unlink()
    verify_blocked(dict(registry_root=inputs["registry_root"],
                        source_id=inputs["source_id"]), "STAGED_BUNDLE_INCOMPLETE")


def test_extra_unlisted_file_blocks(inputs):
    _, entry = stage(inputs)
    (entry / "surprise").write_text("payload")
    verify_blocked(dict(registry_root=inputs["registry_root"],
                        source_id=inputs["source_id"]), "STAGED_BUNDLE_INCOMPLETE")


def test_stage_symlinked_receipt_rejected(inputs):
    _, entry = stage(inputs)
    p = entry / "receipt.json"
    p.unlink()
    p.symlink_to(inputs["raw_source"])
    verify_blocked(dict(registry_root=inputs["registry_root"],
                        source_id=inputs["source_id"]), "STAGED_BUNDLE_INVALID")


def test_registry_group_readability_rejected(inputs):
    stage(inputs)
    root = inputs["registry_root"]
    root.chmod(0o750)
    verify_blocked(dict(registry_root=root, source_id=inputs["source_id"]),
                   "TARGET_NOT_PRIVATE_OWNED_DIRECTORY")


def test_entry_group_readability_rejected(inputs):
    _, entry = stage(inputs)
    entry.chmod(0o750)
    verify_blocked(dict(registry_root=inputs["registry_root"],
                        source_id=inputs["source_id"]), "STAGED_DIRECTORY_NOT_PRIVATE")


def test_receipt_file_must_be_mode_0400(inputs):
    _, entry = stage(inputs)
    (entry / "receipt.json").chmod(0o600)
    verify_blocked(dict(registry_root=inputs["registry_root"],
                        source_id=inputs["source_id"]), "STAGED_FILE_NOT_READONLY")


def test_verify_requires_both_current_capture_and_pin(inputs):
    stage(inputs)
    verify_blocked(dict(registry_root=inputs["registry_root"], source_id=inputs["source_id"],
                        current_capture=inputs["capture_file"]), "CURRENT_CAPTURE_PIN_REQUIRED")


def test_current_provider_updated_at_change_is_stale(inputs):
    stage(inputs)
    altered = save_capture(inputs, lambda x: x.update(updated_at="2026-11-07T01:24:45Z"))
    verify_blocked(dict(registry_root=inputs["registry_root"], source_id=inputs["source_id"],
                        current_capture=inputs["capture_file"],
                        expected_current_capture_sha256=altered["expected_capture_sha256"]),
                   "SOURCE_STALE")


def test_current_provider_body_change_same_timestamp_is_stale(inputs):
    stage(inputs)
    altered = save_capture(inputs, lambda x: x.update(body=x["body"] + "more\n"))
    verify_blocked(dict(registry_root=inputs["registry_root"], source_id=inputs["source_id"],
                        current_capture=inputs["capture_file"],
                        expected_current_capture_sha256=altered["expected_capture_sha256"]),
                   "SOURCE_STALE")


def test_current_provider_node_swap_is_blocked(inputs):
    stage(inputs)
    altered = save_capture(inputs, lambda x: x.update(node_id="I_REPLACED_NODE_123"))
    verify_blocked(dict(registry_root=inputs["registry_root"], source_id=inputs["source_id"],
                        current_capture=inputs["capture_file"],
                        expected_current_capture_sha256=altered["expected_capture_sha256"]),
                   "PROVIDER_IDENTITY_MISMATCH")


def test_current_provider_digest_mismatch_is_blocked(inputs):
    stage(inputs)
    verify_blocked(dict(registry_root=inputs["registry_root"], source_id=inputs["source_id"],
                        current_capture=inputs["capture_file"],
                        expected_current_capture_sha256="0"*64), "CAPTURE_DRIFT")


def test_unknown_source_id_is_not_staged(inputs):
    verify_blocked(dict(registry_root=inputs["registry_root"],
                        source_id="BP-GH-UNKNOWN/r1"), "SOURCE_NOT_STAGED")


def test_offline_capture_can_be_forged_and_never_proves_origin(inputs):
    # A malicious operator controls capture, raw source, snapshot, and pins.
    changed = save_capture(inputs, lambda x: x.update(title="Fabricated GitHub title"))
    r = preflight_capture(**changed)
    assert r["status"] == "PREFLIGHT_PASS_NOT_STAGED"
    assert r["origin_authenticated"] is False
    assert r["semantic_approval_verified"] is False


def test_no_new_mcp_tool_or_activation_path():
    from arca_issue_harness.server import build_server
    import inspect
    source = inspect.getsource(build_server)
    assert "def validate_issue_draft(" in source
    assert "def render_issue_draft(" in source
    assert "def admit_" not in source and "def publish_" not in source


def test_operator_cli_preflight_stage_verify_roundtrip(inputs, capsys):
    from operator_source_admission import main
    args = [
        "--raw-source", str(inputs["raw_source"]),
        "--snapshot", str(inputs["curated_snapshot"]),
        "--capture", str(inputs["capture_file"]),
        "--expected-capture-sha256", inputs["expected_capture_sha256"],
        "--expected-raw-sha256", inputs["expected_raw_sha256"],
        "--expected-snapshot-sha256", inputs["expected_snapshot_sha256"],
        "--source-id", inputs["source_id"],
        "--repository", inputs["repository"],
        "--issue-number", str(inputs["issue_number"]),
        "--node-id", inputs["node_id"],
        "--updated-at", inputs["updated_at"],
        "--registry-root", str(inputs["registry_root"]),
    ]
    assert main(["preflight", *args]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "PREFLIGHT_PASS_NOT_STAGED"
    assert main(["stage", *args]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == STAGE_STATUS
    assert main(["verify", "--registry-root", str(inputs["registry_root"]),
                 "--source-id", inputs["source_id"],
                 "--current-capture", str(inputs["capture_file"]),
                 "--expected-current-capture-sha256",
                 inputs["expected_capture_sha256"]]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "STAGED_VERIFIED_INACTIVE"
    assert result["origin_authenticated"] is False
    assert main(["stage", *args]) == 2
    assert json.loads(capsys.readouterr().out)["code"] == "SOURCE_ALREADY_STAGED"


def test_operator_cli_obscures_raw_contents_on_errors(inputs, capsys):
    from operator_source_admission import main
    assert main(["verify", "--registry-root", str(inputs["registry_root"]),
                 "--source-id", inputs["source_id"]]) == 2
    body = capsys.readouterr().out
    assert json.loads(body)["code"] == "SOURCE_NOT_STAGED"
    assert "予約" not in body
    assert str(inputs["registry_root"]) not in body


def revision_inputs(inputs, *, revision=2, updated_at="2026-11-07T01:25:45Z"):
    """Create the next operator-pinned observation for the SAME synthetic Issue."""
    source_id = "BP-GH-ISSUE-13/r" + str(revision)
    record = json.loads(inputs["curated_snapshot"].read_text())
    record["source_id"] = source_id
    inputs["curated_snapshot"].write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n"
    )
    capture = json.loads(inputs["capture_file"].read_text())
    capture["updated_at"] = updated_at
    inputs["capture_file"].write_text(
        json.dumps(capture, ensure_ascii=False, sort_keys=True) + "\n"
    )
    return inputs | {
        "source_id": source_id,
        "expected_snapshot_sha256": digest(inputs["curated_snapshot"].read_bytes()),
        "expected_capture_sha256": digest(inputs["capture_file"].read_bytes()),
        "updated_at": updated_at,
    }


def test_revision_r2_stages_with_strictly_newer_observation(inputs):
    stage(inputs)
    r2 = revision_inputs(inputs)
    prepared = preflight_capture(**(r2 | {"stage": True}))
    assert prepared["status"] == STAGE_STATUS
    assert prepared["source_id"] == "BP-GH-ISSUE-13/r2"
    assert verify_bundle(
        registry_root=inputs["registry_root"],
        source_id="BP-GH-ISSUE-13/r2"
    )["status"] == "STAGED_VERIFIED_INACTIVE"
    assert len(list(inputs["registry_root"].iterdir())) == 2


def test_revision_gap_r3_refused(inputs):
    stage(inputs)
    r3 = revision_inputs(inputs, revision=3)
    blocked(r3, "SOURCE_REVISION_CONFLICT")


def test_revision_r2_with_old_observation_refused(inputs):
    stage(inputs)
    r2 = revision_inputs(inputs, updated_at="2026-11-07T01:23:45Z")
    blocked(r2, "SOURCE_REVISION_CONFLICT")


def test_first_version_must_be_r1(inputs):
    r2 = revision_inputs(inputs)
    blocked(r2, "SOURCE_REVISION_FIRST_MUST_BE_R1")


def test_same_provider_node_new_source_alias_refused(inputs):
    stage(inputs)
    forged = json.loads(inputs["curated_snapshot"].read_text())
    forged["source_id"] = "BP-GH-ALIAS-13/r1"
    inputs["curated_snapshot"].write_text(
        json.dumps(forged, ensure_ascii=False, indent=2) + "\n"
    )
    pins = inputs | {
        "source_id": forged["source_id"],
        "expected_snapshot_sha256": digest(inputs["curated_snapshot"].read_bytes()),
    }
    blocked(pins, "PROVIDER_IDENTITY_ALREADY_BOUND")


def test_same_source_prefix_other_provider_refused(inputs):
    stage(inputs)
    r2 = revision_inputs(inputs)
    altered = save_capture(r2, lambda x: x.update(
        repository="someone/different",
        html_url="https://github.com/someone/different/issues/13",
        api_url="https://api.github.com/repos/someone/different/issues/13",
    ))
    blocked(altered | {"repository": "someone/different"},
            "SOURCE_IDENTITY_CONFLICT")


def test_partial_existing_record_prevents_revision(inputs):
    stage(inputs)
    (inputs["registry_root"] / "BP-GH-ISSUE-13__r1" / "receipt.json").unlink()
    r2 = revision_inputs(inputs)
    blocked(r2, "STAGED_BUNDLE_INCOMPLETE")


def test_r1_registry_is_not_automatically_mcp_active(inputs):
    record, entry = stage(inputs)
    assert entry.exists()
    # Existing R6 MCP looks for BP-...__rN.json at the configured top-level
    # snapshot directory, not in the operator-only private record bundle.
    assert not (inputs["registry_root"] / "BP-GH-ISSUE-13__r1.json").exists()
    assert (entry / "snapshot.json").exists()
    assert record["activation"] == "NOT_ACTIVE_NOT_PUBLISHED"


def test_disposable_sdk_v2_actual_stdio_roundtrip_on_staged_source(inputs, tmp_path):
    import anyio
    from mcp import Client, StdioServerParameters
    import shutil

    record, entry = stage(inputs)
    assert verify_bundle(
        registry_root=inputs["registry_root"], source_id=record["source_id"]
    )["status"] == "STAGED_VERIFIED_INACTIVE"

    # Explicit disposable TEST-ONLY copy; R1 does not expose an activation API.
    test_snapshots = tmp_path / "TEST_ONLY_MCP_SNAPSHOTS"
    test_snapshots.mkdir(mode=0o700)
    filename = record["source_id"].replace("/", "__") + ".json"
    destination = test_snapshots / filename
    shutil.copyfile(entry / "snapshot.json", destination)
    destination.chmod(0o400)
    assert digest(destination.read_bytes()) == record["snapshot_sha256"]

    candidate = json.loads((ROOT / "fixtures/candidates/C03_DES-002_valid.json").read_text())
    config = StdioServerParameters(
        command=sys.executable,
        args=["-B", "-m", "arca_issue_harness.server"],
        cwd=str(ROOT),
        env={
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "PYTHONPATH": str(ROOT),
            "PYTHONDONTWRITEBYTECODE": "1",
            "ARCA_HARNESS_SNAPSHOTS_DIR": str(test_snapshots),
        },
    )

    async def run():
        async with Client(config, read_timeout_seconds=15) as client:
            names = sorted(t.name for t in (await client.list_tools()).tools)
            assert names == ["render_issue_draft", "validate_issue_draft"]
            hashes = []
            for name in ("validate_issue_draft", "render_issue_draft"):
                reply = await client.call_tool(name, {
                    "source_id": record["source_id"],
                    "source_sha256": record["snapshot_sha256"],
                    "candidate": candidate,
                })
                assert not reply.is_error
                body = reply.structured_content
                assert body["valid"] is True and body["status"] == "READY_DRAFT_ONLY"
                assert body["authority"].startswith("none-issued")
                hashes.append(body["candidate_digest"])
                if name == "render_issue_draft":
                    assert body["semantic_approval_verified"] is False
                    assert digest(body["markdown"].encode()) == body["markdown_sha256"]
                    assert "not-filed" in body["markdown"] and "not-dispatched" in body["markdown"]
            assert hashes[0] == hashes[1]
            reject = await client.call_tool("render_issue_draft", {
                "source_id": record["source_id"], "source_sha256": "0"*64,
                "candidate": candidate,
            })
            r = reject.structured_content
            assert r["status"] == "BLOCKED" and r["markdown"] is None
            assert "SOURCE_DRIFT" in [x["code"] for x in r["findings"]]
            missing = await client.call_tool("validate_issue_draft", {
                "source_id": "BP-GH-UNKNOWN/r1",
                "source_sha256": record["snapshot_sha256"],
                "candidate": candidate,
            })
            assert missing.structured_content["status"] == "BLOCKED"
            assert "SOURCE_UNAVAILABLE" in [x["code"] for x in missing.structured_content["findings"]]

    anyio.run(run)
    assert not (inputs["registry_root"] / filename).exists()


def test_registry_receipt_cannot_claim_unrelated_github_url(inputs):
    _, entry = stage(inputs)
    p = entry / "receipt.json"
    value = json.loads(p.read_text())
    value["github_html_url"] = "https://github.com/another/repo/issues/13"
    p.chmod(0o600)
    p.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True,
                            separators=(",", ":")) + "\n")
    p.chmod(0o400)
    verify_blocked(dict(registry_root=inputs["registry_root"],
                        source_id=inputs["source_id"]),
                   "STAGED_PROVIDER_URL_MISMATCH")


def test_parallel_distinct_aliases_same_provider_are_serialized(inputs, tmp_path):
    from threading import Barrier
    from concurrent.futures import ThreadPoolExecutor

    alias_snapshot = tmp_path / "alias-curated.json"
    obj = json.loads(inputs["curated_snapshot"].read_text())
    obj["source_id"] = "BP-GH-ALIAS-13/r1"
    alias_snapshot.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    alias_args = inputs | {
        "source_id": obj["source_id"],
        "curated_snapshot": alias_snapshot,
        "expected_snapshot_sha256": digest(alias_snapshot.read_bytes()),
    }
    barrier = Barrier(2)

    def attempt(kwargs):
        barrier.wait(timeout=5)
        try:
            return preflight_capture(**(kwargs | {"stage": True}))["status"]
        except AdmissionBlocked as exc:
            return str(exc)

    with ThreadPoolExecutor(max_workers=2) as pool:
        out = list(pool.map(attempt, [inputs, alias_args]))
    assert out.count(STAGE_STATUS) == 1
    assert out.count("PROVIDER_IDENTITY_ALREADY_BOUND") == 1
    assert len(list(inputs["registry_root"].iterdir())) == 1
    assert next(inputs["registry_root"].iterdir()).is_dir()


def test_same_repo_issue_with_forged_node_alias_rejected(inputs):
    stage(inputs)
    obj = json.loads(inputs["curated_snapshot"].read_text())
    obj["source_id"] = "BP-GH-OTHER-ALIAS/r1"
    inputs["curated_snapshot"].write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    altered = save_capture(inputs, lambda x: x.update(node_id="I_OTHER_INVENTED_NODE_100"))
    new_args = altered | {
        "source_id": obj["source_id"],
        "node_id": "I_OTHER_INVENTED_NODE_100",
        "expected_snapshot_sha256": digest(inputs["curated_snapshot"].read_bytes()),
    }
    blocked(new_args, "PROVIDER_IDENTITY_ALREADY_BOUND")


def test_deeply_nested_capture_returns_stable_blocked(inputs):
    p = inputs["capture_file"]
    raw = b"[" * 30000 + b"]" * 30000
    p.write_bytes(raw)
    blocked(inputs | {"expected_capture_sha256": digest(raw)}, "INVALID_SNAPSHOT_JSON")


def test_deeply_nested_snapshot_returns_stable_blocked(inputs):
    p = inputs["curated_snapshot"]
    raw = b"[" * 30000 + b"]" * 30000
    p.write_bytes(raw)
    blocked(inputs | {"expected_snapshot_sha256": digest(raw)}, "INVALID_SNAPSHOT_JSON")


def test_oversized_deeply_nested_registry_receipt_returns_stable_blocked(inputs):
    _, entry = stage(inputs)
    p = entry / "receipt.json"
    raw = b"[" * 30000 + b"]" * 30000
    p.chmod(0o600)
    p.write_bytes(raw)
    p.chmod(0o400)
    verify_blocked(
        dict(registry_root=inputs["registry_root"], source_id=inputs["source_id"]),
        "OVERSIZE"
    )


def test_deeply_nested_capture_cli_has_no_traceback_or_paths(inputs, capsys):
    from operator_source_admission import main
    p = inputs["capture_file"]
    raw = b"[" * 30000 + b"]" * 30000
    p.write_bytes(raw)
    command = [
        "preflight",
        "--raw-source", str(inputs["raw_source"]),
        "--snapshot", str(inputs["curated_snapshot"]),
        "--capture", str(p),
        "--expected-capture-sha256", digest(raw),
        "--expected-raw-sha256", inputs["expected_raw_sha256"],
        "--expected-snapshot-sha256", inputs["expected_snapshot_sha256"],
        "--source-id", inputs["source_id"],
        "--repository", inputs["repository"],
        "--issue-number", str(inputs["issue_number"]),
        "--node-id", inputs["node_id"],
        "--updated-at", inputs["updated_at"],
        "--registry-root", str(inputs["registry_root"]),
    ]
    assert main(command) == 2
    result = capsys.readouterr()
    assert json.loads(result.out) == {
        "code": "INVALID_SNAPSHOT_JSON", "status": "BLOCKED"
    }
    assert result.err == ""


def test_invalid_surrogate_body_is_structurally_blocked(inputs):
    p = inputs["capture_file"]
    current = json.loads(p.read_text())
    current["body"] = "\ud800"
    p.write_text(json.dumps(current, ensure_ascii=True, sort_keys=True) + "\n")
    blocked(inputs | {"expected_capture_sha256": digest(p.read_bytes())},
            "INVALID_CAPTURE_TEXT")


def test_bool_github_issue_number_cannot_hide_in_receipt(inputs):
    # Python's True == 1 must not allow forged receipt type (GitHub Issue #1).
    # This sample is Issue #13, so check type rejection independently of value.
    _, entry = stage(inputs)
    p = entry / "receipt.json"
    obj = json.loads(p.read_text())
    obj["github_issue_number"] = True
    p.chmod(0o600)
    p.write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                            separators=(",", ":")) + "\n")
    p.chmod(0o400)
    verify_blocked(dict(registry_root=inputs["registry_root"],
                        source_id=inputs["source_id"]), "REGISTRY_SCHEMA")
