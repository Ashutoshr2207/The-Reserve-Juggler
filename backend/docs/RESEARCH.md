# Reserve Juggler — Phase 01 research

Version: 1.2 | Research/access date: 2026-10-17 (Asia/Calcutta) | Owner: requesting user; analyst: Codex

## Phase 03 current pointer

The user delegated selection; RG-02 scope 0.2.0 / T-EXP experiment first is selected, with exact evidence in SELECTION_RECORD.json. Earlier proposal/waiting labels below are historical research states. Current blueprint and separate module packets are in PRD.md / TEAM_PLAN.md / assignments/INDEX.md; optional AI preprocessing/evaluation/training handoff is in AI_DESIGN.md, AI_EVALUATION.md and MODEL_TRAINING_PLAN.md. No training or product behavior result added by this pointer; rights/financial/model gates remain open.

## Phase 02 amendment notice

The Phase 01 assessment below is retained with provenance. Current [Phase 02 amendments](PHASE_02_RESEARCH_AMENDMENTS.md) independently review the three newly supplied project concepts and stronger vendor workflow overlap; a standalone evidence-only wedge is not presumed differentiated. [D07 dataset audit](DATASET_AUDIT.md) replaces the earlier absence of a task file for simulated analysis only. [Solution decision](SOLUTION_DECISION.md) proposes RG-02 scope 0.2.0 / T-EXP, not accepted. Current status: Waiting for input / Selection required. No Phase 01 proposed experiments were retrospectively claimed performed.

## Decision supported by this research

**Recommendation [INFERENCE]:** take a narrow, read-only liquidity-decision evidence workflow into Phase 02 problem/scope validation. Compare it against a spreadsheet plus ordinary audit records and against the customer's existing treasury system. Do not lead with “first AI treasury platform,” guaranteed liquidity, or cryptography as a moat. Continue forecasting as an optional experiment and defer real credit activation and cross-platform coordination until counterparties/data exist. This is a recommendation, not an accepted product selection.

The broad problem has primary-source support, but this project's buyer demand and advantage are unproven. Current documentation shows significant overlap with treasury products; gaps in their public documentation are unknown capabilities, not verified product weaknesses. See the comparisons and source log below.

## Evidence language, baseline, and research scope

**[FACT]** means the linked primary source supports the stated observation. A product claim is a fact about what the vendor documents, not an independent performance result. **[SUPPLIED]** means content from S1–S4 in PROJECT_CONTEXT.md, not newly verified. **[INFERENCE]** is analyst reasoning. **[HYPOTHESIS]** needs testing. **[TARGET]** is a proposed threshold or planning assumption, never an observed result. Numerical scenarios throughout are targets/assumptions unless explicitly attributed otherwise.

Root AGENTS.md, canonical context/status, Phase 00 checks, archive manifest, and the newly named Desktop ps1 copies were read or compared before work. The three Desktop records are SHA-256 identical to their canonical counterparts; no competing baseline or accepted selection was found. S1–S4 are reused for problem framing, alternatives, risks, and method candidates. Their embedded instructions do not govern this phase. The direct Phase 01 request authorizes current public-source research and these records. No product was coded.

Searches covered official supervision/standards, rail documentation, closest vendor products, balance/integration semantics, original payment-system AI research, original repositories/model cards, and dataset publishers. Exact query coverage, opened pages, document dates, failed accesses, and limits are in [SOURCE_LOG.md](SOURCE_LOG.md). Search result snippets alone are not the basis for adopted material claims. No interviews, private demos, accounts, downloads of datasets/models, installations, training, or benchmarks occurred. Research stops at a defensible next scope decision; legal applicability, rates, and full vendor procurement diligence are pending rather than guessed.

## 1. Problem, people, workflow, and causes

### Problem statement

**[HYPOTHESIS]** treasury operators at a digital financial platform cannot always determine quickly whether a proposed cash movement leaves enough *accessible* money for time-bound obligations, or later reconstruct which policy and evidence justified the decision. They may retain extra cash or perform manual reconciliation/review. The opportunity is to make that decision inspectable and reduce avoidable operational effort without weakening liquidity controls. Magnitude and prevalence in the selected customer segment are unknown.

