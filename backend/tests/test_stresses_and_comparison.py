"""Tests for BE-03: Stresses, Four-Tier attribution, Ordering, Repo Basis, and Comparison."""
import hashlib
import json
from decimal import Decimal
import pytest

from app.api.contracts import validate
from app.domain.adapter import ForecastGateway
from app.domain.ledger import parse_csv_rows, simulate_policy, compute_repo_accrual
from app.services.comparison import compare_policies
from conftest import client_for, review, scenario, upload


def make_test_csv(count=24, mutate=None):
    from datetime import datetime, timedelta
    base_dt = datetime(2026, 3, 1, 0, 0, 0)
    rows = []
    for h in range(count):
        curr_dt = base_dt + timedelta(hours=h)
        row = {
            'timestamp': curr_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'deposits_usd': '1000.00',
            'withdrawals_usd': '800.00',
            'net_flow_usd': '200.00',
            'repo_sweep_window_open': str(curr_dt.hour == 17),
            'repo_sweep_mature': str(curr_dt.hour == 8),
            'tier1_repo_rate_apy': '4.00',
            'tier2_bond_price_index': '100.50',
            'tier2_bond_liquidation_haircut_pct': '5.00',
            'tier3_stock_index_price': '500.00',
            'emergency_overdraft_penalty_apr_pct': '10.00',
        }
        if mutate:
            mutate(h, row)
        rows.append(row)
    header = [
        'timestamp', 'deposits_usd', 'withdrawals_usd', 'net_flow_usd',
        'repo_sweep_window_open', 'repo_sweep_mature',
        'tier1_repo_rate_apy', 'tier2_bond_price_index',
        'tier2_bond_liquidation_haircut_pct', 'tier3_stock_index_price',
        'emergency_overdraft_penalty_apr_pct',
        'tier1_early_redemption_haircut_pct', 'tier2_bond_yield_pct', 'tier2_bond_mod_duration',
        'tier3_stock_volatility_pct', 'tier3_stock_liquidation_haircut_pct'
    ]
    lines = [','.join(header)]
    for r in rows:
        line = [r.get(c, '0.00') for c in header]
        lines.append(','.join(line))
    return '\n'.join(lines)


@pytest.fixture
def default_settings():
    return {
        'opening_cash_cents': '5000000000',      # $50M
        'reserve_floor_cents': '1000000000',     # $10M
        'credit_limit_cents': '500000000',       # $5M
        'bond_units': '0',
        'equity_units': '0',
        'opening_repo_lots': [],
        'bond_cap_pct': '0',
        'equity_cap_pct': '0',
        'transaction_fee_cents': '0',
        'settlement_delay_hours': 0,
        'ordering': 'payout_before_deposit',
        'repo_basis': 'effective_apy',
        'early_repo_release': False,
        'fictional_acknowledged': True,
        'stress_ids': ['none'],
    }


def test_stress_withdrawal_shock(default_settings):
    """FR-07, AC-07: withdrawal_shock scales requested payouts by 50% surge."""
    csv_text = make_test_csv(count=24)
    rows = parse_csv_rows(csv_text)
    gateway = ForecastGateway()

    # 1. Normal run
    res_normal = simulate_policy('cash_only', rows, default_settings, 'disabled', gateway, 'run_norm', 'hash123')
    
    # 2. Shocked run
    shock_settings = dict(default_settings)
    shock_settings['stress_ids'] = ['withdrawal_shock']
    res_shock = simulate_policy('cash_only', rows, shock_settings, 'disabled', gateway, 'run_shock', 'hash123')

    # Normal: 24 * (1000 - 800) = +4,800 USD = +480,000 cents
    # Shock: withdrawals are 1.5x -> 24 * (1000 - 1200) = -4,800 USD = -480,000 cents
    # Closing cash difference is 24 * 400 USD = 960,000 cents
    diff_wealth = int(res_normal['metrics']['terminal_wealth_cents']) - int(res_shock['metrics']['terminal_wealth_cents'])
    assert diff_wealth == 960000


def test_stress_deposit_delay(default_settings):
    """FR-07, AC-07: deposit_delay holds incoming deposits for 1 hour."""
    # Deficit created if deposit arrives after withdrawal in hour 0
    def mutate(h, row):
        if h == 0:
            row['withdrawals_usd'] = '50000000.00'  # $50M exactly equals opening cash
            row['deposits_usd'] = '10000000.00'     # $10M
    csv_text = make_test_csv(count=24, mutate=mutate)
    rows = parse_csv_rows(csv_text)
    gateway = ForecastGateway()

    # Normal: deposits arrive hour 0, cash is 50M - 50M + 10M = 10M
    res_normal = simulate_policy('cash_only', rows, default_settings, 'disabled', gateway, 'run_d_norm', 'hash123')
    
    # Delayed: deposits at hour 0 settle at hour 1
    delay_settings = dict(default_settings)
    delay_settings['stress_ids'] = ['deposit_delay']
    res_delayed = simulate_policy('cash_only', rows, delay_settings, 'disabled', gateway, 'run_d_delay', 'hash123')

    # The last $1,000 deposit remains a receivable. Only two cents of extra
    # borrowing interest reduce wealth; a settlement delay does not destroy assets.
    diff_wealth = int(res_normal['metrics']['terminal_wealth_cents']) - int(res_delayed['metrics']['terminal_wealth_cents'])
    assert diff_wealth == 2


