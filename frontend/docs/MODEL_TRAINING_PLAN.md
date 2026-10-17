# T-EXP training plan and exact handoff

Blueprint 1.0 | Status: accepted experiment branch, training not started; data/setup gates open

## TRAINING ACTION NEEDED

Start Branch T **alongside Phase 04**, not after app completion. Begin with rights/timing review and conventional adapter/evaluation scaffolding; model fitting waits for A09–A12. Application development proceeds through the no-training adapter. Human/Agent/Hybrid ownership: Human confirms data rights and financial semantics; AI_ML teammate implements/verifies preparation and experiment; BACKEND reviews application/ledger integration; FRONTEND reviews effective-model/fallback display. Actual names/skills are unknown; proposed three-person allocation is in TEAM_PLAN.md.

D07 is locally readable and profiled, but generator/seed/license/commercial and training reuse terms are absent. User requested analysis and accepted a gated experiment, not proof of an upstream license. Ask for rights provenance without requesting secret/customer data in chat. No new dataset download or paid model/API/GPU is required for baseline. No manual labeling of all rows is needed; reviewer checks 50 intervals plus boundaries/exception types for causal labels and liquidity meaning. Optional independent synthetic seed/year remains unavailable.

## Candidate and resource envelope

Baseline: seasonal24/168 + training-only empirical path buffer, no trained weights. First candidate: small CPU quantile regression/gradient boosting, with parameters selected only in development. Secondary SARIMAX if justified within ≤3 families cap. Pretrained Chronos inference remains an optional comparator with separate model access/artifact/license check, not a required download. Deep learning, learned ensembles, fine-tuning, foundation training and RL are no-go for minimum scope. No outcome/accuracy established.

Compute assumption: 4–8 CPU cores, 16GB RAM; max first comparison 8 CPU-hours, no GPU. Labor 16–40h at hypothetical $25–$75/h = $400–$3,000; local incremental compute may be $0, hypothetical rented CPU $0–$8 at $0–$1/h, neither approved spend nor provider quote. Exact machine/runtime capability and installed packages must be measured after setup. Bundled Python has pandas/NumPy; SciPy/sklearn/statsmodels/torch/chronos not available. Phase 04 AI_ML proposes a pinned isolated requirements/lock, BACKEND reviews compatibility; no global installs.

## Handoff tasks

| Task | Deliverable / gate | Primary / reviewer | Requirement / acceptance |
|---|---|---|---|
| T0 | Rights/semantics note, exact source hash, constraints; mark blocked items honestly | Human + AI_ML / BACKEND | FR-02,FR-12 / AC-02,AC-11 |
| T1 | Contract-compliant baseline adapter and causal-feature unit tests | AI_ML / BACKEND | FR-11 / AC-10 |
| T2 | Frozen splits/origin IDs, label/preprocessing manifest per AI_DESIGN; reviewed sample labels | AI_ML / BACKEND | FR-12 / AC-11 |
| T3 | Isolated CPU package lock, module/solver smoke checks; no unapproved downloads | AI_ML / BACKEND | NFR-08 / AC-16 |
| T4 | One capped candidate comparison; saved predictions/labels/evaluation evidence | AI_ML / FRONTEND + BACKEND for ledger metrics | FR-12 / AC-11 |
| T5 | Review pass/inconclusive/no-go and integration impact, keep baseline if no benefit | BACKEND coordinator + AI_ML / FRONTEND | FR-11,FR-12 / AC-10,AC-11 |

Exact teammate prompt: “Implement AI_ML assignment AIM-01 then AIM-02 from docs/assignments/AI_ML.md for accepted RG-02/0.2.0. Read shared contract/design and canonical adapter schema. Start T0/T1 alongside the first Phase 04 slice. Do not fit until rights/timing/runtime gates are recorded. Keep source data unchanged; use causal origins and conventional fallback. Save actual commands, parameters, predictions and failures; never invent accuracy. Submit contract/design changes to BACKEND integrator and your owned status to module_status/AI_ML.md. Do not implement FRONTEND/BACKEND modules or expose live actions.”

Input/output schema and preprocessing are in AI_DESIGN/adapter schema; evaluate exactly AI_EVALUATION protocol and scope gate. No training command exists yet. Future `python -m ai_ml.evaluate --config ...` is a **proposed implementation command**, not runnable now; AI_ML replaces it with actual supported CLI after building/locking, updates README/runbook and records real output. Acceptance of the branch does not require ML in MVP or waive data/financial/release gates.
