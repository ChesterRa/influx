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
- **Bet 1 (REVISED)**: 80–90% authors discoverable via GitHub org seeds (twitter_username field) + following-graph expansion (TWITTER_FOLLOWING_BY_USER_ID, 1–2 pages per seed) | Probe: Fetch 15 GitHub orgs (OpenAI/Anthropic/HF/etc) members → lookup Twitter → expand via followings | Evidence: ≥320 candidates after filters | Window: M0 week 1
- **Bet 2**: Brand/official heuristics (name/bio keywords + domain patterns) filter ≥80% noise with <10% false positive | Probe: Manual review of 50 random filtered-out + 50 kept | Evidence: Precision ≥90%, Recall ≥80% | Window: M0 week 1
- **Bet 3**: Score (activity 30% + quality 50% + relevance 20%) correlates with downstream value | Probe: xoperator A/B test top-500 vs random-500 from pool | Evidence: Top-500 yield ≥2× actionable tweets | Window: M1

## Roadmap (Now/Next/Later)
- **Now (M0, ≤2 weeks)**:
  - Repo skeleton: schema v1.0.0 (simplified: core+metrics_30d+meta+ext), state/influx.db (SQLite), tools/ stubs, CI (lint+validate)
  - Three-path bootstrap (REVISED): (1) GitHub org seeds (twitter_username) → 160–200, (2) following-graph expansion (TWITTER_FOLLOWING) → 160–200, (3) curated X Lists CSV → 40–80
  - Heuristics: brand_heuristics.yml, risk_terms.yml; scoring formula v1 (activity 30% + quality 50% + relevance 20%)
  - First release: `data/latest/latest.jsonl.gz` (400–600, scored, manifest.json); state DB persists history
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

## Decision & Pivot Log (recent 5)
- 2025-11-13 11:16 | Bootstrap approach | Use 3-path synthesis (auto-discover + seeds + lists) vs single keyword crawl | Reduces cold-start risk, diversifies sources, auditable | default
- 2025-11-13 11:19 | PIVOT: Collection strategy | Shift from keyword-heavy (60-70%) to GitHub-seed + following-graph (80-90%); TWITTER_RECENT_SEARCH requires paid API (Aux validation) | Eliminates M0 blocking risk, stays within free RUBE MCP, fully automatable | New proportions: 40-50% GitHub org twitter_username + 40-50% TWITTER_FOLLOWING + 10% curated Lists CSV

## Risk Radar & Mitigations (up/down/flat)
- **R1**: Rate limits / quota exhaustion (up) → Strict page caps (2–3 max), exponential backoff, split by topic/lang batches
- **R2**: Brand/official heuristic false negatives pollute pool (flat) → Weekly manual review of top-100 + random-50; iterative rule updates
- **R3**: Score drift over time without recalc (flat) → Weekly full recalc; version score formula in manifest; log param changes
- **R4**: xoperator integration breaks if schema changes (down) → Semver in manifest; ext field for custom; ≥90d deprecation notice

## Portfolio Health (in-progress / at-risk only)
| ID | Title | Owner | Stage | Latest evidence (one line) | SUBPOR |
|----|-------|-------|-------|----------------------------|--------|
| (none yet) | | | | | |

## Operating Principles (short)
- Falsify before expand; one decidable next step; stop with pride when wrong; Done = evidence.
- Quality闸: verified+30k OR 50k followers; ≥5 original posts/30d; lang en/ja preferred.
- Automation-first: RUBE MCP only; no human large-scale collection; seeds are one-time bootstrap.

## Maintenance & Change Log (append-only, one line each)
- 2025-11-13 11:16 | PeerA | Initialized POR from PROJECT.md; defined M0 roadmap (400–600 authors, 3-path bootstrap) | evidence: POR.md created
- 2025-11-13 11:19 | PeerA | Pivoted collection strategy from keyword-heavy to GitHub-seed + following-graph; added state DB (SQLite); simplified schema | evidence: Aux validation of API tiers, PeerB network expansion alignment

## Aux Delegations - Meta-Review/Revise (strategic)
- [x] Review PROJECT.md three-path bootstrap approach for operational gaps or optimization opportunities — Result: Counter-proposal adopted (shift to GitHub-seed + following-graph to avoid paid API dependency) — integrated 2025-11-13 11:19
