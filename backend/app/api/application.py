import hashlib
import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import hmac

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse, JSONResponse, Response
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware

from app.api.contracts import CONTRACT, Problem, canonical, issue, validate
from app.api.security import Config, LocalSession
from app.domain.intake import profile, settings_semantics
from app.services.simulation import build_evidence_bundle, require_complete
from app.services.worker import RunWorker, RuntimeLease, enqueue, TERMINAL
from app.services.upload import receive_csv
from app.storage.database import Database, generated

ID = re.compile(r'^[a-z][a-z0-9_-]{1,79}$')
HASH = re.compile(r'^[0-9a-f]{64}$')


def run_view(row):
    return {
        'run_id': row['id'],
        'scenario_id': row['scenario_id'],
        'scenario_fingerprint': row['scenario_fingerprint'],
        'contract_version': row['contract_version'],
        'status': row['status'],
        'financial_outcome': row['financial_outcome'],
        'completed_hours': row['completed_hours'],
        'total_hours': row['total_hours'],
        'warnings': json.loads(row['warnings_json']),
    }


async def json_body(request):
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > 65536:
            raise Problem(422, 'ASSUMPTIONS_INCOMPLETE', 'JSON body exceeds 64 KiB.')
    if request.headers.get('content-type', '').split(';')[0] != 'application/json':
        raise Problem(422, 'ASSUMPTIONS_INCOMPLETE', 'Expected application/json.')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate key')
            result[key] = value
        return result
    def nonfinite(_):
        raise ValueError('Nonfinite JSON')
    try:
        return json.loads(data, object_pairs_hook=pairs, parse_constant=nonfinite)
    except (ValueError, UnicodeError, RecursionError):
        raise Problem(422, 'ASSUMPTIONS_INCOMPLETE', 'Malformed JSON.') from None


def request_key(request):
    key = request.headers.get('idempotency-key', '')
    if not 8 <= len(key) <= 128 or any(ord(c) < 33 or ord(c) > 126 for c in key):
        raise Problem(422, 'ASSUMPTIONS_INCOMPLETE', 'A valid Idempotency-Key is required.',
                      [issue('Idempotency-Key', 'Expected 8–128 printable nonspace ASCII characters.')])
    return key


def resource_id(value):
    if not ID.fullmatch(value):
        raise Problem(404, 'NOT_FOUND', 'Resource was not found.')
    return value


def scenario_view(row):
    result = json.loads(row['body_json'])
    result['status'] = row['status']
    return result