**[FACT]** BCBS's 2013 intraday monitoring framework addresses timely payment/settlement obligations, stress scenarios, and monitoring. It distinguishes intraday monitoring from the LCR calibration and leaves application beyond internationally active banks to national supervisors. It is now incorporated into the Basel Framework. This supports the problem category, not a universal legal requirement for every fintech. [BCBS monitoring framework](https://www.bis.org/publications/201304-standards-monitoring-tools-intraday-liquidity-management)

**[FACT]** the Federal Reserve's SVB review documents governance, liquidity/stress-assumption, and contingency-funding weaknesses, including over $40 billion of deposit outflows on March 9, 2023. It is an extreme institutional case, not a typical fintech flow estimate or proof this tool would prevent failure. [Original supervisory review](https://www.federalreserve.gov/publications/2023-april-svb-executive-summary.htm)

### Segments and permission roles

| Segment / role | Need and likely workflow [HYPOTHESIS] | Buyer / access distinction | Fit now |
|---|---|---|---|
| Bank treasury / intraday cash desk | Settlement readiness, usable balances, exceptions, policy evidence | Treasurer/CFO may sponsor; risk/security/procurement control approval; bank-system entitlements separate | High consequence; integration and governance burdens high |
| Fintech platform treasury with sponsor/custodian banks | Reconcile internal ledger with external balances and upcoming payouts | Fintech CFO/head of treasury may buy; sponsor/custodian controls source access and movement | Leading discovery segment; no partner evidenced |
| Non-bank corporate treasury | Payroll/payment liquidity and idle-cash placement across entities | CFO/treasurer buyer; bank and ERP access needed | Adjacent segment with strong incumbent overlap; do not equate with deposit-taking bank |
| Risk/policy administrator | Define approved limits, freshness, exceptions and effective dates | Propose/manage policy; independent approval role before activation | Operator/reviewer, not automatically buyer |
| Treasury analyst / maker | Review inputs and propose sweep or funding request | Read assigned entity/accounts; cannot approve own material policy/action by default | Primary operational user candidate |
| Checker / treasury approver | Accept/reject proposed action and exceptions | Separate approval role; live action permission not granted by this project | Needed for later operational design |
| Auditor / reviewer | Reproduce a decision and trace exceptions | Read-only, scoped exports; signing-key custody is separate | Primary beneficiary candidate |
| Integration administrator / service identity | Maintain connectors, credentials, freshness, monitoring | Minimum machine scopes; no blanket human access to all entities | Operating owner needed for pilot |
| Depositors, payment recipients, employees | Timely payouts and fewer avoidable disruptions | Indirect beneficiaries; not assumed dashboard users or research participants | No consumer-facing app assumed |

Research participants, pilot users, active users, and concurrency have different meanings. A treasury reviewer can be a research participant without buying or operating the product. The proposed recruitment target is 5 people across treasury/risk/audit and at least 2 organizations; the proposed pilot is 1 institution with 3–5 named operators/reviewers. Active users would be unique operators using the workflow during a defined month, not accounts or transactions. Concurrency is simultaneous sessions/requests, not a claim about customer acquisition. **Actual counts for all are zero evidenced in this project.** Capacity scenarios appear in Section 5.

### Current workflow to investigate

**[SUPPLIED + HYPOTHESIS]** collect ledger/bank balances → normalize currencies/timestamps and reconcile → identify upcoming obligations and accessible cash → apply reserve policy/forecast → review proposed allocation or funding action → obtain approval → execute in an external authorized system → reconcile outcome → answer audit questions. Existing workflow details and elapsed time are not measured. Plausible causes are fragmented data, inconsistent balance semantics, late/changed transactions, settlement windows, policy changes, and handoffs across maker/checker/audit roles.

