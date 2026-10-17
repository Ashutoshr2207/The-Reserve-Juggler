# Journeys and state transitions

Blueprint 1.0 | 2026-10-17 | Authoritative lifecycle; screens/states styled in DESIGN.md

## Primary journey J1 — compare a declared fictional policy

Maker opens owned local workspace → S1 imports CSV (FR-01) → dataset ready or explicit validation error → S2 creates a complete fictional scenario (FR-02) → S3 reviewer inspects revision and acknowledges assumptions → S4 creates an immutable run (FR-05) → worker replay emits decision/ledger records (FR-03/04/09) → S4/S5 inspect matched policies and failure states → S6 exports owned completed evidence (FR-13). Baseline works with no trained adapter. First implemented vertical slice is J1 on a small fixture, then D07; scope and checks are in TEAM_PLAN.md.

## Other journeys

J2 change assumption: copy scenario into a new DRAFT revision → diff/review → new run; old run/evidence unchanged. J3 investigate shortfall: select timestamp → show available-before-payout cash, locked lot, debt headroom, unpaid obligations and reason; compare same origin in baseline. J4 model unavailable: adapter responds unavailable/unsupported origin → conventional forecast fallback recorded → core constraints continue. J5 recovery: worker crash → run INTERRUPTED on startup → user creates a new run from the same reviewed snapshot; no blind mid-run continuation. J6 stress: clone scenario into explicitly named stress revision → review → separate run; never overwrite original actuals or benchmark identity.

## State machines

Dataset: received → validating → ready | rejected. Rejected content never becomes a selectable dataset. Duplicate identical source can return its registered dataset ID in the same workspace; no cross-workspace dedup disclosure.

Scenario revision: DRAFT → REVIEWED. Any edited assumption creates a new DRAFT; REVIEWED never mutated. Review records actor label, local review mode, timestamp and revision hash. REVIEWED means fictional-model assumptions acknowledged; it is not institutional policy or legal/data-rights certification. T rights gate is separate.

Run: QUEUED → RUNNING → COMPLETED | FAILED | CANCELLED; QUEUED may cancel; RUNNING becomes INTERRUPTED on process restart. Cancel requested after completion is idempotent and returns terminal state. COMPLETED has outcome NO_SHORTFALLS | SHORTFALLS, never “solvent.” FAILED/INTERRUPTED/CANCELLED partial records cannot enter complete policy ranking. No state is changed by a client dropdown.

Forecast adapter: DISABLED | BASELINE_READY | EXPERIMENT_READY | UNAVAILABLE. Model promotion needs AI_EVALUATION.md gate; disabled/unavailable uses explicit conventional fallback. Run records adapter artifact ID or null and its effective family; no progress animation substitutes for a fit.

## Action ordering at each simulated hour

See invariants/accounting in ARCHITECTURE.md. At start t: release settled eligible previous lots; determine action from information before t; reserve pending amounts and enforce policy; process the declared intra-hour payout/deposit ordering; record settlements/interest and end state. Quote availability is explicitly lagged. Lack of future horizon blocks a new repo lock under conservative terminal rule. Do not consult row t outcomes when deciding at start t. Half-open interval convention and model preprocessing are shared in AI_DESIGN.md.

## Permission/error behavior

Local workflow roles and real security boundary are authoritative in AUTH_SECURITY.md. Invalid draft/review returns 422 or 409 without advancing state; unknown owned resource 404; denied action 403. HTTP status is not a financial outcome: a completed calculation with unpaid obligations returns a valid result with warnings, not a 500. Error envelopes, retries and ETags are defined in API_CONTRACT.md and executable OpenAPI.
