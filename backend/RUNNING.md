# Run the backend

Version 3.0.0 | 2026-10-18 (Asia/Calcutta) | BE-01 through BE-05 backend delivery

This is the current implementation entry point. Packet README, shared status and
blueprint documents remain frozen under the 37-file synchronization manifest;
their “not implemented” text describes the earlier packet. Current evidence and
integration limits are in [BACKEND status](docs/module_status/BACKEND.md) and
[BE-05 handoff](docs/module_status/MODULE-HANDOFF-BE-05.md).

## Setup and launch

Use Python 3.12 and a local checkout. Run from this `backend` directory:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.lock
.venv/Scripts/python.exe -m app.main
```

If the bundled interpreter lacks pip, use an already installed `uv`:

```powershell
python -m venv --without-pip .venv
uv pip sync --python .venv/Scripts/python.exe --link-mode=copy requirements.lock
```

All 39 versions are pinned. This session recreated the isolated environment from
the existing offline uv cache and ran the suite in it. No global packages, model
downloads or services are needed. Registry access is needed if packages are not
cached. Keep a short checkout path on Windows if long paths are disabled.

The launcher binds only `127.0.0.1:8000`, opens `/local/session` with a one-use
fragment capability, exchanges it for an HttpOnly SameSite=Strict cookie and
clears the fragment. Tokens are never printed. This page initializes the session;
the product frontend is delivered separately. The API alone does not render the
product dashboard. Documentation/CDN routes are disabled.

Startup variables: `RG_PORT` (1–65535, default 8000), `RG_ROLE_MODE`
(`operator`, `maker`, `reviewer`, `auditor`; default operator), and optional
`RG_FRONTEND_ORIGIN` (exact HTTP loopback origin, no wildcard). These are trusted
OS settings; request headers cannot select a role or workspace. `.env` is ignored
and is not loaded automatically. Runtime is `work/runtime`; no credentials needed.

## Client workflow

1. Bootstrap using the launcher. The browser obtains CSRF using authenticated
   `GET /local/csrf` and keeps `X-CSRF-Token` in memory. `POST /local/logout`
   requires Origin/CSRF and revokes the session. Restart and 8h idle also revoke it.
2. Use credentialed requests and the same hostname for frontend/backend. Send the
   exact allowed Origin and CSRF on mutations; use one Idempotency-Key per intended
   mutation, reusing it for an ambiguous retry.
3. Import one UTF-8 CSV (maximum 5 MiB, sixteen D07 columns), create a complete
   acknowledged fictional scenario, review its exact **bare 64-hex** ETag using
   If-Match, then create a run. Changed assumptions create a new immutable draft.
4. `POST /api/v1/runs` returns **202 / QUEUED**. Poll the returned run ID every
   1–5 seconds until terminal. One worker executes, with at most five waiting runs;
   a full queue returns 503 QUEUE_FULL with Retry-After. Financial shortfalls can
   be a valid COMPLETED result and remain visible in metrics.
5. Cancellation is immediate for queued work and cooperative at an hour boundary
   for running work. Poll after cancellation acknowledgement. Cancellation racing
   completion preserves whichever terminal transaction commits first. Idempotent
   retries return the original response snapshot; poll for current state.
6. Metrics, decisions and export require COMPLETED. Other states return typed
   409 RUN_NOT_COMPLETE. Decision pages accept limit 1–200 and an opaque cursor
   tied to the run and current session; discard cursors after restart/logout.
7. Export contains only the selected run's eleven JSON members: scenario, dataset
   profile/hash, review mode, engine/source identities, accounting, metrics,
   decisions, lot lifecycles, ledger, comparison and manifest. Raw CSV is retained
   locally; replay requires the same permitted source bytes. Hashes provide
   internal integrity; exports are **unsigned**, with no external reserve claim.

The canonical HTTP 0.1.0 and adapter 1.0 files are unchanged. The generated Python
integration client is `app/api/generated_client.py`; regenerate with
`python tools/generate_client.py`, or check using `--check`. FRONTEND still owns
its actual generated TypeScript client and browser integration.

## Check and recover

```powershell
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests
.venv/Scripts/python.exe tools/generate_client.py --check
.venv/Scripts/python.exe tools/verify_backend.py --repeats 3
.venv/Scripts/python.exe tools/verify_export.py outputs/BE-05-example-export.json
```

The verification command writes JUnit, a dated machine/version/source-hash report,
three year-volume timings and an example export under `outputs`. Its generated
year is a **synthetic surrogate**, not D07. An authorized source can be supplied
using `--dataset <local CSV>`; only the recorded original SHA-256 establishes D07
identity. This performs replay, not training. The Starlette/httpx test-client
deprecation warning is recorded; no package upgrades were introduced to hide it.

Stop the launcher before backup or migration. These commands acquire the same OS
runtime lock as the server and reject an active runtime or existing destination:

```powershell
.venv/Scripts/python.exe -m app.maintenance backup work/runtime work/backups/pre-upgrade
.venv/Scripts/python.exe -m app.maintenance verify work/backups/pre-upgrade
.venv/Scripts/python.exe -m app.maintenance restore work/backups/pre-upgrade work/restored
```

Preserve code and requirements.lock with the snapshot. Backups copy the offline
database and referenced raw files together, verify SQLite integrity/foreign keys
and every source digest, and include a snapshot manifest. Restore to a new path;
never overwrite a failed runtime. The operator may test a restored directory with
`create_app(Config(runtime=Path(...)))`; use matching code before replacing the
normal runtime. All maintenance paths must remain below backend/work. Snapshots
retain source data; no timed purge, deletion API or reverse migration exists.

Schema 3 upgrades 1/2 transactionally. Unsupported versions fail closed. Startup
marks abandoned QUEUED/RUNNING jobs INTERRUPTED; it never resumes a partial
financial replay. Start a new run from the reviewed scenario. Evidence checkpoints
commit every 24 hours per policy and remain incomplete after cancellation/failure.
Complete metrics/reports/lots and terminal success commit atomically. Earlier
BE-03 results retain their legacy identity and are not retroactively recalculated.

The OS account is the local security boundary. This is a synthetic backend
prototype; whole-product release still needs peer review, frontend/browser and
accessibility evidence, original-D07 acceptance and human acceptance. No live
banking, training, spending, external messages, deployment or funds movement is
part of this delivery.
