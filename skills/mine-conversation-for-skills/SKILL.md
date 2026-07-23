---
name: mine-conversation-for-skills
description: Analyze the current conversation, supplied transcripts, or handover material to identify reusable workflows that should become personal skills, distinguish them from prompts, AGENTS.md guidance, automations, and plugins, then help create and install the user-approved candidates. Use when the user asks what in a conversation can be skillized, wants repeated work turned into skills, or wants to mine past discussions for reusable Codex workflows.
---

# Mine a Conversation for Skills

Extract durable, reusable workflows from conversation evidence and turn only the strongest user-approved candidates into personal skills.

Read [references/candidate-rubric.md](references/candidate-rubric.md) before ranking candidates.

## Establish the source

1. Use the current visible conversation by default.
2. When the user supplies a transcript, handover, notes, or project history, include that material.
3. If the user requests earlier conversations not present in context, retrieve personal context only through the applicable personal-context workflow. If unavailable, ask for a transcript or handover instead of inventing history.
4. Record important gaps in the evidence.

Do not treat profile facts or remembered preferences as proof that a workflow has been repeated.

## Inventory existing capabilities

Before proposing candidates:

1. Inspect the available skill names and descriptions.
2. Check personal skills for overlapping triggers, workflows, or resources.
3. Prefer updating an existing personal skill when the new behavior is a coherent extension.
4. Reject candidates already covered adequately by a system, plugin, or personal skill.

Do not create multiple narrow skills that compete for the same trigger.

## Extract candidate workflows

Look for:

- Repeated multi-step procedures
- Recurring review or decision frameworks
- Stable domain-specific constraints and checklists
- Output formats repeatedly reconstructed
- Tool sequences with important ordering or safety boundaries
- Troubleshooting playbooks with reusable diagnostic gates
- Handoffs between research, planning, implementation, verification, and publishing

Separate the reusable procedure from the specific incident, repository, device, version, or answer that revealed it.

Exclude:

- One-off factual questions
- Simple explanations the model already handles well
- Unstable collections of current facts better handled by search
- Secrets, credentials, private identifiers, or raw personal history
- Preferences that belong in a prompt or user settings
- Repository conventions that belong in `AGENTS.md`
- Scheduled work that belongs in an automation
- Bundles requiring commands, hooks, MCP configuration, or multiple capabilities that should be a plugin

## Choose the correct surface

For every candidate, decide among:

- `skill`: A reusable task workflow, domain procedure, reference, template, or script
- `existing-skill update`: A coherent extension of an installed personal skill
- `AGENTS.md`: Durable instructions scoped to one repository or subtree
- `automation`: Scheduled, recurring, or condition-triggered work
- `plugin`: A distributable bundle involving multiple skills, tools, hooks, commands, apps, or MCP setup
- `prompt only`: A one-time instruction or lightweight preference
- `do not preserve`: Sensitive, too narrow, redundant, or unstable material

Explain the decision briefly. Do not force every useful pattern into a skill.

## Rank and present candidates

Score candidates with `references/candidate-rubric.md`. Present at most five strong candidates unless the user asks for a full inventory.

Use this table:

| ID | Candidate | Recommended surface | Evidence | Reusable outcome | Score | Overlap or risk |
|---|---|---|---|---|---:|---|

Then provide, for each recommended skill or update:

- Proposed name
- What it does
- Example trigger phrases
- Core workflow
- Reusable references, scripts, or assets
- What must remain out of scope
- Missing decisions needed before creation

State explicitly when no candidate clears the quality threshold.

## Require a creation decision

Discovery does not authorize persistent creation.

1. Ask the user to select candidate IDs, modify them, or approve all candidates above a stated threshold.
2. Treat an explicit request such as “create the best three” as approval for those three.
3. Do not install rejected, ambiguous, or below-threshold candidates.

## Create approved skills

For each approved candidate:

1. Use the current `skill-creator` workflow.
2. Clarify only missing details that materially affect triggering, scope, resources, or safety.
3. Create one skill at a time.
4. Validate and install it before starting the next.
5. Re-check overlap after each installation because the remaining candidates may now be redundant.
6. Report which candidates were created, merged into existing skills, deferred, or rejected.

Never recursively propose this skill itself as a new candidate.

## Privacy and quality gate

Before presenting or creating anything, verify that:

- Conversation evidence supports the claimed workflow.
- The candidate saves meaningful repeated reasoning or tool work.
- Its triggering boundary is distinct from existing skills.
- Stable procedure is separated from transient facts.
- Sensitive details are omitted or generalized.
- The recommended surface is the smallest one that fits.
- Maintenance cost is justified by expected reuse.
- Persistent creation remains under the user's control.
