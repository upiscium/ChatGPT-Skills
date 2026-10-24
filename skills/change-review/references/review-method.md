## Review the implementation

Use `@human-review`'s `references/goal-alignment.md` at material changes and important PR milestones, and its `references/decision-sweep.md` before the substantive review final. Check silent human-owned effects in the actual diff, not just flagged gates or passing tests. At a significant scope/architecture milestone, also apply its `missed-decision-audit` mode to a bounded historical decision window in this independent context (or a fresh reviewer if this reviewer made the original decision). Keep that retrospective classification separate from this change's correctness verdict; a missing approval log alone is not a verified violation.

Review in this order:

1. Confirm that the approved intent is still appropriate for the current project contract; escalate rather than revise it when human authority is required.
2. Check the diff against every `AC-*` criterion, invariant, non-goal, and compatibility requirement.
3. Derive meaningful failure modes from that contract.
4. Map each criterion and failure mode to test evidence, identifying missing, weak, circular, or misleading tests.
5. Inspect the complete `base...head` PR implementation or frozen prepublication delta, plus surrounding callers, data flow, state transitions, error paths, public contracts, configuration, and documentation.
6. Check that the implementation is necessary and sufficient for the goal, without unrelated scope expansion or hidden behavior changes.
7. Consider CI and prior review signals, but verify their claims against the contract and code.
8. Attribute actionable findings only to the PR or to unmet acceptance criteria of its linked Issues.
9. List unrelated pre-existing problems only as post-merge review leads; do not use them to block this PR unless the change makes them materially worse.

Separate contract compliance from implementation quality in the report. A tidy implementation of the wrong behavior fails the first; compliance alone does not prove robustness. These are review dimensions, not a requirement for two agents or repeated review of every small task.

Give an independent reviewer the approved intent, frozen artifacts, relevant raw evidence and scope. Keep implementer conclusions and the coordinator's preferred verdict out of the initial instructions. Distinguish author claims from observations; inspect the code and evidence independently. Prior findings may be supplied for a scoped re-review.

For every proposed test, identify the realistic defect it would detect. Exact-value or source-text assertions are not substitutes for exercising behavior. After corrections, recheck changed behavior and its affected callers; preserve unaffected valid evidence and avoid restarting the entire review without a concrete risk or required gate.

## Classify findings

Use:

- `blocking`: Must be corrected before merge because the PR is incorrect, unsafe, incomplete against required scope, or lacks essential validation.
- `non-blocking`: Worth improving but safe to defer without violating the linked Issue or contract.
- `question`: A decision or missing fact prevents a reliable conclusion.
- `post-merge-lead`: A pre-existing or broader product concern for `@repo-review`, not a PR defect.

Assign priority `P0` through `P3` and confidence `high`, `medium`, or `low`. Require a precise code path, contract, test result, or reproducible reasoning chain. Do not report style preferences as findings.
