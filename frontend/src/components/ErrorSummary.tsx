import React from 'react';
import { ApiError } from '../types/contracts';
import { IconAlertCircle, IconClose } from './Icons';

interface ErrorSummaryProps {
  error: ApiError | null;
  onDismiss?: () => void;
}

export const ErrorSummary: React.FC<ErrorSummaryProps> = ({ error, onDismiss }) => {
  if (!error) return null;

  return (
    <div
      role="alert"
      aria-live="assertive"
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-2)',
        padding: 'var(--space-4)',
        backgroundColor: 'var(--color-danger-bg)',
        border: '1px solid var(--color-danger-border)',
        borderRadius: 'var(--radius-md)',
        marginBottom: 'var(--space-4)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <div style={{ color: 'var(--color-danger)' }}>
            <IconAlertCircle size={20} />
          </div>
          <span style={{ fontWeight: 600, color: 'var(--color-danger)', fontSize: '14px' }}>
            [{error.code}] {error.message}
          </span>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            aria-label="Dismiss error"
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--color-danger)',
              padding: '2px',
            }}
          >
            <IconClose size={16} />
          </button>
        )}
      </div>

      {error.details && error.details.length > 0 && (
        <ul
          style={{
            margin: 'var(--space-2) 0 0 var(--space-6)',
            fontSize: '13px',
            color: 'var(--color-text)',
          }}
        >
          {error.details.map((d, idx) => (
            <li key={idx} style={{ marginBottom: '4px' }}>
              <strong>{d.field}</strong> {d.row !== null ? `(row ${d.row})` : ''}: {d.message}
            </li>
          ))}
        </ul>
      )}

      <div style={{ display: 'flex', gap: 'var(--space-4)', fontSize: '11px', color: 'var(--color-text-subtle)', marginTop: '4px' }}>
        <span>Request ID: <code>{error.request_id}</code></span>
        <span>Retryable: {error.retryable ? 'Yes' : 'No'}</span>
      </div>
    </div>
  );
};
