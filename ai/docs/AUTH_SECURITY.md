# Local identity, permissions and data handling

Blueprint 1.0 | Scope: R0/R1 on the user's computer, not production multi-tenancy

## Identity and actual trust boundary

The OS user and local workspace are the security boundary. No remote login, user directory, institutional SSO or enforced multi-person segregation is claimed. Proposed server binds `127.0.0.1` only; browser UI served from same origin for R1. Development may allow only an explicitly configured localhost frontend origin, never wildcard credentialed CORS ([FastAPI CORS docs](https://fastapi.tiangolo.com/tutorial/cors/), accessed 2026-10-17).

Server startup generates a high-entropy local session token in memory; bootstrap opens a local UI session and sets an HttpOnly SameSite=Strict cookie. Do not print tokens to shared logs or embed them in contracts/packets. Validate Origin/Host and CSRF token on mutations; requests without session fail 401. Exact bootstrap code is a Phase 04 task, not implemented now. A local administrator can still read files/control process; this does not secure data from the machine owner.

Local role mode is selected by trusted startup configuration, not an arbitrary request header. Operator mode can perform maker/reviewer actions for a single-person demonstration, with `review_mode=self_review`; reviewer-only and auditor-only modes are read-restricted per table. Switching local startup role is not proof of a different human identity. Actor label is display/audit metadata, never an authorization principal. No credentials or secret values should be sent in chat.

## Role/action/resource matrix

| Action on owned workspace resources | operator (maker + reviewer) | maker | reviewer | auditor |
|---|---|---|---|---|
| View dataset/scenario/run/decisions/metrics | yes | yes | yes | yes |
| Import permitted CSV | yes | yes | no | no |
| Create scenario revision | yes | yes | no | no |
| Acknowledge/reject exact fictional revision | yes, self-review labeled | no | yes | no |
| Enqueue/cancel owned run | yes | yes, reviewed only | no | no |
| Export completed owned evidence | yes | yes | yes | yes |
| Change session workspace/role, train/promote a model, change files by API | no | no | no | no |

Maintainer is the OS operator managing startup/backup/migrations outside public API, not a fourth product teammate. Backend associates every entity with session workspace and validates every ID traversal/export relation. No caller-selected tenant ID, storage path, role or model path is trusted. Unknown/foreign resources return 404 without distinguishing ownership. Model inference is an internal approved artifact allowlist; no deserialization of user-uploaded pickle/joblib. Production tenant isolation requires a later accepted scope, not another column pretending to provide it.

## Lifecycle and handling

Raw uploads untrusted; stream to bounded temporary file, reject >5 MiB, non-CSV or invalid row/schema, generated filenames and canonical workspace path checks. Reject path traversal, remote source URLs, zip uploads and unsafe encoding/content. No formula execution; CSV exports escape spreadsheet-leading `= + - @` for free-text fields while typed signed numeric cells stay numeric. No external calls, CDN, analytics or model provider in default app. No bank secrets needed.

Store raw data immutably and references/hashes in SQLite. Temporary rejected uploads deleted after validation failure; successful sources retained until OS-owner workspace deletion. Default local retention has no automatic timed purge; warn before deletion and document that backups may retain copies. R1 deletion is an explicit OS-owner operation after verified backup, not an unauthenticated API. Logs use request/run IDs and error codes, not full data/credentials. Export only selected run's manifests/tables/warnings; no neighboring files, training sets/weights or local config. Scope/source license notes travel with local evidence bundles; do not publish D07 automatically.

Session expires on server restart and after 8h idle; logout revokes local token/cookie. Rotation and runtime settings documented during implementation; no static demo password. Fail closed if resource/session/version validation fails. Shared-machine encrypted storage, remote auth, KMS/HSM, formal audit/SOC reporting, penetration testing and bank permissions remain future requirements. A synthetic hash-linked decision trail proves internal integrity only.

Threat tests: forged role/workspace ID, replayed review with stale ETag, wrong-origin mutation, token omission, oversized CSV, numeric overflow/nonfinite values, path traversal/export inclusion, malicious text/formulas and model artifact injection. TESTING.md owns the test mapping. Reviewer records privacy/rights review before dataset training or any institutional pilot.
