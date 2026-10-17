# BACKEND assignment and integration responsibility

Packet RG02-030A-1.0 | Primary: proposed BACKEND teammate, name unknown

Skill fit: strongest Python/API/ledger contributor. Also **integration and product-acceptance coordinator** among the same three teammates. This is not a fourth role/person. FRONTEND reviews API/security/usability; AI_ML reviews finance/causality/metrics. Both read DESIGN.md. Names/capacity and actual implementation authorization are pending a Phase 04 task.

Owned future paths: backend/app/api/, domain/, services/, storage/, migrations/, backend/tests/, backend dependency lock; HTTP spec custodianship with review. Owned progress docs/module_status/BACKEND.md. Shared integration records only after reviewing other module submissions; do not overwrite peer status.

| Task | Requirements | Modules / dependencies | Acceptance and checks |
|---|---|---|---|
| BE-01 session/API/import/scenario | FR-01/02; NFR-03/07 | API validation, source hashing, scenario versions, session context; canonical contracts before code | AC-01/02/13: invalid/missing/gap/cent/overflow cases, strict typed responses, no path imports; FRONTEND reviewer, AI_ML backup |
| BE-02 ledger/repo/baselines | FR-03/04/05/11; NFR-01 | pure domain cash/lot/debt/obligation engine, conventional adapter gateway; BE-01 + AIM-01 | AC-03/04/05/10: I01–I12 independent fixtures and unavailable adapter; AI_ML reviewer, FRONTEND backup |
| BE-03 stresses/metrics/evidence | FR-06/07/08/09/13 | services/comparison, metrics, decision/export; BE-02 | AC-05/06/07/08: common fingerprint, marked vs usable cash, no return double count, no forgotten unpaid/terminal debt; AI_ML reviewer, FRONTEND backup |
| BE-04 storage/security/lifecycle | FR-10; NFR-02/06/07/08 | SQLite migrations/transactions, worker/idempotency/session/export; BE-01, early integrate BE-02 | AC-09/12/16: wrong role/workspace/origin, stale ETag, retries/cancel/restart, schema migration/restore; FRONTEND reviewer, AI_ML backup |
| BE-05 integrate/release evidence | NFR-03/05/08 | shared spec review, generated-client checks, first slice/E2E, runbook; all core tasks | AC-13/15/16 and all core AC evidence; both teammates review, shared backup; no invented release approval |

First vertical slice is a small reviewed fictional dataset, real conventional replay, real decision trace and honest fallback. No D07 benchmark until finance fixtures pass. Implement actor modes as local workflow, not fabricated banking identities. Require complete acknowledged fictional settings; rights for training remain independent. No optimizer is necessary before a rule baseline is correct; no live account/trade endpoint.

## Integrator duties and conflict resolution

Receive FRONTEND/AI_ML shared-document/contract proposals with impacted requirements and actual checks. Compare packet/version hashes; resolve canonical definitions through DECISIONS.md, obtain both affected reviews, update contracts/design/tests/docs together, then integrate early. Track each role separately; do not absorb their whole module. Assemble evidence for human acceptance, note blocked/untested ACs, and keep risky/model/production changes Proposed if beyond accepted scope. Deliver current status and artifact inventory after each gate.

## Exact starter prompt

“You own BACKEND plus integration coordination for accepted RG-02 scope 0.2.0, packet RG02-030A-1.0. Read mandatory shared docs and BACKEND.md, especially DESIGN, ARCHITECTURE invariants, AUTH_SECURITY and canonical OpenAPI. Start BE-01 and the BE-02 conventional first slice while FRONTEND and AI_ML implement their own modules. Review and integrate their shared changes; do not take over all three. Verify exact finance and failures before D07 results; implement BE-03/04 then coordinate BE-05. No live bank operations, installs/spend outside applicable authorization or false production/model claims. Record own work in docs/module_status/BACKEND.md, update shared records after reviews, and present actual evidence/gaps to the requesting human.”
