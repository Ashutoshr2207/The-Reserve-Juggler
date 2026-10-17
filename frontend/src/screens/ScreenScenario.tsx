import React, { useState } from 'react';
import { Dataset, Scenario, Settings, ApiError, RoleMode } from '../types/contracts';
import { api, DEFAULT_SETTINGS, formatMoneyCents } from '../client/api';
import { IconScenario } from '../components/Icons';
import { ErrorSummary } from '../components/ErrorSummary';
import { SyntheticModeNotice } from '../components/SyntheticModeNotice';

interface ScreenScenarioProps {
  dataset: Dataset | null;
  scenario: Scenario | null;
  roleMode?: RoleMode;
  onScenarioSaved: (scenario: Scenario) => void;
  onNavigateNext: () => void;
}

export const ScreenScenario: React.FC<ScreenScenarioProps> = ({
  dataset,
  scenario,
  roleMode = 'maker',
  onScenarioSaved,
  onNavigateNext,
}) => {
  const [label, setLabel] = useState(scenario?.label || 'Baseline Conventional Treasury Policy');
  const [settings, setSettings] = useState<Settings>(scenario?.settings || DEFAULT_SETTINGS);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const canEdit = roleMode === 'maker' || roleMode === 'operator';

  const handleTextChange = (field: keyof Settings, value: string) => {
    setSettings((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleBoolChange = (field: keyof Settings, value: boolean) => {
    setSettings((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleStressToggle = (stressId: Settings['stress_ids'][number]) => {
    setSettings((prev) => {
      let updated = [...prev.stress_ids];
      if (stressId === 'none') {
        updated = ['none'];
      } else {
        updated = updated.filter((id) => id !== 'none');
        if (updated.includes(stressId)) {
          updated = updated.filter((id) => id !== stressId);
          if (updated.length === 0) updated = ['none'];
        } else {
          updated.push(stressId);
        }
      }
      return { ...prev, stress_ids: updated };
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!canEdit) {
      setError({
        code: 'FORBIDDEN',
        message: `Scenario mutation is not permitted for role '${roleMode}'.`,
        request_id: 'req_local_role',
        retryable: false,
        details: [{ field: 'role_mode', row: null, message: 'Maker or Operator role required (AUTH_SECURITY.md).' }],
      });
      return;
    }

    if (!dataset) {
      setError({
        code: 'ASSUMPTIONS_INCOMPLETE',
        message: 'A validated dataset must be loaded before a scenario can be created.',
        request_id: 'req_local_nodataset',
        retryable: false,
        details: [{ field: 'dataset_id', row: null, message: 'Select or import a dataset in S1.' }],
      });
      return;
    }

    if (!settings.opening_cash_cents || !settings.reserve_floor_cents || !settings.credit_limit_cents) {
      setError({
        code: 'ASSUMPTIONS_INCOMPLETE',
        message: 'Mandatory numeric assumptions cannot be blank.',
        request_id: 'req_local_empty_numeric',
        retryable: false,
        details: [
          ...(!settings.opening_cash_cents ? [{ field: 'opening_cash_cents', row: null, message: 'Opening cash is required.' }] : []),
          ...(!settings.reserve_floor_cents ? [{ field: 'reserve_floor_cents', row: null, message: 'Reserve floor is required.' }] : []),
          ...(!settings.credit_limit_cents ? [{ field: 'credit_limit_cents', row: null, message: 'Credit limit is required.' }] : []),
        ],
      });
      return;
    }

    if (!settings.fictional_acknowledged) {
      setError({
        code: 'ASSUMPTIONS_INCOMPLETE',
        message: 'Mandatory fictional assumption acknowledgment missing.',
        request_id: 'req_local_ack',
        retryable: false,
        details: [{ field: 'fictional_acknowledged', row: null, message: 'You must acknowledge the synthetic nature of this simulation.' }],
      });
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const created = await api.createScenario({
        dataset_id: dataset.dataset_id,
        label,
        settings,
      });
      onScenarioSaved(created);
      onNavigateNext();
    } catch (err: unknown) {
      setError(err as ApiError);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Screen Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--color-primary)', marginBottom: '4px' }}>
          <IconScenario size={20} />
          <span style={{ fontSize: '13px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Screen S2</span>
        </div>
        <h1>Scenario &amp; Policy Assumptions Specification</h1>
        <p style={{ color: 'var(--color-text-muted)', marginTop: '4px', maxWidth: '840px' }}>
          Declare versioned liquid endowment, liquidity buffer floors, borrowing facilities, and risky asset exposure caps (FR-02).
        </p>
      </div>

      <SyntheticModeNotice />
      <ErrorSummary error={error} onDismiss={() => setError(null)} />

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
        {/* Scenario Metadata */}
        <div
          style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--space-6)',
          }}
        >
          <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: 'var(--space-3)' }}>Scenario Information</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-4)' }}>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                Scenario Policy Label
              </label>
              <input
                type="text"
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                required
                maxLength={120}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                Bound Dataset ID
              </label>
              <input
                type="text"
                value={dataset?.dataset_id || 'No dataset selected (return to S1)'}
                disabled
                style={{ backgroundColor: 'var(--color-surface-subtle)', color: 'var(--color-text-muted)' }}
              />
            </div>
          </div>
        </div>

        {/* Core Liquid Cash & Buffer (Tier 0 & Tier 1) */}
        <div
          style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--space-6)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-4)' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Tier 0 &amp; Tier 1: Cash &amp; Repo Liquidity Buffer</h3>
            <span
              style={{
                fontSize: '11px',
                fontWeight: 600,
                color: 'var(--color-success)',
                backgroundColor: 'var(--color-success-bg)',
                padding: '2px 8px',
                borderRadius: 'var(--radius-sm)',
              }}
            >
              DEFAULT POLICIES
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-4)' }}>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>
                Opening Cash (cents)
              </label>
              <span className="text-caption" style={{ display: 'block', marginBottom: '6px' }}>
                Current: <strong className="tabular-nums">{formatMoneyCents(settings.opening_cash_cents)}</strong>
              </span>
              <input
                type="text"
                value={settings.opening_cash_cents}
                onChange={(e) => handleTextChange('opening_cash_cents', e.target.value.replace(/[^0-9]/g, ''))}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>
                Liquidity Reserve Floor (cents)
              </label>
              <span className="text-caption" style={{ display: 'block', marginBottom: '6px' }}>
                Minimum floor: <strong className="tabular-nums">{formatMoneyCents(settings.reserve_floor_cents)}</strong>
              </span>
              <input
                type="text"
                value={settings.reserve_floor_cents}
                onChange={(e) => handleTextChange('reserve_floor_cents', e.target.value.replace(/[^0-9]/g, ''))}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>
                Emergency Credit Limit (cents)
              </label>
              <span className="text-caption" style={{ display: 'block', marginBottom: '6px' }}>
                Available credit: <strong className="tabular-nums">{formatMoneyCents(settings.credit_limit_cents)}</strong>
              </span>
              <input
                type="text"
                value={settings.credit_limit_cents}
                onChange={(e) => handleTextChange('credit_limit_cents', e.target.value.replace(/[^0-9]/g, ''))}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>
                Per-Transaction Execution Fee (cents)
              </label>
              <span className="text-caption" style={{ display: 'block', marginBottom: '6px' }}>
                Fee: <strong className="tabular-nums">{formatMoneyCents(settings.transaction_fee_cents)}</strong>
              </span>
              <input
                type="text"
                value={settings.transaction_fee_cents}
                onChange={(e) => handleTextChange('transaction_fee_cents', e.target.value.replace(/[^0-9]/g, ''))}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                Intra-Hour Flow Ordering
              </label>
              <select
                value={settings.ordering}
                onChange={(e) => handleTextChange('ordering', e.target.value as Settings['ordering'])}
              >
                <option value="payout_before_deposit">Payout before deposit (Conservative)</option>
                <option value="netted_end_hour">Netted end of hour</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                Repo Accrual Basis
              </label>
              <select
                value={settings.repo_basis}
                onChange={(e) => handleTextChange('repo_basis', e.target.value as Settings['repo_basis'])}
              >
                <option value="effective_apy">Effective APY compounding</option>
                <option value="simple_apr">Simple APR basis</option>
              </select>
            </div>
          </div>

          <div style={{ marginTop: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <input
              type="checkbox"
              id="earlyRepoRelease"
              checked={settings.early_repo_release}
              onChange={(e) => handleBoolChange('early_repo_release', e.target.checked)}
            />
            <label htmlFor="earlyRepoRelease" style={{ fontSize: '14px', cursor: 'pointer' }}>
              Permit emergency early repo redemption (subject to dataset haircut penalty)
            </label>
          </div>
        </div>

        {/* Tier 2 (Bonds) & Tier 3 (Equities) What-If Section (FR-06) */}
        <div
          style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--space-6)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Tier 2 &amp; Tier 3: Risky Asset What-If Exposures</h3>
            <span
              style={{
                fontSize: '11px',
                fontWeight: 600,
                color: 'var(--color-warning)',
                backgroundColor: 'var(--color-warning-bg)',
                padding: '2px 8px',
                borderRadius: 'var(--radius-sm)',
              }}
            >
              SEPARATE CAPPED WHAT-IF
            </span>
          </div>
          <p className="text-small" style={{ marginBottom: 'var(--space-4)', lineHeight: 1.4 }}>
            In accordance with FR-06 and AC-06, bonds and equities are controlled what-if scenarios. They are never treated as default payout reserves, and marked price valuation does not imply settled cash liquidity.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 'var(--space-4)' }}>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                Tier 2: Opening Bond Units
              </label>
              <input
                type="text"
                value={settings.bond_units}
                onChange={(e) => handleTextChange('bond_units', e.target.value)}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                Tier 2: Max Bond Allocation Cap (%)
              </label>
              <input
                type="text"
                value={settings.bond_cap_pct}
                onChange={(e) => handleTextChange('bond_cap_pct', e.target.value)}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                Tier 3: Opening Equity Units
              </label>
              <input
                type="text"
                value={settings.equity_units}
                onChange={(e) => handleTextChange('equity_units', e.target.value)}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                Tier 3: Max Equity Allocation Cap (%)
              </label>
              <input
                type="text"
                value={settings.equity_cap_pct}
                onChange={(e) => handleTextChange('equity_cap_pct', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Stress Scenarios (FR-07) */}
        <div
          style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--space-6)',
          }}
        >
          <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: 'var(--space-2)' }}>
            FR-07 Stress Injections &amp; Boundary Conditions
          </h3>
          <p className="text-small" style={{ marginBottom: 'var(--space-4)' }}>
            Inject adverse liquidity events to evaluate policy resilience under liquidity stress.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-3)' }}>
            {[
              { id: 'none', label: 'No Injected Stresses (Standard Replay)' },
              { id: 'withdrawal_shock', label: 'Withdrawal Spike Shock (+50%)' },
              { id: 'deposit_delay', label: 'Inbound Deposit Delay (2-Hour Lag)' },
              { id: 'late_maturity', label: 'Late Repo Maturity Release' },
              { id: 'denied_credit', label: 'Denied Emergency Overdraft' },
            ].map((stress) => (
              <label
                key={stress.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-2)',
                  padding: 'var(--space-3)',
                  backgroundColor: settings.stress_ids.includes(stress.id as any)
                    ? 'var(--color-primary-light)'
                    : 'var(--color-surface-subtle)',
                  border: `1px solid ${
                    settings.stress_ids.includes(stress.id as any)
                      ? 'var(--color-primary)'
                      : 'var(--color-border)'
                  }`,
                  borderRadius: 'var(--radius-md)',
                  cursor: 'pointer',
                  fontSize: '13px',
                }}
              >
                <input
                  type="checkbox"
                  checked={settings.stress_ids.includes(stress.id as any)}
                  onChange={() => handleStressToggle(stress.id as any)}
                />
                <span>{stress.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Fictional Scenario Acknowledgment (AC-02) */}
        <div
          style={{
            backgroundColor: settings.fictional_acknowledged ? 'var(--color-success-bg)' : 'var(--color-warning-bg)',
            border: `1px solid ${settings.fictional_acknowledged ? 'var(--color-success-border)' : 'var(--color-warning-border)'}`,
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--space-6)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-3)',
          }}
        >
          <h3 style={{ fontSize: '15px', fontWeight: 600, color: settings.fictional_acknowledged ? 'var(--color-success)' : 'var(--color-warning)' }}>
            Mandatory Scenario Fictionality Acknowledgment
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--color-text)', lineHeight: 1.5 }}>
            By submitting this scenario for review, I confirm that these settings represent a fictional analytical hypothesis for backtest simulation purposes only, and not an approved institutional credit line or banking commitment.
          </p>
          <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', cursor: 'pointer', marginTop: 'var(--space-2)' }}>
            <input
              type="checkbox"
              checked={settings.fictional_acknowledged}
              onChange={(e) => handleBoolChange('fictional_acknowledged', e.target.checked)}
              required
            />
            <span style={{ fontSize: '14px', fontWeight: 600 }}>
              I acknowledge these assumptions as a fictional analytical scenario (AC-02)
            </span>
          </label>
        </div>

        {/* Submit Actions */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setSettings(DEFAULT_SETTINGS)}
              disabled={!canEdit}
            >
              Reset to Baseline Defaults
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting || !settings.fictional_acknowledged || !canEdit}
            >
              {isSubmitting ? 'Registering Draft...' : 'Submit Draft for Review (S3) \u2192'}
            </button>
          </div>
          {!canEdit && (
            <div style={{ fontSize: '12px', color: 'var(--color-warning)', textAlign: 'right' }}>
              Scenario submission restricted for role '{roleMode}' (AUTH_SECURITY.md).
            </div>
          )}
        </div>
      </form>
    </div>
  );
};
