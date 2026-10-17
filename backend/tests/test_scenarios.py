import copy
import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from app.api.contracts import validate
from app.domain.intake import MAX_INT
from conftest import csv_bytes, review, scenario, scenario_body, upload


def test_immutable_scenario_review_fingerprint_and_audit(live):
    client, app = live
    created = scenario(client)
    assert created.status_code == 201, created.text
    original = validate('Scenario', created.json())
    assert original['status'] == 'DRAFT' and original['revision'] == 1
    assert created.headers['ETag'] == original['fingerprint']
    reviewed = review(client, original)
    assert reviewed.status_code == 200, reviewed.text
    assert reviewed.json()['status'] == 'REVIEWED'
    assert reviewed.headers['ETag'] == original['fingerprint']
    assert client.get('/api/v1/scenarios/' + original['scenario_id']).json() == reviewed.json()
    assert review(client, original).json() == reviewed.json()
    with app.state.database.read() as db:
        row = db.execute('SELECT * FROM reviews').fetchone()
        assert row['mode'] == 'self_review'
        assert row['fingerprint'] == original['fingerprint']
        assert db.execute('SELECT count(*) FROM reviews').fetchone()[0] == 1
    # Editing creates a different immutable draft and leaves reviewed evidence intact.
    changed = scenario(client, original['dataset_id'], key='scenario-key-02',
                       mutate=lambda body: body['settings'].update(reserve_floor_cents='1')).json()
    assert changed['scenario_id'] != original['scenario_id']
    assert changed['fingerprint'] != original['fingerprint'] and changed['status'] == 'DRAFT'
    assert client.get('/api/v1/scenarios/' + original['scenario_id']).json()['status'] == 'REVIEWED'


@pytest.mark.parametrize(('field', 'value', 'code'), [
    ('fictional_acknowledged', False, 'ASSUMPTIONS_INCOMPLETE'),
    ('opening_cash_cents', 100, 'ASSUMPTIONS_INCOMPLETE'),
    ('opening_cash_cents', '-1', 'ASSUMPTIONS_INCOMPLETE'),
    ('opening_cash_cents', str(MAX_INT+1), 'AMOUNT_OUT_OF_RANGE'),
    ('bond_units', '-1', 'ASSUMPTIONS_INCOMPLETE'),
    ('bond_units', '0.000000001', 'ASSUMPTIONS_INCOMPLETE'),
    ('equity_units', '1', 'ASSUMPTIONS_INCOMPLETE'),
    ('bond_cap_pct', '101', 'ASSUMPTIONS_INCOMPLETE'),
    ('equity_cap_pct', '-1', 'ASSUMPTIONS_INCOMPLETE'),
    ('settlement_delay_hours', True, 'ASSUMPTIONS_INCOMPLETE'),
    ('settlement_delay_hours', 49, 'ASSUMPTIONS_INCOMPLETE'),
    ('stress_ids', ['none', 'denied_credit'], 'ASSUMPTIONS_INCOMPLETE'),
    ('stress_ids', ['deposit_delay', 'deposit_delay'], 'ASSUMPTIONS_INCOMPLETE'),
])
def test_settings_semantics(live, field, value, code):
    client, app = live
    result = scenario(client, mutate=lambda body: body['settings'].update({field: value}))
    assert result.status_code == 422, result.text
    assert result.json()['code'] == code
    with app.state.database.read() as db:
        assert db.execute('SELECT count(*) FROM scenarios').fetchone()[0] == 0


def test_no_hidden_defaults_or_client_authority(live):
    client, _ = live
    dataset_id = upload(client).json()['dataset_id']
    body = scenario_body(dataset_id)
    for field in list(body['settings']):
        missing = copy.deepcopy(body)
        del missing['settings'][field]
        response = client.post('/api/v1/scenarios', json=missing, headers={'Idempotency-Key': 'scenario-key-01'})
        assert response.status_code == 422, field
    for field, value in [('workspace_id', 'ws_foreign'), ('status', 'REVIEWED'), ('role', 'operator')]:
        response = client.post('/api/v1/scenarios', json={**body, field: value}, headers={'Idempotency-Key': 'scenario-key-01'})
        assert response.status_code == 422


@pytest.mark.parametrize('etag', ['', '0'*64, '"'+'0'*64+'"'])
def test_stale_or_missing_review_does_not_advance(live, etag):
    client, app = live
    original = scenario(client).json()
    response = client.post(f"/api/v1/scenarios/{original['scenario_id']}/review",
                           json={'actor_label': 'Reviewer', 'acknowledge_fictional_assumptions': True},
                           headers={'Idempotency-Key': 'review-key-01', 'If-Match': etag})
    assert response.status_code == 409
    assert response.json()['code'] == 'STALE_REVISION'
    assert client.get('/api/v1/scenarios/' + original['scenario_id']).json()['status'] == 'DRAFT'
    with app.state.database.read() as db:
        assert db.execute('SELECT count(*) FROM reviews').fetchone()[0] == 0


