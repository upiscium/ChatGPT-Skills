#!/usr/bin/env python3
"""Validate bounded, privately captured KAGARI/OpenCode Session evidence.

No HTTP, credentials, model calls, subprocesses, Session mutation or host effects.
This validates observations; Task/run ownership is verified separately by KAGARI.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import stat
import sys

SESSION = re.compile(r"ses_[A-Za-z0-9]+\Z")
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,95}\Z")
ROLE = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
SCHEMA = "kagari-opencode-observation-v1"
MAX_BYTES = 1024 * 1024


def _receipt(observation_id: str, session_id: str, status: str,
             evidence: list[str], reason: str | None = None,
             model: str | None = None) -> dict:
    result = {
        "schema": "arca-opencode-session-receipt-v1",
        "observation_id": observation_id,
        "session_id": session_id,
        "task_binding": "not_verified_by_observer",
        "source_authenticity": "not_verified_by_observer",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status, "evidence": evidence,
    }
    if reason is not None:
        result["reason"] = reason
    if model is not None:
        result["model_observed"] = model
    return result


def _read_private_file(path: Path, directory: Path) -> dict:
    if not path.is_absolute() or path.is_symlink():
        raise ValueError("evidence file must be an absolute non-symlink file")
    # Lexical is_relative_to() misses aliases through symlinked ancestors or
    # ".." components. Canonicalize both roots before enforcing isolation,
    # and open the resolved target to avoid following the untrusted alias.
    canonical_directory = directory.resolve(strict=True)
    canonical_file = path.resolve(strict=True)
    if canonical_file.is_relative_to(canonical_directory):
        raise ValueError("evidence file must be outside the Product worktree")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    fd = os.open(canonical_file, flags)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) != 0o600
                or info.st_size > MAX_BYTES):
            raise ValueError("evidence file must be owner-private bounded regular file")
        data = os.read(fd, MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("evidence exceeds bound")
    finally:
        os.close(fd)
    doc = json.loads(data)
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise ValueError("invalid observation schema")
    return doc


def _model_observation(messages, agent: str) -> tuple[bool, bool, str | None]:
    if not isinstance(messages, list):
        raise ValueError("invalid message collection")
    started, completed, model = False, False, None
    for msg in messages:
        if not isinstance(msg, dict):
            raise ValueError("invalid message")
        info = msg.get("info")
        if not isinstance(info, dict):
            raise ValueError("invalid message info")
        if info.get("role") != "assistant":
            completed = False
            continue
        if info.get("agent") != agent:
            raise ValueError("assistant agent mismatch")
        completed = False
        provider, model_id = info.get("providerID"), info.get("modelID")
        if not (isinstance(provider, str) and provider
                and isinstance(model_id, str) and model_id):
            continue
        parts = msg.get("parts")
        if not isinstance(parts, list):
            continue
        text = any(isinstance(p, dict) and p.get("type") == "text"
                   and isinstance(p.get("text"), str) and bool(p["text"])
                   for p in parts)
        tool = any(isinstance(p, dict) and p.get("type") == "tool"
                   and isinstance(p.get("tool"), str) and bool(p["tool"])
                   for p in parts)
        if text or tool:
            started = True
            model = provider + "/" + model_id
        if info.get("finish") == "stop" and text and info.get("error") is None:
            completed = True
    return started, completed, model


def observe(args: argparse.Namespace) -> tuple[dict, int]:
    if (not SAFE_ID.fullmatch(args.observation_id)
            or not SESSION.fullmatch(args.session_id)
            or not ROLE.fullmatch(args.agent)
            or not isinstance(args.expected_title, str)
            or not 1 <= len(args.expected_title) <= 128
            or not args.directory.is_absolute() or args.directory.is_symlink()
            or not args.directory.is_dir()):
        return _receipt(args.observation_id, args.session_id, "blocked", [],
                        "invalid_arguments"), 64
    evidence: list[str] = []
    try:
        doc = _read_private_file(args.evidence_file, args.directory)
        health = doc.get("health")
        if not isinstance(health, dict) or health.get("healthy") is not True:
            raise ValueError("unhealthy")
        evidence.append("opencode_initialized")
        session = doc.get("session")
        if (not isinstance(session, dict)
                or session.get("id") != args.session_id
                or session.get("title") != args.expected_title
                or session.get("directory") != str(args.directory)
                or session.get("agent") not in (None, args.agent)):
            return _receipt(args.observation_id, args.session_id, "blocked",
                            evidence, "session_binding_mismatch"), 75
        evidence.append("session_created")
        statuses = doc.get("statuses")
        permissions = doc.get("permissions")
        questions = doc.get("questions")
        if not (isinstance(statuses, dict)
                and isinstance(permissions, list) and isinstance(questions, list)):
            raise ValueError("invalid collections")
        pending = any(isinstance(p, dict) and p.get("sessionID") == args.session_id
                      for p in permissions + questions)
        started, completed, model = _model_observation(doc.get("messages"), args.agent)
        # OpenCode Session.agent may be omitted by some compatible versions.
        # Without it, only actual assistant metadata can establish this role;
        # a Session title alone must never satisfy role acceptance.
        if session.get("agent") is None and not started:
            return _receipt(args.observation_id, args.session_id, "unknown",
                            evidence, "agent_not_observed"), 75
        if started:
            evidence.append("model_started")
        if pending:
            return _receipt(args.observation_id, args.session_id, "awaiting_human",
                            evidence, model=model), 75
        # OpenCode 1.18.35 GET /session/status maps only non-idle Sessions;
        # an absent entry means idle in this API, not missing evidence.
        runtime = statuses.get(args.session_id)
        if runtime is not None and (not isinstance(runtime, dict)
                                    or runtime.get("type") not in ("busy", "idle")):
            raise ValueError("invalid runtime status")
        if isinstance(runtime, dict) and runtime.get("type") == "busy":
            return _receipt(args.observation_id, args.session_id, "running",
                            evidence, model=model), 75
        if started and completed:
            evidence.append("completed")
            return _receipt(args.observation_id, args.session_id, "completed",
                            evidence, model=model), 0
        return _receipt(args.observation_id, args.session_id, "unknown",
                        evidence, "no_verified_completion", model), 75
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
        return _receipt(args.observation_id, args.session_id, "unknown",
                        evidence, "observation_unavailable"), 75


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observation-id", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--expected-title", required=True)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--evidence-file", type=Path, required=True)
    args = parser.parse_args()
    receipt, status = observe(args)
    print(json.dumps(receipt, sort_keys=True, ensure_ascii=True))
    return status


if __name__ == "__main__":
    sys.exit(main())
