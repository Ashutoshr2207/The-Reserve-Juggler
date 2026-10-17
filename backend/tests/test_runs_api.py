"""Tests for /runs lifecycle, execution, metrics, decisions, and evidence export."""
import hashlib
import json
import pytest

from app.api.contracts import validate
from conftest import client_for, review, scenario, upload, wait_for_run


def create_reviewed_scenario(client):
    upload_resp = upload(client)
    assert upload_resp.status_code == 201
    dataset_id = upload_resp.json()['dataset_id']
    scenario_resp = scenario(client, dataset_id=dataset_id)
    assert scenario_resp.status_code == 201
    sc_data = scenario_resp.json()
    review_resp = review(client, sc_data)
    assert review_resp.status_code == 200
    return review_resp.json()


def test_create_and_query_run_with_metrics_and_decisions(live):
    client, app = live
    sc_data = create_reviewed_scenario(client)
    scenario_id = sc_data['scenario_id']

    # 1. Create Run
    run_req = {
        'scenario_id': scenario_id,
        'policy_ids': ['cash_only', 'fixed_repo'],
        'forecast_mode': 'baseline',
        'adapter_artifact_id': None,
    }
    resp = client.post('/api/v1/runs', json=run_req, headers={'Idempotency-Key': 'run-key-01'})
    assert resp.status_code == 202, resp.text
    run_data = resp.json()
    validate('Run', run_data)
    run_id = run_data['run_id']
    assert run_data['status'] == 'QUEUED'
    run_data = wait_for_run(client, run_id)
    assert run_data['status'] == 'COMPLETED'
    assert run_data['completed_hours'] == 24
    assert run_data['total_hours'] == 24
    assert run_data['financial_outcome'] in ('NO_SHORTFALLS', 'SHORTFALLS')

    # 2. Get Run
    get_run_resp = client.get(f'/api/v1/runs/{run_id}')
    assert get_run_resp.status_code == 200
    assert get_run_resp.json() == run_data

    # 3. Get Metrics
    metrics_resp = client.get(f'/api/v1/runs/{run_id}/metrics')
    assert metrics_resp.status_code == 200, metrics_resp.text
    metric_set = metrics_resp.json()
    validate('MetricSet', metric_set)
    assert len(metric_set['metrics']) == 2
    policies = {m['policy_id'] for m in metric_set['metrics']}
    assert policies == {'cash_only', 'fixed_repo'}

    # 4. Get Decisions (Paginated)
    decisions_resp = client.get(f'/api/v1/runs/{run_id}/decisions?limit=10')
    assert decisions_resp.status_code == 200, decisions_resp.text
    page = decisions_resp.json()
    validate('DecisionPage', page)
    assert len(page['items']) <= 10

    # 5. Export Evidence
    export_resp = client.get(f'/api/v1/runs/{run_id}/export')
    assert export_resp.status_code == 200, export_resp.text
    bundle = export_resp.json()
    validate('EvidenceBundle', bundle)
    assert len(bundle['members']) >= 4
    for member in bundle['members']:
        expected_digest = hashlib.sha256(member['content'].encode()).hexdigest()
        assert member['sha256'] == expected_digest, f"Digest mismatch on {member['name']}"


def test_unreviewed_scenario_cannot_create_run(live):
    client, app = live
    upload_resp = upload(client)
    dataset_id = upload_resp.json()['dataset_id']
    # Scenario created in DRAFT status
    sc_data = scenario(client, dataset_id=dataset_id).json()
    assert sc_data['status'] == 'DRAFT'

    run_req = {
        'scenario_id': sc_data['scenario_id'],
        'policy_ids': ['cash_only'],
        'forecast_mode': 'baseline',
        'adapter_artifact_id': None,
    }
    resp = client.post('/api/v1/runs', json=run_req, headers={'Idempotency-Key': 'draft-run-key-01'})
    assert resp.status_code == 422
    assert resp.json()['code'] == 'ASSUMPTIONS_INCOMPLETE'


def test_run_idempotency_and_conflict(live):
    client, app = live
    sc_data = create_reviewed_scenario(client)
    scenario_id = sc_data['scenario_id']

    run_req = {
        'scenario_id': scenario_id,
        'policy_ids': ['cash_only'],
        'forecast_mode': 'disabled',
        'adapter_artifact_id': None,
    }
    key = 'idem-run-key-99'
    resp1 = client.post('/api/v1/runs', json=run_req, headers={'Idempotency-Key': key})
    assert resp1.status_code == 202

    # Exact replay returns same stored response
    resp2 = client.post('/api/v1/runs', json=run_req, headers={'Idempotency-Key': key})
    assert resp2.status_code == 202
    assert resp2.json() == resp1.json()

    # Different payload with same key returns 409 IDEMPOTENCY_CONFLICT
    run_req_diff = {**run_req, 'policy_ids': ['fixed_repo']}
    resp3 = client.post('/api/v1/runs', json=run_req_diff, headers={'Idempotency-Key': key})
    assert resp3.status_code == 409
    assert resp3.json()['code'] == 'IDEMPOTENCY_CONFLICT'


def test_run_cancel_endpoint(live):
    client, app = live
    sc_data = create_reviewed_scenario(client)
    run_req = {
        'scenario_id': sc_data['scenario_id'],
        'policy_ids': ['cash_only'],
        'forecast_mode': 'baseline',
        'adapter_artifact_id': None,
    }
    resp = client.post('/api/v1/runs', json=run_req, headers={'Idempotency-Key': 'cancel-run-key-01'})
    assert resp.status_code == 202
    run_id = resp.json()['run_id']
    wait_for_run(client, run_id)

    cancel_resp = client.post(f'/api/v1/runs/{run_id}/cancel', headers={'Idempotency-Key': 'cancel-op-01'})
    assert cancel_resp.status_code == 200
    # Already completed run remains completed (or reports status)
    assert cancel_resp.json()['status'] in ('COMPLETED', 'CANCELLED')


def test_auditor_role_cannot_create_run(local_root):
    with client_for(local_root, role='auditor') as (client, app):
        run_req = {
            'scenario_id': 'sc_dummy',
            'policy_ids': ['cash_only'],
            'forecast_mode': 'baseline',
            'adapter_artifact_id': None,
        }
        resp = client.post('/api/v1/runs', json=run_req, headers={'Idempotency-Key': 'auditor-key-01'})
        assert resp.status_code == 403
        assert resp.json()['code'] == 'FORBIDDEN'
