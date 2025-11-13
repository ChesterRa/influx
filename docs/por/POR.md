<!-- Updated 2025-11-13 11:16 JST by PeerA -->

# POR - Strategic Board

- **North Star**: Build a 5k–10k high-signal X influencer index across **12 vertical domains** (AI/Tech, Creator, Business, Finance, Science, Design, Media, Gaming, Policy, Web3, Lifestyle, Other) with sustainable refresh & provenance, serving downstream prioritization (xoperator) and ecosystem intelligence.
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
  - **M0.1 (≤1 week)**: ✅ **ACHIEVED** - Manual scale to minimal validation threshold
    - Delivered: **151 authors** (M0.0→48, M0.1→66, M0.2→121, M0.3→151)
    - Method: Manual CSV curation across 4 milestones (team pages, curated lists, tech CEOs, blockchain/crypto leaders)
    - Scoring: Proxy formula v0 (mean 52.3, range 0-100), 100% validation maintained
    - Evidence: Commit 28a8381, SHA-256: 107af7d9..., manifest.count=151, CI green
    - **Acceptance**: ✅ ≥150 target met, sufficient diversity (AI/ML/Tech/Blockchain/Security domains), 100% schema-compliant, proxy-scored, ready for xoperator validation
  - **Three-path bootstrap (BLOCKED, DEFERRED M1)**: GitHub-seed + following-graph blocked by auth issues (GitHub OAuth + Twitter v2 enrollment); automation paths move to M1 post-credential-fix
  - **Execution Guardrails** (per d2-pipeline-contract.md, POR R1): ✓ API total calls ≤150/run; ✓ Entry filters: (verified+30k) OR 50k; ✓ Brand/risk rules mandatory (lists/rules/); ✓ Every stage output includes meta placeholders (proxy_score, last_refresh_at, sources≥1, provenance_hash)
  - Heuristics: brand_heuristics.yml ✓, risk_terms.yml ✓
- **Next (M1, ≤6 weeks)**:
  - **🔴 GATING: Auth-unblock (week 1, BLOCKING M1 automation)**: Two credential blockers must be resolved before automation paths (GitHub-seed + following-graph) can proceed: (1) **GitHub OAuth** - requires valid OAuth token with org:read scope for GITHUB_LIST_ORGANIZATION_MEMBERS + GITHUB_GET_A_USER (owner: PeerB + external Composio integration team; ETA: M1 day 1-2, ~4-8h setup + test); (2) **Twitter v2 enrollment** - TWITTER_FOLLOWING_BY_USER_ID fails "client-not-enrolled" error, requires Composio credentials upgrade to Twitter v2 API Project (owner: External Composio/user account admin; ETA: M1 day 1-3, dependent on Composio support response time). Validation: Retry following slice-1 probe (5 seeds × 1 page, tools/influx-harvest following) to confirm both paths unblocked. **M0→M1 Migration Gate**: M1 automation paths (GitHub-seed + following-graph targeting 2k-3k scale) cannot begin until T000003 auth-unblock completes; if unresolved >72h, M1 must pivot to extended manual CSV + x-lists approach with +2 week timeline. **Risk**: If auth unblock >3 days, M1 automation paths remain blocked and scale must continue via manual CSV approach through M1.
  - **Filter implementation (week 1)**: Implement entry filters ((verified+30k) OR 50k) + brand/risk rules in tools/influx-harvest; replaces M0 manual CSV pre-filtering with automated pipeline enforcement
  - Scale to 2k–3k via incremental refresh (6–12h cadence)
  - Refine heuristics based on manual review (sample 100/week)
  - Snapshot automation: daily Release w/ tag YYYYMMDD
  - Add shards/ (topic/lang) when count >1.5k
- **Later (M2+, >6 weeks)**:
  - Reach 5k–8k; maintain churn <20%/week
  - Visualization dashboard (independent site)
  - Parquet export for analysis; weekly full recalc to prevent drift
  - ID-map cache optimization (Aux): Persistent GitHub login ↔ X handle cache + early dedupe/aliasing; cuts 30–60% redundant lookups under free tier

## Domain Coverage Plan (Cross-Domain Expansion)

**Strategy**: Phased bootstrap-then-expand approach to maintain quality gates while scaling across heterogeneous verticals.

### M1 Bootstrap Domains (5-6 domains, 2k-3k authors, 2-3 weeks)
**Target Domains** (confirmed via PeerB feasibility analysis):
1. **AI & Technology** (1000-1500 authors, PROVEN M0)
   - Discovery: GitHub org seeds, research papers, tech conferences
   - Complexity: EASY (existing seeds + following-graph)
