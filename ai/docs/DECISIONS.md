# Decision register and specification change control

Blueprint 1.0 | 2026-10-17

## Authority and accepted choice

SEL-01: accepted by **human-delegated selection**. In response to the exact RG-02/0.2.0/T-EXP selection question, user wrote: “do whatever u think will be giving the best output for unique project , from existing solutions”. The agent selected unchanged RG-02/0.2.0 with T-EXP experiment first, recorded question/reply/basis and original decision hash in SELECTION_RECORD.json. Do not claim the human typed the named acceptance sentence. The direct request authorizes Phase 03/03A documentation and ZIP; product construction/training begins under a subsequent Phase 04 task and the existing gates.

| ID | Decision / status | Rationale / owner |
|---|---|---|
| ADR-01 | Local offline research prototype, cash/repo default; accepted scope | Source funding deficit and real-world authority gaps; user delegated choice |
| ADR-02 | React/TypeScript + Python/FastAPI, SQLite, one worker; blueprint implementation choice | Separate three-teammate modules and typed contracts; exact versions remain Phase 04 lock task; BACKEND integration owner |
| ADR-03 | One HTTP OpenAPI and one forecast JSON Schema; blueprint choice | Shared source of interface truth; generated code may not fork it |
| ADR-04 | Integer-cent strings on wire; exact postings; synthetic time vs UTC metadata | Prevent precision/time leakage; invariants in ARCHITECTURE.md |
| ADR-05 | Conventional adapter mandatory; T optional experimental | Model failure must not block core; AI_ML owns evidence, BACKEND release boundary |
| ADR-06 | No production identity/multi-tenant/live transactions | Local OS boundary only; AUTH_SECURITY owns matrix |
| ADR-07 | BACKEND also integrator/product-acceptance coordinator among exactly 3 proposed roles | Central ledger/contracts need integration authority; no fourth teammate or invented person |

## Open decisions / constraints

| ID | Question / status | Owner and blocking effect |
|---|---|---|
| OD-01 | Actual 3 people and skills unknown | User maps people to proposed roles; does not block packets; may trigger reviewed stack adjustment |
| OD-02 | D07 origin/license/allowed model use and publication | Human rights owner; blocks fitting/public release, not current blueprint/fixture-only work |
| OD-03 | Real endowment/reserve/caps/credit/instrument/fees/settlement terms | Human treasury/policy owner; R1 may use explicitly acknowledged fictional assumptions, never real investment claims |
| OD-04 | Dollar economic materiality and acceptable financial-risk limits | Human policy owner; blocks model/commercial performance claim, not conventional technical proof |
| OD-05 | Exact dependencies/Node/build versions and available hardware | Module owners with BACKEND review at Phase 04 setup; no lockfile or install falsely claimed |
| OD-06 | Independent seed/year, real buyer/participant access and usefulness | Human sponsor; blocks generalization/commercial/pilot claims |
| OD-07 | Signing need, authentication/remote hosting, real connectors | Proposed future scope only, not silently included |

## Authoritative detail map and conflict procedure

Scope: SOLUTION_DECISION (accepted 0.2.0); requirements: PRD; lifecycle: FLOW; screens/styles/shared validation presentation: DESIGN; finance/data/storage: ARCHITECTURE; HTTP fields/errors/operations: contracts/openapi.json; forecast fields: contracts/forecast-adapter.schema.json; identity/roles: AUTH_SECURITY; evaluation/preprocessing: AI documents; task ownership: TEAM_PLAN + module assignments; actual execution evidence: PROJECT_STATUS/module_status/check records. Source data and historical documents are immutable provenance, not current implementation authority.

If a contributor finds a conflict, record affected IDs/files, expected behavior and examples in their status, stop only affected integration and submit a change to BACKEND integrator. Integrator obtains FRONTEND/BACKEND agreement for DESIGN/HTTP and AI_ML review for adapter/forecast semantics; update canonical spec first, version, regenerate clients/fixtures and update dependent tests/docs. Material scope changes stay Proposed until human decision; minor implementation choices may be resolved by integrator within accepted scope. Re-run affected checks and record actual evidence. Never overwrite another module's progress or silently repair two divergent specs.

Each teammate implements and verifies owned changes and reviews another module. BACKEND coordinates integration and presents product acceptance evidence; the requesting human remains final scope/release authority, not a fictitious fourth engineering teammate. No team messages or task dispatch sent by this planning phase.
