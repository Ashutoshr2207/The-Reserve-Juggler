# Interface contract guide

Blueprint 1.0 | HTTP API 0.1.0 | Adapter 1.0 | Local single-workspace scope

**Machine authorities:** [contracts/openapi.json](../contracts/openapi.json) for HTTP; [contracts/forecast-adapter.schema.json](../contracts/forecast-adapter.schema.json) for the internal forecast interface. Do not author a second YAML/TypeScript/Pydantic spec. Generated clients/validators derive from these; API implementation exports are checked against the checked-in authority, not silently substituted. [OpenAPI 3.1.1](https://spec.openapis.org/oas/v3.1.1.html) and [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-validation) are the formats (opened 2026-10-17).

## Operations

Local `/api/v1`: get workspace context; import CSV and fetch dataset profile; create/retrieve immutable scenario revisions; review exact revision with If-Match; enqueue/get/cancel run; fetch paginated decisions and aggregate metrics; export completed owned evidence as a JSON object whose members may be written into a local ZIP. No account, trade, lending or model-training endpoint. Allowed local role modes and ownership in AUTH_SECURITY.md. Server uses workspace from authenticated local session, not a body/header claim.

All mutations require Idempotency-Key except review, which also requires If-Match. Idempotency scope is workspace + operation + key; retain for 24h. Same key/same canonical payload returns stored response; different payload returns 409 IDEMPOTENCY_CONFLICT. Reserve the key transactionally before side effects; retry ambiguous network failures with same key, never invent a new trade/run. ETag is immutable scenario fingerprint, response header on scenario GET/create; stale/missing precondition returns 409 STALE_REVISION. Invalid review cannot advance state.

Clients poll runs initially every 1s then at most 5s; stop at terminal status. GET may retry transport/503 twice with jitter; mutations retry once with the same key only for transport/503; no blind retry 403/404/409/422. Queue full returns 503 QUEUE_FULL with Retry-After; user may cancel queued work. R1 maximum one active worker and five queued runs; financial infeasibility is an outcome, not a retryable server error.

Error envelope: code, message, request_id, retryable, details (field/row issues). No filesystem path/stack/secret echoed. Stable error enum and response schemas are in OpenAPI. Security failure returns 401/403; resource lookup hides foreign/nonexistent IDs as 404. Validation 422 includes numeric/time/assumption semantics; unsupported version 409. Per-hour currency/accrual invariants require domain checks beyond JSON Schema. JSON Schema validation alone does not prove accounting correctness.

Amounts cross the browser boundary as integer-cent strings; no IEEE floating currency. Negative signs preserved. Case-sensitive synthetic timestamps carry no zone; metadata timestamps are separately UTC. Contract examples are fictional fixtures, not D07 results. Upload ceiling 5 MiB and CSV schema are explicit R1 limits; larger/multifile support is Proposed outside current task. File paths/URLs cannot be supplied as source imports.

## Compatibility and review

Version endpoints with `/v1`; retain `contract_version` in responses/manifests. Optional additive fields within supported schemas require coordinated version/test updates because strict clients reject undeclared properties; breaking enum/units/state changes require a new major interface or simultaneous unreleased contract bump. Never reinterpret an existing money field or enum value. BACKEND owns HTTP spec; AI_ML owns adapter spec; FRONTEND reviews both consumed shapes. All three approve shared money/time conventions via integrator.

Current first integrated outcome is a **validated contract fixture path**, not a running frontend/server: `contracts/examples/first_slice.json` connects dataset → scenario → reviewed revision → run → metrics/decision and adapter fallback. `tools/check_blueprint.py` checks local references and fixture structure/cross-links. It is a dependency-free structural checker for the schema subset we use, not a full official OpenAPI/JSON-Schema conformance validator. Phase 04 must add a standards validator plus generated-client/server-contract tests before declaring interface conformance. No API request has been served in Phase 03.
