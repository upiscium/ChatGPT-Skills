## Preserve boundaries

- Do not modify code, Issue/PR content, branches, labels, projects, or releases. The only exception is the automatic update of the marked `codex-repo-state:v1` record on an already selected Issue/PR carrier; it must be read back and must never be treated as an approval.
- Do not perform a general defect hunt; use `@repo-review` when the goal is finding Bugs or Feature Requests.
- Do not generate an implementation plan; use `@patch-plan` or `@blueprint` after the user selects work.
- Use `@repo-handoff` for automatic persistence of the owned snapshot fields without overwriting coordinator runs or next actions. Do not replace `@handover` or preserve private conversation context in a public record.
- On the default vNext path, KAGARI owns native Task/Ask monitoring and MUSUBI is the UI/notification consumer. SwitchBoard monitors only an explicitly selected legacy OpenCode workflow. This status snapshot neither monitors nor answers Ask; do not infer a run failed because the connection is unavailable or claim monitoring/notifications are configured without evidence.
- Route security-sensitive details to `@security-audit`; summarize only the existence and handling status of restricted work.

## Quality gate

Verify that:

- The snapshot is pinned to a branch, commit, and observation time.
- All five views are answered, including an explicit unknown or none-confirmed result where appropriate.
- Usable claims trace through the intended path and name their release/environment or supported checkout and prerequisites; code existence is not mistaken for user availability.
- Planned, partial, absent, and unknown states are not collapsed together.
- Active work is supported by current artifacts rather than open-Issue count alone; stale or idle partial work is not presented as ongoing activity.
- Not-started claims are limited to accepted scope and the inspected branches, PRs, and tasks; inaccessible sources are disclosed.
- Durable continuation records are located, pinned to a carrier and checked for drift. Persist materially changed actionable state; reuse the prior marker for an unchanged snapshot. Report missing carriers as `bootstrap` rather than inventing them.
- Roadmap position is tied to documented milestones and their exit criteria; missing roadmaps and parallel tracks are represented honestly.
- The agreed next action, an unconfirmed plan, and assistant recommendations are distinguished; coordinator checkpoints and prior denials remain intact.
- Every active gate preserves its prerequisite, authority, fallback, evidence, and revalidation.
- Completed work is not presented as pending, and merged-but-unverified work is not overstated.
- A reader can identify the current architectural position and next decision without reading the entire repository history.
