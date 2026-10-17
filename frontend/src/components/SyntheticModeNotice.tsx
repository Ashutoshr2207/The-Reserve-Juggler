import React from 'react';
import { IconWarning } from './Icons';

interface SyntheticModeNoticeProps {
  compact?: boolean;
}

export const SyntheticModeNotice: React.FC<SyntheticModeNoticeProps> = ({ compact = false }) => {
  if (compact) {
    return (
      <div
        role="status"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 'var(--space-2)',
          padding: '2px 8px',
          background: 'var(--color-warning-bg)',
          border: '1px solid var(--color-warning-border)',
          borderRadius: 'var(--radius-sm)',
          fontSize: '12px',
          color: 'var(--color-warning)',
          fontWeight: 600,
        }}
      >
        <IconWarning size={14} />
        <span>SIMULATED MODEL (FICTIONAL ASSUMPTIONS)</span>
      </div>
    );
  }

  return (
    <div
      role="region"
      aria-label="Synthetic Environment Notice"
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: 'var(--space-3)',
        padding: 'var(--space-3) var(--space-4)',
        backgroundColor: 'var(--color-warning-bg)',
        border: '1px solid var(--color-warning-border)',
        borderRadius: 'var(--radius-md)',
        marginBottom: 'var(--space-4)',
      }}
    >
      <div style={{ color: 'var(--color-warning)', marginTop: '2px' }}>
        <IconWarning size={20} />
      </div>
      <div>
        <div style={{ fontWeight: 600, color: 'var(--color-warning)', fontSize: '14px', marginBottom: '2px' }}>
          Synthetic Simulation Environment &amp; Fictional Policy Mode
        </div>
        <div style={{ fontSize: '13px', color: 'var(--color-text)', lineHeight: 1.4 }}>
          Reserve Juggler is a local treasury policy simulator and causal replay engine. It does not operate a bank, hold customer funds, or move money. All flows, rate projections, and stress assumptions are synthetic. Backtest outputs reflect model logic, not institutional solvency or asset guarantees.
        </div>
      </div>
    </div>
  );
};

export const LiveApiStatusBadge: React.FC<{ isFixtureMode: boolean }> = ({ isFixtureMode }) => {
  return (
    <div
      title={isFixtureMode ? 'Using contract fixture fallback (standalone)' : 'Connected to local FastAPI simulation backend'}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '3px 8px',
        backgroundColor: isFixtureMode ? 'var(--color-surface-subtle)' : 'var(--color-success-bg)',
        border: `1px solid ${isFixtureMode ? 'var(--color-border)' : 'var(--color-success-border)'}`,
        borderRadius: 'var(--radius-sm)',
        fontSize: '12px',
        color: isFixtureMode ? 'var(--color-text-muted)' : 'var(--color-success)',
        fontWeight: 500,
      }}
    >
      <span
        style={{
          width: '7px',
          height: '7px',
          borderRadius: '50%',
          backgroundColor: isFixtureMode ? 'var(--color-text-subtle)' : 'var(--color-success)',
        }}
      />
      <span>{isFixtureMode ? 'Contract Fixture Mode' : 'Local API Active'}</span>
    </div>
  );
};
