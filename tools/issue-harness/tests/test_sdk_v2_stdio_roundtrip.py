"""Optional genuine MCP Python SDK v2 subprocess stdio integration test.

Install: python -m pip install -e '.[test,mcp]'
Run:     python -m pytest -q tests/test_sdk_v2_stdio_roundtrip.py

Synthetic fictional fixture only. No GitHub writes, KAGARI, Plugin,
ChatGPT Normal Chat, Tunnel, or actual Human approval.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import importlib.metadata
import json
import os
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures"
SOURCE_ID = "BP-NC-ROOM-ALL/r1"


def _candidate(name: str) -> dict:
    return json.loads((FIX / "candidates" / name).read_text(encoding="utf-8"))


def test_real_sdk_v2_stdio_six_calls_and_negative_boundaries() -> None:
    pytest.importorskip("mcp", reason="optional MCP Python SDK v2 dependency")
    version = importlib.metadata.version("mcp")
    if int(version.split(".", 1)[0]) != 2:
        pytest.skip("requires the official MCP Python SDK v2")

    import anyio
    from mcp import Client, StdioServerParameters

    digest = json.loads((FIX / "snapshot_digests.json").read_text())[
        SOURCE_ID
    ]
    c2 = _candidate("C03_DES-002_valid.json")
    c3 = _candidate("C03_DES-003_valid.json")
    c1 = deepcopy(c2)
    c1["id"] = "DES-001"
    c1["title"] = "本人名義の予約作成"
    for ac in c1["acceptance_criteria"]:
        ac["id"] = ac["id"].replace("AC-002-", "AC-001-")
    for dep in c1["dependencies"]:
        dep["ac_refs"] = [
            ref.replace("AC-002-", "AC-001-")
            for ref in dep["ac_refs"]
        ]
    # C1 is a structural synthetic fixture; this does not prove semantic
    # adequacy to the user's original goal or Human approval.
    candidates = (c1, c2, c3)

    async def actual_stdio_roundtrip() -> None:
        # Keep auth tokens and unrelated profile settings out of the child.
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "PYTHONPATH": str(ROOT),
            "ARCA_HARNESS_SNAPSHOTS_DIR": str(FIX / "snapshots"),
            "PYTHONNOUSERSITE": "1",
        }
        server = StdioServerParameters(
            command=sys.executable,
            args=["-B", "-m", "arca_issue_harness.server"],
            env=env,
            cwd=str(ROOT),
        )
        results = {}
        async with Client(server, read_timeout_seconds=15.0) as client:
            assert str(client.protocol_version) == "2026-07-28"
            listing = await client.list_tools()
            names = {tool.name for tool in listing.tools}
            assert names == {"validate_issue_draft", "render_issue_draft"}
            assert listing.next_cursor is None

            for name in ("validate_issue_draft", "render_issue_draft"):
                for candidate in candidates:
                    receipt = await client.call_tool(name, {
                        "source_id": SOURCE_ID,
                        "source_sha256": digest,
                        "candidate": candidate,
                    })
                    assert receipt.is_error is False
                    reply = receipt.structured_content
                    assert isinstance(reply, dict), (name, candidate["id"])
                    assert reply["status"] == "READY_DRAFT_ONLY"
                    assert reply["valid"] is True
                    if name == "render_issue_draft":
                        markdown = reply["markdown"]
                        assert reply.get("semantic_approval_verified") is False
                        assert "not-filed" in markdown
                        assert "not-dispatched" in markdown
                        assert sha256(markdown.encode()).hexdigest() == reply["markdown_sha256"]
                    results.setdefault(candidate["id"], set()).add(name)
            assert len(results) == 3
            assert all(
                used == {"validate_issue_draft", "render_issue_draft"}
                for used in results.values()
            )

            # Drifted source does not generate a standalone Issue draft.
            drift = await client.call_tool("render_issue_draft", {
                "source_id": SOURCE_ID,
                "source_sha256": "0" * 64,
                "candidate": c2,
            })
            assert not drift.is_error
            drift_body = drift.structured_content
            assert drift_body and drift_body["status"] == "BLOCKED"
            assert drift_body["markdown"] is None
            assert drift_body["markdown_sha256"] is None

            # Validate must reject the same drift; rendering is not special.
            drift_validation = await client.call_tool("validate_issue_draft", {
                "source_id": SOURCE_ID,
                "source_sha256": "0" * 64,
                "candidate": c2,
            })
            assert not drift_validation.is_error
            validation_body = drift_validation.structured_content
            assert validation_body and validation_body["status"] == "BLOCKED"

            # An unrecognized source ID must not grant access to other paths.
            wrong_source = await client.call_tool("render_issue_draft", {
                "source_id": "../../injected",
                "source_sha256": digest,
                "candidate": c2,
            })
            assert not wrong_source.is_error
            wrong_body = wrong_source.structured_content
            assert wrong_body and wrong_body["status"] == "BLOCKED"
            assert wrong_body["markdown"] is None

            # Model-supplied "approved" fields do not grant Human authority.
            forged = deepcopy(c2)
            forged["approval_override"] = "file now"
            rejected = await client.call_tool("render_issue_draft", {
                "source_id": SOURCE_ID,
                "source_sha256": digest,
                "candidate": forged,
            })
            assert not rejected.is_error
            rejected_body = rejected.structured_content
            assert rejected_body and rejected_body["status"] == "BLOCKED"
            assert rejected_body["markdown"] is None
            assert any(
                finding["code"] == "UNKNOWN_FIELD"
                for finding in rejected_body["findings"]
            )

            # Human approval revalidation is an authority STOP condition, not
            # a candidate-controlled flag that can be set to True.
            forged_human = deepcopy(c2)
            forged_human["human_action_approval"] = True
            human_reply = await client.call_tool("render_issue_draft", {
                "source_id": SOURCE_ID,
                "source_sha256": digest,
                "candidate": forged_human,
            })
            assert not human_reply.is_error
            human_body = human_reply.structured_content
            assert human_body and human_body["status"] == "BLOCKED"
            assert human_body["markdown"] is None
            assert any(x["code"] == "UNKNOWN_FIELD" for x in human_body["findings"])

    anyio.run(actual_stdio_roundtrip)
