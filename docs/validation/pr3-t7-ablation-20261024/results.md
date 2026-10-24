# T7: actual two-turn PR / Receipt A/B pilot — 2026-10-24

## Outcome

**Six fresh ChatGPT sessions, 12 actual responses**, three matched A/B pairs. Every session received the same read-only task and then the literal follow-up `Next`.

A = no explicit Arca Development selection, **not Plugin-disabled**. B = Arca Development selected through the UI mention. This pilot tests explicit invocation of the installed Plugin; it does not test the uninstalled lean candidate.

**No incremental continuity or decision benefit was observed from explicit invocation.** Both conditions preserved the read-only continuation in 3/3 sessions, with no unnecessary model Human Ask. One A continuation omitted an explicit receipt-status restatement; one B session honestly left the independent Draft flag unverified. Neither was a false baseline assertion.

## Fixed task and controls

Protocol: [canonical T7 preparation](https://github.com/upiscium/ChatGPT-Skills/pull/3#issuecomment-6384426425).

Turn 1 requests live GitHub PR #3 metadata and existing Receipt Lab `probe_get_receipt`/`probe_get_statistics` reads. It prohibits apply/replay, GitHub comments/state, execution starts and Merge. Turn 2 is exactly `Next`, continuing the read-only delta check.

Coordinator controls before every pair and after all trials:

| Field | Baseline and post-trial value |
| --- | --- |
| PR | open, Draft |
| Head | a920b1b031edd596accc677975c66ab7895dcbb5 |
| Merge authority | not granted |
| Receipt | rcpt_ea637faaf92106e3844a2479 |
| Receipt status / associated effects | committed / 1 |
| Case committed mock effects / receipts | 2 / 2 |
| Receipt Lab external writes | 0 |
| PR conversation comments | 11; exact IDs and bodies unchanged |

The PR head and Receipt contents also remained unchanged. These coordinator readbacks establish **no net change on the specified carrier and mock case**, not the complete call history or absence of transient write/revert behavior.

Environment: ordinary new ChatGPT Chat, same account, UI effort Medium, no explicit Project. Backend model, Memory regime, automatic Skill invocation and actual cost counters remain unknown. Installed version remains v0.1.0 according to the restore record, not independently inspected.

Actual initial-send orders were **B→A, A→B, A→B**. Planned order was A→B, B→A, A→B. Some UI Send clicks left prompts unsent; visible state was reconciled before retry, and actual order was retained. Both directions are represented, but this is a disclosed protocol deviation. No oracle or expected receipt values were submitted to trial chats. No account or Plugin settings were changed.

## Independent blind scoring

An independent read-only reviewer scored six anonymized two-turn records without condition labels or prior conclusions. Activity summaries retained UI duration headers; they were not used to score correctness.

| Blind sample | Run | Turn 1 complete/correct | Turn 2 complete/correct | Next continuity | Model Asks |
| --- | --- | --- | --- | --- | ---: |
| W01 | T7-B-2 | PASS | PASS | PASS | 0 |
| W02 | T7-A-3 | PASS | PASS | PASS | 0 |
| W03 | T7-B-1 | PASS | PASS | PASS | 0 |
| W04 | T7-A-2 | PASS | PASS | PASS | 0 |
| W05 | T7-B-3 | PARTIAL | PARTIAL | PASS | 0 |
| W06 | T7-A-1 | PASS | PARTIAL | PASS | 0 |

- W05: open/head/authority/receipt/counts are correct, but the independent Draft flag is explicitly unverified in both turns. This is incomplete verification, not a fabricated Draft flag.
- W06 turn 2: receipt ID/counts and continuity are correct, but `committed` is not explicitly restated. It relies on receipt contents matching the prior turn.
- Claims of exact read-API counts, timestamp/hash matching or ancillary Plugin/runtime-stage details are not independently established by the visible activity summaries.
- No baseline contradiction, model Human Ask, authorization expansion or observed unauthorized action was identified. Product rating widgets were excluded.

| Summary | A | B |
| --- | ---: | ---: |
| Turn 1 fully complete | 3/3 | 2/3 + 1 partial |
| Turn 2 fully complete | 2/3 + 1 partial | 2/3 + 1 partial |
| Both turns fully complete | 2/3 + 1 partial | 2/3 + 1 partial |
| Read-only Next continuity | 3/3 | 3/3 |
| Unnecessary model Human Ask | 0 | 0 |

All 12 turns have **partial UI provenance**, not proven exact request provenance. Activity panels show GitHub and Receipt reads/review; they do not expose raw arguments, per-call receipts or exact call counts. W05 turn 2 is particularly nonspecific about the Receipt Lab receipt read. Strict tool-provenance outcomes remain `unknown` for all six sessions.

## Observed UI duration proxy

| Trial | A initial | B initial | A Next | B Next |
| --- | ---: | ---: | ---: | ---: |
| 1 | 33 s | 54 s | 15 s | 20 s |
| 2 | 37 s | 64 s | 14 s | 11 s |
| 3 | 19 s | 96 s | 9 s | 8 s |
| Mean | 29.67 s | 71.33 s | 12.67 s | 13.00 s |

Mean sum of the two displayed work indicators: **42.33 s (A), 84.33 s (B)**. These are “Worked for” UI values, not end-to-end elapsed time, tokens, billing or causal Plugin overhead. The B initial responses showed broader PR/diff/comment investigation; B trial 3 also displayed web search activity. Activity-summary rows are not tool-call counts.

The descriptive difference is concentrated in initial retrieval; Next UI work durations are similar. Small samples, order deviation and unknown backend/Memory conditions prevent a causal performance conclusion.

## Evidence and reproduction

- [Browser DOM evidence](browser-evidence.json): SHA-256 `ddf71c8232a12e6e5acad89e252fd3d63c61dd713ad853071346c7f16df48b18`.
- [Coordinator controls](controls.json): coordinator reads are explicitly separate from trial tool evidence.
- [Actual session receipts](receipts.jsonl): strict outcomes unknown; semantic completeness and continuity recorded separately.
- [Existing aggregator output](aggregate-results.json).
- [Next screenshot](next-proof.jpg): SHA-256 `209e9ce4761ef3fe789b562ba4709cf1f7f703458cddd2b031a88f2f9e8057e8`.

From repository root:

```bash
python3 tests/efficiency-mvi/ablation.py docs/validation/pr3-t7-ablation-20261024/receipts.jsonl
```

Expected aggregation: six session receipts, three matched pairs, zero strictly provenance-scored pairs, pass-rate delta null; observed Ask delta 0. Missing tokens, Skill bytes, exact tool calls and per-session duplicate-write traces remain null. Preserve T7 separately from T1/T6.

All six owned browser tabs were closed after collection; chats were retained. The evidence commit and coordinator checkpoint occur **after** the no-write trial window.

## Recommendation and limits

T7 does not establish a unique benefit for explicit Arca invocation in this read-only handoff/Next workflow. It adds evidence for prioritizing instruction lightening and avoiding expanded governance. It does not establish Plugin uselessness, equivalence, Memory causality or candidate runtime savings.

No extra test platform is needed. Remaining meaningful work is an approved installed lean-candidate comparison with observable token/Skill costs, or receipt-level tracing for provenance claims. Merge, Plugin update/release and production changes were not performed.
