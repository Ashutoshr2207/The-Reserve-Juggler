"""Validators derive from the canonical authority, never a second model spec."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = json.loads((ROOT / 'contracts/openapi.json').read_text(encoding='utf-8'))


class Problem(Exception):
    def __init__(self, status, code, message, details=None, retryable=False):
        self.status, self.code, self.message = status, code, message
        self.details, self.retryable = details or [], retryable


def issue(field, message, row=None):
    return {'field': field, 'row': row, 'message': message}


def validate(name, value, *, output=False):
    schema = {'$ref': f'#/components/schemas/{name}', **CONTRACT}
    errors = list(Draft202012Validator(schema).iter_errors(value))
    if errors:
        if output:
            raise RuntimeError('Response violated canonical contract')
        # Never echo invalid values, submitted text, filenames or local paths.
        details = [issue('.'.join(map(str, e.absolute_path)) or 'body',
                         f'Invalid value ({e.validator}).') for e in errors[:25]]
        raise Problem(422, 'ASSUMPTIONS_INCOMPLETE', 'Request does not match the contract.', details)
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)
