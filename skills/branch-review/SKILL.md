---
name: branch-review
description: Explicit legacy alias for @branch-review. Route a named pull request to @change-review PR mode; do not use automatically or run the former review procedure.
---

# Compatibility entrypoint

Keep this alias only for explicit legacy invocations during migration. Do not execute an independent legacy workflow.

Read the installed `@change-review` skill completely and route the exact user request to it. Use PR mode for a named PR. Frozen prepublication work uses the new skill's prepublication mode.

If the replacement is unavailable, stop and report that dependency. Do not fall back to old instructions, invent a review, broaden authority or execute Ready/Merge. Preserve the replacement's live verification, recording and human gates.
