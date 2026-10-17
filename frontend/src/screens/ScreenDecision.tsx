import React, { useState, useEffect } from 'react';
import { Run, Decision, ApiError } from '../types/contracts';
import { api } from '../client/api';
import { MoneyCell } from '../components/MoneyCell';
import { IconDecision } from '../components/Icons';
import { ErrorSummary } from '../components/ErrorSummary';
import { SyntheticModeNotice } from '../components/SyntheticModeNotice';
import { DecisionInspector } from '../components/DecisionInspector';

interface ScreenDecisionProps {
  activeRun: Run | null;
  onNavigateEvidence: () => void;
}

export const ScreenDecision: React.FC<ScreenDecisionProps> = ({ activeRun, onNavigateEvidence }) => {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [selectedDecision, setSelectedDecision] = useState<Decision | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    if (activeRun) {
      loadDecisions(activeRun.run_id);
    }
  }, [activeRun]);

  const loadDecisions = async (runId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const page = await api.getRunDecisions(runId);
      setDecisions(page.items);
      if (page.items.length > 0) {
        setSelectedDecision(page.items[0]);
      }
    } catch (err: unknown) {
      setError(err as ApiError);
    } finally {
      setIsLoading(false);
    }
  };

  if (!activeRun) {
    return (
      <div style={{ textAlign: 'center', padding: 'var(--space-12) 0' }}>
        <IconDecision size={40} className="text-muted" />
        <h2 style={{ marginTop: 'var(--space-3)' }}>No Active Simulation Run</h2>
        <p className="text-small" style={{ marginTop: 'var(--space-1)' }}>
          Please execute a policy comparison in S4 to inspect hourly decision records.
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Screen Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--color-primary)', marginBottom: '4px' }}>
          <IconDecision size={20} />
          <span style={{ fontSize: '13px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Screen S5</span>
        </div>
        <h1>Deterministic Decision Inspector &amp; Causal Trace</h1>
        <p style={{ color: 'var(--color-text-muted)', marginTop: '4px', maxWidth: '840px' }}>
          Inspect hourly investment and buffer decisions. Verifies strict start-of-hour information cutoff, sweep allowances, blocked reasons, and forecast adapter provenance (FR-04, FR-09).
        </p>
      </div>

      <SyntheticModeNotice compact />
      <ErrorSummary error={error} onDismiss={() => setError(null)} />

      {/* Main Two-Column Layout */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
          gap: 'var(--space-6)',
          alignItems: 'start',
        }}
      >
        {/* Decisions List / Timeline Table */}
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
            <h3 style={{ fontSize: '15px', fontWeight: 600 }}>Hourly Origin Timeline</h3>
            <span className="text-caption">Showing {decisions.length} recorded events</span>
          </div>

          {isLoading ? (
            <div style={{ padding: 'var(--space-6)', textAlign: 'center', color: 'var(--color-text-muted)' }}>
              Loading decision ledger...
            </div>
          ) : decisions.length === 0 ? (
            <div style={{ padding: 'var(--space-6)', textAlign: 'center', color: 'var(--color-text-muted)' }}>
              No decision records found for this run.
            </div>
          ) : (
            <div style={{ maxHeight: '520px', overflowY: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--color-border)', textAlign: 'left', backgroundColor: 'var(--color-surface)' }}>
                    <th style={{ padding: '8px 12px', fontWeight: 600 }}>Origin Time</th>
                    <th style={{ padding: '8px 12px', fontWeight: 600 }}>Policy</th>
                    <th style={{ padding: '8px 12px', fontWeight: 600 }}>Result</th>
                    <th style={{ padding: '8px 12px', fontWeight: 600, textAlign: 'right' }}>Usable Cash</th>
                  </tr>
                </thead>
                <tbody>
                  {decisions.map((d) => {
                    const isSelected = selectedDecision?.decision_id === d.decision_id;
                    return (
                      <tr
                        key={d.decision_id}
                        onClick={() => setSelectedDecision(d)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            setSelectedDecision(d);
                          }
                        }}
                        tabIndex={0}
                        role="button"
                        aria-label={`Select decision point at ${d.origin}`}
                        style={{
                          borderBottom: '1px solid var(--color-border-subtle)',
                          cursor: 'pointer',
                          backgroundColor: isSelected ? 'var(--color-primary-light)' : 'transparent',
                        }}
                      >
                        <td style={{ padding: '10px 12px', fontWeight: 500 }} className="tabular-nums">
                          {d.origin}
                        </td>
                        <td style={{ padding: '10px 12px' }}>
                          <code>{d.policy_id}</code>
                        </td>
                        <td style={{ padding: '10px 12px' }}>
                          <span
                            style={{
                              fontSize: '11px',
                              fontWeight: 600,
                              padding: '2px 6px',
                              borderRadius: 'var(--radius-sm)',
                              backgroundColor:
                                d.result === 'ALLOWED'
                                  ? 'var(--color-success-bg)'
                                  : d.result === 'BLOCKED'
                                  ? 'var(--color-warning-bg)'
                                  : 'var(--color-surface-subtle)',
                              color:
                                d.result === 'ALLOWED'
                                  ? 'var(--color-success)'
                                  : d.result === 'BLOCKED'
                                  ? 'var(--color-warning)'
                                  : 'var(--color-text-muted)',
                            }}
                          >
                            {d.result}
                          </span>
                        </td>
                        <td style={{ padding: '10px 12px', textAlign: 'right' }}>
                          <MoneyCell cents={d.available_cash_cents} showSignColor={false} />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Decision Inspector Detail Card */}
        {selectedDecision && (
          <DecisionInspector
            decision={selectedDecision}
            onNavigateEvidence={onNavigateEvidence}
          />
        )}
      </div>
    </div>
  );
};
