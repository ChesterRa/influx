# D2 Collection Pipeline Contract

**Version**: 1.0.0
**Owner**: PeerA (architecture) + PeerB (implementation)
**Purpose**: Define CLI interface, JSONL I/O format, and rate-limit guardrails for M0 collection tools

---

## Tool Interfaces

### influx-harvest (Author Discovery)

```bash
# GitHub org seeds (40-50% of M0 target)
influx-harvest github-seeds \
  --orgs openai,anthropic,pytorch,huggingface \
  --out github_seeds.jsonl

# Following-graph expansion (40-50% of M0 target)
influx-harvest following \
  --seeds github_seeds.jsonl \
  --pages 2 \
  --out following_expanded.jsonl

# Curated X Lists (10% of M0 target)
influx-harvest x-lists \
  --list-urls lists/seeds/x-lists.txt \
  --out curated.jsonl
```

**Outputs**: JSONL with minimal author records:
```jsonl
{"id": "12345", "handle": "username", "name": "Display Name", "verified": "blue", "followers_count": 50000, "lang_primary": "en", "topic_tags": ["ai"], "sources": [{"method": "github_seed", "fetched_at": "2025-11-13T12:00:00Z", "evidence": "github.com/openai"}]}
```

### influx-score (Scoring & Ranking)

```bash
# Score new authors (30d metrics window)
influx-score update \
  --authors combined.jsonl \
  --window-days 30 \
  --out scored.jsonl
```

**Outputs**: JSONL with added `score`, `rank_global`, `meta` fields (must validate against schema/bigv.schema.json)

### influx-export (Publication)

```bash
# Export to latest release
influx-export latest \
  --input scored.jsonl \
  --out data/latest/
```

**Outputs**:
- `data/latest/latest.jsonl.gz` (sorted by score desc → followers desc → handle lex)
- `data/latest/manifest.json` (schema_version, timestamp, count, sha256)

---

## Data Flow (M0)

```
GitHub Orgs (16) → influx-harvest github-seeds → github_seeds.jsonl (160-200 authors)
                                                          ↓
                                              influx-harvest following (2 pages/seed)
                                                          ↓
                                              following_expanded.jsonl (160-200 authors)
                                                          ↓
                                              merge + dedupe → combined.jsonl (~320-400 unique)
                                                          ↓
X Lists CSV → influx-harvest x-lists → curated.jsonl (40-80 authors)
                                                          ↓
                                              merge + dedupe → all_authors.jsonl (~400-600)
                                                          ↓
                                              influx-score update (30d metrics)
                                                          ↓
                                              scored.jsonl (validated via influx-validate)
                                                          ↓
                                              influx-export latest
                                                          ↓
                                              data/latest/latest.jsonl.gz + manifest.json
```

---

## Gating Filters (Applied at Collection Time)

### Entry Filters (influx-harvest)
1. **Follower threshold**: `(verified == true AND followers_count >= 30000) OR followers_count >= 50000`
2. **Language preference**: `lang_primary IN ('en', 'ja')` (best-effort; not hard gate for M0)
3. **Activity minimum**: Skip if author has 0 recent tweets (indicates suspended/inactive)

### Brand/Official Heuristics (lists/rules/brand_heuristics.yml)
- Name/bio/username contains: `Official`, `News`, `Press`, `PR`, `Team`, `Support`, `Corp`, `Media`, `Store`, `Shop`
- Domain patterns (when available): news sites, e-commerce, corporate homepages
- Action: Set `is_org=true` or `is_official=true`; exclude from M0 pool

### Risk Terms (lists/rules/risk_terms.yml)
- Keywords: `nsfw`, `political`, `controversy`, `spam`, `hate_speech`
- Action: Set `risk_flags=[...]`; exclude from M0 pool by default

---

## Rate Limit Guardrails (POR R1)

### TWITTER_FOLLOWING Pagination
- **Pages per seed**: ≤ 2 pages (~200 follows per seed)
- **Batch size**: Max 50 seeds per run
- **Total API calls per run**: ≤ 150 calls
  - GitHub org members: ~20-30 calls (GITHUB_SEARCH_USERS + GITHUB_GET_A_USER per member)
  - Twitter user lookup: ~50-100 calls (TWITTER_USER_LOOKUP_BY_USERNAMES, batch of 100)
  - Following expansion: ~50-100 calls (TWITTER_FOLLOWING_BY_USER_ID, 2 pages × 50 seeds)