def test_false_acknowledgment_and_extra_fields(live):
    client, _ = live
    original = scenario(client).json()
    for ack in [False, 1, 'true']:
        response = client.post(f"/api/v1/scenarios/{original['scenario_id']}/review",
                               json={'actor_label': 'operator', 'acknowledge_fictional_assumptions': ack},
                               headers={'Idempotency-Key': 'review-key-01', 'If-Match': original['fingerprint']})
        assert response.status_code == 422


def test_idempotency_and_canonical_payload(live):
    client, app = live
    dataset = upload(client).json()['dataset_id']
    first = scenario(client, dataset)
    body = scenario_body(dataset)
    # Whitespace/object order do not alter canonical payload identity.
    second = client.post('/api/v1/scenarios', content=json.dumps(body, sort_keys=True, indent=2),
                         headers={'Content-Type': 'application/json', 'Idempotency-Key': 'scenario-key-01'})
    assert first.status_code == second.status_code == 201 and first.json() == second.json()
    conflict = scenario(client, dataset, mutate=lambda body: body.update(label='Changed'))
    assert conflict.status_code == 409 and conflict.json()['code'] == 'IDEMPOTENCY_CONFLICT'
    assert upload(client, csv_bytes(23)).status_code == 409
    assert upload(client, b'invalid CSV with the same committed key').status_code == 409
    incomplete = client.post('/api/v1/scenarios', json={}, headers={'Idempotency-Key': 'scenario-key-01'})
    assert incomplete.status_code == 409
    assert review(client, first.json(), key='scenario-key-01').status_code == 200  # operation-scoped key
    with app.state.database.read() as db:
        assert db.execute('SELECT count(*) FROM scenarios').fetchone()[0] == 1


def test_concurrent_import_create_review(live):
    client, app = live
    with ThreadPoolExecutor(max_workers=8) as workers:
        imports = list(workers.map(lambda _: upload(client), range(8)))
    assert {r.status_code for r in imports} == {201}
    dataset_id = imports[0].json()['dataset_id']
    assert {r.json()['dataset_id'] for r in imports} == {dataset_id}
    with ThreadPoolExecutor(max_workers=8) as workers:
        creates = list(workers.map(lambda _: scenario(client, dataset_id), range(8)))
    assert {r.status_code for r in creates} == {201}
    value = creates[0].json()
    assert len({r.json()['scenario_id'] for r in creates}) == 1
    with ThreadPoolExecutor(max_workers=8) as workers:
        reviews = list(workers.map(lambda _: review(client, value), range(8)))
    assert {r.status_code for r in reviews} == {200}
    with app.state.database.read() as db:
        assert db.execute('SELECT count(*) FROM datasets').fetchone()[0] == 1
        assert db.execute('SELECT count(*) FROM scenarios').fetchone()[0] == 1
        assert db.execute('SELECT count(*) FROM reviews').fetchone()[0] == 1


def test_concurrent_conflicting_payload_has_one_winner(live):
    client, _ = live
    dataset = upload(client).json()['dataset_id']
    with ThreadPoolExecutor(max_workers=2) as workers:
        results = list(workers.map(lambda label: scenario(client, dataset, mutate=lambda b: b.update(label=label)), ['A', 'B']))
    assert sorted(r.status_code for r in results) == [201, 409]


def test_opening_lot_semantics(live):
    client, _ = live
    dataset = upload(client).json()['dataset_id']
    valid = {'principal_cents': '10000', 'entry_time': '2025-12-31 17:00:00',
             'maturity_time': '2026-01-01 08:00:00', 'entry_rate_pct': '4.0'}
    result = scenario(client, dataset, mutate=lambda b: b['settings'].update(opening_repo_lots=[valid]))
    assert result.status_code == 201
    for index, changes in enumerate([{'entry_time': '2026-01-01 17:00:00'}, {'principal_cents': '0'},
                                     {'maturity_time': '2026-01-02 08:00:00'}, {'entry_rate_pct': '-1'}]):
        invalid = {**valid, **changes}
        assert scenario(client, dataset, key=f'invalid-lot-{index}',
                        mutate=lambda b: b['settings'].update(opening_repo_lots=[invalid])).status_code == 422


def test_json_parser_rejects_duplicate_keys_nonfinite_and_deep_input(live):
    client, _ = live
    for body in ['{"label":"one","label":"two"}', '{"opening_cash_cents":NaN}', '['*1200+']'*1200, 'x'*65537]:
        response = client.post('/api/v1/scenarios', content=body,
                               headers={'Content-Type': 'application/json', 'Idempotency-Key': 'scenario-key-01'})
        assert response.status_code == 422
        validate('Error', response.json())
