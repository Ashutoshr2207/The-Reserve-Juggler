"""Pure domain cash/lot/debt/obligation simulation engine implementing Invariants I01–I12."""
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

from app.api.contracts import canonical
from app.domain.adapter import ForecastGateway
from app.domain.intake import clock, TIME_FORMAT


def compute_repo_accrual(principal_cents: int,
                         rate_apy_pct: Decimal,
                         hours: int = 15,
                         basis: str = 'effective_apy') -> int:
    """I05: fixed entry-rate effective APY (or simple APR) over actual hours/8760, quantized HALF_EVEN to cents."""
    if basis == 'simple_apr':
        interest = Decimal(principal_cents) * (rate_apy_pct / Decimal('100')) * (Decimal(hours) / Decimal('8760'))
        return int(interest.quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))
    with localcontext() as ctx:
        ctx.prec = 48
        factor = (Decimal(1) + rate_apy_pct / 100) ** (Decimal(hours) / 8760) - 1
        interest = Decimal(principal_cents) * factor
        return int(interest.quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))


def simulate_policy(policy_id: str,
                    dataset_rows: list[dict],
                    settings: dict,
                    forecast_mode: str,
                    adapter_gateway: ForecastGateway,
                    run_id: str,
                    dataset_hash: str,
                    checkpoint=None, artifact_id=None) -> dict:
    """Execute single policy replay under exact accounting and invariants."""
    opening_cash = int(settings['opening_cash_cents'])
    reserve_floor = int(settings['reserve_floor_cents'])
    credit_limit = int(settings['credit_limit_cents'])
    fee_per_tx = int(settings.get('transaction_fee_cents', 0))
    ordering = settings.get('ordering', 'payout_before_deposit')
    repo_basis = settings.get('repo_basis', 'effective_apy')
    early_repo_release = settings.get('early_repo_release', False)
    settlement_delay = int(settings.get('settlement_delay_hours', 0))

    stress_ids = settings.get('stress_ids', ['none'])
    has_withdrawal_shock = 'withdrawal_shock' in stress_ids
    has_deposit_delay = 'deposit_delay' in stress_ids
    has_late_maturity = 'late_maturity' in stress_ids
    has_denied_credit = 'denied_credit' in stress_ids

    effective_credit_limit = 0 if has_denied_credit else credit_limit

    # Four-Tier Holdings (FR-06, I06)
    bond_units = Decimal(str(settings.get('bond_units', '0')))
    equity_units = Decimal(str(settings.get('equity_units', '0')))

    cash_cents = opening_cash
    debt_principal_cents = 0
    unpaid_interest_accrual = Decimal('0')
    outstanding_unpaid_cents = 0
    total_unpaid_new_cents = 0
    shortfall_hours = 0
    peak_debt_cents = 0
    total_fees_cents = 0
    total_haircuts_cents = 0
    debt_hour_sum = 0
    minimum_cash_cents = opening_cash

    active_repo_lots = []
    all_repo_lots = []
    decisions = []
    ledger_events = []
    sequence = 0
    delayed_deposits = {}  # settlement hour -> receivable cents

    def record_event(origin, event_type, amount, balance, debt, unpaid, details=None):
        nonlocal sequence
        from app.domain.intake import MAX_INT
        if any(abs(value) > MAX_INT for value in (amount, balance, debt, unpaid)) or min(balance, debt, unpaid) < 0:
            raise ArithmeticError('Invalid or out-of-range ledger posting')
        sequence += 1
        ledger_events.append({
            'sequence': sequence,
            'policy_id': policy_id,
            'origin': origin,
            'event_type': event_type,
            'amount_cents': str(amount),
            'balance_cents': str(balance),
            'debt_cents': str(debt),
            'unpaid_cents': str(unpaid),
            'details_json': canonical(details or {}),
        })

    # Record initial opening balance event
    record_event(dataset_rows[0]['timestamp'], 'OPENING_BALANCE', opening_cash, cash_cents,
                 debt_principal_cents, outstanding_unpaid_cents)

    # Initialize opening repo lots if specified
    for lot_input in settings.get('opening_repo_lots', []):
        entry_t = lot_input['entry_time']
        mat_t = lot_input['maturity_time']
        rate_apy = Decimal(str(lot_input['entry_rate_pct']))
        p = int(lot_input['principal_cents'])
        lot = {
            'lot_id': f"lot_open_{len(all_repo_lots)+1}",
            'policy_id': policy_id,
            'principal_cents': str(p),
            'rate_apy': str(rate_apy),
            'entry_time': entry_t,
            'maturity_time': mat_t,
            'status': 'LOCKED',
            'accrued_interest_cents': '0',
        }
        active_repo_lots.append(lot)
        all_repo_lots.append(lot)

    # Opening marked wealth components (I06, I09)
    opening_bond_cents = int((bond_units * Decimal(str(dataset_rows[0]['tier2_bond_price_index'])) * Decimal('100')).quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))
    opening_equity_cents = int((equity_units * Decimal(str(dataset_rows[0]['tier3_stock_index_price'])) * Decimal('100')).quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))
    opening_repo_principal = sum(int(l['principal_cents']) for l in active_repo_lots)
    opening_repo_accrued = sum(compute_repo_accrual(
        int(l['principal_cents']), Decimal(l['rate_apy']),
        hours=int((clock(dataset_rows[0]['timestamp']) - clock(l['entry_time'])).total_seconds() // 3600),
        basis=repo_basis) for l in active_repo_lots)
    opening_wealth = opening_cash + opening_repo_principal + opening_repo_accrued + opening_bond_cents + opening_equity_cents

    dataset_end_dt = clock(dataset_rows[-1]['timestamp'])

    # Hourly simulation loop
    for i, row in enumerate(dataset_rows):
        origin = row['timestamp']
        current_dt = clock(origin)
        # Step 1: Matured Repo Lots Release (I04, I05)
        # Under normal conditions, 08:00 release of existing lots.
        # Under late_maturity stress, release is delayed until 12:00.
        can_release_repo = row['repo_sweep_mature']
        if has_late_maturity and current_dt.hour < 12:
            can_release_repo = False

        if can_release_repo or (has_late_maturity and current_dt.hour >= 12 and any(l['status'] == 'LOCKED' and current_dt >= clock(l['maturity_time']) for l in active_repo_lots)):
            maturing = [lot for lot in active_repo_lots if current_dt >= clock(lot['maturity_time']) and lot['status'] == 'LOCKED']
            for lot in maturing:
                p = int(lot['principal_cents'])
                rate = Decimal(lot['rate_apy'])
                entry_dt = clock(lot['entry_time'])
                mat_hours = max(1, int((current_dt - entry_dt).total_seconds() // 3600))
                interest = compute_repo_accrual(p, rate, hours=mat_hours, basis=repo_basis)
                total_return = p + interest
                cash_cents += total_return
                lot['status'] = 'MATURED'
                lot['accrued_interest_cents'] = str(interest)
                record_event(origin, 'REPO_MATURED', total_return, cash_cents,
                             debt_principal_cents, outstanding_unpaid_cents,
                             {'lot_id': lot['lot_id'], 'principal_cents': p, 'interest_cents': interest})
            active_repo_lots = [lot for lot in active_repo_lots if lot['status'] == 'LOCKED']

        # Step 7: Repo Sweep Decision (17:00 sweep window, I04)
        if row['repo_sweep_window_open']:
            available_cash_before = cash_cents
            decision_state = {'debt_cents': str(debt_principal_cents),
                              'unpaid_cents': str(outstanding_unpaid_cents),
                              'active_repo_lots': [dict(lot) for lot in active_repo_lots]}
            surplus = max(0, cash_cents - reserve_floor - fee_per_tx)
            # Only completed prior hours are supplied to the conventional gateway.
            history_before = [
                {'timestamp': r['timestamp'], 'deposits_cents': str(r['deposits_cents']),
                 'withdrawals_cents': str(r['withdrawals_cents'])}
                for r in dataset_rows[max(0, i - 168):i]
            ]
            # Forecast query
            forecast = adapter_gateway.predict(
                forecast_mode, dataset_hash, origin, history_before, [15, 24], artifact_id=artifact_id
            )

            if policy_id == 'cash_only':
                result = 'BLOCKED'
                proposed_sweep = '0'
                reason_codes = ['POLICY_CASH_ONLY']
            else:
                # fixed_repo policy
                maturity_target = current_dt + timedelta(hours=15)
                release_target = maturity_target + timedelta(hours=4 if has_late_maturity else 0)
                if i == 0:
                    result = 'UNKNOWN'
                    proposed_sweep = '0'
                    reason_codes = ['PRIOR_QUOTE_UNAVAILABLE']
                elif release_target > dataset_end_dt:
                    # I04: No entry maturing after available horizon
                    result = 'BLOCKED'
                    proposed_sweep = '0'
                    reason_codes = ['INSUFFICIENT_FUTURE_HORIZON']
                elif surplus <= 0:
                    result = 'BLOCKED'
                    proposed_sweep = '0'
                    reason_codes = ['RESERVE_FLOOR_BINDING']
                elif debt_principal_cents > 0 or outstanding_unpaid_cents > 0:
                    # Liabilities precede discretionary sweep
                    result = 'BLOCKED'
                    proposed_sweep = '0'
                    reason_codes = ['OUTSTANDING_LIABILITIES']
                else:
                    proposed_sweep = str(surplus)
                    result = 'ALLOWED'
                    reason_codes = ['SWEEP_PERMITTED']
                    # Execute sweep
                    cash_cents -= surplus
                    new_lot = {
                        'lot_id': f"lot_{origin.replace(' ', '_').replace(':', '')}",
                        'policy_id': policy_id,
                        'principal_cents': str(surplus),
                        'rate_apy': str(dataset_rows[i - 1]['tier1_repo_rate_apy']),
                        'entry_time': origin,
                        'maturity_time': maturity_target.strftime(TIME_FORMAT),
                        'status': 'LOCKED',
                        'accrued_interest_cents': '0',
                    }
                    active_repo_lots.append(new_lot)
                    all_repo_lots.append(new_lot)
                    record_event(origin, 'REPO_SWEEP', -surplus, cash_cents,
                                 debt_principal_cents, outstanding_unpaid_cents,
                                 {'lot_id': new_lot['lot_id'], 'principal_cents': surplus})
                    if fee_per_tx > 0:
                        total_fees_cents += fee_per_tx
                        cash_cents -= fee_per_tx
                        record_event(origin, 'TRANSACTION_FEE', -fee_per_tx, cash_cents,
                                     debt_principal_cents, outstanding_unpaid_cents)

            eff_fam = forecast.get('effective_family', 'disabled')
            if eff_fam not in (
                'disabled', 'seasonal_baseline', 'quantile_experiment', 'sarimax_experiment', 'pretrained_experiment'
            ):
                eff_fam = 'disabled'

            if forecast.get('quality_label') == 'unavailable' or not forecast.get('predicted_gross'):
                reason_codes.append('CONVENTIONAL_FIXED_RULE_FALLBACK')
            input_digest = hashlib.sha256(canonical({
                'dataset_hash': dataset_hash,
                'settings': settings,
                'ledger_before_action': decision_state,
                'origin': origin,
                'policy_id': policy_id,
                'available_cash_cents': str(available_cash_before),
                'proposed_sweep_cents': proposed_sweep,
                'forecast_origin': forecast.get('origin'),
                'effective_family': eff_fam,
                'forecast': forecast,
                'prior_quote_rate': str(dataset_rows[i - 1]['tier1_repo_rate_apy']) if i else None,
            }).encode()).hexdigest()

            decisions.append({
                'decision_id': f"dec_{policy_id}_{origin.replace(' ', '_').replace(':', '')}",
                'run_id': run_id,
                'origin': origin,
                'history_before': origin,
                'policy_id': policy_id,
                'available_cash_cents': str(available_cash_before),
                'proposed_sweep_cents': proposed_sweep,
                'result': result,
                'reason_codes': reason_codes,
                'effective_family': eff_fam,
                'quality_label': 'computed_simulation',
                'input_hash': input_digest,
            })

        # Determine effective withdrawals under withdrawal_shock stress (FR-07, AC-07)
        raw_withdrawals = row['withdrawals_cents']
        if has_withdrawal_shock:
            # 50% shock surge on requested withdrawals
            req_payout = int((Decimal(raw_withdrawals) * Decimal('1.5')).quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))
        else:
            req_payout = raw_withdrawals

        # Determine effective deposits under deposit_delay stress / settlement delay
        raw_deposits = row['deposits_cents']
        delay_hours = max(1, settlement_delay) if has_deposit_delay else settlement_delay
        if delay_hours > 0:
            due = i + delay_hours
            delayed_deposits[due] = delayed_deposits.get(due, 0) + raw_deposits
            current_deposits = delayed_deposits.pop(i, 0)
        else:
            current_deposits = raw_deposits

        # Optional, explicitly configured whole-lot early redemption under distress.
        # Conservative convention: principal less one lagged haircut; forego interest.
        payout_cash = cash_cents + (current_deposits if ordering == 'netted_end_hour' else 0)
        if early_repo_release and payout_cash < req_payout and i > 0:
            haircut_rate = dataset_rows[i - 1]['tier1_early_redemption_haircut_pct']
            for lot in list(active_repo_lots):
                if payout_cash >= req_payout:
                    break
                principal = int(lot['principal_cents'])
                haircut = int((Decimal(principal) * haircut_rate / 100).quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))
                proceeds = principal - haircut
                cash_cents += proceeds
                payout_cash += proceeds
                total_haircuts_cents += haircut
                lot['status'] = 'EARLY_RELEASED'
                active_repo_lots.remove(lot)
                record_event(origin, 'REPO_EARLY_RELEASE', proceeds, cash_cents,
                             debt_principal_cents, outstanding_unpaid_cents,
                             {'lot_id': lot['lot_id'], 'principal_cents': principal,
                              'haircut_cents': haircut, 'interest_foregone': True})

        minimum_cash_cents = min(minimum_cash_cents, cash_cents)

        # Step 2 & 3: Cash Flow Execution based on ordering
        if ordering == 'payout_before_deposit':
            # Payouts first against available cash
            if req_payout > 0:
                if cash_cents >= req_payout:
                    cash_cents -= req_payout
                    record_event(origin, 'WITHDRAWAL_PAID', -req_payout, cash_cents,
                                 debt_principal_cents, outstanding_unpaid_cents)
                else:
                    paid_cash = cash_cents
                    deficit = req_payout - paid_cash
                    cash_cents = 0
                    if paid_cash > 0:
                        record_event(origin, 'WITHDRAWAL_PAID', -paid_cash, cash_cents,
                                     debt_principal_cents, outstanding_unpaid_cents)

                    # Emergency credit draw if available (I07)
                    available_credit = max(0, effective_credit_limit - debt_principal_cents)
                    if available_credit > 0 and deficit > 0:
                        draw = min(deficit, available_credit)
                        cash_cents += draw
                        debt_principal_cents += draw
                        deficit -= draw
                        if debt_principal_cents > peak_debt_cents:
                            peak_debt_cents = debt_principal_cents
                        record_event(origin, 'CREDIT_DRAW', draw, cash_cents,
                                     debt_principal_cents, outstanding_unpaid_cents)
                        cash_cents -= draw
                        record_event(origin, 'WITHDRAWAL_PAID', -draw, cash_cents,
                                     debt_principal_cents, outstanding_unpaid_cents)

                    # Remaining deficit becomes explicit unpaid liability (I08)
                    if deficit > 0:
                        total_unpaid_new_cents += deficit
                        outstanding_unpaid_cents += deficit
                        record_event(origin, 'UNPAID_OBLIGATION', deficit, cash_cents,
                                     debt_principal_cents, outstanding_unpaid_cents,
                                     {'unpaid_new_cents': deficit})

            # Deposits arrive
            if current_deposits > 0:
                cash_cents += current_deposits
                record_event(origin, 'DEPOSIT_RECEIVED', current_deposits, cash_cents,
                             debt_principal_cents, outstanding_unpaid_cents)

        elif ordering == 'netted_end_hour':
            # Netted cash flow at end of hour
            net_flow = current_deposits - req_payout
            if net_flow >= 0:
                cash_cents += net_flow
                record_event(origin, 'NET_FLOW_CREDIT', net_flow, cash_cents,
                             debt_principal_cents, outstanding_unpaid_cents)
            else:
                deficit = -net_flow
                if cash_cents >= deficit:
                    cash_cents -= deficit
                    record_event(origin, 'NET_FLOW_DEBIT', -deficit, cash_cents,
                                 debt_principal_cents, outstanding_unpaid_cents)
                else:
                    paid_cash = cash_cents
                    rem_deficit = deficit - paid_cash
                    cash_cents = 0
                    if paid_cash > 0:
                        record_event(origin, 'NET_FLOW_DEBIT', -paid_cash, cash_cents,
                                     debt_principal_cents, outstanding_unpaid_cents)

                    # Credit draw
                    available_credit = max(0, effective_credit_limit - debt_principal_cents)
                    if available_credit > 0 and rem_deficit > 0:
                        draw = min(rem_deficit, available_credit)
                        cash_cents += draw
                        debt_principal_cents += draw
                        rem_deficit -= draw
                        if debt_principal_cents > peak_debt_cents:
                            peak_debt_cents = debt_principal_cents
                        record_event(origin, 'CREDIT_DRAW', draw, cash_cents,
                                     debt_principal_cents, outstanding_unpaid_cents)
                        cash_cents -= draw
                        record_event(origin, 'NET_FLOW_DEBIT', -draw, cash_cents,
                                     debt_principal_cents, outstanding_unpaid_cents)

                    if rem_deficit > 0:
                        total_unpaid_new_cents += rem_deficit
                        outstanding_unpaid_cents += rem_deficit
                        record_event(origin, 'UNPAID_OBLIGATION', rem_deficit, cash_cents,
                                     debt_principal_cents, outstanding_unpaid_cents,
                                     {'unpaid_new_cents': rem_deficit})

        # Step 4: Settle unpaid obligations and repay credit debt if surplus above floor
        if outstanding_unpaid_cents > 0 and cash_cents > reserve_floor:
            surplus = cash_cents - reserve_floor
            repay_unpaid = min(surplus, outstanding_unpaid_cents)
            cash_cents -= repay_unpaid
            outstanding_unpaid_cents -= repay_unpaid
            record_event(origin, 'UNPAID_SETTLED', -repay_unpaid, cash_cents,
                         debt_principal_cents, outstanding_unpaid_cents)

        if debt_principal_cents > 0 and cash_cents > reserve_floor:
            surplus = cash_cents - reserve_floor
            repay_debt = min(surplus, debt_principal_cents)
            cash_cents -= repay_debt
            debt_principal_cents -= repay_debt
            record_event(origin, 'DEBT_REPAYMENT', -repay_debt, cash_cents,
                         debt_principal_cents, outstanding_unpaid_cents)

        # Step 5: Borrowing Interest Accrual (I07)
        if debt_principal_cents > 0:
            penalty_apr = Decimal(str(row['emergency_overdraft_penalty_apr_pct']))
            hourly_interest = Decimal(debt_principal_cents) * (penalty_apr / Decimal('100')) / Decimal('8760')
            unpaid_interest_accrual += hourly_interest

        # Step 6: Shortfall Tracking
        if outstanding_unpaid_cents > 0:
            shortfall_hours += 1

        debt_hour_sum += debt_principal_cents
        record_event(origin, 'HOUR_CLOSE', 0, cash_cents, debt_principal_cents,
                     outstanding_unpaid_cents,
                     {'unsettled_deposits_cents': str(sum(delayed_deposits.values())),
                      'locked_repo_principal_cents': str(sum(int(l['principal_cents']) for l in active_repo_lots)),
                      'unpaid_interest_cents_unrounded': str(unpaid_interest_accrual)})

        if checkpoint:
            checkpoint(i + 1, decisions, ledger_events, all_repo_lots)

    # Terminal Wealth and Treasury Result Calculation (I06, I09)
    total_borrowing_costs = int(unpaid_interest_accrual.quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))
    total_cost_cents = total_borrowing_costs + total_fees_cents + total_haircuts_cents

    active_repo_principal = sum(int(l['principal_cents']) for l in active_repo_lots)
    active_repo_accrued = sum(
        compute_repo_accrual(int(l['principal_cents']), Decimal(l['rate_apy']),
                             hours=int((dataset_end_dt + timedelta(hours=1) - clock(l['entry_time'])).total_seconds() // 3600),
                             basis=repo_basis)
        for l in active_repo_lots
    )

    # Marked positions at terminal boundary (I06: marked to market, no automatic liquidation)
    terminal_bond_cents = int((bond_units * Decimal(str(dataset_rows[-1]['tier2_bond_price_index'])) * Decimal('100')).quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))
    terminal_equity_cents = int((equity_units * Decimal(str(dataset_rows[-1]['tier3_stock_index_price'])) * Decimal('100')).quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))

    terminal_wealth = (
        cash_cents
        + sum(delayed_deposits.values())  # unsettled deposits are receivables, never cash
        + active_repo_principal
        + active_repo_accrued
        + terminal_bond_cents
        + terminal_equity_cents
        - debt_principal_cents
        - outstanding_unpaid_cents
        - total_borrowing_costs
    )

    total_gross_deposits = sum(r['deposits_cents'] for r in dataset_rows)
    if has_withdrawal_shock:
        total_requested_withdrawals = sum(
            int((Decimal(r['withdrawals_cents']) * Decimal('1.5')).quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))
            for r in dataset_rows
        )
    else:
        total_requested_withdrawals = sum(r['withdrawals_cents'] for r in dataset_rows)

    net_external_flows = total_gross_deposits - total_requested_withdrawals
    wealth_change = terminal_wealth - opening_wealth
    treasury_result = wealth_change - net_external_flows

    metrics = {
        'policy_id': policy_id,
        'treasury_result_cents': str(treasury_result),
        'unpaid_new_cents': str(total_unpaid_new_cents),
        'shortfall_hours': shortfall_hours,
        'peak_debt_cents': str(peak_debt_cents),
        'terminal_wealth_cents': str(terminal_wealth),
        'total_cost_cents': str(total_cost_cents),
    }

    # Stop on arithmetic beyond the declared posting range; never publish invalid success.
    from app.domain.intake import MAX_INT
    if any(abs(int(v)) > MAX_INT for k, v in metrics.items() if k.endswith('_cents')):
        raise ArithmeticError('Ledger amount exceeds signed int64 cents')
    return {
        'policy_id': policy_id,
        'metrics': metrics,
        'diagnostics': {
            'opening_wealth_cents': str(opening_wealth),
            'net_external_flows_cents': str(net_external_flows),
            'terminal_cash_cents': str(cash_cents),
            'terminal_receivables_cents': str(sum(delayed_deposits.values())),
            'terminal_repo_principal_cents': str(active_repo_principal),
            'terminal_repo_accrued_cents': str(active_repo_accrued),
            'terminal_bond_mark_cents': str(terminal_bond_cents),
            'terminal_equity_mark_cents': str(terminal_equity_cents),
            'terminal_debt_cents': str(debt_principal_cents),
            'terminal_unpaid_cents': str(outstanding_unpaid_cents),
            'borrowing_cost_cents': str(total_borrowing_costs),
            'transaction_fees_cents': str(total_fees_cents),
            'haircut_cost_cents': str(total_haircuts_cents),
            'minimum_cash_before_payout_cents': str(minimum_cash_cents),
            'mean_debt_cents': str(Decimal(debt_hour_sum) / len(dataset_rows)),
            'early_release_convention': 'whole lot; lagged principal haircut once; interest foregone',
        },
        'decisions': decisions,
        'ledger_events': ledger_events,
        'repo_lots': all_repo_lots,
    }


