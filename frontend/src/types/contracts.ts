/**
 * Authoritative TypeScript representations of OpenAPI 3.1.1 contracts
 * Source: contracts/openapi.json
 */

export type RoleMode = 'operator' | 'maker' | 'reviewer' | 'auditor';

export interface Workspace {
  workspace_id: string;
  contract_version: '0.1.0';
  role_mode: RoleMode;
  simulation_only: true;
}

export interface Dataset {
  dataset_id: string;
  sha256: string;
  rows: number;
  columns: number;
  start: string;
  end: string;
  clock: 'synthetic_naive';
  warnings: string[];
}

export interface RepoLotInput {
  principal_cents: string;
  entry_time: string;
  maturity_time: string;
  entry_rate_pct: string;
}

export type FlowOrdering = 'payout_before_deposit' | 'netted_end_hour';
export type RepoBasis = 'effective_apy' | 'simple_apr';
export type StressId = 'withdrawal_shock' | 'deposit_delay' | 'late_maturity' | 'denied_credit' | 'none';

export interface Settings {
  opening_cash_cents: string;
  reserve_floor_cents: string;
  credit_limit_cents: string;
  bond_units: string;
  equity_units: string;
  opening_repo_lots: RepoLotInput[];
  bond_cap_pct: string;
  equity_cap_pct: string;
  transaction_fee_cents: string;
  settlement_delay_hours: number;
  ordering: FlowOrdering;
  repo_basis: RepoBasis;
  early_repo_release: boolean;
  fictional_acknowledged: boolean;
  stress_ids: StressId[];
}

export interface ScenarioCreate {
  dataset_id: string;
  label: string;
  settings: Settings;
}

export type ScenarioStatus = 'DRAFT' | 'REVIEWED';

export interface Scenario {
  scenario_id: string;
  dataset_id: string;
  label: string;
  fingerprint: string;
  revision: number;
  status: ScenarioStatus;
  settings: Settings;
}

export interface ReviewRequest {
  acknowledge_fictional_assumptions: true;
  actor_label: string;
}

export type PolicyId = 'cash_only' | 'fixed_repo';
export type ForecastMode = 'disabled' | 'baseline' | 'experimental';

export interface RunCreate {
  scenario_id: string;
  policy_ids: PolicyId[];
  forecast_mode: ForecastMode;
  adapter_artifact_id: string | null;
}

export type RunStatusType = 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED' | 'INTERRUPTED';
export type FinancialOutcome = 'NO_SHORTFALLS' | 'SHORTFALLS' | null;

export interface Run {
  run_id: string;
  scenario_id: string;
  scenario_fingerprint: string;
  contract_version: '0.1.0';
  status: RunStatusType;
  financial_outcome: FinancialOutcome;
  completed_hours: number;
  total_hours: number;
  warnings: string[];
}

export interface Metric {
  policy_id: PolicyId;
  treasury_result_cents: string;
  unpaid_new_cents: string;
  shortfall_hours: number;
  peak_debt_cents: string;
  terminal_wealth_cents: string;
  total_cost_cents: string;
}

export type QualityLabel = 'illustrative_fixture' | 'computed_simulation';

export interface MetricSet {
  run_id: string;
  scenario_fingerprint: string;
  metric_definition_version: '1.0';
  quality_label: QualityLabel;
  metrics: Metric[];
  warnings: string[];
}

export type DecisionResult = 'ALLOWED' | 'BLOCKED' | 'UNKNOWN';
export type EffectiveFamily =
  | 'disabled'
  | 'seasonal_baseline'
  | 'quantile_experiment'
  | 'sarimax_experiment'
  | 'pretrained_experiment';

export interface Decision {
  decision_id: string;
  run_id: string;
  origin: string;
  history_before: string;
  policy_id: PolicyId;
  available_cash_cents: string;
  proposed_sweep_cents: string;
  result: DecisionResult;
  reason_codes: string[];
  effective_family: EffectiveFamily;
  quality_label: QualityLabel;
  input_hash: string;
}

export interface DecisionPage {
  run_id: string;
  items: Decision[];
  next_cursor: string | null;
}

export interface EvidenceMember {
  name: string;
  sha256: string;
  content: string;
}

export interface EvidenceBundle {
  run_id: string;
  contract_version: '0.1.0';
  members: EvidenceMember[];
  warnings: string[];
}

export type ApiErrorCode =
  | 'UNAUTHORIZED'
  | 'FORBIDDEN'
  | 'NOT_FOUND'
  | 'INVALID_CSV'
  | 'ASSUMPTIONS_INCOMPLETE'
  | 'SCENARIO_NOT_REVIEWED'
  | 'STALE_REVISION'
  | 'IDEMPOTENCY_CONFLICT'
  | 'UNSUPPORTED_VERSION'
  | 'AMOUNT_OUT_OF_RANGE'
  | 'RUN_NOT_COMPLETE'
  | 'QUEUE_FULL'
  | 'INTERNAL_ERROR';

export interface ApiErrorDetail {
  field: string;
  row: number | null;
  message: string;
}

export interface ApiError {
  code: ApiErrorCode;
  message: string;
  request_id: string;
  retryable: boolean;
  details: ApiErrorDetail[];
}
