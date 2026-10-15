# Independent Missed-Decision Audit

Use `@human-review missed-decision-audit` for a retrospective, bounded review at significant scope/architecture milestones or for an explicitly requested historical sample. It is separate from the per-turn Decision Candidate Sweep and is not an audit of every message. Missing an executor flag must not exclude a decision from the sample.

## Freeze scope and establish independence

- Name repositories, time window/milestone, sampled decision units and inclusion rule. Pin relevant base/head or merged SHAs and observation time. State inaccessible sources and whether the sample is purposive; do not claim a population miss rate from it.
- Use a fresh reviewer context that did not make the implementation/gate judgment under review. Supply accepted intent and raw artifacts, not the original agent's preferred verdict. When independence cannot be obtained, report a non-independent preliminary inspection; do not label it an independent audit.
- Use read-only source access or an isolated review surface. The reviewer returns evidence to the existing coordinator; it does not change code, gates, permissions, PR state or the original decisions.

## Reconstruct each consequential choice

1. Read the original human goal/authority, measurable outcome, non-goals, resource constraints and applicable delegated latitude.
2. Reconstruct the timeline: proposal and brief, actual human decision and its scope, implementation/contract changes, review findings, later corrections or goal changes. Read later comments before treating an old Issue-body gate as current.
3. Inspect the actual significant diff and contracts, callers/integration when relevant, and validation limits. Do not audit only PR titles, summaries, `NEEDS_DECISION` flags or the implementer's self-assessment.
4. Compare the implemented decision with the authority effective at that time. Check counterevidence and concrete prior grants. A later priority change or unnecessary feature removal does not alone prove the earlier decision lacked authorization.
5. Distinguish direct human evidence, connector/agent-reported consent, inference and unavailable original provenance. A comment attributed to the owner but produced via an app may report a decision without containing independently retrieved original human words.

## Classify with evidence

Use one primary classification per sampled decision; split separately decidable choices explicitly and update the denominator rather than double-counting a PR.

| Classification | Required basis |
|---|---|
| `verified-unasked-human-owned` | Positive evidence that a consequential human-owned choice was taken outside applicable authority without asking: for example an explicit acknowledged bypass, an action contradicting a still-applicable denial, or a sufficiently complete decision/action trace. Explain why the evidence establishes absence of authorization; missing logs alone never suffice. |
| `suspected-needs-provenance` | Material choice or goal/resource drift is plausible but original authority, chronology or coverage is insufficient. State what would distinguish a miss from authorized work. |
| `already-human-approved` | Recoverable approval resolves this exact scope at the relevant revision/time. Label reported approval as reported; if its scope or credibility is materially uncertain, use suspected instead. |
| `delegated-noncritical` | The accepted contract/latitude determines an ordinary technical choice without changing human-owned effects. Cite that contract. |

Keep technical defects, overengineering/late decisions and missing authorization distinct. A technical research run is not scientific acceptance. Do not reopen an exact approved design/Merge merely because it is important, and do not infer new authority from a generic continuation.

## Report and hand back

Give a bounded summary and a table of decision ID, pinned artifact, actual choice, authority/chronology, classification, confidence/provenance, and evidence gaps. Count verified misses, suspected cases, approved decisions and delegated choices separately with the explicit denominator. State what was inspected beyond metadata and what remains unverified. A zero verified count is not proof that no historical misses exist.

For a verified miss, explain the missed gate, consequence and the current remedial choice, if any. For suspected cases, request the smallest provenance check first. If a current unresolved human-owned action actually needs approval, use the existing four-field approval brief with options; a historical finding does not grant retroactive approval, rollback, Merge or new execution.

Return a pinned audit delta to the existing coordinator. A standalone audit may checkpoint only its owned neutral observation through `@repo-handoff` on the existing carrier under that skill's recording policy; preserve the coordinator's next action, existing decisions and gate statuses. Do not publish restricted details, create Issues or non-marker comments, or convert findings into work without authority.