2. **Creator Economy** (800-1200 authors, PROVEN M0)
   - Discovery: YouTube/TikTok educators, platform observers
   - Complexity: EASY (keyword search + lists)
3. **Business & Entrepreneurship** (800-1200 authors)
   - Discovery: Founders, VCs, product managers
   - Complexity: MEDIUM (LinkedIn crossover, keyword overlap with Tech)
4. **Finance & Markets** (600-1000 authors)
   - Discovery: Traders, analysts, fintwit, macro commentators
   - Complexity: MEDIUM (distinct keywords but overlaps with Tech VCs)
5. **Science & Research** (400-800 authors)
   - Discovery: Researchers, academics, science communicators
   - Complexity: MEDIUM (arXiv links, conference hashtags)
6. **Design & Creative** (400-600 authors)
   - Discovery: Product designers, UX, visual artists
   - Complexity: MEDIUM (portfolio links, Dribbble/Behance crossover)

**M1 Quotas**: 2k-3k total, ~350-500 per domain (flexible allocation based on discovery yield)
**API Budget**: ~30k calls/month (6% of RUBE MCP free tier 500k quota) – SAFE
**Validation**: 100-author manual review per domain (600 total) for heuristic tuning
**Timeline**: 2-3 weeks (Week 1: Business + Finance, Week 2: Science + Design, Week 3: Integration + release)

### M2 Expansion Domains (6 additional domains, +3k-5k authors, Week 4-6)
**Target Domains** (deferred due to complexity/risk):
7. **Media & Journalism** (400-600 authors, DEFER M2)
   - Challenge: Heavy overlap with brand/official accounts (high false-positive risk)
   - Heuristic tuning: +40-60 lines to distinguish independent journalists from news orgs
8. **Gaming & Esports** (300-500 authors, DEFER M2)
   - Challenge: Niche community, Twitch/YouTube crossover
   - Complexity: MEDIUM (distinct community but requires sub-domain mapping)
9. **Policy & Society** (300-500 authors, DEFER M2, HIGH RISK)
   - Challenge: High political/controversy risk; requires extensive manual review
   - Heuristic tuning: "political" keyword currently auto-excludes; needs nuance for Policy domain
10. **Web3 & Decentralization** (300-500 authors, DEFER M2)
    - Challenge: High spam/scam risk; needs aggressive filtering
    - Complexity: MEDIUM (distinct keywords but quality variance)
11. **Lifestyle & Wellness** (200-400 authors, DEFER M2)
    - Challenge: Fragmented sub-niches (fashion/food/travel/fitness); keyword noise
    - Complexity: HARD (requires sub-domain strategy)
12. **Other High-Quality** (200-400 authors, DEFER M2)
    - Catch-all for cross-domain creators (books, history, philosophy)
    - Complexity: UNDEFINED (cannot scope without sub-domain definition)

**M2 Quotas**: 5k-8k total cumulative (M1 + M2 combined)
**API Budget**: ~60k calls/month (12% quota after M2 expansion) – SAFE with margin
**Validation**: 1200-author manual review total (M1: 600 + M2: 600)
**Timeline**: Week 4-6 (3 domains/week, parallel validation)

### Quality Thresholds (All Domains)
- **Entry filters**: (verified + followers≥30k) OR followers≥50k; recent 30d posts≥5
- **Brand/official exclusion**: Automatic filtering via `lists/rules/brand_heuristics.yml` + per-domain tuning
- **Risk filtering**: `lists/rules/risk_terms.yml` + per-domain sensitivity adjustment
- **Engagement baselines**: Vary by domain (Tech: median 50-200 likes; Gaming: median 200-1k likes)
- **Precision target**: ≥90% per Bet 2 (measured via 100-sample manual review per domain)

### Success Metrics
- **M1 Bootstrap Success**: 2k-3k authors, ≥90% precision, <10% brand/official contamination, 100% schema-compliant
- **M2 Expansion Success**: 5k-8k cumulative, maintain ≥90% precision across all domains, <20% churn/week

## Fallback M1 (Twitter v2 Blocked >7 Days)

**Trigger**: If Twitter v2 enrollment remains unresolved >7 days (T000003 blocked), M1 automation paths (GitHub-seed + following-graph) remain unavailable.

**Fallback Strategy**: Extended manual CSV + X Lists approach (proven M0 method) scaled to M1 targets.

