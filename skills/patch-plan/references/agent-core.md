## Prepare Agent Core execution

In `agent-core` mode, produce one self-contained Main Orchestrator batch packet plus one Task record per workstream. Follow the live repository contract; when it exposes the current Templates lifecycle, require the coordinator to:

1. Initialize the Main session from the default-branch worktree and stop on any initialization failure.
2. From the default-branch worktree, create each explicitly selected new Issue's Task only through `just agent::task-start-from-issue <numeric-issue> <slug>`. Run the matching initial contract check and retain the complete `status: READY`, `mode: initial`, Task ID, worktree, and contract checksum evidence. Creating a Task does not authorize starting another Issue.
3. For an existing already-launched resumable Task, use only the repository's resume readiness path. Never recreate, rehydrate, reset, or replace it to manufacture readiness. Treat non-resumable or post-publication states through the Main-owned lifecycle instead of starting a replacement Task.
4. When at least two explicit Tasks are ready, run the repository's batch safety check, such as `just agent::batch-plan <task...>`. Treat its dependency, scope, coordination-surface, and external-resource conflicts as serialization constraints. Do not auto-discover additional Tasks.
5. Launch exactly one Task Orchestrator per parallel-safe Task, up to available concurrency, with that Task's complete readiness handoff. Do not launch generic implementation SubAgents in place of Task Orchestrators.
6. Keep each Task Orchestrator inside its assigned Task worktree. It may delegate its own bounded Work Units only according to the repository call graph, then stop at the packet's authorized boundary. Draft PR preparation/publication is not automatic.
7. Preserve partial progress: one blocked, failed, or decision-waiting Task does not cancel or rewrite independent Tasks. Continue only work that the batch plan still marks parallel-safe.
8. Leave merge, post-merge finalization, and cleanup with the Main/human authorities defined by the repository. Identify the current supported cleanup route and owner in the handoff so `@workspace-cleanup` can invoke it after its gates pass; do not silently omit finalization or replace it with generic Git commands.

Do not also apply the generic worktree setup below in `agent-core` mode.
