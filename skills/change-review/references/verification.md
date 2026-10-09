# Evidence and meaningful verification

Use this policy in patch-plan packets, OpenCode results, change-review and dev-loop completion reports. Resolve it through the installed `change-review` skill. Copy applicable requirements into a self-contained packet; do not make remote executors discover Arca's skills.

## Bind a claim to a check

Before saying a behavior works or a task is complete:

1. Identify the precise claim and the check that can establish it.
2. Inspect the actual command and complete available result, including exit status, failures, skips and whether execution finished.
3. Match the run to its immutable commit or frozen content manifest, environment, inputs and scope.
4. Compare those facts with the current target. State any gap instead of extrapolating.

Retain one compact evidence entry per check:

| Field | Required content |
|---|---|
| Identity | Run/revision plus exact commit or frozen manifest digest |
| Check | Command or reproducible procedure, relevant inputs and checked behavior |
| Environment | Relevant runtime, dependencies, platform and configuration; no secrets |
| Result | `pass`, `fail`, `blocked`, `not-run` or `timed-out`; exit status or explicitly unavailable |
| Coverage | Scope, counts/skips and whether all required shards or cases finished |
| Evidence | Readable log/artifact reference, observation time and executor/reviewer provenance |
| Applicability | Applicable, superseded or unverified for the current target, with reason |

Tool acceptance, an executor's success message and independent review are separate facts. A checked log can establish that a particular run passed; independent review additionally checks the contract, changed code and whether the test could detect the relevant defect. Do not describe author-reported results as independently rerun.

## Keep claims within their scope

- A successful linter does not establish a build or runtime behavior.
- An import/collection failure caused by missing runtime dependencies is an environment blocker, not an observed behavioral regression or a passing test.
- A timed-out full suite remains timed-out. Passing focused runs establish their named scope. Claim full coverage from shards only when their complete membership and results match the required suite at the same snapshot and compatible environment; never call that a successful monolithic run.
- A regression test observed failing for the expected behavioral reason and then passing supports the repair. A test only observed passing has no demonstrated pre-fix sensitivity; report that limit without destroying existing code.
- A clean independent review is a recommendation at its pinned snapshot. It does not grant publication, Ready or Merge.

## Revalidate without repeating everything

Reuse readable evidence when the tested content, relevant dependencies/configuration and check scope are demonstrably applicable. Read the artifact and compare current identities before reuse; do not refresh only its timestamp or rely on memory. If applicability cannot be established, mark it unverified and rerun the relevant check on an authorized safe surface when feasible.

After a change, rerun checks affected by that change and required repository gates. Expand to broader checks for a concrete integration risk. Do not rerun every suite on each response merely to make the evidence recent. Keep independent unaffected streams moving when their contracts permit it; isolate existing baseline failures instead of silently fixing unrelated problems.

Run repository tests only within their operation grant and a known safe environment. Check for external writes, required services and credentials before execution. A missing safe test surface is a disclosed limitation; it does not authorize production probes, host setup, dependency installation or network changes.

## Test the behavior that matters

Before adding or demanding a test, name the defect it should catch and derive the expected outcome from the approved requirement or an independently checked fixture.

- Avoid using the implementation or its helpers to calculate both actual and expected results.
- Exercise observable outputs, state transitions, side effects, error handling or compatibility. Do not merely search source text for implementation fragments or assert that a mock exists.
- Test boundary behavior around configurable values, including alternate valid settings. Do not freeze editable budgets, warning margins or incidental wording unless exact values are themselves an explicit accepted contract.
- Keep relevant internal behavior real; replace only the external or expensive boundary when needed. Use faithful success and error fixtures so one permissive mock cannot satisfy every branch.
- Mentally remove a required side effect or choose a wrong branch: identify which check would notice. If none would, improve the smallest relevant check rather than padding coverage.
- Human prose, simple reversible value edits and trivial forwarding need no ceremonial test. Format/frontmatter/link validation checks structure only. Evaluate a materially changed skill or prompt by an agent using it on realistic inputs, not by counting matching strings.

Prefer a small failing behavioral example before a repair when practical. If adding regression coverage to existing work, use an isolated before/after surface or a narrowly controlled counterexample when justified. Never reset, delete or rewrite someone's working code to manufacture a test-first history.

## Report the limit

State what passed, what remains unverified, why it matters, and the smallest next check that resolves it. Use test names, counts and evidence references only as precisely as the artifacts support. Stop optional verification once the material uncertainty and required gates are resolved.
