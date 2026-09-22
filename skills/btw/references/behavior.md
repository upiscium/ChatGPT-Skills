# BTW behavior reference

`/btw [question]` in Claude Code is documented as a side question about the current session that does not enter the conversation history. This skill adopts the same user-facing contract while adapting to a skill-based chat surface:

- one question and one answer;
- no tools or writes by default;
- no effect on the main workflow;
- an explicit indication of whether the answer is merely informational or needs promotion;
- a separate main-task request for any live inspection, implementation, Issue/PR mutation, or decision.

Do not promise UI behavior such as a dismissible overlay or hidden transcript in Codex. Promise only the semantic guarantees above.
