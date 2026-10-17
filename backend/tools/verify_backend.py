"""Reproducible BE-05 tests and repeated local year-volume benchmark.

Generated workload is a synthetic surrogate, never relabeled as the absent D07.
Run from backend with the locked Python environment; outputs stay in outputs/.
"""
import argparse
import csv
import hashlib
import importlib.metadata
import io
import json
import os
import platform
import shutil
import sqlite3
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.api.application import create_app
from app.api.contracts import canonical
from app.api.generated_client import BackendClient
from app.api.security import Config
from app.domain.adapter import ForecastGateway
from app.domain.intake import COLUMNS
from fastapi.testclient import TestClient
from verify_export import verify


def fictional_csv(count=8760):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=COLUMNS)
    writer.writeheader()
    for index in range(count):
        stamp = datetime(2026, 1, 1) + timedelta(hours=index)
        row = dict.fromkeys(COLUMNS, '0')
        row.update(timestamp=stamp.strftime('%Y-%m-%d %H:%M:%S'), deposits_usd='1000.00',
                   withdrawals_usd='900.00', net_flow_usd='100.00',
                   repo_sweep_window_open=str(stamp.hour == 17), repo_sweep_mature=str(stamp.hour == 8),
                   tier1_repo_rate_apy='4.0', tier2_bond_price_index='100', tier3_stock_index_price='5000',
                   emergency_overdraft_penalty_apr_pct='10', tier1_early_redemption_haircut_pct='1')
        writer.writerow(row)
    return stream.getvalue().encode()


