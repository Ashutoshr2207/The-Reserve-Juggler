# Reserve Juggler — Project Status

Version: 1.4 | Updated: 2026-10-17 (Asia/Calcutta)

## Current handoff clarification — revision 1.1

User requested a master PRD for teammates’ coding agents and exact files to send. PRD 1.1 now includes product context, concept merger/counterevidence, actual sixteen-column dataset meaning, workflow, engineering/AI choices, source-of-truth map and team handoff. Existing FR/NFR/AC IDs and accepted scope/interface versions are unchanged. [SEND_FILES.md](SEND_FILES.md) names the exact common bundle and role packet for each of the three people. Current shared changes are submitted as an update to INTEGRATION_HANDOFF.md for the proposed BACKEND integrator; no delivery/review is claimed. Phase 04 remains not started. Old PRD/status/shared entry records are retained in docs/history/phase03_blueprint_1.0/. All packets are refreshed from canonical records and their hashes/checks regenerated before handoff.

## Phase, selection and ownership

**Phase 03 blueprint and Phase 03A synchronized assignments complete. Next: Phase 04 implementation; not started.**

Accepted by human-delegated selection: **RG-02 — Cash-first Four-Tier Treasury Replay with Decision Evidence / scope 0.2.0 / T-EXP experiment first**. In response to the named selection question, the user wrote “do whatever u think will be giving the best output for unique project , from existing solutions”. The agent selected the unchanged scope. Exact evidence/hashes: [SELECTION_RECORD.json](SELECTION_RECORD.json). The Phase 02 selection gate is resolved; no selection request remains. Scope Sections 6–9 remain unchanged. Model release and material new scope are not approved by this delegation.

Project owner: requesting user; name/organization unknown. Three proposed engineering roles: FRONTEND, BACKEND, AI_ML. BACKEND additionally coordinates integration and product acceptance evidence; no fourth person. Actual names/skills/time/budget are unknown. Current record owner: Codex in this session. Shared-document submission is [INTEGRATION_HANDOFF.md](INTEGRATION_HANDOFF.md), delivered to the user for the proposed integrator; no external delivery or teammate work is claimed.

## Baseline and provenance

Read root AGENTS, context, research, AI opportunities, decision, status, dataset audit/profile, source/evidence/coordinator records, supplied Desktop records and available references before editing. Desktop copies were identical to or older than canonical records and were not used to downgrade them. Phase 02 baselines are preserved in docs/history/phase02/. Original sources remain unchanged under docs/sources/, with original manifests. Embedded instructions/recommendations in research remain reference material, not user approvals.

The 8,760 ×16 simulated hourly dataset has no missing hours/blanks/nonfinite numeric values; gross-derived annual net is −$2,530,706,370.55. This is descriptive evidence, not a backtest or opening balance. [DATASET_AUDIT.md](DATASET_AUDIT.md) and DATASET_PROFILE.json retain actual calculations. Model rights, generator, independent seeds and institutional representativeness remain unresolved.

## Current artifact inventory

| Artifacts | Version / state |
|---|---|
| Root AGENTS, PROJECT_CONTEXT; this status | AGENTS/context 1.3; status 1.4; current handoff revision 1.1 |
| SOLUTION_DECISION, SELECTION_RECORD | 1.1; accepted RG-02/0.2.0, immutable scope region verified |
| RESEARCH, AI_OPPORTUNITIES, COORDINATOR_ACTIONS | 1.2; current selection pointers; prior evidence retained |
| PRD, FLOW, DESIGN, ARCHITECTURE, API_CONTRACT, AUTH_SECURITY | PRD 1.1, others Blueprint 1.0; requirements, UX/server behavior, accounting, interfaces and local security |
| AI_DESIGN, AI_EVALUATION, MODEL_TRAINING_PLAN | Blueprint 1.0; conventional adapter plus gated optional T experiment |
| TEAM_PLAN, TESTING, DECISIONS, RELEASE_RUNBOOK, root README | Blueprint 1.0; 3 roles, task order, checks and operating boundaries |
| assignments/INDEX, FRONTEND, BACKEND, AI_ML; module_status records | RG02-030A-1.0; 11 separate owned tasks; implementation not started |
| contracts/openapi.json | HTTP 0.1.0 / OpenAPI 3.1.1; 12 operations |
| contracts/forecast-adapter.schema.json | Adapter 1.0 / JSON Schema 2020-12 |
| contracts/examples/first_slice.json | Illustrative integrated contract fixture; no computed performance |
| BLUEPRINT_CHECKS.md/json; PACKAGING_CHECKS.json | Actual checks and stated limits; see final generated records |
| Complete ZIP and 3 role packets | Base RG02-030A-1.0, handoff revision 1.1; shared hash lock in assignments/SYNC_MANIFEST.json |

