# Arca Issue Handoff — Claude Code-only local plugin preview

Status: **isolated, not installed or published**. This package wraps the source-only R6 MVI merged in `upiscium/ChatGPT-Skills` at commit `ef057d1a64a563cb64bfbf8230e1bbcdad34d8a8`. The GitHub blob comparison was performed externally during staging; the wrapper itself checks SHA-256 file drift rather than proving GitHub provenance.

## Composition and boundaries

- `.claude-plugin/plugin.json`: Claude Code plugin manifest.
- `.mcp.json`: one local stdio MCP server. No ChatGPT Tunnel, HTTP listener or network forwarding.
- `skills/issue-draft-handoff/SKILL.md`: source-bound prompts and Human STOP rules.
- `scripts/run-mcp.sh`: bash launcher with drift checks and explicit SDK v2 prerequisites.
- `harness/`: 21 unchanged R6 source/fixture/test files.
- `manifest.sha256`: SHA-256 list for *only* those 21 harness files.

The manifest detects unexpected additions, removals, or changes under `harness/`, but **is not cryptographic protection against a writer who can edit the manifest itself**. Plugin metadata, script, skill and README are not covered by this manifest. Run local tests with `PYTHONDONTWRITEBYTECODE=1` and the pytest cache provider disabled; generated `__pycache__` files are deliberately rejected as unlisted source until removed from the package. The Python subprocess runs with the OS user's privileges: its read-only MCP *Tools* do not constitute an OS sandbox.

No actual Human approval, issue filing, GitHub write, KAGARI dispatch, release, or Plugin update is supported.

## Runtime requirements (Linux / GNU coreutils)

Python >=3.11 with official MCP Python SDK v2; validated with `mcp==2.3.0`. Ensure `bash` and `sha256sum` are available. This preview has not been validated on macOS or Windows.

Create an isolated Python runtime with `mcp==2.3.0`, then **export** `ARCA_R6_PYTHON=/absolute/path/to/python` in the shell **before starting** Claude. Do not point it at a global Python installation without verifying its SDK dependency.

For an ephemeral developer session only:
```sh
export ARCA_R6_PYTHON=/path/to/isolated/venv/bin/python
claude --plugin-dir /path/to/arca-issue-handoff
```

The plugin loads a private local stdio MCP server. Test discovery with `/mcp` and invoke the bundled skill using `/arca-issue-handoff:issue-draft-handoff` (namespace in the running Claude host may vary). The Tool permission dialog is expected: only grant the two read-only R6 MCP Tools. No need for `claude mcp add`, installed marketplace, or modifying global Claude settings.

When the client shows `CONNECTION_CLOSED`, check `/mcp` and the server launcher stderr for `exit 12` diagnostics; inspect the isolated Python SDK and file SHA checks. In the bounded Adam CLI test, a transient startup notice appeared but the explicit Tool calls succeeded. Do not infer success from the notice alone.

## Limits

Only fictional C02/C03 snapshot source mappings are provided. For real source admission, specify a new reviewed contract and get Human approval for any writer path first. Source SHA equality is not Human approval or semantic acceptance. Claude's text alone is not tool-call evidence.
