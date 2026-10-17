import copy
import hashlib
import importlib.util
import json
import sqlite3

import pytest

from app.api.contracts import ROOT
from app.maintenance import snapshot, verify_runtime
from conftest import client_for, review, scenario, wait_for_run


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f'tools/{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_client_is_reproducible():
    from app.api.generated_client import CONTRACT_SHA256
    assert CONTRACT_SHA256 == hashlib.sha256((ROOT / 'contracts/openapi.json').read_bytes()).hexdigest()
    assert (ROOT / 'app/api/generated_client.py').read_text() == load_tool('generate_client').render()


def test_verified_offline_backup_restore_contains_complete_runs(local_root):
    runtime, backup, restored = (local_root / name for name in ('r', 'b', 's'))
    with client_for(runtime) as (client, app):
        value = scenario(client).json()
        assert review(client, value).status_code == 200
        accepted = client.post('/api/v1/runs', json={'scenario_id': value['scenario_id'],
                    'policy_ids': ['cash_only', 'fixed_repo'], 'forecast_mode': 'disabled',
                    'adapter_artifact_id': None}, headers={'Idempotency-Key': 'backup-run-key'}).json()
        assert wait_for_run(client, accepted['run_id'])['status'] == 'COMPLETED'
        original = client.get('/api/v1/runs/' + accepted['run_id'] + '/export').json()
        with pytest.raises(RuntimeError, match='already owned'):
            snapshot(runtime, backup)
    assert snapshot(runtime, backup)['verified']
    assert snapshot(backup, restored, restore=True)['verified']
    assert verify_runtime(runtime) == verify_runtime(restored)
    with pytest.raises(ValueError, match='never overwritten'):
        snapshot(runtime, backup)
    with client_for(restored) as (client, app):
        assert client.get('/api/v1/runs/' + accepted['run_id'] + '/export').json() == original
        assert load_tool('verify_export').verify(original)['verified_members'] == 11


def test_export_verifier_rejects_corruption_duplicates_and_paths(live):
    client, app = live
    value = scenario(client).json()
    review(client, value)
    run = client.post('/api/v1/runs', json={'scenario_id': value['scenario_id'],
                'policy_ids': ['cash_only'], 'forecast_mode': 'disabled', 'adapter_artifact_id': None},
                headers={'Idempotency-Key': 'verify-export-run'}).json()
    wait_for_run(client, run['run_id'])
    original = client.get('/api/v1/runs/' + run['run_id'] + '/export').json()
    verify = load_tool('verify_export').verify
    assert verify(original)['integrity_only']
    bad = copy.deepcopy(original)
    bad['members'][1]['content'] += 'changed'
    with pytest.raises(ValueError, match='digest'):
        verify(bad)
    bad = copy.deepcopy(original)
    bad['members'].append(bad['members'][1])
    with pytest.raises(ValueError, match='duplicate'):
        verify(bad)
    bad = copy.deepcopy(original)
    bad['members'][1]['name'] = '../config.json'
    with pytest.raises(RuntimeError, match='contract'):
        verify(bad)


def test_snapshot_tamper_rejected_before_restore(local_root):
    runtime, backup, restored = (local_root / name for name in ('r', 'b', 's'))
    with client_for(runtime) as (client, app):
        scenario(client)
    snapshot(runtime, backup)
    raw = next(backup.glob('ws_*/raw/*.csv'))
    raw.write_bytes(b'modified')
    with pytest.raises(ValueError, match='Source integrity'):
        snapshot(backup, restored, restore=True)
    assert not restored.exists()


def test_forward_v2_migration_preserves_records(local_root):
    local_root.mkdir(parents=True)
    connection = sqlite3.connect(local_root / 'metadata.sqlite3')
    try:
        for name in ('001_initial.sql', '002_evidence_ledger.sql'):
            connection.executescript((ROOT / 'migrations' / name).read_text())
        connection.execute("INSERT INTO workspaces VALUES('ws_historical')")
        connection.commit()
    finally:
        connection.close()
    from app.storage.database import Database
    database = Database(local_root)
    with database.read() as db:
        assert db.execute('SELECT version FROM schema_version').fetchone()[0] == 3
        assert db.execute('SELECT id FROM workspaces').fetchone()[0] == 'ws_historical'