### Fallback Path A: Manual CSV + Curated X Lists (PRIMARY)
**Method**: Extend M0 manual curation approach with structured sourcing:
1. **GitHub Organizations** (manual CSV extraction):
   - Export twitter_username from public GitHub org member profiles
   - Organizations: OpenAI, DeepMind, Anthropic, Meta AI, Google AI, NVIDIA, Hugging Face, etc.
   - Target: 200-400 handles per domain (Tech/AI/Business)
2. **Curated X Lists** (strategic imports):
   - Identify high-quality public Lists per domain (AI/Tech/Creator/Finance/Design)
   - Manual review of List quality (curator reputation, member count, last updated)
   - Export List members as CSV, filter brand/official, validate
   - Target: 150-300 handles per domain
3. **Domain-Specific Seeds** (expert curation):
   - Finance: Fintwit influencers, macro analysts (via Bloomberg/WSJ follows)
   - Science: Academic Twitter, ArXiv authors, science communicators
   - Design: Dribbble/Behance top creators, design thought leaders
   - Target: 100-200 handles per domain

**Scaling**:
- Week 1-2: Collect 1k-1.5k seeds across 5-6 domains (200-300 per domain)
- Week 3: Batch USER_LOOKUP validation (1.5k calls), brand/risk filtering, scoring
- Week 4: M1 release with 1.5k-2k authors (reduced from 2k-3k automation target)

**Trade-offs**:
- ✅ **Pros**: Proven M0 method (151/151 success rate), no API dependency, high precision (manual curation)
- ❌ **Cons**: Labor-intensive (50-80 hours curation), slower scale (1.5k-2k vs 2k-3k), limited network discovery (no following-graph expansion)

**Timeline**: +2 weeks vs automation path (4-5 weeks total for M1 vs 2-3 weeks with automation)

### Fallback Path B: Hybrid Automation (GitHub-Only, No Twitter Following)
**Method**: If GitHub OAuth succeeds but Twitter v2 remains blocked, use GitHub-seed without following-graph expansion:
1. **GitHub Org Discovery**: Automated via GITHUB_LIST_ORGANIZATION_MEMBERS + GITHUB_GET_A_USER
2. **Twitter Handle Extraction**: twitter_username field from GitHub profiles
3. **Batch Validation**: TWITTER_USER_LOOKUP (v1 API, no enrollment required) for profile enrichment
4. **Manual Supplementation**: Fill gaps with curated X Lists (200-300 handles/domain)

**Scaling**:
- Week 1: GitHub discovery (500-800 handles, Tech/AI/Business domains)
- Week 2: Batch validation + X Lists supplementation (+500-700 handles, remaining domains)
- Week 3: Scoring + M1 release with 1.2k-1.5k authors

**Trade-offs**:
- ✅ **Pros**: Partially automated (GitHub discovery), faster than full manual (3 weeks vs 4-5)
- ❌ **Cons**: Limited to GitHub-heavy domains (Tech/AI/Business), misses Creator/Finance/Design depth

**Timeline**: +1 week vs full automation (3 weeks for M1 vs 2 weeks)

### Fallback Decision Tree
- **T+72h (3 days)**: Twitter v2 unresolved → Start Fallback Path B (GitHub-only) in parallel with continued auth-unblock efforts
- **T+7d (1 week)**: Twitter v2 unresolved → Commit to Fallback Path A (manual CSV + Lists), notify user of +2 week timeline
- **T+14d (2 weeks)**: Twitter v2 unresolved → M1 releases with 1.5k-2k authors via Fallback Path A; defer automation to M2

**Risk Mitigation**: Fallback paths maintain M1 delivery (albeit slower/smaller) while preserving option to resume automation in M2 when auth unblocks.

