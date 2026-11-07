"""Operator-only CLI for offline Source Admission R1 (never an MCP tool).

A GitHub capture in a JSON file is *not* authenticated just because an operator
supplies matching SHA-256 values. All output remains inactive and unauthorizing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from source_admission import AdmissionBlocked
from source_admission_r1 import preflight_capture, verify_bundle


def _args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Operator-only offline GitHub Issue capture validation / inactive staging"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "stage"):
        p = sub.add_parser(name, help="Preflight only or stage private, inactive source bundle")
        p.add_argument("--raw-source", type=Path, required=True)
        p.add_argument("--snapshot", type=Path, required=True)
        p.add_argument("--capture", type=Path, required=True)
        p.add_argument("--expected-capture-sha256", required=True)
        p.add_argument("--expected-raw-sha256", required=True)
        p.add_argument("--expected-snapshot-sha256", required=True)
        p.add_argument("--source-id", required=True)
        p.add_argument("--repository", required=True)
        p.add_argument("--issue-number", type=int, required=True)
        p.add_argument("--node-id", required=True)
        p.add_argument("--updated-at", required=True)
        p.add_argument("--registry-root", type=Path, required=True)
    p = sub.add_parser("verify", help="Check already staged bundle without activating it")
    p.add_argument("--registry-root", type=Path, required=True)
    p.add_argument("--source-id", required=True)
    p.add_argument("--current-capture", type=Path)
    p.add_argument("--expected-current-capture-sha256")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _args().parse_args(argv)
    try:
        if args.command == "verify":
            result = verify_bundle(
                registry_root=args.registry_root, source_id=args.source_id,
                current_capture=args.current_capture,
                expected_current_capture_sha256=args.expected_current_capture_sha256,
            )
        else:
            result = preflight_capture(
                raw_source=args.raw_source, curated_snapshot=args.snapshot,
                capture_file=args.capture,
                expected_capture_sha256=args.expected_capture_sha256,
                expected_raw_sha256=args.expected_raw_sha256,
                expected_snapshot_sha256=args.expected_snapshot_sha256,
                source_id=args.source_id, repository=args.repository,
                issue_number=args.issue_number, node_id=args.node_id,
                updated_at=args.updated_at, registry_root=args.registry_root,
                stage=args.command == "stage"
            )
    except AdmissionBlocked as exc:
        print(json.dumps({"status": "BLOCKED", "code": str(exc)}, sort_keys=True))
        return 2
    except (OSError, ValueError, RecursionError) as exc:
        # Do not print filenames, raw issue text or exception content.
        print(json.dumps({"status": "BLOCKED", "code": "OPERATOR_IO_FAILURE"}, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
