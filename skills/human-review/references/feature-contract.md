# Feature Contract — reusable user-goal specification (vNext candidate)

Use when an approved user feature spans multiple Issues or its original purpose must be compared with delivery. For a small already aligned Issue, the approved brief and ACs are enough. **Do not create a new Epic or ask for approval merely because this reference was read.** A Feature Contract is a specification artifact, not an execution grant.

Keep only fields material to this feature:
- Original human-approved goal, source, revision and intended user-visible behavior.
- Actors, usage assumptions, required positive/negative/integration behavior and observable minimum acceptance.
- Approved scope, explicit non-goals and the stage-specific assurance boundary (isolated MVI versus real deployment).
- Relevant dependencies, known time/compute/resource limits and actual acceptance Evidence requirements; unknowns stay unknown.
- Related function-level Issue IDs and ACs, current agreement/decision provenance and exact changed scope.

## Agreement and implementation boundary

First alignment: ask grouped questions only about unresolved requirements and summarize the user-visible behavior, scope, assumptions and expected completeness. Reuse an existing exact approval.

Second alignment: before implementing selected Issues, show their exact IDs and changes, and obtain authorization for **that Issue set**. Approval of a Feature Contract or permission to file Issues does not authorize KAGARI Task startup, PR publication, Merge or release.

KAGARI owns in-scope implementation, technical tests/review/correction and native Task/Ask; Arca later evaluates the delivered behavior against the original goal. If requirements change materially, update only the affected specification after the proper Human decision; retain prior revision provenance without expanding unaffected grants.
