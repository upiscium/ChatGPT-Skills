# Conversation-to-Skill Candidate Rubric

Score each dimension from 0 to 3.

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Repeatability | One-off | Might recur | Clearly recurring | Frequently repeated |
| Procedural depth | Simple answer | A few reminders | Multi-step judgment | Fragile or safety-critical workflow |
| Context savings | Negligible | Small | Material | Reconstructing context is expensive |
| Stability | Changes constantly | Several volatile assumptions | Mostly stable | Durable procedure |
| Reuse scope | One incident | One narrow project | Multiple tasks or projects | Broad recurring workflow |
| Outcome value | Cosmetic | Convenient | Meaningful quality or time gain | Prevents costly errors or unlocks major work |

Subtract penalties:

| Penalty | Points |
|---|---:|
| Strong overlap with an existing skill | -4 |
| Better suited to another surface | -4 |
| High maintenance burden | -2 |
| Sensitive or difficult to generalize safely | -3 |
| Depends mainly on current web facts | -2 |

Interpret totals:

- `14–18`: Strong skill candidate
- `10–13`: Candidate only if the user expects repeated use
- `6–9`: Usually use another surface or merge into an existing skill
- `0–5`: Do not preserve

The score informs judgment; it does not replace it.

## Evidence rules

- Cite conversation patterns by paraphrased topic or workflow, not by dumping raw history.
- One detailed occurrence can support a candidate only when the procedure is clearly reusable and expensive to reconstruct.
- Multiple similar factual questions do not automatically imply a workflow.
- User frustration is evidence of a problem, not proof that a skill is the right solution.
- Prefer one composable skill over several candidates split only by technology name.

## Candidate naming

- Use lowercase hyphen-case.
- Prefer a short verb-led action.
- Name the reusable outcome, not the conversation topic.
- Avoid generic names such as `helper`, `assistant`, `review`, or `workflow`.
