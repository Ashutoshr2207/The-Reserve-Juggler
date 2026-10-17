"""Independent answer keys for accounting bugs uncovered during BE-04/05 review."""
from decimal import Decimal

from app.domain.adapter import ForecastGateway
from app.domain.ledger import compute_repo_accrual, parse_csv_rows, simulate_policy
from app.services.comparison import compare_policies
from conftest import csv_bytes, scenario_body


def run(rows, settings=None, policy='fixed_repo'):
    config = scenario_body('ds_fixture')['settings']
    config.update(opening_cash_cents='100000', reserve_floor_cents='10000',
                  credit_limit_cents='0', transaction_fee_cents='0', stress_ids=['none'],
                  opening_repo_lots=[], settlement_delay_hours=0, early_repo_release=False)
    config.update(settings or {})
    return simulate_policy(policy, rows, config, 'disabled', ForecastGateway(), 'run_regression', 'a' * 64)


def rows(count=48):
    return parse_csv_rows(csv_bytes(count).decode())


def test_start_of_hour_decision_ignores_current_and_future_flows_and_quotes():
    original = rows()
    changed = [dict(r) for r in original]
    for r in changed[17:]:
        r.update(deposits_cents=900000000, withdrawals_cents=100000000,
                 tier1_repo_rate_apy=Decimal('99'))
    before, after = run(original), run(changed)
    assert before['decisions'][0] == after['decisions'][0]
    assert before['repo_lots'][0]['rate_apy'] == after['repo_lots'][0]['rate_apy'] == '4.0'


def test_fee_is_reserved_and_posted_separately_without_creating_cash():
    data = rows()
    for r in data:
        r.update(deposits_cents=0, withdrawals_cents=0, tier1_repo_rate_apy=Decimal(0))
    result = run(data, {'transaction_fee_cents': '100'})
    sweep = next(e for e in result['ledger_events'] if e['event_type'] == 'REPO_SWEEP')
    fee = next(e for e in result['ledger_events'] if e['event_type'] == 'TRANSACTION_FEE')
    assert sweep['amount_cents'] == '-89900'
    assert fee['amount_cents'] == '-100' and fee['balance_cents'] == '10000'
    assert result['metrics']['treasury_result_cents'] == '-100'
    assert all(int(e['balance_cents']) >= 0 for e in result['ledger_events'])


def test_unsettled_deposits_are_receivables_and_not_an_investment_loss():
    data = rows(3)
    for r in data:
        r.update(deposits_cents=1000, withdrawals_cents=0)
    result = run(data, {'settlement_delay_hours': 2}, policy='cash_only')
    # Only hour zero deposit has settled; two more remain due after the horizon.
    assert result['diagnostics']['terminal_cash_cents'] == '101000'
    assert result['diagnostics']['terminal_receivables_cents'] == '2000'
    assert result['metrics']['terminal_wealth_cents'] == '103000'
    assert result['metrics']['treasury_result_cents'] == '0'


def test_credit_postings_and_unpaid_reconcile_without_debt_as_income():
    data = rows(1)
    data[0].update(deposits_cents=0, withdrawals_cents=500,
                   emergency_overdraft_penalty_apr_pct=Decimal(0))
    result = run(data, {'opening_cash_cents': '100', 'credit_limit_cents': '200',
                        'reserve_floor_cents': '0'}, policy='cash_only')
    assert result['metrics']['terminal_wealth_cents'] == '-400'
    assert result['metrics']['unpaid_new_cents'] == '200'
    assert result['metrics']['treasury_result_cents'] == '0'
    cash = 100
    for e in result['ledger_events'][1:]:
        if e['event_type'] != 'UNPAID_OBLIGATION':
            cash += int(e['amount_cents'])
        assert cash == int(e['balance_cents'])


def test_late_release_beyond_horizon_blocks_new_entry():
    result = run(rows(34), {'stress_ids': ['late_maturity']})
    assert result['repo_lots'] == []
    assert result['decisions'][0]['result'] == 'BLOCKED'