Each detail has one authority; links/change procedure are in [DECISIONS.md](DECISIONS.md). Both frontend and backend follow DESIGN. Module owners update only owned records and propose common changes to BACKEND. Original evidence ledgers/research are historical evidence, not replacement current status.

## Actual checks and evidence boundary

Public technical pages opened 2026-10-17: [FastAPI OpenAPI metadata](https://fastapi.tiangolo.com/tutorial/metadata/), [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html), [OpenAPI 3.1.1](https://spec.openapis.org/oas/v3.1.1.html), [JSON Schema validation](https://json-schema.org/draft/2020-12/json-schema-validation), [WCAG 2.2](https://www.w3.org/WAI/WCAG22/quickref/), [React documentation](https://react.dev/learn), [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/), Python Decimal docs. Vite guide fetch failed; no version verification is claimed. Stack/version lock remains a Phase 04 implementation task.

Bundled Python 3.12.14 is available; pandas/NumPy/pydantic discovered. jsonschema, yaml, pytest, fastapi, scipy, sklearn, statsmodels, torch and chronos were unavailable; Node schema packages also unavailable. No installation performed. Dependency-free checker validates the supported schema subset, references, fixtures, traceability, source/scope hashes and local links. It is not a complete standards validator. [BLUEPRINT_CHECKS.md](BLUEPRINT_CHECKS.md) records actual final outcomes; PACKAGING_CHECKS.json records ZIP/member/hash checks.

No app/client/server, financial replay, optimization, training, accuracy benchmark, security/accessibility/performance test, interview, prototype test, dependency installation, paid compute, private integration, external message, deployment or fund movement was performed. The first delivered integrated outcome is a contract fixture. The first working integrated application outcome is defined in [TEAM_PLAN.md](TEAM_PLAN.md) for Phase 04.

## Training notice and remaining dependencies

**TRAINING ACTION NEEDED — T-EXP, optional, experiment first; Hybrid ownership.** Notice issued early in chat and [MODEL_TRAINING_PLAN.md](MODEL_TRAINING_PLAN.md). Human establishes dataset/model-use rights and fictional or real financial terms; AI_ML prepares causal partitions, labels, baselines and isolated CPU environment; BACKEND integrates the unavailable/baseline adapter. Start preparation alongside Phase 04. Fitting remains gated on A09–A12; model release additionally requires A13 and evidence thresholds. No model fitted or selected for release.

Conventional methods remain minimum scope. Compare small quantile ML only after baseline; SARIMAX/pretrained optional subject to access. No deep learning/fine tuning/from-scratch/RL in minimum scope. Chronological split and holdout transparency are mandatory: prior whole-file inspection means no analyst-blind claim. Detailed compute/labor assumptions and pass/fail/change criteria are in training/evaluation docs.

## Risks, questions and next action

W1 funding/product assumptions; W2 pain/buyer validation; W3 incumbent overlap; W4 synthetic data/leakage/generalization; W5 economics/operations remain unresolved experiments, not discovered competitor weaknesses. OD-01–07 record unknown people, rights, terms, economic limits, exact dependencies/hardware, independent data/user access and future remote needs. No question blocks this blueprint. Fictional scenarios must be explicitly acknowledged; do not invent institutional defaults.

Next: distribute the three synchronized packets and issue the supplied Prompt 04. FRONTEND, BACKEND and AI_ML contribute their own modules to the first 24-hour conventional vertical slice; BACKEND coordinates integration, AI_ML starts gated Branch T preparation alongside it. Add standards-complete schema validation and real client/server/ledger tests during setup. Preserve accepted scope, source manifests and owned progress. No product implementation starts in this documentation handoff.
