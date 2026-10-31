# Arca Issue Harness — read-only MCP MVI (experimental)

**State:** source-only experimental prototype; NOT merged, deployed, or installed as a Plugin. This project is a proof-of-concept for [upiscium/ChatGPT-Skills #4](https://github.com/upiscium/ChatGPT-Skills/issues/4), using the five R4-partial cases from the **2026-10-31** Normal Chat evaluation as *structured regression characterizations*. It is **not** a production approval service.

## Scope and guarantees

Two read-only entrypoints exist in the same deterministic core:

- `validate_issue_draft(source_id, source_sha256, candidate)`: validate the structured `DES-*` candidate against a pinned, server-local source snapshot. Returns `READY_DRAFT_ONLY` or `BLOCKED` with machine-readable findings; never claims Human approval.
- `render_issue_draft(...)`: if valid, render self-contained Markdown with pinned goal/source, project non-goals, candidate-level AC status, Human decisions, evidence, **business-rule** revalidation, and a separate **authority** revalidation table for every downstream operation. Otherwise no Markdown is emitted.

The source is **not supplied as a Tool parameter**. The server loads a source JSON from an operator-configured read-only directory and verifies exact SHA-256. Model-authored `confirmed` ACs must **exactly match** a canonical source claim; newly inferred ACs remain `derived-unconfirmed` and require a mapped unresolved Human decision. Required dependencies/business checks may only refer to confirmed ACs. A `derived-unconfirmed` dependency/check can be expressed as *conditional*, never as a binding implementation condition.

Authority checks are not model-authored free text: rendering always expands per-action `STOP`/`UNKNOWN`, Human clearing authority, operation-specific approval requirement, and exact pre-operation revalidation. **No action can become ALLOWED through these Tools.** The output is always `not-filed` / `not-dispatched`.

## Run the standalone core (no dependencies)

Requirements: Python 3.11+. From the extracted directory:

```bash
python make_fixtures.py                    # Rebuilds fictional snapshots and SHA-256 manifest
python -m pytest -q                     # Requires pytest; 37 tests as of this snapshot
python -m arca_issue_harness.cli validate \
  --snapshots-dir fixtures/snapshots \
  --source-id BP-NC-ROOM-01/r1 \
  --source-sha256 0414d0dd845032fa60cc8926cd8ec66b676d7222d4e72d3c47c9c51e9466f335 \
  --candidate fixtures/candidates/C02_DES-002_valid.json
```

SHA-256 values are **byte-oriented** and deliberately change when snapshot file contents change. Read `fixtures/snapshot_digests.json` after regenerating fixtures. `validate` and `render` return JSON; invalid cases exit with status `2`.

For a known problematic case:

```bash
python -m arca_issue_harness.cli validate \
  --snapshots-dir fixtures/snapshots \
  --source-id BP-NC-ROOM-ALL/r1 \
  --source-sha256 8d8d5f9b2a08112ac56ba87946c9d80f3954889c1ed2913b52c615761774d78d \
  --candidate fixtures/candidates/C03_2_DES-003_legacy_partial.json
```

Expected findings: `UNCONFIRMED_BINDING` (the inferred recheck would otherwise be a required dependency/business rule).

## MCP server (Python SDK v2)

Install into an isolated environment (no production installation or network endpoint is configured by this bundle):

```bash
python -m venv .venv
.venv/bin/pip install -e '.[mcp,test]'
export ARCA_HARNESS_SNAPSHOTS_DIR="$PWD/fixtures/snapshots"
.venv/bin/python -m arca_issue_harness.server
```

This starts an **stdio MCP server** exposing exactly two Tools. The adapter targets the current official Python MCP SDK **v2** (`from mcp.server import MCPServer`, `mcp.run("stdio")`). It does not start an HTTP service, hold a GitHub token, or register with ChatGPT. For manual inspection, use MCP Inspector in an isolated setup with `mcp dev arca_issue_harness/server.py` or an equivalent SDK v2 host; use module execution for the documented runtime. This source package was checked with a mock SDK adapter, not a live MCP wire-protocol test. Ensure an SDK v2 install and actual client round-trip are verified before any hosted deployment.

## Regression coverage and comparison limits

| R4 PARTIAL case | Structured characterization | Harness response |
| --- | --- | --- |
| C02_1 DES-002 | Authority revalidation missing Merge/Release/Plugin update | `AUTHORITY_REVALIDATION_GAP` |
| C02_2 DES-002 | Authority revalidation covers only filing/implementation | `AUTHORITY_REVALIDATION_GAP` |
| C03_2 DES-003 | `derived-unconfirmed` recheck reused as mandatory | `UNCONFIRMED_BINDING` |
| C03_3 DES-002 | Pre-action approval/revision checks missing | `AUTHORITY_REVALIDATION_GAP` |
| C03_3 DES-003 | Both missing action checks and derived mandatory recheck | both codes |

These are **manual, source-grounded structured translations** of the five observed failures, not an automatic semantic analysis of the six raw ChatGPT responses. The optional `legacy_revalidation_coverage` field exists **only** for regression-characterization input: if present, the checker requires coverage of every prohibited action. If it is absent, the renderer generates the complete action table from the pinned source. It never assumes that an earlier free-text output was inspected.

The proof-of-concept deliberately makes *false acceptance of inferred rules* harder by requiring exact matches for `confirmed`. This can produce false negatives for legitimate paraphrases and does **not** establish semantic equivalence between a candidate and the original user's intent. Human alignment and actual approval remain outside the model and this mechanical MVI.

## Security and operational boundaries

- The source directory is an **operator-controlled fixture**, not a specification database or approval authority. Even a SHA-256-matched local file does not prove that the Human approved its contents. A future trusted source adapter must attach evidence of the actual approval and revalidate the latest source before writing.
- Both Tools are read-only and there is no `file_approved_issue` or `dispatch_task` operation in this MVI. No KAGARI, MUSUBI, RITSU, OpenCode or GitHub tool is called.
- Reject unknown JSON fields, unverified `confirmed` ACs, missing project decisions, contradictory conditional/mandatory references, source drift, symlinks, invalid identifiers and unsupported data types.
- A structured validator cannot protect a writing workflow if a client can bypass it and call generic GitHub Issue-writing tools. **Future enforcement must sit inside the sole allowed write path** and verify a fresh approval plus exact snapshot and rendered-body digests at the effect boundary. That is deliberately not implemented here.
- Native ChatGPT/MCP UI, remote hosting, authentication, audit logging, rate limiting, live approval receipts, existing KAGARI Task dispatch, PR merge and Plugin deployment are all outside this MVI.

## Recommended integration steps after local validation

1. Independent source/security review and actual SDK v2 in-memory/stdio Tool round-trip on a disposable host.
2. Read-only Arca Plugin adapter: present structured draft data to MCP Tools, observe blocked findings, and keep the exact approved source snapshot separately pinned. Treat `READY_DRAFT_ONLY` as *a draft validation result*, not Human approval.
3. Compare generated standalone bodies against the old C02/C03 cases with a separate actual Normal Chat trial. The pass criterion is that missing project non-goals/action gates and illegal derived-state promotions cannot cross the *handoff* boundary even if the LLM initially emits an incomplete draft.
4. Only by separate authorization, add a guarded Issue-filing operation at the actual GitHub-write boundary. Require exact Human permission, source/Issue revision, body hash and pre-effect revalidation. Preserve existing KAGARI Contract/Task authority; do not rebuild it in this harness.
