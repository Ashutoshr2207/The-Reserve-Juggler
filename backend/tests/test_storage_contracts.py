import hashlib
import json
import shutil
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from openapi_spec_validator import OpenAPIV31SpecValidator

from app.api.application import create_app
from app.api.contracts import CONTRACT, ROOT, Problem, canonical, validate
from app.api.security import Config
from app.storage.database import Database
from conftest import client_for, review, scenario, upload


def test_canonical_contract_standards_and_implemented_surface(live):
    assert list(OpenAPIV31SpecValidator(CONTRACT).iter_errors()) == []
    app = live[1]
    exported = app.openapi()
    assert list(OpenAPIV31SpecValidator(exported).iter_errors()) == []
    actual = {(route.path.removeprefix('/api/v1'), method.lower()): route.operation_id
              for route in app.routes if route.path.startswith('/api/v1') for method in route.methods}
    expected = {(path, method): operation['operationId'] for path, methods in exported['paths'].items()
                for method, operation in methods.items()}
    assert actual == expected and len(actual) == 12
    assert exported['components'] == CONTRACT['components']
    for schema in CONTRACT['components']['schemas'].values():
        Draft202012Validator.check_schema(schema)
    fixture = json.loads((ROOT / 'contracts/examples/first_slice.json').read_text())
    for case in fixture['http_cases']:
        validate(case['schema'], case['value'])
    adapter = json.loads((ROOT / 'contracts/forecast-adapter.schema.json').read_text())
    Draft202012Validator.check_schema(adapter)
    for case in fixture['adapter_cases']:
        Draft202012Validator(adapter).validate(case)


def test_all_shared_baseline_hashes_unchanged():
    manifest = json.loads((ROOT / 'docs/assignments/SYNC_MANIFEST.json').read_text())
    for filename, digest in manifest['shared_sha256'].items():
        assert hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == digest, filename


def test_persistence_and_review_retry_survive_restart(local_root):
    with client_for(local_root) as (client, app):
        original = scenario(client).json()
        reviewed = review(client, original).json()
        workspace = app.state.workspace
    with client_for(local_root) as (client, app):
        assert app.state.workspace == workspace
        assert client.get('/api/v1/scenarios/' + original['scenario_id']).json() == reviewed
        assert review(client, original).json() == reviewed
        # A replay returns its original response snapshot, even after later review.
        assert scenario(client, original['dataset_id']).json() == original


def test_foreign_keys_immutability_and_failed_effect_rollback(live):
    client, app = live
    original = scenario(client).json()
    database = app.state.database
    for sql in ["UPDATE scenarios SET fingerprint='changed'", "UPDATE scenarios SET body_json='{}'",
                "UPDATE datasets SET sha256='changed'",
                "INSERT INTO scenarios VALUES('ws_missing','sc_bad','ds_missing','x','{}','DRAFT')"]:
        with pytest.raises(sqlite3.IntegrityError):
            with database.transaction() as db:
                db.execute(sql)
    def fail(db):
        db.execute('INSERT INTO workspaces VALUES(?)', ('ws_rollback',))
        raise RuntimeError('Simulated failure')
    with pytest.raises(RuntimeError):
        database.mutate(app.state.workspace, 'test', 'failure-key-01', {}, fail)
    with database.read() as db:
        assert db.execute('SELECT id FROM workspaces WHERE id=?', ('ws_rollback',)).fetchone() is None
        assert db.execute('SELECT * FROM idempotency WHERE key=?', ('failure-key-01',)).fetchone() is None
        assert db.execute('PRAGMA foreign_key_check').fetchall() == []


def test_expired_key_can_create_new_operation(live):
    client, app = live
    first = scenario(client).json()
    with app.state.database.transaction() as db:
        db.execute("UPDATE idempotency SET expires_at=0 WHERE operation='createScenario'")
    second = scenario(client, first['dataset_id']).json()
    assert second['scenario_id'] != first['scenario_id']


def test_fresh_and_repeated_and_concurrent_migration(local_root):
    with ThreadPoolExecutor(max_workers=4) as workers:
        databases = list(workers.map(lambda _: Database(local_root), range(4)))
    db = databases[0]
    db.migrate()
    with db.read() as connection:
        assert [r[0] for r in connection.execute('SELECT version FROM schema_version')] == [3]
        assert connection.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert connection.execute('PRAGMA foreign_keys').fetchone()[0] == 1


