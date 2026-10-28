#!/usr/bin/env python3
"""Read-only, bounded OpenCode/KAGARI Session API receipt observer.

Never starts a model, launches a process, writes a Product file or answers Ask.
The caller retains process/Task authority and preserves the returned receipt.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import stat
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

SESSION = re.compile(r"ses_[A-Za-z0-9]+\Z")
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,95}\Z")
ROLE = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
MAX_RESPONSE = 1024 * 1024


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _receipt(run_id: str, session_id: str, status: str, evidence: list[str],
             reason: str | None = None, model: str | None = None) -> dict:
    result = {"schema": "arca-opencode-session-receipt-v1",
              "run_id": run_id, "session_id": session_id,
              "observed_at_utc": datetime.now(timezone.utc).isoformat(),
              "status": status, "evidence": evidence}
    if reason is not None:
        result["reason"] = reason
    if model is not None:
        result["model_observed"] = model
    return result


def _read_secret(path: Path) -> str:
    if not path.is_absolute() or path.is_symlink():
        raise ValueError("credential file not a trusted absolute regular file")
    info = path.stat()
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) != 0o600):
        raise ValueError("credential file requires owner and 0600")
    value = path.read_text().strip()
    if not value or len(value) > 1024 or "\n" in value:
        raise ValueError("invalid credential file")
    return value


def _get(opener, base: str, path: str, directory: str, auth: str):
    url = base + path + "?" + urlencode({"directory": directory})
    req = Request(url, headers={"Authorization": auth, "Accept": "application/json"},
                  method="GET")
    with opener.open(req, timeout=5) as result:
        body = result.read(MAX_RESPONSE + 1)
        if len(body) > MAX_RESPONSE:
            raise ValueError("response exceeds private observation limit")
        return json.loads(body)


def _model_observation(messages, role: str) -> tuple[bool, bool, str | None]:
    if not isinstance(messages, list):
        raise ValueError("unexpected Session message collection")
    started = False
    completed = False
    last_model = None
    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("invalid Session message shape")
        info = message.get("info")
        if not isinstance(info, dict) or info.get("role") != "assistant":
            continue
        if info.get("agent") != role:
            raise ValueError("assistant role binding mismatch")
        # A prior completed turn cannot certify a later unfinished turn.
        completed = False
        provider = info.get("providerID")
        model = info.get("modelID")
        if not (isinstance(provider, str) and provider
                and isinstance(model, str) and model):
            continue
        parts = message.get("parts")
        if not isinstance(parts, list):
            continue
        valid_output = any(isinstance(part, dict)
                           and part.get("type") == "text"
                           and isinstance(part.get("text"), str)
                           and bool(part["text"]) for part in parts)
        valid_tool = any(isinstance(part, dict)
                         and part.get("type") == "tool"
                         and isinstance(part.get("tool"), str)
                         and bool(part["tool"]) for part in parts)
        if valid_output or valid_tool:
            started = True
            last_model = provider + "/" + model
        if info.get("finish") == "stop" and valid_output and info.get("error") is None:
            completed = True
    # A newer user message awaiting model processing makes the previous
    # assistant completion inapplicable to the current Session state.
    if messages and (not isinstance(messages[-1].get("info"), dict)
                     or messages[-1]["info"].get("role") != "assistant"):
        completed = False
    return started, completed, last_model


def observe(args: argparse.Namespace) -> tuple[dict, int]:
    if (not SAFE_ID.fullmatch(args.run_id)
            or not SESSION.fullmatch(args.session_id)
            or not ROLE.fullmatch(args.agent)
            or not isinstance(args.expected_title, str)
            or not 1 <= len(args.expected_title) <= 128
            or not 0 < args.port < 65536
            or not args.directory.is_absolute() or args.directory.is_symlink()
            or not args.directory.is_dir()):
        return _receipt(args.run_id, args.session_id, "blocked", [], "invalid_arguments"), 64
    try:
        secret = _read_secret(args.password_file)
    except (ValueError, OSError):
        return _receipt(args.run_id, args.session_id, "blocked", [], "invalid_credentials"), 64

    base = f"http://127.0.0.1:{args.port}"
    authorization = "Basic " + base64.b64encode(("opencode:" + secret).encode()).decode()
    opener = build_opener(ProxyHandler({}), _NoRedirect())
    path = "/session/" + quote(args.session_id, safe="")
    folder = str(args.directory)
    evidence: list[str] = []
    try:
        health = _get(opener, base, "/global/health", folder, authorization)
        if not isinstance(health, dict) or health.get("healthy") is not True:
            raise ValueError("unhealthy")
        evidence.append("opencode_initialized")
        session = _get(opener, base, path, folder, authorization)
        if (not isinstance(session, dict)
                or session.get("id") != args.session_id
                or session.get("directory") != folder
                or session.get("agent") != args.agent
                or session.get("title") != args.expected_title):
            return _receipt(args.run_id, args.session_id, "blocked", evidence,
                            "session_binding_mismatch"), 75
        evidence.append("session_created")
        statuses = _get(opener, base, "/session/status", folder, authorization)
        messages = _get(opener, base, path + "/message", folder, authorization)
        permissions = _get(opener, base, "/permission", folder, authorization)
        questions = _get(opener, base, "/question", folder, authorization)
        if not (isinstance(statuses, dict) and isinstance(permissions, list)
                and isinstance(questions, list)):
            raise ValueError("invalid observation collection")
        # Other concurrent Sessions' pending Asks are unrelated.
        pending = any(isinstance(v, dict) and v.get("sessionID") == args.session_id
                      for v in permissions + questions)
        started, completed, model = _model_observation(messages, args.agent)
        if started:
            evidence.append("model_started")
        if pending:
            return _receipt(args.run_id, args.session_id, "awaiting_human",
                            evidence, model=model), 75
        runtime = statuses.get(args.session_id)
        if runtime is not None and (not isinstance(runtime, dict)
                                    or runtime.get("type") not in ("busy", "idle")):
            raise ValueError("unknown runtime status")
        if isinstance(runtime, dict) and runtime.get("type") == "busy":
            return _receipt(args.run_id, args.session_id, "running",
                            evidence, model=model), 75
        if started and completed:
            evidence.append("completed")
            return _receipt(args.run_id, args.session_id, "completed",
                            evidence, model=model), 0
        return _receipt(args.run_id, args.session_id, "unknown",
                        evidence, "no_verified_completion", model), 75
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        return _receipt(args.run_id, args.session_id, "unknown",
                        evidence, "observation_unavailable"), 75


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--expected-title", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--password-file", type=Path, required=True)
    args = parser.parse_args()
    receipt, status = observe(args)
    print(json.dumps(receipt, ensure_ascii=True, sort_keys=True))
    return status


if __name__ == "__main__":
    sys.exit(main())
