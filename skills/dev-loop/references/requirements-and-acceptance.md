# Arca requirements → Issue specifications → user-goal acceptance

Authority: https://github.com/upiscium/ChatGPT-Skills/issues/4
KAGARI: https://github.com/upiscium/KUMIKI/issues/291 and https://github.com/upiscium/KUMIKI/issues/292
MUSUBI: https://github.com/upiscium/MUSUBI/issues/1

## Owners
- User: original requirements, aligned scope, selected Issue execution set, material changes, next phase and Release/Merge.
- Arca: elicit original user intent, produce approved function-level Issue specifications, and evaluate observed delivered functionality against the original goal.
- KAGARI Main and Task Orchestrator: accepted Issue assignment, code, tests, technical reviews/corrections, Evidence and native runtime Ask.
- MUSUBI: mobile UI for KAGARI's common Task/Ask control interface. It does not own a second Task registry or independent OpenCode broker.

## First human alignment — original intent
Use blueprint and goal alignment. Extract desired user-visible outcomes, target actors, scenarios, operating assumptions, in-scope behavior, non-goals and measurable acceptance. Group material questions without an arbitrary count or production-only checklist. Summarize agreed behavior and boundaries. Iterate only unresolved material differences; reuse exact recorded approval.

Use `@human-review`'s Feature Contract reference only when material feature-level goal, revision or assurance scope needs a shared anchor across Issues. An existing approved Epic/brief is sufficient; do not turn contract formatting into a new authority gate. Material proposed scope drift follows its Scope Change reference: in-spec technical corrections remain with KAGARI, unrelated improvements are deferred, and only changed original user intent needs Human alignment.

## Function-level GitHub Issues
Use issue-filer, not a new specification database. Each coherent Issue unit carries original approved goal/revision, exact expected function and user scenario, exclusions, stable observable ACs, dependencies and evidence expectations. Issue creation is separate from Task execution authorization.

Before executing a selected set of Issues, present their exact repository/Issue IDs, user-visible outcomes, scope changes and explicit exclusions for a second focused human alignment. Human authorizes that exact set; generic Next is not a new implementation/phase grant.

## KAGARI handoff
Only call a verified supported Issue/Task API or CLI after the human authorization and exact source/revision checks. If no interface is available, return not-dispatched with the bounded Issue packet; do not invent CLI syntax, launch OpenCode sessions directly, or claim an accepted Task. KAGARI's implementation and correction loops are autonomous only inside the approved Issue scope. It owns Task Ask; MUSUBI presents it.

## User-goal acceptance
Use repo-review in the user-goal-acceptance mode. Read the original user goal, approved Issues/ACs and actual KAGARI Task Evidence/user operation. Distinguish:
- Goal satisfied: evidence shows the required user workflow actually works.
- In-spec technical defect: return criterion, reproduction and evidence to the owning KAGARI Task for repair; no Arca code-review micro-management.
- Specification-goal mismatch: the Issue itself misses the original intent; ask the User about the affected requirement and revise only the approved scope.
- Unknown: insufficient/stale evidence or unavailable runtime; request only the necessary observation, not a fabricated PASS.

Combine bounded read-only/specification steps without a one-stage-per-response bottleneck, but stop at human-owned alignment, new execution set, next phase or material risk. Do not re-add Arca live Ask polling, separate technical Reviewer, a new policy engine or mandatory full OpenCode logs.

This source contract is not a live KAGARI adapter, installed Plugin update or permission to Merge/Release. Legacy Arca OpenCode Skills remain explicitly selectable for existing work until integrated KAGARI/MUSUBI E2E is accepted.
