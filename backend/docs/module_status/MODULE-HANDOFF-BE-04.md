# MODULE-HANDOFF — BACKEND / BE-04

Version 3.0.0 | 2026-10-18 (Asia/Calcutta) | RG-02/0.2.0

BE-04 storage/security/lifecycle is implemented and locally verified. The direct
user request covers completing the backend; affected peer review remains pending.
Shared contracts and the 37 synchronized baseline files are unchanged.

`app/services/worker.py` owns one OS-locked worker and five waiting jobs in a
durable SQLite queue. Run acceptance and its 24h idempotency snapshot commit
together, returning canonical 202/QUEUED. Computation holds no request-wide write
transaction. Queued cancellation is immediate; running cancellation is checked at
each hour. Completion and cancellation serialize; terminal states are immutable.

Migration 003 adds cancellation, engine/source provenance, run fingerprints,
queue/page indexes and accounting reports. It upgrades schema 1/2 transactionally.
Evidence cannot be updated/deleted or appended after terminal state. Startup and
shutdown mark unfinished runs INTERRUPTED; an actual process-kill test verifies
recovery and OS lock release. Restart never resumes partial financial replay.

Evidence checkpoints commit every 24 simulated hours per policy and remain
incomplete after failure/cancel. Complete metrics/reports/lots and success commit
atomically. Incomplete runs expose no successful metrics, decision page or export.
Source bytes are rehashed per replay. Posting overflow/negative cash fails the run.
Errors are redacted; inability to persist failure status stops new work until
restart. Cursor pages are bounded, run/session-bound and reject malformed inputs.

Existing one-use bootstrap, trusted startup roles, cookie/CSRF/Host/Origin,
idle/logout/restart revocation and workspace checks are retained. The OS user is
the local boundary; no production identity claim is made.

`python -m app.maintenance` provides offline backup/verify/restore into new paths
below backend/work. Its shared OS lease rejects an active server and protects
initialization/migration. Snapshots cover database plus referenced raw files;
SQLite integrity/FKs, hashes, complete-run restoration, tamper rejection and
refusal to overwrite are tested. Retain matching code/lock; no reverse migration,
online/power-loss/full-disk guarantee or deletion API is claimed.

Evidence is in the final **151-test** suite: [JUnit](../../outputs/BE-05-tests.xml)
and [verification](../../outputs/BE-05-VERIFICATION.json). [RUNNING](../../RUNNING.md)
has exact commands; [BACKEND status](BACKEND.md) records execution limits.
FRONTEND is reviewer, AI_ML backup; no review is invented.
