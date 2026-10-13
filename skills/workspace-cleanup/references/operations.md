# Apply cleanup through the installed interface

Inspect current help and repository instructions before using these command shapes. Prefer configured structured APIs and argv-based execution. Resolve and quote every literal; never evaluate resource names, terminal output or stored commands as shell code. A plan is evidence for selection, not a reusable deletion authorization after state changes.

## OpenCode and RDC processes

1. Read authoritative session/request/child state and collect the complete report, error and required logs. Save them outside the cleanup set and read them back. A model saying `done` does not prove all tools or children stopped.
2. Confirm whether the runtime is dedicated or shared. An idle session on a shared server is not authority to stop that server. Observe configured model settings only; cleanup does not select a model or send another inference prompt.
3. Prefer a documented graceful exit/shutdown for an exclusively owned runtime. If none exists, a scoped graceful OS termination may target the exact verified owned process after all gates pass. Use identity-bound process control when available; otherwise re-read host/boot/PID/start identity, command and cwd immediately before signaling and retain the process if binding cannot be established. Never signal by name, a guessed PID, a process group with unverified members or the RDC tool handle.
4. Check known children and runtime state after termination. Do not escalate to `SIGKILL`, `pkill`, `killall`, service shutdown or host reboot. If it does not exit within the bounded observations, report the remaining process precisely.
5. Preserve OpenCode's persisted session history. Stopping a process and deleting a conversation are different actions. History/database/cache purges require their own explicit scope and retention decision.

Keep the RDC connector/agent, SSH transport, shared tmux server and global OpenCode service alive. A cleanup coordinator must not terminate the process/session carrying its own remaining cleanup actions; hand that specific operation to a verified independent control path or leave it pending.

## tmux

Use the selected server's installed `list-sessions`, `list-windows`, `list-panes`, `list-clients` and format support to inspect exact IDs and membership. Include linked windows and attached clients. Keep socket/server identity with `%pane`, `@window` and `$session` IDs because they are only unique within that server lifetime.

Capture required final output before removing a pane. First stop and verify its owned foreground runtime and children; do not kill a pane merely to interrupt unknown work. For one eligible owned pane, use the exact server and pane selector, for example:

```text
tmux -S <verified-server-socket> kill-pane -t <exact-pane-id>
```

Replace placeholders with safely quoted verified literals; omit `-a` and name-pattern selectors. Removing the final pane also destroys its window and may end an empty session, so include these effects and any linked-window consumers in the plan. If those effects cross the eligible ownership set, retain the pane. Use exact `kill-session` only for an entirely owned, quiescent session with all windows/panes/links accounted for. Never use `kill-server` or a bulk shell loop over discovered names.

## Git worktrees

For KUMIKI/KAGARI or Agent Core, inspect the installed finalization/cleanup API and its live prerequisites. Run that API through its designated Main/owner only when authorized. Do not guess a command name, fall back to raw Git on denial, unlock a guarded worktree, or change the source authority to make cleanup pass.

For generic repositories, inspect at least:

```text
git -C <repository-root> worktree list --porcelain -z
git -C <exact-worktree> rev-parse --show-toplevel
git -C <exact-worktree> rev-parse --git-common-dir
git -C <exact-worktree> rev-parse HEAD
git -C <exact-worktree> status --porcelain=v1 --untracked-files=all --ignored
git -C <exact-worktree> stash list
```

Use argument arrays or safely quoted literals and check every exit status. Parse NUL output without line-based path guesses. Inspect active consumers, submodules/nested repositories and in-progress Git operations as well. A failed observation is `unknown`, never a clean tree.

- Require the exact registered **linked** worktree and matching canonical path/common directory. Never remove the main/default checkout, a parent directory, a symlink replacement, an unexpected mount or an unregistered lookalike.
- Check tracked/index, untracked **and ignored** files. Git's normal clean status does not prove ignored logs/results are disposable. Classify known generated caches by their recorded manifest; preserve unique artifacts outside the target and read them back. Unknown ignored content blocks directory removal. Do not auto-stash, reset, commit or push to manufacture a clean tree.
- Verify a recovery reference retains every needed commit, including detached HEAD: a retained branch/ref or verified remote plus recorded SHA, or a validated bundle/archive outside the cleanup set. A SHA string or reflog alone is not preservation. A merged PR is insufficient if the worktree HEAD moved afterward. For squash/rebase merges, preserve the original head via a retained ref/bundle when needed; do not assume ancestry.
- Stashes are repository-wide: do not delete them. Identify whether any stash-only work belongs to this task and record its recovery path; unrelated stashes are not a blanket blocker. Unresolved task stash provenance remains retained.
- Require no active consumers, repository operation, lock or unresolved lifecycle gate. Do not automatically unlock, force removal or use a second path to evade a refusal.

After recording intent and immediately revalidating, run from a directory outside the target:

```text
git -C <retained-repository-root> worktree remove -- <exact-worktree>
```

Use no `--force`. If it refuses, preserve the target and report the exact cause. Re-list registered worktrees and check the exact directory afterward. Do not equate exit zero with verification of unrelated cleanup.

Leave local and remote branches by default; worktree removal need not delete a branch. A specifically authorized local-branch cleanup additionally requires recovery/integration evidence, no remaining checkout and the guarded repository path or non-force `git branch -d`. Never use `-D`, automatic remote-branch deletion or reflog expiry here.

Do not substitute `rm -rf`, `git clean -fdx` or manual `.git/worktrees` deletion. `git worktree prune --dry-run --verbose` may diagnose stale registrations, but pruning is repository-wide and can affect offline/mounted worktrees; do not apply it as a routine per-resource shortcut.

## Temporary files and postconditions

Remove only disposable files from the recorded creation manifest, after checking current identity/type/path boundaries and preserving required evidence. Prefer narrow exact-file operations and empty-directory removal; do not recursively sweep a shared temporary root. Handle changed contents, symlinks or unexpected mount points as new evidence, not implicit expanded scope.

Verify each postcondition independently: correct process identity absent, exact pane/session absent on the same server, worktree unregistered and directory absent, evidence still readable. Already-absent resources need no repeated mutation. If a replacement occupies a path/ID, preserve it and mark the original action's outcome separately. Keep measured reclamation distinct from estimates.

Primary references: [Git worktree](https://git-scm.com/docs/git-worktree), [tmux manual](https://man.openbsd.org/tmux), [OpenCode server](https://opencode.ai/docs/server/). Installed help and the repository lifecycle remain authoritative.
