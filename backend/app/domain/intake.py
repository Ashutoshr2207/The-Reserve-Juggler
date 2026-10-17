"""Exact input validation only. Forecasting and ledger execution belong to BE-02."""
import csv
import hashlib
import io
import re
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from app.api.contracts import Problem, issue

MAX_INT = 2**63 - 1
MAX_UPLOAD = 5 * 1024 * 1024
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
COLUMNS = (
    'timestamp', 'deposits_usd', 'withdrawals_usd', 'net_flow_usd',
    'repo_sweep_window_open', 'repo_sweep_mature', 'tier1_repo_rate_apy',
    'tier2_bond_yield_pct', 'tier2_bond_price_index', 'tier2_bond_mod_duration',
    'tier3_stock_index_price', 'tier3_stock_volatility_pct',
    'tier1_early_redemption_haircut_pct', 'tier2_bond_liquidation_haircut_pct',
    'tier3_stock_liquidation_haircut_pct', 'emergency_overdraft_penalty_apr_pct',
)
MONEY = {'deposits_usd', 'withdrawals_usd', 'net_flow_usd'}
FLAGS = {'repo_sweep_window_open': 17, 'repo_sweep_mature': 8}


def fail(field, message, row=None, code='INVALID_CSV'):
    raise Problem(422, code, 'Input validation failed.', [issue(field, message, row)])


def clock(value, field='timestamp', row=None, code='INVALID_CSV'):
    try:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', value):
            raise ValueError
        result = datetime.strptime(value, TIME_FORMAT)
        if result.minute or result.second:
            raise ValueError
        return result
    except (ValueError, TypeError):
        fail(field, 'Expected a valid whole-hour synthetic timestamp.', row, code)


def number(value, field, row=None, code='INVALID_CSV'):
    # Bounds prevent Decimal context rounding and abusive exponents/huge integers.
    if not isinstance(value, str) or len(value) > 40 or not re.fullmatch(r'-?\d+(?:\.\d+)?', value):
        fail(field, 'Expected a finite plain decimal.', row, code)
    try:
        result = Decimal(value)
        if len(result.as_tuple().digits) > 28:
            raise InvalidOperation
        return result
    except InvalidOperation:
        fail(field, 'Decimal precision exceeds 28 digits.', row, code)


def cents(value, field, row=None, dollars=False):
    amount = number(value, field, row, 'ASSUMPTIONS_INCOMPLETE' if not dollars else 'INVALID_CSV')
    amount *= 100 if dollars else 1
    if amount != amount.to_integral_value():
        fail(field, 'Money must be exact cents.', row)
    if abs(amount) > MAX_INT:
        fail(field, 'Money exceeds signed int64 cents.', row, 'AMOUNT_OUT_OF_RANGE')
    return int(amount)


