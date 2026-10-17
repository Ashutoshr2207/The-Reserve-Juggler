# Phase 03A synchronized teammate assignments

Packet set RG02-030A-1.0 | Handoff revision 1.1 | Scope 0.2.0 | HTTP 0.1.0 | Adapter 1.0 | 2026-10-17

Phase 03A is complete as **three separate assignments and packets**, not dispatched threads or completed implementation. [FRONTEND](FRONTEND.md), [BACKEND](BACKEND.md), [AI_ML](AI_ML.md). BACKEND additionally coordinates integration/product acceptance; no fourth teammate. Names and demonstrated skills are unknown; role mapping is proposed until user maps the people.

Each packet contains the same shared docs/contracts/fixtures/source manifests plus assignments/status as shared reference and a TASK.md selecting its sole owned role. Other role assignments are coordination references, not extra ownership. Packet hashes/version lock are in [SYNC_MANIFEST.json](SYNC_MANIFEST.json). No packet can silently use an older API/adapter. Full source CSV stays in the complete local bundle; AI_ML/other packet users obtain it from the unchanged canonical path or same user's complete ZIP, verify D07 hash, and respect rights gates.

Shared mandatory reading: root AGENTS.md, PROJECT_CONTEXT.md, docs/PROJECT_STATUS.md, SOLUTION_DECISION.md, PRD.md, DESIGN.md, FLOW.md, ARCHITECTURE.md, API_CONTRACT.md, AUTH_SECURITY.md, TEAM_PLAN.md, TESTING.md, DECISIONS.md and RELEASE_RUNBOOK.md. Both frontend and backend follow DESIGN. AI_ML also reads all AI design/evaluation/training docs and DATASET_AUDIT/PROFILE plus coordinator gates. These are included so teammates can work from a self-contained packet without copying one another's module source.

Start only when a Phase 04 implementation task is issued. Integrate FE-01 + BE-01/02 + AIM-01 early using first_slice.json as a contract reference, not as computed evidence. Start Branch T rights/split/setup work alongside that first slice; fitting remains gated. Own status files live in docs/module_status/. Before changes, check packet hashes against repository, then propose any shared change to BACKEND rather than updating independent copies. User's exact delegated selection evidence is in SELECTION_RECORD.json; do not request selection again.

Each assignment includes task IDs, requirements, paths, owner/reviewer/backup, dependencies, acceptance/checks and exact starter prompt. Deliver verified changes and actual command output to BACKEND integrator through the shared review workflow; sending packets in this phase does not mean a human/agent received or ran them. No task creation or external messaging occurred.

Role packets omit historical/raw source archives to avoid unnecessary duplication. Run the full source-integrity checker from the extracted complete bundle, not a standalone role packet. Shared specs/fixtures are byte-identical in every packet.

For distribution and coding-agent onboarding, start with [master PRD](../PRD.md) and [exact send list](../SEND_FILES.md). Current PRD is 1.1; task ownership and interface versions are unchanged.
