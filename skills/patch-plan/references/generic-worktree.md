## Prepare generic SubAgent execution

In `generic-worktree` mode, produce a separate self-contained instruction packet for every parallel workstream that can be assigned to one Codex SubAgent without access to the other packets.

Require the implementation coordinator to:

1. Allocate at most one active SubAgent per workstream, bounded by available concurrency.
2. Before creating the first worktree, resolve the repository root with `git rev-parse --show-toplevel` and inspect the root `.gitignore`.
3. Require the exact anchored entry `/.worktrees/` in the committed root `.gitignore`. Verify it with `git check-ignore .worktrees/`. If absent, stop and propose a separately authorized minimal setup PR. Ready/Merge is user-executed; verify the merge, refresh the base SHA, and only then create worktrees.
4. Create every worktree inside `<repository-root>/.worktrees/<workstream-id>` from the refreshed verified base SHA. Do not use a sibling directory, `/tmp`, a workspace-global directory, or another external path.
5. Give each SubAgent a unique branch and its assigned repository-local worktree.
6. Prevent SubAgents from editing the coordinator's working tree or another workstream's branch.
7. Preserve workstream scope and report unexpected overlap before continuing.
8. Collect results, validation evidence, branch names, head SHAs, and PR URLs without merging branches locally.
9. Run authorized cross-workstream integration checks on pinned frozen results or PRs when a safe isolated combined test surface exists; do not require unauthorized PR publication just to test.

Use worktree commands equivalent to:

```bash
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
rg -xF '/.worktrees/' .gitignore
git show '<verified-base-sha>:.gitignore' | rg -xF '/.worktrees/'
git check-ignore .worktrees/
git worktree add ".worktrees/WS-001" -b '<unique-branch>' '<verified-base-sha>'
```

Do not let `mkdir`, `git worktree add`, or a SubAgent silently create worktrees before the ignore prerequisite passes.

If fewer SubAgent slots are available than parallel workstreams, queue the remaining workstreams within the same wave rather than combining their scope.
