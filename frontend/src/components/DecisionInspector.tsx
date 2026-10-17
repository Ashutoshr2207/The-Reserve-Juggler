import React from 'react';
import { Decision } from '../types/contracts';
import { MoneyCell } from './MoneyCell';

interface DecisionInspectorProps {
  decision: Decision;
  onNavigateEvidence?: () => void;
}

export const DecisionInspector: React.FC<DecisionInspectorProps> = ({ decision, onNavigateEvidence }) => {
  return (
    <div
      style={{
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        padding: 'var(--space-6)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-4)',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <span className="text-caption">INSPECTED DECISION POINT</span>
          <h3 style={{ fontSize: '18px', fontWeight: 600, marginTop: '2px' }} className="tabular-nums">
            {decision.origin}
          </h3>
        </div>
        <span
          style={{
            fontSize: '12px',
            fontWeight: 600,
            padding: '4px 10px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor:
              decision.result === 'ALLOWED'
                ? 'var(--color-success-bg)'
                : 'var(--color-warning-bg)',
            color:
              decision.result === 'ALLOWED'
                ? 'var(--color-success)'
                : 'var(--color-warning)',
            border: `1px solid ${
              decision.result === 'ALLOWED'
                ? 'var(--color-success-border)'
                : 'var(--color-warning-border)'
            }`,
          }}
        >
          ACTION: {decision.result}
        </span>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 'var(--space-3)',
          padding: 'var(--space-3) 0',
          borderTop: '1px solid var(--color-border-subtle)',
          borderBottom: '1px solid var(--color-border-subtle)',
        }}
      >
        <div>
          <span className="text-caption">USABLE CASH (BEFORE PAYOUT)</span>
          <div style={{ fontSize: '16px', fontWeight: 600 }}>
            <MoneyCell cents={decision.available_cash_cents} />
          </div>
        </div>
        <div>
          <span className="text-caption">PROPOSED SWEEP TO REPO</span>
          <div style={{ fontSize: '16px', fontWeight: 600 }}>
            <MoneyCell cents={decision.proposed_sweep_cents} />
          </div>
        </div>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 'var(--space-3)',
          padding: 'var(--space-3) 0',
          borderBottom: '1px solid var(--color-border-subtle)',
        }}
      >
        <div>
          <span className="text-caption">ENCUMBRANCE (LOCKED LOTS)</span>
          <div style={{ fontSize: '15px', fontWeight: 600 }}>
            <MoneyCell cents={decision.result === 'ALLOWED' ? decision.proposed_sweep_cents : '0'} />
          </div>
        </div>
        <div>
          <span className="text-caption">BORROWING / DEBT HEADROOM</span>
          <div style={{ fontSize: '15px', fontWeight: 600 }}>
            <MoneyCell cents="0" />
          </div>
        </div>
      </div>

      <div>
        <span className="text-caption">DECISION CONSEQUENCE</span>
        <div
          style={{
            fontSize: '13px',
            lineHeight: 1.5,
            padding: '8px 12px',
            backgroundColor:
              decision.result === 'ALLOWED'
                ? 'var(--color-success-bg)'
                : decision.result === 'BLOCKED'
                ? 'var(--color-warning-bg)'
                : 'var(--color-surface-subtle)',
            borderRadius: 'var(--radius-sm)',
            border: `1px solid ${
              decision.result === 'ALLOWED'
                ? 'var(--color-success-border)'
                : decision.result === 'BLOCKED'
                ? 'var(--color-warning-border)'
                : 'var(--color-border-subtle)'
            }`,
            color: 'var(--color-text)',
            marginTop: '4px',
          }}
        >
          {decision.result === 'ALLOWED' ? (
            <>
              <strong>Sweep Executed:</strong> Committed <MoneyCell cents={decision.proposed_sweep_cents} /> to Tier 1 overnight repo.
              Funds encumbered and unavailable until synthetic 08:00 release window.
            </>
          ) : decision.result === 'BLOCKED' ? (
            <>
              <strong>Sweep Prevented:</strong> Zero funds swept. 100% of available cash retained in Tier 0 to satisfy immediate intra-hour clearing obligations.
            </>
          ) : (
            <>
              <strong>Indeterminate State:</strong> Action unknown; defaulting to conservative liquid cash retention.
            </>
          )}
        </div>
      </div>

      <div>
        <span className="text-caption">REASON CODES &amp; INVARIANTS</span>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '4px' }}>
          {decision.reason_codes.map((rc, i) => (
            <span
              key={i}
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                backgroundColor: 'var(--color-surface-subtle)',
                padding: '3px 8px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--color-border)',
              }}
            >
              {rc}
            </span>
          ))}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)', fontSize: '13px' }}>
        <div>
          <span className="text-caption">INFORMATION CUTOFF</span>
          <div style={{ fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
            {decision.history_before}
          </div>
        </div>
        <div>
          <span className="text-caption">FORECAST ADAPTER FAMILY</span>
          <div style={{ fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
            {decision.effective_family}
          </div>
        </div>
      </div>

      <div>
        <span className="text-caption">CAUSAL INPUT HASH (SHA-256)</span>
        <div
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
            backgroundColor: 'var(--color-surface-subtle)',
            padding: '6px 10px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--color-border-subtle)',
            wordBreak: 'break-all',
            marginTop: '4px',
          }}
        >
          {decision.input_hash}
        </div>
      </div>

      {onNavigateEvidence && (
        <div style={{ marginTop: 'var(--space-4)', display: 'flex', justifyContent: 'flex-end' }}>
          <button className="btn btn-primary" onClick={onNavigateEvidence}>
            Export Evidence Bundle (S6) &rarr;
          </button>
        </div>
      )}
    </div>
  );
};