### Error Handling
- **429 TooManyRequests**: Exponential backoff (2s → 4s → 8s → 16s → stop)
- **Per-run caps**: Stop after 150 API calls OR 429 with retry-after > 60s
- **Batch by topic/lang**: Split large runs into smaller batches (max 50 seeds each)

---

## Out-of-Scope (Per Pivot Decision POR#L39)

### Prohibited Endpoints (Paid/Elevated API)
- ❌ `TWITTER_RECENT_SEARCH` (requires paid tier per Aux validation)
- ❌ `TWITTER_RECENT_SEARCH_COUNTS` (requires paid tier)
- ❌ `TWITTER_SEARCH_ADAPTIVE` (hypothetical; not available in free tier)

### Deferred to M1
- Keyword-based discovery (radar + search) - only if free-tier access confirmed
- Incremental 6-12h refresh (M0 = one-shot collection)
- Following-of-following (2-hop expansion; defer until 1-hop validated)

---

## Validation Contract

All JSONL outputs MUST pass:
```bash
python3 tools/influx-validate -s schema/bigv.schema.json <input.jsonl>
```

Exit code 0 = valid; non-zero = schema violation (CI blocks merge).

### Intermediate Artifact Compliance Strategy

**Problem**: Schema requires `meta` object with `score`, `last_refresh_at`, `sources`, `provenance_hash` (all required per schema/bigv.schema.json:L220-225), but intermediate outputs from `influx-harvest` lack scores (scoring occurs in `influx-score`).

**Solution (Option A)**: `influx-harvest` writes **minimal compliant meta placeholders**:
- `meta.score`: `0` (placeholder; actual score computed by influx-score)
- `meta.last_refresh_at`: Current timestamp (ISO 8601)
- `meta.sources`: Array of source objects with `method`, `fetched_at`, `evidence` (already collected during harvest)
- `meta.provenance_hash`: SHA-256 of canonical JSON fields (`id`+`handle`+`followers_count`+`verified`+`sources`)

**Rationale**:
- Enables end-to-end validation at every pipeline stage (harvest → score → export)
- Prevents "validate later" technical debt
- `score=0` is semantically correct for unscored records
- `provenance_hash` based on harvest-time fields is stable and reproducible

**Alternative (Option B - REJECTED)**: Define separate intermediate schema and only validate final artifacts. Rejected because it creates schema drift risk and dual-contract maintenance burden.

---

## Evidence Requirements (M0)

Each author record MUST include:
```json
{
  "sources": [
    {
      "method": "github_seed" | "following_expansion" | "x_list",
      "fetched_at": "ISO 8601 timestamp",
      "evidence": "github.com/org/username" | "@seed_handle" | "x.com/i/lists/123"
    }
  ]
}
```

Provenance enables audit trail and reproducibility.

---

## Acceptance Criteria (M0)

### T000002 github-seeds Probe (Minimal Validation)
**Scope**: Implement `influx-harvest github-seeds` with 4 orgs (openai, anthropic, pytorch, huggingface)

**Output**: `.cccc/work/foreman/probe-20251113/github_seeds.sample.jsonl`

**Acceptance**:
1. **File exists** with ≥5 author records (one JSONL object per line)
2. **Schema validation passes**: `python3 tools/influx-validate -s schema/bigv.schema.json github_seeds.sample.jsonl` exits with code 0
3. **Required fields present** in each record:
   - Core: `id`, `handle`, `name`, `verified`, `followers_count`, `lang_primary`, `topic_tags`
   - Meta placeholders: `meta.score=0`, `meta.last_refresh_at`, `meta.sources` (≥1 item with `method="github_seed"`, `fetched_at`, `evidence`), `meta.provenance_hash`
4. **Dedup/filter logic**: Code includes placeholder functions for deduplication (by `id` or `handle`) and brand/risk filtering (may be no-op for probe)
5. **One-shot command documented**: README at `.cccc/work/foreman/probe-20251113/README.md` includes exact command to reproduce, output path, and timestamp

**Evidence**: Commit with probe output file + README; validation passes in CI

### Following Slice-1 Probe (Minimal Graph Expansion Validation)
**Scope**: Implement `influx-harvest following` with 5 seed authors (first 5 records from `github_seeds.sample.jsonl`) × 1 page per seed

**Input**: `.cccc/work/foreman/probe-20251113/github_seeds.sample.jsonl` (first 5 records only, prioritize those with X user IDs already resolved)

