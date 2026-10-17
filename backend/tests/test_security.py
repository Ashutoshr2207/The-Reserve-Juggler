import json

import pytest

from app.api.contracts import validate
from conftest import client_for, review, scenario, scenario_body, upload


def test_session_bootstrap_single_use_cookie_and_logout(local_root):
    with client_for(local_root, login=False) as (client, app):
        capability = app.state.session.bootstrap
        assert client.get('/api/v1/workspace').status_code == 401
        assert client.post('/local/bootstrap', json={'capability': 'invalid'},
                           headers={'Origin': 'http://127.0.0.1:8000'}).status_code == 401
        assert client.post('/local/bootstrap', json={'capability': capability},
                           headers={'Origin': 'http://evil.invalid'}).status_code == 403
        response = client.post('/local/bootstrap', json={'capability': capability},
                               headers={'Origin': 'http://127.0.0.1:8000'})
        assert response.status_code == 204
        assert 'HttpOnly' in response.headers['set-cookie'] and 'SameSite=strict' in response.headers['set-cookie']
        assert capability not in response.text
        assert client.post('/local/bootstrap', json={'capability': capability},
                           headers={'Origin': 'http://127.0.0.1:8000'}).status_code == 401
        assert client.get('/api/v1/workspace').status_code == 200
        csrf = client.get('/local/csrf').headers['X-CSRF-Token']
        assert client.post('/local/logout', headers={'Origin': 'http://127.0.0.1:8000', 'X-CSRF-Token': csrf}).status_code == 204
        assert client.get('/api/v1/workspace').status_code == 401
        assert app.state.session.token is None


def test_idle_expiry_and_restart_invalidate_tokens(local_root):
    with client_for(local_root) as (client, app):
        old_cookie = client.cookies.get('rg_session')
        app.state.session.last_used -= 8 * 3600
        assert client.get('/api/v1/workspace').status_code == 401
    with client_for(local_root, login=False) as (client, app):
        client.cookies.set('rg_session', old_cookie)
        assert client.get('/api/v1/workspace').status_code == 401


@pytest.mark.parametrize('headers', [
    {'Origin': 'http://evil.invalid'}, {'Origin': 'null'}, {'Origin': ''},
    {'X-CSRF-Token': ''}, {'X-CSRF-Token': 'forged'},
    {'Host': 'evil.invalid'}, {'Host': '127.0.0.1:9999'}, {'Sec-Fetch-Site': 'cross-site'},
])
def test_origin_host_csrf_denials(live, headers):
    response = upload_with(live[0], headers)
    assert response.status_code == 403
    validate('Error', response.json())


def upload_with(client, headers):
    from conftest import csv_bytes
    return client.post('/api/v1/datasets', files={'file': ('fictional.csv', csv_bytes())},
                       headers={'Idempotency-Key': 'import-key-01', **headers})


@pytest.mark.parametrize('role', ['operator', 'maker', 'reviewer', 'auditor'])
def test_role_matrix_and_forged_headers(local_root, role):
    with client_for(local_root) as (creator, _):
        value = scenario(creator).json()
    with client_for(local_root, role) as (client, app):
        assert client.get('/api/v1/workspace').json()['role_mode'] == role
        assert client.get('/api/v1/scenarios/' + value['scenario_id']).status_code == 200
        assert client.get('/api/v1/datasets/' + value['dataset_id']).status_code == 200
        client.headers.update({'X-Role': 'operator', 'X-Workspace-ID': 'ws_forged'})
        expected_import = 201 if role in ('operator', 'maker') else 403
        assert upload(client).status_code == expected_import
        assert scenario(client, value['dataset_id']).status_code == expected_import
        assert review(client, value).status_code == (200 if role in ('operator', 'reviewer') else 403)
        if role == 'reviewer':
            with app.state.database.read() as db:
                assert db.execute('SELECT mode FROM reviews').fetchone()[0] == 'local_reviewer'


def test_foreign_resource_ids_hidden_and_body_cannot_select_workspace(live):
    client, app = live
    db = app.state.database
    owned = scenario(client).json()
    with db.transaction() as connection:
        connection.execute('INSERT INTO workspaces VALUES(?)', ('ws_foreign',))
        row = connection.execute('SELECT * FROM datasets').fetchone()
        connection.execute('INSERT INTO datasets VALUES(?,?,?,?,?)',
                           ('ws_foreign', 'ds_foreign', row['sha256'], row['source_name'], row['profile_json']))
        connection.execute('INSERT INTO scenarios VALUES(?,?,?,?,?,?)',
                           ('ws_foreign', 'sc_foreign', 'ds_foreign', owned['fingerprint'], json.dumps(owned), 'DRAFT'))
    for identity in ['ds_foreign', 'ds_missing']:
        response = client.get('/api/v1/datasets/' + identity)
        assert response.status_code == 404 and response.json()['message'] == 'Resource was not found.'
        assert scenario(client, identity, key='foreign-key-01').status_code == 404
    for identity in ['sc_foreign', 'sc_missing']:
        assert client.get('/api/v1/scenarios/' + identity).status_code == 404
        assert review(client, {**owned, 'scenario_id': identity}).status_code == 404


def test_denied_request_does_not_parse_or_reserve_idempotency(local_root):
    with client_for(local_root, 'auditor') as (client, app):
        response = client.post('/api/v1/datasets', content=b'invalid malformed body',
                               headers={'Content-Type': 'multipart/form-data', 'Idempotency-Key': 'import-key-01'})
        assert response.status_code == 403
        with app.state.database.read() as db:
            assert db.execute('SELECT count(*) FROM idempotency').fetchone()[0] == 0


def test_unknown_operations_and_no_financial_endpoints(live):
    client, _ = live
    for method, url in [('post', '/api/v1/trades'), ('get', '/openapi.json'),
                        ('delete', '/api/v1/scenarios/sc_missing')]:
        response = getattr(client, method)(url)
        assert response.status_code == 404
        validate('Error', response.json())


def test_dev_cors_exact_origin(local_root):
    with client_for(local_root, frontend_origin='http://localhost:5173') as (client, _):
        response = client.options('/api/v1/scenarios', headers={'Origin': 'http://localhost:5173',
                                   'Access-Control-Request-Method': 'POST',
                                   'Access-Control-Request-Headers': 'X-CSRF-Token,Idempotency-Key'})
        assert response.status_code == 200
        assert response.headers['access-control-allow-origin'] == 'http://localhost:5173'
        response = client.options('/api/v1/scenarios', headers={'Origin': 'http://evil.invalid',
                                   'Access-Control-Request-Method': 'POST'})
        assert 'access-control-allow-origin' not in response.headers


def test_config_fails_closed_for_remote_or_invalid_mode(local_root):
    from app.api.security import Config
    for values in [{'role': 'admin'}, {'origin': 'http://0.0.0.0:8000'},
                   {'frontend_origin': '*'}, {'frontend_origin': 'http://localhost:5173/path'}]:
        with pytest.raises(ValueError):
            Config(runtime=local_root, **values)