def create_app(config=None):
    config = config or Config()
    config.runtime.mkdir(parents=True, exist_ok=True)
    initialization = RuntimeLease(config.runtime)
    initialization.acquire()
    try:
        database = Database(config.runtime)
        workspace = database.workspace()
        database.verify_sources()
    finally:
        initialization.release()
    session = LocalSession(config)
    worker = RunWorker(database)

    @asynccontextmanager
    async def lifespan(app):
        await run_in_threadpool(worker.start)
        try:
            yield
        finally:
            await run_in_threadpool(worker.close)

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.state.worker = worker
    app.state.database, app.state.session, app.state.workspace = database, session, workspace
    # Expose canonical contract now that /runs are implemented in BE-02
    app.openapi = lambda: CONTRACT

    def failure(request, error):
        body = {'code': error.code, 'message': error.message, 'request_id': request.state.request_id,
                'retryable': error.retryable, 'details': error.details}
        validate('Error', body, output=True)
        return JSONResponse(body, status_code=error.status,
                            headers={'Retry-After': '1'} if error.code == 'QUEUE_FULL' else None)

    @app.middleware('http')
    async def guard(request, call_next):
        request.state.request_id = 'req_' + uuid.uuid4().hex
        try:
            session.check_host(request)
            if request.url.path not in ('/local/session', '/local/bootstrap'):
                session.authenticate(request)
            response = await call_next(request)
        except Problem as exc:
            response = failure(request, exc)
        except sqlite3.OperationalError:
            response = failure(request, Problem(503, 'INTERNAL_ERROR', 'Local storage is temporarily unavailable.', retryable=True))
        except Exception:
            response = failure(request, Problem(503, 'INTERNAL_ERROR', 'Local operation failed.', retryable=False))
        response.headers['X-Request-ID'] = request.state.request_id
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = "default-src 'none'; script-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
        return response

    @app.exception_handler(Problem)
    async def problem_handler(request, exc):
        return failure(request, exc)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request, exc):
        return failure(request, Problem(422, 'ASSUMPTIONS_INCOMPLETE', 'Invalid request parameters.'))

    @app.exception_handler(HTTPException)
    async def http_handler(request, exc):
        return failure(request, Problem(404, 'NOT_FOUND', 'Resource or operation was not found.'))

    def result(name, body, status=200, headers=None):
        validate(name, body, output=True)
        return JSONResponse(body, status_code=status, headers=headers)

    def stored(name, value):
        status, body, headers = value
        return result(name, body, status, headers)

    @app.get('/local/session', include_in_schema=False)
    async def bootstrap_page():
        return HTMLResponse('''<!doctype html><html lang="en"><title>Local simulation session</title>
<p id="status">Starting local session…</p><script>
const token=location.hash.slice(1); history.replaceState(null,'','/local/session');
fetch('/local/bootstrap',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({capability:token})}).then(async r=>{
if(!r.ok) throw Error(); document.getElementById('status').textContent=
'Local simulation session ready. Open the integrated frontend when available.';
}).catch(()=>document.getElementById('status').textContent='Restart the local launcher to obtain a new session.');
</script></html>''')

    @app.post('/local/bootstrap', include_in_schema=False)
    async def bootstrap(request: Request):
        if request.headers.get('origin') != config.origin:
            raise Problem(403, 'FORBIDDEN', 'Local bootstrap origin is required.')
        body = await json_body(request)
        if not isinstance(body, dict) or set(body) != {'capability'} or not isinstance(body['capability'], str):
            raise Problem(401, 'UNAUTHORIZED', 'Invalid local bootstrap.')
        session.exchange(body['capability'])
        response = Response(status_code=204, headers={'X-CSRF-Token': session.csrf})
        response.set_cookie('rg_session', session.token, httponly=True, samesite='strict', path='/')
        return response

    @app.get('/local/csrf', include_in_schema=False)
    async def csrf():
        return Response(status_code=204, headers={'X-CSRF-Token': session.csrf})

    @app.post('/local/logout', include_in_schema=False)
    async def logout():
        session.revoke()
        response = Response(status_code=204)
        response.delete_cookie('rg_session', path='/', httponly=True, samesite='strict')
        return response

    @app.get('/api/v1/workspace', operation_id='getWorkspace')
    async def get_workspace():
        session.role('getWorkspace')
        return result('Workspace', {'workspace_id': workspace, 'contract_version': '0.1.0',
                                   'role_mode': config.role, 'simulation_only': True})

    @app.post('/api/v1/datasets', operation_id='importDataset')
    async def import_dataset(request: Request):
        session.role('importDataset')
        key = request_key(request)
        temporary = await receive_csv(request, config.runtime / 'tmp')
        try:
            source = temporary.read_bytes()
            digest = hashlib.sha256(source).hexdigest()
            def effect(db):
                existing = db.execute('SELECT profile_json FROM datasets WHERE workspace_id=? AND sha256=?',
                                      (workspace, digest)).fetchone()
                if existing:
                    return 201, json.loads(existing[0]), {}
                summary = profile(source)
                data = {'dataset_id': generated('ds'), **summary}
                validate('Dataset', data, output=True)
                name = database.register_source(workspace, temporary, summary['sha256'])
                db.execute('INSERT INTO datasets VALUES(?,?,?,?,?)',
                           (workspace, data['dataset_id'], summary['sha256'], name, canonical(data)))
                return 201, data, {}
            return stored('Dataset', database.mutate(workspace, 'importDataset', key,
                          {'source_sha256': digest}, effect))
        finally:
            temporary.unlink(missing_ok=True)

    @app.get('/api/v1/datasets/{dataset_id}', operation_id='getDataset')
    async def get_dataset(dataset_id: str):
        session.role('getDataset')
        with database.read() as db:
            row = database.owned(db, 'datasets', workspace, resource_id(dataset_id))
            return result('Dataset', json.loads(row['profile_json']))

    @app.post('/api/v1/scenarios', operation_id='createScenario')
    async def create_scenario(request: Request):
        session.role('createScenario')
        key = request_key(request)
        body = await json_body(request)
        def effect(db):
            validate('ScenarioCreate', body)
            if not body['label'].strip():
                raise Problem(422, 'ASSUMPTIONS_INCOMPLETE', 'Scenario label cannot be blank.')
            dataset = database.owned(db, 'datasets', workspace, body['dataset_id'])
            settings_semantics(body['settings'], json.loads(dataset['profile_json']))
            fingerprint = hashlib.sha256(canonical({'dataset_sha256': dataset['sha256'],
                          'settings': body['settings'], 'contract_version': '0.1.0'}).encode()).hexdigest()
            value = {'scenario_id': generated('sc'), **body, 'fingerprint': fingerprint,
                     'revision': 1, 'status': 'DRAFT'}
            validate('Scenario', value, output=True)
            db.execute('INSERT INTO scenarios VALUES(?,?,?,?,?,?)',
                       (workspace, value['scenario_id'], body['dataset_id'], fingerprint, canonical(value), 'DRAFT'))
            return 201, value, {'ETag': fingerprint}
        return stored('Scenario', database.mutate(workspace, 'createScenario', key, body, effect))

    @app.get('/api/v1/scenarios/{scenario_id}', operation_id='getScenario')
    async def get_scenario(scenario_id: str):
        session.role('getScenario')
        with database.read() as db:
            row = database.owned(db, 'scenarios', workspace, resource_id(scenario_id))
            return result('Scenario', scenario_view(row), headers={'ETag': row['fingerprint']})

    @app.post('/api/v1/scenarios/{scenario_id}/review', operation_id='reviewScenario')
    async def review_scenario(scenario_id: str, request: Request):
        session.role('reviewScenario')
        resource_id(scenario_id)
        key = request_key(request)
        body = await json_body(request)
        etag = request.headers.get('if-match', '')
        def effect(db):
            row = database.owned(db, 'scenarios', workspace, scenario_id)
            validate('ReviewRequest', body)
            if not body['actor_label'].strip():
                raise Problem(422, 'ASSUMPTIONS_INCOMPLETE', 'Actor display label cannot be blank.')
            if not HASH.fullmatch(etag) or etag != row['fingerprint']:
                raise Problem(409, 'STALE_REVISION', 'Review requires the exact current revision fingerprint.')
            if row['status'] == 'DRAFT':
                db.execute('INSERT INTO reviews VALUES(?,?,?,?,?,?)',
                           (workspace, scenario_id, etag, body['actor_label'],
                            'self_review' if config.role == 'operator' else 'local_reviewer',
                            datetime.now(timezone.utc).isoformat()))
                db.execute("UPDATE scenarios SET status='REVIEWED' WHERE workspace_id=? AND id=?",
                           (workspace, scenario_id))
            value = scenario_view(row)
            value['status'] = 'REVIEWED'
            return 200, value, {'ETag': etag}
        return stored('Scenario', database.mutate(workspace, 'reviewScenario:' + scenario_id, key,
                      {'request': body, 'if_match': etag}, effect))

    @app.post('/api/v1/runs', operation_id='createRun')
    async def create_run(request: Request):
        session.role('createRun')
        key = request_key(request)
        body = await json_body(request)
        def effect(db):
            validate('RunCreate', body)
            if worker.stop.is_set() or not worker.thread or not worker.thread.is_alive():
                raise Problem(503, 'INTERNAL_ERROR', 'Local worker is unavailable; restart the launcher.', retryable=True)
            row = enqueue(database, db, workspace, body)
            return 202, run_view(row), {}
        value = await run_in_threadpool(database.mutate, workspace, 'createRun', key, body, effect)
        worker.wake.set()
        return stored('Run', value)

    @app.get('/api/v1/runs/{run_id}', operation_id='getRun')
    async def get_run(run_id: str):
        session.role('getRun')
        resource_id(run_id)
        with database.read() as db:
            row = database.owned(db, 'runs', workspace, run_id)
            return result('Run', run_view(row))

    @app.post('/api/v1/runs/{run_id}/cancel', operation_id='cancelRun')
    async def cancel_run(run_id: str, request: Request):
        session.role('cancelRun')
        resource_id(run_id)
        key = request_key(request)
        def effect(db):
            row = database.owned(db, 'runs', workspace, run_id)
            if row['status'] not in TERMINAL:
                if row['status'] == 'QUEUED':
                    db.execute("UPDATE runs SET status='CANCELLED',cancel_requested=1,warnings_json=?,updated_at=? WHERE workspace_id=? AND id=?",
                               (canonical(['RUN_CANCELLED: queued work did not execute.']),
                                datetime.now(timezone.utc).isoformat(), workspace, run_id))
                else:
                    db.execute("UPDATE runs SET cancel_requested=1 WHERE workspace_id=? AND id=?", (workspace, run_id))
                row = database.owned(db, 'runs', workspace, run_id)
            return 200, run_view(row), {}
        value = await run_in_threadpool(database.mutate, workspace, 'cancelRun:' + run_id, key, {'run_id': run_id}, effect)
        worker.wake.set()
        return stored('Run', value)

    @app.get('/api/v1/runs/{run_id}/metrics', operation_id='getMetrics')
    async def get_metrics(run_id: str):
        session.role('getMetrics')
        resource_id(run_id)
        with database.read() as db:
            require_complete(database.owned(db, 'runs', workspace, run_id))
            ms_row = db.execute('SELECT * FROM metric_sets WHERE workspace_id=? AND run_id=?',
                                (workspace, run_id)).fetchone()
            if not ms_row:
                raise Problem(404, 'NOT_FOUND', 'Metrics not found for run.')
            m_rows = db.execute('SELECT * FROM metrics WHERE workspace_id=? AND run_id=? ORDER BY policy_id',
                                (workspace, run_id)).fetchall()
            metrics = [{
                'policy_id': r['policy_id'],
                'treasury_result_cents': r['treasury_result_cents'],
                'unpaid_new_cents': r['unpaid_new_cents'],
                'shortfall_hours': r['shortfall_hours'],
                'peak_debt_cents': r['peak_debt_cents'],
                'terminal_wealth_cents': r['terminal_wealth_cents'],
                'total_cost_cents': r['total_cost_cents'],
            } for r in m_rows]
            metric_set = {
                'run_id': run_id,
                'scenario_fingerprint': ms_row['scenario_fingerprint'],
                'metric_definition_version': ms_row['metric_definition_version'],
                'quality_label': ms_row['quality_label'],
                'metrics': metrics,
                'warnings': json.loads(ms_row['warnings_json']),
            }
            return result('MetricSet', metric_set)

    @app.get('/api/v1/runs/{run_id}/decisions', operation_id='getDecisions')
    async def get_decisions(run_id: str, cursor: str | None = None, limit: int = 50):
        session.role('getDecisions')
        resource_id(run_id)
        with database.read() as db:
            require_complete(database.owned(db, 'runs', workspace, run_id))
            if not 1 <= limit <= 200:
                raise Problem(422, 'ASSUMPTIONS_INCOMPLETE', 'Decision limit must be between 1 and 200.')
            offset = 0
            if cursor:
                try:
                    cursor_run, position, signature = cursor.split('.')
                    expected = hmac.new(session.csrf.encode(), f'{cursor_run}.{position}'.encode(), 'sha256').hexdigest()
                    if cursor_run != run_id or not position.isdecimal() or len(position) > 12 or not hmac.compare_digest(signature, expected):
                        raise ValueError()
                    offset = int(position)
                except ValueError:
                    raise Problem(422, 'ASSUMPTIONS_INCOMPLETE', 'Invalid decision cursor.') from None
            rows = db.execute('SELECT * FROM decisions WHERE workspace_id=? AND run_id=? ORDER BY origin,policy_id,decision_id LIMIT ? OFFSET ?',
                              (workspace, run_id, limit + 1, offset)).fetchall()
            has_more = len(rows) > limit
            items_rows = rows[:limit]
            items = [{
                'decision_id': r['decision_id'],
                'run_id': run_id,
                'origin': r['origin'],
                'history_before': r['history_before'],
                'policy_id': r['policy_id'],
                'available_cash_cents': r['available_cash_cents'],
                'proposed_sweep_cents': r['proposed_sweep_cents'],
                'result': r['result'],
                'reason_codes': json.loads(r['reason_codes_json']),
                'effective_family': r['effective_family'],
                'quality_label': r['quality_label'],
                'input_hash': r['input_hash'],
            } for r in items_rows]
            next_cursor = None
            if has_more:
                cursor_body = f'{run_id}.{offset + limit}'
                next_cursor = cursor_body + '.' + hmac.new(session.csrf.encode(), cursor_body.encode(), 'sha256').hexdigest()
            return result('DecisionPage', {'run_id': run_id, 'items': items, 'next_cursor': next_cursor})

    @app.get('/api/v1/runs/{run_id}/export', operation_id='exportEvidence')
    async def export_evidence(run_id: str):
        session.role('exportEvidence')
        resource_id(run_id)
        with database.read() as db:
            database.owned(db, 'runs', workspace, run_id)
            bundle = build_evidence_bundle(db, workspace, run_id)
            return result('EvidenceBundle', bundle)

    if config.frontend_origin:
        app.add_middleware(CORSMiddleware, allow_origins=[config.frontend_origin], allow_credentials=True,
                           allow_methods=['GET', 'POST'],
                           allow_headers=['Content-Type', 'X-CSRF-Token', 'Idempotency-Key', 'If-Match'],
                           expose_headers=['ETag', 'X-CSRF-Token', 'X-Request-ID', 'Retry-After'])
    return app
