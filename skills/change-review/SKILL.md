---
name: change-review
description: Independently review one frozen prepublication change or GitHub pull request against approved intent, acceptance criteria and evidence. Use before authorized publication or merge, individually or as an isolated concurrent review. Produce findings and a pinned recommendation without changing code, publishing, approving or merging.
---

# Review a Frozen Change or Pull Request

Review the exact change independently against the approved goal, ACs, non-goals and relevant evidence. For OpenCode independent reviews, use `@opencode-reviewer` to verify the exact reviewer role/session/model in a fresh context. Read [verification policy](references/verification.md) to evaluate completion evidence; reuse relevant rules in executor packets. Passing tests alone does not prove acceptance or authorize publication.

## Select the applicable path

- For a frozen prepublication snapshot, read [preflight and isolation](references/preflight-and-isolation.md) plus [prepublication contract](references/prepublication.md).
- For a PR, read [preflight and isolation](references/preflight-and-isolation.md), pin base/head and fetch only relevant patch and test evidence.
- For findings, read [review method](references/review-method.md). Assess risk relative to the **approved stage and actually reachable effects**. Do not block isolated MOCK-only MVI solely for out-of-scope future hardening.
- For a full structured report, read [report template](references/report-template.md).
- For a changed result or handoff, read [checkpoint and quality](references/checkpoint-and-quality.md). Unchanged rechecks reuse the previous marker without another write.

## Non-negotiable review boundaries

An executor's result is a claim, not independent review. Reviewers must have a distinct verified context and role; a blocked send is not a completed review. Material in-scope risk, ambiguous approved intent, invalid evidence or changed head blocks a positive verdict. The reviewer never edits code, approves, merges, posts public comments or releases without the relevant separate grant.
