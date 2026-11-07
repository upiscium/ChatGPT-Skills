# Arca #13 — Source Admission R1: GitHub Issue offline capture and inactive registry

Status: **source-only R1 implementation tracked in Draft PR #18; not merged or activated**. Separate Human authorization is required before any correction Commit, Push, PR update, Ready, Merge, Plugin update, source activation, real Issue filing, Task dispatch, Release or Tunnel change.

## Purpose

Extend the R0 operator-only, deterministic read-only source preflight with a narrowly-scoped **GitHub Issue capture binding and versioned Source Registry**, without introducing a third MCP Tool or write authority. Source-based standalone Issue drafts remain **DRAFT_ONLY / not-filed / not-dispatched**. The R6 MCP Core `arca_issue_harness` is untouched.

Only a human-operated local CLI can prepare a capture/registry. An LLM does not choose arbitrary URLs or local paths through MCP. The *installed* Claude Plugin remains pinned to fictional C02/C03 and is **not** modified or activated by this work.

## Trust and authority (non-negotiable)

1. **Operator-supplied evidence is not provider authenticity.** An offline JSON file, `node_id`, `updated_at`, URL, ETag, SHA-256 or locally generated receipt can be entirely fabricated by a same-user operator. R1 checks coherence and exact bytes; it **does not contact GitHub**. All outputs keep `origin_authenticated=false`, `semantic_approval_verified=false` and `effect_authority=NONE`, even when a later local capture matches.
2. **The next Host integration must independently fetch** the canonical provider Issue using an authorized GitHub connector, verify the repository + Issue number + Node ID + exact revision and body SHA-256, and preserve the observed tool request/response evidence. No unverified model response may supply `origin_authenticated=true`. The Host must recheck before activation and at any future effect boundary.
3. **Operator semantic review remains essential.** R0's exact full-line claims/non-goals/Human-decision lexical match prevents some truncations but cannot establish their meaning, contextual negation, omissions, or original Human approval. In particular, a malicious operator can build a matching raw body and capture from the curated snapshot. A verified capture does not turn a model-transcribed requirement into a Human-approved one.
4. **Non-activation by construction.** The registry stores private bundles in its own `BP-...__rN/` directories. The active R6 `Harness` searches the root snapshots directory for `BP-...__rN.json`. Registry bundles are **not** in that format. Nothing in R1 switches or edits the running Claude Plugin.
5. **Human write gate is separate.** GitHub Issue filing, KAGARI Task dispatch, code change, Merge, Release, Plugin update and live source activation remain STOP/UNKNOWN pending separate action-specific Human approval and just-in-time source/target/contract revalidation.

## Input contracts

### 1. GitHub capture envelope

A local, explicitly selected UTF-8 JSON object (not arbitrary API response) with **exactly**:

```json
{
  "schema_version": "arca.issue-harness.github-issue-capture.v1",
  "provider": "github",
  "repository": "example-org/example-repo",
  "issue_number": 123,
  "node_id": "I_SYNTHETIC_EXAMPLE_123",
  "updated_at": "2026-11-07T00:00:00Z",
  "html_url": "https://github.com/example-org/example-repo/issues/123",
  "api_url": "https://api.github.com/repos/example-org/example-repo/issues/123",
  "title": "Synthetic title",
  "body": "One exact source line per requirement.\nAnother line.\n"
}
```

All provider fields are *operator supplied* in R1. Type/identity/URL consistency is checked. The `updated_at` timestamp is a **mutable revision indicator**, not a cryptographically immutable GitHub revision; even a GitHub-issued updated_at may change for metadata changes. Actual provider fetch at an authorized host and exact body SHA-256 are needed for independent provenance. No GitHub/HTTP fetch is implemented here. Pull requests disguised as Issues are outside this normalized capture contract.

### 2. Reviewed source snapshot

Existing `arca.issue-harness.snapshot.v1` with `BP-.../rN` source ID, fixed `draft-only` scope, exact declared Claim/non-goal/Human decision lines, `prohibited_actions` and **exact** `approval_provenance="operator-curated lexical transcription; NOT independently verified"`. R0 checks literal CR/LF-delimited source lines, approval provenance and the existing R6 schema. Unicode visual line separators (U+2028/U+2029), C1 controls and disallowed C0 controls are rejected rather than silently split. R1 rechecks all of these rules when verifying a staged bundle. No automatic summarization or truncation of multi-line Markdown occurs; an unrepresentable Issue must fail and be explicitly reviewed/restructured. Source-claim IDs and the completeness of lists are not independently authenticated.

### 3. Pinned digest/identity inputs

The operator supplies separately:
- SHA-256 of the **raw capture JSON bytes**
- SHA-256 of the Issue **body UTF-8 bytes**, required to equal the explicitly supplied raw text file
- SHA-256 of the **curated snapshot bytes**
- Repository, Issue number, Node ID and `updated_at` expected from an external provider read
- Source ID and privately owned registry directory

Pins are consistency checks. Self-supplied pins do not independently authenticate the provider.

## Workflow (operator CLI only)

Files:
- `source_admission.py`: R0 raw/snapshot schema, whole-line lexical checks and private staged copy helper; not called from MCP.
- `source_admission_r1.py`: provider capture verifier, revision rule, registry bundle writer and nonactivating verifier.
- `operator_source_admission.py`: **operator-only CLI** with `preflight`, `stage`, `verify`.

All commands are offline. Malformed/nested JSON, duplicate keys and unsafe input paths are rejected with structured `BLOCKED` error codes (including `RecursionError` from deeply nested JSON); raw source text is not printed by errors. From `tools/issue-harness/`:

