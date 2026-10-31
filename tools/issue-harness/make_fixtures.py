"""Rebuild deterministic fictional sample fixtures; not an approval registration API."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SNAP = ROOT / 'fixtures' / 'snapshots'
CAND = ROOT / 'fixtures' / 'candidates'


def write(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def source(id, goal, claims, decisions, prohibitions, *, non_goals=None):
    return dict(schema_version='arca.issue-harness.snapshot.v1', source_id=id,
                original_goal=goal, approval_provenance='Fixed synthetic prompt reports Human approval for specification drafts only; original approval record not independently verified',
                draft_scope='draft-only',
                project_non_goals=non_goals or ['予約取消', '通知', '外部カレンダー', '管理者操作', '課金'],
                source_claims=[dict(id=i, text=t) for i, t in claims],
                human_decisions=[dict(id=i, question=q, impact=impact) for i, q, impact in decisions],
                prohibited_actions=prohibitions)


c02 = source(
    'BP-NC-ROOM-01/r1',
    '社員がスマホWebで自分の会議室予約を作成し、既存予約を一覧から選択して予約日時を変更できることが必須です。',
    [('SRC-C02-001','既存予約を一覧から選択して予約日時を変更できることが必須です。')],
    [('DEC-VISIBILITY', '予約一覧を本人限定・全社員のどちらが閲覧できるか', '一覧の抽出条件と閲覧権限は未確定; 影響部分の実装を停止する')],
    ['issue_filing', 'task_dispatch', 'code_change', 'merge', 'release', 'plugin_update']
)
c03 = source(
    'BP-NC-ROOM-ALL/r1',
    '全社員は他の社員の予約を含む全予約を閲覧できます。ただし他人の予約を編集・変更することは禁止です。',
    [('SRC-C03-001','全社員は他の社員の予約を含む全予約を閲覧できます。'),
     ('SRC-C03-002','ただし他人の予約を編集・変更することは禁止です。')],
    [('DEC-RECHECK', '予約変更確定時の競合再検証手順を追加の必須ACとするか', '具体的な競合再検証方式は未承認; 必須実装条件へ昇格させない'),
     ('DEC-DISPLAY', '閲覧できる予約の具体的表示項目を確定するか', '全社員閲覧権限は確認済みだが表示項目は別判断')],
    ['issue_filing', 'task_dispatch', 'code_change', 'merge', 'release'],
    non_goals=['予約取消', '通知', '管理者機能', '外部カレンダー', '課金']
)
write(SNAP / 'BP-NC-ROOM-01__r1.json', c02)
write(SNAP / 'BP-NC-ROOM-ALL__r1.json', c03)

c02_candidate = dict(
    schema_version='arca.issue-harness.candidate.v1', id='DES-002', revision='r1',
    title='既存会議室予約の一覧と選択', desired_outcome='社員がスマホWebの一覧から目的の既存予約を選べる',
    scenario='社員が既存予約を開き対象を選び、日時変更へ進む前に対象を確認する',
    in_scope=['予約一覧表示', '目的予約の選択'],
    candidate_exclusions=['予約変更処理そのものは本Issueの担当外'],
    acceptance_criteria=[
        dict(id='AC-002-01', text='既存予約を一覧から選択して予約日時を変更できることが必須です。', status='confirmed', source_claim_id='SRC-C02-001'),
        dict(id='AC-002-02', text='他人の予約を表示するかの抽出条件を定める', status='derived-unconfirmed', decision_id='DEC-VISIBILITY'),
    ], dependencies=[dict(text='一覧権限の確定',ac_refs=['AC-002-02'],binding='conditional')],
    business_revalidations=[],human_decision_ids=['DEC-VISIBILITY'],
    evidence=['独立Issue本文の出典と停止条件', 'スマホWebでの一覧表示と選択の観測証拠'])

c03_candidate = dict(
    schema_version='arca.issue-harness.candidate.v1', id='DES-003', revision='r1',
    title='本人予約の開始前日時変更', desired_outcome='本人だけが開始前に予約日時を変更できる',
    scenario='社員が全員閲覧可能な一覧から自分の予約を選び、開始前に日時を変更する',
    in_scope=['本人による予約日時変更', '他人の予約の変更を禁止'],
    candidate_exclusions=['他人の予約の変更処理は本Issueで許可しない'],
    acceptance_criteria=[
        dict(id='AC-003-01', text='全社員は他の社員の予約を含む全予約を閲覧できます。', status='confirmed', source_claim_id='SRC-C03-001'),
        dict(id='AC-003-02', text='ただし他人の予約を編集・変更することは禁止です。', status='confirmed', source_claim_id='SRC-C03-002'),
        dict(id='AC-003-06', text='日時変更の確定直前に本人・開始前・重複の条件を再確認する', status='derived-unconfirmed', decision_id='DEC-RECHECK'),
    ], dependencies=[dict(text='確定時再検証方式', ac_refs=['AC-003-06'], binding='conditional')],
    business_revalidations=[dict(text='競合更新に対する確定時再検証', ac_refs=['AC-003-06'], binding='conditional')],
    human_decision_ids=['DEC-RECHECK', 'DEC-DISPLAY'],
    evidence=['権限による変更拒否のテスト', '未承認の競合再検証は実装テストの必須条件としない'])
c03_candidate002 = dict(
    schema_version='arca.issue-harness.candidate.v1', id='DES-002', revision='r1',
    title='全社員による予約一覧と選択', desired_outcome='全社員が他人の予約も閲覧・選択できる',
    scenario='社員が他社員の予約を参照し、編集権限がないことを確認する',
    in_scope=['全社員による予約参照', '他人の予約を変更する権限は付与しない'],
    candidate_exclusions=['日時変更処理そのものは別Issue'],
    acceptance_criteria=[
        dict(id='AC-002-01', text='全社員は他の社員の予約を含む全予約を閲覧できます。', status='confirmed', source_claim_id='SRC-C03-001'),
        dict(id='AC-002-02', text='ただし他人の予約を編集・変更することは禁止です。', status='confirmed', source_claim_id='SRC-C03-002'),
        dict(id='AC-002-03', text='予約者欄の開示範囲を仕様化する', status='derived-unconfirmed', decision_id='DEC-DISPLAY'),
    ], dependencies=[dict(text='表示項目の決定', ac_refs=['AC-002-03'], binding='conditional')],
    business_revalidations=[], human_decision_ids=['DEC-RECHECK', 'DEC-DISPLAY'],
    evidence=['全社員閲覧テストと他人変更拒否テスト'])
write(CAND/'C02_DES-002_valid.json',c02_candidate)
write(CAND/'C03_DES-002_valid.json',c03_candidate002)
write(CAND/'C03_DES-003_valid.json',c03_candidate)
# Targeted regression fixtures faithfully model the five observed *types* of
# R4 partials; they are structured characterizations, not verbatim UI output.
regressions = [
    ('C02_1_DES-002',c02_candidate,'legacy_revalidation_coverage',['issue_filing','task_dispatch','code_change']),
    ('C02_2_DES-002',c02_candidate,'legacy_revalidation_coverage',['issue_filing','code_change']),
    ('C03_2_DES-003',c03_candidate,'derived_promoted_to_required',None),
    ('C03_3_DES-002',c03_candidate002,'legacy_revalidation_coverage',['task_dispatch']),
    ('C03_3_DES-003',c03_candidate,'both',None),
]
for label,source_candidate,mode,coverage in regressions:
    item=copy.deepcopy(source_candidate)
    if mode in ('derived_promoted_to_required','both'):
        item['dependencies'][0]['binding']='required'
        if item['business_revalidations']:
            item['business_revalidations'][0]['binding']='required'
    if mode in ('legacy_revalidation_coverage','both'):
        item['legacy_revalidation_coverage'] = coverage if coverage is not None else ['issue_filing','task_dispatch']
    write(CAND/(label+'_legacy_partial.json'), item)
manifest={}
for name in sorted(SNAP.glob('*.json')):
    manifest[json.loads(name.read_text())['source_id']] = hashlib.sha256(name.read_bytes()).hexdigest()
write(ROOT/'fixtures'/'snapshot_digests.json',manifest)
