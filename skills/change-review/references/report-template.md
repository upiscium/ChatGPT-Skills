## Produce the review contract

```markdown
# Change Review

## Target
- Repository:
- Review batch and workstream:
- Mode: prepublication | pr
- Run / instruction revision:
- Frozen manifest / digest (prepublication):
- Pull request: number | not-created
- Pull request URL:
- State:
- Base branch and commit:
- Head branch and commit:
- Linked issues:
- Sibling PR heads at dispatch:

## Scope and validation
- Authoritative intent:
- Contract provenance:
- Acceptance criteria and non-goals:
- Risk tier: low | medium | high
- Inspected:
- Checks run:
- Existing CI/review signals:
- Limitations:

## Review recommendation
- Decision: ready-for-publication-review (prepublication) | ready (PR) | changes-required | blocked
- Rationale:
- Human review mode: summary-only | focused-review | decision-required
- Base sensitivity: base-stable | base-sensitive

## Decision interface
- Intent alignment: pass | fail | decision-needed
- Acceptance contract: <satisfied>/<total>; <partial or unverified criteria>
- Test evidence: strong | partial | insufficient
- Implementation and scope: pass | concern | fail
- Critical findings:
- Human decisions required:
- Focused review locations:
- Cross-PR concerns:

## Requirement traceability

| Criterion | Implementation evidence | Test evidence | Status |
|---|---|---|---|
| AC-001 | | | `satisfied` / `partial` / `violated` / `unverified` |

## Next gate contract
- Target action: publication decision for frozen <digest> | human merge of PR #<number> at <SHA>
- Authorization: separate and not granted by this review
- Status: stop | conditional | allowed
- Unresolved prerequisite: none | <required correction, check, approval, or decision>
- Clearing authority: <fresh change-review, required CI, repository protection, or named human decision>
- Admissible fallback: <correction packet, wait, or no merge>
- Evidence snapshot: <head SHA and checked signals>
- Reverify before action: <live head, base, checks, approvals, and mergeability>

## Findings

### PR-001: <title>
- Classification: blocking | non-blocking | question | post-merge-lead
- Priority: P0 | P1 | P2 | P3
- Confidence: high | medium | low
- Location:
- Evidence:
- Impact:
- Required change:
- Verification:
```

Keep existing `PR-*` finding IDs when reviewing a PR. Use stable `CHG-*` IDs for prepublication findings; preserve an explicit mapping after publication rather than losing finding history. Omit `Required change` only for questions and post-merge leads.