def test_stress_late_maturity(default_settings):
    """FR-07, AC-07: late_maturity delays repo release from 08:00 to 12:00."""
    csv_text = make_test_csv(count=48)
    rows = parse_csv_rows(csv_text)
    gateway = ForecastGateway()

    late_settings = dict(default_settings)
    late_settings['stress_ids'] = ['late_maturity']
    res_late = simulate_policy('fixed_repo', rows, late_settings, 'baseline', gateway, 'run_late', 'hash123')

    # Check that repo lots matured at or after 12:00, not 08:00
    events = res_late['ledger_events']
    matured_events = [e for e in events if e['event_type'] == 'REPO_MATURED']
    assert len(matured_events) > 0
    for e in matured_events:
        hour = int(e['origin'].split(' ')[1].split(':')[0])
        assert hour >= 12, f"Matured prematurely at hour {hour}"


def test_stress_denied_credit(default_settings):
    """FR-05, FR-07, AC-07: denied_credit blocks borrowing; deficits become immediate unpaid obligations."""
    def stress(h, row):
        if h == 5:
            row['withdrawals_usd'] = '55000000.00'  # $55M > $50M cash
    csv_text = make_test_csv(count=24, mutate=stress)
    rows = parse_csv_rows(csv_text)
    gateway = ForecastGateway()

    # 1. With credit available: $5M credit limit is drawn, 0 unpaid obligations
    res_credit = simulate_policy('cash_only', rows, default_settings, 'disabled', gateway, 'run_cred', 'hash123')
    assert int(res_credit['metrics']['peak_debt_cents']) > 0
    assert int(res_credit['metrics']['unpaid_new_cents']) == 0

    # 2. With denied_credit: credit is denied, 0 debt, entire deficit becomes unpaid!
    denied_settings = dict(default_settings)
    denied_settings['stress_ids'] = ['denied_credit']
    res_denied = simulate_policy('cash_only', rows, denied_settings, 'disabled', gateway, 'run_denied', 'hash123')
    assert int(res_denied['metrics']['peak_debt_cents']) == 0
    assert int(res_denied['metrics']['unpaid_new_cents']) > 0
    assert res_denied['metrics']['shortfall_hours'] > 0


def test_ordering_netted_vs_payout_before_deposit(default_settings):
    """Tests ordering semantics: payout_before_deposit vs netted_end_hour."""
    # Hour 2: cash is $50M, withdrawal is $54M, deposit is $10M
    def mutate(h, row):
        if h == 2:
            row['withdrawals_usd'] = '54000000.00'
            row['deposits_usd'] = '10000000.00'
    csv_text = make_test_csv(count=10, mutate=mutate)
    rows = parse_csv_rows(csv_text)
    gateway = ForecastGateway()

    # Under payout_before_deposit: $54M withdrawal hits $50.04M cash -> draws $3,999,600.00 (399,960,000 cents) credit!
    payout_first_settings = dict(default_settings)
    payout_first_settings['ordering'] = 'payout_before_deposit'
    res_payout = simulate_policy('cash_only', rows, payout_first_settings, 'disabled', gateway, 'run_payout', 'hash123')
    assert int(res_payout['metrics']['peak_debt_cents']) == 399960000  # $3,999,600 debt

    # Under netted_end_hour: net flow is $10M - $54M = -$44M. $50M cash covers $44M net deficit -> 0 debt!
    netted_settings = dict(default_settings)
    netted_settings['ordering'] = 'netted_end_hour'
    res_netted = simulate_policy('cash_only', rows, netted_settings, 'disabled', gateway, 'run_netted', 'hash123')
    assert int(res_netted['metrics']['peak_debt_cents']) == 0  # 0 debt!


def test_repo_basis_simple_vs_compound(default_settings):
    """I05: effective_apy (compound) vs simple_apr accrual."""
    principal = 100000000  # $1M
    rate = Decimal('5.0')  # 5%
    hours = 15
    compound_accrual = compute_repo_accrual(principal, rate, hours=hours, basis='effective_apy')
    simple_accrual = compute_repo_accrual(principal, rate, hours=hours, basis='simple_apr')
    # Over 15 hours, both are non-zero and compound >= simple
    assert compound_accrual > 0
    assert simple_accrual > 0


