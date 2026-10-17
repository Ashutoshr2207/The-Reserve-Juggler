# Stage-appropriate setup and release runbook

Blueprint 1.0 | No application server/build/model exists yet

## Runnable now

From repository root with Python 3.12 available: `python tools/check_blueprint.py`. On this host the verified runtime path is `C:\Users\ASUS\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`; use PowerShell `& '<runtime path>' tools/check_blueprint.py`. Checker/fixtures are documentation verification, not product functionality. See BLUEPRINT_CHECKS.md for actual result and limitations. No dependency installation needed for this check.

## Phase 04 setup (planned; not runnable yet)

FRONTEND creates frontend package/lock and supported Node/build configuration; BACKEND creates Python project/test/lock, API/domain/storage and startup; AI_ML creates conventional adapter and isolated optional experiment requirements. Proposed developer commands **after those files exist**: `python -m venv .venv`, `python -m pip install -r backend/requirements.lock`, `python -m pytest`, `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`; frontend `npm ci --prefix frontend`, `npm run test --prefix frontend -- --run`, `npm run build --prefix frontend`. Owners must replace/verify actual commands and record exact versions rather than copy this as evidence they work. No global installs, cloud or model downloads under this runbook alone.

Use fictional fixtures first. Data file already exists under docs/sources/phase02/; do not alter its bytes. R1 creates runtime data under ignored `work/runtime/`, with a generated workspace ID and settings separate from source. Default loopback, same-origin UI and session bootstrap per AUTH_SECURITY.md. Check session, upload bounds and origin before enabling mutations. No credentials needed for dataset-only flow; real service secrets use approved local config/OS storage, never chat/records.

## Integration/release checklist

1. BACKEND coordinates the first real vertical slice in TEAM_PLAN, with FRONTEND and AI_ML present through their own contributions; check API/client/adapter hashes. Freeze shared baseline after review.
2. Run relevant TST families, schema standards validation and AC checks; record hardware/versions and exact outputs. Confirm baseline works with T disabled/unavailable. All warnings/effective family and synthetic scope visible.
3. Confirm acknowledged fictional settings, matching policy endowments and finite credit, correct first/final repo boundaries, no missing coupon treated as yield. Review W1–W5 and open decisions. No commercial/data-license claim without evidence.
4. Back up DB+raw artifacts/manifests as one local snapshot; migrate copy, verify foreign keys/I01–I12 and record schema version. Startup marks unfinished runs INTERRUPTED; retry as new immutable run.
5. Package app plus supported setup, source/license notes and evidence; exclude secrets, runtime tokens, unapproved data publication and incomplete model artifacts. Local user handoff is not public hosting.
6. BACKEND presents acceptance evidence; FRONTEND reviews interaction/export, AI_ML reviews metrics/fallback. Requesting human decides release within scope. A trained model is excluded if T fails/inconclusive or rights missing.

## Failure and rollback

Stop new runs on invariant/storage failure; preserve source/event evidence and mark run FAILED/INTERRUPTED, never show complete metrics. Cancel worker cooperatively at hour boundary. Restore last verified DB+artifact snapshot and prior locked code together; do not hand-edit ledger financial results or silently drop debt/unpaid obligations. Re-import unchanged data only into a new versioned run. Logs use request/run IDs, no full source/secrets. Confirm backup retention and explicit workspace deletion with OS owner.

Pilot/production require new approved scope, security/tenant/institutional data rights, legal/product/credit terms, controls/recovery/monitoring/support owners and measured capacity/accessibility. No deployment or transaction command is provided because none is authorized or implemented.