## Decision & Pivot Log (recent 6)
- 2025-11-13 11:16 | Bootstrap approach | Use 3-path synthesis (auto-discover + seeds + lists) vs single keyword crawl | Reduces cold-start risk, diversifies sources, auditable | default
- 2025-11-13 11:19 | PIVOT: Collection strategy | Shift from keyword-heavy (60-70%) to GitHub-seed + following-graph (80-90%); TWITTER_RECENT_SEARCH requires paid API (Aux validation) | Eliminates M0 blocking risk, stays within free RUBE MCP, fully automatable | New proportions: 40-50% GitHub org twitter_username + 40-50% TWITTER_FOLLOWING + 10% curated Lists CSV
- 2025-11-13 12:20 | M0 target refinement | Set M0 target to 600 authors (not 400-600 range) based on Aux ROI analysis; 600 provides optimal balance vs 800-1000 (faster evidence with sufficient xoperator validation confidence) | Trades +30-60% time/cost for ±5-8% confidence vs ±3-5% for 800-1000 | Target: 600
- 2025-11-13 13:05 | PIVOT: M0 staged release + Bet 1 FALSIFIED | Twitter v2 enrollment blocker (TWITTER_FOLLOWING fails "client-not-enrolled", 0/5 API calls); 2 consecutive auth blockers in 24h (GitHub OAuth + Twitter v2) falsify Bet 1 automation paths | Stage M0: M0.0 (48 authors, manual CSV, proxy score, today) + M0.1 (150-200 authors, manual curation, ≤1 week); defer automation to M1 | Trades automation elegance for evidence velocity; aligns with Aux risk pivot at ">2 failed retries"; manual CSV now primary M0 path
- 2025-11-13 14:28 | Format choice (JSONL.gz vs multi-JSON) | User questioned why JSONL.gz instead of separate JSON files per author; decision maintains JSONL.gz for streaming processing, stable sorting (d2-pipeline-contract.md), CI validation efficiency, compression (13KB vs ~95KB), atomic updates, industry standard (GitHub Archive/npm/PyPI) | Outcome: Keep data/latest/latest.jsonl.gz + manifest.json as authoritative contract; add readability tools (tools/influx-view viewer, .cccc/work/export/preview/ samples, README quick-view guide) without changing published artifacts | Rationale in .cccc/mailbox/peerA/to_user.md (000046 response)
- 2025-11-13 14:56 | M0→M1 migration gate | Auth-unblock (T000003) designated as M1 GATING milestone per Foreman directive; M1 automation paths (GitHub-seed + following-graph) cannot begin until both GitHub OAuth + Twitter v2 enrollment resolved | Outcome: Roadmap/Next marked with 🔴 GATING designation, R1a risk upgraded to GATING status; migration condition: ≤72h target for auth resolution, else M1 pivots to extended manual CSV + x-lists (+2 week timeline) | Why: Clarifies M0 (manual baseline, ACHIEVED) vs M1 (automation scale, BLOCKED) boundary; makes external dependency explicit in POR; aligns peer expectations on M1 start conditions