def profile(source):
    if not source or len(source) > MAX_UPLOAD:
        fail('file', 'CSV must contain data and be at most 5 MiB.')
    try:
        text = source.decode('utf-8-sig')
        if '\x00' in text:
            fail('file', 'NUL bytes are not permitted.')
        reader = csv.reader(io.StringIO(text, newline=''), strict=True)
        header = next(reader)
        if len(header) != len(COLUMNS) or set(header) != set(COLUMNS):
            fail('file', 'Expected the sixteen unique D07 column names.', 1)
        previous = start = None
        count = residuals = 0
        for rowno, cells in enumerate(reader, 2):
            if len(cells) != len(header):
                fail('file', 'Unexpected cell count or blank row.', rowno)
            row = dict(zip(header, cells))
            stamp = clock(row['timestamp'], row=rowno)
            if previous is not None and stamp - previous != timedelta(hours=1):
                fail('timestamp', 'Rows must be ordered, unique and exactly one hour apart.', rowno)
            previous = stamp
            start = start or stamp
            amounts = {}
            for field in COLUMNS[1:]:
                value = row[field]
                if field in FLAGS:
                    if value not in ('True', 'False') or (value == 'True') != (stamp.hour == FLAGS[field]):
                        fail(field, 'Expected case-sensitive True/False matching the 17:00/08:00 schedule.', rowno)
                elif field in MONEY:
                    amounts[field] = cents(value, field, rowno, dollars=True)
                    if field != 'net_flow_usd' and amounts[field] < 0:
                        fail(field, 'Gross flows cannot be negative.', rowno)
                else:
                    numeric = number(value, field, rowno)
                    if numeric < 0 or ('price' in field and numeric <= 0):
                        fail(field, 'Expected a nonnegative rate or positive price.', rowno)
                    if 'haircut' in field and numeric > 100:
                        fail(field, 'Haircuts must be between 0 and 100 percentage points.', rowno)
            net = amounts['deposits_usd'] - amounts['withdrawals_usd']
            difference = amounts['net_flow_usd'] - net
            if abs(difference) > 1:
                fail('net_flow_usd', 'Gross-derived net differs by more than one cent.', rowno)
            residuals += bool(difference)
            count += 1
        if not count:
            fail('file', 'At least one data row is required.')
    except (UnicodeError, csv.Error, StopIteration):
        fail('file', 'Expected a well-formed UTF-8 CSV.')
    warnings = ['Synthetic input; profile validation does not certify funding or training rights.']
    if residuals:
        warnings.append(f'{residuals} rows have one-cent net residuals; canonical net uses gross cents.')
    return {'sha256': hashlib.sha256(source).hexdigest(), 'rows': count, 'columns': 16,
            'start': start.strftime(TIME_FORMAT), 'end': previous.strftime(TIME_FORMAT),
            'clock': 'synthetic_naive', 'warnings': warnings}


def settings_semantics(settings, dataset):
    code = 'ASSUMPTIONS_INCOMPLETE'
    if settings['fictional_acknowledged'] is not True:
        fail('settings.fictional_acknowledged', 'Explicit fictional acknowledgment is required.', code=code)
    for field in ('opening_cash_cents', 'reserve_floor_cents', 'credit_limit_cents', 'transaction_fee_cents'):
        cents(settings[field], f'settings.{field}')
    caps = []
    for field in ('bond_cap_pct', 'equity_cap_pct'):
        cap = number(settings[field], f'settings.{field}', code=code)
        if not 0 <= cap <= 100:
            fail(f'settings.{field}', 'Exposure caps must be between 0 and 100.', code=code)
        caps.append(cap)
    if sum(caps) > 100:
        fail('settings', 'Combined risky exposure caps exceed 100 percent.', code=code)
    for field in ('bond_units', 'equity_units'):
        units = number(settings[field], f'settings.{field}', code=code)
        if units < 0 or units.as_tuple().exponent < -8:
            fail(f'settings.{field}', 'Units must be nonnegative with at most eight decimals.', code=code)
        if units != 0:
            fail(f'settings.{field}', 'Opening marks before the first origin are unavailable; initial units must be zero.', code=code)
    stresses = settings['stress_ids']
    if len(set(stresses)) != len(stresses) or ('none' in stresses and len(stresses) != 1):
        fail('settings.stress_ids', 'Stress choices must be unique; none cannot be combined.', code=code)
    start = clock(dataset['start'])
    seen = set()
    total = int(settings['opening_cash_cents'])
    for i, lot in enumerate(settings['opening_repo_lots']):
        prefix = f'settings.opening_repo_lots.{i}'
        principal = cents(lot['principal_cents'], prefix + '.principal_cents')
        entry = clock(lot['entry_time'], prefix + '.entry_time', code=code)
        maturity = clock(lot['maturity_time'], prefix + '.maturity_time', code=code)
        rate = number(lot['entry_rate_pct'], prefix + '.entry_rate_pct', code=code)
        if principal <= 0 or rate < 0 or entry.hour != 17 or maturity - entry != timedelta(hours=15) or not entry < start <= maturity:
            fail(prefix, 'Opening lot needs positive principal, nonnegative entry rate and a prior 17:00 entry with unexpired next-08:00 maturity.', code=code)
        identity = (entry, maturity)
        if identity in seen:
            fail(prefix, 'Duplicate opening lot lifecycle.', code=code)
        seen.add(identity)
        total += principal
    if total + int(settings['credit_limit_cents']) > MAX_INT:
        fail('settings', 'Combined opening endowment and credit exceed signed int64.', code='AMOUNT_OUT_OF_RANGE')
