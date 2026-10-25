# Decision Candidate Sweep

Before the final response of each substantive repository workflow turn, inspect the newly available evidence and intended next action for human-owned choices. Do this even when neither the executor nor the coordinator emitted `NEEDS_DECISION`. This is a lightweight declarative skill instruction, not a guaranteed always-on runtime hook, background monitor or proof that all choices will be caught.

## Bound the sweep

Use the current turn's contracts, actual diff/scope and resource/responsibility deltas, observed results, review findings and next action. Reuse relevant current evidence; follow only concrete leads. Do not fetch or re-read supporting Skills, Issues or full histories solely to satisfy this sweep when no new material candidate exists. Do not rescan the repository or run the retrospective audit every turn. Exempt `@btw`, unrelated conversation and unchanged pure observation. A newly observed material decision or drift makes an observation substantive.

In read-only/status/command-only workflows, detect and report within that mode. A candidate does not authorize execution, an unsolicited approval request or an extra write. `approval-brief` alone remains formatting only. A nested skill/coordinator may reuse the same sweep at the same snapshot; do not duplicate it at every layer.

## Inspect the decision, not its flag

1. Compare accepted objective, success criteria, non-goals, scope and known resource envelope with what actually changed or is proposed. Use the goal-alignment preflight when its trigger applies.
2. Look for new or changed architecture, public contract, responsibility/ownership, operational burden, compatibility, data/privacy/security policy, resource allocation or critical risk acceptance. Inspect important contracts/diffs as well as labels, tests and completion messages.
3. Identify the smallest consequential choice, exact action/target/revision, human-owned effect, available authority source and whether it remains applicable. Distinguish an executor's claim of approval from the original decision when retrievable.
4. Resolve routine technical choices from the accepted contract. Evaluate a proposed security or assurance gate against the approved stage (isolated MVI vs real integration/production), actual reachable effects and documented threat model. Out-of-scope hardening is a nonblocking deferred candidate, not a new Ask; material changes to approved risk are human-owned. Retain concrete existing approval, including an exact design or Merge grant, without demanding new formatting or ritual confirmation. A generic `Next`/`Accept` has only a recoverable previously explained scope; it cannot authorize an unidentified different target or risk.
5. Inspect recoverable provenance gaps before asking. Missing logs mean `unknown/needs-inspection`, not either permission or a verified violation. Do not manufacture speculative gates.

## Return a small delta

Record scope/snapshot and one disposition per real candidate:

| Disposition | Handling |
|---|---|
| `already-approved` | Cite exact applicable source/scope; continue within the grant. |
| `delegated-noncritical` | Cite the resolving contract; no human Ask. |
| `needs-inspection` | Name missing evidence and bounded next check; hold only an action whose authority/impact depends on it. |
| `human-decision` | Explain the unresolved choice with the four-field approval brief; critical choices use its decision-quality guidance. |

No candidate: record `none-found` for the inspected scope when a checkpoint is already required; do not claim universal absence of missed decisions. Omit a ceremonial user-facing section. Preserve the exact `review-queue` no-review response. Keep original evidence, confidence and affected next-action gate; never clear it merely because the sweep ran.

Send the delta to the existing workflow/coordinator writer. Do not create a new carrier, parallel ledger, queue scan or checkpoint write just for this reference. Detection does not grant retroactive authority, publication, Merge, deployment or installation. KAGARI owns runtime Ask state and answers; MUSUBI displays the common Task/Ask UI. Arca does not run a separate Ask watcher or notification broker.
