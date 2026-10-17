# Shared frontend and backend design

Blueprint 1.0 | 2026-10-17 | UI contract for RG-02/0.2.0

**FRONTEND and BACKEND contributors must read and follow this file.** AI_ML must follow its forecast provenance/error conventions. No visual references/screenshots were supplied for the new app; the comparative audit supplies conceptual reporting references only. Do not copy a competitor UI or hardcoded model claims. Detailed journeys live in [FLOW.md](FLOW.md), schemas in [API_CONTRACT.md](API_CONTRACT.md), security in [AUTH_SECURITY.md](AUTH_SECURITY.md), business invariants in [ARCHITECTURE.md](ARCHITECTURE.md).

## Screens and components

| Screen | Primary content and action | Backend responsibility / permission |
|---|---|---|
| S1 Data | Dataset summary (period, rows, hash), file picker and row-level issues; “Import CSV” | Validate content, cap upload, hash bytes, workspace ownership; maker import |
| S2 Scenario | Funding/assumption form; clear fictional-mode banner; cash/repo defaults and distinct Tier 2/3 what-if section; “Submit for review” | Strict schema + semantic validation; immutable revision; maker cannot fake approval |
| S3 Review | Source fingerprint, assumptions, changed fields, risk limits and unresolved warnings; “Acknowledge fictional scenario” or return to draft | Reviewer context plus exact revision/ETag; reject stale review. One-person local review explicitly self-reviewed, never claimed independent |
| S4 Compare | Run controls, progress, cash-only/fixed-repo/candidate comparison; separate funding case and tier-risk scenario; “Run comparison” | Server requires reviewed snapshot; common scenario fingerprint; worker states; failure is not investment success |
| S5 Decision | Time-ordered ledger/availability chart + accessible table; select origin to inspect decision, input cutoff, reason, adapter/fallback and consequence | Paginated immutable evidence; cursor tied to run; preserve negative values and unknown states |
| S6 Evidence | Run manifest, metrics definitions, checks/warnings, downloadable JSON/CSV bundle; “Export evidence” | Bundle only owned run resources; sanitization, checksums; no export of model weights or unrelated files |

Shared components: AppShell, WorkspaceBadge, SyntheticModeNotice, DatasetCard, AssumptionField (label/unit/help/error), ReviewDiff, RunStatus, MoneyCell, AvailabilityTimeline, ComparisonTable, DecisionInspector, ErrorSummary, ExportPanel. Share one MoneyCell implementation; no frontend financial calculation beyond formatting/cents-string display. Do not add tabs for every engine or public marketing page in R1.

Desktop wireframe: 240px left navigation, main area max-width 1,280px; title + synthetic/workspace context; dataset/scenario header; primary action; metric table; timeline/table; evidence drawer. At <1,024px navigation collapses, comparison cards stack and filters wrap; at <640px use a labeled menu, full-width forms and a horizontally scrollable data table with sticky row labels. No hidden critical warnings. Maintain table semantics rather than squeezing columns into unreadable text.

## Visual tokens (authoritative values)

Light neutral UI: canvas #F5F7FA, surface #FFFFFF, text #172B4D, muted text #42526E, border #CBD5E1, primary #174EA6, focus #6D28D9, success #17643B, warning #7A4B00, danger #B42318. Use text/icon labels in addition to color; verify contrast in actual UI before release. Typography system sans (Segoe UI/Arial fallback), body 16px/1.5, small 14px, heading 24/32px; tabular numerals for financial values. Spacing scale 4/8/12/16/24/32px; radius 8px; control minimum height 44px. No animation of training completion or invented progress percentages. Reduced-motion preference removes decorative transitions. No external font/CDN dependency needed.

Money displays USD with negative sign and separators; values beyond JS safe integer stay decimal strings/BigInt in the typed client. Rates show percentage points with explicit label. Timestamp includes synthetic clock label, not fabricated UTC or IST. Null/unknown displays “Unavailable” with reason; true zero displays 0. Pending marked proceeds and available cash remain separate.

## Shared state, validation and error mapping

| State | UI behavior / recovery | Server behavior |
|---|---|---|
| No dataset/scenario/run | Helpful next action, no default fictitious totals | Empty owned collection, not fake completed run |
| Loading/importing | Disable duplicate submit; announce busy/status | Validate before dataset becomes ready; atomic registration; return request_id |
| Invalid input (422) | Error summary links to fields/CSV row; retain nonsecret form input | Stable code + field/row location; reject whole bad import; no partial source mutation |
| Missing policy/rights acknowledgment | Explain exact prerequisite, keep review/run disabled | 422 ASSUMPTIONS_INCOMPLETE or 409 SCENARIO_NOT_REVIEWED; no zero defaults |
| Forbidden (403)/unknown resource (404) | No leaked path/owner details; return to owned workspace view | Enforce local context/role and resource lookup; deny forged mode/header |
| Stale revision/idempotency mismatch (409) | Reload latest snapshot; show changed assumptions; never auto-approve | Version and idempotency checks before mutation |
| Queued/running | Phase label and completed hourly count only when measured; cancel action | Single worker, bounded queue; poll result; cancellation cooperative at hour boundary |
| Financially infeasible completed run | “Completed with shortfalls” warning, inspect unpaid amounts | A valid calculation can have unpaid obligations; not a runtime failure or success guarantee |
| Runtime/adapter error | Show retryable status and fallback identity; keep prior good run read-only | Transient errors bounded; unknown arithmetic fails run; adapter fallback recorded separately |
| Cancelled/interrupted | Partial preview watermarked; resume unsupported, new run from immutable scenario | Mark cancelled/interrupted; partial totals excluded from ranking/export as complete |
| Export unavailable | Show why (nonterminal run etc.); retry same logical request | Stable 409/503; never return stale bundle as new result |

Error responses use one envelope from OpenAPI. Validation constraints run at backend even if frontend already checked. UI cannot turn workflow role labels into authority; server session context is authoritative. State transitions are defined only in FLOW.md. On changes: module owner proposes a design diff; BACKEND integrator gets FRONTEND + affected AI_ML review, updates API/fixtures/tests and bumps blueprint version together. If schema and design conflict, stop affected integration and resolve through DECISIONS.md; do not silently implement two interpretations.

Accessibility target: WCAG 2.2 AA for R1 interactions, with semantic landmarks/headings, visible focus, label/error associations, live status region, dialog focus return, logical tab order, skip link, zoom/reflow and chart data alternatives. See [W3C quick reference](https://www.w3.org/WAI/WCAG22/quickref/) (accessed 2026-10-17); actual conformance untested.
