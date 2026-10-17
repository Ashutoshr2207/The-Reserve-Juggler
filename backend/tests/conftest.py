import csv
import io
import json
import shutil
import uuid
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.application import create_app
from app.api.contracts import ROOT
from app.api.security import Config
from app.domain.intake import COLUMNS


def csv_bytes(count=24, change=None):
    rows = []
    for index in range(count):
        stamp = datetime(2026, 1, 1) + timedelta(hours=index)
        row = {field: '0' for field in COLUMNS}
        row.update(timestamp=stamp.strftime('%Y-%m-%d %H:%M:%S'), deposits_usd='100.10',
                   withdrawals_usd='90.05', net_flow_usd='10.05',
                   repo_sweep_window_open=str(stamp.hour == 17), repo_sweep_mature=str(stamp.hour == 8),
                   tier1_repo_rate_apy='4.0', tier2_bond_price_index='100', tier3_stock_index_price='5000')
        rows.append(row)
    if change:
        change(rows)
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=COLUMNS)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode()


@pytest.fixture
def local_root():
    path = ROOT / 'work/tests' / uuid.uuid4().hex[:10]
    yield path
    if path.exists():
        shutil.rmtree(path)


@contextmanager
def client_for(root, role='operator', login=True, **kwargs):
    app = create_app(Config(runtime=root, role=role, **kwargs))
    with TestClient(app, base_url='http://127.0.0.1:8000', client=('127.0.0.1', 50000)) as client:
        if login:
            response = client.post('/local/bootstrap', json={'capability': app.state.session.bootstrap},
                                   headers={'Origin': 'http://127.0.0.1:8000'})
            assert response.status_code == 204
            client.headers.update({'Origin': 'http://127.0.0.1:8000',
                                   'X-CSRF-Token': response.headers['X-CSRF-Token']})
        yield client, app


@pytest.fixture
def live(local_root):
    with client_for(local_root) as pair:
        yield pair


def upload(client, data=None, key='import-key-01', filename='fictional.csv'):
    return client.post('/api/v1/datasets', files={'file': (filename, data or csv_bytes(), 'text/csv')},
                       headers={'Idempotency-Key': key})


def scenario_body(dataset_id):
    fixture = json.loads((ROOT / 'contracts/examples/first_slice.json').read_text())
    body = next(c['value'] for c in fixture['http_cases'] if c['schema'] == 'ScenarioCreate')
    return {**body, 'dataset_id': dataset_id}


def scenario(client, dataset_id=None, key='scenario-key-01', mutate=None):
    if dataset_id is None:
        response = upload(client)
        assert response.status_code == 201, response.text
        dataset_id = response.json()['dataset_id']
    body = scenario_body(dataset_id)
    if mutate:
        mutate(body)
    return client.post('/api/v1/scenarios', json=body, headers={'Idempotency-Key': key})


def review(client, value, key='review-key-01', etag=None):
    return client.post(f"/api/v1/scenarios/{value['scenario_id']}/review",
                       json={'actor_label': 'Local fictional reviewer', 'acknowledge_fictional_assumptions': True},
                       headers={'Idempotency-Key': key, 'If-Match': etag or value['fingerprint']})


def wait_for_run(client, run_id, timeout=10):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = client.get(f'/api/v1/runs/{run_id}')
        assert response.status_code == 200, response.text
        value = response.json()
        if value['status'] in ('COMPLETED', 'CANCELLED', 'FAILED', 'INTERRUPTED'):
            return value
        time.sleep(.01)
    raise AssertionError('Run did not reach a terminal state')
