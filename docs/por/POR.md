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
- **Bet 1 (REVISED)**: 80–90% authors discoverable via GitHub org seeds (twitter_username field) + following-graph expansion (TWITTER_FOLLOWING_BY_USER_ID, 1–2 pages per seed) | Probe: Fetch 15 GitHub orgs (OpenAI/Anthropic/HF/etc) members → lookup Twitter → expand via followings | Evidence: ≥320 candidates after filters | Success criteria (Aux refined): twitter_username coverage≥65%, mapping precision≥95% (manual N=50 audit), active handles (tweeted ≤90d)≥70%, follower heavy-tail (Gini≥0.6; top decile ≥50% of followers), org/verified affiliation≥30%, duplicate/alias rate≤5% | T000002 calibration: 83% hit rate (48/58 manual CSV), 17% attrition (handles not found) | Window: M0 week 1
- **Bet 2**: Brand/official heuristics (name/bio keywords + domain patterns) filter ≥80% noise with <10% false positive | Probe: Manual review of 50 random filtered-out + 50 kept | Evidence: Precision ≥90%, Recall ≥80% | Window: M0 week 1
- **Bet 3**: Score (activity 30% + quality 50% + relevance 20%) correlates with downstream value | Probe: xoperator A/B test top-500 vs random-500 from pool | Evidence: Top-500 yield ≥2× actionable tweets | Window: M1

## Roadmap (Now/Next/Later)
- **Now (M0, ≤2 weeks)**:
  - Repo skeleton: schema v1.0.0 (simplified: core+metrics_30d+meta+ext), state/influx.db (SQLite), tools/ stubs, CI (lint+validate)
  - Three-path bootstrap (REVISED): (1) Manual CSV seeds (T000002: 48 profiles) + following-graph expansion (TWITTER_FOLLOWING) → 200–250, (2) [optional] curated X Lists CSV → 40–80 | **Strategy (Aux)**: Parallelize following-graph + x-lists for 30-50% faster time-to-evidence; merge+dedupe at end
  - D2 collection pipeline: [Contract: docs/por/d2-pipeline-contract.md] influx-harvest (github-seeds/following/x-lists) → influx-score (30d metrics) → influx-export (latest.jsonl.gz + manifest)
  - **Execution Guardrails** (per d2-pipeline-contract.md, POR R1): ✓ API total calls ≤150/run; ✓ TWITTER_FOLLOWING ≤2 pages/seed; ✓ Entry filters: (verified+30k) OR 50k; ✓ Brand/risk rules mandatory (lists/rules/); ✓ Every stage output includes Option A meta placeholders (score=0, last_refresh_at, sources≥1, provenance_hash)
  - Heuristics: brand_heuristics.yml, risk_terms.yml; scoring formula v1 (activity 30% + quality 50% + relevance 20%)
  - First release: `data/latest/latest.jsonl.gz` (**target: 600 per Aux ROI analysis**, scored, manifest.json); state DB persists history
  - Acceptance: Schema validates; CI green; manifest sha256 matches; xoperator ingests without error; state DB queryable
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

## Risk Radar & Mitigations (up/down/flat)
- **R1**: Rate limits / quota exhaustion (up) → Pagination guardrails: TWITTER_FOLLOWING ≤2 pages per seed (~200 follows); batch execution by topic/lang (max 50 seeds/run); exponential backoff on 429 (2s→4s→8s→16s→stop); per-run cap: 150 API calls total
- **R1a**: API auth blockers delay M0 evidence (resolved via T000002 manual pivot) → Risk pivot decision tree (Aux): If auth blocker >90m unresolved, start alternative path in parallel (x-lists/manual CSV); if >2h or >2 failed retries, pivot to manual CSV seeds + following-graph; if >4h, re-scope M0 to alternative-path-only evidence and unblock auth offline | T000002 precedent: Manual CSV delivered 48 profiles in ~2h vs waiting for GitHub OAuth
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

## Aux Delegations - Meta-Review/Revise (strategic)
- [x] Review PROJECT.md three-path bootstrap approach for operational gaps or optimization opportunities — Result: Counter-proposal adopted (shift to GitHub-seed + following-graph to avoid paid API dependency) — integrated 2025-11-13 11:19
- [x] Strategic review of M0 scope, Bet1 criteria, collection optimization, risk pivots, artifact quality — Result: Target 600 (not 400-600 range, ROI optimal); refined Bet1 success criteria (coverage≥65%, precision≥95%, active≥70%, follower Gini≥0.6, org affiliation≥30%, duplicate≤5%); parallelize github-seeds + x-lists (30-50% faster); risk pivot at >90m (x-lists parallel), >2h (manual CSV), >4h (re-scope); keep x-lists.txt with schema header; ID-map cache for M2 (cuts 30-60% redundant lookups) — integrated 2025-11-13 12:20
