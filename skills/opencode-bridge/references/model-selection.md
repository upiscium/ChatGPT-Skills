# OpenCode model selection

Use **GPT-6.1 Sol** with **high** reasoning effort for OpenCode sessions launched or selected for this workflow unless the user explicitly requests another selection. This preference applies to the OpenCode executor, not Arca's own model or separately assigned child-agent models.

## Resolve the installed interface

- Inspect the installed version, the relevant command's help, and the available model/variant metadata before choosing syntax. Resolve the exact provider/model ID; do not infer it from a display label.
- The configured OpenCode 1.18.30 installation was checked on 2026-10-09: `openai/gpt-6.1-sol` is named `GPT-6.1 Sol`, and its `high` variant sets `reasoningEffort: high`. Revalidate availability on the selected target; do not substitute a fast/ultrafast alias or another provider silently.
- Read only needed model and variant fields. Do not dump credentials or full host configuration to discover a model.

## Select both settings before work

- For a supported `opencode run` invocation, use `--model openai/gpt-6.1-sol --variant high` together, including on continuation of the exact session. Confirm the installed help first. These are model-selection arguments, not a complete launch command or permission to create a new run.
- For the full TUI, use its supported `--model` flag when an initial launch is authorized, then select and verify the `high` variant through the installed session/UI controls before submitting the packet. OpenCode 1.18.30's top-level TUI help does **not** advertise `--variant`; do not copy that flag from `run` to the TUI or assume model selection resets effort.
- For an existing session or structured API, use the supported per-session/per-message model and variant controls. Preserve the exact session, agent, worktree and transport binding. Do not invent endpoints or restart a session to change its model.
- Inspect effective selection metadata or the session UI, including applicable agent/variant overrides. The requested flags, a prompt saying which model to use, or an assistant's self-description alone are not proof of the effective setting. Record what is selected before submission and any observed request/result metadata during the existing receipt budget; do not add a monitoring loop.
- If the session is busy, leave it running and apply the preference at the next authorized idle/resume boundary. A status or collect request never changes its selection. If no supported control can establish both settings, keep new work unsent and report the exact missing capability or unavailable model; request a substitute only when needed.

Use invocation/session-scoped controls. Do not change global host defaults, credentials or repository-owned model allocations as an incidental fix. Model selection does not grant launch, dispatch, interruption or implementation authority.

## Carry the selection across handoffs

Include requested display name, resolved provider/model ID and effort/variant in every execution packet. Keep observed values, evidence reference and verification time separate; retain `unknown` honestly. Repeat the requirement in manual handoffs. A mismatch remains visible in collection and recovery, and never permits an automatic resend. Use the current user preference for the next authorized turn while preserving the historical settings of an existing run.

Primary references: [OpenCode models](https://opencode.ai/docs/models/) and [CLI](https://opencode.ai/docs/cli/). Installed help and runtime metadata determine support for the selected version.
