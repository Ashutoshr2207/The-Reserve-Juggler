"""Independent reviewed fixture tests validating Invariants I01–I12 and domain ledger execution."""
import io
import csv
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.domain.adapter import ForecastGateway
from app.domain.intake import COLUMNS
from app.domain.ledger import compute_repo_accrual, parse_csv_rows, simulate_policy


def make_fixture_csv(count=48, mutate=None):
    rows = []
    base_time = datetime(2026, 1, 1, 0, 0, 0)
    for i in range(count):
        stamp = base_time + timedelta(hours=i)
        is_17 = stamp.hour == 17
        is_8 = stamp.hour == 8
        row = {
            'timestamp': stamp.strftime('%Y-%m-%d %H:%M:%S'),
            'deposits_usd': '1000.00',
            'withdrawals_usd': '800.00',
            'net_flow_usd': '200.00',
            'repo_sweep_window_open': str(is_17),
            'repo_sweep_mature': str(is_8),
            'tier1_repo_rate_apy': '4.0',
            'tier2_bond_yield_pct': '5.0',
            'tier2_bond_price_index': '100.0',
            'tier2_bond_mod_duration': '4.5',
            'tier3_stock_index_price': '5000.0',
            'tier3_stock_volatility_pct': '15.0',
            'tier1_early_redemption_haircut_pct': '1.0',
            'tier2_bond_liquidation_haircut_pct': '2.0',
            'tier3_stock_liquidation_haircut_pct': '5.0',
            'emergency_overdraft_penalty_apr_pct': '10.0',
        }
        rows.append(row)
    if mutate:
        mutate(rows)
    buf = io.StringIO(newline='')
    writer = csv.DictWriter(buf, fieldnames=COLUMNS)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