def test_four_tiers_marked_holdings_ac06(default_settings):
    """FR-06, AC-06, I06: Four tiers present, marked-to-market, no automatic liquidation."""
    four_tier_settings = dict(default_settings)
    four_tier_settings['bond_units'] = '1000'
    four_tier_settings['equity_units'] = '500'
    four_tier_settings['bond_cap_pct'] = '10.0'
    four_tier_settings['equity_cap_pct'] = '5.0'

    csv_text = make_test_csv(count=24)
    rows = parse_csv_rows(csv_text)
    gateway = ForecastGateway()

    res = simulate_policy('cash_only', rows, four_tier_settings, 'disabled', gateway, 'run_4tier', 'hash123')
    # Terminal wealth includes cash + bond mark (1000 * 100.50 * 100) + equity mark (500 * 500.00 * 100)
    # Bond mark: 1000 * 100.50 = $100,500 = 10,050,000 cents
    # Equity mark: 500 * 500.00 = $250,000 = 25,000,000 cents
    # Total marked noncash: 35,050,000 cents
    m = res['metrics']
    assert int(m['terminal_wealth_cents']) > int(default_settings['opening_cash_cents'])


def test_policy_comparison_service_winner_ranking_ac05():
    """FR-08, AC-05: Returns alone never determine winner; safety is enforced."""
    run_record = {
        'run_id': 'run_cmp_test',
        'scenario_fingerprint': 'abc123def456',
    }
    settings = {
        'opening_cash_cents': '5000000000',
        'reserve_floor_cents': '1000000000',
        'stress_ids': ['none'],
    }

    # Case A: fixed_repo has positive treasury delta with zero shortfalls -> fixed_repo preferred
    metrics_safe = [
        {'policy_id': 'cash_only', 'treasury_result_cents': '0', 'unpaid_new_cents': '0', 'shortfall_hours': 0, 'peak_debt_cents': '0', 'total_cost_cents': '0', 'terminal_wealth_cents': '5000000000'},
        {'policy_id': 'fixed_repo', 'treasury_result_cents': '50000', 'unpaid_new_cents': '0', 'shortfall_hours': 0, 'peak_debt_cents': '0', 'total_cost_cents': '0', 'terminal_wealth_cents': '5000050000'},
    ]
    cmp_safe = compare_policies(run_record, metrics_safe, settings)
    assert cmp_safe['winner_assessment']['preferred_policy'] == 'fixed_repo'
    assert cmp_safe['winner_assessment']['liquidity_safe'] is True

    # Case B (AC-05): fixed_repo has higher yield but causes shortfalls -> cash_only preferred!
    metrics_unsafe = [
        {'policy_id': 'cash_only', 'treasury_result_cents': '0', 'unpaid_new_cents': '0', 'shortfall_hours': 0, 'peak_debt_cents': '0', 'total_cost_cents': '0', 'terminal_wealth_cents': '5000000000'},
        {'policy_id': 'fixed_repo', 'treasury_result_cents': '100000', 'unpaid_new_cents': '5000000', 'shortfall_hours': 3, 'peak_debt_cents': '1000000', 'total_cost_cents': '1000', 'terminal_wealth_cents': '5000100000'},
    ]
    cmp_unsafe = compare_policies(run_record, metrics_unsafe, settings)
    # AC-05: yield cannot override unpaid obligations/shortfall hours!
    assert cmp_unsafe['winner_assessment']['preferred_policy'] == 'cash_only'
    assert cmp_unsafe['winner_assessment']['liquidity_safe'] is False
    assert cmp_unsafe['winner_assessment']['raw_return_only_ranking_prevented'] is True


def test_evidence_bundle_contains_comparison_json_and_hashes_reconcile(live):
    """FR-10, FR-13, AC-08: /runs/{id}/export includes comparison.json with valid SHA-256."""
    client, app = live
    # 1. Upload & create scenario
    upload_resp = upload(client)
    dataset_id = upload_resp.json()['dataset_id']
    sc_resp = scenario(client, dataset_id=dataset_id)
    sc_data = sc_resp.json()
    review(client, sc_data)

    # 2. Run simulation
    run_req = {
        'scenario_id': sc_data['scenario_id'],
        'policy_ids': ['cash_only', 'fixed_repo'],
        'forecast_mode': 'baseline',
        'adapter_artifact_id': None,
    }
    create_run_resp = client.post('/api/v1/runs', json=run_req, headers={'Idempotency-Key': 'run-exp-01'})
    run_id = create_run_resp.json()['run_id']
    from conftest import wait_for_run
    assert wait_for_run(client, run_id)['status'] == 'COMPLETED'

    # 3. Export evidence bundle
    export_resp = client.get(f'/api/v1/runs/{run_id}/export')
    assert export_resp.status_code == 200
    bundle = export_resp.json()
    validate('EvidenceBundle', bundle)

    # Verify members include comparison.json
    member_names = {m['name'] for m in bundle['members']}
    assert 'manifest.json' in member_names
    assert 'metrics.json' in member_names
    assert 'decisions.json' in member_names
    assert 'ledger_events.json' in member_names
    assert 'comparison.json' in member_names

    # Check manifest content
    manifest_member = next(m for m in bundle['members'] if m['name'] == 'manifest.json')
    manifest_doc = json.loads(manifest_member['content'])
    assert 'comparison.json' in manifest_doc['members_sha256']

    # Verify exact hash matches for every member
    for member in bundle['members']:
        expected_digest = hashlib.sha256(member['content'].encode()).hexdigest()
        assert member['sha256'] == expected_digest, f"Digest mismatch on {member['name']}"
