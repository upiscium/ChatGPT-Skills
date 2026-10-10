# OpenCode-configured model selection

Use the model, reasoning effort and variant configured by OpenCode for the selected role/session. Arca's skills must not choose or override them. This policy supersedes older packets that pinned a model or effort; retain those values only as historical evidence.

## Preserve native selection

- For CLI launches and continuations, omit `--model` / `-m` and `--variant`. Keep an explicit agent argument when the workflow requires a particular role.
- For session creation and message APIs, omit optional `model`, `variant` and reasoning-effort override fields. Omit the fields entirely; do not send `null`, `inherit`, an empty object or a model copied from discovery. Let the installed runtime apply its own role/session/default precedence.
- For a TUI or existing session, use its current selection without operating model or variant selectors. Preserve the exact session, role, directory and configured environment; do not reset a stored choice or restart to change models.
- For child agents, preserve their own OpenCode configuration. A parent's selection does not establish the child's actual model; do not inject an override into either.
- Do not add model-selecting environment variables, inline configuration, prompt instructions or global/repository configuration changes. If an interface requires an explicit model, prefer a supported native-default route; otherwise report the concrete interface limitation instead of guessing a value.

## Observe without changing

Read only relevant configured and runtime metadata in the target context. Record actual provider/model and effort/variant when exposed, with evidence and observation time. Keep configured values separate from observed execution; a prompt or model self-description is not proof. Missing model metadata is `unknown`, not by itself a reason to block authorized work or change the selection.

Use the existing bounded receipt observations; do not add monitoring. Status and collection never change selection. Report an actual model-unavailable or provider error as a blocker without substituting another model, changing configuration or resending uncertain work.

## Carry the policy across handoffs

Include `model_policy: opencode-config` as packet metadata and state that model/effort overrides are omitted. Copy this policy into manual and independent-review handoffs. Keep observed values and evidence separate; never turn them into arguments for the next launch. Preserve historical run settings on resume, and do not replay an older pinned-model requirement into a new authorized turn.

Primary references: [OpenCode models](https://opencode.ai/docs/models/) and [CLI](https://opencode.ai/docs/cli/). Installed help, API schemas and runtime metadata determine the selected version's native behavior.
