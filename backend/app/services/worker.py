"""One durable local worker. SQLite owns queue, cancellation and commit ordering."""
import hashlib
import json
import os
import threading
from datetime import datetime, timezone

from app.api.contracts import ROOT, Problem, canonical
from app.services.simulation import ENGINE_VERSION, RunStopped, execute_simulation

TERMINAL = ('COMPLETED', 'FAILED', 'CANCELLED', 'INTERRUPTED')


def now():
    return datetime.now(timezone.utc).isoformat()


def provenance(dataset_hash, fingerprint, body):
    # Code identities pin the actual calculation, rather than a manually bumped label alone.
    files = ['app/domain/ledger.py', 'app/domain/adapter.py', 'app/services/simulation.py',
             'app/services/comparison.py', 'app/services/worker.py', 'contracts/openapi.json',
             'contracts/forecast-adapter.schema.json', 'requirements.lock']
    record = {'engine_version': ENGINE_VERSION, 'dataset_sha256': dataset_hash,
              'scenario_fingerprint': fingerprint, 'policy_ids': body['policy_ids'],
              'forecast_mode': body['forecast_mode'], 'adapter_artifact_id': body['adapter_artifact_id'],
              'effective_adapter': 'seasonal_baseline' if body['forecast_mode'] == 'baseline' else 'disabled',
              'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files}}
    return record, hashlib.sha256(canonical(record).encode()).hexdigest()


def enqueue(database, db, workspace, body):
    if len(set(body['policy_ids'])) != len(body['policy_ids']):
        raise Problem(422, 'ASSUMPTIONS_INCOMPLETE', 'Policies must be unique.')
    scenario = database.owned(db, 'scenarios', workspace, body['scenario_id'])
    if scenario['status'] != 'REVIEWED':
        raise Problem(422, 'ASSUMPTIONS_INCOMPLETE', 'Scenario must be reviewed before running.')
    if db.execute("SELECT count(*) FROM runs WHERE status='QUEUED'").fetchone()[0] >= 5:
        raise Problem(503, 'QUEUE_FULL', 'Local run queue is full.', retryable=True)
    dataset = database.owned(db, 'datasets', workspace, scenario['dataset_id'])
    profile = json.loads(dataset['profile_json'])
    record, fingerprint = provenance(dataset['sha256'], scenario['fingerprint'], body)
    from app.storage.database import generated
    identity, timestamp = generated('run'), now()
    db.execute('''INSERT INTO runs(workspace_id,id,scenario_id,scenario_fingerprint,
               status,total_hours,forecast_mode,adapter_artifact_id,created_at,updated_at,
               engine_version,run_fingerprint,provenance_json)
               VALUES(?,?,?,?,'QUEUED',?,?,?,?,?,?,?,?)''',
               (workspace, identity, scenario['id'], scenario['fingerprint'], profile['rows'],
                body['forecast_mode'], body['adapter_artifact_id'], timestamp, timestamp,
                ENGINE_VERSION, fingerprint, canonical(record)))
    db.executemany('INSERT INTO run_policies VALUES(?,?,?)',
                   [(workspace, identity, pid) for pid in body['policy_ids']])
    return database.owned(db, 'runs', workspace, identity)


class RuntimeLease:
    """OS byte-range lock is released on process exit; no stale PID deletion needed."""
    def __init__(self, root):
        self.path, self.file = root / 'worker.lock', None

    def acquire(self):
        self.file = self.path.open('a+b')
        if self.path.stat().st_size == 0:
            self.file.write(b'0')
            self.file.flush()
        self.file.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.file.close()
            self.file = None
            raise RuntimeError('Runtime is already owned by another worker.') from None

    def release(self):
        if self.file:
            self.file.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)
            self.file.close()
            self.file = None


class RunWorker:
    def __init__(self, database):
        self.database = database
        self.stop = threading.Event()
        self.wake = threading.Event()
        self.thread = None
        self.lease = RuntimeLease(database.root)

    def recover(self):
        with self.database.transaction() as db:
            db.execute("""UPDATE runs SET status='INTERRUPTED',financial_outcome=NULL,
                       warnings_json=?,updated_at=? WHERE status IN ('QUEUED','RUNNING')""",
                       (canonical(['STARTUP_RECOVERY: incomplete run; create a new run to replay.']), now()))

    def start(self):
        self.lease.acquire()
        try:
            self.database.verify_sources()
            self.recover()
            self.thread = threading.Thread(target=self.loop, name='rg-local-worker', daemon=False)
            self.thread.start()
        except BaseException:
            self.lease.release()
            raise

    def close(self):
        self.stop.set()
        self.wake.set()
        if self.thread:
            self.thread.join(10)
            if self.thread.is_alive():
                raise RuntimeError('Worker did not stop; runtime lease retained.')
        try:
            self.recover()
        finally:
            self.lease.release()

    def claim(self):
        with self.database.transaction() as db:
            row = db.execute("SELECT * FROM runs WHERE status='QUEUED' ORDER BY created_at,id LIMIT 1").fetchone()
            if row:
                db.execute("UPDATE runs SET status='RUNNING',updated_at=? WHERE workspace_id=? AND id=?",
                           (now(), row['workspace_id'], row['id']))
                return dict(row)

    def finish_failure(self, row, stopped):
        with self.database.transaction() as db:
            current = self.database.owned(db, 'runs', row['workspace_id'], row['id'])
            if current['status'] in TERMINAL:
                return
            state = ('CANCELLED' if current['cancel_requested'] else 'INTERRUPTED') if stopped else 'FAILED'
            warning = ('RUN_CANCELLED: incomplete evidence.' if state == 'CANCELLED' else
                       'RUN_INTERRUPTED: replay in a new run.' if state == 'INTERRUPTED' else
                       'RUN_FAILED: calculation or storage failed; complete metrics unavailable.')
            db.execute('UPDATE runs SET status=?,financial_outcome=NULL,warnings_json=?,updated_at=? '
                       'WHERE workspace_id=? AND id=?',
                       (state, canonical([warning]), now(), row['workspace_id'], row['id']))

    def execute(self, row):
        with self.database.read() as db:
            workspace = row['workspace_id']
            scenario = dict(self.database.owned(db, 'scenarios', workspace, row['scenario_id']))
            dataset = dict(self.database.owned(db, 'datasets', workspace, scenario['dataset_id']))
            policies = json.loads(row['provenance_json'])['policy_ids']
        execute_simulation(self.database, workspace, row['id'], scenario, dataset,
                           self.database.root / workspace / 'raw' / (dataset['sha256'] + '.csv'),
                           policies, row['forecast_mode'], row['adapter_artifact_id'], self.stop)

    def loop(self):
        while not self.stop.is_set():
            try:
                row = self.claim()
            except Exception:
                # Storage may be temporarily unavailable. Do not leak local paths in logs.
                self.stop.wait(.25)
                continue
            if row:
                try:
                    self.execute(row)
                except Exception as exc:
                    try:
                        self.finish_failure(row, isinstance(exc, RunStopped))
                    except Exception:
                        # Stop accepting work if failure status cannot be persisted.
                        # Startup recovery will mark the preserved run INTERRUPTED.
                        self.stop.set()
            else:
                self.wake.wait(.1)
                self.wake.clear()
