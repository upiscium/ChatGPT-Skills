# Role discovery and launch compatibility

## Resolve roles in the target context

Inspect installed help before using examples. Run discovery in the same working directory, approved environment wrapper and configuration context as the intended runtime. When attaching, the server's agent list is authoritative for that server. File names and a successful local listing do not prove a remote role exists.

```text
opencode --version
opencode agent list
opencode debug agent <exact-listed-role>
opencode run --help
opencode serve --help
```

Do not use `debug agent --tool` merely to inspect configuration: that option executes a tool. Keep discovery read-only. Retain raw output privately when needed; print only relevant names, modes, descriptions, model settings and permissions. Agent-list permission arrays can run into the next header without a newline in 1.18.30. A line-start-only filter can silently omit roles; confirm absence against unfiltered output or structured `/agent` data.

## Choose the route

| Effective role/runtime | Supported choice | Check before calling it started |
|---|---|---|
| Repository-owned reviewer lifecycle | Its advertised discovery and launch APIs | Role, snapshot, session and repository gate evidence |
| Verified OpenCode session/message API | Fresh session; exact `agent` on creation and submission | Created session binding and actual assistant metadata |
| `primary` or `all` role with compatible CLI | Exact `--agent`; omit model/variant arguments | No fallback warning; actual agent and exposed model metadata |
| `subagent` with CLI that requires primary | Verified API, or approved fresh parent using Task/@ | Actual reviewer/child identity and its model, not the parent label |
| Missing role, unsupported route, permission denial | Report the concrete blocker and preserve state | No invented substitute, mode promotion or permission widening |

OpenCode **1.18.30**, checked 2026-10-10: `run.ts` rejects both unknown agents and `mode: subagent` for its `--agent` selection, warns, then uses the default agent. The same check exists for `run --attach`. Exit code zero is therefore insufficient evidence. Do not use `--pure`, a config override changing mode, or a more privileged role to evade that check or other policy.

## Verified session API example

Inspect the selected server's `/doc` first; schemas differ between versions. Use the configured authenticated transport. If an authorized dedicated process is necessary, `opencode serve --hostname 127.0.0.1 --port 0` is supported by 1.18.30. Discover the actual returned port; do not assume 4096, reuse another task's port, install a daemon or disable authentication. Register actual process identity, owner, consumers and report-collection cleanup trigger with `@workspace-cleanup`. Preserve it after the receipt budget while work remains outstanding, then release the owned runtime after evidence collection and eligibility checks.

On 1.18.30, use `GET /path` to verify the effective directory and `GET /agent` for roles and exposed model settings. Filter sensitive configuration before presenting any output. Create one fresh session with the exact role and no model override:

```json
{
  "title": "<review-run-id>",
  "agent": "<exact-listed-role>"
}
```

Submit this to `POST /session`, then read back the actual ID, agent, exposed model metadata and effective restrictions. Do not add permissive session rules. Additional denial-only restrictions may narrow the review; they must not remove or override a denial. Bind and save dispatch intent before sending the review packet.

Submit literal JSON to `POST /session/<actual-session-id>/prompt_async`:

```json
{
  "agent": "<exact-listed-role>",
  "parts": [{"type": "text", "text": "<complete authorized review packet>"}]
}
```

Omit `model` and `variant` entirely from creation and submission; do not send placeholder values or copy discovery results into these fields. Let OpenCode apply its native role/session/default selection. Do not add `tools: true`, replace the role prompt, or change permissions to get a stalled review past a gate. A `204` proves submission acceptance only. Read the bound session/messages during the existing receipt budget and record assistant `agent`, exposed `providerID`, `modelID`, `variant`, completion/error and evidence provenance. Keep observed runtime facts separate from configuration; unavailable metadata remains `unknown`.

The 1.18.30 prompt schema makes model and variant optional. Its implementation selects the configured agent model when present, otherwise the native current/default model, and applies the agent variant when applicable. Earlier runtime smoke checks verified both reviewer roles through this API with explicit overrides; those checks establish role-route compatibility, not a runtime test of the no-override examples above. Verify current execution metadata without pinning those historical settings.

## Failure handling and continuation

- Role not found: re-check the same directory/environment and complete list once; do not create a role automatically.
- Subagent CLI fallback: treat it as wrong-role execution. Preserve the submitted session if any; use the compatible route only after resolving whether work ran. A generic agent's result is not the requested reviewer result.
- Configured model unavailable: report the actual provider/model error and preserve state. Do not inject another model, change effort, or rewrite configuration to make the review run.
- Permission/Ask blocked: return the needed authorized action to the coordinator. Do not grant broad permissions, use `--auto`, or route around a denial.
- Startup/connection error: keep the sanitized error, cwd/version/role/mode, actual process/request IDs and last confirmed state. A tool-returned running handle requires reading that handle, not relaunching.
- Timeout/rate limit: preserve the existing session and report unknown/waiting; do not fan out duplicate reviewers or start a monitoring loop.

For Task/@ invocation, use only the live repository's allowed parent-to-reviewer call graph. Pass a self-contained neutral packet, keep a fresh child context, and record its actual session. Preserve the child's OpenCode-configured model/effort and observe its metadata; a parent's selection does not establish the child's selection. Do not inject parent or child model overrides or rewrite repository-owned reviewer allocations.

Primary references: [Agents](https://opencode.ai/docs/agents/), [Server API](https://opencode.ai/docs/server/), [v1.18.30 CLI selection](https://github.com/anomalyco/opencode/blob/v1.18.30/packages/opencode/src/cli/cmd/run.ts), [v1.18.30 prompt selection](https://github.com/anomalyco/opencode/blob/v1.18.30/packages/opencode/src/session/prompt.ts). The installed API schema and repository lifecycle are authoritative for an actual run.
