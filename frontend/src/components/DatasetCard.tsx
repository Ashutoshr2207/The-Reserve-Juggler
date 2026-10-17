import React from 'react';
import { Dataset } from '../types/contracts';
import { IconCheckCircle } from './Icons';

interface DatasetCardProps {
  dataset: Dataset;
  onProceed?: () => void;
}

export const DatasetCard: React.FC<DatasetCardProps> = ({ dataset, onProceed }) => {
  return (
    <div
      style={{
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-sm)',
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
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <div style={{ color: 'var(--color-success)' }}>
            <IconCheckCircle size={18} />
          </div>
          <h3 style={{ fontSize: '15px', fontWeight: 600 }}>Verified Dataset Profile</h3>
        </div>
        <span
          style={{
            fontSize: '12px',
            fontFamily: 'var(--font-mono)',
            backgroundColor: 'var(--color-surface)',
            padding: '2px 8px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--color-border)',
          }}
        >
          ID: {dataset.dataset_id}
        </span>
      </div>

      <div style={{ padding: 'var(--space-6)' }}>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 'var(--space-4)',
            marginBottom: 'var(--space-6)',
          }}
        >
          <div>
            <span className="text-caption">RECORD COUNT</span>
            <div style={{ fontSize: '18px', fontWeight: 600 }} className="tabular-nums">
              {dataset.rows.toLocaleString()} hours
            </div>
          </div>
          <div>
            <span className="text-caption">COLUMN COUNT</span>
            <div style={{ fontSize: '18px', fontWeight: 600 }} className="tabular-nums">
              {dataset.columns} fields
            </div>
          </div>
          <div>
            <span className="text-caption">START TIMESTAMP</span>
            <div style={{ fontSize: '14px', fontWeight: 500 }} className="tabular-nums">
              {dataset.start}
            </div>
          </div>
          <div>
            <span className="text-caption">END TIMESTAMP</span>
            <div style={{ fontSize: '14px', fontWeight: 500 }} className="tabular-nums">
              {dataset.end}
            </div>
          </div>
        </div>

        <div style={{ marginBottom: 'var(--space-4)' }}>
          <span className="text-caption">SHA-256 INTEGRITY DIGEST</span>
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              backgroundColor: 'var(--color-surface-subtle)',
              padding: '8px 12px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--color-border-subtle)',
              wordBreak: 'break-all',
              marginTop: '4px',
            }}
          >
            {dataset.sha256}
          </div>
        </div>

        {dataset.warnings && dataset.warnings.length > 0 && (
          <div style={{ marginTop: 'var(--space-4)' }}>
            <span className="text-caption" style={{ color: 'var(--color-warning)' }}>
              DATASET AUDIT NOTICES
            </span>
            <ul
              style={{
                margin: 'var(--space-2) 0 0 var(--space-5)',
                fontSize: '13px',
                color: 'var(--color-text-muted)',
              }}
            >
              {dataset.warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {onProceed && (
        <div
          style={{
            padding: 'var(--space-4) var(--space-6)',
            backgroundColor: 'var(--color-surface-subtle)',
            borderTop: '1px solid var(--color-border)',
            display: 'flex',
            justifyContent: 'flex-end',
          }}
        >
          <button className="btn btn-primary" onClick={onProceed}>
            Configure Policy Assumptions (S2) &rarr;
          </button>
        </div>
      )}
    </div>
  );
};
