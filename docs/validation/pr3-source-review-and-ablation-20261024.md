# PR #3 — source review and ablation feasibility, 2026-10-24

> Later update: [12 actual ChatGPT trial responses and independent scoring](pr3-ablation-20261024/results.md) supersede the earlier API-only execution limitation and zero-trial status below. The earlier evidence remains historical.

## Scope and conclusion

Repository: upiscium/ChatGPT-Skills. Base: `fad2a799fa0533a55006ae1f97778846a9bb9ce5`.
Restored Draft head: `658077e936a7f5b29093dbb4e3328f5937a6295c`.
This report accompanies a five-file correction over that head. It establishes source correctness and experiment feasibility, **not measured Plugin efficacy or installed behavior**. Merge, Plugin installation/update/release and production changes remain separately authorized.

## Independent review

A fresh, read-only Codex reviewer context inspected the complete PR delta and relevant surrounding instructions/tests. This was a new local source inspection; the older blocked OpenCode submission was not retried and remains unexecuted.

| Finding | Original result | Correction |
| --- | --- | --- |
| PR-001, P2 blocking | ablation.py matched each trial correctly but pooled matched pairs across different case/history/Memory/model/snapshot/toolset strata into one mean. Opposing effects could cancel to zero. | Reject heterogeneous matched strata with an actionable error; summarize separate JSONL files. Retain repeated trials within one stratum. |
| PR-002, P3 nonblocking | Two relocated references still instructed unconditional continuation/checkpoint refresh, contradicting the unchanged-state invariant. | Explicitly reuse the prior marker for unchanged Next/status and write only material/recovery-critical changes. |

The initial independent verdict was changes-required at `658077e`. Focused independent re-review found both findings resolved and no important residual findings in the five-file correction. It verified A/B and B/C mixed groups, combined unlike comparison groups, valid repeated trials, unmatched records, and unknown metrics. Source readiness is separate from empirical acceptance. Review risk: medium; findings/corrections are base-stable. No new human product/risk decision was identified.

Correction manifest SHA-256: `e66b6e448c2ad7c10489de0a49e58f8ef3c8559cc6c91bee1f3fb77f9bdcc020`, over sorted UTF-8 lines `<sha256>  <relative-path>\n`.

| Path | SHA-256 |
| --- | --- |
| skills/repo-handoff/references/output-and-quality.md | 75778af2216ce0cb0ccc43df623c717d5b91f65724c49b3ca68856f7268672df |
| skills/repo-status/references/quality-and-gates.md | 0b5ff62900a880dca77450f3f1b1898b036809aa4691165f0a2dd4a74a7043d9 |
| tests/efficiency-mvi/ablation-runbook.md | e721f12aac782f1f6c3fd69755f0c653d1f24c60d2e155b3ff8dc4049ab6040f |
| tests/efficiency-mvi/ablation.py | c20ed9b7ec3f8bbcae5827d9ebd05102b69ed1ff4767ec4e971cf58be6871487 |
| tests/efficiency-mvi/test_ablation.py | f74aa9e83c0c7b97432a1aff6ff7f144afb31cc9c445d05fb91db943d0bbe307 |

## Verification evidence

Environment: local Work container, Python 3.12.14. Downloaded skills/tests source: 117/117 files verified against GitHub git-blob SHAs at the restored head.

- Original snapshot: `python3 -m unittest discover -s tests/efficiency-mvi -p 'test_*.py' -v`: 20/20 PASS, independently repeated by reviewer.
- Correction: same suite: 22/22 PASS, independently repeated by reviewer.
- Sensitivity: the new no-pooling regression against the original aggregator fails all six subcases (case/history/Memory/model/snapshot/toolset); the correction passes. These are **synthetic software regression inputs**, not ChatGPT A/B observations.
- `tests/issue1/validate_structure.py --base <reconstructed-base-tree>`: PASS; same two pre-existing missing repo-review icon references. The validation checkout reconstructed skills/tests base content by reversing the complete PR diff, then overlaid candidate/corrected files. Its local base tree `1e7a9fdb848f62edbda052850b5c775d90e1e165` is **not the upstream commit ID**.
- Skill creator quick validation: repo-handoff and repo-status PASS. Their root metadata/UI were unchanged.
- Structural validator includes diff whitespace checks. These are structural/static checks, not proof of model behavior.
- At restore, GitHub returned no submitted PR reviews, commit statuses or pull-request workflow runs; this does not mean GitHub CI passed.

