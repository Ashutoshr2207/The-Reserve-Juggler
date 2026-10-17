import React from 'react';
import { MetricSet } from '../types/contracts';
import { MoneyCell } from './MoneyCell';

interface ComparisonTableProps {
  metrics: MetricSet;
  onInspectDecisions?: () => void;
}

export const ComparisonTable: React.FC<ComparisonTableProps> = ({ metrics, onInspectDecisions }) => {
  return (
    <div
      style={{
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          padding: 'var(--space-4) var(--space-6)',
          backgroundColor: 'var(--color-surface-subtle)',
          borderBottom: '1px solid var(--color-border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div>
          <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Policy Replay Comparison Matrix</h3>
          <p className="text-caption">Standardized accounting invariants under identical endowment &amp; constraints (AC-05)</p>
        </div>
        {onInspectDecisions && (
          <button className="btn btn-secondary btn-sm" onClick={onInspectDecisions}>
            Inspect Hourly Decisions (S5) &rarr;
          </button>
        )}
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--color-border)', textAlign: 'left', backgroundColor: 'var(--color-surface)' }}>
              <th style={{ padding: '12px 16px', fontWeight: 600 }}>Policy Identity</th>
              <th style={{ padding: '12px 16px', fontWeight: 600, textAlign: 'right' }}>Net Treasury Result</th>
              <th style={{ padding: '12px 16px', fontWeight: 600, textAlign: 'right' }}>Terminal Wealth</th>
              <th style={{ padding: '12px 16px', fontWeight: 600, textAlign: 'right' }}>Unpaid Obligations</th>
              <th style={{ padding: '12px 16px', fontWeight: 600, textAlign: 'right' }}>Shortfall Hours</th>
              <th style={{ padding: '12px 16px', fontWeight: 600, textAlign: 'right' }}>Peak Debt</th>
              <th style={{ padding: '12px 16px', fontWeight: 600, textAlign: 'right' }}>Total Cost</th>
            </tr>
          </thead>
          <tbody>
            {metrics.metrics.map((m, i) => (
              <tr key={i} style={{ borderBottom: '1px solid var(--color-border-subtle)' }}>
                <td style={{ padding: '12px 16px', fontWeight: 600 }}>
                  {m.policy_id === 'cash_only' ? (
                    <span>Cash-Only Baseline (RG-00)</span>
                  ) : (
                    <span>Fixed-Floor Repo Sweep</span>
                  )}
                </td>
                <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                  <MoneyCell cents={m.treasury_result_cents} />
                </td>
                <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                  <MoneyCell cents={m.terminal_wealth_cents} showSignColor={false} />
                </td>
                <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                  <MoneyCell cents={m.unpaid_new_cents} />
                </td>
                <td style={{ padding: '12px 16px', textAlign: 'right' }} className="tabular-nums">
                  {m.shortfall_hours} hrs
                </td>
                <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                  <MoneyCell cents={m.peak_debt_cents} />
                </td>
                <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                  <MoneyCell cents={m.total_cost_cents} showSignColor={false} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div
        style={{
          padding: 'var(--space-3) var(--space-6)',
          backgroundColor: 'var(--color-surface-subtle)',
          borderTop: '1px solid var(--color-border)',
          fontSize: '12px',
          color: 'var(--color-text-muted)',
        }}
      >
        Metric Definition v1.0 | Quality: <strong>{metrics.quality_label}</strong>. Net treasury result includes investment return minus transaction fees, repo redemption haircuts, and overdraft debt interest.
      </div>
    </div>
  );
};
