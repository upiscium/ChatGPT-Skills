# Arca #13 / Source Admission R2A — Offline evaluator contract

Status: **SOURCE_ONLY / LOCAL_UNCOMMITTED / NOT_ACTIVE / NO_PROVIDER_PROOF**.
Reference: R2 D0 FINAL design on Adam, SHA-256
`2e5506198a1b919f28dac3a0b920fd12f6d97b213567142650b76d4c89acab35`.
Baseline: `upiscium/ChatGPT-Skills@e9196d685a37dc2fa3f31a383adac47fe15d08bf`
(merged PR #18). Parent Issue #13 stays OPEN.

## Scope and provenance

This module does **not** contact GitHub, issue HTTP requests, read credentials,
access the source registry, install/activate a Plugin, modify the MCP server,
write a GitHub Issue, or grant any action authority. It consumes **caller-supplied
synthetic** response bytes and a **frozen in-memory copy** of an R1 bundle.
Its only success is `SYNTHETIC_SOURCE_MATCH_NOT_PROVIDER_OBSERVED`, and results
always have `origin_authenticated=false`, `human_approval_verified=false`,
`semantic_approval_verified=false`, `effect_authority=NONE`,
`activation=NOT_ACTIVE_NOT_PUBLISHED`. Synthetic success does not prove
the Issue exists on GitHub or that a Human approved the content.

The source is outside the `arca_issue_harness` package. Existing MCP tools
remain **only** `validate_issue_draft` and `render_issue_draft`. No new
runtime installation, deployment, GitHub reader, read-through cache, Host
attestation, signed proof, Task dispatcher or source activation.

## Input and deterministic checks

`SourceTarget` pins repository (exact case), Issue number, an **explicit
caller-supplied numeric Issue ID** (absent from R1), node ID, timestamp, title,
body digest, source ID, and required state `open`. The Issue ID is a synthetic
test value and is not preapproved, authenticated or hardcoded from Issue #13.
The duplicate fields must match the R1 bundle; conflicts are blocked before
the synthetic HTTP event is considered.

`R1BundleBytes` contains frozen `bytes` for `capture.json`, `raw.txt`,
`snapshot.json`, `receipt.json` and a source ID. An in-memory validator
recreates the content checks from R1: duplicate JSON keys, nonfinite values,
canonical receipt formatting, exact R1 authority flags, R1 envelope fields,
exact hashes, identity/URLs, raw capture-body byte equality, R6 snapshot schema,
unapproved provenance rejection and whole-line lexical binding. The existing
R1 `_json_unique`, `_record_bytes` and `validate_snapshot_against_raw`
are reused. The last function creates a disposable private `0700` scratch
directory via `tempfile`; tests configure an isolated TMPDIR and verify
scratch cleanup. No persistent bundle or receipt is written.

`SyntheticHttpResponse(status, headers, body)` and
`SyntheticTransportFailure(kind)` encode **only test inputs**; they are
not trusted network results. All positive synthetic HTTP responses must have
status 200, Content-Type `application/json` (optional charset=utf-8),
Content-Encoding absent or identity, bounded body (1 MiB), JSON depth <=64,
and required numeric id/Issue number/node ID/state/3 canonical URLs/title/body/
UTC seconds timestamp. An explicit `pull_request` field blocks the response
as a PR, even if its other fields look like an Issue. Comparisons are exact;
there is no Unicode normalization, body trimming or timestamp-based
acceptance of changed content.

`R2AStatus` is a closed enum. Invalid targets/events/types are blocked,
existing R1 integrity/authority failures are blocked, HTTP statuses and
transport failures map to dedicated blocked classes, and source mismatches
produce distinct identity/state/staleness blocks. Header names are matched
case-insensitively, duplicate case-folded names are rejected for all statuses.
For 403, Retry-After takes precedence; then x-ratelimit-remaining=0 means
rate limiting, malformed values produce HTTP_STATUS, otherwise AUTH.
No automatic retry. No status represents provider-origin authentication,
Host authority, a Human approval, or a write grant.

## Explicit R2A exclusions / subsequent gates

* Does not independently authenticate GitHub response provenance, even if a
  caller sends `authenticated=true`, a request ID, ETag or matching SHA-256.
* Does not verify OS file ownership or lock discipline of a registry directory.
  The R2A byte validator also does not check R1 directory inventory, ownership,
  modes 0400/0700, symlinks, revision sequence or cross-source aliases. Those
  remain the path-based R1 registry verifier's responsibility. The R2A
  content verifier is not a cryptographic proof of staging; an operator can
  fabricate a self-consistent R1-like bundle. Parity tests compare content
  allow/deny decisions, not path safety.
* Does not persist provider observations, mutate the R1 receipt, or use the
  R1 `prepare` path to activate snapshots.
* A real fixed GitHub GET adapter, credential limits, redirects, API errors,
  dedicated Host trust boundary, OS isolation and Human action approval are
  **separate** R2B and later-gated work. A live read from Adam's existing
  `gh` session alone is not cryptographic provider attestation.

## Verification and stop

Run isolated synthetic tests with Python 3.12 and 3.13 and MCP SDK v2.3.0.
Include the existing R1/core/stdio test suite (actual MCP SDK v2 stdio checks are owned by the existing test_sdk_v2_stdio_roundtrip.py, not the R2A module tests); exercise table-driven
status and schema failures, self-consistently rehashed tampering,
positive/negative parity with the R1 registry verifier on disposable fixtures,
scratch cleanup and unchanged MCP tools. Independently review the exact
source. Preserve preexisting R1, server, packaging, and installed Plugin
files. Maintain `main` and production untouched.

**STOP:** any need for live GitHub, credentials, R1/MCP edits, third MCP tool,
source registry publication, Plugin update, Task dispatch, Commit/Push/PR,
Ready/Merge, Release, or activation without a subsequent Human grant.

Input-check exceptions are categorized as BLOCKED_TARGET_INVALID, bundle-check / temporary
scratch exceptions as BLOCKED_STAGED_SOURCE, and unexpected synthetic response
parser exceptions as BLOCKED_PROVIDER_SCHEMA. All are fail-closed; none is
an authority decision. R1 scratch allocation failures may be reported under
BLOCKED_STAGED_SOURCE even when the bundle bytes themselves are valid.
