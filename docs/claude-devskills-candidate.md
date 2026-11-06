# Arca DevSkills: Claude Code source candidate

Issue: https://github.com/upiscium/ChatGPT-Skills/issues/15

This source-only track adds the Claude Code plugin identity **Arca DevSkills**
without touching the installed **Arca Development** OpenAI/Codex identity.
The repository itself is not renamed.

## Source and packaging boundary

- Canonical behavior lives in the existing skills/ tree.
- Claude candidate includes exactly blueprint, human-review, issue-filer,
  repo-handoff, repo-status, handover and their Markdown references/.
  It intentionally excludes agents/openai.yaml, icons and legacy
  execution/reviewer/merge skills.
- The candidate builder replaces cross-skill @name references with
  /arca-devskills:name for included Skills. Known references to excluded
  legacy Skills are rendered as inert descriptions. New unknown references
  cause a build failure, not implicit executor installation.
- Existing packaging/build_candidate.py, arca-development and
  arca-development-vnext-isolated source identities remain unchanged.
- A candidate does not bundle an MCP server, execution hook, agent, model
  or credentials. Neither gh availability nor a validated package confers
  repository mutation or KAGARI Task authority.
- No automatic CLAUDE_CONFIG_DIR selection or Work path routing is added
  to KAGARI. This is an interactive Adam shell convenience only.

## Offline validation (no model or plugin installation)

In an isolated checkout with Python 3.10+ and a Claude Code CLI:

~~~sh
python3 -B -m unittest discover -s tests/issue15 -v
python3 -B packaging/build_claude_candidate.py --out /tmp/arca-devskills.zip --preview-uncommitted
mkdir -p /tmp/arca-devskills-check
cd /tmp/arca-devskills-check
python3 -m zipfile -e /tmp/arca-devskills.zip .
claude plugin validate --strict .
~~~

The --preview-uncommitted flag is for isolated source development only;
production artifacts must be generated from a clean committed revision.
The builder will not overwrite an existing archive and emits its source
HEAD and SHA-256. No installation, model launch or publication is implied.

## Subsequent, separately authorized E2E

1. Load the exact reviewed candidate with claude --plugin-dir in a
   disposable environment, under the user's official Claude Code account.
2. Exercise requirement clarification and standalone Issue drafts before
   any GitHub write. Compare original-user-goal interpretation.
3. Only with exact Human authority, qualify GitHub Issue filing and one
   bounded KAGARI dispatch/receipt, followed by fresh-session acceptance.
   No automatic PR/Merge or next Issue.

The existing ChatGPT Plugin remains usable while the Claude candidate is
evaluated. A separate release/cutover plan is required for any public
identity migration.
