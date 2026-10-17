# FRONTEND assignment

Packet RG02-030A-1.0 | Primary: proposed FRONTEND teammate, name unknown

Skill fit: strongest UI/TypeScript/accessibility contributor. Reviewer BACKEND for interface/security, AI_ML for forecast labels; backup AI_ML for review, BACKEND for integration. Read every shared file in INDEX.md, particularly DESIGN.md, before implementation. Current work is assigned/not started; no app source exists.

## Owned module and tasks

Owned future paths: frontend/src/screens/, components/, client/, styles/, frontend/tests/, frontend/package.json and lock. Owned progress: docs/module_status/FRONTEND.md. Do not edit backend/ or ai_ml/ to satisfy a UI test. Shared DESIGN/contracts changes are submitted to BACKEND, not maintained as a frontend fork.

| Task | Requirements | Files / dependencies | Acceptance / actual checks to perform |
|---|---|---|---|
| FE-01 Data, Scenario, Review | FR-01/02/10; NFR-03 | screens/Data,Scenario,Review; typed client/errors. Depends on canonical HTTP and BE-01; fixture-backed UI can start first, labeled mock | AC-01/02/09/13: valid/invalid import, missing settings, stale review and errors; client schema tests; reviewed units; no fake backend validation |
| FE-02 Compare, Decision, Evidence | FR-06/08/09/11/13 | screens/Compare,Decision,Evidence; MoneyCell/timeline/table/export. Depends FE-01 + BE-02/03 + AIM-01 | AC-05/06/08/10: match fingerprint, signed cents, unknown/shortfalls, experimental/unavailable labels; connect actual server slice before D07 |
| FE-03 A11y/responsive/E2E | NFR-04/07/08 | frontend/tests and shared E2E proposals. Depends FE-02 and BE-04 | AC-12/14/16: keyboard/focus/error associations, chart table, zoom/mobile, network recovery, forbidden access, no raw token logs; record build/test/manual results |

For each task FRONTEND is primary; BACKEND reviewer for FE-01/03, AI_ML reviewer for FE-02; the other role is backup. Every task must carry AC evidence before marked complete. No production login or multi-tenant claims. UI formatting never owns arithmetic; do not convert cents strings to unsafe Number values or hide deficit signs. Display run state separately from financial result. Empty/loading/error states must match DESIGN and backend codes.

## First integration handoff

Demonstrate S1→S3 against shared fixture then real local API: no fake uploaded dataset success, no browser-only financial result. Pair with BACKEND to check request/response/version/errors; AI_ML checks fallback label. Submit shared-spec/design edits plus affected req/AC/tests to BACKEND. Update owned status with files, versions, actual commands/output, gaps and next action. Do not modify other modules' progress.

## Exact starter prompt

“You own FRONTEND only for accepted RG-02 scope 0.2.0, packet RG02-030A-1.0. Read docs/assignments/INDEX.md and FRONTEND.md plus shared mandatory docs; both UI and backend must follow DESIGN.md. Implement FE-01 first, coordinating the first real vertical slice with BACKEND and AI_ML. Use canonical OpenAPI and clearly labeled contract fixtures; do not invent computed metrics, backend validation or trained results. Then FE-02/FE-03 in dependency order. Implement and test your module, review assigned peers, and record actual evidence in docs/module_status/FRONTEND.md. Propose shared changes to BACKEND integrator; do not implement all modules, change accepted scope, publish, spend or access private data.”
