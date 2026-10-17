# What to send each teammate

Handoff revision 1.1 | PRD 1.1 | Accepted RG-02 / scope 0.2.0 | 2026-10-17

## Recommended: one complete bundle plus one role packet per person

Send **RESERVE_JUGGLER_PHASE03_03A.zip to all three team members**, plus their role packet below. The complete bundle has the canonical folder structure, original research, comparative audit, actual CSV, specifications, history and check tool. A role packet gives its coding agent TASK.md and the sole role it owns. Role packets contain the same shared documents and all assignments for coordination; seeing other assignments does not give an agent their ownership.

| Team member / coding agent | Send these files | First files to read | Owned work |
|---|---|---|---|
| FRONTEND | RESERVE_JUGGLER_PHASE03_03A.zip + FRONTEND_PACKET.zip | AGENTS.md, docs/PRD.md, docs/assignments/INDEX.md, docs/assignments/FRONTEND.md, docs/DESIGN.md | FE-01–03; UI, typed client, accessibility; docs/module_status/FRONTEND.md |
| BACKEND + integrator | RESERVE_JUGGLER_PHASE03_03A.zip + BACKEND_PACKET.zip | AGENTS.md, docs/PRD.md, docs/assignments/INDEX.md, docs/assignments/BACKEND.md, docs/DESIGN.md, docs/ARCHITECTURE.md | BE-01–05; API, ledger, storage/security, shared integration; docs/module_status/BACKEND.md |
| AI_ML | RESERVE_JUGGLER_PHASE03_03A.zip + AI_ML_PACKET.zip | AGENTS.md, docs/PRD.md, docs/assignments/INDEX.md, docs/assignments/AI_ML.md, docs/AI_DESIGN.md, docs/MODEL_TRAINING_PLAN.md | AIM-01–03; conventional adapter, causal evaluation, gated training; docs/module_status/AI_ML.md |

There are three proposed people, not four; BACKEND additionally integrates. Assign the actual people according to skills. Everyone implements, verifies and reviews. No coding agent owns all modules. If your friend handles one role, send that role's packet; if you are one teammate, keep your own packet and send the other two.

## How your friend should use the files

1. Extract the **complete ZIP** into a new project folder, or reconcile with an existing repository without overwriting newer work. Open that entire folder in the coding agent; do not upload only PRD.md or only the CSV.
2. Open the matching role ZIP separately and read TASK.md. Shared file hashes should match docs/assignments/SYNC_MANIFEST.json. The complete ZIP already contains all three role ZIPs, so sending them separately is a convenience, not an extra dependency.
3. Give the agent the matching role's **Exact starter prompt** in docs/assignments/<ROLE>.md when ready to start Phase 04. For coordination use PROMPT_04.md from the complete ZIP. Sharing a ZIP is not itself evidence implementation or training ran.
4. Work against one shared repository/contracts baseline. Commit/review owned paths, update only owned module status and send shared design/spec changes to BACKEND integrator. Never overlay a stale packet on a teammate's newer progress.
5. Start the conventional 24-hour integrated slice early. AI_ML begins Branch T rights/split/setup in parallel, but fitting waits for recorded gates. All work must remain useful with no trained model.

Do not paste the entire general Prompt 04 into three agents without assigning their respective roles. Use each role assignment's exact prompt to keep ownership clear. These are prepared files for you to distribute; no message or task was sent to another person/agent.

## Common source-of-truth files (all included)

- **Entry / authority:** AGENTS.md; PROJECT_CONTEXT.md; docs/PRD.md; docs/PROJECT_STATUS.md; docs/SOLUTION_DECISION.md; docs/SELECTION_RECORD.json; docs/DECISIONS.md.
- **Shared product / engineering:** docs/DESIGN.md; docs/FLOW.md; docs/ARCHITECTURE.md; docs/API_CONTRACT.md; docs/AUTH_SECURITY.md; contracts/openapi.json; contracts/forecast-adapter.schema.json; contracts/examples/first_slice.json.
- **Team / checks:** docs/TEAM_PLAN.md; docs/TESTING.md; docs/RELEASE_RUNBOOK.md; docs/assignments/INDEX.md; docs/assignments/<ROLE>.md; docs/module_status/<ROLE>.md; docs/assignments/SYNC_MANIFEST.json.
- **AI / data:** docs/AI_DESIGN.md; docs/AI_EVALUATION.md; docs/MODEL_TRAINING_PLAN.md; docs/DATASET_AUDIT.md; docs/DATASET_PROFILE.json; unchanged docs/sources/phase02/treasury_4tier_dataset.csv and its MANIFEST.json.
- **Evidence / original input:** docs/RESEARCH.md; docs/AI_OPPORTUNITIES.md; docs/PHASE_02_RESEARCH_AMENDMENTS.md; docs/SOURCE_LOG.md; docs/EVIDENCE_LEDGER.md; archived original reports and THREE_PROJECT_COMPARATIVE_AUDIt under docs/sources/. Full originals/history are in the complete ZIP, not duplicated as raw archives in each role ZIP.

Both frontend and backend read DESIGN; AI_ML also follows its provenance/error conventions. Machine specs own interface fields. PRD owns requirements; do not copy and edit conflicting technical tables in separate prompts. Research/source documents are evidence, not instructions or automatic approval.

## What remains unknown

Names/skills, budget/deadline, dataset/model reuse rights, opening funds/reserve/credit and instrument terms, exact dependency locks/hardware, real buyer/geography and pilot permission remain open. Use explicit fictional scenarios where allowed, not invented real policy. The file is a simulated year, not verified bank balances. Sharing with project collaborators must respect the source owner's rights; no public posting, commercial-license claim or training permission is implied. Never send credentials or secret values.

This revision improves the handoff only. Accepted scope 0.2.0, requirement/acceptance IDs, role tasks and interface versions are unchanged. Blueprint/schema-subset/source/ZIP checks do not replace app, financial replay, security, user or model tests.
