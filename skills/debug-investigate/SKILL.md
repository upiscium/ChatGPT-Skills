---
name: debug-investigate
description: Investigate a concrete test, CI, build, runtime or performance failure through bounded reproduction, boundary tracing and discriminating hypotheses. Use when the cause is unclear, a fix failed or repeated guesses are not working. Produce evidence and a scoped investigation or repair handoff; do not implement repairs, publish changes or monitor OpenCode.
---

# Investigate a Failure

Find what failed and why before selecting a repair. Own diagnosis and evidence; send authorized implementation to OpenCode through `@patch-plan`, `@dev-loop` and `@opencode-bridge`. Do not turn a plausible explanation into a confirmed cause.

Read [references/investigation-record.md](references/investigation-record.md) for the compact report. Read `@change-review`'s `references/verification.md` when checking result claims. [references/superpowers-notice.md](references/superpowers-notice.md) records the adapted source and license.

## Bind the investigation

Resolve the supplied failure, expected behavior, repository/version or frozen snapshot, environment, run identity and existing workstream. Reuse relevant supplied logs; collect only the missing observations. Read applicable repository instructions before commands.

Start with read-only source/log inspection and safe, bounded diagnostics. Inspect test commands before running them: tests may write databases, access devices or change remote services. Use an already authorized isolated surface for reproduction. If one is unavailable, finish source-based diagnosis and specify the missing probe or delegate it within an approved grant. Do not change host/network/security settings, install dependencies, add instrumentation to product code or operate production systems implicitly.

Keep secrets and unrelated personal data out of evidence. Report only allowlisted non-sensitive values or presence/absence when configuration propagation matters; do not dump environment variables or credentials. Preserve existing dirty work and sessions.

## 1. Establish the observed failure

- Read the full relevant error and stack trace, command, exit status and surrounding events.
- Write expected versus actual behavior and a minimal reproducer or explain why reproduction is unavailable.
- Classify failure stage: setup, import/collection, build, assertion, runtime, performance or external dependency. Missing setup is not proof of a product regression.
- Compare the failing snapshot and environment with the nearest relevant working case; inspect recent changes without assuming the most recent change caused it.

For intermittent failures, record observation counts and conditions. Absence during one retry does not prove a fix. Bound the number and cost of attempts to the question being answered; do not start continuous monitoring.

## 2. Trace the first divergence

Follow the erroneous value or missing event backward to where actual behavior first differs from the contract. In a multi-component path, compare inputs, outputs, configuration propagation and state at each relevant boundary. Use existing logs first. If instrumentation is needed, specify the smallest redacted observation and the operation authority it requires.

Compare a known working path in the same codebase or an applicable primary reference. Check version and environment differences. Distinguish correlation, mechanism inferred from source and reproduced causal evidence.

## 3. Test competing explanations

Record a small ranked set of hypotheses. For each, state supporting and contradicting evidence, a predicted observation, and a minimal check that distinguishes it from alternatives.

Test one variable at a time on the authorized surface. Keep results, including failed hypotheses, so a later session does not repeat them. A failed check means revise the explanation, not stack more speculative fixes. A change that merely suppresses the symptom is not evidence of its cause.

When repeated probes or repairs fail, re-examine the model and shared assumptions before another attempt. Three unsuccessful repair attempts are a practical signal to revisit coupling and architecture, not proof that the architecture is wrong. Continue bounded evidence gathering where useful; ask a human only for an actual material scope, authority or risk decision. Do not introduce a universal three-attempt approval ritual.

If evidence supports an external or environmental cause, name the boundary and uncertainty. Do not blame the environment merely because local code inspection found nothing.

## 4. Return the diagnosis and next bounded action

Return the observed failure, cause status (`confirmed|supported|unresolved`), evidence, rejected alternatives, remaining uncertainty and next action. Propose a repair only as strongly as the evidence permits. Include the behavioral regression to demonstrate, relevant baseline, safe check and exact stop point.

- Existing Issue/workstream: preserve its IDs and send the result to its coordinator; existing change corrections remain in the same workstream.
- New merged-state defect without an Issue: hand evidence to `@repo-review` for a finding. Use `@issue-filer` only when filing is authorized and its input requirements are met.
- Unknown cause: produce a bounded investigation packet, not a guessed executable repair.
- A material design choice: route to `@blueprint` or `@human-review` with evidence and concrete options.

Use `@repo-handoff` for an existing canonical carrier when recording is authorized under the active instructions; otherwise return a continuation delta or `bootstrap`/`pending-write`. Keep raw sensitive logs out of public records. Diagnosis does not grant dispatch, code edits, commit, push, PR, Ready or Merge. SwitchBoard owns ongoing Ask monitoring.

## Final check

Verify that every factual claim names its evidence and snapshot, the proposed probe can distinguish alternatives, no permissions were inferred from access, and the next action stays inside its grant. Report partial evidence plainly and stop once the question is resolved or the next required observation is concrete.
