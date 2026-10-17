import React from 'react';

export interface DiffEntry {
  label: string;
  current: string;
  baseline: string;
}

interface ReviewDiffProps {
  diffs: DiffEntry[];
}

export const ReviewDiff: React.FC<ReviewDiffProps> = ({ diffs }) => {
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
        }}
      >
        <h3 style={{ fontSize: '15px', fontWeight: 600 }}>Assumption Variance Against System Baseline</h3>
      </div>

      {diffs.length === 0 ? (
        <div style={{ padding: 'var(--space-6)', color: 'var(--color-text-muted)', fontSize: '14px' }}>
          All scenario parameters strictly match the standard system baseline defaults.
        </div>
      ) : (
        <div style={{ padding: 'var(--space-4) var(--space-6)', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--color-border)', textAlign: 'left' }}>
                <th style={{ padding: '8px 12px', fontWeight: 600 }}>Parameter</th>
                <th style={{ padding: '8px 12px', fontWeight: 600 }}>Revision Value</th>
                <th style={{ padding: '8px 12px', fontWeight: 600 }}>Baseline Default</th>
              </tr>
            </thead>
            <tbody>
              {diffs.map((d, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--color-border-subtle)' }}>
                  <td style={{ padding: '10px 12px', fontWeight: 500 }}>{d.label}</td>
                  <td style={{ padding: '10px 12px', color: 'var(--color-primary)', fontWeight: 600 }}>{d.current}</td>
                  <td style={{ padding: '10px 12px', color: 'var(--color-text-muted)' }}>{d.baseline}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
