# A/B receipt capture (manual and read-only)

This workbook is not an experiment result. A and B must be run in separate,
otherwise equivalent new chats. For a minimum pilot, copy the fictional
fixture in fixture-ablation-r1.md into both chats and use exactly the same
model, Project and Memory setting. Make two A/B pairs with reversed order
before trying broader scenarios; three matched pairs per case are needed
before drawing any conclusion.

For a **tool-mediated** comparison, also run T6 from
[plugin-ablation.md](plugin-ablation.md) in a separate A/B pair. Both
conditions must use the same GitHub read permissions. Grade tool-source
grounding separately from answer plausibility; a correct answer copied from
Memory without a verified source read is not a PASS for T6. Record actual
tool invocation and obtained commit references, or mark unknown.

For each response, score PASS only if all required fixture answers are
correct; score FAIL with a short factual evidence reference; otherwise
UNKNOWN. Do not infer Plugin invocation merely from the prompt wording.
Use the ChatGPT UI / tool trace to record observed invocation when available.

Save sanitized results as JSON Lines, one object per run:
{"case_id":"T1","trial":1,"condition":"A","history":"fresh",
 "memory":"unknown","model":"same-model","snapshot":"fixture-aurora-20261024-r1",
 "toolset":"same-common-tools","outcome":"unknown","evidence_ref":null,
 "tool_calls":null,"skill_bytes":null,"tokens":null,
 "unnecessary_asks":null,"duplicate_writes":null,"plugin_observed":null}
Repeat with condition B and the same fields except real observed values.

Null means unavailable, not zero. Token counts must come from an actual
usage meter; rendered output text length is not token usage. Evidence
references must point to a verifiable run excerpt or saved local file and
must not include secrets or personal data. No run or response is created
by the aggregation script.

Run:
python3 tests/efficiency-mvi/ablation.py path/to/collected-runs.jsonl

The resulting mean deltas are descriptive. B-A measures explicit invocation,
not necessarily actual Plugin availability. Condition C requires independent
proof the Plugin was unavailable; don't use C just because it was not named.
Never pool records with different Memory state, model, fixture or common tools.
