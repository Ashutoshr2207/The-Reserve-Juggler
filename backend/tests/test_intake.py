import hashlib

import pytest

from app.api.contracts import validate
from app.domain.intake import MAX_INT, MAX_UPLOAD, profile
from conftest import csv_bytes, upload


def test_import_profile_preserves_exact_bytes_and_deduplicates(live):
    client, app = live
    raw = csv_bytes()
    response = upload(client, raw)
    assert response.status_code == 201, response.text
    value = validate('Dataset', response.json())
    assert value['rows'] == 24 and value['columns'] == 16
    assert value['start'] == '2026-01-01 00:00:00'
    assert value['end'] == '2026-01-01 23:00:00'
    assert value['sha256'] == hashlib.sha256(raw).hexdigest()
    source = app.state.database.root / app.state.workspace / 'raw' / (value['sha256'] + '.csv')
    assert source.read_bytes() == raw
    for key in ('import-key-01', 'distinct-key-01'):
        duplicate = upload(client, raw, key)
        assert duplicate.status_code == 201
        assert duplicate.json() == value
    assert client.get('/api/v1/datasets/' + value['dataset_id']).json() == value
    assert list((app.state.database.root / 'tmp').iterdir()) == []


@pytest.mark.parametrize(('field', 'value', 'code'), [
    ('timestamp', '2026-02-30 00:00:00', 'INVALID_CSV'),
    ('timestamp', '2026-01-01 00:30:00', 'INVALID_CSV'),
    ('timestamp', '2026-01-01T00:00:00Z', 'INVALID_CSV'),
    ('deposits_usd', 'NaN', 'INVALID_CSV'),
    ('deposits_usd', 'Infinity', 'INVALID_CSV'),
    ('deposits_usd', '1e100000', 'INVALID_CSV'),
    ('deposits_usd', '-1', 'INVALID_CSV'),
    ('deposits_usd', 'true', 'INVALID_CSV'),
    ('deposits_usd', '1.001', 'INVALID_CSV'),
    ('deposits_usd', str(MAX_INT // 100 + 1), 'AMOUNT_OUT_OF_RANGE'),
    ('deposits_usd', '', 'INVALID_CSV'),
    ('net_flow_usd', '10.07', 'INVALID_CSV'),
    ('repo_sweep_window_open', 'false', 'INVALID_CSV'),
    ('repo_sweep_window_open', '0', 'INVALID_CSV'),
    ('repo_sweep_mature', 'True', 'INVALID_CSV'),
    ('tier2_bond_price_index', '0', 'INVALID_CSV'),
    ('tier3_stock_index_price', '=HYPERLINK()', 'INVALID_CSV'),
    ('tier2_bond_liquidation_haircut_pct', '101', 'INVALID_CSV'),
])
def test_invalid_row_rejected_without_side_effects(live, field, value, code):
    client, app = live
    response = upload(client, csv_bytes(change=lambda rows: rows[0].update({field: value})))
    assert response.status_code == 422, response.text
    error = validate('Error', response.json())
    assert error['code'] == code
    assert error['details'][0]['field'] == field
    assert error['details'][0]['row'] == 2
    with app.state.database.read() as db:
        assert db.execute('SELECT count(*) FROM datasets').fetchone()[0] == 0
        assert db.execute('SELECT count(*) FROM idempotency').fetchone()[0] == 0
    assert list((app.state.database.root / 'tmp').iterdir()) == []


@pytest.mark.parametrize('mode', ['gap', 'duplicate', 'reverse'])
def test_hour_sequence(live, mode):
    client, _ = live
    def change(rows):
        if mode == 'gap':
            rows[1]['timestamp'] = '2026-01-01 03:00:00'
        elif mode == 'duplicate':
            rows[1]['timestamp'] = rows[0]['timestamp']
        else:
            rows.reverse()
    response = upload(client, csv_bytes(change=change))
    assert response.status_code == 422
    assert response.json()['details'][0]['field'] == 'timestamp'


def test_net_residual_exact_one_cent_and_signed_values(live):
    client, _ = live
    raw = csv_bytes(change=lambda rows: rows[0].update(withdrawals_usd='110.10', net_flow_usd='-9.99'))
    response = upload(client, raw)
    assert response.status_code == 201
    assert any('1 rows' in warning for warning in response.json()['warnings'])


@pytest.mark.parametrize('name', ['../bad.csv', 'C:\\bad.csv', 'https://test.csv', 'bad.zip', '.hidden.csv'])
def test_no_path_or_archive_import(live, name):
    response = upload(live[0], filename=name)
    assert response.status_code == 422
    assert name not in response.text


@pytest.mark.parametrize('data', [b'\xff\xfeinvalid', b'\x00', b'', b'col\n1\n', b'abc' * (MAX_UPLOAD // 3 + 1)],
                         ids=['encoding', 'nul', 'empty', 'schema', 'oversize'])
def test_encoding_schema_and_size(live, data):
    client, _ = live
    response = client.post('/api/v1/datasets', files={'file': ('fixture.csv', data, 'text/csv')},
                           headers={'Idempotency-Key': 'import-key-01'})
    assert response.status_code == 422


def test_multiple_parts_and_truncated_multipart(live):
    client, app = live
    response = client.post('/api/v1/datasets', files=[('file', ('a.csv', csv_bytes())), ('file', ('b.csv', csv_bytes()))],
                           headers={'Idempotency-Key': 'import-key-01'})
    assert response.status_code == 422
    response = client.post('/api/v1/datasets', content=b'--test\r\nContent-Disposition: form-data; name="file"; filename="a.csv"\r\n\r\na',
                           headers={'Content-Type': 'multipart/form-data; boundary=test', 'Idempotency-Key': 'import-key-01'})
    assert response.status_code == 422
    assert list((app.state.database.root / 'tmp').iterdir()) == []


def test_wrong_import_body_is_typed(live):
    response = live[0].post('/api/v1/datasets', json={'path': '../secret.csv'},
                            headers={'Idempotency-Key': 'import-key-01'})
    assert response.status_code == 422
    validate('Error', response.json())


def test_duplicate_and_missing_columns(live):
    raw = csv_bytes()
    for bad in (raw.replace(b'deposits_usd', b'withdrawals_usd', 1), raw.replace(b'deposits_usd,', b'', 1)):
        assert upload(live[0], bad).status_code == 422
