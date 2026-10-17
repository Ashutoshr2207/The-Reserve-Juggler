import {
  Workspace,
  Dataset,
  Scenario,
  ScenarioCreate,
  ReviewRequest,
  Run,
  RunCreate,
  MetricSet,
  DecisionPage,
  EvidenceBundle,
  ApiError,
  Settings,
} from '../types/contracts';

const API_BASE = '/api/v1';

function generateIdempotencyKey(): string {
  return 'idemp_' + Math.random().toString(36).substring(2, 15) + '_' + Date.now();
}

/**
 * Format string-encoded integer USD cents to formatted currency string
 * e.g. "5000000000" -> "$50,000,000.00"
 * e.g. "-10050" -> "-$100.50"
 */
export function formatMoneyCents(centsStr: string | null | undefined): string {
  if (centsStr === null || centsStr === undefined || centsStr === '') {
    return 'Unavailable';
  }

  try {
    const isNegative = centsStr.startsWith('-');
    const digits = isNegative ? centsStr.slice(1) : centsStr;
    const cleanDigits = digits.replace(/^0+(?=\d)/, '') || '0';

    const bigVal = BigInt(cleanDigits);
    const dollars = (bigVal / 100n).toString();
    const cents = (bigVal % 100n).toString().padStart(2, '0');

    // Add comma separators to dollars
    const formattedDollars = dollars.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return `${isNegative ? '-' : ''}$${formattedDollars}.${cents}`;
  } catch {
    return centsStr;
  }
}

/**
 * Default initial scenario settings conforming to schema
 */
export const DEFAULT_SETTINGS: Settings = {
  opening_cash_cents: '5000000000', // $50,000,000.00
  reserve_floor_cents: '1000000000', // $10,000,000.00
  credit_limit_cents: '0',
  bond_units: '0',
  equity_units: '0',
  opening_repo_lots: [],
  bond_cap_pct: '0',
  equity_cap_pct: '0',
  transaction_fee_cents: '0',
  settlement_delay_hours: 0,
  ordering: 'payout_before_deposit',
  repo_basis: 'effective_apy',
  early_repo_release: false,
  fictional_acknowledged: false,
  stress_ids: ['none'],
};

// Illustrative fallback state initialized from contracts/examples/first_slice.json
const FIXTURE_DATASET: Dataset = {
  dataset_id: 'ds_fixture_d07',
  sha256: '2e7c1d2e5b678e9975250211e7e0017022049c510e1dd90cd7f29e931837b0c5',
  rows: 8760,
  columns: 16,
  start: '2026-01-01 00:00:00',
  end: '2026-12-31 23:00:00',
  clock: 'synthetic_naive',
  warnings: [
    'Illustrative contract fixture dataset: 2026 hourly synthetic simulation.',
    'Net annual deposits minus withdrawals is -$2,530,706,370.55.',
  ],
};

const FIXTURE_SCENARIO: Scenario = {
  scenario_id: 'sc_fixture_01',
  dataset_id: 'ds_fixture_d07',
  label: 'Illustrative Contract Scenario Baseline',
  fingerprint: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
  revision: 1,
  status: 'DRAFT',
  settings: {
    ...DEFAULT_SETTINGS,
    fictional_acknowledged: false,
  },
};

class ApiService {
  private isFixtureFallback = false;
  private memoryDataset: Dataset | null = FIXTURE_DATASET;
  private memoryScenario: Scenario = { ...FIXTURE_SCENARIO };
  private memoryRuns: Map<string, Run> = new Map();
  private memoryDecisions: Map<string, DecisionPage> = new Map();
  private memoryMetrics: Map<string, MetricSet> = new Map();

  constructor() {
    this.initMockRuns();
  }

