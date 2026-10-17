"""Simulation service coordinating domain ledger execution and SQLite persistence."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from app.api.contracts import canonical, validate
from app.domain.adapter import ForecastGateway
from app.domain.ledger import parse_csv_rows, simulate_policy
from app.services.comparison import compare_policies
from app.storage.database import Database, generated

ENGINE_VERSION = 'rg02-ledger-1.1.0'


class RunStopped(Exception):
    pass


def require_complete(row):
    from app.api.contracts import Problem
    if row['status'] != 'COMPLETED':
        raise Problem(409, 'RUN_NOT_COMPLETE', 'Complete results are unavailable for this run.')


def execute_simulation(database, workspace_id: str, run_id: str,
                       scenario_row: dict, dataset_row: dict,
                       source_path: Path, policy_ids: list[str],
                       forecast_mode: str, adapter_artifact_id: str | None, stop=None) -> dict:
    """Run deterministic multi-policy simulation and commit all evidence atomically."""
    scenario_body = json.loads(scenario_row['body_json'])
    settings = scenario_body['settings']
    fingerprint = scenario_row['fingerprint']
    dataset_sha256 = dataset_row['sha256']
    
    source_bytes = source_path.read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != dataset_sha256:
        raise RuntimeError('Stored source integrity failure')
    source_text = source_bytes.decode('utf-8-sig')
    rows = parse_csv_rows(source_text)
    total_hours = len(rows)

    gateway = ForecastGateway()
    all_metrics = []
    all_reports = {}
    all_decisions = []
    all_events = []
    all_lots = []
    has_shortfalls = False

    for policy_index, pid in enumerate(policy_ids):
        saved_events = 0
        saved_decisions = 0

        def checkpoint(hour, decisions, events, lots):
            nonlocal saved_events, saved_decisions
            if stop and stop.is_set():
                raise RunStopped()
            with database.read() as connection:
                current = database.owned(connection, 'runs', workspace_id, run_id)
                if current['status'] != 'RUNNING' or current['cancel_requested']:
                    raise RunStopped()
            if hour % 24 and hour != total_hours:
                return
            with database.transaction() as connection:
                current = database.owned(connection, 'runs', workspace_id, run_id)
                if current['status'] != 'RUNNING' or current['cancel_requested']:
                    raise RunStopped()
                for evt in events[saved_events:]:
                    seq = (evt['sequence'] - 1) * len(policy_ids) + policy_index + 1
                    connection.execute('INSERT INTO ledger_events VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                        (workspace_id, run_id, seq, pid, evt['origin'], evt['event_type'],
                         evt['amount_cents'], evt['balance_cents'], evt['debt_cents'],
                         evt['unpaid_cents'], evt['details_json']))
                for dec in decisions[saved_decisions:]:
                    validate('Decision', dec, output=True)
                    connection.execute('INSERT INTO decisions VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (workspace_id, run_id, dec['decision_id'], len(decisions), dec['origin'],
                         dec['history_before'], pid, dec['available_cash_cents'], dec['proposed_sweep_cents'],
                         dec['result'], canonical(dec['reason_codes']), dec['effective_family'],
                         dec['quality_label'], dec['input_hash']))
                progress = hour if policy_index == len(policy_ids) - 1 else 0
                connection.execute('UPDATE runs SET completed_hours=?,updated_at=? WHERE workspace_id=? AND id=?',
                    (progress, datetime.now(timezone.utc).isoformat(), workspace_id, run_id))
            saved_events, saved_decisions = len(events), len(decisions)

        result = simulate_policy(
            policy_id=pid,
            dataset_rows=rows,
            settings=settings,
            forecast_mode=forecast_mode,
            adapter_gateway=gateway,
            run_id=run_id,
            dataset_hash=dataset_sha256,
            checkpoint=checkpoint, artifact_id=adapter_artifact_id,
        )
        m = result['metrics']
        validate('Metric', m, output=True)
        all_metrics.append(m)
        all_reports[pid] = result['diagnostics']
        all_decisions.extend(result['decisions'])
        all_events.extend(result['ledger_events'])
        for lot in result['repo_lots']:
            lot_copy = dict(lot)
            lot_copy['lot_id'] = f"{pid}_{lot['lot_id']}"
            all_lots.append(lot_copy)

        if int(m['unpaid_new_cents']) > 0 or m['shortfall_hours'] > 0:
            has_shortfalls = True

    # Assign strictly unique sequential ordering across the run
    for seq_num, evt in enumerate(all_events, start=1):
        evt['sequence'] = seq_num

    financial_outcome = 'SHORTFALLS' if has_shortfalls else 'NO_SHORTFALLS'
    now_iso = datetime.now(timezone.utc).isoformat()

    run_record = {
        'run_id': run_id,
        'scenario_id': scenario_row['id'],
        'scenario_fingerprint': fingerprint,
        'contract_version': '0.1.0',
        'status': 'COMPLETED',
        'financial_outcome': financial_outcome,
        'completed_hours': total_hours,
        'total_hours': total_hours,
        'warnings': ['Computed synthetic simulation; no external reserve verification.',
                     'Conventional fixed-rule policy; forecasts do not authorize investments.',
                     *(['Experimental adapter unavailable; conventional fixed-rule fallback.']
                       if forecast_mode == 'experimental' else []),
                     *(['Forecast disabled; conventional fixed-rule fallback.']
                       if forecast_mode == 'disabled' else [])],
    }
    validate('Run', run_record, output=True)

    metric_set = {
        'run_id': run_id,
        'scenario_fingerprint': fingerprint,
        'metric_definition_version': '1.0',
        'quality_label': 'computed_simulation',
        'metrics': all_metrics,
        'warnings': run_record['warnings'],
    }
    validate('MetricSet', metric_set, output=True)

    # Checkpoint evidence remains incomplete until final metrics and COMPLETED commit.
    with database.transaction() as db:
        current = database.owned(db, 'runs', workspace_id, run_id)
        if current['status'] != 'RUNNING' or current['cancel_requested'] or (stop and stop.is_set()):
            raise RunStopped()
        for m in all_metrics:
            db.execute('''
                INSERT INTO metrics(workspace_id, run_id, policy_id, treasury_result_cents,
                                    unpaid_new_cents, shortfall_hours, peak_debt_cents,
                                    terminal_wealth_cents, total_cost_cents)
                VALUES(?,?,?,?,?,?,?,?,?)
            ''', (workspace_id, run_id, m['policy_id'], m['treasury_result_cents'],
                  m['unpaid_new_cents'], m['shortfall_hours'], m['peak_debt_cents'],
                  m['terminal_wealth_cents'], m['total_cost_cents']))

        for pid, report in all_reports.items():
            db.execute('INSERT INTO run_reports VALUES(?,?,?,?)',
                       (workspace_id, run_id, pid, canonical(report)))

        db.execute('''
            INSERT INTO metric_sets(workspace_id, run_id, scenario_fingerprint,
                                    metric_definition_version, quality_label, warnings_json)
            VALUES(?,?,?,?,?,?)
        ''', (workspace_id, run_id, fingerprint, '1.0', 'computed_simulation', canonical(metric_set['warnings'])))

        for lot in all_lots:
            db.execute('''
                INSERT INTO repo_lots(workspace_id, run_id, lot_id, policy_id,
                                      principal_cents, rate_apy, entry_time,
                                      maturity_time, status, accrued_interest_cents)
                VALUES(?,?,?,?,?,?,?,?,?,?)
            ''', (workspace_id, run_id, lot['lot_id'], lot['policy_id'],
                  lot['principal_cents'], lot['rate_apy'], lot['entry_time'],
                  lot['maturity_time'], lot['status'], lot['accrued_interest_cents']))

        db.execute("""UPDATE runs SET status='COMPLETED',financial_outcome=?,
                   completed_hours=total_hours,warnings_json=?,updated_at=?
                   WHERE workspace_id=? AND id=?""",
                   (financial_outcome, canonical(run_record['warnings']), now_iso, workspace_id, run_id))

    return run_record


def build_evidence_bundle(db, workspace_id: str, run_id: str) -> dict:
    """Construct hashed evidence; this does not provide a digital signature."""
    run_row = db.execute('SELECT * FROM runs WHERE workspace_id=? AND id=?', (workspace_id, run_id)).fetchone()
    if not run_row:
        raise ValueError('Run not found')
    require_complete(run_row)

    # 1. Metrics
    ms_row = db.execute('SELECT * FROM metric_sets WHERE workspace_id=? AND run_id=?', (workspace_id, run_id)).fetchone()
    metrics_rows = db.execute('SELECT * FROM metrics WHERE workspace_id=? AND run_id=? ORDER BY policy_id', (workspace_id, run_id)).fetchall()
    metrics_list = [{
        'policy_id': r['policy_id'],
        'treasury_result_cents': r['treasury_result_cents'],
        'unpaid_new_cents': r['unpaid_new_cents'],
        'shortfall_hours': r['shortfall_hours'],
        'peak_debt_cents': r['peak_debt_cents'],
        'terminal_wealth_cents': r['terminal_wealth_cents'],
        'total_cost_cents': r['total_cost_cents'],
    } for r in metrics_rows]
    metric_set = {
        'run_id': run_id,
        'scenario_fingerprint': ms_row['scenario_fingerprint'],
        'metric_definition_version': ms_row['metric_definition_version'],
        'quality_label': ms_row['quality_label'],
        'metrics': metrics_list,
        'warnings': json.loads(ms_row['warnings_json']),
    }
    metrics_content = canonical(metric_set)

    # 2. Decisions
    decision_rows = db.execute('SELECT * FROM decisions WHERE workspace_id=? AND run_id=? ORDER BY origin, policy_id',
                               (workspace_id, run_id)).fetchall()
    decisions_list = [{
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
    } for r in decision_rows]
    decisions_content = canonical(decisions_list)

    # 3. Ledger Events
    event_rows = db.execute('SELECT * FROM ledger_events WHERE workspace_id=? AND run_id=? ORDER BY sequence',
                            (workspace_id, run_id)).fetchall()
    events_list = [{
        'sequence': r['sequence'],
        'policy_id': r['policy_id'],
        'origin': r['origin'],
        'event_type': r['event_type'],
        'amount_cents': r['amount_cents'],
        'balance_cents': r['balance_cents'],
        'debt_cents': r['debt_cents'],
        'unpaid_cents': r['unpaid_cents'],
        'details': json.loads(r['details_json']),
    } for r in event_rows]
    events_content = canonical(events_list)

    # 4. Comparison (FR-08, AC-05, AC-06)
    scenario_row = db.execute('SELECT body_json FROM scenarios WHERE workspace_id=? AND id=?',
                              (workspace_id, run_row['scenario_id'])).fetchone()
    scenario_settings = json.loads(scenario_row['body_json'])['settings'] if scenario_row else {}
    comparison_data = compare_policies(dict(run_row), metrics_list, scenario_settings)
    comparison_content = canonical(comparison_data)

    # Replay inputs and provenance exclude raw CSV and unrelated local configuration.
    scenario = json.loads(db.execute('SELECT body_json FROM scenarios WHERE workspace_id=? AND id=?',
                                   (workspace_id, run_row['scenario_id'])).fetchone()[0])
    scenario['status'] = 'REVIEWED'
    review_row = db.execute('SELECT fingerprint,actor_label,mode,reviewed_at FROM reviews WHERE workspace_id=? AND scenario_id=?',
                            (workspace_id, run_row['scenario_id'])).fetchone()
    extra = {
        'accounting.json': canonical({r['policy_id']: json.loads(r['body_json']) for r in db.execute(
            'SELECT policy_id,body_json FROM run_reports WHERE workspace_id=? AND run_id=? ORDER BY policy_id',
            (workspace_id, run_id))}),
        'scenario.json': canonical(scenario),
        'dataset_profile.json': db.execute('SELECT profile_json FROM datasets WHERE workspace_id=? AND id=?',
                                          (workspace_id, scenario['dataset_id'])).fetchone()[0],
        'review.json': canonical(dict(review_row)),
        'provenance.json': run_row['provenance_json'],
        'repo_lots.json': canonical([dict(r) for r in db.execute(
            'SELECT lot_id,policy_id,principal_cents,rate_apy,entry_time,maturity_time,status,accrued_interest_cents '
            'FROM repo_lots WHERE workspace_id=? AND run_id=? ORDER BY lot_id', (workspace_id, run_id))]),
    }
    # 5. Manifest
    members_manifest = {
        'metrics.json': hashlib.sha256(metrics_content.encode()).hexdigest(),
        'decisions.json': hashlib.sha256(decisions_content.encode()).hexdigest(),
        'ledger_events.json': hashlib.sha256(events_content.encode()).hexdigest(),
        'comparison.json': hashlib.sha256(comparison_content.encode()).hexdigest(),
    }
    members_manifest.update({name: hashlib.sha256(content.encode()).hexdigest() for name, content in extra.items()})
    manifest_doc = {
        'run_id': run_id,
        'scenario_id': run_row['scenario_id'],
        'scenario_fingerprint': run_row['scenario_fingerprint'],
        'contract_version': run_row['contract_version'],
        'status': run_row['status'],
        'engine_version': run_row['engine_version'],
        'run_fingerprint': run_row['run_fingerprint'],
        'integrity': 'sha256_member_digests_unsigned',
        'limitations': 'Synthetic internal replay only; source rights unresolved. No solvency, compliance or production claim.',
        'financial_outcome': run_row['financial_outcome'],
        'completed_hours': run_row['completed_hours'],
        'total_hours': run_row['total_hours'],
        'created_at': run_row['created_at'],
        'members_sha256': members_manifest,
    }
    manifest_content = canonical(manifest_doc)

    members = [
        {'name': 'manifest.json', 'sha256': hashlib.sha256(manifest_content.encode()).hexdigest(), 'content': manifest_content},
        {'name': 'metrics.json', 'sha256': members_manifest['metrics.json'], 'content': metrics_content},
        {'name': 'decisions.json', 'sha256': members_manifest['decisions.json'], 'content': decisions_content},
        {'name': 'ledger_events.json', 'sha256': members_manifest['ledger_events.json'], 'content': events_content},
        {'name': 'comparison.json', 'sha256': members_manifest['comparison.json'], 'content': comparison_content},
    ]

    members.extend({'name': name, 'sha256': members_manifest[name], 'content': content}
                   for name, content in sorted(extra.items()))
    bundle = {
        'run_id': run_id,
        'contract_version': '0.1.0',
        'members': members,
        'warnings': json.loads(run_row['warnings_json']),
    }
    validate('EvidenceBundle', bundle, output=True)
    return bundle
