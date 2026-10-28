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
    def test_human_review_default_kagari_ownership(self):
        s = source('skills/human-review/SKILL.md')
        self.assertIn('owning KAGARI Task Orchestrator', s)
        self.assertIn('legacy technical-audit mode', s)
        self.assertIn('MUSUBI presents', s)
        self.assertIn('explicitly selected legacy OpenCode workflow', s)
        self.assertNotIn('SwitchBoard owns monitoring', s)

    def test_user_goal_acceptance_reports_evidence_scope(self):
        s = source('skills/repo-review/references/user-goal-acceptance.md')
        for phrase in ('limited smoke or fixture success',
                       'actual user-workflow acceptance',
                       'integration/completion is demonstrably pending',
                       'lacks direct user-operation evidence',
                       'evidence is stale or inaccessible',
                       'not new statuses or approval gates'):
            self.assertIn(phrase, s)

    def test_shared_default_and_legacy_monitoring_owners(self):
        default_docs = (
            'skills/human-review/SKILL.md',
            'skills/repo-handoff/references/execution-contract.md',
            'skills/repo-handoff/references/record-and-restore.md',
            'skills/repo-status/references/quality-and-gates.md',
        )
        for path in default_docs:
            with self.subTest(path=path):
                content = source(path)
                self.assertIn('KAGARI', content)
                self.assertIn('MUSUBI', content)
                self.assertIn('legacy OpenCode workflow', content)
                self.assertIn('SwitchBoard', content)
        contract=source('skills/repo-handoff/references/execution-contract.md')
        self.assertNotIn('Ask monitor/notification owner '+chr(96)+'SwitchBoard'+chr(96), contract)
        self.assertNotIn('SwitchBoard/MUSUBI retains Ask monitoring', contract)
        self.assertNotIn('Ask monitoring and notifications belong to SwitchBoard',
                         source('skills/repo-handoff/references/record-and-restore.md'))
        self.assertNotIn('Ask monitoring/notification belongs to SwitchBoard',
                         source('skills/repo-status/references/quality-and-gates.md'))

    def test_monitoring_schema_has_native_owner_and_separate_ui(self):
        import json
        schema=source('skills/repo-handoff/references/state-schema.md')
        fence=chr(96)*3
        example=json.loads(schema.split(fence+'json\n',1)[1].split('\n'+fence,1)[0])
        monitoring=example['runs'][0]['monitoring']
        self.assertEqual(monitoring['owner'], 'KAGARI')
        self.assertEqual(monitoring['notification_consumer'], 'MUSUBI')
        self.assertEqual(monitoring['delivery_state'], 'unknown')
        self.assertIn('explicitly selected legacy OpenCode workflow', schema)
        self.assertIn('Do not rewrite historical markers', schema)

    def test_no_arbitrary_single_stage_default(self):
        g=source('skills/dev-loop/references/governance.md')
        self.assertIn('without one-substantive-stage-per-response throttling',g)
    def test_skill_ui_routing_and_legacy_invocation(self):
        import yaml
        def agent(name):
            return yaml.safe_load(source('skills/' + name + '/agents/openai.yaml'))
        dev = agent('dev-loop')
        review = agent('repo-review')
        patch = agent('patch-plan')
        self.assertIn('approved function-level Issue specifications',
                      dev['interface']['default_prompt'])
        self.assertNotIn('advance the current authorized OpenCode checkpoint',
                         dev['interface']['default_prompt'])
        self.assertIn('actual delivered user-visible behavior',
                      review['interface']['default_prompt'])
        self.assertNotIn('review this merged repository',
                         review['interface']['default_prompt'])
        self.assertIn('Legacy', patch['interface']['display_name'])
        self.assertFalse(patch['policy']['allow_implicit_invocation'])
        self.assertTrue(dev['policy']['allow_implicit_invocation'])
        self.assertTrue(review['policy']['allow_implicit_invocation'])
    def test_legacy_orchestration_reviewers_do_not_implicitly_route(self):
        import yaml
        for name in ('opencode-bridge', 'opencode-reviewer', 'change-review',
                     'debug-investigate'):
            with self.subTest(skill=name):
                data=yaml.safe_load(source('skills/' + name + '/agents/openai.yaml'))
                self.assertIs(data['policy']['allow_implicit_invocation'], False)

if __name__=='__main__': unittest.main()
