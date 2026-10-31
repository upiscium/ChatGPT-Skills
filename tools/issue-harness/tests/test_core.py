from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from arca_issue_harness.core import ACTIONS, Harness, snapshot_sha256

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / 'fixtures'
H = Harness(FIX / 'snapshots')
DIGESTS = json.loads((FIX / 'snapshot_digests.json').read_text())


def candidate(name):
    return json.loads((FIX / 'candidates' / name).read_text())


def verify(source, value):
    return H.validate(source, DIGESTS[source], value)


def render(source, value):
    return H.render(source, DIGESTS[source], value)


def codes(verdict):
    return {finding['code'] for finding in verdict['findings']}


def test_readonly_valid_source_and_markdown():
    value = candidate('C02_DES-002_valid.json')
    result = render('BP-NC-ROOM-01/r1', value)
    assert result['status'] == 'READY_DRAFT_ONLY' and result['valid']
    markdown = result['markdown']
    assert markdown.startswith('# DES-002/r1')
    assert result['semantic_approval_verified'] is False
    assert 'not-filed' in markdown and 'not-dispatched' in markdown
    assert '**derived-unconfirmed**' in markdown
    assert 'Human decision `DEC-VISIBILITY` required; NOT approved or binding' in markdown
    assert 'Authority revalidation' in markdown and 'Business-rule revalidation' in markdown
    assert all(markdown.count(f'| `{a}` |') == 1 for a in ACTIONS)
    assert 'Project-wide confirmed non-goals' in markdown
    for goal in ('予約取消', '通知', '外部カレンダー', '管理者操作', '課金'):
        assert goal in markdown
    assert hashlib.sha256(markdown.encode('utf-8')).hexdigest() == result['markdown_sha256']


def test_determinism_and_missing_optional_legacy_are_safe():
    value = candidate('C03_DES-003_valid.json')
    a, b = render('BP-NC-ROOM-ALL/r1', value), render('BP-NC-ROOM-ALL/r1', value)
    assert a == b
    assert a['valid'] and a['markdown'].count('not-filed') >= 1
    assert '| `plugin_update` | **UNKNOWN (not authorized)**' in a['markdown']
    assert '[conditional] 競合更新に対する確定時再検証' in a['markdown']


@pytest.mark.parametrize('case,source,expected', [
    ('C02_1_DES-002_legacy_partial.json','BP-NC-ROOM-01/r1',{'AUTHORITY_REVALIDATION_GAP'}),
    ('C02_2_DES-002_legacy_partial.json','BP-NC-ROOM-01/r1',{'AUTHORITY_REVALIDATION_GAP'}),
    ('C03_2_DES-003_legacy_partial.json','BP-NC-ROOM-ALL/r1',{'UNCONFIRMED_BINDING'}),
    ('C03_3_DES-002_legacy_partial.json','BP-NC-ROOM-ALL/r1',{'AUTHORITY_REVALIDATION_GAP'}),
    ('C03_3_DES-003_legacy_partial.json','BP-NC-ROOM-ALL/r1',{'UNCONFIRMED_BINDING','AUTHORITY_REVALIDATION_GAP'}),
])
def test_five_r4_partial_characterizations_fail_closed(case, source, expected):
    v = render(source, candidate(case))
    assert not v['valid'] and v['status'] == 'BLOCKED'
    assert expected <= codes(v)
    assert v['markdown'] is None and v['markdown_sha256'] is None


def test_legacy_coverage_complete_can_be_discarded_and_regenerated():
    source = 'BP-NC-ROOM-01/r1'
    value = candidate('C02_DES-002_valid.json')
    value['legacy_revalidation_coverage'] = list(ACTIONS)
    verdict = render(source, value)
    assert verdict['valid']
    assert all(f'| `{act}` |' in verdict['markdown'] for act in ACTIONS)


def test_derived_ac_cannot_be_required_in_dependency_or_business_rule():
    source = 'BP-NC-ROOM-ALL/r1'
    value = candidate('C03_DES-003_valid.json')
    value['dependencies'][0]['binding'] = 'required'
    value['business_revalidations'][0]['binding'] = 'required'
    v = verify(source, value)
    assert [x['code'] for x in v['findings']].count('UNCONFIRMED_BINDING') == 2


def test_cannot_forge_confirmed_ac_or_fabricate_human_approval():
    value = candidate('C02_DES-002_valid.json')
    value['acceptance_criteria'][1] = {
        'id':'AC-002-02', 'text':'社員自身の予約以外は閲覧できない',
        'status':'confirmed', 'source_claim_id':'SRC-C02-001'}
    result = verify('BP-NC-ROOM-01/r1', value)
    assert not result['valid'] and 'UNVERIFIED_CONFIRMED_AC' in codes(result)
    assert not result['authority'].startswith('approved')