def test_forward_migration_from_v1_to_v2(local_root):
    v1_path = local_root / 'v1_db'
    v1_path.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(v1_path / 'metadata.sqlite3')
    statement = ''
    for line in (ROOT / 'migrations/001_initial.sql').read_text().splitlines(True):
        statement += line
        if sqlite3.complete_statement(statement):
            conn.execute(statement)
            statement = ''
    assert [r[0] for r in conn.execute('SELECT version FROM schema_version')] == [1]
    conn.commit()
    conn.close()

    db = Database(v1_path)
    with db.read() as connection:
        assert [r[0] for r in connection.execute('SELECT version FROM schema_version')] == [3]
        assert connection.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert connection.execute('PRAGMA foreign_keys').fetchone()[0] == 1
        tables = [r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for expected_table in ('runs', 'decisions', 'metrics', 'metric_sets', 'ledger_events', 'repo_lots'):
            assert expected_table in tables


def test_future_and_unversioned_database_fail_closed(local_root):
    database = Database(local_root)
    with database.transaction() as db:
        db.execute('DROP TABLE schema_version')
        db.execute('CREATE TABLE schema_version(version INTEGER PRIMARY KEY)')
        db.execute('INSERT INTO schema_version VALUES(4)')
    before = database.path.read_bytes()
    with pytest.raises(RuntimeError, match='Unsupported database version'):
        Database(local_root)
    assert database.path.read_bytes() == before
    with database.transaction() as db:
        db.execute('DROP TABLE schema_version')
    with pytest.raises(RuntimeError, match='Unversioned database'):
        Database(local_root)


def test_failed_migration_is_atomic(local_root, monkeypatch):
    import app.storage.database as storage_module
    (local_root / 'spec/migrations').mkdir(parents=True)
    (local_root / 'spec/migrations/001_initial.sql').write_text('CREATE TABLE test(id INTEGER);\nINVALID SQL;\n')
    monkeypatch.setattr(storage_module, 'ROOT', local_root / 'spec')
    with pytest.raises(sqlite3.OperationalError):
        Database(local_root / 'db')
    connection = sqlite3.connect(local_root / 'db/metadata.sqlite3')
    try:
        assert connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall() == []
    finally:
        connection.close()


def test_offline_backup_restore_and_source_tamper(local_root):
    runtime, backup, restored = (local_root / p for p in ('runtime', 'backup', 'restored'))
    with client_for(runtime) as (client, app):
        value = scenario(client).json()
        review(client, value)
    # Server closed: copy metadata and owned raw files as one offline snapshot.
    shutil.copytree(runtime, backup)
    shutil.copytree(backup, restored)
    with client_for(restored) as (client, app):
        assert client.get('/api/v1/scenarios/' + value['scenario_id']).json()['status'] == 'REVIEWED'
        with app.state.database.read() as db:
            assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
            assert db.execute('PRAGMA foreign_key_check').fetchall() == []
    raw_file = next(restored.glob('ws_*/raw/*.csv'))
    raw_file.write_bytes(b'tampered')
    with pytest.raises(RuntimeError, match='source integrity'):
        create_app(Config(runtime=restored))


def test_storage_failure_is_redacted_and_no_success_cached(live, monkeypatch):
    client, app = live
    def unavailable(*args):
        raise sqlite3.OperationalError('private C:/secret/storage path')
    monkeypatch.setattr(app.state.database, 'register_source', unavailable)
    response = upload(client)
    assert response.status_code == 503
    assert response.json()['retryable'] is True
    assert 'secret' not in response.text and 'C:/' not in response.text
    with app.state.database.read() as db:
        assert db.execute('SELECT count(*) FROM idempotency').fetchone()[0] == 0
        assert db.execute('SELECT count(*) FROM datasets').fetchone()[0] == 0


def test_source_move_then_metadata_failure_is_not_selectable_and_retry_recovers(live, monkeypatch):
    client, app = live
    database = app.state.database
    register = database.register_source
    def fail_after_move(*args):
        register(*args)
        raise RuntimeError('Simulated post-move failure')
    monkeypatch.setattr(database, 'register_source', fail_after_move)
    response = upload(client)
    assert response.status_code == 503
    with database.read() as db:
        assert db.execute('SELECT count(*) FROM datasets').fetchone()[0] == 0
        assert db.execute('SELECT count(*) FROM idempotency').fetchone()[0] == 0
    # A crash may leave an unreferenced content-addressed file; it is never a dataset.
    assert len(list(database.root.glob('ws_*/raw/*.csv'))) == 1
    monkeypatch.setattr(database, 'register_source', register)
    assert upload(client).status_code == 201
    database.verify_sources()
