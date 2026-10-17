import React from 'react';
import { IconClose } from './Icons';

interface LegalModalProps {
  isOpen: boolean;
  type: 'terms' | 'privacy' | null;
  onClose: () => void;
}

export const LegalModal: React.FC<LegalModalProps> = ({ isOpen, type, onClose }) => {
  if (!isOpen || !type) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="legal-dialog-title"
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(9, 30, 66, 0.54)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 2000,
        padding: 'var(--space-4)',
      }}
    >
      <div
        style={{
          backgroundColor: 'var(--color-surface)',
          borderRadius: 'var(--radius-lg)',
          maxWidth: '680px',
          width: '100%',
          maxHeight: '85vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: 'var(--shadow-lg)',
          border: '1px solid var(--color-border)',
        }}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: 'var(--space-4) var(--space-6)',
            borderBottom: '1px solid var(--color-border)',
          }}
        >
          <h2 id="legal-dialog-title" style={{ fontSize: '18px', fontWeight: 600 }}>
            {type === 'terms' ? 'Terms of Simulation & Operational Scope' : 'Privacy & Local Data Isolation Policy'}
          </h2>
          <button
            onClick={onClose}
            aria-label="Close dialog"
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--color-text-muted)',
              padding: '4px',
            }}
          >
            <IconClose size={20} />
          </button>
        </div>

        <div
          style={{
            padding: 'var(--space-6)',
            overflowY: 'auto',
            fontSize: '14px',
            lineHeight: 1.6,
            color: 'var(--color-text)',
          }}
        >
          {type === 'terms' ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <p>
                <strong>1. Nature of the Software:</strong> Reserve Juggler is a local treasury-policy simulator and deterministic decision evidence viewer developed under accepted scope 0.2.0 (RG-02).
              </p>
              <p>
                <strong>2. Non-Banking Disclaimer:</strong> The software does not operate a commercial bank, credit institution, depository, or investment vehicle. It does not initiate wire transfers, process automated clearing house (ACH) credits, or custody financial instruments.
              </p>
              <p>
                <strong>3. Synthetic Simulation Invariants:</strong> All hourly cashflows, interest accruals, liquidation haircuts, repo locks, and overdraft penalties are synthetic mathematical constructs evaluated against the user-supplied time series (D07 format).
              </p>
              <p>
                <strong>4. No Financial or Solvency Guarantee:</strong> Completion of a simulation run without recorded shortfalls does not constitute evidence of legal solvency, contractual counterparty performance, or regulatory liquidity coverage (LCR/NSFR).
              </p>
              <p>
                <strong>5. Review &amp; Acknowledgment:</strong> Scenarios require explicit local acknowledgment of fictional assumptions before policy backtest execution.
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <p>
                <strong>1. Local Single-Workspace Boundary:</strong> Reserve Juggler runs exclusively within the local host operating system workspace as defined in <code>AUTH_SECURITY.md</code>.
              </p>
              <p>
                <strong>2. Zero Telemetry &amp; External Transmission:</strong> No dataset content, transaction entries, scenario parameters, financial metrics, or user identification details are transmitted to external servers, cloud AI providers, or third-party telemetry collectors.
              </p>
              <p>
                <strong>3. Storage Integrity:</strong> Imported CSV files and exported evidence bundles are stored locally with calculated SHA-256 integrity digests.
              </p>
              <p>
                <strong>4. Role Modes:</strong> Workflow session roles (maker, reviewer, auditor, operator) are bounded to local process execution and are not multi-tenant cloud credentials.
              </p>
            </div>
          )}
        </div>

        <div
          style={{
            padding: 'var(--space-4) var(--space-6)',
            borderTop: '1px solid var(--color-border)',
            display: 'flex',
            justifyContent: 'flex-end',
          }}
        >
          <button className="btn btn-secondary btn-sm" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