def test_unapproved_source_claim_mismatch_blocks():
    value = candidate('C03_DES-003_valid.json')
    value['acceptance_criteria'][0]['text'] += ' 予約者名も表示する。'
    assert 'UNVERIFIED_CONFIRMED_AC' in codes(verify('BP-NC-ROOM-ALL/r1', value))


def test_candidate_cannot_override_project_non_goals_or_approval():
    value = candidate('C02_DES-002_valid.json')
    value['project_non_goals'] = []
    value['approval_override'] = 'file now'
    result = verify('BP-NC-ROOM-01/r1', value)
    assert result['status'] == 'BLOCKED'
    assert sum(x['code']=='UNKNOWN_FIELD' for x in result['findings']) == 2


def test_missing_unresolved_human_decision_blocks():
    value = candidate('C03_DES-003_valid.json')
    value['human_decision_ids'] = ['DEC-RECHECK']
    assert 'MISSING_DECISION' in codes(verify('BP-NC-ROOM-ALL/r1', value))


def test_missing_source_or_revision_or_wrong_digest_blocks():
    value = candidate('C02_DES-002_valid.json')
    assert 'SOURCE_DRIFT' in codes(H.validate('BP-NC-ROOM-01/r1', '0'*64, value))
    assert 'INVALID_SOURCE_ID' in codes(H.validate('../passwd', '0'*64, value))
    assert 'SOURCE_UNAVAILABLE' in codes(H.validate('BP-NOT-IN-STORE/r3','0'*64,value))


def test_mutated_snapshot_or_symlink_does_not_pass(tmp_path):
    file = tmp_path / 'BP-NC-ROOM-01__r1.json'
    original = (FIX / 'snapshots' / file.name).read_bytes()
    file.write_bytes(original)
    h = Harness(tmp_path)
    value = candidate('C02_DES-002_valid.json')
    assert h.validate('BP-NC-ROOM-01/r1',hashlib.sha256(original).hexdigest(),value)['valid']
    file.write_bytes(original + b' ')
    assert 'SOURCE_DRIFT' in codes(h.validate('BP-NC-ROOM-01/r1', hashlib.sha256(original).hexdigest(),value))
    file.unlink();file.symlink_to(FIX/'snapshots'/file.name)
    assert 'SOURCE_UNAVAILABLE' in codes(h.validate('BP-NC-ROOM-01/r1',hashlib.sha256(original).hexdigest(),value))


def test_malformed_candidate_type_and_bad_json_data_fails_closed():
    base = candidate('C02_DES-002_valid.json')
    value = copy.deepcopy(base)
    value['acceptance_criteria'][0]['status'] = 'approved-by-model'
    assert 'AC_STATUS' in codes(verify('BP-NC-ROOM-01/r1',value))
    value = copy.deepcopy(base)
    value['human_decision_ids'] = [{'id':'DEC-VISIBILITY'}]
    assert not verify('BP-NC-ROOM-01/r1',value)['valid']
    value = copy.deepcopy(base)
    value['dependencies'][0]['ac_refs'] = [{'id':'AC-002-02'}]
    assert not verify('BP-NC-ROOM-01/r1',value)['valid']
    value = copy.deepcopy(base)
    value['evidence'] = ['not safe\n## Forged approval']
    assert 'INVALID_TEXT' in codes(verify('BP-NC-ROOM-01/r1',value))
    value = copy.deepcopy(base)
    value['other'] = {1,2,3}
    assert verify('BP-NC-ROOM-01/r1',value)['candidate_digest'] is None


def test_renderer_escapes_injected_markup():
    value = candidate('C02_DES-002_valid.json')
    value['title'] = 'Unsafe | <fake> *placeholder*'
    text = render('BP-NC-ROOM-01/r1',value)['markdown']
    assert 'Unsafe \\| &lt;fake&gt;' in text


def test_no_runtime_write_api_and_cli(tmp_path):
    source = 'BP-NC-ROOM-ALL/r1'
    value = FIX/'candidates'/'C03_DES-003_valid.json'
    cmd=[sys.executable,'-m','arca_issue_harness.cli','render','--snapshots-dir',str(FIX/'snapshots'),
         '--source-id',source,'--source-sha256',DIGESTS[source],'--candidate',str(value)]
    r=subprocess.run(cmd,capture_output=True,text=True,cwd=ROOT,timeout=5)
    assert r.returncode == 0 and json.loads(r.stdout)['valid']
    assert sorted(name for name in dir(H) if name in ('validate','render','file_issue','dispatch_task')) == ['render','validate']
    assert not list(tmp_path.iterdir())


