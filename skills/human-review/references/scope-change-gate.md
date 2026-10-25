# Scope Change — classify only material deviations (vNext candidate)

A proposed improvement, risk or defect is **not** an automatic change to the accepted feature/Issue scope. Reuse existing approvals and the original user goal; ask only when the next consequential action genuinely depends on a new Human choice.

| Kind | Meaning | Owner / action |
| --- | --- | --- |
| A — in-spec correction | Approved Issue/AC not met; no new product requirement | Existing KAGARI Task fixes/tests within its grant, without an extra Arca Ask |
| B — optional enhancement | Not needed for current accepted behavior or assurance | Defer as a nonblocking candidate; do not silently file/implement it |
| C — material requirement change | Different user-facing behavior, scope, architecture, resource allocation or accepted risk | Hold only the dependent step; Arca asks Human to align and revise affected Issues |
| D — unresolved evidence | Whether an observed gap belongs to A/B/C is unclear | Inspect minimal read-only evidence; retain unknown, stop only affected action if it depends on a Human-owned choice |

Production-only hardening outside an isolated MVI's approved threat model is B/deferred unless it affects the actual in-scope minimum or changes accepted risk. An actual destructive/external/sensitive effect still needs its existing authorization; this classification cannot bypass it.

Record only a **material actionable delta** on the existing Issue/PR carrier with evidence, reason, affected scope, next owner and trigger. Reuse an unchanged record; no per-turn polling, blanket candidate ledger or repeated Ask. Aggregate deferred B and nonblocking D at user-requested prioritization or the next genuine feature/phase decision; never interrupt the present authorized Task once per suggestion.

An arbitrary `Next` does not approve C, expand a selected Issue set or start the next phase. No new authority system or generic state database is created here.
