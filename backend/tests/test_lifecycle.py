"""BE-04/05 failure, race, queue and incomplete-evidence acceptance checks."""
import hashlib
import json
import sqlite3
import threading
import time
import subprocess
import sys

import pytest

from app.api.application import create_app
from app.api.contracts import ROOT
from app.api.security import Config
from app.services.worker import enqueue
from conftest import client_for, csv_bytes, review, scenario, upload, wait_for_run


def prepared(client, count=72):
    dataset = upload(client, csv_bytes(count)).json()
    value = scenario(client, dataset['dataset_id']).json()
    assert review(client, value).status_code == 200
    return {'scenario_id': value['scenario_id'], 'policy_ids': ['cash_only', 'fixed_repo'],
            'forecast_mode': 'disabled', 'adapter_artifact_id': None}


def submit(client, body, key='lifecycle-run-01'):
    return client.post('/api/v1/runs', json=body, headers={'Idempotency-Key': key})


def test_bounded_queue_retry_conflict_and_queued_cancel(live, monkeypatch):
    client, app = live
    entered, release = threading.Event(), threading.Event()
    execute = app.state.worker.execute

    def blocked(row):
        entered.set()
        assert release.wait(5)
        return execute(row)

    monkeypatch.setattr(app.state.worker, 'execute', blocked)
    body = prepared(client)
    first = submit(client, body).json()
    try:
        assert entered.wait(2)
        assert client.get('/api/v1/workspace').status_code == 200
        queued = [submit(client, body, f'queue-run-{i:02}').json() for i in range(5)]
        full = submit(client, body, 'queue-full-key')
        assert full.status_code == 503 and full.json()['code'] == 'QUEUE_FULL'
        assert full.headers['Retry-After'] == '1'
        assert submit(client, body).json() == first
        assert submit(client, {**body, 'policy_ids': ['cash_only']}).status_code == 409
        rid = queued[0]['run_id']
        cancelled = client.post(f'/api/v1/runs/{rid}/cancel', headers={'Idempotency-Key': 'queued-cancel-01'})
        assert cancelled.json()['status'] == 'CANCELLED'
        assert submit(client, body, 'queue-full-key').status_code == 202
        with app.state.database.read() as db:
            assert db.execute("SELECT count(*) FROM runs WHERE status='RUNNING'").fetchone()[0] == 1
            assert db.execute("SELECT count(*) FROM runs WHERE status='QUEUED'").fetchone()[0] == 5
    finally:
        release.set()


def test_running_cancel_preserves_partial_evidence_and_hides_success(live, monkeypatch):
    import app.services.simulation as service
    client, app = live
    entered, release = threading.Event(), threading.Event()
    original = service.simulate_policy

    def paused(*args, **kwargs):
        callback = kwargs['checkpoint']
        def checkpoint(hour, *state):
            callback(hour, *state)
            if hour == 24:
                entered.set()
                assert release.wait(5)
        kwargs['checkpoint'] = checkpoint
        return original(*args, **kwargs)

    monkeypatch.setattr(service, 'simulate_policy', paused)
    rid = submit(client, prepared(client)).json()['run_id']
    try:
        assert entered.wait(2)
        for suffix in ('metrics', 'decisions', 'export'):
            response = client.get(f'/api/v1/runs/{rid}/{suffix}')
            assert response.status_code == 409 and response.json()['code'] == 'RUN_NOT_COMPLETE'
        cancelled = client.post(f'/api/v1/runs/{rid}/cancel', headers={'Idempotency-Key': 'running-cancel-01'})
        assert cancelled.status_code == 200
    finally:
        release.set()
    result = wait_for_run(client, rid)
    assert result['status'] == 'CANCELLED' and result['financial_outcome'] is None
    with app.state.database.read() as db:
        assert db.execute('SELECT count(*) FROM ledger_events WHERE run_id=?', (rid,)).fetchone()[0] > 0
        assert db.execute('SELECT count(*) FROM metrics WHERE run_id=?', (rid,)).fetchone()[0] == 0


