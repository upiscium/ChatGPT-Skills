# Arca Development: actual ChatGPT A/B pilot, 2026-10-24

## Conclusion

The browser route was available, superseding the previous API-only feasibility limit. **12 fresh normal-Chat responses were actually executed:** T1 and T6, three A/B pairs each. The installed Plugin was not updated.

**No semantic-correctness advantage from explicit Plugin invocation was observed on these two tasks.** Both conditions answered all six task instances correctly. This small pilot does not establish equivalence, Plugin uselessness, or Memory causality.

A = no explicit Plugin selection, **not Plugin-disabled**. B = Arca Development explicitly selected through the @ menu. Actual automatic Skill invocation is unknown in both conditions.

## Conditions and execution

- Same authenticated account and browser; ordinary new ChatGPT chats, outside an explicitly selected Project.
- Chat mode and UI thinking effort **Medium** throughout. Exact backend model/effort internals and Memory setting remain unknown.
- No account, Memory, Plugin or connector settings changed.
- Each case used identical substantive prompt text. B added only the selected Plugin mention.
- Pair order per case: trial 1 A→B, trial 2 B→A, trial 3 A→B.
- Prompts and the observed Plugin selections are preserved in [browser-evidence.json](browser-evidence.json). The scoring oracle was not submitted to the trial chats.
- Restored source head was `820af1af5af8c53287e9bc288271c63bd6c1ed4f`. T6 deliberately compares immutable source commits `fad2a799...` and `97439e99...`; it does not evaluate execution of the current candidate Plugin.
- Installed Plugin version is v0.1.0 according to the durable restore record; it was not independently re-inspected during these trials.
- Some browser actions timed out after taking effect. Visible state was reconciled before continuing; no trial prompt was intentionally resent and no duplicate response was scored. Completed browser tabs were closed after evidence collection; chats were not deleted.

## Observed results

| Measure | A: no explicit invocation | B: explicit Arca |
| --- | ---: | ---: |
| T1 semantic correctness | 3/3 | 3/3 |
| T1 plain JSON / no-code-block compliance | 3/3 | 1/3 |
| T1 strict combined task pass | 3/3 | 1/3 |
| T6 answer correctness | 3/3 | 3/3 |
| T6 exact two-ref tool provenance | unknown, 3/3 | unknown, 3/3 |
| Unnecessary model Human Asks observed | 0/6 | 0/6 |
| Actual tokens / loaded Skill bytes / exact tool-call counts | unknown | unknown |

T1-B trials 2 and 3 rendered JSON code blocks despite the explicit no-Markdown-fence instruction. Their values were correct. This is an output-contract defect observed in the selected condition, not evidence that the Plugin caused it.

T6 activity panels showed repository fetching/review activity in all samples. They **did not expose raw tool arguments, per-ref receipts, call counts or returned contents**. Thus correct answers and matching source links are insufficient to certify retrieval of both exact refs. The strict T6 receipt outcome is `unknown`, not `pass`. The models' claims of “both verified” are not independently established by the visible evidence.

## UI time proxy, kept separate from token and latency measurements

| T6 trial | A “Worked for” | B “Worked for” |
| --- | ---: | ---: |
| 1 | 14 s | 14 s |
| 2 | 9 s | 17 s |
| 3 | 9 s | 14 s |
| Mean | 10.67 s | 15.00 s |

This is the **displayed UI work-duration indicator**, not measured end-to-end latency, billing time, model compute or context use. With only three pairs and unknown backend/Memory details, it is a descriptive signal only; it does not establish causal overhead.

The five candidate source roots remain 87.4% smaller by UTF-8 byte count. This pilot did not measure candidate-versus-v0.1.0 runtime context savings.

## Independent blind scoring

A separate read-only reviewer received 12 randomly ordered, anonymized response/activity snapshots and the task prompts. Condition labels, invocation chips and previous conclusions were withheld. Activity snapshots retained their “Worked for” headers; these times were not used to score correctness. The reviewer did not inspect the condition map.

| Blind sample | Run | Semantic | Required format | Source provenance | Model Asks observed |
| --- | --- | --- | --- | --- | ---: |
| S01 | T1-A-1 | PASS | PASS | n/a | 0 |
| S02 | T1-A-2 | PASS | PASS | n/a | 0 |
| S03 | T6-A-1 | PASS | PASS | partial | 0 |
| S04 | T6-A-3 | PASS | PASS | partial | 0 |
| S05 | T1-B-1 | PASS | PASS | n/a | 0 |
| S06 | T1-A-3 | PASS | PASS | n/a | 0 |
| S07 | T1-B-2 | PASS | FAIL | n/a | 0 |
| S08 | T1-B-3 | PASS | FAIL | n/a | 0 |
| S09 | T6-B-2 | PASS | PASS | partial | 0 |
| S10 | T6-A-2 | PASS | PASS | partial | 0 |
| S11 | T6-B-1 | PASS | PASS | partial | 0 |
| S12 | T6-B-3 | PASS | PASS | partial | 0 |

The reviewer independently confirmed the semantic results and two format failures, and required the strict T6 source-provenance limitation above. T1's absence of an activity panel cannot prove no hidden calls; zero Asks means no model Ask in the observed answers. Product rating widgets are excluded.

## Evidence and reproduction

- [Raw browser DOM evidence](browser-evidence.json), SHA-256 `1744b3711151ac915eca75f817d18f5d3911cad6aaaf9a49c7bf7ad85288eac7`.
- [T1 actual receipts](t1-receipts.jsonl), scored for semantic plus required format compliance.
- [T6 actual receipts](t6-receipts.jsonl), strict source outcome unknown; semantic correctness recorded separately.
- [Existing aggregator results](aggregate-results.json).
- [T6-B screenshot with expanded activity](t6b-proof.jpg), SHA-256 `2da66bbd1d4c42db7bcdf4a27ef4542ed0ccc8ca5aad8e109ce841b0832a1135`.

Run from repository root:

```bash
python3 tests/efficiency-mvi/ablation.py docs/validation/pr3-ablation-20261024/t1-receipts.jsonl
python3 tests/efficiency-mvi/ablation.py docs/validation/pr3-ablation-20261024/t6-receipts.jsonl
```

T1: matched=3, scored=3, B−A strict-pass delta=-2/3. This is driven entirely by formatting, not decision correctness. T6: matched=3, scored=0, strict-pass delta=null. Both show observed Ask delta=0; unavailable cost counters remain null. Do not pool cases.

The JSON evidence is derived from the rendered DOM. A clipboard-based collector returned stale/converter text in an intermediate check; those values were discarded and are **not** included as response evidence or used for scoring.

After all trials, PR #3 still had the same source head and nine existing comments as before the trials. This verifies no new checkpoint on that carrier; it is not a comprehensive audit of all possible external effects. Duplicate-write counters remain unknown.

## Recommendation and remaining scope

Retain the source-lightening direction; **do not expand governance or claim Plugin-specific gains on this evidence**. These two straightforward tasks show no measured semantic advantage from explicit invocation, two B-condition format failures, and a higher B UI time indicator. They support prioritizing lower instruction overhead over adding controls, but not deleting the Plugin solely from this pilot.

Remaining unverified: actual Skill/token consumption; strictly traced two-ref retrieval; old-versus-candidate installed Plugin behavior; Work-mode results; meaningful repeated-next/durable-handoff integration behavior; Memory causality. A larger management platform is unnecessary. If continuing efficacy work, use one real handoff/repeated-next workflow with observable receipts and cost counters, and compare a separately approved lean Plugin build with the installed baseline.

PR remains Draft. Merge, Plugin update/release and production changes were not performed.
