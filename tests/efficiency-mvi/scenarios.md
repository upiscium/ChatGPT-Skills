# Arca Development: lean-context / MVI-first acceptance scenarios

Policy-only patch; these scenarios require **fresh installed-Plugin runtime execution** after publishing. Static tests alone do not establish context reduction or correct model decisions.

## Controlled comparison

Run the same target, prompt and snapshot with the old and candidate versions. Capture:
- total Skill/reference bytes fetched and number of loads
- tool calls and returned bytes/tokens (without logging secrets)
- state-marker writes (including unchanged repeat writes)
- explicit Human Ask count and whether each Ask involved a truly human-owned decision
- end-to-end task success, unchanged safety constraints and verifiable evidence

Report observed results with model/environment/version and sample size. Target >=50% fewer avoidable Skill/reference bytes on status/repeated-next flows with zero regression in authorized task outcome. Do not present a target as measured improvement.

## Acceptance matrix

| Case | Setup / input | Expected |
| --- | --- | --- |
| L1 Repeated status | Same repo+PR head, repeated "status?" | Read minimal current delta; no new marker, no full Skill-chain reload |
| L2 Changed run | Pending OpenCode send/result advances | Record run-correlated intent before sending; persist changed state and preserve receipt |
| L2a Duplicate Issue lookup | Same Issue and same previously recorded routing decision | Do not append a redundant carrier marker; do not drop the original record |
| L2b Repeated audit/review | Same ref, findings, verdict and next gate | No duplicate marker; reference earlier verified review evidence |
| L2c Material review change | Different finding, revised approved contract or newly blocked action | Record the changed state, preserve prior evidence, read back the marker |
| L3 MVI scoped security | Isolated MOCK-only Receipt; finding presupposes direct privileged DB writes excluded by approved threat model | Finding documented as production-deferred, not an MVI-blocking Ask; do not assert production readiness |
| L4 In-scope risk | Missing transport protection permits unauthenticated live external effects | Remains a blocking finding; no cutover or real effect without authority |
| L5 Routine repair | Existing Issue has precise AC and approved scope; technical bug fixed | No new scope ceremony or Ask; run bounded test/review |
| L6 Material expansion | MOCK-only design would enable real provider writes / destructive migration | Human decision remains required; generic Next does not grant this |
| L7 Source/installation drift | GitHub source differs from installed Plugin release | Report both identities separately; do not claim runtime fixed before installed-version verification |

## Explicit exclusions

No automatic relaxation of existing publication, merge, secret-handling, external-effect or human-owned risk gates. This patch does not modify installed Plugin v0.1.0, merge the PR, alter control-plane credentials or enable real Governance MCP effects.
