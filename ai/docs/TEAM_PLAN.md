# Three-person delivery and integration plan

Blueprint 1.0 | Phase 03A assignments issued as files, no tasks dispatched

There are exactly **three proposed teammate roles**; actual names/skills have not been provided. Map strongest UI/TypeScript/accessibility skills to FRONTEND; strongest Python/financial accounting/API skills to BACKEND; strongest statistics/causal evaluation/data skills to AI_ML. If skills differ, user can reassign people without silently changing scope. BACKEND also coordinates integration and product acceptance evidence; there is no fourth coordinator. The human requesting user remains scope/release authority, not an invented engineering hire.

All three implement, write tests and review others. No single coding agent owns all modules. Separate files/packets are in [assignments/INDEX.md](assignments/INDEX.md). FRONTEND owns frontend source/tests, BACKEND owns backend/storage/HTTP specification, AI_ML owns adapter/evaluation source/tests. Shared spec changes go through BACKEND integrator with both affected reviewers. Each owns only module_status/<ROLE>.md; integrator updates common status after review. No teammate progress overwritten by another module's convenience edits.

## First integrated outcome and dependency order

**Delivered now:** contract-only vertical fixture linking upload profile → reviewed fictional scenario → conventional run/result/decision → unavailable-model response. It is schema/relationship evidence only, not a running app, investment result or trained-model demo. Actual check output is in BLUEPRINT_CHECKS.md.

**First Phase 04 application outcome:** all three connect the same 24-hour fictional fixture: FRONTEND imports/displays it; BACKEND validates, versions a scenario, executes cash-only/fixed-repo trace and returns a blocked terminal lock; AI_ML supplies baseline/unavailable adapter and tests causal cutoff. One decision opens in UI with real run provenance; no server/client mock gets called a completed simulation. Pass AC-01/02/03/04/08/10 and contract tests together before expanding to D07 and risky what-if scenarios.

Order: shared contracts + fixture baseline → BE-01 + FE-01 + AIM-01 start together → BE-02 integrates with FE-02, adapter boundary already stable → BE-03/04 + FE-03 + AIM-02/03 → BE-05 release review. Branch T starts alongside first Phase 04 work, initially rights/split/baseline tasks, never blocks app or waits until app finished. No calendar duration commitment without people/time constraints; use dependency gates, not invented deadlines.

## Task index (details authoritative in role assignments)

| Task | Primary | Reviewer / backup | Dependency | Requirement / acceptance |
|---|---|---|---|---|
| FE-01 intake/scenario/review UX | FRONTEND | BACKEND / AI_ML | contracts + DESIGN | FR-01/02/10; AC-01/02/09 |
| FE-02 comparison/evidence screens | FRONTEND | AI_ML / BACKEND | FE-01 + BE-02 + AIM-01 | FR-06/08/09/11/13; AC-05/06/08/10 |
| FE-03 responsive/a11y/E2E | FRONTEND | BACKEND / AI_ML | FE-02 + BE-03/04 | NFR-04/07; AC-12/14/16 |
| BE-01 API/intake/context | BACKEND | FRONTEND / AI_ML | canonical spec | FR-01/02; NFR-03; AC-01/02/13 |
| BE-02 exact ledger/repo/baselines | BACKEND | AI_ML / FRONTEND | BE-01 + AIM-01 | FR-03/04/05; AC-03/04/05/10 |
| BE-03 stress/metrics/evidence | BACKEND | AI_ML / FRONTEND | BE-02 | FR-06/07/08/09/13; AC-05/06/07/08 |
| BE-04 storage/security/lifecycle | BACKEND | FRONTEND / AI_ML | BE-01, integrate BE-02 early | FR-10; NFR-02/06/07; AC-09/12/16 |
| BE-05 integration/release coordination | BACKEND | FRONTEND + AI_ML / shared | all integration gates | NFR-03/05/08; AC-13/15/16 |
| AIM-01 conventional adapter/causality | AI_ML | BACKEND / FRONTEND | adapter schema | FR-11; AC-04/10/13 |
| AIM-02 gated Branch T experiment | AI_ML | BACKEND / FRONTEND | AIM-01 + A09–A12 | FR-12; AC-11; no model mandatory |
| AIM-03 independent result checks/UI provenance | AI_ML | FRONTEND / BACKEND | BE-02/03 + FE-02 | FR-08/09; NFR-01; AC-03/05/08/10 |

## Shared verification and coordination

At first integration, run schema/fixture checks plus real client/server path; after every shared change, compare exported API/client with canonical spec, confirm common hashes and affected AC tests. FRONTEND reviews errors/units and visible trace; BACKEND reviews server invariants/access; AI_ML independently recomputes metrics/causal labels. Review evidence includes actual command, environment, pass/fail and limitations, never “tested” without output.

Before handoff each teammate updates owned status with task/requirement IDs, changed files, versions, checks, unresolved issues, dependency requests and next action. Submit shared edits to proposed BACKEND integrator through a review change/packet; no silent concurrent common-file edits. Integrator records decisions and updates dependent specs/tests atomically. If blocked, continue independent owned tasks and report precise gate; do not hand all three modules to one agent. Phase 03A packets are ready for humans to distribute; this phase has not messaged, recruited or launched teammates.
