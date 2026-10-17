# Verification plan and actual evidence boundary

Blueprint 1.0 | Tests below are planned unless BLUEPRINT_CHECKS.md says actually run

## Levels and traceability

| Test family | Requirements / acceptance | Required cases | Owner / independent reviewer |
|---|---|---|---|
| TST-01 input/schema | FR-01/02, AC-01/02/13 | D07 dimensions/hash; invalid clock/order/gap/duplicate/nonfinite/bool/cent residual/overflow; missing settings | BACKEND / FRONTEND |
| TST-02 ledger/domain | FR-03/04/05, AC-03/04/05 | I01–I12; no first phantom release; 17→08 lock; terminal boundary; exact debt/fees/unpaid; price/haircut double count; upfront vs settled | BACKEND / AI_ML |
| TST-03 policy/stress | FR-06/07/08, AC-05/06/07 | identical fingerprint/funding; exhausted credit; delayed deposit/maturity; no automatic risky allocation; stale evidence -> unknown | BACKEND / AI_ML |
| TST-04 evidence | FR-09/13, AC-08 | deterministic replay, member hashes, signed amounts, complete warnings; forbidden bundle member/path injection | BACKEND / FRONTEND |
| TST-05 workflow/security | FR-10,NFR-02/06/07, AC-09/12/16 | role matrix; forged header; wrong workspace; CSRF/origin; idempotency same/different payload; stale ETag; cancel/race/restart/queue/storage failures | BACKEND / FRONTEND |
| TST-06 UI/accessibility | NFR-04, AC-14 | every DESIGN state; keyboard only, focus dialogs/errors, screen-reader status/chart table, 200–400% zoom, mobile width, negative and unavailable values | FRONTEND / BACKEND |
| TST-07 adapter | FR-11, AC-04/10/13 | cutoff/origin/horizon/unit/version; short history, unavailable/disabled, timeout, negative forecasts, future row, fallback identity | AI_ML / BACKEND |
| TST-08 model evaluation | FR-12, AC-11 | rights/splits/preprocessing freeze, no future labels, metrics recomputation, paired uncertainty, no-go handling | AI_ML / FRONTEND + BACKEND |
| TST-09 end-to-end | shared AC-01–10/12–16 | real local client/server first slice then D07; conventional path works with model missing; failed run not ranked | all three; BACKEND integrates |
| TST-10 performance/recovery | NFR-05/08, AC-15/16 | declared machine/versions, repeated 8,760-hour baseline timing, forecast warm batch, backup/restore/migration/interrupt smoke | BACKEND / FRONTEND + AI_ML |

Property checks: postings/wealth reconcile, no negative inventory/double maturity, paid + outstanding obligation equals requested totals (accounting for prior balance), matched policies do not diverge through hidden inputs, changed source/assumption/model identity changes run fingerprint. Randomized generated fixtures may supplement hand-reviewed financial examples but must not replace independent answer keys. Stress tests are hypothetical, not bank crises observed in D07.

Contract verification now is `python tools/check_blueprint.py`. It uses only stdlib, validates the declared supported schema subset and cross-record links, and writes an evidence report. It does not run the product, a standards-complete OpenAPI validator, accessibility tests or training. Phase 04 adds an installed standards validator, backend test runner, frontend tests/build and browser/E2E harness under locked dependencies. Exact commands become runnable only when package manifests/source exist; runbook distinguishes them.

Do not write tests merely mirroring one formula and call them validation. Use independent reviewed cases and failure outcomes, especially I09 unpaid/debt/external-flow treatment. Verify no stale success values after a failure and no frontend recomputation hiding backend errors. Repeat broad checks only after shared changes/failure concerns; preserve earlier unaffected actual results.

Release requires mapped AC evidence or explicit accepted deferment within scope; no missing check becomes a green zero. Record unsuccessful runs and missing tooling. Branch T success is governed by scope and AI_EVALUATION; baseline release may proceed without a model if all core gates pass.
