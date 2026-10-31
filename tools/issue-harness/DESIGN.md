# Decision note — MCP Issue Handoff Harness / MVI

Status: **isolated prototype**, not new production governance or a completed Normal Chat acceptance.

## Problem

Arca vNext Isolated rc.4 produced 13/18 PASS and 5/18 PARTIAL detached DES candidates in the C02/C03 targeted Normal Chat run, despite the source-only fixes in Draft PR #12. Remaining problems are authority revalidation omitted for downstream actions and inferred (`derived-unconfirmed`) ACs reused as mandatory dependencies or business revalidations. Every candidate was an independent Issue handoff artifact; global disclaimers did not repair its local omissions. Critical FAIL observed: 0, not proof of safety.

## Chosen scope

Use a **pure, read-only contract checker** and deterministic renderer, wrapped by MCP SDK v2. Do not invent an approval authority or Task orchestration service. A model proposes structured fields; independently pinned source values supply original goal, project non-goals, applicable action prohibitions and unresolved decisions. The renderer, not the model, creates the authority table. A separate business-rule section carries AC status and may not promote inferred rules to required.

### Explicit source authority limit

The snapshots are synthetic reconstructions of the user's fictional test inputs and bear a hash. They have NOT been authenticated against a Human-signed or GitHub-audited approval. Their `source-reported` metadata is a local test input, not an access token. No tool in the MVI can write to GitHub or KAGARI.

### API

- `validate_issue_draft(source_id, source_sha256, candidate)` -> `READY_DRAFT_ONLY` or `BLOCKED`, findings and digests
- `render_issue_draft(source_id, source_sha256, candidate)` -> same plus deterministic Markdown and SHA-256 only on pass

Both are synchronous/stateless and do bounded, offline local reads. A model can voluntarily call them, but it cannot establish effect-boundary enforcement merely by doing so.

## Acceptance matrix

- Five manually translated R4 defect cases must fail closed with expected codes; rendering rejected.
- Two constructed valid scenarios C02/C03 must render deterministically and carry all project non-goals, AC statuses, unresolved Human decisions, and every action-specific Human approval/revalidation requirement.
- A source digest change or symlink escape must block.
- A fabricated confirmed AC, or a derived AC promoted to `required`, must block.
- Unknown, malformed or adversarial input must block, not throw exceptions or produce Markdown.
- Tool list contains no writers, KAGARI or external shell capabilities.

## Deferred decisions

Actual canonical source acquisition, semantic goal evaluation, explicit Human alignment, source authorization verification, enforcement at GitHub Issue creation, KAGARI Task contract binding, Remote MCP authentication, and an end-to-end Normal Chat comparison require separate design/authority and implementation work. Keeping those separate avoids inadvertently creating a second KAGARI authority hierarchy or a generic policy engine.

## Reusable evidence

- Prior R4 targeted report: `ARCA-I4-R4-NORMALCHAT-TARGETED-R1`, 18 detached DES verdicts 13 PASS / 5 PARTIAL.
- Prototype source tests: see `tests/test_core.py`; snapshot digests in `fixtures/snapshot_digests.json`.
- Fixed source: [ChatGPT-Skills Draft PR #12](https://github.com/upiscium/ChatGPT-Skills/pull/12), left untouched.


## Source characterization after namespace hardening (2026-10-31)

The MVI enforces local ID identity (DES-002 -> AC-002-*) to prevent
standalone Issue drafts accidentally inheriting another function's AC.
Synthetic snapshots now carry all behavior text from the two fixed R4 booking
prompts as one-line original goals, with a bounded set of exact, verbatim
source claims. These fixtures remain source-reported, not an independently
authenticated Human approval record; full semantic goal alignment is deferred.
