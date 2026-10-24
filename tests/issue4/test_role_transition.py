"""Static contract checks for Issue #4 first slice, not runtime model evidence."""
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
def source(path): return (ROOT / path).read_text(encoding='utf-8')
class RoleTransitionTests(unittest.TestCase):
    def test_default_route(self):
        root=source('skills/dev-loop/SKILL.md')
        self.assertIn('requirements-and-acceptance.md',root)
        self.assertIn('KAGARI owns Issue execution',root)
    def test_two_human_alignments(self):
        self.assertIn('first human-alignment summary',source('skills/blueprint/SKILL.md'))
        self.assertIn('second focused human alignment check',source('skills/issue-filer/SKILL.md'))
    def test_spec_before_execution(self):
        s=source('skills/dev-loop/references/requirements-and-acceptance.md')
        self.assertIn('not-dispatched',s)
        self.assertIn('Task execution authorization',s)
    def test_runtime_ask_and_technical_review_ownership(self):
        gov=source('skills/dev-loop/references/governance.md')
        self.assertIn('KAGARI/Task Orchestrator:',gov)
        self.assertIn('MUSUBI:',gov)
        self.assertIn('no routine technical code review',gov)
    def test_goal_outcome_categories(self):
        a=source('skills/repo-review/references/user-goal-acceptance.md')
        for x in ('goal-satisfied','in-spec-defect','specification-goal-mismatch','unknown'):self.assertIn(x,a)
    def test_no_unapproved_effects(self):
        d=source('skills/dev-loop/SKILL.md')
        for term in ('Always save/read back dispatch intent before sending','Never disclose secrets','silently merge or release'):self.assertIn(term,d)
    def test_no_arbitrary_single_stage_default(self):
        g=source('skills/dev-loop/references/governance.md')
        self.assertIn('without one-substantive-stage-per-response throttling',g)
if __name__=='__main__': unittest.main()
