-- Migration 002: Evidence Ledger, Run Lifecycle and Invariants
DROP TABLE schema_version;
CREATE TABLE schema_version(version INTEGER PRIMARY KEY CHECK(version = 2));
INSERT INTO schema_version VALUES(2);

CREATE TABLE runs(
  workspace_id TEXT NOT NULL REFERENCES workspaces(id),
  id TEXT NOT NULL,
  scenario_id TEXT NOT NULL,
  scenario_fingerprint TEXT NOT NULL,
  contract_version TEXT NOT NULL DEFAULT '0.1.0',
  status TEXT NOT NULL CHECK(status IN ('QUEUED','RUNNING','COMPLETED','FAILED','CANCELLED','INTERRUPTED')),
  financial_outcome TEXT CHECK(financial_outcome IN ('NO_SHORTFALLS','SHORTFALLS')),
  completed_hours INTEGER NOT NULL DEFAULT 0,
  total_hours INTEGER NOT NULL,
  warnings_json TEXT NOT NULL DEFAULT '[]',
  forecast_mode TEXT NOT NULL DEFAULT 'baseline' CHECK(forecast_mode IN ('disabled','baseline','experimental')),
  adapter_artifact_id TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY(workspace_id, id),
  FOREIGN KEY(workspace_id, scenario_id) REFERENCES scenarios(workspace_id, id)
);

CREATE TABLE run_policies(
  workspace_id TEXT NOT NULL,
  run_id TEXT NOT NULL,
  policy_id TEXT NOT NULL CHECK(policy_id IN ('cash_only','fixed_repo')),
  PRIMARY KEY(workspace_id, run_id, policy_id),
  FOREIGN KEY(workspace_id, run_id) REFERENCES runs(workspace_id, id)
);

CREATE TABLE ledger_events(
  workspace_id TEXT NOT NULL,
  run_id TEXT NOT NULL,
  sequence INTEGER NOT NULL,
  policy_id TEXT NOT NULL CHECK(policy_id IN ('cash_only','fixed_repo')),
  origin TEXT NOT NULL,
  event_type TEXT NOT NULL,
  amount_cents TEXT NOT NULL,
  balance_cents TEXT NOT NULL,
  debt_cents TEXT NOT NULL DEFAULT '0',
  unpaid_cents TEXT NOT NULL DEFAULT '0',
  details_json TEXT NOT NULL DEFAULT '{}',
  PRIMARY KEY(workspace_id, run_id, sequence),
  FOREIGN KEY(workspace_id, run_id) REFERENCES runs(workspace_id, id)
);

CREATE TABLE repo_lots(
  workspace_id TEXT NOT NULL,
  run_id TEXT NOT NULL,
  lot_id TEXT NOT NULL,
  policy_id TEXT NOT NULL CHECK(policy_id IN ('cash_only','fixed_repo')),
  principal_cents TEXT NOT NULL,
  rate_apy TEXT NOT NULL,
  entry_time TEXT NOT NULL,
  maturity_time TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('LOCKED','MATURED','EARLY_RELEASED')),
  accrued_interest_cents TEXT NOT NULL DEFAULT '0',
  PRIMARY KEY(workspace_id, run_id, lot_id),
  FOREIGN KEY(workspace_id, run_id) REFERENCES runs(workspace_id, id)
);

CREATE TABLE decisions(
  workspace_id TEXT NOT NULL,
  run_id TEXT NOT NULL,
  decision_id TEXT NOT NULL,
  sequence INTEGER NOT NULL,
  origin TEXT NOT NULL,
  history_before TEXT NOT NULL,
  policy_id TEXT NOT NULL CHECK(policy_id IN ('cash_only','fixed_repo')),
  available_cash_cents TEXT NOT NULL,
  proposed_sweep_cents TEXT NOT NULL,
  result TEXT NOT NULL CHECK(result IN ('ALLOWED','BLOCKED','UNKNOWN')),
  reason_codes_json TEXT NOT NULL,
  effective_family TEXT NOT NULL CHECK(effective_family IN ('disabled','seasonal_baseline','quantile_experiment','sarimax_experiment','pretrained_experiment')),
  quality_label TEXT NOT NULL CHECK(quality_label IN ('illustrative_fixture','computed_simulation')),
  input_hash TEXT NOT NULL,
  PRIMARY KEY(workspace_id, run_id, decision_id),
  FOREIGN KEY(workspace_id, run_id) REFERENCES runs(workspace_id, id)
);

CREATE TABLE metrics(
  workspace_id TEXT NOT NULL,
  run_id TEXT NOT NULL,
  policy_id TEXT NOT NULL CHECK(policy_id IN ('cash_only','fixed_repo')),
  treasury_result_cents TEXT NOT NULL,
  unpaid_new_cents TEXT NOT NULL,
  shortfall_hours INTEGER NOT NULL,
  peak_debt_cents TEXT NOT NULL,
  terminal_wealth_cents TEXT NOT NULL,
  total_cost_cents TEXT NOT NULL,
  PRIMARY KEY(workspace_id, run_id, policy_id),
  FOREIGN KEY(workspace_id, run_id) REFERENCES runs(workspace_id, id)
);

CREATE TABLE metric_sets(
  workspace_id TEXT NOT NULL,
  run_id TEXT NOT NULL,
  scenario_fingerprint TEXT NOT NULL,
  metric_definition_version TEXT NOT NULL DEFAULT '1.0',
  quality_label TEXT NOT NULL CHECK(quality_label IN ('illustrative_fixture','computed_simulation')),
  warnings_json TEXT NOT NULL DEFAULT '[]',
  PRIMARY KEY(workspace_id, run_id),
  FOREIGN KEY(workspace_id, run_id) REFERENCES runs(workspace_id, id)
);

CREATE TRIGGER run_immutable_after_terminal BEFORE UPDATE ON runs
  WHEN OLD.status IN ('COMPLETED','FAILED','CANCELLED')
  BEGIN SELECT RAISE(ABORT, 'immutable terminal run'); END;

CREATE TRIGGER decision_immutable BEFORE UPDATE ON decisions
  BEGIN SELECT RAISE(ABORT, 'immutable decision'); END;

CREATE TRIGGER metric_immutable BEFORE UPDATE ON metrics
  BEGIN SELECT RAISE(ABORT, 'immutable metric'); END;

CREATE TRIGGER ledger_event_immutable BEFORE UPDATE ON ledger_events
  BEGIN SELECT RAISE(ABORT, 'immutable ledger event'); END;