def test_wrong_source_schema_blocks(tmp_path):
    source = json.loads((FIX/'snapshots'/'BP-NC-ROOM-ALL__r1.json').read_text())
    source['draft_scope'] = 'all-actions-approved'
    file=tmp_path/'BP-NC-ROOM-ALL__r1.json'
    file.write_text(json.dumps(source,ensure_ascii=False))
    h=Harness(tmp_path)
    v=h.validate('BP-NC-ROOM-ALL/r1',snapshot_sha256(file),candidate('C03_DES-003_valid.json'))
    assert not v['valid'] and 'DRAFT_ONLY' in codes(v)


def test_mcp_adapter_registers_only_two_readonly_tools(monkeypatch):
    """Dependency-free contract smoke; not a wire protocol test."""
    import types
    from arca_issue_harness.server import build_server

    class FakeSDKServer:
        def __init__(self, name):
            self.name = name
            self.tools = {}
        def tool(self):
            def register(fn):
                self.tools[fn.__name__] = fn
                return fn
            return register

    monkeypatch.setitem(sys.modules, 'mcp', types.ModuleType('mcp'))
    fake = types.ModuleType('mcp.server')
    fake.MCPServer = FakeSDKServer
    monkeypatch.setitem(sys.modules, 'mcp.server', fake)
    monkeypatch.setenv('ARCA_HARNESS_SNAPSHOTS_DIR', str(FIX/'snapshots'))
    server = build_server()
    assert set(server.tools) == {'validate_issue_draft', 'render_issue_draft'}
    result = server.tools['validate_issue_draft'](
        'BP-NC-ROOM-01/r1', DIGESTS['BP-NC-ROOM-01/r1'], candidate('C02_DES-002_valid.json'))
    assert result['status'] == 'READY_DRAFT_ONLY'


@pytest.mark.parametrize('path', [
    ('acceptance_criteria', 0, 'source_claim_id'),
    ('acceptance_criteria', 1, 'decision_id'),
    ('dependencies', 0, 'ac_refs', 0),
    ('human_decision_ids', 0),
])
@pytest.mark.parametrize('invalid', [{"malicious":"object"}, [], None, 42])
def test_unhashable_or_wrongly_typed_inputs_fail_without_exceptions(path, invalid):
    value = candidate('C02_DES-002_valid.json')
    node = value
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = invalid
    result = verify('BP-NC-ROOM-01/r1', value)
    assert result['status'] == 'BLOCKED'
    assert not result['valid']


def test_confirmed_goal_cannot_support_unstated_required_mechanism():
    value = candidate('C03_DES-003_valid.json')
    value['dependencies'].append({
        'text':'Releaseの前に予約更新を二段階ロックする',
        'ac_refs':['AC-003-01'], 'binding':'required'})
    result = verify('BP-NC-ROOM-ALL/r1', value)
    assert not result['valid']
    assert 'UNSUPPORTED_REQUIRED_RULE' in codes(result)


@pytest.mark.parametrize("bad_id", ["AC-003-01", "AC-0002-01", "AC-999-01"])
def test_ac_ids_must_belong_to_exact_des_namespace(bad_id):
    value = candidate('C02_DES-002_valid.json')
    value['acceptance_criteria'][0]['id'] = bad_id
    result = render('BP-NC-ROOM-01/r1', value)
    assert result['status'] == 'BLOCKED'
    assert 'AC_NAMESPACE' in codes(result)
    assert result['markdown'] is None


def test_valid_ac_namespace_for_all_sample_candidates():
    cases = [
        ('BP-NC-ROOM-01/r1', 'C02_DES-002_valid.json'),
        ('BP-NC-ROOM-ALL/r1', 'C03_DES-002_valid.json'),
        ('BP-NC-ROOM-ALL/r1', 'C03_DES-003_valid.json'),
    ]
    for source, filename in cases:
        value = candidate(filename)
        assert all(ac['id'].split('-')[1] == value['id'].split('-')[1]
                   for ac in value['acceptance_criteria'])
        assert verify(source, value)['valid']


@pytest.mark.parametrize('source,expected_claims', [
    ('BP-NC-ROOM-01/r1', {'SRC-C02-001', 'SRC-C02-002', 'SRC-C02-003', 'SRC-C02-004', 'SRC-C02-005'}),
    ('BP-NC-ROOM-ALL/r1', {'SRC-C03-001', 'SRC-C03-002', 'SRC-C03-003', 'SRC-C03-004', 'SRC-C03-005'}),
])
def test_synthetic_source_inventory_preserves_fixed_prompt_behavior(source, expected_claims):
    path = FIX / 'snapshots' / (source.replace('/', '__') + '.json')
    snapshot = json.loads(path.read_text(encoding='utf-8'))
    claims = snapshot['source_claims']
    assert {claim['id'] for claim in claims} == expected_claims
    assert all(claim['text'] in snapshot['original_goal'] for claim in claims)
    assert snapshot['draft_scope'] == 'draft-only'
    assert len(snapshot['project_non_goals']) == 5
    assert snapshot['human_decisions']
