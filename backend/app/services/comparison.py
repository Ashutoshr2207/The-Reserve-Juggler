"""Policy comparison and four-tier attribution service implementing FR-06, FR-08, AC-05, AC-06."""
import json
from decimal import Decimal


def compare_policies(run_record: dict,
                     metrics_list: list[dict],
                     scenario_settings: dict,
                     dataset_rows: list[dict] | None = None) -> dict:
    """Compare simulation policies under identical fingerprint, evaluating four tiers and winner ranking.
    
    AC-05: Policies use identical scenario fingerprints and benchmark; no raw-return-only winner ranking.
    AC-06: Bonds and equities never become default payout reserves or automatic recommendations.
    """
    fingerprint = run_record['scenario_fingerprint']
    run_id = run_record.get('run_id') or run_record.get('id')
    stresses = scenario_settings.get('stress_ids', ['none'])

    metrics_by_policy = {m['policy_id']: m for m in metrics_list}
    cash_metrics = metrics_by_policy.get('cash_only')
    repo_metrics = metrics_by_policy.get('fixed_repo')

    comparison_deltas = {}
    winner_assessment = {}

    if cash_metrics and repo_metrics:
        delta_treasury = int(repo_metrics['treasury_result_cents']) - int(cash_metrics['treasury_result_cents'])
        delta_unpaid = int(repo_metrics['unpaid_new_cents']) - int(cash_metrics['unpaid_new_cents'])
        delta_shortfall_hours = repo_metrics['shortfall_hours'] - cash_metrics['shortfall_hours']
        delta_peak_debt = int(repo_metrics['peak_debt_cents']) - int(cash_metrics['peak_debt_cents'])
        delta_total_cost = int(repo_metrics['total_cost_cents']) - int(cash_metrics['total_cost_cents'])

        comparison_deltas = {
            'delta_treasury_result_cents': str(delta_treasury),
            'delta_unpaid_new_cents': str(delta_unpaid),
            'delta_shortfall_hours': delta_shortfall_hours,
            'delta_peak_debt_cents': str(delta_peak_debt),
            'delta_total_cost_cents': str(delta_total_cost),
        }

        # Winner assessment adhering to AC-05:
        # Returns on investment alone never determine winner.
        # If fixed_repo incurs more shortfalls or unpaid obligations than cash_only,
        # it CANNOT be preferred regardless of yield!
        if delta_unpaid > 0 or delta_shortfall_hours > 0 or delta_peak_debt > 0:
            preferred = 'cash_only'
            rationale = (
                'cash_only baseline preferred: fixed_repo incurred additional shortfalls '
                f'({delta_shortfall_hours}h) or unpaid obligations ({delta_unpaid} cents). '
                f'Additional peak debt: {delta_peak_debt} cents. '
                'Yield cannot compensate for compromised liquidity safety (AC-05).'
            )
            liquidity_safe = False
        elif delta_unpaid < 0 or delta_shortfall_hours < 0 or delta_peak_debt < 0:
            preferred = 'fixed_repo'
            rationale = 'fixed_repo preferred: reduced shortfall hours or unpaid obligations relative to cash_only.'
            liquidity_safe = True
        else:
            # Equal liquidity safety
            if delta_treasury > 0:
                preferred = 'fixed_repo'
                rationale = (
                    f'fixed_repo preferred: generated +{delta_treasury} cents incremental treasury result '
                    'with identical zero-additional-shortfall liquidity profile.'
                )
                liquidity_safe = True
            elif delta_treasury < 0:
                preferred = 'cash_only'
                rationale = 'cash_only preferred: fixed_repo underperformed after transaction fees or costs.'
                liquidity_safe = True
            else:
                preferred = 'tied'
                rationale = 'Both policies produced identical treasury and liquidity outcomes.'
                liquidity_safe = True

        if ((int(cash_metrics['unpaid_new_cents']) > 0 or cash_metrics['shortfall_hours'] > 0)
                and (int(repo_metrics['unpaid_new_cents']) > 0 or repo_metrics['shortfall_hours'] > 0)):
            preferred = 'no_safe_policy'
            rationale = 'Both policies have shortfalls; neither is a safe recommendation under this scenario.'
        # Equal failures cannot be advertised as safe merely because deltas are zero.
        liquidity_safe = (int(repo_metrics['unpaid_new_cents']) == 0
                          and repo_metrics['shortfall_hours'] == 0 and delta_peak_debt <= 0)
        winner_assessment = {
            'benchmark_policy': 'cash_only',
            'evaluated_policy': 'fixed_repo',
            'preferred_policy': preferred,
            'liquidity_safe': liquidity_safe,
            'raw_return_only_ranking_prevented': True,
            'rationale': rationale,
        }

    # Four-Tier Investment Framework summary (FR-06, AC-06)
    bond_units = str(scenario_settings.get('bond_units', '0'))
    equity_units = str(scenario_settings.get('equity_units', '0'))
    bond_cap = str(scenario_settings.get('bond_cap_pct', '0'))
    equity_cap = str(scenario_settings.get('equity_cap_pct', '0'))

    four_tier_summary = {
        'tier_0_operating_cash': {
            'description': 'Immediate demand liquidity for payouts; non-yielding.',
            'opening_cash_cents': str(scenario_settings['opening_cash_cents']),
            'reserve_floor_cents': str(scenario_settings['reserve_floor_cents']),
        },
        'tier_1_overnight_repo': {
            'description': '17:00 sweep window, 08:00 T+1 maturity, compound APY accrual, locked intraday.',
            'basis': scenario_settings.get('repo_basis', 'effective_apy'),
            'opening_repo_lots_count': len(scenario_settings.get('opening_repo_lots', [])),
        },
        'tier_2_treasury_bonds': {
            'description': '10Y Treasury index; marked-to-market what-if holding with liquidation haircut.',
            'units': bond_units,
            'cap_pct': bond_cap,
            'role': 'what_if_marked_exposure_only',
            'is_default_payout_reserve': False,
        },
        'tier_3_equities': {
            'description': 'S&P 500 stock index; marked-to-market what-if holding.',
            'units': equity_units,
            'cap_pct': equity_cap,
            'role': 'what_if_marked_exposure_only',
            'is_default_payout_reserve': False,
        },
        'compliance_note': (
            'AC-06: Tier 2 (bonds) and Tier 3 (equities) are price-only what-if exposures; '
            'they never become default payout reserves or automatic recommendations.'
        ),
    }

    return {
        'run_id': run_id,
        'scenario_fingerprint': fingerprint,
        'metric_definition_version': '1.0',
        'stresses_applied': stresses,
        'ordering_rule': scenario_settings.get('ordering', 'payout_before_deposit'),
        'comparison_deltas': comparison_deltas,
        'winner_assessment': winner_assessment,
        'four_tier_framework': four_tier_summary,
    }
