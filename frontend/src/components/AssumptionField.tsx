import React from 'react';

interface AssumptionFieldProps {
  id?: string;
  label: string;
  unit?: string;
  preview?: React.ReactNode;
  helpText?: string;
  error?: string;
  disabled?: boolean;
  children: React.ReactNode;
}

export const AssumptionField: React.FC<AssumptionFieldProps> = ({
  id,
  label,
  unit,
  preview,
  helpText,
  error,
  children,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <label htmlFor={id} style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text)' }}>
          {label} {unit && <span style={{ color: 'var(--color-text-muted)', fontWeight: 400 }}>({unit})</span>}
        </label>
        {preview && (
          <span className="text-caption" style={{ color: 'var(--color-text-muted)' }}>
            {preview}
          </span>
        )}
      </div>

      <div>{children}</div>

      {helpText && !error && (
        <span className="text-caption" style={{ color: 'var(--color-text-subtle)', lineHeight: 1.3 }}>
          {helpText}
        </span>
      )}

      {error && (
        <span style={{ fontSize: '12px', color: 'var(--color-danger)', fontWeight: 500 }}>
          {error}
        </span>
      )}
    </div>
  );
};
