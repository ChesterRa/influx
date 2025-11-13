<!-- Updated 2025-11-13 11:16 JST by PeerA -->

# POR - Strategic Board

- **North Star**: Build a 5k–10k high-signal X influencer index (AI/Tech/Creator/Ecosystem) with sustainable refresh & provenance, serving downstream prioritization (xoperator) and ecosystem intelligence.
- **Guardrails**: Quality (activity×relevance×safety) > quantity; no paid X API; no browser automation; all sources auditable; licensed CC BY 4.0; 100% RUBE MCP tooling.
- **Non-Goals / Boundaries**: No "encyclopedia-scale" (>15k); no NSFW/political/controversy by default; no private data; no ToS violations; no black-box scoring.

## Deliverables (top-level)
- **D1: Schema & Validation** - `schema/bigv.schema.json` + validation scripts - Both
- **D2: Collection Pipeline** - `tools/influx-{radar,harvest,expand,score,export}` CLI suite - PeerA (with Aux)
- **D3: Initial Dataset** - `data/latest/latest.jsonl.gz` (400–600 authors, M0) - Both
- **D4: Governance & Docs** - `README.md`, `LICENSE`, `docs/schema.md`, heuristics YAMLs - PeerB

## Bets & Assumptions
- **Bet 1 (FALSIFIED for M0)**: 80–90% authors discoverable via GitHub org seeds (twitter_username field) + following-graph expansion (TWITTER_FOLLOWING_BY_USER_ID, 1–2 pages per seed) | **Finding (M0)**: BOTH automation paths blocked - (1) GitHub OAuth unresolved (T000002 pivoted to manual CSV), (2) Twitter v2 enrollment blocker (TWITTER_FOLLOWING_BY_USER_ID fails "client-not-enrolled", 0/5 API calls succeeded) | **Evidence**: T000002 delivered 48 via manual CSV (83% hit rate); following probe failed with credential error | **Pivot**: M0 uses manual CSV approach (PROJECT.md §4.3.2); automation paths deferred to M1 post-credential-fix | **Original success criteria** (Aux refined, defer to M1): twitter_username coverage≥65%, mapping precision≥95%, active handles≥70%, follower Gini≥0.6, org affiliation≥30%, duplicate≤5% | Window: M1 (post-auth-fix)
- **Bet 2**: Brand/official heuristics (name/bio keywords + domain patterns) filter ≥80% noise with <10% false positive | Probe: Manual review of 50 random filtered-out + 50 kept | Evidence: Precision ≥90%, Recall ≥80% | Window: M0 week 1
- **Bet 3**: Score (activity 30% + quality 50% + relevance 20%) correlates with downstream value | Probe: xoperator A/B test top-500 vs random-500 from pool | Evidence: Top-500 yield ≥2× actionable tweets | Window: M1

## Roadmap (Now/Next/Later)
- **Now (M0, ≤1 week, PIVOTED)**:
  - **M0.0 (≤3 days, STAGING)**: Minimal viable release
    - Repo skeleton: schema v1.0.0 ✓, state/influx.db ✓, tools/ stubs ✓, CI (lint+validate) ✓
    - D2 collection pipeline: T000002 manual CSV (48 authors) → influx-score (proxy formula v0) → influx-export (latest.jsonl.gz + manifest)
    - **Scoring**: Proxy formula v0 (log10(followers) + verified_boost, no 30d metrics); M1 will add full formula (activity 30% + quality 50% + relevance 20%)
    - **Release**: `data/latest/latest.jsonl.gz` (48 authors, proxy-scored, manifest notes "v0_proxy_no_metrics")
    - **Acceptance**: Schema validates; CI green; manifest sha256 matches; full pipeline validated (collect → score → export); consumable by xoperator for smoke tests
  - **M0.1 (≤1 week)**: Manual scale to minimal validation threshold
    - Manual CSV curation: T000002's 48 + curated X Lists (~50-70) + public team pages (~50-70) = **150-200 authors**
    - Method: Manual CSV approach (PROJECT.md §4.3.2, 10% path scaled to 25-33%)
    - Re-score with proxy formula v0 + re-export
    - **Acceptance**: Sufficient diversity for xoperator validation (score distribution, AI/Tech/Creator domains, filter testing); state DB queryable
  - **Three-path bootstrap (BLOCKED, DEFERRED M1)**: GitHub-seed + following-graph blocked by auth issues (GitHub OAuth + Twitter v2 enrollment); automation paths move to M1 post-credential-fix
  - **Execution Guardrails** (per d2-pipeline-contract.md, POR R1): ✓ API total calls ≤150/run; ✓ Entry filters: (verified+30k) OR 50k; ✓ Brand/risk rules mandatory (lists/rules/); ✓ Every stage output includes meta placeholders (proxy_score, last_refresh_at, sources≥1, provenance_hash)
  - Heuristics: brand_heuristics.yml ✓, risk_terms.yml ✓