def parse_csv_rows(source_text: str) -> list[dict]:
    """Parse CSV text into structured rows with exact cents."""
    import csv, io
    reader = csv.DictReader(io.StringIO(source_text.lstrip('\ufeff'), newline=''))
    rows = []
    for r in reader:
        # Canonical net is gross deposits minus gross withdrawals in cents (I01)
        dep = int((Decimal(r['deposits_usd']) * 100).quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))
        wth = int((Decimal(r['withdrawals_usd']) * 100).quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))
        rows.append({
            'timestamp': r['timestamp'],
            'deposits_cents': dep,
            'withdrawals_cents': wth,
            'repo_sweep_window_open': r['repo_sweep_window_open'].strip().lower() == 'true',
            'repo_sweep_mature': r['repo_sweep_mature'].strip().lower() == 'true',
            'tier1_repo_rate_apy': Decimal(r['tier1_repo_rate_apy']),
            'tier2_bond_price_index': Decimal(r['tier2_bond_price_index']),
            'tier2_bond_liquidation_haircut_pct': Decimal(r['tier2_bond_liquidation_haircut_pct']),
            'tier1_early_redemption_haircut_pct': Decimal(r['tier1_early_redemption_haircut_pct']),
            'tier3_stock_index_price': Decimal(r['tier3_stock_index_price']),
            'emergency_overdraft_penalty_apr_pct': Decimal(r['emergency_overdraft_penalty_apr_pct']),
        })
    return rows
