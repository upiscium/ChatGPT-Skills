---
name: repo-review
description: Evaluate delivered user-visible behavior against the original approved goal and Issue specifications using KAGARI Task Evidence. Legacy merged-repository audit remains available only on explicit request.
---

# Review Delivered User Goals

Arca's default review is original user-goal acceptance, not Task code review. KAGARI Task Orchestrator owns implementation, technical tests, code review and correction. Do not rerun those phases from Arca merely because a Task has finished.

## Select the narrow review mode

- **User-goal acceptance (default):** read [user-goal acceptance](references/user-goal-acceptance.md). Compare the original approved outcome and function-level Issue scope against observed user behavior and real Task Evidence. Classify goal-satisfied, in-spec-defect (return to KAGARI Task), specification-goal-mismatch (ask User about affected requirement) or unknown (missing evidence).
- **Legacy integrated repository audit (explicit request only):** read [legacy repository audit](references/legacy-repository-audit.md) for a bounded full-repository merged-state review and candidate findings. Do not turn this into a second mandatory reviewer for KAGARI.

## Authority and evidence

Human owns product intent, material scope changes, new Issue/phase, risk and Merge/Release. A green test suite or completed Task is not proof of the original user outcome. KAGARI supplies Task/Ask/Evidence; MUSUBI is the shared UI, not a separate Task authority.

Do not start KAGARI Tasks, edit code, publish issues or Merge merely because acceptance finished. Reuse prior verified state when unchanged; **unchanged review reuses the prior marker** without a new checkpoint. Record newly verified actionable drift through repo-handoff on the canonical carrier. Never invent actual KAGARI API behavior or declare unavailable evidence PASS.
