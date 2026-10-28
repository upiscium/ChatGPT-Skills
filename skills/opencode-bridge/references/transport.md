# Transport preflight and fallback

Use only the connection explicitly selected by the user or verified configuration. Discover the relevant connected tool descriptions; credentials remain with configured tools. A permission failure is a stop, not a reason to switch hosts/transports.

## Read-only binding

Verify the device identity and exact repository/session from minimal observations. If Remote Desktop Commander is selected, use its advertised device selection and process/session APIs. Its process ID or tool-call ID is not automatically an OpenCode session ID.

If an existing tmux OpenCode session is selected, inspect its pane, command and repository context before sending. Never paste a packet into an unverified shell, broad pane selector or guessed session. Prefer a structured OpenCode message API supported by the installed version; otherwise use verified literal-input handling. Do not invent API endpoints or tmux command syntax from memory: inspect available help/docs first.

Record opaque references in public GitHub state; keep host/IP/path/session mappings in approved connection configuration. An opaque reference must be resolvable by the next authorized operator; if not, mark recovery incomplete instead of claiming repository-only recovery.

## Mandatory stdin EOF for noninteractive OpenCode CLI

**Every headless `opencode run` must begin with stdin at EOF.** On OpenCode 1.18.35, a fully specified argv prompt or `--file` does *not* stop a non-TTY parent socket from blocking before session creation. In a Python process launcher use `subprocess.Popen([...], stdin=subprocess.DEVNULL, ...)`; in a verified POSIX shell command use `opencode run ... </dev/null`. Do not pass an open pipe, inherit a Remote Desktop Commander's stdin socket, or rely on shell/tool timeout to supply EOF. A noninteractive prompt must come from argv, `--file`, or a verified session API, **never** from stdin when this rule applies.

When the packaged helper [`scripts/run-headless.sh`](../scripts/run-headless.sh) has been explicitly verified available in the *target* execution environment, prefer:

```sh
sh /verified/plugin/scripts/run-headless.sh /verified/bin/opencode --dir /verified/worktree --file /verified/prompt.md "Run the authorized packet"
```

It forwards exact arguments and exit status, requires an absolute executable path, closes fd 0, and adds no model/variant/permission flags. The example paths are placeholders, not approved host locations: verify executable, worktree, packet and grant before actual use. If that packaged script is not present remotely, use the explicit `</dev/null` launch form; do not assume a plugin-local file exists on another computer. Avoid untrusted `PATH` substitution and arbitrary shell interpolation. This is a noninteractive CLI rule; do not redirect the stdin of an intentionally interactive TUI or change its permission policy.

### Receipt-aware unattended runs through the native Session API

The shell helper is **only an EOF-safe transport** and does not prove a Session exists. For autonomous KAGARI-managed Tasks, use KAGARI's existing issue-bound `opencode serve` + Session API to create and own the exact Task Session. Do **not** implement an additional CLI subprocess/log supervisor in Arca: it duplicates KAGARI process ownership and risks unbounded capture and uncertain child cleanup.

For read-only receipt collection, when a verified authenticated loopback OpenCode server already exists, the packaged Python 3.11+ [`scripts/observe-session.py`](../scripts/observe-session.py) can observe its *existing* Session. It only issues bounded authenticated GETs: `/global/health`, `/session/<id>`, `/session/status`, `/session/<id>/message`, `/permission` and `/question`. No Session/model/process is created, no native Ask is answered, and no files are written by the probe.

```sh
python3 /verified/plugin/scripts/observe-session.py \
  --run-id <existing-authorized-run-id> \
  --session-id <actual-session-id> --agent <verified-role> \
  --expected-title <actual-bound-session-title> \
  --directory /verified/issue-worktree --port <loopback-port> \
  --password-file /verified/owner-private-0600-password \
  > /verified/private-evidence/run-receipt.json
```

Example paths and identifiers above are placeholders, not permission to launch a server, access an unrelated Session or assume the packaged script exists remotely. Verify the real API schema, target directory, exact Session ID/title/role, user grant, credential file owner/mode, and that the loopback server is already authorized before use. The probe refuses non-loopback URLs, redirects and proxies; it never sends credentials to a public host or echoes assistant content/credential values. Store the normalized JSON receipt outside the Product Worktree with appropriate private permissions.

The **underlying KAGARI launcher** owns `process_spawned` identity and recovery facts. The probe reports `opencode_initialized` only from a healthy server response, `session_created` only from exact Session ID/title/Worktree/role readback (an observation, not the authority for creation), `model_started` only from structurally valid matching assistant messages, and `completed` only from an observed terminal assistant `finish=stop`, validated output, idle Session, and no pending native Ask. Otherwise it returns `running`, `awaiting_human`, `blocked` or `unknown` with non-success exit. An absent or unreachable server, malformed response or stale Session is never treated as completed. The coordinator owns durable run/Task correlation and never blindly retries based on a failed probe.

If a standalone noninteractive `opencode run` must be used outside a KAGARI Session server, keep stdin EOF via `</dev/null` or the verified POSIX shell helper. **Without an independently verified Session or equivalent structured receipt, its process PID, output and exit status are not sufficient to claim a successfully acknowledged autonomous Task.** Use a separate authorized observation route or report `unknown`; never add broad permissions, substitute a model, or auto-retry.

**Startup is not receipt.** Separate `process_spawned`, `opencode_initialized`, `session_created`, `model_started`, and `completed` evidence. A live PID with 0-byte stdout/stderr and no session ID is *not* accepted or running work. At the bounded receipt deadline classify it as `startup_stalled/unknown`, inspect run-scoped sanitized logs/FD and current worktree, and do not resend. After proving exact process ownership and no session/in-flight effects, use the existing owned-resource cleanup gate to release only that failed launch; then a *new* run and separately verified dispatch intent may be considered. Do not kill by name or alter shared OpenCode servers.

## Dispatch safeguards

- Distinguish the chat transport's asynchronous call handle from the actual run. If a tool returns a running call ID, read that call's result; do not issue the send again.
- Treat multiline packets, shell metacharacters and instructions as literal data. Do not use eval, interpolate untrusted text into shell commands, or send commands to an uncertain pane.
- Do not overwrite a shared tmux paste buffer or inject text into a busy prompt. Use a documented isolated transport mechanism; if unavailable, return a manual handoff.
- Confirm input submission and receipt separately. An echoed input line is not an acknowledgement unless the interface supplies authoritative delivery evidence.
- Do not kill a remote operation because the receipt budget expired. Report uncertainty and preserve its identifier.
- Bounded receipt checks are dispatch acknowledgement checks, not Ask monitoring. SwitchBoard alone owns ongoing Ask detection/notifications.

## Resource lifecycle

Register persistent RDC-launched processes, OpenCode runtimes and tmux resources with `@workspace-cleanup` before/after creation. Capture the actual process identity, not just RDC's asynchronous handle; record server/pane/session IDs and whether the target is newly owned or reused. Preserve the RDC connector and shared transport itself.

Keep executing resources alive at dispatch return. After completed output is collected and saved, let the coordinator use `@workspace-cleanup` to release eligible owned resources through the same configured connection. Report partial cleanup or loss of connectivity with retained IDs; never reinterpret an unreachable host as permission to kill or relaunch.

## Manual fallback

Return the same approved packet with run/revision/digest, target, grant and stop point. State `not-sent`, who will submit it, what acknowledgement/result to return, and how the canonical record will be reconciled. Never hand the user a replacement job when the original may already have been delivered; first reconcile uncertain delivery.
