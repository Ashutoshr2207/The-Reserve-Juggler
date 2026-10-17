"""Versioned SQLite metadata; callers own explicit mutation transactions."""
import hashlib
import json
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager, closing
from pathlib import Path

from app.api.contracts import ROOT, Problem, canonical


MIGRATIONS = [
    (1, ROOT / 'migrations/001_initial.sql'),
    (2, ROOT / 'migrations/002_evidence_ledger.sql'),
    (3, ROOT / 'migrations/003_worker_lifecycle.sql'),
]
CURRENT_SCHEMA_VERSION = 3


def generated(prefix):
    return prefix + '_' + uuid.uuid4().hex


class Database:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / 'metadata.sqlite3'
        self.migrate()

    def connect(self):
        db = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA busy_timeout=5000')
        return db

    def migrate(self):
        with closing(self.connect()) as db:
            # Exclusive initialization also handles simultaneous first startups.
            db.execute('BEGIN EXCLUSIVE')
            try:
                exists = db.execute("SELECT 1 FROM sqlite_master WHERE name='schema_version'").fetchone()
                if exists:
                    versions = [r[0] for r in db.execute('SELECT version FROM schema_version')]
                    if len(versions) != 1 or versions[0] > CURRENT_SCHEMA_VERSION or versions[0] < 1:
                        raise RuntimeError('Unsupported database version; restore a compatible snapshot.')
                    current = versions[0]
                else:
                    if db.execute("SELECT 1 FROM sqlite_master WHERE type='table'").fetchone():
                        raise RuntimeError('Unversioned database requires maintainer review.')
                    current = 0

                migrations = [
                    (1, ROOT / 'migrations/001_initial.sql'),
                    (2, ROOT / 'migrations/002_evidence_ledger.sql'),
                    (3, ROOT / 'migrations/003_worker_lifecycle.sql'),
                ]
                for v, path in migrations:
                    if v > current:
                        # executescript implicitly commits: execute complete statements individually.
                        statement = ''
                        for line in path.read_text(encoding='utf-8').splitlines(True):
                            statement += line
                            if sqlite3.complete_statement(statement):
                                db.execute(statement)
                                statement = ''

                if db.execute('PRAGMA foreign_key_check').fetchall():
                    raise RuntimeError('Foreign key verification failed.')
                db.commit()
            except BaseException:
                db.rollback()
                raise

    def workspace(self):
        with self.transaction() as db:
            row = db.execute('SELECT id FROM workspaces ORDER BY rowid LIMIT 1').fetchone()
            if row:
                return row[0]
            identity = generated('ws')
            db.execute('INSERT INTO workspaces VALUES(?)', (identity,))
            return identity

    @contextmanager
    def read(self):
        with closing(self.connect()) as db:
            yield db

    @contextmanager
    def transaction(self):
        db = self.connect()
        try:
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def owned(self, db, table, workspace, identity):
        assert table in ('datasets', 'scenarios', 'runs')
        row = db.execute(f'SELECT * FROM {table} WHERE workspace_id=? AND id=?', (workspace, identity)).fetchone()
        if row is None:
            raise Problem(404, 'NOT_FOUND', 'Resource was not found.')
        return row

    def mutate(self, workspace, operation, key, payload, effect):
        digest = hashlib.sha256(canonical(payload).encode()).hexdigest()
        with self.transaction() as db:
            now = time.time()
            db.execute('DELETE FROM idempotency WHERE expires_at<=?', (now,))
            row = db.execute('SELECT * FROM idempotency WHERE workspace_id=? AND operation=? AND key=?',
                             (workspace, operation, key)).fetchone()
            if row:
                if row['payload_hash'] != digest:
                    raise Problem(409, 'IDEMPOTENCY_CONFLICT', 'Key already belongs to different request content.')
                return row['response_status'], json.loads(row['response_json']), json.loads(row['headers_json'])
            db.execute('INSERT INTO idempotency(workspace_id,operation,key,payload_hash,expires_at) VALUES(?,?,?,?,?)',
                       (workspace, operation, key, digest, now + 86400))
            status, body, headers = effect(db)
            db.execute('UPDATE idempotency SET response_json=?,response_status=?,headers_json=? '
                       'WHERE workspace_id=? AND operation=? AND key=?',
                       (canonical(body), status, canonical(headers), workspace, operation, key))
            return status, body, headers

    def register_source(self, workspace, temporary, digest):
        directory = self.root / workspace / 'raw'
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / (digest + '.csv')
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise RuntimeError('Stored source integrity failure')
        else:
            # Validated, generated path; file is durable before the referencing DB commit.
            os.replace(temporary, target)
        return target.name

    def verify_sources(self):
        with self.read() as db:
            for row in db.execute('SELECT workspace_id,sha256,source_name FROM datasets'):
                expected = row['sha256'] + '.csv'
                if row['source_name'] != expected:
                    raise RuntimeError('Invalid source reference')
                source = self.root / row['workspace_id'] / 'raw' / expected
                if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != row['sha256']:
                    raise RuntimeError('Stored source integrity failure')