def test_worker_exception_is_redacted_and_queue_continues(live, monkeypatch):
    client, app = live
    execute = app.state.worker.execute
    def failed(row):
        raise RuntimeError('secret C:/private/sensitive.csv')
    monkeypatch.setattr(app.state.worker, 'execute', failed)
    body = prepared(client)
    rid = submit(client, body).json()['run_id']
    result = wait_for_run(client, rid)
    assert result['status'] == 'FAILED'
    assert 'secret' not in json.dumps(result)
    assert client.get(f'/api/v1/runs/{rid}/metrics').json()['code'] == 'RUN_NOT_COMPLETE'
    monkeypatch.setattr(app.state.worker, 'execute', execute)
    rid = submit(client, body, 'after-failure-key').json()['run_id']
    assert wait_for_run(client, rid)['status'] == 'COMPLETED'


def test_final_commit_failure_rolls_back_complete_metrics(live):
    client, app = live
    body = prepared(client)
    with app.state.database.transaction() as db:
        db.execute("CREATE TRIGGER fail_metric_set BEFORE INSERT ON metric_sets BEGIN SELECT RAISE(ABORT,'test failure'); END")
    rid = submit(client, body).json()['run_id']
    assert wait_for_run(client, rid)['status'] == 'FAILED'
    with app.state.database.read() as db:
        assert db.execute('SELECT count(*) FROM metrics WHERE run_id=?', (rid,)).fetchone()[0] == 0
        assert db.execute('SELECT count(*) FROM ledger_events WHERE run_id=?', (rid,)).fetchone()[0] > 0


def test_restart_recovers_queued_running_and_preserves_terminal(local_root):
    with client_for(local_root) as (client, app):
        body = prepared(client)
        complete_id = submit(client, body).json()['run_id']
        assert wait_for_run(client, complete_id)['status'] == 'COMPLETED'
    # Emulate a crash after committed acceptance and a claimed run, without a worker.
    with app.state.database.transaction() as db:
        queued = dict(enqueue(app.state.database, db, app.state.workspace, body))
        running = dict(enqueue(app.state.database, db, app.state.workspace, body))
        db.execute("UPDATE runs SET status='RUNNING' WHERE id=?", (running['id'],))
    with client_for(local_root) as (client, restarted):
        for row in (queued, running):
            recovered = client.get('/api/v1/runs/' + row['id']).json()
            assert recovered['status'] == 'INTERRUPTED'
            assert recovered['financial_outcome'] is None
            assert client.get('/api/v1/runs/' + row['id'] + '/export').status_code == 409
        assert client.get('/api/v1/runs/' + complete_id).json()['status'] == 'COMPLETED'
        rid = submit(client, body, 'restart-new-run').json()['run_id']
        assert wait_for_run(client, rid)['status'] == 'COMPLETED'


def test_second_worker_fails_closed_without_interrupting_first(live):
    client, app = live
    from fastapi.testclient import TestClient
    with pytest.raises(RuntimeError, match='already owned'):
        with TestClient(create_app(Config(runtime=app.state.database.root))):
            pass
    rid = submit(client, prepared(client)).json()['run_id']
    assert wait_for_run(client, rid)['status'] == 'COMPLETED'


@pytest.mark.parametrize('query', ['limit=0', 'limit=-1', 'limit=201', 'limit=bad', 'cursor=bad'])
def test_pagination_invalid_inputs_have_typed_errors(live, query):
    client, _ = live
    rid = submit(client, prepared(client)).json()['run_id']
    assert wait_for_run(client, rid)['status'] == 'COMPLETED'
    response = client.get(f'/api/v1/runs/{rid}/decisions?{query}')
    assert response.status_code == 422 and response.json()['code'] == 'ASSUMPTIONS_INCOMPLETE'


def test_pagination_cursor_is_run_bound_and_exhaustive(live):
    client, _ = live
    body = prepared(client)
    rid = submit(client, body).json()['run_id']
    wait_for_run(client, rid)
    first = client.get(f'/api/v1/runs/{rid}/decisions?limit=1').json()
    other = submit(client, body, 'cursor-other-run').json()['run_id']
    wait_for_run(client, other)
    assert client.get(f'/api/v1/runs/{other}/decisions', params={'cursor': first['next_cursor']}).status_code == 422
    items, cursor = [], None
    while True:
        page = client.get(f'/api/v1/runs/{rid}/decisions', params={'limit': 1, **({'cursor': cursor} if cursor else {})}).json()
        items.extend(page['items'])
        cursor = page['next_cursor']
        if cursor is None:
            break
    assert len(items) == len({d['decision_id'] for d in items}) == 6
    assert items == sorted(items, key=lambda d: (d['origin'], d['policy_id']))