**Output**: `.cccc/work/foreman/probe-20251113/following.sample.jsonl`

**Acceptance**:
1. **Strict entry filters applied**: `(verified == true AND followers_count >= 30000) OR followers_count >= 50000`
2. **Brand/risk rules enforced**: Brand heuristics (`lists/rules/brand_heuristics.yml`) and risk terms (`lists/rules/risk_terms.yml`) applied; branded/risky accounts excluded
3. **Pagination locked**: Exactly 1 page per seed (`--pages=1`), no automatic expansion
4. **Output threshold**: ≥50 author records after filters
5. **Schema validation passes**: `python3 tools/influx-validate -s schema/bigv.schema.json following.sample.jsonl` exits with code 0
6. **Meta placeholders present**: Each record includes Option A meta fields (`score=0`, `last_refresh_at`, `sources` with `method="following_expansion"`, `provenance_hash`)
7. **API call tracking**: Execution logs record actual API call count (expected: 5-10 calls for 5 seeds × 1 page)
8. **Boundary enforcement**: If output count <50, log reason (insufficient follows passing filters, seed accounts suspended, etc.) and **STOP** - do NOT increase pages or seed count without explicit approval

**Command**:
```bash
influx-harvest following \
  --seeds .cccc/work/foreman/probe-20251113/github_seeds.sample.jsonl \
  --limit-seeds 5 \
  --pages 1 \
  --out .cccc/work/foreman/probe-20251113/following.sample.jsonl
```

**Evidence**: Commit with probe output file + command/results in T000002 SUBPOR REV section; validation passes

**Risk Mitigation**: Locks slice boundaries (5 seeds × 1 page) to prevent scope creep during probing; if ≥50 output demonstrates following-graph viability, proceed to full M0; if <50, diagnose bottleneck (filter too strict? seed quality?) before expanding

**Cross-reference**: POR.md:L25 execution guardrails (API≤150/run, TWITTER_FOLLOWING≤2 pages/seed, entry filters, brand/risk rules mandatory, Option A meta placeholders)

### Full M0 Pipeline (End-to-End)
**Scope**: Complete collection pipeline producing 400-600 scored authors

**Acceptance**:
1. **Data flow completes**: GitHub seeds (160-200) → following expansion (160-200) → merge+dedupe (~320-400) → [optional: x-lists +40-80] → score → export
2. **Final output**: `data/latest/latest.jsonl.gz` + `manifest.json`
   - Count: 400-600 authors
   - Sorting: score desc → followers desc → handle lex
   - Manifest: schema_version, timestamp, count, sha256 match file
3. **Schema validation**: All intermediate and final outputs pass `influx-validate`
4. **Rate limits respected**: Execution logs show ≤150 API calls per run; no 429 errors with retry-after >60s
5. **Provenance complete**: Each author has ≥1 source with method/fetched_at/evidence
6. **CI green**: All workflows pass (.github/workflows/validate.yml)

**Evidence**: Release tag YYYYMMDD with data/ artifact; POR Portfolio Health updated; xoperator ingests without error

### Rate Limit Feasibility Confirmation

**≤150 API calls per run** is feasible for M0:
- **GitHub org members** (4 orgs × ~10-15 members): ~50-60 calls (GITHUB_SEARCH_USERS + GITHUB_GET_A_USER per member to extract `twitter_username`)
- **Twitter user lookup** (~40-50 unique handles): ~1-2 calls (TWITTER_USER_LOOKUP_BY_USERNAMES batches 100 usernames per call)
- **Following expansion** (40-50 seeds × 2 pages): ~80-100 calls (TWITTER_FOLLOWING_BY_USER_ID)
- **Total**: ~131-162 calls (probe with 4 orgs is within budget; scale to 16 orgs requires batching into 3-4 runs)

**≤2 pages per seed** trade-off:
- **Pros**: Stays within free-tier rate limits; ~200 follows per seed is sufficient for high-signal diversity
- **Cons**: Misses long-tail follows (seeds with >200 follows get truncated)
- **Mitigation**: Prioritize high-centrality seeds (verified accounts with >100k followers likely follow other high-signal accounts in top 200)

**Acceptance**: M0 execution completes without rate limit blocks; adjust batch size if needed (split 16 orgs into smaller runs)

---

**Last Updated**: 2025-11-13
**Refs**: POR#L20-L26 (M0 Now), POR#L39 (pivot decision), POR#L42 (R1 rate limits)