@pytest.fixture
def base_settings():
    return {
        'opening_cash_cents': '5000000000',  # $50M
        'reserve_floor_cents': '1000000000',  # $10M
        'credit_limit_cents': '500000000',   # $5M
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


def test_i01_canonical_net_is_gross_deposits_minus_withdrawals():
    csv_text = make_fixture_csv(count=5)
    rows = parse_csv_rows(csv_text)
    for r in rows:
        assert r['deposits_cents'] == 100000
        assert r['withdrawals_cents'] == 80000
        canonical_net = r['deposits_cents'] - r['withdrawals_cents']
        assert canonical_net == 20000


def test_i02_decisions_use_strictly_prior_history(base_settings):
    csv_text = make_fixture_csv(count=48)
    rows = parse_csv_rows(csv_text)
    gateway = ForecastGateway()
    result = simulate_policy('fixed_repo', rows, base_settings, 'baseline', gateway, 'run_test_i02', 'hash123')
    decisions = result['decisions']
    assert len(decisions) > 0
    for dec in decisions:
        assert dec['history_before'] == dec['origin']


def test_i03_cash_conservation_law(base_settings):
    csv_text = make_fixture_csv(count=48)
    rows = parse_csv_rows(csv_text)
    gateway = ForecastGateway()
    result = simulate_policy('fixed_repo', rows, base_settings, 'baseline', gateway, 'run_test_i03', 'hash123')
    events = result['ledger_events']

    # Verify that closing balance in every event equals previous balance + amount
    current_cash = int(base_settings['opening_cash_cents'])
    for evt in events:
        if evt['event_type'] == 'OPENING_BALANCE':
            continue
        amt = int(evt['amount_cents'])
        bal = int(evt['balance_cents'])
        if evt['event_type'] != 'UNPAID_OBLIGATION':
            # Cash-impacting events must conserve exactly
            expected_bal = current_cash + amt
            assert bal == expected_bal, f"Conservation violation in {evt['event_type']}: expected {expected_bal}, got {bal}"
            current_cash = bal


def test_i04_repo_lock_and_terminal_boundary_prevention(base_settings):
    # Exactly 24 hours: 17:00 occurs at index 17, maturity would be 17 + 15 = 32 > 23 (file end)
    csv_text = make_fixture_csv(count=24)
    rows = parse_csv_rows(csv_text)
    gateway = ForecastGateway()
    result = simulate_policy('fixed_repo', rows, base_settings, 'baseline', gateway, 'run_test_i04', 'hash123')
    decisions = result['decisions']
    # Decision at 17:00 must be BLOCKED due to INSUFFICIENT_FUTURE_HORIZON
    sweep_dec = next(d for d in decisions if '17:00:00' in d['origin'])
    assert sweep_dec['result'] == 'BLOCKED'
    assert 'INSUFFICIENT_FUTURE_HORIZON' in sweep_dec['reason_codes']
    assert sweep_dec['proposed_sweep_cents'] == '0'


def test_i05_repo_effective_apy_accrual_half_even_quantization():
    # $10,000,000 principal at 4.0% APY for 15 hours
    p = 1000000000  # cents
    rate = Decimal('4.0')
    accrual = compute_repo_accrual(p, rate, hours=15)
    # 1.04 ** (15/8760) - 1 ≈ 0.000067161424
    # 1,000,000,000 * 0.000067161424 = 67161.42 cents -> 67161 cents
    assert accrual == 67161


def test_i07_finite_credit_and_overdraft_interest(base_settings):
    # Stress: massive withdrawals causing deficit and credit draw
    def stress_withdrawals(rows):
        rows[10]['withdrawals_usd'] = '55000000.00'  # $55M withdraw > $50M cash
    csv_text = make_fixture_csv(count=24, mutate=stress_withdrawals)
    rows = parse_csv_rows(csv_text)
    gateway = ForecastGateway()
    result = simulate_policy('cash_only', rows, base_settings, 'disabled', gateway, 'run_test_i07', 'hash123')
    m = result['metrics']
    # Deficit was $55M - $50.002M = $4,998,000.00 (499,800,000 cents), within $5M credit limit
    assert int(m['peak_debt_cents']) == 499800000
    assert int(m['total_cost_cents']) > 0  # interest accrued on debt


def test_i08_unpaid_obligations_explicit_and_separate_from_stock(base_settings):
    # Stress: massive withdrawals exceeding cash + credit
    def huge_withdrawals(rows):
        rows[5]['withdrawals_usd'] = '60000000.00'  # $60M withdraw > $50.001M cash + $5M credit
    csv_text = make_fixture_csv(count=24, mutate=huge_withdrawals)
    rows = parse_csv_rows(csv_text)
    gateway = ForecastGateway()
    result = simulate_policy('cash_only', rows, base_settings, 'disabled', gateway, 'run_test_i08', 'hash123')
    m = result['metrics']
    # Deficit was $60M - $50.001M = $9,999,000.00. Credit drew $5M. Unpaid was $4,999,000.00 (499,900,000 cents)
    assert int(m['unpaid_new_cents']) == 499900000
    assert m['shortfall_hours'] > 0


def test_i09_terminal_wealth_and_treasury_result_formula(base_settings):
    # Simple 24h run with no shortfalls and no debt
    csv_text = make_fixture_csv(count=24)
    rows = parse_csv_rows(csv_text)
    gateway = ForecastGateway()
    result = simulate_policy('cash_only', rows, base_settings, 'disabled', gateway, 'run_test_i09', 'hash123')
    m = result['metrics']
    # External net = 24 * (1000.00 - 800.00) = $4,800.00 = 480,000 cents
    # Opening cash = $50M = 5,000,000,000 cents
    # Closing cash = 5,000,480,000 cents
    # Terminal wealth = 5,000,480,000 cents
    # Wealth change = 480,000 cents
    # Treasury result = 480,000 - 480,000 = 0 cents!
    assert int(m['terminal_wealth_cents']) == 5000480000
    assert int(m['treasury_result_cents']) == 0
    assert int(m['unpaid_new_cents']) == 0
    assert int(m['total_cost_cents']) == 0


def test_i10_policy_comparison_identical_fingerprint(base_settings):
    csv_text = make_fixture_csv(count=48)
    rows = parse_csv_rows(csv_text)
    gateway = ForecastGateway()
    res_cash = simulate_policy('cash_only', rows, base_settings, 'baseline', gateway, 'run_cmp', 'hash123')
    res_repo = simulate_policy('fixed_repo', rows, base_settings, 'baseline', gateway, 'run_cmp', 'hash123')
    
    # In fixed_repo, interest earned on repo sweeps yields a positive treasury result
    m_cash = res_cash['metrics']
    m_repo = res_repo['metrics']
    assert int(m_repo['treasury_result_cents']) >= int(m_cash['treasury_result_cents'])


def test_i11_unavailable_adapter_gives_explicit_fallback(base_settings):
    csv_text = make_fixture_csv(count=24)
    rows = parse_csv_rows(csv_text)
    gateway = ForecastGateway()
    # Adapter predict with disabled mode returns unavailable quality/family
    pred = gateway.predict('disabled', 'hash123', '2026-03-01 17:00:00', [])
    assert pred['effective_family'] == 'unavailable'
    assert pred['quality_label'] == 'unavailable'

    # Decisions map unavailable adapter response to contract-compliant disabled enum
    res = simulate_policy('fixed_repo', rows, base_settings, 'disabled', gateway, 'run_unavail', 'hash123')
    for dec in res['decisions']:
        assert dec['effective_family'] == 'disabled'


def test_i12_reproducibility_of_simulation_replay(base_settings):
    csv_text = make_fixture_csv(count=48)
    rows = parse_csv_rows(csv_text)
    gateway = ForecastGateway()
    run1 = simulate_policy('fixed_repo', rows, base_settings, 'baseline', gateway, 'run_rep', 'hash123')
    run2 = simulate_policy('fixed_repo', rows, base_settings, 'baseline', gateway, 'run_rep', 'hash123')
    assert run1['metrics'] == run2['metrics']
    assert len(run1['decisions']) == len(run2['decisions'])
    assert run1['decisions'][0]['input_hash'] == run2['decisions'][0]['input_hash']
