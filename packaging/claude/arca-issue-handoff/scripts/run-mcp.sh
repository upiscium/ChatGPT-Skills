#!/usr/bin/env bash
# Claude Code local MCP transport only; no Tunnel/Plugin publication.
set -euo pipefail
umask 077
export PYTHONNOUSERSITE=1
export PYTHONDONTWRITEBYTECODE=1
ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
HARNESS="$ROOT/harness"
if [[ ! -f "$ROOT/manifest.sha256" || ! -f "$HARNESS/arca_issue_harness/server.py" ]]; then
  echo "R6 plugin package or source manifest missing" >&2
  exit 12
fi
# This is an accidental-drift check, not tamper-proof signature verification.
# Detect both modified/missing listed files AND unexpected new source files.
cd "$ROOT"
if ! diff -u <(awk '{print $2}' manifest.sha256 | LC_ALL=C sort) <(find harness -type f -print | LC_ALL=C sort) >/dev/null; then
  echo "R6 unlisted/missing source files" >&2
  exit 12
fi
sha256sum -c --status manifest.sha256 || { echo "R6 packaged-source digest mismatch" >&2; exit 12; }
PY="${ARCA_R6_PYTHON:-python3}"
if ! "$PY" -B -c 'from mcp.server import MCPServer;import importlib.metadata as m,sys;v=m.version("mcp");assert v.split(".",1)[0]=="2" and sys.version_info>=(3,11)' ; then
  echo "R6 requires Python >=3.11 and working official MCP SDK v2" >&2
  exit 12
fi
# No automatic authority or remote credential propagation.
unset OPENAI_API_KEY OPENAI_ADMIN_KEY CONTROL_PLANE_API_KEY ANTHROPIC_API_KEY GH_TOKEN GITHUB_TOKEN
export PYTHONPATH="$HARNESS"
export ARCA_HARNESS_SNAPSHOTS_DIR="$HARNESS/fixtures/snapshots"
cd "$HARNESS"
exec "$PY" -B -m arca_issue_harness.server
