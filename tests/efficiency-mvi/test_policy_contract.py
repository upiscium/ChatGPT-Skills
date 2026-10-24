"""Static guardrails for the lean-context and MVI-first policy.

These checks verify documented operating rules, not actual LLM behavior.
Measure context usage and human-Ask outcomes with scenarios.md.
Run: python3 -m unittest discover -s tests/efficiency-mvi -p 'test_*.py'
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def skill(rel):
    return (ROOT / "skills" / rel).read_text(encoding="utf-8")


class ArcaPolicyContractTests(unittest.TestCase):
    def test_no_checkpoint_for_identical_status(self):
        handoff = skill("repo-handoff/SKILL.md")
        status = skill("repo-status/SKILL.md")
        self.assertIn("Do **not** write a fresh marker for unchanged reads", handoff)
        self.assertIn("Repeated read-only status with no new state", status)
        self.assertNotIn("For every repository-workflow response that observes or changes state", handoff)

    def test_dispatch_and_external_authority_not_weakened(self):
        loop = skill("dev-loop/SKILL.md")
        handoff = skill("repo-handoff/SKILL.md")
        self.assertIn("Always save/read back dispatch intent before sending", loop)
        self.assertIn("dispatch intent before sending", handoff.lower())
        self.assertIn("Never disclose secrets", loop)
        self.assertIn("silently merge or release", loop)
        self.assertIn("material change to the accepted threat model remains human-owned", loop)

    def test_context_budget_and_lazy_references(self):
        loop = skill("dev-loop/SKILL.md")
        plan = skill("patch-plan/SKILL.md")
        self.assertIn("Reuse previously loaded Skill instructions and verified state", loop)
        self.assertIn("Limit each tool response to pertinent fields", loop)
        self.assertIn("Use the relevant sections of", plan)
        self.assertIn("only when producing an execution-ready plan", plan)

    def test_mvi_risk_is_scoped_not_ignored(self):
        plan = skill("patch-plan/SKILL.md")
        review = skill("change-review/SKILL.md")
        security = skill("security-audit/SKILL.md")
        human = skill("human-review/SKILL.md")
        self.assertIn("production-deferred", plan)
        self.assertIn("Only in-scope failures block the MVI", plan)
        self.assertIn("approved stage and actually reachable effects", review)
        self.assertIn("do not automatically convert (b) or (c)", security)
        self.assertIn("Missing threat-model evidence is", security)
        self.assertIn("Preserve explicit material risk", human)

    def test_sweep_avoids_extra_tool_work(self):
        sweep = skill("human-review/references/decision-sweep.md")
        self.assertIn("Do not fetch or re-read supporting Skills", sweep)
        self.assertIn("material changes to approved risk are human-owned", sweep)


    def test_all_checkpoint_entrypoints_follow_changed_state_rule(self):
        """Static consistency check only: each route must explicitly exempt unchanged outcomes."""
        expected = {
            "issue-filer/SKILL.md": "unchanged duplicate lookup",
            "blueprint/SKILL.md": "unchanged brief reuses the prior marker",
            "security-plan/SKILL.md": "unchanged planning observation creates no marker",
            "security-audit/SKILL.md": "Unchanged read-only rechecks create no marker",
            "repo-review/SKILL.md": "unchanged review reuses the prior marker",
            "patch-plan/SKILL.md": "reuse the existing marker without writing",
            "handover/SKILL.md": "Otherwise link the prior marker without another write",
            "change-review/SKILL.md": "Unchanged rechecks reuse the previous marker",
        }
        for path, rule in expected.items():
            with self.subTest(skill=path):
                self.assertIn(rule, skill(path))

    def test_required_transitions_are_not_removed(self):
        """Do not optimize away dispatch intent or actionable state recording."""
        handoff = skill("repo-handoff/SKILL.md")
        self.assertIn("dispatch intent before sending", handoff.lower())
        self.assertIn("newly discovered failure", handoff)
        self.assertIn("material dependency/base change", handoff)
        self.assertIn("do not suppress evidence to meet a token budget", handoff)

    def test_large_skill_entrypoints_are_lazy_and_links_exist(self):
        """Static routing check: short root and real separately readable references."""
        from re import findall
        for name in ("dev-loop", "repo-handoff", "patch-plan", "repo-status", "change-review"):
            with self.subTest(skill=name):
                root = ROOT / "skills" / name
                source = (root / "SKILL.md").read_text(encoding="utf-8")
                self.assertLess(len(source.encode("utf-8")), 4200)
                links = findall(r"\]\((references/[^)]+)\)", source)
                self.assertGreaterEqual(len(links), 3)
                for link in links:
                    self.assertTrue((root / link).is_file(), (name, link))

    def test_relocated_stage_contracts_survive(self):
        self.assertIn("Complete at most one substantive stage per response",
                      skill("dev-loop/references/governance.md"))
        self.assertIn("Before external dispatch, save and read back",
                      skill("repo-handoff/references/checkpoint-policy.md"))
        self.assertIn("## Prepare Agent Core execution",
                      skill("patch-plan/references/agent-core.md"))
        self.assertIn("## Prepare generic SubAgent execution",
                      skill("patch-plan/references/generic-worktree.md"))
        self.assertIn("## 1. 実装済みで利用可能な機能・内容",
                      skill("repo-status/references/five-view-format.md"))
        self.assertIn("## Classify findings",
                      skill("change-review/references/review-method.md"))

if __name__ == "__main__":
    unittest.main()
