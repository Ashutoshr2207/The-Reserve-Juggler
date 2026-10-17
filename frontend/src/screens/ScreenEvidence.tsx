import React, { useState, useEffect } from 'react';
import { Run, EvidenceBundle, ApiError } from '../types/contracts';
import { api } from '../client/api';
import { IconEvidence } from '../components/Icons';
import { ErrorSummary } from '../components/ErrorSummary';
import { SyntheticModeNotice } from '../components/SyntheticModeNotice';
import { ExportPanel } from '../components/ExportPanel';

interface ScreenEvidenceProps {
  activeRun: Run | null;
}

export const ScreenEvidence: React.FC<ScreenEvidenceProps> = ({ activeRun }) => {
  const [bundle, setBundle] = useState<EvidenceBundle | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    if (activeRun) {
      loadEvidence(activeRun.run_id);
    }
  }, [activeRun]);

  const loadEvidence = async (runId: string) => {
    setIsExporting(true);
    setError(null);
    try {
      const data = await api.exportEvidence(runId);
      setBundle(data);
    } catch (err: unknown) {
      setError(err as ApiError);
    } finally {
      setIsExporting(false);
    }
  };

  if (!activeRun) {
    return (
      <div style={{ textAlign: 'center', padding: 'var(--space-12) 0' }}>
        <IconEvidence size={40} className="text-muted" />
        <h2 style={{ marginTop: 'var(--space-3)' }}>No Active Simulation Run</h2>
        <p className="text-small" style={{ marginTop: 'var(--space-1)' }}>
          Execute a comparison run to generate reproducible audit evidence.
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Screen Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--color-primary)', marginBottom: '4px' }}>
          <IconEvidence size={20} />
          <span style={{ fontSize: '13px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Screen S6</span>
        </div>
        <h1>Reproducible Evidence &amp; Attestation Bundle</h1>
        <p style={{ color: 'var(--color-text-muted)', marginTop: '4px', maxWidth: '840px' }}>
          Inspect and export cryptographic simulation proof. Packages immutable scenario fingerprints, accounting metrics, and decision traces without leaking out-of-scope files (FR-13, AC-08).
        </p>
      </div>

      <SyntheticModeNotice compact />
      <ErrorSummary error={error} onDismiss={() => setError(null)} />

      {bundle && <ExportPanel bundle={bundle} isExporting={isExporting} />}
    </div>
  );
};