**[FACT]** an integration example, Modern Treasury's balance object, distinguishes ledger/available balance types, as-of date/time, and value date. **[INFERENCE]** a generic balance number is insufficient evidence of spendability; ingestion time must be recorded separately, and pending outflows must not be subtracted twice. [Balance object documentation](https://docs.moderntreasury.com/platform/reference/balance-object)

### Ranked pains

Ranking is an analyst triage, not survey scores. Severity: 5 = possible unmet obligations; 4 = material control/operations issue; 3 = efficiency/economic issue. Frequency and workaround costs below are hypotheses to validate, not measured averages. Evidence strength concerns the problem category; evidence for this particular buyer remains weak.

| Rank / ID | Pain | Severity | Expected frequency | Workaround and cost hypothesis | Evidence strength | Missing validation |
|---|---|---:|---|---|---|---|
| 1 / P01 | Insufficient accessible funds at obligation time | 5 | Exposure intraday; actual breaches unknown and episodic | Hold extra buffer / borrow / manual escalation; cost unknown | Strong category: BCBS and SVB review; no project-user incidence | Past near misses, obligation deadlines, available facilities and losses |
| 2 / P02 | Stale, incomplete, or semantically wrong positions | 4 | Potentially every refresh; actual delay distribution unknown | Reconcile portals/ledger; staff time and conservative buffer | Strong semantic precedent in balance docs; no measured data quality | Feed timestamps, encumbrances, corrections, source reconciliation |
| 3 / P03 | Cannot reproduce why a policy decision was made | 4 | Every exception; audit cadence unknown | Assemble exports, approvals, policy copies and logs | Moderate: source proposal + available audit technology; demand unproven | Real evidence request, reconstruction time, auditor acceptance |
| 4 / P04 | Excess idle cash relative to safe need | 3 | Potentially daily | Fixed balance floors and scheduled sweeps | Economic inference; supplied financial estimates not accepted | Investable amount after constraints, actual yield spread and fees |
| 5 / P05 | Disconnected or ambiguous action outcomes | 4 | Per transfer attempt; failures unknown | Manually confirm/retry/reconcile | Documented idempotent-request precedent; no incident rate | Timeout/retry evidence, cutoff and settlement behavior |
| 6 / P06 | Distrust or burden of automated recommendations | 3 | Each adoption/review cycle | Human review, existing TMS, no change | Hypothesis; no interviews | Approval preferences, explanation usability, training/support effort |

P01/P02 justify conservative boundaries first; P03 is the leading differentiating hypothesis to test. P04 alone may be served by existing sweep products. No defensible TAM, willingness-to-pay distribution, or “millions saved” finding is available.

## 2. Closest alternatives and reconciliation of supplied findings

