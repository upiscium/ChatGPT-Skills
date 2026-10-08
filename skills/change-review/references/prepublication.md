# Frozen prepublication review

Use repository-owned freeze/manifest APIs when present, without running publication or other guarded mutations. Otherwise collect a read-only manifest of the exact proposed delta. Do not reset, stage, commit, stash, clean or disturb the executor to obtain it.

## Required identity

- Repository, canonical Issue/Task, workstream, run and instruction revision/digest
- Source base SHA and current HEAD when applicable
- Scope: staged-only, all worktree changes or another explicit frozen selection
- Every included path and disposition: add/modify/delete/rename; content hash, mode/type; binary/generated/submodule identity where applicable
- Explicit exclusions, including untracked paths, and reason
- Manifest digest, immutable artifact reference and capture time
- Test commands/environment/results and the exact snapshot tested

Compare the manifest before and after inspection. Read only an immutable copy, or stop on mutation. Do not claim a whole-worktree verdict when only the index or a partial patch was inspected. Unreadable binaries or unavailable relevant files are evidence gaps, not implicit passes.

## Independent evidence

Reconstruct accepted intent before looking at the executor's proposed solution. Inspect full relevant code, tests and callers. Re-run safe relevant checks in an isolated surface when authorized; otherwise state source-only limits. An executor's report can point to evidence but cannot substitute for it.

## Publication handoff

Return the frozen identity, criterion traceability, findings, and `ready-for-publication-review|changes-required|blocked`. Include the exact still-required publication authority, allowed operations and stop point. Never infer commit, push, Draft PR, Ready or Merge approval from review readiness.

After a separate authorized publication, compare published content with the frozen selection and revalidate current base/CI/PR gates. Any material divergence requires a fresh review of the affected snapshot. Preserve CHG-to-PR finding mappings and the prior evidence trail.
