---
name: issue-draft-handoff
description: Validate and render standalone read-only Issue drafts against the bundled fictional C02/C03 pinned meeting-room sources through Claude Code's local R6 MCP tools. External source admission is not supported.
---

# Claude Code-only R6 Issue handoff

This skill is **read-only**. It does not authorize GitHub Issues, Tasks, code edits, Human approval, merges, releases or deployment.

## Source binding (fictional C02/C03 only)

- C02 `BP-NC-ROOM-01/r1`: SHA-256 `9fea79e192be88a36db69fc35c8dc396316e51f2d62dd0062b44508e104cf31b`
- C03 `BP-NC-ROOM-ALL/r1`: SHA-256 `359490dfc57c35ecacab938f7a20ff0a48d2f06492fc62cd022340698e0f8abb`

The local server accepts exactly the bundled synthetic source mappings. **Other source IDs are not supported.** Their snapshots and SHA hashes attest to bytes only, not Human authorization or requirement semantics.

## Workflow

1. Use the C02/C03 source mapping above. Read the candidate from the plugin's `harness/fixtures/candidates/` if accessible. Optional source inspection: `harness/fixtures/snapshots/BP-NC-ROOM-ALL__r1.json` or C02 equivalent. Reading plugin files outside the current working directory may require a Claude Code permission prompt; if you cannot access the source, stop rather than inventing it.
2. Invoke the observed Claude Code MCP Tool `mcp__plugin_arca-issue-handoff_arca-issue-harness__validate_issue_draft` with `source_id`, exact `source_sha256` and structured `candidate`. Confirm the MCP tool's actual full name via `/mcp` if your host displays a different prefix.
3. If `status=BLOCKED`, report the finding codes verbatim. Do not call render or silently bypass the failure.
4. If `READY_DRAFT_ONLY`, invoke `mcp__plugin_arca-issue-handoff_arca-issue-harness__render_issue_draft` with the same candidate/source. Compare `candidate_digest` from validate with `candidate_digest` from render, as well as `source_id` and `source_sha256`. When the Markdown is independently processed, recompute SHA-256 and compare it to the returned `markdown_sha256`.
5. Present the full standalone Markdown as **DRAFT_ONLY / not-filed / not-dispatched**. Keep `derived-unconfirmed` ACs conditional; preserve `STOP`/`UNKNOWN` authority revalidation.
6. Never claim a tool was invoked without observing the actual Tool result. Model output alone is not MCP transport proof.

## Important constraints

- MCP server exposes only `validate_issue_draft` and `render_issue_draft`; no filing or approvals.
- Source snapshots and candidates in the bundle are **fictional**. C03 DES-001 is synthesized from DES-002 for structural tests only; it is not a source fixture and not semantic approval.
- Downstream writes require a separate action-specific Human decision; do not use Bash, GitHub or other tools to file an Issue under this skill.
- **No ChatGPT Tunnel integration** or HTTP listener. Loading this local-only candidate must not reconfigure user's installed Plugins or services.
- Runtime: Python 3.11+ with the official MCP SDK v2. Set `ARCA_R6_PYTHON` before launching Claude Code, or ensure a compatible `python3` is in PATH. A transient `CONNECTION_CLOSED` startup notice was observed in operator tests even while the actual tools later returned valid results. Use `/mcp` and actual Tool responses to establish readiness, not the notice alone.