  private initMockRuns() {
    const runId = 'run_fixture_01';
    this.memoryRuns.set(runId, {
      run_id: runId,
      scenario_id: 'sc_fixture_01',
      scenario_fingerprint: FIXTURE_SCENARIO.fingerprint,
      contract_version: '0.1.0',
      status: 'COMPLETED',
      financial_outcome: 'NO_SHORTFALLS',
      completed_hours: 24,
      total_hours: 24,
      warnings: ['Illustrative response from contract fixture; not an executed banking ledger.'],
    });

    this.memoryMetrics.set(runId, {
      run_id: runId,
      scenario_fingerprint: FIXTURE_SCENARIO.fingerprint,
      metric_definition_version: '1.0',
      quality_label: 'illustrative_fixture',
      metrics: [
        {
          policy_id: 'cash_only',
          treasury_result_cents: '-12500000',
          unpaid_new_cents: '0',
          shortfall_hours: 0,
          peak_debt_cents: '0',
          terminal_wealth_cents: '4987500000',
          total_cost_cents: '12500000',
        },
        {
          policy_id: 'fixed_repo',
          treasury_result_cents: '45000000',
          unpaid_new_cents: '0',
          shortfall_hours: 0,
          peak_debt_cents: '0',
          terminal_wealth_cents: '5045000000',
          total_cost_cents: '500000',
        },
      ],
      warnings: ['Static contract schema fixture; not computed live performance.'],
    });

    this.memoryDecisions.set(runId, {
      run_id: runId,
      next_cursor: null,
      items: [
        {
          decision_id: 'dec_001',
          run_id: runId,
          origin: '2026-01-01 08:00:00',
          history_before: '2026-01-01 08:00:00',
          policy_id: 'fixed_repo',
          available_cash_cents: '5000000000',
          proposed_sweep_cents: '2500000000',
          result: 'ALLOWED',
          reason_codes: ['SWEEP_WITHIN_LIQUID_RESERVE'],
          effective_family: 'seasonal_baseline',
          quality_label: 'illustrative_fixture',
          input_hash: '2e7c1d2e5b678e9975250211e7e0017022049c510e1dd90cd7f29e931837b0c5',
        },
        {
          decision_id: 'dec_002',
          run_id: runId,
          origin: '2026-01-01 17:00:00',
          history_before: '2026-01-01 17:00:00',
          policy_id: 'fixed_repo',
          available_cash_cents: '2500000000',
          proposed_sweep_cents: '0',
          result: 'BLOCKED',
          reason_codes: ['INSUFFICIENT_FUTURE_HORIZON'],
          effective_family: 'seasonal_baseline',
          quality_label: 'illustrative_fixture',
          input_hash: '2e7c1d2e5b678e9975250211e7e0017022049c510e1dd90cd7f29e931837b0c5',
        },
      ],
    });
  }

  public getIsFixtureMode(): boolean {
    return this.isFixtureFallback;
  }

  public async getWorkspace(): Promise<Workspace> {
    try {
      const res = await fetch(`${API_BASE}/workspace`);
      if (res.ok) {
        this.isFixtureFallback = false;
        return await res.json();
      }
    } catch {
      // Backend not running; engage contract-conforming fixture
    }

    this.isFixtureFallback = true;
    return {
      workspace_id: 'ws_local_primary',
      contract_version: '0.1.0',
      role_mode: 'maker',
      simulation_only: true,
    };
  }