def test_source_mutation_after_startup_fails_run(live):
    client, app = live
    body = prepared(client)
    source = next(app.state.database.root.glob('ws_*/raw/*.csv'))
    source.write_bytes(b'changed')
    rid = submit(client, body).json()['run_id']
    assert wait_for_run(client, rid)['status'] == 'FAILED'


def test_real_process_kill_releases_lease_and_recovers_run(local_root):
    with client_for(local_root) as (client, app):
        body = prepared(client)
    script = '''import json,sys,time,threading
from pathlib import Path
from app.api.application import create_app
from app.api.security import Config
from app.services.worker import enqueue
root=Path(sys.argv[1]); body=json.loads(sys.argv[2])
app=create_app(Config(runtime=root)); worker=app.state.worker
worker.execute=lambda row: threading.Event().wait(60)
worker.start()
with app.state.database.transaction() as db:
    row=dict(enqueue(app.state.database,db,app.state.workspace,body))
worker.wake.set()
while True:
    with app.state.database.read() as db:
        status=db.execute('SELECT status FROM runs WHERE id=?',(row['id'],)).fetchone()[0]
    if status=='RUNNING':
        (root/'crash.json').write_text(json.dumps({'run_id':row['id']}))
        break
    time.sleep(.01)
threading.Event().wait(60)
'''
    child = subprocess.Popen([sys.executable, '-c', script, str(local_root), json.dumps(body)],
                             cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    marker = local_root / 'crash.json'
    try:
        deadline = time.monotonic() + 5
        while not marker.exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(.02)
        assert marker.exists(), 'Child did not commit a running job'
        rid = json.loads(marker.read_text())['run_id']
    finally:
        child.kill()
        child.communicate(timeout=5)
    with client_for(local_root) as (client, app):
        recovered = client.get('/api/v1/runs/' + rid).json()
        assert recovered['status'] == 'INTERRUPTED'
        assert client.get('/api/v1/runs/' + rid + '/metrics').status_code == 409


def test_duplicate_policy_ids_rejected_without_reservation(live):
    client, app = live
    body = prepared(client)
    response = submit(client, {**body, 'policy_ids': ['cash_only', 'cash_only']})
    assert response.status_code == 422
    assert submit(client, body).status_code == 202


def test_terminal_evidence_and_run_identity_immutable(live):
    client, app = live
    rid = submit(client, prepared(client)).json()['run_id']
    wait_for_run(client, rid)
    for sql in ["UPDATE runs SET status='RUNNING'", "DELETE FROM runs", "DELETE FROM decisions",
                "DELETE FROM ledger_events", "DELETE FROM metrics", "UPDATE run_reports SET body_json='{}'",
                "UPDATE repo_lots SET status='LOCKED'"]:
        with pytest.raises(sqlite3.IntegrityError):
            with app.state.database.transaction() as db:
                db.execute(sql)


def test_export_has_inputs_nonempty_ledger_reconciled_hashes_and_provenance(live):
    client, app = live
    body = prepared(client)
    rid = submit(client, body).json()['run_id']
    assert wait_for_run(client, rid)['status'] == 'COMPLETED'
    bundle = client.get(f'/api/v1/runs/{rid}/export').json()
    assert client.get(f'/api/v1/runs/{rid}/export').json() == bundle
    members = {m['name']: m for m in bundle['members']}
    manifest = json.loads(members['manifest.json']['content'])
    for name, member in members.items():
        assert hashlib.sha256(member['content'].encode()).hexdigest() == member['sha256']
        if name != 'manifest.json':
            assert manifest['members_sha256'][name] == member['sha256']
    assert json.loads(members['ledger_events.json']['content'])
    assert json.loads(members['scenario.json']['content'])['settings']['fictional_acknowledged']
    assert json.loads(members['review.json']['content'])['mode'] == 'self_review'
    assert manifest['run_fingerprint'] and manifest['integrity'].endswith('unsigned')
    reports = json.loads(members['accounting.json']['content'])
    assert reports['cash_only']['net_external_flows_cents'] == str(72 * 1005)
    assert 'raw' not in members and all('/' not in name for name in members)
