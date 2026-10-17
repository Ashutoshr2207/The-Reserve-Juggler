> Historical BE-01 setup snapshot. For the current BE-01–05 runtime, schema 3,
> verified commands and recovery instructions, use [RUNNING.md](../../RUNNING.md)
> and [current backend status](BACKEND.md). The earlier Desktop path below is
> historical and must not be used as this checkout's location.

# BE-01 setup and migration notes

Version 1.0.0 | Phase 04 / BE-01 | 2026-10-17 (Asia/Calcutta)

Run from `C:\Users\ASUS\OneDrive\Desktop\LiqProof\backend`. This is intake/review only; shared RELEASE_RUNBOOK is the unchanged blueprint.

## Runtime and launch

Verified Python 3.12.14, SQLite 3.53.1; exact package versions in requirements.lock. Bundled ensurepip failed, but the venv executable was created and uv installed packages successfully. Recreate without ensurepip:

```powershell
& 'C:\Users\ASUS\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv --without-pip .venv
uv pip sync --python .venv/Scripts/python.exe --cache-dir work/uv-cache requirements.lock
.venv/Scripts/python.exe -m pytest -q --tb=short
.venv/Scripts/python.exe -m app.main
```

uv must already be available; alternatively use a Python 3.12 venv with working pip to install requirements.lock. The pinned environment was installed/tested; a clean sync reinstall was not separately repeated. Registry access is required. Restricted execution stalled in Windows asyncio's local socketpair before any request; recorded passing tests used reviewed local-socket permission. No global installation, account, database service, model or GPU is required.

Launcher: 127.0.0.1 only, one process, proxy trust/access logging disabled. Opens a one-use local capability in a browser URL fragment, exchanges it by same-origin POST, then clears history. No token is printed/saved. Session confirmation page is infrastructure, not the product UI. Restart launcher after consumed/failed bootstrap, logout or idle expiry.

Trusted startup variables, owned by the OS operator: RG_PORT (default 8000); RG_ROLE_MODE (operator/maker/reviewer/auditor, default operator); optional RG_FRONTEND_ORIGIN (exact localhost/127.0.0.1 HTTP origin, no wildcard). Runtime remains in ignored backend/work/runtime. .env is ignored but not automatically loaded. No secret values belong in chat/docs.

## Local lifecycle proposal for FRONTEND review

These infrastructure routes satisfy AUTH_SECURITY's local lifecycle but are **outside canonical HTTP 0.1.0**; see G1 in MODULE-HANDOFF:

1. Launcher opens GET /local/session with a fragment capability; page POSTs /local/bootstrap with exact local Origin and JSON capability. Successful 204 sets rg_session (HttpOnly, SameSite=Strict) and returns X-CSRF-Token.
2. Authenticated GET /local/csrf returns 204 + X-CSRF-Token for the frontend to keep in memory.
3. Mutations require cookie credentials, allowed Origin, X-CSRF-Token and Idempotency-Key; review also sends the **bare 64-hex fingerprint** in If-Match, matching the current machine authority. ETag is likewise bare; quoted standard HTTP tags require shared revision G2.
4. POST /local/logout requires Origin/CSRF and revokes cookie/token. Eight hours idle or process restart revoke it. Local role comes only from trusted startup; actor text is display metadata.

Use the same hostname for frontend and backend (127.0.0.1 on both is suitable) so SameSite works; configure the exact dev origin. Browser integration/a11y and the actual frontend have not been tested. Loopback HTTP is the accepted local boundary; remote auth/HTTPS is later scope.

## API, validation and retry

Six implemented operations: workspace GET; dataset POST/GET; scenario POST/GET; scenario review POST, under /api/v1. Validators read contracts/openapi.json directly, with no second DTO specification. app.openapi() exports only that canonical subset; remaining run operations are absent and return typed NOT_FOUND. Swagger/CDN routes are disabled.