```bash
python operator_source_admission.py preflight \
  --capture /absolute/capture.json --raw-source /absolute/raw.txt \
  --snapshot /absolute/curated.json \
  --expected-capture-sha256 '<actual-sha256>' \
  --expected-raw-sha256 '<actual-sha256>' \
  --expected-snapshot-sha256 '<actual-sha256>' \
  --repository example-org/example-repo --issue-number 123 \
  --node-id I_SYNTHETIC_EXAMPLE_123 --updated-at 2026-11-07T00:00:00Z \
  --source-id BP-EXAMPLE/r1 --registry-root /absolute/private-registry

# Explicit operator step, NOT automatic activation:
python operator_source_admission.py stage <same-validated-options>

python operator_source_admission.py verify \
  --registry-root /absolute/private-registry --source-id BP-EXAMPLE/r1 \
  --current-capture /absolute/new-observation.json \
  --expected-current-capture-sha256 '<actual-sha256>'
```

Create the registry directory beforehand as the invoking user, with no group/other access (typically `0700`). Inputs must be regular absolute files, without symlink ancestors, and are bounded (raw 256 KiB, snapshot 128 KiB; capture 272 KiB). The `verify` command can run without a current observation, but then explicitly reports `current_capture_compared=false`: it is merely an offline private bundle integrity check.

## Staged registry and lifecycle

An operator-only `stage` creates `REGISTRY/BP-...__rN/` with mode `0700`, exactly four files all `0400`:

- `capture.json`: raw normalized capture bytes
- `raw.txt`: body bytes pinned to the capture
- `snapshot.json`: curated R6 snapshot bytes
- `receipt.json`: deterministic identity/Digest/status receipt written **last**

The receipt contains `STAGED_INACTIVE_OPERATOR_REVIEW_REQUIRED`, source ID, repository, Issue number, Node ID, updated_at, canonical GitHub URL, three hashes, and `origin_authenticated=false`, `semantic_approval_verified=false`, `activation=NOT_ACTIVE_NOT_PUBLISHED`, `effect_authority=NONE`. It is a local consistency record, **not a signed authorization or authentic provenance proof**. It must never be interpreted as a Human approval receipt.

The registry root directory is held under an **exclusive Linux advisory `flock`** during stage: alias/revision scans through receipt publication, entry fsync and registry-root fsync are serialized between cooperating operator processes. The directory is created exclusively. Existing `source_id` cannot be overwritten. For the **same provider Node ID**, R1 requires the same source ID prefix, sequential `rN` versions, strictly increasing `updated_at`, and a previously intact bundle; aliases, version gaps and conflicting IDs are rejected. GitHub `updated_at` is not sufficient alone for actual provenance.

`verify_bundle` refuses missing/extra files, symlinks, nonprivate modes, malformed/noncanonical receipt, authority mutation, Digest drift, provider identity mismatch, **snapshot provenance/schema/whole-line source binding violations**, revision mismatch and optionally an altered *operator-supplied* latest capture (including title changes). It does **not** poll GitHub and **cannot prove that the supplied latest capture was actually fetched**.

The staging operation is fail-closed but not an atomic multi-file transaction. If root fsync fails after receipt creation, `stage` returns `STAGING_WRITE_FAILED` even though an intact but durability-uncertain bundle may remain; inspect the entry and verify it before any manual recovery. Never hand-author a receipt to repair a partial bundle. Advisory `flock` cannot prevent a non-cooperating same-user process from editing the registry; Linux and a local filesystem supporting directory advisory locks are R1 prerequisites. A process interruption can leave a partial, nonusable bundle; `receipt.json` is written last, verification refuses incomplete bundles and later additions fail until explicitly examined. Same-user write access can defeat local hashes; deployment requires separate OS/environment constraints and trusted evidence.

## Scope boundaries and known limitations

- Never add `admit_source`, `file_issue` or any other side-effect Tool to the R6 MCP server.
- No GitHub API calls, SSH, Remote MCP, Task/KAGARI, Plugin installation, Release or real Issue writer.
- No verified Human approval; no automated parsing of arbitrary long GitHub Issue Markdown or semantic goal evaluation. Nested JSON inputs are bounded and fail closed. Unicode surrogate body text is rejected. Full-line matching remains a lexical-only necessary condition.
- No automatic active snapshot switch or changes to `~/.claude-personal`.
- `SOURCE_DRIFT` is checked relative to the pinned digest supplied to R6. It cannot prove the operator's pin was authentic.
- Provider API response may describe a PR or edited Issue; future trusted Host adapter must reject wrong resource types and re-fetch exact current revision at acceptance time.
- In R1, root directory symlink/race checks are best effort (no openat2 or immutable signed store). Schema checks use disposable, private writable scratch outside the registry, including for `verify` (which writes no persistent registry state); source directory bytecode/cache pollution is prevented during tests with `PYTHONDONTWRITEBYTECODE=1`.

## Test and review gate

Source-only isolated tests use synthetic captures. R0 regression tests are reused in-tree; Core and R1 tests run with the merged R6 harness unchanged. A dedicated test uses real official MCP SDK v2 subprocess stdio with a **disposable explicit snapshot copy**; that test-only copy is not a plugin activation API.

Before advancing: local full suite, explicit official SDK v2 tests (no skipped transport tests), independent source/security review, exact changed-file inventory, then separately approved correction Commit/Push to the existing Draft PR. Ready/Merge and Adam installed Claude Plugin changes require **separate approvals**.

R1 exits with `PREFLIGHT_PASS_NOT_STAGED`, `STAGED_INACTIVE_OPERATOR_REVIEW_REQUIRED` or `STAGED_VERIFIED_INACTIVE` and always `origin_authenticated=false` and `semantic_approval_verified=false`. Invalid inputs return `BLOCKED` in the CLI with a stable code. **R1 does not provide a production source authenticator.**
