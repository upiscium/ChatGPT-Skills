#!/usr/bin/env python3
"""Issue #9: receipt-aware, noninteractive OpenCode runner (no model override).

This is a local process supervisor, not an authorization or cleanup service.
On ambiguous startup it preserves the exact child instead of retrying/killing it.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
from datetime import datetime, timezone

SCHEMA = "arca-headless-receipt-v1"
RUN_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,95}\Z")
SESSION_ID = re.compile(r"ses_[A-Za-z0-9]+\Z")
EVENTS = {"step_start", "step_finish", "text", "tool_use", "error"}
MODEL_EVENTS = {"text", "tool_use"}
MAX_LINE = 1024 * 1024
RECEIPT_UNCERTAIN = 75


def _stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _linux_process_identity(pid: int) -> dict:
    """Retain restart-resistant private process facts for scoped reconciliation."""
    try:
        proc = Path("/proc") / str(pid)
        value = (proc / "stat").read_text()
        fields = value[value.rfind(")") + 2:].split()
        boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        return {"boot_id": boot, "start_ticks": int(fields[19])}
    except (OSError, IndexError, ValueError):
        return {"process_identity": "unavailable"}


def _create_file(path: Path):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    return os.fdopen(fd, "wb", buffering=0)


class Receipt:
    def __init__(self, handle, run_id: str):
        self.handle = handle
        self.run_id = run_id

    def emit(self, event: str, **facts) -> None:
        record = {"schema": SCHEMA, "run_id": self.run_id,
                  "at_utc": _stamp(), "event": event, **facts}
        self.handle.write((json.dumps(record, sort_keys=True) + "\n").encode())
        os.fsync(self.handle.fileno())


def _cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--startup-seconds", type=float, default=20.0)
    parser.add_argument("--runtime-seconds", type=float, default=600.0)
    parser.add_argument("options", nargs=argparse.REMAINDER)
    return parser.parse_args()


def _validate(args: argparse.Namespace) -> list[str]:
    if not RUN_ID.fullmatch(args.run_id):
        raise ValueError("invalid run ID")
    if not 0.1 <= args.startup_seconds <= args.runtime_seconds <= 86400:
        raise ValueError("invalid time bounds")
    root = args.state_root
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise ValueError("private state root must be an existing absolute directory")
    if stat.S_IMODE(root.stat().st_mode) != 0o700 or root.stat().st_uid != os.getuid():
        raise ValueError("private state root must be owned and mode 0700")
    if not args.cwd.is_absolute() or not args.cwd.is_dir() or args.cwd.is_symlink():
        raise ValueError("cwd must be a verified absolute directory")
    if not args.binary.is_absolute() or not args.binary.is_file() or not os.access(args.binary, os.X_OK):
        raise ValueError("OpenCode binary must be a verified absolute executable")
    extra = args.options[1:] if args.options[:1] == ["--"] else args.options
    # Headless reviewer/Task mode and model selection are owned by OpenCode and
    # the calling Issue grant. The supervisor cannot silently broaden either.
    prohibited = {"--auto", "--format", "--model", "-m", "--variant",
                  "--dir", "--continue", "-c", "--session", "-s"}
    if any(value in prohibited or any(value.startswith(k + "=") for k in prohibited if k.startswith("--"))
           for value in extra):
        raise ValueError("unapproved OpenCode control option")
    return list(extra)


def run(args: argparse.Namespace) -> int:
    try:
        extra = _validate(args)
    except ValueError as exc:
        print("launch refused: " + str(exc), file=sys.stderr)
        return 64

    state = args.state_root / args.run_id
    try:
        state.mkdir(mode=0o700, exist_ok=False)
    except FileExistsError:
        print("launch refused: run ID already has durable state; reconcile before retry", file=sys.stderr)
        return 73
    except OSError:
        print("launch refused: cannot create private run state", file=sys.stderr)
        return 73

    with _create_file(state / "receipt.jsonl") as receipt_file:
        receipt = Receipt(receipt_file, args.run_id)
        receipt.emit("launch_intent", cwd=str(args.cwd), executable=str(args.binary),
                     mode="noninteractive-json", stdin="devnull")
        with _create_file(state / "stdout.jsonl") as output, _create_file(state / "stderr.log") as errors:
            try:
                child = subprocess.Popen(
                    [str(args.binary), "run", "--format", "json", *extra],
                    cwd=args.cwd, stdin=subprocess.DEVNULL, stdout=output,
                    stderr=errors, start_new_session=True, shell=False,
                )
            except OSError:
                receipt.emit("spawn_failed")
                return 70
            receipt.emit("process_spawned", pid=child.pid, **_linux_process_identity(child.pid))

        # The captured output is a private regular file, so inspection doesn't
        # consume bytes from the child's stdout or require an interactive pipe.
        started = time.monotonic()
        initialized = False
        session_id = None
        model_started = False
        error_seen = False
        malformed_seen = False
        pending = b""
        total_read = 0
        with (state / "stdout.jsonl").open("rb") as stream:
            while True:
                chunk = stream.read(65536)
                if chunk:
                    total_read += len(chunk)
                    pending += chunk
                    if total_read > 8 * MAX_LINE or len(pending) > MAX_LINE:
                        receipt.emit("output_unbounded_unknown", pid=child.pid)
                        return RECEIPT_UNCERTAIN
                    while b"\n" in pending:
                        line, pending = pending.split(b"\n", 1)
                        try:
                            obj = json.loads(line)
                        except (ValueError, UnicodeError):
                            malformed_seen = True
                            continue  # no event proof from invalid output
                        if type(obj) is not dict or obj.get("type") not in EVENTS:
                            continue
                        if not initialized:
                            receipt.emit("opencode_initialized", source_event=obj["type"])
                            initialized = True
                        observed_id = obj.get("sessionID")
                        if session_id is None and isinstance(observed_id, str) and SESSION_ID.fullmatch(observed_id):
                            session_id = observed_id
                            receipt.emit("session_created", session_id=session_id, source_event=obj["type"])
                        if session_id is not None and observed_id == session_id:
                            if obj["type"] in MODEL_EVENTS and not model_started:
                                receipt.emit("model_started", session_id=session_id,
                                             source_event=obj["type"])
                                model_started = True
                            if obj["type"] == "error":
                                receipt.emit("model_error_observed", session_id=session_id)
                                error_seen = True

                status = child.poll()
                if status is not None:
                    # The child may have finished between the last EOF read
                    # and poll(); drain any bytes flushed at shutdown first.
                    if stream.tell() < os.fstat(stream.fileno()).st_size:
                        continue
                    if pending.strip():
                        malformed_seen = True
                        receipt.emit("trailing_invalid_event_unknown")
                    if status != 0:
                        receipt.emit("exited_failure", exit_code=status,
                                     session_id=session_id)
                        return status if 0 < status < 256 else 70
                    if error_seen or malformed_seen or not session_id or not model_started:
                        receipt.emit("exited_without_verified_completion_unknown",
                                     exit_code=0, session_id=session_id,
                                     model_observed=model_started)
                        return RECEIPT_UNCERTAIN
                    receipt.emit("completed", exit_code=0, session_id=session_id)
                    return 0

                elapsed = time.monotonic() - started
                if session_id is None and elapsed >= args.startup_seconds:
                    receipt.emit("startup_stalled_unknown", pid=child.pid,
                                 elapsed_seconds=round(elapsed, 3),
                                 child_retained=True)
                    return RECEIPT_UNCERTAIN
                if elapsed >= args.runtime_seconds:
                    receipt.emit("runtime_stalled_unknown", pid=child.pid,
                                 session_id=session_id, child_retained=True)
                    return RECEIPT_UNCERTAIN
                time.sleep(0.05)


if __name__ == "__main__":
    sys.exit(run(_cli()))