## Measured source-loading proxy

| Skill root | Base bytes | Candidate bytes |
| --- | ---: | ---: |
| dev-loop | 16,869 | 2,821 |
| repo-handoff | 19,211 | 2,367 |
| patch-plan | 23,431 | 2,193 |
| repo-status | 16,334 | 2,119 |
| change-review | 16,291 | 2,107 |
| Total | 92,136 | 11,607 |

Measured reduction: **87.4023% in the five root files only**. The correction does not change those roots. Required references still incur loading cost; full task context, actual tokens and time saved are unknown. Loading all references would defeat the intended on-demand mechanism.

## T1/T6 feasibility and actual observations

| Item | Observed result |
| --- | --- |
| T1 controlled fresh-chat A/B | Not run; no supported independent ChatGPT conversation-creation API available in this session. Current context already contains the fixture/oracle. |
| T6 source-read feasibility | Actual GitHub fetch_file reads succeeded at both exact frozen commits below. This is an ad-hoc preflight, not an A/B trial. |
| T6 preflight root reads | 3 successful fetch_file calls: base once, candidate twice; one candidate read was duplicated after a local collection error. Decoded source content returned: 23,945 UTF-8 bytes. Envelope/transport bytes unknown. |
| Matched fresh-chat A/B pairs | 0 |
| Tokens, end-to-end latency, incremental accuracy, Ask/write reduction | unknown |
| Memory causality | unknown |
| Installed Plugin | v0.1.0 per restored record; not updated or independently re-inspected here. |

T6 sources actually checked:

- [BASE repo-handoff root](https://github.com/upiscium/ChatGPT-Skills/blob/fad2a799fa0533a55006ae1f97778846a9bb9ce5/skills/repo-handoff/SKILL.md): record every repository response observing/changing state; save/read back dispatch intent before sending.
- [CANDIDATE repo-handoff root](https://github.com/upiscium/ChatGPT-Skills/blob/97439e99a40c8c373021c2336520376e4f77ac3e/skills/repo-handoff/SKILL.md): no fresh marker for unchanged reads/repeated Next/status; dispatch intent still mandatory before send.

The T6 task intentionally freezes an earlier candidate identity `97439e99`. It cannot by itself validate all changes at the current PR head. Current-session observations are excluded from the A/B receipt aggregator; no experimental outcome records were invented.

## Minimal remaining operator actions

1. Start four otherwise equivalent **new ChatGPT chats**: T1-A, T1-B, T6-A, T6-B. Use the same model/effort, Project instructions, common tools and Memory setting. Record unknown settings honestly.
2. For T1, copy only the frozen record and identical Test prompt from [fixture-ablation-r1.md](../../tests/efficiency-mvi/fixture-ablation-r1.md). Keep the scoring oracle outside the trial prompt.
3. For T6, copy the identical task prompt from [plugin-ablation.md](../../tests/efficiency-mvi/plugin-ablation.md). Both conditions need the same GitHub read access.
4. A has no explicit Plugin selection; B explicitly selects Arca Development. A is **not Plugin-disabled**. Keep substantive prompts identical and retain outputs plus visible tool/Skill traces.
5. Collect actual receipts using [ablation-runbook.md](../../tests/efficiency-mvi/ablation-runbook.md). Missing counters are null/unknown, not zero. Group each case/settings stratum into its own JSONL file; include effort and Plugin version in identifiers.
6. One pair per case is a pilot only. Before interpreting differences, collect at least three matched pairs per selected case (12 responses for T1+T6) with both A-B and B-A ordering.

This compares explicit use of the installed Plugin with non-explicit use. Candidate-versus-v0.1.0 runtime evaluation remains separate and requires a separately approved installation/update. No account-setting changes or Plugin-disabled condition were created.

## Recommendation

Keep PR Draft while collecting the bounded pilot. Source cleanup is supported by independent review, but **retain/remove/expand decisions based on Plugin-specific benefit remain unsupported by comparative evidence**. Do not add another management framework. If matched trials show no material benefit at higher cost, reduce overlapping instructions; if they show a reproducible gain in recovery/correctness/decision handling, retain those parts. No claim of equality or superiority follows from zero trials.
