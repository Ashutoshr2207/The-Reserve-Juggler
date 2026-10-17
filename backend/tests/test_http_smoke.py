"""Exercise the actual loopback socket in addition to the in-process transport."""
import socket
import threading
import time

import httpx
import uvicorn

from app.api.application import create_app
from app.api.contracts import validate
from app.api.security import Config
from conftest import csv_bytes, scenario_body
from app.api.generated_client import BackendClient


def test_actual_loopback_http_intake_review(local_root):
    listener = socket.socket()
    listener.bind(('127.0.0.1', 0))
    listener.listen(16)
    port = listener.getsockname()[1]
    origin = f'http://127.0.0.1:{port}'
    app = create_app(Config(runtime=local_root, origin=origin))
    server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=port, access_log=False,
                                         proxy_headers=False, log_level='error'))
    thread = threading.Thread(target=lambda: server.run(sockets=[listener]), daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 5
        while not server.started and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(.01)
        assert server.started
        with httpx.Client(base_url=origin, trust_env=False, timeout=5) as client:
            assert client.get('/api/v1/workspace').status_code == 401
            bootstrap = client.post('/local/bootstrap', json={'capability': app.state.session.bootstrap},
                                    headers={'Origin': origin})
            assert bootstrap.status_code == 204
            client.headers.update({'Origin': origin, 'X-CSRF-Token': bootstrap.headers['X-CSRF-Token']})
            validate('Workspace', client.get('/api/v1/workspace').json())
            imported = client.post('/api/v1/datasets', files={'file': ('fictional.csv', csv_bytes())},
                                   headers={'Idempotency-Key': 'network-import-01'})
            assert imported.status_code == 201
            dataset = validate('Dataset', imported.json())
            created = client.post('/api/v1/scenarios', json=scenario_body(dataset['dataset_id']),
                                  headers={'Idempotency-Key': 'network-scenario-01'})
            assert created.status_code == 201
            value = validate('Scenario', created.json())
            reviewed = client.post('/api/v1/scenarios/' + value['scenario_id'] + '/review',
                                   json={'actor_label': 'Local reviewer', 'acknowledge_fictional_assumptions': True},
                                   headers={'Idempotency-Key': 'network-review-01', 'If-Match': created.headers['ETag']})
            assert reviewed.status_code == 200
            assert validate('Scenario', reviewed.json())['status'] == 'REVIEWED'
            # All public operations pass through a generated contract client over TCP.
            api = BackendClient(client)
            assert api.get_workspace().status_code == 200
            assert api.import_dataset(files={'file': ('fictional.csv', csv_bytes())},
                                      headers={'Idempotency-Key': 'generated-import'}).status_code == 201
            assert api.get_dataset(path={'dataset_id': dataset['dataset_id']}).status_code == 200
            draft = api.create_scenario(body=scenario_body(dataset['dataset_id']),
                                        headers={'Idempotency-Key': 'generated-scenario'}).json()
            assert api.get_scenario(path={'scenario_id': draft['scenario_id']}).status_code == 200
            assert api.review_scenario(path={'scenario_id': draft['scenario_id']},
                        body={'actor_label': 'Generated client', 'acknowledge_fictional_assumptions': True},
                        headers={'Idempotency-Key': 'generated-review', 'If-Match': draft['fingerprint']}).status_code == 200
            accepted = api.create_run(body={'scenario_id': draft['scenario_id'],
                        'policy_ids': ['cash_only', 'fixed_repo'], 'forecast_mode': 'experimental',
                        'adapter_artifact_id': None}, headers={'Idempotency-Key': 'generated-run'}).json()
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                finished = api.get_run(path={'run_id': accepted['run_id']}).json()
                if finished['status'] in ('COMPLETED', 'FAILED', 'CANCELLED', 'INTERRUPTED'):
                    break
                time.sleep(.01)
            assert finished['status'] == 'COMPLETED'
            assert any('fallback' in w for w in finished['warnings'])
            assert api.get_metrics(path={'run_id': accepted['run_id']}).status_code == 200
            assert api.get_decisions(path={'run_id': accepted['run_id']}, query={'limit': 1}).status_code == 200
            assert api.export_evidence(path={'run_id': accepted['run_id']}).status_code == 200
            assert api.cancel_run(path={'run_id': accepted['run_id']},
                                  headers={'Idempotency-Key': 'generated-cancel'}).json()['status'] == 'COMPLETED'
    finally:
        server.should_exit = True
        thread.join(5)
        listener.close()
        assert not thread.is_alive()