CSV: sixteen unique D07 names (any column order), UTF-8/BOM, preserved bytes/hash, contiguous unique whole hours; case-sensitive True/False flags match 17:00/08:00. Exact-cent gross/supplied net values fit int64, gross flows nonnegative; canonical net derives from gross, supplied residual ≤1 cent. Plain finite decimal rates are nonnegative; prices positive; haircuts 0–100. One file only, source ≤5 MiB, total multipart overhead ≤64 KiB, generated temporary/storage names. Reject paths/URLs/archives, malformed/extra parts, NUL/nonfinite/formula-like values. Rejected temporary files are removed; errors use field/row without echoing source contents or paths.

JSON ≤64 KiB, duplicate keys/nonfinite/undeclared fields rejected. All settings required; no hidden financial defaults. Fictional acknowledgment required, combined risky caps ≤100, nonnegative units with ≤8 decimals. Initial risky units must be zero because no pre-origin marks are supplied. Opening repo lots need positive principal, nonnegative entry rate, prior 17:00 entry and unexpired next-08:00 maturity; duplicates disallowed. Opening endowment plus credit fits int64. Financial infeasibility is not preemptively hidden by these input checks.

Each scenario POST creates an independent immutable draft (revision=1); changed settings create new ID/fingerprint. Contract lacks parent/edit inputs (G3). Fingerprint binds source/settings/version; label is display text. Review stores actual self_review/local_reviewer mode, actor label/hash and UTC time. Response lacks provenance fields (G4); frontend must not infer independent approval from the actor label or current role.

Idempotency is workspace + operation + key for 24h; review scope includes resource ID and If-Match payload. Response/status/ETag and mutation commit transactionally; JSON canonicalization ignores key order/whitespace, CSV identity uses raw SHA-256. Same committed key/content returns the original response snapshot, even DRAFT after subsequent review; different parsed content returns 409. Invalid/uncommitted operations roll back reservations and can be corrected. Retries still require current session/role. SQLite writes serialize (5s busy timeout); operational storage failures are redacted retryable 503, other unexpected failures nonretryable 503. Follow canonical retry limits: mutation once with same key for transport/503, never blind retry 403/404/409/422.

## Persistence, migration and recovery

Startup applies migrations/001_initial.sql transactionally to an empty DB, then verifies version/FKs; version 1 is not reapplied. Unknown/newer/unversioned DBs fail closed. No financial tables/later migrations exist. Every connection enables foreign keys; composite workspace relations, source/idempotency uniqueness and immutability triggers protect current records.

Source is fsynced to a generated temporary file, atomically moved to work/runtime/<workspace>/raw/<sha256>.csv, then metadata commits. Startup rehashes referenced sources and fails on corruption/missing bytes. A crash after file move but before commit may leave an unreferenced raw file; it never becomes selectable, and same-source retry verifies/reuses it safely. No cross-file/DB atomicity, power-loss, full-disk chaos or directory-fsync guarantee is claimed.

Before future upgrades, **stop the launcher** and copy the entire work/runtime directory to a new unique backend/work/backups snapshot, retaining matching code/lock. Never copy just metadata or copy while writes continue. Offline copy/restore was tested, including SQLite integrity/FK and raw-hash checks. Preserve failed runtime, restore snapshot into a separate backend work directory and verify using create_app(Config(runtime=Path(...))) with matching code; replace actual runtime only under OS-owner authority. No reverse migration, hand-edited ledger, deletion API or timed purge exists. Backups may retain source data.

## Pending verification

See [verification](../../outputs/BE-01-VERIFICATION.json) and [JUnit](../../outputs/BE-01-tests.xml). D07 absent: obtain unchanged authorized CSV inside backend and verify SHA-256 2e7c1d2e5b678e9975250211e7e0017022049c510e1dd90cd7f29e931837b0c5 before import; expected 8,760×16, 2026-01-01 00:00:00→2026-12-31 23:00:00. This acceptance is pending.

No financial replay/invariant checks, AI inference, generated frontend client, browser/E2E, D07 timing or peer review was run. Module checks alone do not sign off whole AC-01/09/12/13/16 or release. Mechanism references checked 2026-10-17: [FastAPI middleware](https://fastapi.tiangolo.com/advanced/middleware/), [jsonschema](https://python-jsonschema.readthedocs.io/en/stable/validate/). Attempted Starlette requests page fetch failed; pinned installed code and tests provide implementation evidence.
