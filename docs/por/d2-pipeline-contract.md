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

**Last Updated**: 2025-11-13
**Refs**: POR#L20-L26 (M0 Now), POR#L39 (pivot decision), POR#L42 (R1 rate limits)
