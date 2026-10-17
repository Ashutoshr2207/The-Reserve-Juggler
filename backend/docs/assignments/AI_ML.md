# AI_ML assignment

Packet RG02-030A-1.0 | Primary: proposed AI_ML teammate, name unknown

Skill fit: strongest data/time-series/experimental-method contributor. BACKEND reviews causality/financial integration; FRONTEND reviews evidence labels/readability. Backup review rotates between them. Own future ai_ml/adapter.py, preprocessing/, evaluation/, tests/, experiment config/lock/manifests. Own docs/module_status/AI_ML.md; adapter schema custodianship through integrator review. Never implement FRONTEND/BACKEND as substitute for your handoff.

Read INDEX mandatory docs, AI_DESIGN, AI_EVALUATION, MODEL_TRAINING_PLAN, DATASET_AUDIT/PROFILE, accepted scope Section 7 and A09–A12. Training is optional, currently not run, rights and runtime gates unresolved. No LLM/RAG/agent service required. Start Branch T preparatory work alongside Phase 04 first integration, not after app completion; no fitting merely because the CSV is present.

| Task | Requirements | Files / dependencies | Acceptance and checks |
|---|---|---|---|
| AIM-01 conventional adapter/causal tests | FR-11; NFR-01/03 | ai_ml adapter/preprocess/tests, versioned baseline; shared schema and fixture first | AC-04/10/13: strict t cutoff, short-history/unavailable/fallback identity, time/units/quantiles; BACKEND reviewer, FRONTEND backup |
| AIM-02 T-EXP gates + capped comparison | FR-12; NFR-08 | experiment rights/setup/splits/config/predictions/metrics; AIM-01 + A09–A12 | AC-11/16: record license/access, frozen split, sample labels, pinned CPU runtime; baseline first, at most allowed family/cost cap, no fabricated scores; BACKEND reviewer, FRONTEND backup |
| AIM-03 independent finance/provenance review | FR-08/09; NFR-01/04 | read-only result checker/report tests, reviewed backend outputs, frontend labels; BE-02/03 + FE-02 | AC-03/05/08/10: independently recompute posted results and metrics from saved records, no hidden debt/unpaid/price carry, honest experiment quality; FRONTEND reviewer, BACKEND backup |

Branch T handoff and numeric go/no-go authority are MODEL_TRAINING_PLAN and accepted scope. Contract fixture is not a prediction result. Historical S5 audit scores do not transfer. No future synthetic actuals, current target/net feature, global scaling or test-tuned ensemble. Full-year data was profiled; never call final quarter analyst-blind. No trained model in release if gates fail/inconclusive; keep core usable via baseline.

Before fitting, produce TRAINING ACTION NEEDED record for unresolved rights/setup/semantics, with Human/Agent/Hybrid ownership and exact minimal request; never ask secrets. During experiment retain actual config/versions/origin IDs/predictions/labels/failure metrics and measured latency; no GPU/cloud/model download without specific authority. Submit adapter/evaluation/shared changes through BACKEND, with FRONTEND review of all displayed evidence statuses.

## Exact starter prompt

“You own AI_ML only for accepted RG-02 scope 0.2.0 / T-EXP experiment first, packet RG02-030A-1.0. Read shared/AI/dataset docs and assignment. Implement AIM-01 conventional and unavailable adapters with causal contract tests alongside the first Phase 04 UI/backend slice. Begin T rights/split/setup preparation in parallel; do not fit or download until gates/authority are recorded. If permitted, run only the capped comparison with saved evidence and frozen thresholds; model inclusion is optional. Perform AIM-03 independent finance/provenance review. Update docs/module_status/AI_ML.md with actual checks/gaps and submit shared changes to BACKEND integrator. Do not implement all modules or invent model performance.”
