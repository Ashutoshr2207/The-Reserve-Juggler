import React, { useState, useEffect } from 'react';
import { Scenario, Run, MetricSet, PolicyId, ForecastMode, ApiError, RoleMode } from '../types/contracts';
import { api } from '../client/api';
import { IconCompare, IconPlay, IconStop } from '../components/Icons';
import { ErrorSummary } from '../components/ErrorSummary';
import { SyntheticModeNotice } from '../components/SyntheticModeNotice';
import { RunStatus } from '../components/RunStatus';
import { ComparisonTable } from '../components/ComparisonTable';

interface ScreenCompareProps {
  scenario: Scenario | null;
  activeRun: Run | null;
  roleMode?: RoleMode;
  onRunCreated: (run: Run) => void;
  onNavigateDecisions: () => void;
}

export const ScreenCompare: React.FC<ScreenCompareProps> = ({
  scenario,
  activeRun,
  roleMode = 'maker',
  onRunCreated,
  onNavigateDecisions,
}) => {
  const canRun = roleMode === 'maker' || roleMode === 'operator';
  const [selectedPolicies, setSelectedPolicies] = useState<PolicyId[]>(['cash_only', 'fixed_repo']);
  const [forecastMode, setForecastMode] = useState<ForecastMode>('baseline');
  const [metrics, setMetrics] = useState<MetricSet | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  // Poll active run if running
  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null;
    if (activeRun && (activeRun.status === 'RUNNING' || activeRun.status === 'QUEUED')) {
      interval = setInterval(async () => {
        try {
          const updated = await api.getRun(activeRun.run_id);
          onRunCreated(updated);
          if (updated.status === 'COMPLETED' || updated.status === 'FAILED' || updated.status === 'CANCELLED') {
            loadMetrics(updated.run_id);
          }
        } catch {
          // ignore transient poll error
        }
      }, 1500);
    } else if (activeRun && activeRun.status === 'COMPLETED' && !metrics) {
      loadMetrics(activeRun.run_id);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [activeRun]);

  const loadMetrics = async (runId: string) => {
    try {
      const data = await api.getRunMetrics(runId);
      setMetrics(data);
    } catch (err: unknown) {
      setError(err as ApiError);
    }
  };

  const handleStartRun = async () => {
    if (!scenario) return;

    if (!canRun) {
      setError({
        code: 'FORBIDDEN',
        message: `Run execution is not permitted for role '${roleMode}'.`,
        request_id: 'req_local_role',
        retryable: false,
        details: [{ field: 'role_mode', row: null, message: 'Maker or Operator role required (AUTH_SECURITY.md).' }],
      });
      return;
    }

    if (scenario.status !== 'REVIEWED') {
      setError({
        code: 'SCENARIO_NOT_REVIEWED',
        message: 'Precondition failed: scenario must be marked REVIEWED before execution.',
        request_id: 'req_local_notreviewed',
        retryable: false,
        details: [{ field: 'scenario_id', row: null, message: 'Attest and acknowledge fictional scenario in S3.' }],
      });
      return;
    }

    setIsExecuting(true);
    setError(null);

    try {
      const run = await api.createRun({
        scenario_id: scenario.scenario_id,
        policy_ids: selectedPolicies,
        forecast_mode: forecastMode,
        adapter_artifact_id: null,
      });
      onRunCreated(run);
    } catch (err: unknown) {
      setError(err as ApiError);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleCancelRun = async () => {
    if (!activeRun) return;
    try {
      const cancelled = await api.cancelRun(activeRun.run_id);
      onRunCreated(cancelled);
    } catch (err: unknown) {
      setError(err as ApiError);
    }
  };

  const isRunning = activeRun?.status === 'RUNNING' || activeRun?.status === 'QUEUED';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Screen Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--color-primary)', marginBottom: '4px' }}>
          <IconCompare size={20} />
          <span style={{ fontSize: '13px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Screen S4</span>
        </div>
        <h1>Deterministic Policy Comparison &amp; Backtest</h1>
        <p style={{ color: 'var(--color-text-muted)', marginTop: '4px', maxWidth: '840px' }}>
          Execute and compare conventional treasury policies against common synthetic cashflows and constraints. Evaluates cash-only baseline vs fixed-floor repo (FR-05, FR-08, AC-05).
        </p>
      </div>

      <SyntheticModeNotice />
      <ErrorSummary error={error} onDismiss={() => setError(null)} />

      {/* Execution Controls */}
      <div
        style={{
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--space-6)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-4)',
        }}
      >
        <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Simulation Run Configuration</h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 'var(--space-4)' }}>
          {/* Policy Selection */}
          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
              Matched Policies to Execute
            </label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={selectedPolicies.includes('cash_only')}
                  disabled
                />
                <span>Mandatory Baseline: <strong>Cash Only (RG-00)</strong></span>
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={selectedPolicies.includes('fixed_repo')}
                  onChange={(e) => {
                    if (e.target.checked) setSelectedPolicies(['cash_only', 'fixed_repo']);
                    else setSelectedPolicies(['cash_only']);
                  }}
                />
                <span>Candidate Policy: <strong>Fixed-Floor Repo Sweeps</strong></span>
              </label>
            </div>
          </div>

          {/* Forecast Adapter Mode */}
          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
              Forecast Adapter Mode
            </label>
            <select
              value={forecastMode}
              onChange={(e) => setForecastMode(e.target.value as ForecastMode)}
              disabled={isRunning}
            >
              <option value="baseline">Causal History Baseline (No Training)</option>
              <option value="disabled">Disabled (Static Reservation Only)</option>
              <option value="experimental">T-EXP Quantile Experiment (Gated)</option>
            </select>
            <span className="text-caption" style={{ display: 'block', marginTop: '4px' }}>
              Causal baseline enforces history-before cutoff; no future leakage.
            </span>
          </div>

          {/* Action Button */}
          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            {isRunning ? (
              <button
                className="btn btn-danger"
                onClick={handleCancelRun}
                style={{ width: '100%' }}
              >
                <IconStop size={16} /> Cancel Running Simulation
              </button>
            ) : (
              <button
                className="btn btn-primary"
                onClick={handleStartRun}
                disabled={isExecuting || scenario?.status !== 'REVIEWED' || !canRun}
                style={{ width: '100%' }}
              >
                <IconPlay size={16} /> Run Policy Comparison
              </button>
            )}
          </div>
        </div>

        {!canRun && (
          <div style={{ fontSize: '12px', color: 'var(--color-warning)', marginTop: '4px' }}>
            Run execution restricted: Role '{roleMode}' holds read-only access (AUTH_SECURITY.md).
          </div>
        )}

        {canRun && scenario?.status !== 'REVIEWED' && (
          <div style={{ fontSize: '13px', color: 'var(--color-warning)', marginTop: '4px' }}>
            Run blocked: Current scenario is in DRAFT. Review and acknowledge in S3 before starting.
          </div>
        )}
      </div>

      {/* Active Run Status & Progress */}
      {activeRun && (
        <RunStatus run={activeRun} canRun={canRun} onRestart={handleStartRun} />
      )}

      {/* Multi-Policy Comparison Table (FR-08) */}
      {metrics && metrics.metrics.length > 0 && (
        <ComparisonTable metrics={metrics} onInspectDecisions={onNavigateDecisions} />
      )}
    </div>
  );
};