- **Next (M1, ≤6 weeks)**:
  - Scale to 2k–3k via incremental refresh (6–12h cadence)
  - Refine heuristics based on manual review (sample 100/week)
  - Snapshot automation: daily Release w/ tag YYYYMMDD
  - Add shards/ (topic/lang) when count >1.5k
- **Later (M2+, >6 weeks)**:
  - Reach 5k–8k; maintain churn <20%/week
  - Visualization dashboard (independent site)
  - Parquet export for analysis; weekly full recalc to prevent drift
  - ID-map cache optimization (Aux): Persistent GitHub login ↔ X handle cache + early dedupe/aliasing; cuts 30–60% redundant lookups under free tier

## Decision & Pivot Log (recent 5)
- 2025-11-13 11:16 | Bootstrap approach | Use 3-path synthesis (auto-discover + seeds + lists) vs single keyword crawl | Reduces cold-start risk, diversifies sources, auditable | default
- 2025-11-13 11:19 | PIVOT: Collection strategy | Shift from keyword-heavy (60-70%) to GitHub-seed + following-graph (80-90%); TWITTER_RECENT_SEARCH requires paid API (Aux validation) | Eliminates M0 blocking risk, stays within free RUBE MCP, fully automatable | New proportions: 40-50% GitHub org twitter_username + 40-50% TWITTER_FOLLOWING + 10% curated Lists CSV
- 2025-11-13 12:20 | M0 target refinement | Set M0 target to 600 authors (not 400-600 range) based on Aux ROI analysis; 600 provides optimal balance vs 800-1000 (faster evidence with sufficient xoperator validation confidence) | Trades +30-60% time/cost for ±5-8% confidence vs ±3-5% for 800-1000 | Target: 600
- 2025-11-13 13:05 | PIVOT: M0 staged release + Bet 1 FALSIFIED | Twitter v2 enrollment blocker (TWITTER_FOLLOWING fails "client-not-enrolled", 0/5 API calls); 2 consecutive auth blockers in 24h (GitHub OAuth + Twitter v2) falsify Bet 1 automation paths | Stage M0: M0.0 (48 authors, manual CSV, proxy score, today) + M0.1 (150-200 authors, manual curation, ≤1 week); defer automation to M1 | Trades automation elegance for evidence velocity; aligns with Aux risk pivot at ">2 failed retries"; manual CSV now primary M0 path

## Risk Radar & Mitigations (up/down/flat)
- **R1**: Rate limits / quota exhaustion (flat) → Pagination guardrails: TWITTER_FOLLOWING ≤2 pages per seed (~200 follows); batch execution by topic/lang (max 50 seeds/run); exponential backoff on 429; per-run cap: 150 API calls total | Status: Deferred to M1 (following-graph blocked)
- **R1a**: API auth blockers delay M0 evidence (ESCALATED → HIGH) → **Status**: 2 consecutive blockers in 24h - (1) GitHub OAuth (resolved via T000002 manual CSV pivot), (2) **Twitter v2 enrollment blocker (ACTIVE)** - TWITTER_FOLLOWING_BY_USER_ID fails "client-not-enrolled" (Composio credentials lack v2 Project attachment); following probe 0/5 API calls succeeded | **Mitigation (EXECUTED)**: Pivoted to manual CSV approach per Aux decision tree (">2 failed retries → pivot to alternative path"); M0.0 ships 48 authors (manual CSV), M0.1 scales to 150-200 (manual curation); automation paths (GitHub-seed + following-graph) deferred to M1 post-credential-fix | **Finding**: Bet 1 FALSIFIED for M0 - free-tier RUBE MCP has systematic auth/enrollment gating for advanced features
- **R2**: Brand/official heuristic false negatives pollute pool (flat) → Weekly manual review of top-100 + random-50; iterative rule updates
- **R3**: Score drift over time without recalc (flat) → Weekly full recalc; version score formula in manifest; log param changes
- **R4**: xoperator integration breaks if schema changes (down) → Semver in manifest; ext field for custom; ≥90d deprecation notice