def test_missing_preorigin_quote_is_unknown_not_zero_rate():
    data = rows()[17:48]
    result = run(data)
    assert result['decisions'][0]['result'] == 'UNKNOWN'
    assert 'PRIOR_QUOTE_UNAVAILABLE' in result['decisions'][0]['reason_codes']


def test_early_redemption_haircut_applied_once_and_no_double_maturity():
    data = rows()
    for r in data:
        r.update(deposits_cents=0, withdrawals_cents=0, tier1_repo_rate_apy=Decimal(0),
                 tier1_early_redemption_haircut_pct=Decimal(10))
    data[18]['withdrawals_cents'] = 70000
    result = run(data, {'early_repo_release': True})
    released = [e for e in result['ledger_events'] if e['event_type'] == 'REPO_EARLY_RELEASE']
    assert len(released) == 1 and released[0]['amount_cents'] == '81000'
    assert result['metrics']['treasury_result_cents'] == '-9000'
    assert result['metrics']['total_cost_cents'] == '9000'
    assert result['repo_lots'][0]['status'] == 'EARLY_RELEASED'
    assert not any(e['event_type'] == 'REPO_MATURED' for e in result['ledger_events'])


def test_apr_and_effective_apy_have_independent_exact_answers():
    # One full year at 4% effective APY is exactly 4%, even at the int64 boundary.
    assert compute_repo_accrual(9_000_000_000_000_000_000, Decimal(4), 8760) == 360_000_000_000_000_000
    assert compute_repo_accrual(876000, Decimal(10), 1, 'simple_apr') == 10


def test_higher_peak_borrowing_prevents_return_only_preference():
    base = {'policy_id': 'cash_only', 'treasury_result_cents': '0', 'unpaid_new_cents': '0',
            'shortfall_hours': 0, 'peak_debt_cents': '0', 'total_cost_cents': '0',
            'terminal_wealth_cents': '100'}
    risky = {**base, 'policy_id': 'fixed_repo', 'treasury_result_cents': '10', 'peak_debt_cents': '50'}
    comparison = compare_policies({'run_id': 'run_fixture', 'scenario_fingerprint': 'a' * 64},
                                 [base, risky], scenario_body('ds_fixture')['settings'])
    assert comparison['winner_assessment']['preferred_policy'] == 'cash_only'
    assert comparison['winner_assessment']['liquidity_safe'] is False


def test_baseline_history_boundary_and_no_fabricated_quantile():
    gateway = ForecastGateway()
    data = rows(48)
    history = [{'timestamp': r['timestamp'], 'deposits_cents': str(i + 1),
                'withdrawals_cents': '0'} for i, r in enumerate(data[:24])]
    response = gateway.predict('baseline', 'a' * 64, data[24]['timestamp'], history, [15, 24])
    assert response['predicted_gross'][0]['deposits_cents'] == '120'
    assert response['path_deficit_quantiles'] == []
    response = gateway.predict('baseline', 'a' * 64, data[23]['timestamp'], history)
    assert response['effective_family'] == 'unavailable'


def test_bom_source_is_replayable():
    assert len(parse_csv_rows('\ufeff' + csv_bytes().decode())) == 24


def test_equal_shortfalls_do_not_become_a_safe_recommendation():
    base = {'policy_id': 'cash_only', 'treasury_result_cents': '0', 'unpaid_new_cents': '100',
            'shortfall_hours': 1, 'peak_debt_cents': '0', 'total_cost_cents': '0',
            'terminal_wealth_cents': '-100'}
    other = {**base, 'policy_id': 'fixed_repo', 'treasury_result_cents': '50'}
    comparison = compare_policies({'run_id': 'run_fixture', 'scenario_fingerprint': 'a' * 64},
                                 [base, other], scenario_body('ds_fixture')['settings'])
    assert comparison['winner_assessment']['preferred_policy'] == 'no_safe_policy'
    assert comparison['winner_assessment']['liquidity_safe'] is False
