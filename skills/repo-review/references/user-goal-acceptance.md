# User-goal acceptance of KAGARI Task delivery

This is Arca's user-facing acceptance evaluation, not Task Orchestrator code review.

## Evidence
Pin the original human-approved goal/source/revision; the selected Issue specifications, ACs and exclusions; and actual KAGARI Task Evidence or user-visible operation. Do not infer practical user success from green CI, source code or Task PASS. Missing Evidence is unknown.

For feature-level completion across Issues, use `@human-review`'s `references/feature-acceptance-gate.md` to keep original user minimum behavior separate from code/PR/release status. This is a read-only evaluation and does not create a second technical Reviewer or new approval for an already resolved decision.

## Classify original user outcomes
- goal-satisfied: the observed workflow achieves the original user-approved outcome with sufficient actual evidence.
- in-spec-defect: implementation violates an already approved Issue/AC. Return exact reproduction, criterion and evidence to the existing KAGARI Task for ordinary technical repair; Arca does not conduct its own code review.
- specification-goal-mismatch: the Issue may pass but its promised behavior does not meet the original human intent. Bring the affected requirement and concrete gap to the User; revise only the authorized Issue scope.
- unknown: relevant direct observation or Task Evidence is stale, missing or inaccessible. Identify the minimum evidence required, not a fabricated PASS.

## Output
For each relevant user goal show: approved goal and revision, Issue IDs and ACs, observed behavior/evidence, scope exclusions, classification and next owner (User / KAGARI Task / none). Report implemented behavior separately from verified user acceptance.

Separate **limited smoke or fixture success** from **actual user-workflow acceptance** by naming each environment and its own observed result. A successful isolated OpenCode Session smoke can satisfy its bounded smoke goal while the real approved user-Issue workflow remains `unknown`; a merged PR and green CI do not close that gap.

For an `unknown` outcome, identify whether (a) integration/completion is demonstrably pending, (b) an implemented path lacks direct user-operation evidence, or (c) evidence is stale or inaccessible. Where the reason itself cannot be verified, mark the reason `unknown` rather than inferring missing functionality from missing receipts. State the minimum next observation and its owner. These are explanations under the existing four classifications, **not new statuses or approval gates**.

The User retains new Issue/phase, scope, risk and Merge/Release decisions. Runtime Ask stays with KAGARI; MUSUBI is its UI. No new Task, continuous polling, extra reviewer, direct OpenCode action or live KAGARI API integration is implied by this source document.