## Portfolio Health (in-progress / at-risk only)
| ID | Title | Owner | Stage | Latest evidence (one line) | SUBPOR |
|----|-------|-------|-------|----------------------------|--------|
| T000001 | D1 — Schema validation + CI (M0) | peerB | completed | Commit 78efffe: validator (252L), fixtures (3 valid + 5 invalid), CI workflow, State DB fixes | docs/por/T000001-d1-validate/SUBPOR.md |
| T000002 | D2 — Bootstrap github-seeds probe (M0) | peerB | completed | Commit eab982f: 48 profiles validated, manual CSV + Twitter verify, placeholder meta, 100% schema-compliant | docs/por/T000002-d2-bootstrap/SUBPOR.md |

## Operating Principles (short)
- Falsify before expand; one decidable next step; stop with pride when wrong; Done = evidence.
- Quality闸: verified+30k OR 50k followers; ≥5 original posts/30d; lang en/ja preferred.
- Automation-first: RUBE MCP only; no human large-scale collection; seeds are one-time bootstrap.

## Maintenance & Change Log (append-only, one line each)
- 2025-11-13 11:16 | PeerA | Initialized POR from PROJECT.md; defined M0 roadmap (400–600 authors, 3-path bootstrap) | evidence: POR.md created
- 2025-11-13 11:19 | PeerA | Pivoted collection strategy from keyword-heavy to GitHub-seed + following-graph; added state DB (SQLite); simplified schema | evidence: Aux validation of API tiers, PeerB network expansion alignment
- 2025-11-13 12:14 | PeerA | Added acceptance criteria + intermediate artifact compliance strategy (Option A: meta placeholders) to D2 pipeline contract; confirmed ≤150 API calls feasible for M0 | evidence: docs/por/d2-pipeline-contract.md updated, Foreman directive 000016
- 2025-11-13 12:20 | PeerA | Integrated Aux strategic review: M0 target refined to 600; Bet1 success criteria added (coverage≥65%, precision≥95%, active≥70%, Gini≥0.6, org affiliation≥30%, duplicate≤5%); risk pivot thresholds (>90m/2h/4h); parallelization strategy (following+x-lists concurrent); T000002 completion (48 profiles, 83% hit rate, 100% schema-compliant) calibrates expectations | evidence: Aux review output, T000002 SUBPOR, POR updated
- 2025-11-13 12:28 | PeerA | Added explicit Execution Guardrails to M0 Now section per Foreman directive: API≤150/run, TWITTER_FOLLOWING≤2 pages/seed, entry filters (verified+30k OR 50k), brand/risk rules mandatory, Option A meta placeholders at every stage; cross-references d2-pipeline-contract.md | evidence: Foreman 000019, POR.md:L25
- 2025-11-13 13:05 | PeerA | MAJOR PIVOT: Bet 1 FALSIFIED for M0 (Twitter v2 enrollment blocker + GitHub OAuth = 2 consecutive auth blockers); staged M0 into M0.0 (48 authors, manual CSV, proxy score v0, ≤3 days) + M0.1 (150-200 authors, manual curation, ≤1 week); chose Option S (proxy scoring) for M0 deliverable; automation paths (GitHub-seed + following-graph) deferred to M1 post-credential-fix; manual CSV now primary M0 path | evidence: PeerB following probe failure (0/5 API calls), Aux risk pivot decision tree at ">2 failed retries", POR.md updated (Bet 1, Roadmap, Risk Radar)

## Aux Delegations - Meta-Review/Revise (strategic)
- [x] Review PROJECT.md three-path bootstrap approach for operational gaps or optimization opportunities — Result: Counter-proposal adopted (shift to GitHub-seed + following-graph to avoid paid API dependency) — integrated 2025-11-13 11:19
- [x] Strategic review of M0 scope, Bet1 criteria, collection optimization, risk pivots, artifact quality — Result: Target 600 (not 400-600 range, ROI optimal); refined Bet1 success criteria (coverage≥65%, precision≥95%, active≥70%, follower Gini≥0.6, org affiliation≥30%, duplicate≤5%); parallelize github-seeds + x-lists (30-50% faster); risk pivot at >90m (x-lists parallel), >2h (manual CSV), >4h (re-scope); keep x-lists.txt with schema header; ID-map cache for M2 (cuts 30-60% redundant lookups) — integrated 2025-11-13 12:20
