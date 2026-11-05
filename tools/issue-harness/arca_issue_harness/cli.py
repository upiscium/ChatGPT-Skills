"""Deterministic offline CLI using the same core as the MCP adapter."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from .core import Harness


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Arca Issue draft harness")
    parser.add_argument("command", choices=("validate", "render"))
    parser.add_argument("--snapshots-dir", type=Path, required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()
    try:
        candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
        harness = Harness(args.snapshots_dir)
        result = (harness.validate if args.command == "validate" else harness.render)(
            args.source_id, args.source_sha256, candidate)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": type(exc).__name__}, ensure_ascii=False))
        return 2
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
