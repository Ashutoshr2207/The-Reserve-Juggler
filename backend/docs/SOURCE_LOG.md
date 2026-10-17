# Phase 01 primary-source and search log

Version: 1.1 | All searches and opens: 2026-10-17 (Asia/Calcutta)

Phase 02 adds S5/D07 under docs/sources/phase02/MANIFEST.json. New primary-source searches/opens, citations, dates and failed source accesses are recorded in [PHASE_02_RESEARCH_AMENDMENTS.md](PHASE_02_RESEARCH_AMENDMENTS.md); actual D07 checks are in [DATASET_AUDIT.md](DATASET_AUDIT.md). The Phase 01 log below is preserved, including its then-current dataset absence and access limitations.

The date above is the research access date, not a guarantee that a live web page is an immutable snapshot. Publication/update dates below are stated only where visible. Dynamic repositories and product pages must be rechecked before implementation/procurement; no commit/version is pinned for execution in this phase. Sources are linked near claims in RESEARCH.md and AI_OPPORTUNITIES.md. No third-party summaries are used as claim evidence.

## Opened primary sources used

| ID | Source | Document date / freshness observed | Evidence role and boundary |
|---|---|---|---|
| R01 | [BCBS intraday monitoring](https://www.bis.org/publications/201304-standards-monitoring-tools-intraday-liquidity-management) | 2013-04-11; landing page says consolidated | Problem/monitoring precedent; not entity-specific legal advice |
| R02 | [Federal Reserve SVB executive summary](https://www.federalreserve.gov/publications/2023-april-svb-executive-summary.htm) | April 2023 review | Original institutional failure account; not representative incidence |
| R03 | [Nilus Liquidity Agent launch](https://www.nilus.com/blog/introducing-the-nilus-liquidity-agent-your-treasurys-always-on-policy-monitor/) | 2026-03-31 | Vendor-described monitoring/recommendations; not independent testing |
| R04 | [Kyriba platform fact sheet](https://www.kyriba.com/resources/fact-sheets/liquidity-performance-platform/) | Undated live page | Vendor-described integrated capabilities |
| R05 | [Trovata Forecasts Guide](https://help-center.trovata.io/en/articles/9648869-forecasts-guide) | 2026-01-14 | Product help workflow and reporting condition |
| R06 | [Mercury Treasury](https://mercury.com/treasury) | Undated live page | Portfolio access/liquidity descriptions; quoted live yields not adopted |
| R07 | [Mercury transfer-rule support](https://support.mercury.com/hc/en-us/articles/28768212621332-Setting-up-auto-transfer-rules) | Undated live page | Specific rules and settlement constraints |
| R08 | [Fedwire operating schedule](https://www.frbservices.org/resources/financial-services/wires/fedwire-funds-service-national-settlement-service-operating-hours/) | Undated live operating page | Corrects blanket 24/7 assumption; future expansions not assumed implemented |
| R09 | [RBI RTGS FAQ](https://www.rbi.org.in/scripts/FS_FAQs.aspx?Id=65) | FAQ item cites effective 2020-12-14; site footer 2026-10-17 | Separate India rail scenario; not a product license |
| R10 | [Modern Treasury balance object](https://docs.moderntreasury.com/platform/reference/balance-object) | Relative update “4 months ago” displayed | Balance metadata semantics |
| R11 | [Modern Treasury idempotent requests](https://docs.moderntreasury.com/platform/reference/idempotent-requests) | Relative update “about 1 year ago” displayed | Retry/state precedent, not an integration performed |
| R12 | [Prophet original repository](https://github.com/facebook/prophet) | Live README's 2026 v1.4.0 maintenance notice | Open-source baseline and MIT license; no local benchmark |
| R13 | [Chronos original repository](https://github.com/amazon-science/chronos-forecasting) | Live repository; release history includes 2025-10-20 and 2026-06-05 | Pretrained comparator; no checkout installed |
| R14 | [Amazon Chronos-2 model card](https://huggingface.co/amazon/chronos-2) | Live model card; no revision pinned | Artifact capabilities/license; not local performance |
| R15 | [immudb original repository](https://github.com/codenotary/immudb), [current license](https://github.com/codenotary/immudb/blob/master/LICENSE) | Live master; license references version 1.9DOM.2 or later | Audit component precedent; qualified licensing checked |
| R16 | [BIS WP1310 landing](https://www.bis.org/publications/working-paper-1310-ai-agents-cash-management-payment-systems), [original paper](https://www.bis.org/publications/working-paper-1310-ai-agents-cash-management-payment-systems.pdf) | Landing 2025-11-26; paper November 2025 | Original stylized AI research; not field validation |
| R17 | [NN5 Monash deposit v3](https://zenodo.org/records/4656110) | Record says published 2020-06-11; technical modification 2021-04-01 | Proxy dataset discovery; licensing remains unresolved |
| R18 | [CHAPS official metadata](https://www.bankofengland.co.uk/statistics/details/further-details-about-chaps-daily-settlement-data) | Last updated 2025-07-28 | Official aggregate data scope |
| R19 | [Bank of England legal/database terms](https://www.bankofengland.co.uk/legal) | Last updated 2026-10-15 | Data-specific reuse terms and exceptions |
| R20 | [IBM AMLSim repository](https://github.com/IBM/AMLSim), [code license](https://github.com/IBM/AMLSim/blob/master/LICENSE) | Live master; no commit installed | Generator scope, dependencies and code license |
| R21 | [LangGraph official overview](https://docs.langchain.com/oss/python/langgraph/overview) | Undated live documentation | Orchestration capabilities; optional, not selected |
| R22 | [OWASP prompt injection guidance](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | LLM01:2025 edition; live page | Primary security guidance; no completed threat test |

## Search coverage: actual query batches

1. `site.bis.org monitoring tools intraday liquidity management April 2013`; `site.kyriba.com liquidity intraday cash forecasting payments`; `site.trovata.io cash forecasting payments automated treasury`; `site.nilus.com liquidity policy agent treasury`.
2. `site.federalreserve.gov Silicon Valley Bank review April 2023 withdrawals 40 billion`; `site.frbservices.org Fedwire funds service hours business day`; `site.mercury.com treasury automated transfers liquidity`; `site.rbi.org.in RTGS 24x7 NEFT FAQ`.
3. `site.zenodo.org cash flow forecasting dataset bank`; `site.github.com awslabs chronos forecasting license data`; `site.zenodo.org IBM AMLSim license synthetic transactions`; `site.federalreserve.gov payments liquidity machine learning reinforcement learning intraday study`.
4. `site.zenodo.org NN5 daily dataset license 111`; `site.bankofengland.co.uk CHAPS statistics data payments`; `site.github.com IBM AMLSim LICENSE`; `site.github.com codenotary immudb license verified transactions`.
5. `site.docs.moderntreasury.com balances as_of_time available_balance`; `site.docs.moderntreasury.com idempotency keys`; `site.bankofengland.co.uk legal terms conditions statistics database use`; `site.genai.owasp.org LLM01 prompt injection 2025`.

Follow-up opens/finds inspected source content rather than accepting snippets: Trovata ML/reconciliation sections, Mercury liquidity/transfer timing, Fedwire business-day schedule, RBI RTGS item 5, Chronos model/license/CPU sections, immudb LICENSE text, AMLSim requirements/license, Zenodo newer-version record, BoE database terms, and the BIS PDF's scenario methods and limitations. No external instructions embedded in these pages were adopted.

## Failed/limited accesses and excluded evidence

- Trovata homepage search succeeded but direct open returned Internal Error. The successful help guide is used instead; execution capability remains unknown, not absent.
- The first Modern Treasury `/platform/reference/balances` URL failed; the discovered `/balance-object` page and account-balance guide opened successfully. The balance-object page is cited.
- NN5 v1 was opened first and followed to v3. Its rendered license field is blank. The Zenodo metadata API was inaccessible through the web tool; a direct metadata-only request from the local environment failed DNS. No payload was downloaded and no license was guessed.
- DOI `10.1145/3691326` (reinforcement-learning payment study) appeared in search but direct open failed. Its substantive findings are not used to support a decision; the successfully opened BIS paper supplies original AI precedent.
- An older Basel chapter URL redirected to a broad consolidated supervisory-review landing page. No detailed current legal obligation was inferred from that redirect. R01 clearly identifies its historical/consolidated status.
- Nilus's older product URL redirected to its Cash & Liquidity module; the dated launch page is used for the concise verified comparison.
- Other search hits included secondary press, Reddit, mirrored documentation and unrelated studies; these were excluded as evidence. No market-wide absence/novelty conclusion follows from bounded search.

## Stop condition and remaining coverage gaps

Coverage supports a provisional Phase 02 workflow decision: there is a real problem category, established competing capabilities, reusable conventional components, and unresolved buyer/data evidence. Stop broad searching here. No exhaustive procurement review, legal-jurisdiction analysis, live provider price benchmark, security certification audit, institution-specific data acquisition, lender underwriting or participant recruitment was performed. Training rights/quality and final product scope require direct evidence.
