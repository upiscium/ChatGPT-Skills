---
name: pr-merge
description: Explicit legacy alias for @pr-merge. Route the named PR to @dev-loop merge-command-only mode; never start a full loop or execute Ready or Merge. Do not use automatically.
---

# Compatibility entrypoint

Keep this alias only for explicit legacy invocations during migration. Do not execute an independent legacy workflow.

Read the installed `@dev-loop` skill completely and route the exact user request to it. Use only merge-command-only mode and its required reference; do not initiate other development-loop stages.

If the replacement is unavailable, stop and report that dependency. Do not fall back to old instructions, invent a review, broaden authority or execute Ready/Merge. Preserve the replacement's live verification, recording and human gates.