def benchmark(repeats, dataset=None):
    source = dataset.read_bytes() if dataset else fictional_csv()
    digest = hashlib.sha256(source).hexdigest()
    is_d07 = digest == '2e7c1d2e5b678e9975250211e7e0017022049c510e1dd90cd7f29e931837b0c5'
    runtime = ROOT / 'work' / ('bench_' + uuid.uuid4().hex[:6])
    timings, results = [], []
    app = create_app(Config(runtime=runtime))
    try:
        with TestClient(app, base_url='http://127.0.0.1:8000', client=('127.0.0.1', 50000)) as http:
            bootstrap = http.post('/local/bootstrap', json={'capability': app.state.session.bootstrap},
                                  headers={'Origin': 'http://127.0.0.1:8000'})
            assert bootstrap.status_code == 204
            http.headers.update({'Origin': 'http://127.0.0.1:8000', 'X-CSRF-Token': bootstrap.headers['X-CSRF-Token']})
            api = BackendClient(http)
            imported = api.import_dataset(files={'file': ('fictional.csv', source)},
                                           headers={'Idempotency-Key': 'benchmark-import'} )
            assert imported.status_code == 201, imported.text
            dataset_profile = imported.json()
            fixture = json.loads((ROOT / 'contracts/examples/first_slice.json').read_text())
            body = next(case['value'] for case in fixture['http_cases'] if case['schema'] == 'ScenarioCreate')
            body['dataset_id'] = dataset_profile['dataset_id']
            body['label'] = 'Acknowledged fictional performance scenario'
            body['settings'].update(opening_cash_cents='300000000000', reserve_floor_cents='100000000',
                                    credit_limit_cents='0', transaction_fee_cents='100', stress_ids=['none'],
                                    early_repo_release=False, fictional_acknowledged=True)
            created = api.create_scenario(body=body, headers={'Idempotency-Key': 'benchmark-scenario'})
            assert created.status_code == 201, created.text
            scenario = created.json()
            reviewed = api.review_scenario(path={'scenario_id': scenario['scenario_id']},
                            body={'actor_label': 'Local performance verification', 'acknowledge_fictional_assumptions': True},
                            headers={'Idempotency-Key': 'benchmark-review', 'If-Match': scenario['fingerprint']})
            assert reviewed.status_code == 200
            for index in range(repeats):
                start = time.perf_counter()
                accepted = api.create_run(body={'scenario_id': scenario['scenario_id'],
                            'policy_ids': ['cash_only', 'fixed_repo'], 'forecast_mode': 'baseline',
                            'adapter_artifact_id': None}, headers={'Idempotency-Key': f'benchmark-run-{index}'})
                assert accepted.status_code == 202, accepted.text
                rid = accepted.json()['run_id']
                while time.perf_counter() - start < 120:
                    run = api.get_run(path={'run_id': rid}).json()
                    if run['status'] in ('COMPLETED', 'FAILED', 'CANCELLED', 'INTERRUPTED'):
                        break
                    time.sleep(.05)
                elapsed = time.perf_counter() - start
                assert run['status'] == 'COMPLETED', run
                timings.append(round(elapsed, 4))
                metric_set = api.get_metrics(path={'run_id': rid}).json()
                results.append(metric_set['metrics'])
                if index == 0:
                    bundle = api.export_evidence(path={'run_id': rid}).json()
                    verify(bundle)
                    (ROOT / 'outputs/BE-05-example-export.json').write_text(canonical(bundle), encoding='utf-8')
                print(f'Year-volume replay {index + 1}/{repeats}: {elapsed:.3f}s', flush=True)
            assert all(result == results[0] for result in results), 'Nondeterministic metrics'
        # Warm conventional adapter latency; no experimental/trained model exists.
        gateway = ForecastGateway()
        history = [{'timestamp': (datetime(2026, 1, 1) + timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S'),
                    'deposits_cents': '100000', 'withdrawals_cents': '90000'} for i in range(168)]
        samples = []
        for i in range(101):
            started = time.perf_counter()
            gateway.predict('baseline', digest, '2026-01-08 00:00:00', history)
            if i:
                samples.append(time.perf_counter() - started)
        return {'workload': 'D07 (hash verified)' if is_d07 else 'generated synthetic surrogate; not D07',
                'source_sha256': digest, 'rows': dataset_profile['rows'], 'columns': dataset_profile['columns'],
                'policies': ['cash_only', 'fixed_repo'], 'forecast_mode': 'baseline',
                'timing_scope': 'acceptance, queue, computation, SQLite checkpoints and completion polling; excludes export',
                'replay_seconds': timings, 'all_below_60_seconds': all(t < 60 for t in timings),
                'deterministic_metrics': True, 'warm_adapter_samples': len(samples),
                'warm_adapter_p95_seconds': round(sorted(samples)[94], 6),
                'd07_acceptance_verified': is_d07,
                'settings': body['settings'], 'metrics': results[0]}
    finally:
        if runtime.exists():
            shutil.rmtree(runtime)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--dataset', type=Path)
    args = parser.parse_args()
    if not 2 <= args.repeats <= 5:
        parser.error('Use two to five repeats')
    os.chdir(ROOT)
    output = ROOT / 'outputs'
    output.mkdir(exist_ok=True)
    started = time.perf_counter()
    completed = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
                    '--junitxml=outputs/BE-05-tests.xml', 'tests'], cwd=ROOT, capture_output=True, text=True)
    (output / 'BE-05-tests.txt').write_text(completed.stdout + completed.stderr, encoding='utf-8')
    print(completed.stdout, flush=True)
    if completed.returncode:
        raise SystemExit(completed.returncode)
    suite = ET.parse(output / 'BE-05-tests.xml').getroot()
    tests = sum(int(s.attrib['tests']) for s in suite.iter('testsuite'))
    benchmark_result = benchmark(args.repeats, args.dataset)
    versions = {line.split('==')[0]: importlib.metadata.version(line.split('==')[0])
                for line in (ROOT / 'requirements.lock').read_text().splitlines() if '==' in line}
    report = {'date': '2026-10-18', 'timezone': 'Asia/Calcutta', 'tests': tests, 'failed': 0,
              'environment': {'python': sys.version, 'sqlite': sqlite3.sqlite_version,
                              'os': platform.platform(), 'cpu': platform.processor(), 'logical_cpus': os.cpu_count(),
                              'packages': versions}, 'benchmark': benchmark_result,
              'checks': ['12 generated-client operations over real loopback HTTP',
                         'schema standards and 37 shared hashes', 'bounded worker queue and cancellation',
                         'startup interruption and failure rollback', 'offline backup and restore',
                         'financial regression answer keys and unsigned export verification'],
              'limitations': ['Frontend browser/accessibility and affected peer review pending',
                              'D07 acceptance pending unless benchmark explicitly verifies its hash',
                              'No trained model, production release or live integration'],
              'elapsed_seconds': round(time.perf_counter() - started, 3)}
    report['source_sha256'] = {str(path.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(path.read_bytes()).hexdigest()
           for folder in ['app', 'tests', 'migrations', 'tools'] for path in (ROOT / folder).rglob('*')
           if path.is_file() and path.suffix in ('.py', '.sql')}
    (output / 'BE-05-VERIFICATION.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'tests': tests, 'replay_seconds': benchmark_result['replay_seconds'],
                      'report': 'outputs/BE-05-VERIFICATION.json'}, indent=2))


if __name__ == '__main__':
    main()
