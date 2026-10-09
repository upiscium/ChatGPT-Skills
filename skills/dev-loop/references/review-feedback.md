# Process review feedback before delegation

Use this when converting external feedback or change-review findings into a correction packet. A reviewer proposes a finding; the approved contract determines the required behavior. Arca evaluates and coordinates; OpenCode performs authorized repairs.

## Evaluate the finding

1. Pin its ID, reviewed snapshot, claimed defect and requested behavior. Re-read the full relevant feedback and contract.
2. Inspect the current code, affected callers, supported versions and available evidence. Check whether the concern still applies, is already corrected, or conflicts with an accepted decision.
3. Separate the defect from the suggested implementation. A valid defect can have an unsuitable remedy; retain the defect while choosing a remedy within approved design latitude.
4. Classify the disposition with evidence:

| Disposition | Meaning and next action |
|---|---|
| `accepted` | Reproduced or established by code/contract; include a bounded correction and verification |
| `rejected` | Contradicted by specific evidence or outside the accepted contract; explain without changing scope |
| `needs-evidence` | Plausible but not established; request or collect a discriminating observation |
| `decision-required` | Changes architecture, scope, compatibility, authority or risk acceptance; present the concrete choice |
| `deferred` | A non-blocking improvement can wait without violating ACs; retain its reason and later destination |

Do not reject solely because the current tests pass, accept solely because a reviewer sounds confident, or close a confirmed blocker as a convenience. Independent review must resolve disputed blocking findings before the verdict becomes ready. A human-owned tradeoff stays with the human. Finding IDs and the reviewed snapshot survive every disposition update.

## Prepare the correction

- Correct accepted blockers in dependency order and keep verification with each coherent change. Consolidate related fixes without bundling unrelated improvements.
- Clarify ambiguous interdependent findings before work that relies on their interpretation. Continue clearly independent authorized work; one uncertain item does not freeze the whole batch.
- Prefer existing interfaces and actual consumers over speculative abstractions. Do not infer that code is unused merely because a text search found no direct caller; check public/plugin/dynamic consumers and the compatibility contract.
- Carry scope, expected/must-not-touch paths, affected ACs, regression evidence, rejected hypotheses, operation grant and stop point into the new instruction revision. Preserve the current workstream and publication boundary.
- Select test commands from inspected repository instructions, manifests or proven run evidence. Test-file syntax or an installed runner alone does not establish the project's command. When that evidence is missing, state the behavioral check and a bounded command-discovery step; label any example command provisional, not executable or verified. Missing information must remain explicit in a draft packet.
- Reconcile an old pending delivery before dispatching a correction. Dispatch once through `opencode-bridge`, then return after bounded receipt checks.

After collection, request scoped independent re-review of corrected behavior and affected assumptions. Broaden review only for a new concrete interaction risk or required gate; do not redispatch the complete original plan for a local correction.

Respond with the technical conclusion and evidence. State when a previous assessment was wrong and what changed it. Posting a reply or resolving a GitHub thread remains a separate externally visible action requiring existing user authorization.
