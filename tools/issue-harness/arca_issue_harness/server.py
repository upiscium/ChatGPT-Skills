"""Optional MCP Python SDK v2 stdio adapter, exposing read-only tools only.

Run from the root with `python -m arca_issue_harness.server` after installing
`mcp>=2,<3`. No writes, external API calls, or execution capability.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from arca_issue_harness.core import Harness


def build_server():
    # Dependency is imported lazily, so the deterministic core needs no SDK.
    from mcp.server import MCPServer  # MCP Python SDK v2, NOT v1 FastMCP

    base = Path(os.environ["ARCA_HARNESS_SNAPSHOTS_DIR"])
    harness = Harness(base)
    mcp = MCPServer("Arca Issue Harness — read-only draft proofing")

    @mcp.tool()
    def validate_issue_draft(source_id: str, source_sha256: str, candidate: dict[str, Any]) -> dict[str, Any]:
        """Validate a structured DES draft against a pinned local source. Never authorizes or files an Issue."""
        return harness.validate(source_id, source_sha256, candidate)

    @mcp.tool()
    def render_issue_draft(source_id: str, source_sha256: str, candidate: dict[str, Any]) -> dict[str, Any]:
        """Render complete, deterministic Markdown only after structural validation; remains not-filed/not-dispatched."""
        return harness.render(source_id, source_sha256, candidate)

    return mcp


def main() -> None:
    build_server().run("stdio")


if __name__ == "__main__":
    main()