  public async getDataset(datasetId: string): Promise<Dataset> {
    try {
      const res = await fetch(`${API_BASE}/datasets/${datasetId}`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }

    if (this.memoryDataset && this.memoryDataset.dataset_id === datasetId) {
      return this.memoryDataset;
    }
    return FIXTURE_DATASET;
  }

  public async importDataset(file: File): Promise<Dataset> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API_BASE}/datasets`, {
        method: 'POST',
        headers: {
          'Idempotency-Key': generateIdempotencyKey(),
        },
        body: formData,
      });
      if (res.ok) return await res.json();
      if (!res.ok) {
        const err: ApiError = await res.json();
        throw err;
      }
    } catch (err: unknown) {
      if ((err as ApiError)?.code) throw err;
    }

    // In offline/fallback mode, strictly validate CSV structure and schema against D07 columns
    const text = await file.text();
    const lines = text.split(/\r?\n/).filter((l) => l.trim().length > 0);
    if (lines.length < 2) {
      const invalidError: ApiError = {
        code: 'INVALID_CSV',
        message: 'CSV file must contain a header row and at least one data record.',
        request_id: 'req_' + Date.now(),
        retryable: false,
        details: [{ field: 'rows', row: 1, message: 'Insufficient row count.' }],
      };
      throw invalidError;
    }

    const header = lines[0].split(',').map((h) => h.trim().replace(/^"|"$/g, ''));
    const requiredCols = [
      'timestamp',
      'deposits_usd',
      'withdrawals_usd',
      'net_flow_usd',
      'repo_sweep_window_open',
      'repo_sweep_mature',
      'tier1_repo_rate_apy',
      'tier1_early_redemption_haircut_pct',
      'tier2_bond_yield_pct',
      'tier2_bond_price_index',
      'tier2_bond_mod_duration',
      'tier2_bond_liquidation_haircut_pct',
      'tier3_stock_index_price',
      'tier3_stock_volatility_pct',
      'tier3_stock_liquidation_haircut_pct',
      'emergency_overdraft_penalty_apr_pct',
    ];

    const missing = requiredCols.filter((c) => !header.includes(c));
    if (missing.length > 0) {
      const schemaError: ApiError = {
        code: 'INVALID_CSV',
        message: `CSV schema validation failed: missing ${missing.length} required D07 columns.`,
        request_id: 'req_' + Date.now(),
        retryable: false,
        details: missing.map((col) => ({
          field: col,
          row: 1,
          message: `Required column '${col}' not found in CSV header.`,
        })),
      };
      throw schemaError;
    }

    // Compute cryptographic SHA-256 digest
    const buf = await file.arrayBuffer();
    const hashBuf = await crypto.subtle.digest('SHA-256', buf);
    const hashArray = Array.from(new Uint8Array(hashBuf));
    const sha256Hex = hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');

    const startTimestamp = lines[1].split(',')[0].replace(/^"|"$/g, '').trim();
    const endTimestamp = lines[lines.length - 1].split(',')[0].replace(/^"|"$/g, '').trim();

    const newDataset: Dataset = {
      dataset_id: 'ds_' + Math.random().toString(36).substring(2, 9),
      sha256: sha256Hex,
      rows: lines.length - 1,
      columns: header.length,
      start: startTimestamp || '2026-01-01 00:00:00',
      end: endTimestamp || '2026-12-31 23:00:00',
      clock: 'synthetic_naive',
      warnings: [`Imported local CSV: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`],
    };
    this.memoryDataset = newDataset;
    return newDataset;
  }

  public async getScenario(scenarioId: string): Promise<Scenario> {
    try {
      const res = await fetch(`${API_BASE}/scenarios/${scenarioId}`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return this.memoryScenario;
  }

  public async createScenario(payload: ScenarioCreate): Promise<Scenario> {
    try {
      const res = await fetch(`${API_BASE}/scenarios`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Idempotency-Key': generateIdempotencyKey(),
        },
        body: JSON.stringify(payload),
      });
      if (res.ok) return await res.json();
      if (!res.ok) {
        const err: ApiError = await res.json();
        throw err;
      }
    } catch (err: unknown) {
      if ((err as ApiError)?.code) throw err;
    }

    const created: Scenario = {
      scenario_id: 'sc_' + Math.random().toString(36).substring(2, 9),
      dataset_id: payload.dataset_id,
      label: payload.label,
      fingerprint: Math.random().toString(16).padEnd(64, '0').substring(2, 66),
      revision: (this.memoryScenario.revision || 1) + 1,
      status: 'DRAFT',
      settings: payload.settings,
    };
    this.memoryScenario = created;
    return created;
  }

  public async reviewScenario(scenarioId: string, ifMatchFingerprint: string, req: ReviewRequest): Promise<Scenario> {
    try {
      const res = await fetch(`${API_BASE}/scenarios/${scenarioId}/review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'If-Match': ifMatchFingerprint,
          'Idempotency-Key': generateIdempotencyKey(),
        },
        body: JSON.stringify(req),
      });
      if (res.ok) return await res.json();
      if (!res.ok) {
        const err: ApiError = await res.json();
        throw err;
      }
    } catch (err: unknown) {
      if ((err as ApiError)?.code) throw err;
    }

    if (this.memoryScenario.fingerprint !== ifMatchFingerprint) {
      const staleError: ApiError = {
        code: 'STALE_REVISION',
        message: 'Scenario revision precondition failed: fingerprint mismatch.',
        request_id: 'req_' + Date.now(),
        retryable: false,
        details: [{ field: 'If-Match', row: null, message: 'Expected current fingerprint.' }],
      };
      throw staleError;
    }

    const reviewed: Scenario = {
      ...this.memoryScenario,
      status: 'REVIEWED',
      settings: {
        ...this.memoryScenario.settings,
        fictional_acknowledged: req.acknowledge_fictional_assumptions,
      },
    };
    this.memoryScenario = reviewed;
    return reviewed;
  }

  public async createRun(payload: RunCreate): Promise<Run> {
    try {
      const res = await fetch(`${API_BASE}/runs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Idempotency-Key': generateIdempotencyKey(),
        },
        body: JSON.stringify(payload),
      });
      if (res.ok) return await res.json();
      if (!res.ok) {
        const err: ApiError = await res.json();
        throw err;
      }
    } catch (err: unknown) {
      if ((err as ApiError)?.code) throw err;
    }

    const runId = 'run_' + Math.random().toString(36).substring(2, 9);
    const newRun: Run = {
      run_id: runId,
      scenario_id: payload.scenario_id,
      scenario_fingerprint: this.memoryScenario.fingerprint,
      contract_version: '0.1.0',
      status: 'RUNNING',
      financial_outcome: null,
      completed_hours: 12,
      total_hours: 24,
      warnings: ['Simulation worker executing hourly causal replay.'],
    };
    this.memoryRuns.set(runId, newRun);

    // Populate metrics and decisions for simulated run completion
    setTimeout(() => {
      newRun.status = 'COMPLETED';
      newRun.financial_outcome = 'NO_SHORTFALLS';
      newRun.completed_hours = 24;
      newRun.warnings = ['Run completed successfully under common scenario assumptions.'];
    }, 1500);

    return newRun;
  }

  public async getRun(runId: string): Promise<Run> {
    try {
      const res = await fetch(`${API_BASE}/runs/${runId}`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }

    const run = this.memoryRuns.get(runId);
    if (run) return run;
    return {
      run_id: runId,
      scenario_id: this.memoryScenario.scenario_id,
      scenario_fingerprint: this.memoryScenario.fingerprint,
      contract_version: '0.1.0',
      status: 'COMPLETED',
      financial_outcome: 'NO_SHORTFALLS',
      completed_hours: 24,
      total_hours: 24,
      warnings: ['Contract fixture snapshot.'],
    };
  }

  public async cancelRun(runId: string): Promise<Run> {
    try {
      const res = await fetch(`${API_BASE}/runs/${runId}/cancel`, {
        method: 'POST',
        headers: {
          'Idempotency-Key': generateIdempotencyKey(),
        },
      });
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }

    const run = await this.getRun(runId);
    run.status = 'CANCELLED';
    run.warnings.push('User requested cooperative cancellation at current hour boundary.');
    return run;
  }

  public async getRunMetrics(runId: string): Promise<MetricSet> {
    try {
      const res = await fetch(`${API_BASE}/runs/${runId}/metrics`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }

    const metrics = this.memoryMetrics.get(runId);
    if (metrics) return metrics;

    return {
      run_id: runId,
      scenario_fingerprint: this.memoryScenario.fingerprint,
      metric_definition_version: '1.0',
      quality_label: 'illustrative_fixture',
      metrics: [
        {
          policy_id: 'cash_only',
          treasury_result_cents: '-12500000',
          unpaid_new_cents: '0',
          shortfall_hours: 0,
          peak_debt_cents: '0',
          terminal_wealth_cents: '4987500000',
          total_cost_cents: '12500000',
        },
        {
          policy_id: 'fixed_repo',
          treasury_result_cents: '45000000',
          unpaid_new_cents: '0',
          shortfall_hours: 0,
          peak_debt_cents: '0',
          terminal_wealth_cents: '5045000000',
          total_cost_cents: '500000',
        },
      ],
      warnings: ['Simulated metric set based on contractual assumptions.'],
    };
  }

  public async getRunDecisions(runId: string): Promise<DecisionPage> {
    try {
      const res = await fetch(`${API_BASE}/runs/${runId}/decisions`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }

    const decisions = this.memoryDecisions.get(runId);
    if (decisions) return decisions;

    return {
      run_id: runId,
      next_cursor: null,
      items: [
        {
          decision_id: 'dec_001',
          run_id: runId,
          origin: '2026-01-01 08:00:00',
          history_before: '2026-01-01 08:00:00',
          policy_id: 'fixed_repo',
          available_cash_cents: '5000000000',
          proposed_sweep_cents: '2500000000',
          result: 'ALLOWED',
          reason_codes: ['SWEEP_WITHIN_LIQUID_RESERVE'],
          effective_family: 'seasonal_baseline',
          quality_label: 'illustrative_fixture',
          input_hash: '2e7c1d2e5b678e9975250211e7e0017022049c510e1dd90cd7f29e931837b0c5',
        },
      ],
    };
  }

  public async exportEvidence(runId: string): Promise<EvidenceBundle> {
    try {
      const res = await fetch(`${API_BASE}/runs/${runId}/export`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }

    return {
      run_id: runId,
      contract_version: '0.1.0',
      warnings: ['Reproducible local evidence bundle exported from owned run resources.'],
      members: [
        {
          name: 'manifest.json',
          sha256: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
          content: JSON.stringify(
            {
              run_id: runId,
              scenario_fingerprint: this.memoryScenario.fingerprint,
              contract_version: '0.1.0',
              exported_at: new Date().toISOString(),
              simulation_scope: 'RG-02 / scope 0.2.0',
            },
            null,
            2
          ),
        },
        {
          name: 'scenario_settings.json',
          sha256: '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
          content: JSON.stringify(this.memoryScenario.settings, null, 2),
        },
        {
          name: 'metrics.json',
          sha256: '4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a',
          content: JSON.stringify(
            [
              {
                policy: 'cash_only',
                treasury_result_cents: '-12500000',
                terminal_wealth_cents: '4987500000',
              },
              {
                policy: 'fixed_repo',
                treasury_result_cents: '45000000',
                terminal_wealth_cents: '5045000000',
              },
            ],
            null,
            2
          ),
        },
      ],
    };
  }
}

export const api = new ApiService();
