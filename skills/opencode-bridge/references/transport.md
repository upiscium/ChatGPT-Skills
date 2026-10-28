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

### Receipt-aware unattended runs

The shell helper above is **only an EOF-safe transport**; it cannot prove that OpenCode started a Session. For autonomous CLI dispatch, use either a verified native Session API with read-back of real Session/status/messages, **or** the packaged Python 3.11+ [`scripts/run-headless-receipt.py`](../scripts/run-headless-receipt.py) when that source and interpreter are verified available on the authorized target. An unattended shell invocation without one of these observation channels is not a completed dispatch receipt.

```sh
python3 /verified/plugin/scripts/run-headless-receipt.py \
  --run-id <unique-authorized-run-id> \
  --state-root /verified/owner-private-0700-state \
  --cwd /verified/issue-worktree \
  --binary /verified/bin/opencode \
  --startup-seconds 20 --runtime-seconds 600 -- \
  --file /verified/authorized-packet.md "Run the authorized packet"
```

The state root must already exist, be owned by the caller, and have mode `0700`. The helper atomically allocates one exclusive run-ID directory; it refuses reuse without reconciliation. It writes owner-private (`0600`) `receipt.jsonl` records, `stdout.jsonl`, and `stderr.log`, all outside the Product worktree; stdout/stderr may contain private data and **must not** be published or copied into an Issue. The exact Python interpreter, script, binary, cwd, packet and operation grant must be verified independently; the script never installs anything or changes OpenCode's model/permissions. It rejects `--auto`, model/variant overrides, alternate `--dir`, continuation and non-JSON format overrides. Native configured model and CLI agent role still apply.

Receipts are observations, not declarations of completion. `launch_intent` is saved before the effect; `process_spawned` records the actual PID; `opencode_initialized` follows a valid OpenCode JSON stream event; `session_created` means a valid `sessionID` was *observed in that stream* (not a guarantee of durable host ownership); `model_started` requires a matching assistant text/tool event; `completed` requires all preceding evidence and process exit 0. `exited_failure`, `exited_without_verified_completion_unknown`, `startup_stalled_unknown`, `runtime_stalled_unknown`, and `output_unbounded_unknown` must **never** be treated as PASS. A timeout returns code 75 **without terminating the child**, preserving exact process/run identity and the evidence files. Before retry or cleanup, reconcile session/child/Git/Task authority and use verified owned-resource cleanup; a different run ID alone is never retry authorization. No native Ask is auto-approved.

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
