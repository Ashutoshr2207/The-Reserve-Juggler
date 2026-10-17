import React, { useState } from 'react';
import { Dataset, ApiError, RoleMode } from '../types/contracts';
import { api } from '../client/api';
import { IconUpload, IconDataset, IconInfo } from '../components/Icons';
import { ErrorSummary } from '../components/ErrorSummary';
import { DatasetCard } from '../components/DatasetCard';

interface ScreenDataProps {
  dataset: Dataset | null;
  roleMode?: RoleMode;
  onDatasetLoaded: (dataset: Dataset) => void;
  onNavigateNext: () => void;
}

export const ScreenData: React.FC<ScreenDataProps> = ({ dataset, roleMode = 'maker', onDatasetLoaded, onNavigateNext }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const canImport = roleMode === 'maker' || roleMode === 'operator';

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      setError({
        code: 'AMOUNT_OUT_OF_RANGE',
        message: 'File size exceeds maximum allowable upload limit of 5 MiB.',
        request_id: 'req_local_size_check',
        retryable: false,
        details: [{ field: 'file', row: null, message: `File size is ${(file.size / (1024 * 1024)).toFixed(2)} MiB.` }],
      });
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const res = await api.importDataset(file);
      onDatasetLoaded(res);
    } catch (err: unknown) {
      setError(err as ApiError);
    } finally {
      setIsUploading(false);
    }
  };

  const handleLoadBenchmark = async () => {
    setIsUploading(true);
    setError(null);
    try {
      const res = await api.getDataset('ds_fixture_d07');
      onDatasetLoaded(res);
    } catch (err: unknown) {
      setError(err as ApiError);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Screen Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--color-primary)', marginBottom: '4px' }}>
          <IconDataset size={20} />
          <span style={{ fontSize: '13px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Screen S1</span>
        </div>
        <h1>Data Intake &amp; Temporal Profile Validation</h1>
        <p style={{ color: 'var(--color-text-muted)', marginTop: '4px', maxWidth: '840px' }}>
          Import and validate hourly gross treasury flows. Conforms to FR-01 and the D07 16-column schema. Preserves canonical SHA-256 byte digests without client-side data mutation.
        </p>
      </div>

      <ErrorSummary error={error} onDismiss={() => setError(null)} />

      {/* File Intake Section */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 'var(--space-4)',
        }}
      >
        {/* Upload Box */}
        <div
          style={{
            backgroundColor: 'var(--color-surface)',
            border: '2px dashed var(--color-border)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--space-6)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            gap: 'var(--space-3)',
          }}
        >
          <div
            style={{
              width: '48px',
              height: '48px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--color-primary-light)',
              color: 'var(--color-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <IconUpload size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--color-text)' }}>Import Treasury CSV</h3>
            <p className="text-small" style={{ marginTop: '2px' }}>
              Standard 16-column D07 schema (max 5 MiB).
            </p>
          </div>
          <label
            className="btn btn-primary"
            style={{ cursor: isUploading || !canImport ? 'not-allowed' : 'pointer', marginTop: 'var(--space-2)', opacity: !canImport ? 0.6 : 1 }}
          >
            {isUploading ? 'Validating...' : 'Select CSV File'}
            <input
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              disabled={isUploading || !canImport}
              style={{ display: 'none' }}
            />
          </label>
          {!canImport && (
            <div style={{ fontSize: '12px', color: 'var(--color-warning)', marginTop: '4px' }}>
              Import restricted: Role '{roleMode}' holds read-only access (AUTH_SECURITY.md).
            </div>
          )}
        </div>

        {/* Benchmark Quick Loader */}
        <div
          style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--space-6)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
              <IconInfo size={18} className="text-primary" />
              <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Standard 2026 D07 Benchmark</h3>
            </div>
            <p className="text-small" style={{ lineHeight: 1.5 }}>
              Use the archived 8,760-hour synthetic benchmark. Features 17:00 repo sweep windows, 08:00 release schedules, Tier 2 bond indices, Tier 3 equities, and overdraft penalty APRs.
            </p>
          </div>
          <div style={{ marginTop: 'var(--space-4)' }}>
            <button
              className="btn btn-secondary"
              onClick={handleLoadBenchmark}
              disabled={isUploading || !canImport}
              style={{ width: '100%' }}
            >
              Load Standard D07 Benchmark Dataset
            </button>
            {!canImport && (
              <div style={{ fontSize: '12px', color: 'var(--color-warning)', marginTop: '4px', textAlign: 'center' }}>
                Benchmark intake restricted for role '{roleMode}'.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Dataset Profile Card (FR-01) */}
      {dataset && (
        <DatasetCard dataset={dataset} onProceed={onNavigateNext} />
      )}
    </div>
  );
};
