import React, { useState } from 'react';
import { Scenario, ApiError, RoleMode } from '../types/contracts';
import { api, formatMoneyCents, DEFAULT_SETTINGS } from '../client/api';
import { IconReview, IconAlertCircle, IconLock } from '../components/Icons';
import { ErrorSummary } from '../components/ErrorSummary';
import { SyntheticModeNotice } from '../components/SyntheticModeNotice';
import { ReviewDiff } from '../components/ReviewDiff';

interface ScreenReviewProps {
  scenario: Scenario | null;
  roleMode?: RoleMode;
  onScenarioReviewed: (scenario: Scenario) => void;
  onReturnToDraft: () => void;
  onNavigateNext: () => void;
}

export const ScreenReview: React.FC<ScreenReviewProps> = ({
  scenario,
  roleMode = 'maker',
  onScenarioReviewed,
  onReturnToDraft,
  onNavigateNext,
}) => {
  const isOperator = roleMode === 'operator';
  const canReview = roleMode === 'reviewer' || roleMode === 'operator';
  const [actorLabel, setActorLabel] = useState(isOperator ? 'Operator (self-review)' : 'Local Treasury Reviewer');
  const [isReviewing, setIsReviewing] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  if (!scenario) {
    return (
      <div style={{ textAlign: 'center', padding: 'var(--space-12) 0' }}>
        <IconAlertCircle size={40} className="text-warning" />
        <h2 style={{ marginTop: 'var(--space-3)' }}>No Scenario Selected</h2>
        <p className="text-small" style={{ marginTop: 'var(--space-1)', marginBottom: 'var(--space-4)' }}>
          Please configure and submit a scenario draft in S2 before reviewing.
        </p>
        <button className="btn btn-primary" onClick={onReturnToDraft}>
          Go to S2 Scenario Configuration
        </button>
      </div>
    );
  }

  const isReviewed = scenario.status === 'REVIEWED';

  const handleReview = async () => {
    if (!actorLabel.trim()) {
      setError({
        code: 'ASSUMPTIONS_INCOMPLETE',
        message: 'Reviewer actor label cannot be blank.',
        request_id: 'req_local_actor',
        retryable: false,
        details: [{ field: 'actor_label', row: null, message: 'Provide an actor or analyst designation.' }],
      });
      return;
    }

    setIsReviewing(true);
    setError(null);

    try {
      const updated = await api.reviewScenario(scenario.scenario_id, scenario.fingerprint, {
        acknowledge_fictional_assumptions: true,
        actor_label: actorLabel.trim(),
      });
      onScenarioReviewed(updated);
    } catch (err: unknown) {
      setError(err as ApiError);
    } finally {
      setIsReviewing(false);
    }
  };

  // Compute diff vs baseline defaults for ReviewDiff component
  const getDiffs = () => {
    const diffs: Array<{ label: string; current: string; baseline: string }> = [];
    const s = scenario.settings;
    if (s.opening_cash_cents !== DEFAULT_SETTINGS.opening_cash_cents) {
      diffs.push({
        label: 'Opening Cash',
        current: formatMoneyCents(s.opening_cash_cents),
        baseline: formatMoneyCents(DEFAULT_SETTINGS.opening_cash_cents),
      });
    }
    if (s.reserve_floor_cents !== DEFAULT_SETTINGS.reserve_floor_cents) {
      diffs.push({
        label: 'Liquidity Reserve Floor',
        current: formatMoneyCents(s.reserve_floor_cents),
        baseline: formatMoneyCents(DEFAULT_SETTINGS.reserve_floor_cents),
      });
    }
    if (s.credit_limit_cents !== DEFAULT_SETTINGS.credit_limit_cents) {
      diffs.push({
        label: 'Credit Facility Cap',
        current: formatMoneyCents(s.credit_limit_cents),
        baseline: formatMoneyCents(DEFAULT_SETTINGS.credit_limit_cents),
      });
    }
    if (s.bond_units !== DEFAULT_SETTINGS.bond_units) {
      diffs.push({
        label: 'Tier 2 Bond Units',
        current: s.bond_units,
        baseline: DEFAULT_SETTINGS.bond_units,
      });
    }
    if (s.equity_units !== DEFAULT_SETTINGS.equity_units) {
      diffs.push({
        label: 'Tier 3 Equity Units',
        current: s.equity_units,
        baseline: DEFAULT_SETTINGS.equity_units,
      });
    }
    if (s.ordering !== DEFAULT_SETTINGS.ordering) {
      diffs.push({
        label: 'Flow Ordering',
        current: s.ordering,
        baseline: DEFAULT_SETTINGS.ordering,
      });
    }
    return diffs;
  };

  const diffs = getDiffs();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Screen Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--color-primary)', marginBottom: '4px' }}>
          <IconReview size={20} />
          <span style={{ fontSize: '13px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Screen S3</span>
        </div>
        <h1>Scenario Review &amp; Precondition Attestation</h1>
        <p style={{ color: 'var(--color-text-muted)', marginTop: '4px', maxWidth: '840px' }}>
          Inspect immutable scenario revision, verify assumption diffs against default baselines, and attest to fictional bounds (FR-10, AC-02, AC-09).
        </p>
      </div>

      <SyntheticModeNotice />
      <ErrorSummary error={error} onDismiss={() => setError(null)} />

      {/* Revision Fingerprint Bar */}
      <div
        style={{
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--space-6)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 'var(--space-4)',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 600 }}>{scenario.label}</h3>
            <span
              style={{
                fontSize: '12px',
                fontWeight: 600,
                padding: '2px 8px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: isReviewed ? 'var(--color-success-bg)' : 'var(--color-warning-bg)',
                color: isReviewed ? 'var(--color-success)' : 'var(--color-warning)',
                border: `1px solid ${isReviewed ? 'var(--color-success-border)' : 'var(--color-warning-border)'}`,
              }}
            >
              {scenario.status} (REV {scenario.revision})
            </span>
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
            Bound Dataset ID: <code>{scenario.dataset_id}</code>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <span className="text-caption">ETAG PRECONDITION FINGERPRINT</span>
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              backgroundColor: 'var(--color-surface-subtle)',
              padding: '6px 10px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--color-border-subtle)',
              maxWidth: '360px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
            title={scenario.fingerprint}
          >
            {scenario.fingerprint}
          </div>
        </div>
      </div>

      {/* Review Diff Section */}
      <ReviewDiff diffs={diffs} />

      {/* Review & Attestation Box */}
      <div
        style={{
          backgroundColor: isReviewed ? 'var(--color-success-bg)' : 'var(--color-surface)',
          border: `1px solid ${isReviewed ? 'var(--color-success-border)' : 'var(--color-border)'}`,
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--space-6)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-4)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <IconLock size={18} className={isReviewed ? 'text-success' : 'text-primary'} />
          <h3 style={{ fontSize: '16px', fontWeight: 600 }}>
            {isReviewed ? 'Scenario Verified & Acknowledged' : 'Formal Review Attestation & ETag Commit'}
          </h3>
        </div>

        {isReviewed ? (
          <div style={{ fontSize: '14px', color: 'var(--color-success)', lineHeight: 1.5 }}>
            This scenario revision has been formally marked <strong>REVIEWED</strong>. The parameter fingerprint is immutable and locked. Any parameter modification in S2 will automatically fork a new draft revision.
          </div>
        ) : (
          <>
            <p className="text-small" style={{ lineHeight: 1.5 }}>
              Under AC-02 and AC-09, policy comparison runs are blocked until this specific revision has been acknowledged. One-person local review is recorded as self-reviewed and never claimed as external institutional sign-off.
            </p>
            <div style={{ maxWidth: '360px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                Reviewing Analyst / Role Designation
              </label>
              <input
                type="text"
                value={actorLabel}
                onChange={(e) => setActorLabel(e.target.value)}
                placeholder="e.g. Lead Liquidity Analyst"
                required
              />
            </div>
          </>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'var(--space-2)', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
            <button className="btn btn-secondary" onClick={onReturnToDraft}>
              &larr; Return to S2 Scenario Draft
            </button>

            {isReviewed ? (
              <button className="btn btn-primary" onClick={onNavigateNext}>
                Proceed to Policy Comparison (S4) &rarr;
              </button>
            ) : (
              <button
                className="btn btn-primary"
                onClick={handleReview}
                disabled={isReviewing || !canReview}
              >
                {isReviewing ? 'Submitting Precondition Review...' : 'Acknowledge Fictional Scenario (Commit)'}
              </button>
            )}
          </div>
          {!isReviewed && !canReview && (
            <div style={{ fontSize: '12px', color: 'var(--color-warning)', textAlign: 'right' }}>
              Review attestation blocked: Role '{roleMode}' cannot acknowledge scenarios. Reviewer or Operator role required (AUTH_SECURITY.md).
            </div>
          )}
          {isOperator && !isReviewed && (
            <div style={{ fontSize: '11px', color: 'var(--color-text-subtle)', textAlign: 'right' }}>
              Single-person operator session: review_mode=self_review recorded.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
