# Transport preflight and fallback

Use only the connection explicitly selected by the user or verified configuration. Discover the relevant connected tool descriptions; credentials remain with configured tools. A permission failure is a stop, not a reason to switch hosts/transports.

## Read-only binding

Verify the device identity and exact repository/session from minimal observations. If Remote Desktop Commander is selected, use its advertised device selection and process/session APIs. Its process ID or tool-call ID is not automatically an OpenCode session ID.

If an existing tmux OpenCode session is selected, inspect its pane, command and repository context before sending. Never paste a packet into an unverified shell, broad pane selector or guessed session. Prefer a structured OpenCode message API supported by the installed version; otherwise use verified literal-input handling. Do not invent API endpoints or tmux command syntax from memory: inspect available help/docs first.

Record opaque references in public GitHub state; keep host/IP/path/session mappings in approved connection configuration. An opaque reference must be resolvable by the next authorized operator; if not, mark recovery incomplete instead of claiming repository-only recovery.

## Dispatch safeguards

- Distinguish the chat transport's asynchronous call handle from the actual run. If a tool returns a running call ID, read that call's result; do not issue the send again.
- Treat multiline packets, shell metacharacters and instructions as literal data. Do not use eval, interpolate untrusted text into shell commands, or send commands to an uncertain pane.
- Do not overwrite a shared tmux paste buffer or inject text into a busy prompt. Use a documented isolated transport mechanism; if unavailable, return a manual handoff.
- Confirm input submission and receipt separately. An echoed input line is not an acknowledgement unless the interface supplies authoritative delivery evidence.
- Do not kill a remote operation because the receipt budget expired. Report uncertainty and preserve its identifier.
- Bounded receipt checks are dispatch acknowledgement checks, not Ask monitoring. SwitchBoard alone owns ongoing Ask detection/notifications.

## Manual fallback

Return the same approved packet with run/revision/digest, target, grant and stop point. State `not-sent`, who will submit it, what acknowledgement/result to return, and how the canonical record will be reconciled. Never hand the user a replacement job when the original may already have been delivered; first reconcile uncertain delivery.
