import React from 'react';
import { Run } from '../types/contracts';

interface RunStatusProps {
  run: Run;
  canRun: boolean;
  onRestart: () => void;
}

export const RunStatus: React.FC<RunStatusProps> = ({ run, canRun, onRestart }) => {
  return (
    <div
      style={{
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        padding: 'var(--space-6)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-3)' }}>
        <div>
          <span className="text-caption">ACTIVE SIMULATION RUN</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Run ID: <code>{run.run_id}</code></h3>
            <span
              style={{
                fontSize: '11px',
                fontWeight: 600,
                padding: '2px 8px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor:
                  run.status === 'COMPLETED'
                    ? 'var(--color-success-bg)'
                    : run.status === 'RUNNING'
                    ? 'var(--color-primary-light)'
                    : 'var(--color-warning-bg)',
                color:
                  run.status === 'COMPLETED'
                    ? 'var(--color-success)'
                    : run.status === 'RUNNING'
                    ? 'var(--color-primary)'
                    : 'var(--color-warning)',
              }}
            >
              {run.status}
            </span>
            {run.financial_outcome && (
              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor:
                    run.financial_outcome === 'NO_SHORTFALLS'
                      ? 'var(--color-success-bg)'
                      : 'var(--color-danger-bg)',
                  color:
                    run.financial_outcome === 'NO_SHORTFALLS'
                      ? 'var(--color-success)'
                      : 'var(--color-danger)',
                }}
              >
                {run.financial_outcome === 'NO_SHORTFALLS' ? 'NO SHORTFALLS' : 'SHORTFALLS RECORDED'}
              </span>
            )}
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <span className="text-caption">PROGRESS</span>
          <div style={{ fontSize: '14px', fontWeight: 600 }} className="tabular-nums">
            {run.completed_hours} / {run.total_hours} Hours
          </div>
        </div>
      </div>

      {(run.status === 'CANCELLED' || run.status === 'INTERRUPTED') && (
        <div
          role="status"
          style={{
            backgroundColor: 'var(--color-danger-bg)',
            border: '1px solid var(--color-danger-border)',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--space-3) var(--space-4)',
            margin: 'var(--space-3) 0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 'var(--space-2)',
          }}
        >
          <div>
            <div style={{ fontWeight: 700, color: 'var(--color-danger)', fontSize: '13px', letterSpacing: '0.4px' }}>
              [WATERMARK: INCOMPLETE PARTIAL EXECUTION &bull; {run.status}]
            </div>
            <div style={{ fontSize: '12px', color: 'var(--color-text)', marginTop: '2px' }}>
              Execution terminated at hour {run.completed_hours} of {run.total_hours}. Mid-run resumption is unsupported by design. Partial totals are excluded from policy ranking and export.
            </div>
          </div>
          <button
            className="btn btn-secondary btn-sm"
            onClick={onRestart}
            disabled={!canRun}
          >
            Restart New Clean Replay
          </button>
        </div>
      )}

      {/* Progress Bar */}
      <div
        style={{
          width: '100%',
          height: '8px',
          backgroundColor: 'var(--color-surface-subtle)',
          borderRadius: '4px',
          overflow: 'hidden',
          marginBottom: 'var(--space-3)',
        }}
      >
        <div
          style={{
            width: `${Math.min(100, (run.completed_hours / run.total_hours) * 100)}%`,
            height: '100%',
            backgroundColor: run.status === 'FAILED' ? 'var(--color-danger)' : 'var(--color-primary)',
            transition: 'width 0.3s ease',
          }}
        />
      </div>

      {run.warnings && run.warnings.length > 0 && (
        <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
          {run.warnings.join(' | ')}
        </div>
      )}
    </div>
  );
};
