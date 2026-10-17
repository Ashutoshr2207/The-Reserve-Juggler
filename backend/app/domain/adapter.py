"""Internal forecast adapter gateway conforming to forecast-adapter.schema.json."""
import hashlib
import json
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path

from jsonschema import Draft202012Validator

from app.api.contracts import ROOT
from app.domain.intake import clock
from datetime import timedelta

ADAPTER_SCHEMA = json.loads((ROOT / 'contracts/forecast-adapter.schema.json').read_text(encoding='utf-8'))
ADAPTER_VALIDATOR = Draft202012Validator(ADAPTER_SCHEMA)


class ForecastGateway:
    def __init__(self, validator=ADAPTER_VALIDATOR):
        self.validator = validator

    def request(self, dataset_hash: str, origin: str, history: list[dict], horizons_hours: list[int]) -> dict:
        if len(dataset_hash) != 64 or not all(c in '0123456789abcdef' for c in dataset_hash.lower()):
            dataset_hash = hashlib.sha256(dataset_hash.encode()).hexdigest()
        req = {
            'message_type': 'forecast_request',
            'adapter_contract': '1.0',
            'dataset_hash': dataset_hash.lower(),
            'origin': origin,
            'history': history,
            'horizons_hours': horizons_hours,
        }
        self.validator.validate(req)
        origin_dt = clock(origin)
        stamps = [clock(row['timestamp']) for row in history]
        if (any(t >= origin_dt for t in stamps)
                or any(b - a != timedelta(hours=1) for a, b in zip(stamps, stamps[1:]))
                or stamps[-1] != origin_dt - timedelta(hours=1)):
            raise ValueError('Unavailable or noncausal forecast history')
        return req

    def predict(self, mode: str, dataset_hash: str, origin: str,
                history: list[dict], horizons_hours: list[int] | None = None,
                artifact_id: str | None = None) -> dict:
        horizons = horizons_hours or [15, 24]
        # Validate request payload shape
        if history:
            try:
                self.request(dataset_hash, origin, history, horizons)
            except Exception:
                return {
                    'message_type': 'forecast_response', 'adapter_contract': '1.0',
                    'origin': origin, 'training_cutoff': None, 'effective_family': 'unavailable',
                    'artifact_id': None, 'quality_label': 'unavailable', 'predicted_gross': [],
                    'path_deficit_quantiles': [], 'warnings': ['INVALID_HISTORY: conventional fixed-rule fallback.'],
                }

        if mode == 'disabled':
            resp = {
                'message_type': 'forecast_response',
                'adapter_contract': '1.0',
                'origin': origin,
                'training_cutoff': None,
                'effective_family': 'unavailable',
                'artifact_id': None,
                'quality_label': 'unavailable',
                'predicted_gross': [],
                'path_deficit_quantiles': [],
                'warnings': ['FORECAST_DISABLED: disabled by run configuration.'],
            }
        elif mode == 'baseline':
            # Check history length: seasonal baseline needs history strictly before origin
            if len(history) < 24:
                # Short history fallback
                resp = {
                    'message_type': 'forecast_response',
                    'adapter_contract': '1.0',
                    'origin': origin,
                    'training_cutoff': None,
                    'effective_family': 'seasonal_baseline',
                    'artifact_id': None,
                    'quality_label': 'conventional_estimate',
                    'predicted_gross': [],
                    'path_deficit_quantiles': [],
                    'warnings': ['SHORT_HISTORY: backend must select labeled conventional fallback.'],
                }
            else:
                # Repeat the last observed day at the same hour; no fitted probabilities.
                recent_24 = history[-24:]
                predicted_gross = []
                path_deficit_quantiles = []
                for h in horizons:
                    dep_h = sum(int(r['deposits_cents']) for r in recent_24[:h])
                    wth_h = sum(int(r['withdrawals_cents']) for r in recent_24[:h])
                    predicted_gross.append({
                        'horizon_hours': h,
                        'deposits_cents': str(max(0, dep_h)),
                        'withdrawals_cents': str(max(0, wth_h)),
                    })
                resp = {
                    'message_type': 'forecast_response',
                    'adapter_contract': '1.0',
                    'origin': origin,
                    'training_cutoff': None,
                    'effective_family': 'seasonal_baseline',
                    'artifact_id': None,
                    'quality_label': 'conventional_estimate',
                    'predicted_gross': predicted_gross,
                    'path_deficit_quantiles': path_deficit_quantiles,
                    'warnings': ['UNCALIBRATED_BASELINE: no probability or accuracy claim.'],
                }
        else:
            # Experimental mode or unrecognized
            resp = {
                'message_type': 'forecast_response',
                'adapter_contract': '1.0',
                'origin': origin,
                'training_cutoff': None,
                'effective_family': 'unavailable',
                'artifact_id': artifact_id,
                'quality_label': 'unavailable',
                'predicted_gross': [],
                'path_deficit_quantiles': [],
                'warnings': ['EXPERIMENTAL_UNAVAILABLE: experimental model not active or cleared.'],
            }

        self.validator.validate(resp)
        return resp
