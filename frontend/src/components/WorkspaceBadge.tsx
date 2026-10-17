import React from 'react';
import { Workspace } from '../types/contracts';
import { IconLock } from './Icons';

interface WorkspaceBadgeProps {
  workspace: Workspace | null;
}

export const WorkspaceBadge: React.FC<WorkspaceBadgeProps> = ({ workspace }) => {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-2)',
        padding: '6px 10px',
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-sm)',
        fontSize: '12px',
        color: 'var(--color-text-muted)',
      }}
    >
      <IconLock size={14} />
      <span>
        Workspace: <strong style={{ color: 'var(--color-text)' }}>{workspace?.workspace_id || 'ws_local'}</strong>
      </span>
      <span style={{ color: 'var(--color-border)' }}>|</span>
      <span>
        Role: <strong style={{ color: 'var(--color-text)' }}>{workspace?.role_mode?.toUpperCase() || 'MAKER'}</strong>
      </span>
      <span style={{ color: 'var(--color-border)' }}>|</span>
      <span
        style={{
          color: 'var(--color-primary)',
          backgroundColor: 'var(--color-primary-light)',
          padding: '1px 6px',
          borderRadius: '2px',
          fontWeight: 600,
          fontSize: '11px',
        }}
      >
        SIMULATION ONLY
      </span>
    </div>
  );
};