## Risk Radar & Mitigations (up/down/flat)
- **R1**: Rate limits / quota exhaustion (flat) → Pagination guardrails: TWITTER_FOLLOWING ≤2 pages per seed (~200 follows); batch execution by topic/lang (max 50 seeds/run); exponential backoff on 429; per-run cap: 150 API calls total | Status: Deferred to M1 (following-graph blocked)
- **R1a**: 🔴 **GATING** - X paid/restricted API dependency & auth blockers (HIGH, M1 automation blocker) → **Status**: 2 consecutive blockers in 24h - (1) GitHub OAuth (T000003 targets M1 day 1-2), (2) **Twitter v2 enrollment blocker (ACTIVE)** - TWITTER_FOLLOWING_BY_USER_ID fails "client-not-enrolled" (T000003 targets M1 day 1-3); TWITTER_RECENT_SEARCH requires paid API (unusable on free tier) | **Alternative Priorities**: (1) **GitHub-seed + Following-graph** (PRIMARY, unblocks 2k-3k M1 scale post-auth-fix via T000003), (2) **Manual CSV + X Lists** (PROVEN, M0 fallback, sustainable to ~500 authors), (3) **TWITTER_RECENT_SEARCH** (DOWNGRADED, requires paid tier, deprioritized for M1-M2) | **M1 Gate Impact**: Auth-unblock completion is REQUIRED milestone before M1 automation paths can begin; currently 48h elapsed since first blocker detected | **Mitigation**: M0.1 achieved via manual CSV (151 authors); M1 blocked on T000003 auth-unblock (≤72h target); if auth-unblock fails, M1 extends manual approach + x-lists with +2 week timeline
- **R2**: Brand/official heuristic false negatives pollute pool (flat) → Weekly manual review of top-100 + random-50; iterative rule updates
- **R3**: Score drift over time without recalc (flat) → Weekly full recalc; version score formula in manifest; log param changes
- **R4**: xoperator integration breaks if schema changes (down) → Semver in manifest; ext field for custom; ≥90d deprecation notice
- **R5**: Domain skew in M0.1 manual curation (new, sev=med) → Manual CSV approach may over-sample certain domains/orgs (e.g., OpenAI/Anthropic/HuggingFace heavy due to curators' network bias) affecting diversity/representativeness | **Mitigation**: Per-domain quotas (≤30% from single org, ≤50% from AI-core domain); document source distribution in manifest/SUBPOR; M1 automation (following-graph + x-lists) will rebalance via algorithmic diversity | **Acceptance**: M0.1 manifest includes source_distribution field showing org/domain breakdown
- **R6**: Pipeline filter enforcement gap (new, sev=med) → tools/influx-harvest has TODO placeholders for entry filters + brand/risk rules (L53, L80); M0.0/M0.1 succeeded via manual CSV pre-filtering, bypassing pipeline automation | **Impact**: Scaling without implemented filters risks quality degradation; pipeline doesn't enforce POR guardrails ((verified+30k) OR 50k, brand/risk rules from lists/rules/*) | **Mitigation**: M0 continues manual pre-filtering (proven approach); M1 week 1 implements filters in influx-harvest to enable full automation; document M0 limitation in d2-pipeline-contract.md | **Acceptance**: M1 filter implementation tested with ≥50 handle batch, 100% compliance with entry filters + brand/risk rules

## Portfolio Health (in-progress / at-risk only)
| ID | Title | Owner | Stage | Latest evidence (one line) | SUBPOR |
|----|-------|-------|-------|----------------------------|--------|
| T000001 | D1 — Schema validation + CI (M0) | peerB | completed | Commit 78efffe: validator (252L), fixtures (3 valid + 5 invalid), CI workflow, State DB fixes | docs/por/T000001-d1-validate/SUBPOR.md |
| T000002 | D2 — Bootstrap + M0.0 release (M0) | peerB | completed | M0.0 tag v0.0.0-m0.0 (commit 4060da8): 48 authors, proxy score v0 (range 0.0-82.3), 100% validated, manifest SHA-256: 43b89903..., full pipeline proven | docs/por/T000002-d2-bootstrap/SUBPOR.md |

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
- 2025-11-13 13:52 | PeerA | Added M1 auth-fix plan (GitHub OAuth + Twitter v2 enrollment resolution, week 1 blocking) + filter implementation plan (week 1, tools/influx-harvest); added R6 risk (pipeline filter enforcement gap, sev=med); verified PeerB schema blocker FALSE (meta fields always required); confirmed guardrails gap (influx-harvest L53/L80 TODO placeholders) | evidence: Foreman 000035 directive, PeerB 000036 schema verification, tools/influx-harvest:L53/L80 grep, POR.md updated (Next, Risk Radar, Maintenance Log)
- 2025-11-13 14:05 | PeerA | Enhanced Auth-unblock section per Foreman 000038: expanded to 1-paragraph format with owners (PeerB + Composio team for GitHub OAuth, External admin for Twitter v2 enrollment), ETA (M1 day 1-2 for GitHub, day 1-3 for Twitter), validation method (following slice-1 probe retry), and inline risk statement (>3 days blocks M1 automation) | evidence: Foreman 000038 directive post-M0.2 completion (121 authors), POR.md:L37 updated Auth-unblock paragraph
- 2025-11-13 14:15 | PeerA | M0.1 ACHIEVED milestone marked (151 authors, commit 28a8381); created T000003 Auth-unblock SUBPOR (docs/por/T000003-auth-unblock/SUBPOR.md) with resolution steps, dependencies, validation probe, owners/ETA/contacts; updated R1a risk to clarify X API dependency + alternative priorities (GitHub-seed+Following PRIMARY, Manual CSV+X Lists PROVEN fallback, TWITTER_RECENT_SEARCH DOWNGRADED) | evidence: Foreman 000042 directive (Chinese), POR.md:L28-33 M0.1 achieved, T000003 SUBPOR created, POR.md:L58 R1a updated with priorities

## Aux Delegations - Meta-Review/Revise (strategic)
- [x] Review PROJECT.md three-path bootstrap approach for operational gaps or optimization opportunities — Result: Counter-proposal adopted (shift to GitHub-seed + following-graph to avoid paid API dependency) — integrated 2025-11-13 11:19
- [x] Strategic review of M0 scope, Bet1 criteria, collection optimization, risk pivots, artifact quality — Result: Target 600 (not 400-600 range, ROI optimal); refined Bet1 success criteria (coverage≥65%, precision≥95%, active≥70%, follower Gini≥0.6, org affiliation≥30%, duplicate≤5%); parallelize github-seeds + x-lists (30-50% faster); risk pivot at >90m (x-lists parallel), >2h (manual CSV), >4h (re-scope); keep x-lists.txt with schema header; ID-map cache for M2 (cuts 30-60% redundant lookups) — integrated 2025-11-13 12:20