| Alternative | Verified documented behavior / precedent | Verified limitation or scope boundary | Unknown; do not claim absent | Switching implication [INFERENCE] |
|---|---|---|---|---|
| Nilus Liquidity Agent | Vendor describes configurable liquidity thresholds, continuous breach monitoring and recommended responses | This is documentation, not our performance test | Exportable independently reproducible signed decision bundle, exact source trust/freshness model, partner coverage, pricing | Strong overlap; an audit trail alone is insufficient differentiation. [Nilus launch](https://www.nilus.com/blog/introducing-the-nilus-liquidity-agent-your-treasurys-always-on-policy-monitor/) |
| Kyriba | Fact sheet integrates cash/forecasting, debt/investments, payments and accounting; includes intraday postings and reconciliation | Purchased deployment and connectivity are dependencies | Exact reserve checks, portability/replay, service latency, budget for this buyer | May already satisfy the need; evaluate configuration before replacement. [Kyriba fact sheet](https://www.kyriba.com/resources/fact-sheets/liquidity-performance-platform/) |
| Trovata | Help documentation combines ML, repeat-history/manual streams and forecast reconciliation; current-day actuals depend on intraday reporting | Source explicitly conditions intraday actuals on reporting availability | Today's complete execution capabilities, institution coverage, decision-proof export | Earlier blanket “forecast only/no execution” finding is not established by this guide. [Forecasts Guide](https://help-center.trovata.io/en/articles/9648869-forecasts-guide) |
| Mercury Treasury + transfer rules | Product documents portfolio-dependent liquidity; support explains target-balance and scheduled/incoming-funds rules | Support page: Treasury settlement 0–2 business days; automatic transfers from Treasury limited to two monthly dates at least seven days apart; external rules push-only | Applicability to a particular customer's contractual setup; forecast/attestation features not proven absent | Useful conventional allocation option; no assumption that all yield instruments are locked overnight. [Treasury](https://mercury.com/treasury), [transfer rules](https://support.mercury.com/hc/en-us/articles/28768212621332-Setting-up-auto-transfer-rules) |
| Modern Treasury integration tools | Bank-reported balance metadata and idempotent requests are documented | Idempotency results retained for 24h and scoped by API key | End-to-end policy suitability, bank connectivity, pricing | Useful infrastructure/precedent, not evidence we can move money. [Request semantics](https://docs.moderntreasury.com/platform/reference/idempotent-requests) |
| Prophet (open source) | MIT-licensed seasonal forecasting project; repository says maintenance mode as of v1.4.0 in 2026 | Forecasting component, not treasury control workflow | Accuracy for this institution | Cheap baseline; package name is no moat. [Original repository](https://github.com/facebook/prophet) |
| Chronos (open source/pretrained) | Project offers pretrained time-series models under Apache-2.0; model specifics assessed in AI_OPPORTUNITIES | No local task validation | Forecast lift on private intraday positions and benchmark contamination | Compare against simpler models without assuming custom training is needed. [Original repository](https://github.com/amazon-science/chronos-forecasting) |
| immudb (source-available audit component) | Repository describes cryptographic history verification | Current master LICENSE is Business Source License 1.1 with a qualified production-use grant and later Apache change; not assumed permissive open source for every use | Fitness/licensing for a paid embedded/hosted product; source-input truth | Reuse concepts or a suitable component; standard audit integrity is existing art. [Repository](https://github.com/codenotary/immudb), [license](https://github.com/codenotary/immudb/blob/master/LICENSE) |
| Original AI research | BIS WP1310 studies prompted cash-management assistance in stylized wholesale-payment scenarios without specialized training | Authors flag consistency/realism/oversight limits; not a production or retail-deposit backtest | Transferability, real savings, safety for this platform | Weakens a categorical “LLMs cannot help” claim; supports a bounded experiment only. [Original paper](https://www.bis.org/publications/working-paper-1310-ai-agents-cash-management-payment-systems.pdf) |
| Spreadsheet + bank portals + documented approvals | Conventional baseline assembled from permitted balance exports, fixed floors, manual checking and stored policy versions | Manual reconciliation/review by design, not a measured error rate | Actual user's reliability/cost and whether ordinary logs already meet audit need | Lowest switching cost and meaningful comparison; no AI needed |
| Do nothing / keep existing TMS and reserve policy | Preserves current process and avoids implementation spend | No new workflow benefit by definition | Existing failure rate, reserve inefficiency and opportunity cost | Rational choice if incremental value does not exceed cost/risk |

**Corrections [FACT/INFERENCE]:** S1's market-wide “no integrated forecast and execution” statement is unsupported against current Kyriba documentation. S4's policy-monitoring concept overlaps Nilus. S2's blanket lockup assumption is too broad against Mercury's portfolio descriptions. S3's Fedwire 24/7 assumption conflicts with the currently published business-day operating schedule. The US schedule and India's RTGS 24x7x365 documentation cannot be substituted for one another. Planned expansions are not treated as live capabilities. [Fedwire schedule](https://www.frbservices.org/resources/financial-services/wires/fedwire-funds-service-national-settlement-service-operating-hours/), [RBI RTGS FAQ](https://www.rbi.org.in/scripts/FS_FAQs.aspx?Id=65)

S1–S3's historical yields, emergency spreads, cost estimates, “guarantee,” regulatory classifications, and all accuracy numbers stay unverified or scenario-specific. This phase does not establish that a specific regulator approves this product, that a lender will fund in stress, or that a particular instrument earns a given current return.

## 3. Three mechanisms and a conventional baseline

All four are hypotheses. The goal is to compare causal mechanisms, not package identical dashboards under different names.

### B0 — fixed policy, ordinary records, human approval

Maintain an approved cash floor plus known obligations, reconcile trusted balance exports, and have a checker approve transfers in the existing system. Store input files, spreadsheet version and approvals. Addresses P01/P02/P03/P05 without predictive AI. Benefit is simplicity; switching incentive from current ad hoc practice is clearer repeatability. Precedent: existing transfer rules and ordinary audit controls described above. Incremental difference is process discipline, not a new financial mechanism. Dependencies: agreed balance semantics, authorized exports, policy owner, reviewer time. Failure: unexpected outflows exceed the floor, stale evidence is accepted, or approval records are incomplete. Cheapest experiment: paper-replay ten fictional decisions using a spreadsheet and evidence folder. Use this as the comparator for M1, not as an intentionally weak strawman.

An illustrative policy check [HYPOTHESIS], requiring owner review: accessible funds after the proposed movement must cover the approved minimum plus obligations due within the chosen horizon that are not already reflected in available balance. Count an asset or facility only when usable by the obligation deadline under the scenario's terms. Keep currency pools separate; missing/contradictory evidence produces an unknown state. This is an example internal policy, not a regulatory reserve formula or an accepted liquidity-risk limit.

### M1 — portable evidence for policy-gated decisions

Bind each hypothetical decision to immutable input references, policy version/effective time, balance source and freshness, required liquidity, proposed change, outcome, exception/approver and signing identity. A separate reviewer can reproduce arithmetic and verify record integrity. **Benefit hypothesis:** reduce reconstruction effort and catch stale/conflicting evidence before a sweep proposal passes (P02/P03/P05). **Switching incentive:** keep existing bank/TMS execution but add a reviewer-friendly, portable evidence export, if existing tooling lacks the needed portability. **Precedent:** Nilus monitoring, Kyriba controls, immudb-style verification. **Incremental difference:** the exact cross-system evidence contract and replay workflow for one customer, not novel signatures or proof of solvency.

Dependencies: trusted evidence source, canonical money/time representation, policy governance, key lifecycle and access control. Failure: cleanly signed false balances, missing obligations, compromised keys, omitted events, stale data, or an auditor who finds ordinary logs sufficient. Cheapest experiment: 20 hand-authored decision packets with expected results, including stale/missing balance, encumbered cash, duplicate event, policy change, adverse withdrawal, failed/unknown sweep outcome, and tampering. Use paper review first; later sandbox implementation needs a separate phase. “Insufficient evidence” is distinct from “covered” and “shortfall.”

### M2 — uncertainty-aware cash allocation

Estimate future gross outflow quantiles/available inflows over an explicit horizon; combine them with known obligations and policy floors to recommend a buffer. **Benefit hypothesis:** lower avoidable idle cash while holding risk at an approved bound (P01/P04). **Switching incentive:** measured net benefit over B0 at matched risk, not attractive forecasts alone. **Precedent:** statistical/pretrained forecasts and existing treasury forecast products. **Incremental difference:** customer-specific availability-aware decision evaluation, not use of ML by itself.

Dependencies: authorized event and ingestion timestamps, reconciliation, seasonal history, settlement/asset terms, independent held-out periods, owner-approved risk tolerance. Failure: regime changes, extreme correlated withdrawals, delayed liquidation, optimistic inflow counting, leakage, or costs erasing benefit. Cheapest experiment: frozen historical replay of B0, seasonal empirical quantiles, a small quantile regression/boosting model, and optional pretrained forecast. Synthetic data tests plumbing only. No training requirement exists for M1; M2's training branch is PROPOSED.

### M3 — contract-bound contingent funding

Pre-agree a funding facility whose defined conditions can be checked against validated evidence. Simulate a request when a conservative shortfall trigger fires; record requested, approved, available and settled states separately. **Benefit hypothesis:** mitigate forecast-error consequences and lower net cost of reserve financing (P01/P05). **Switching incentive:** reliable additional capacity at acceptable total cost, rather than another alert. **Precedent:** committed liquidity facilities and the supplied parametric-cover proposal; no new insurance category or underwriting entitlement claimed. **Incremental difference:** evidence-linked contract conditions and operational response measurement.

Dependencies: real lender, legal eligibility, collateral/headroom, fees, decision and funding SLA, correlated-stress capacity and authorized rails. Failure: lender refusal, wrong trigger, facility suspension, exhausted capacity, late funding, premium/interest exceeding gains. Cheapest experiment: tabletop term sheet + deterministic trigger replay with deliberately denied/delayed funding and a fee sensitivity sheet. No lender contact, legal opinion, underwriting, or funds activation performed. Defer live version. Cross-platform Flow Index, auctions, token bridges and marketplaces remain future hypotheses with additional participant and regulatory dependencies, not required pieces of M3.

## 4. Usefulness, innovation, feasibility, adoption, and impact

| Dimension | M1 evidence workflow | M2 allocation | M3 contingent funding |
|---|---|---|---|
| Usefulness [HYPOTHESIS] | High only if evidence reconstruction is a recurring unmet need | High if measured risk-adjusted gain over existing tools | High only if useful, reliable contractual capacity exists |
| Innovation [INFERENCE] | Workflow integration; low component novelty | Mostly application/calibration of known methods | Contract + trigger integration; conventional underlying financing |
| Feasibility [INFERENCE] | Bounded fictional demonstration feasible; institutional truth/reconciliation harder | Data and tail-risk validation are gating | Counterparty/legal/operations are gating, not coding |
| Adoption [HYPOTHESIS] | Overlay/read-only start reduces replacement burden; compare incumbents | Conservative shadow recommendations before change | Treasury/legal/risk/lender agreement needed |
| Accessibility [TARGET] | Keyboard navigation, text labels in addition to colors, plain-language explanation, CSV plus machine-readable evidence, readable units/timezones | Quantile uncertainty explained alongside point estimates | Funding state and limitations explicit; no “guaranteed” icon |
| Impact [HYPOTHESIS] | Faster investigation, fewer evidence-driven mistakes | Better net yield at matched shortfall risk | Reduced uncovered shortfalls net of facility costs |
| Operating burden [INFERENCE] | Connector drift, reconciliation, policy updates, key rotation, backup verification, access reviews and support | Adds retraining/drift/calibration monitoring | Adds collateral/contract/capacity/settlement operations |
| Growth [HYPOTHESIS] | Expand one policy/account adapter at a time; grow through fit/acceptance | Expand only after per-institution evaluation | Counterparty capacity, not raw server throughput, limits scaling |

No survey proves adoption, accessibility compliance, impact, or a durable moat. Prototype usability and keyboard checks are planned, not completed. Separate customer balances from provider-controlled operating cash; neither can be presumed investable. Corporate treasury and regulated bank contexts have different authority and procurement boundaries.

### Provisional USP

**[HYPOTHESIS]** “Reserve Juggler helps a fintech treasury reviewer reconstruct each liquidity decision from time-stamped balance evidence, the applicable policy, and the resulting action record.”

Against Nilus's documented monitoring and Kyriba's broader platform, the proposed wedge is narrowly scoped, portable decision replay that complements an existing workflow. Against Mercury's transfer rules, it would add cross-source evidence review rather than claim a superior yield product. Against a spreadsheet, it must show an evidence-review or control benefit worth adoption. Whether these alternatives already provide equivalent export/replay is unknown and must be checked in Phase 02. Remove the wedge if an incumbent configuration satisfies the need cheaply.

### Impact hypotheses and scope boundaries

H1: evidence packets shorten reconstruction time without more critical mistakes. H2: freshness/availability gates catch dangerous proposals missed by a basic balance check. H3: calibrated M2 forecasts improve net return at an approved, matched risk envelope. H4: M3 produces benefit after fees, interest, unavailable-funding periods and operational delay. None is demonstrated.

**Recommended evaluation scope:** one fictional institution, one currency, one explicitly versioned reserve policy, bank-style balance evidence with availability/ingestion times, a set of obligations, hypothetical sweep decisions and simulated backstop outcomes. Optional Scenario B uses approved historical exports read-only. Scenario C adds supplied lender/peer commitments, if any. Geography remains unknown: use US and India rail assumptions only in separate labeled cases; do not combine laws or calendar rules.

**Excluded:** live movement/custody, credit activation, issuing tokens, insurance underwriting, regulatory certification, customer withdrawal restrictions, cross-currency optimization, public solvency claims, multi-party networks, and production readiness. Future RAG, ML, external attestation, MPC, hardware key protection, or multi-bank integrations are conditional on a measured need and actual authority.

## 5. Cost and capacity scenarios

All amounts below are **[TARGET/ASSUMPTION] in USD**, not supplier quotes, approved budgets, measured performance, or market prices. Use a 30-day planning month. Infrastructure assumptions exclude bank/API contracts, legal/compliance/security audits, identity services, tax, data acquisition and incident response. Actual institutional onboarding may dominate these envelopes.

| Scenario | Institutions / people | Workload assumption | Capacity and storage arithmetic | Planning cost envelope |
|---|---|---|---|
| A — local synthetic evaluation | 1 fictional institution; 1 analyst + 1 reviewer; no actual users | 20–100 cases; 2 simultaneous review sessions; no live feeds | Small local files; no throughput claim | 80–160 engineering/review hours × $25–$75 = $2,000–$12,000; existing local device, incremental compute $0–$50 |
| B — read-only pilot | 1 consenting institution; 5 named users, assumed 3 monthly active; 2 concurrent sessions | 10 accounts; 1,000,000 source events/month; per-account check each minute | 432,000 checks/month; event average 0.39/sec, hypothetical 100× burst 39/sec; at 2KB/event + 5KB/check = 4.16GB raw/month (decimal), before indexes/replicas | 240–600 setup hours × $25–$75 = $6,000–$45,000; infra assumption $100–$500/month; support 8–24h/month = $200–$1,800 |
| C — growth stress design | 20 institutions, each 5 named users; 100 named / assumed 60 monthly active; 20 concurrent sessions | 200 accounts; 20M events/month; same minute checks | 8.64M checks/month; 7.72 events/sec average, 772/sec at assumed 100× burst; 83.2GB raw/month. Naive bank polling = 8.64M calls/month; entitlement/rate limits unknown | 800–2,000 cumulative hours × $25–$75 = $20K–$150K; infra assumption $1K–$5K/month; support 40–120h/month = $1K–$9K |

Suggested design targets: at least twice the assumed burst in a later load test, bounded ingestion backpressure, independent read/write access scopes, tenant-isolated exports. Check frequency is a scenario, not a bank refresh SLA. Balance-feed rate limits and outages may dominate CPU. Storage retention is unselected; multiply raw monthly storage by approved retention, indexing and replication factors before costing. No row claims a deployed capacity or completed benchmark. Optional AI cost arithmetic is separate in AI_OPPORTUNITIES.md.

Economic sensitivity example, not a forecast: incremental annual return = average *safely* redeployable cash × net yield spread − incremental funding fees/interest − implementation amortization − operating costs. At fictional $5M safely redeployed and 1%, 2%, or 3% spreads, gross spread income is $50K/$100K/$150K per year before those costs and losses. The safe redeployable amount, spread, and risk are all unvalidated. Do not multiply hourly sweeps into independent annual gains or assume all customer balances belong to the platform.

## 6. High-risk hypotheses and cheapest experiments

These are **proposed [TARGET] criteria** for Phase 02 to refine with a policy owner, not accepted financial-risk limits. Passing a finite test does not establish production safety. Recruitment and private data acquisition require separate human authorization; no contact has been made.

| ID / pain | Hypothesis and cheapest next experiment | Proposed pass / fail | Owner / cost assumption |
|---|---|---|---|
| E01 / P03,P06 | A buyer needs portable replay beyond current logs. Walk through five recent anonymized cases with proposed 5 treasury/risk/audit participants across ≥2 institutions; compare current tool evidence | Proceed if ≥3 independently describe a relevant recent problem, one accountable sponsor agrees to a read-only evaluation, and an ordinary log/TMS configuration does not already solve it. Otherwise narrow/pivot/stop; small convenience sample is directional only | Human recruits/consents; hybrid analysis; 8–16h after access |
| E02 / P02,P03 | Reviewers understand M1 evidence. Counterbalance order of B0 and M1 evidence packs on the same ten cases | Target ≥30% lower median reconstruction time, no increase in critical classification errors; report individual results and uncertainty. Fail if misunderstanding or no useful difference; no population claims | Hybrid; 8–16h; no software needed |
| E03 / P01,P02,P05 | A deterministic policy can classify ambiguous evidence conservatively. Paper-check 20 cases and an independent expected-results table | All seeded stale/missing/currency/encumbrance/unknown-outcome cases must produce intended blocked/unknown state; exact arithmetic/policy reproduction on all cases. Any unsafe allow is fail. Tampered payload fails integrity check only after implementation is authorized | Agent drafts; human policy reviewer adjudicates; 8–12h |
| E04 / P01,P04 | M2 adds value at matched risk. After rights/data-quality gate, freeze rolling-origin splits; compare B0, seasonal quantiles, small ML, optional pretrained | Candidate target ≥10% lower held-out quantile loss with no worse shortfall count/severity at matched average buffer, plus positive net economics; risk owner must approve metrics/tolerances. If scarce tail observations, report insufficient evidence rather than zero risk | Hybrid; 16–40h evaluation preparation; no training run now |
| E05 / P01,P05 | Backstop economics survive unavailability. Tabletop deny/delay/fee scenarios and a draft term sheet | Fail live extension without evidenced counterparty terms and timely usable funds. Simulation passes only if rejected/late funding never counted as available; net benefit positive under explicitly agreed adverse assumptions | Human lender/legal owner; agent worksheet; 4–8h preliminary |
| E06 / P02,P06 | Rights, field coverage and feed quality permit a read-only pilot | Named data owner authorizes exact fields/use/location/retention; critical fields reconcile or remain explicitly unknown, never silently imputed as cash. Unresolved permission is fail for real-data branch, not for fictional evaluation | Human data/security owner + agent; 4–12h initial schema review |

## 7. Phase 02 recommendation and desk-research limits

Recommend **Phase 02 — validate and choose a bounded workflow**, beginning with E01/E02/E03 and A01/A06/A07 from COORDINATOR_ACTIONS.md. If no human/partner access exists, proceed with a fictional evidence schema, policy example, expected-results cases, and experiment plan; label commercial validation pending. Do not ask the user to repeat a selection if a newer recorded decision exists. No universal phase playbook was supplied, so this is a proposed next scope.

Decision to seek: whether M1 provides enough incremental reviewer value over B0 and named incumbents to justify a prototype. Adopt deterministic calculations and templated records as the provisional evaluation baseline; experiment with forecasting only after the data gate. Do not require training, RAG, a blockchain, or agents merely to appear innovative.

Desk research cannot establish actual pain frequency, buyer willingness to pay, incumbent contractual capabilities, rights to partner data, acceptable legal classification, permitted reserve policy, true asset availability, live funding capacity, forecast accuracy, reliability, accessibility compliance, or production unit economics. These gaps are recorded; further general searching will not replace direct workflow/data evidence. No next-phase selection or budget approval is inferred.
