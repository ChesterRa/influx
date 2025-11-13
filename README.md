# influx

> **High-signal creator index** — A curated, evidence-based collection of 5k–10k active, high-quality X (Twitter) influencers across AI/Tech, Creator/Platform, and Ecosystem domains.

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Schema Version](https://img.shields.io/badge/schema-v1.0.0-green.svg)](schema/bigv.schema.json)

## Purpose

**influx** provides a stable, auditable index of high-activity, non-official, non-brand X authors to support:

- **Prioritized data collection** (e.g., [xoperator](https://github.com/user/xoperator) BigV-first crawling)
- **Ecosystem intelligence** (tracking emerging voices, trends, network dynamics)
- **Research and analysis** (reproducible, versioned datasets with provenance)

### Principles

- **Quality over quantity**: 5k–10k curated authors (strict upper limit 15k) vs. uncurated millions
- **Evidence-first**: Every author includes traceability (sources, metrics windows, provenance hash)
- **Sustainable automation**: 6–12 hour refresh cadence using only free-tier APIs (RUBE MCP Twitter tools)
- **Safe and compliant**: No NSFW/political/controversial by default; brand/official/risk filtering; respects X Terms of Service
- **Open and auditable**: CC BY 4.0 license; schema versioning; governance via PR reviews

### Non-Goals

- Encyclopedia-scale collection (>15k authors)
- Browser automation or paid X API usage
- Black-box scoring or proprietary methods
- Storage of private or sensitive data

---

## Data Model

See [schema/bigv.schema.json](schema/bigv.schema.json) for the full JSON Schema v1.0.0.

### Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Twitter author_id (primary key) |
| `handle` | string | Username without @ (unique) |
| `name` | string | Display name |
| `verified` | string | Verification status: `none`, `blue`, `org`, `legacy` |
| `followers_count` | int | Current follower count |
| `lang_primary` | string | Primary language (ISO 639-1: `en`, `ja`, etc.) |
| `topic_tags` | [string] | Domain tags: `ai_core`, `gpu`, `creator_platform`, `ecosystem`, etc. |

### Metrics (30-day rolling window)

All metrics under `metrics_30d` are computed over the most recent 30 days:

| Field | Description |
|-------|-------------|
| `posts_total` | Total tweets (including replies, retweets) |
| `posts_original` | Original tweets only (excludes replies, retweets) |
| `median_likes` | Median likes per original tweet |
| `p90_likes` | 90th percentile likes per original tweet |
| `median_replies` | Median replies per original tweet |
| `median_retweets` | Median retweets per original tweet |
| `media_rate` | Fraction of original tweets with media (0–1) |

### Scoring & Ranking

| Field | Description |
|-------|-------------|
| `score` | Composite score (0–100): 30% activity + 50% quality + 20% relevance |
| `rank_global` | Global rank by score (1 = highest) |
| `rank_by_topic` | Per-topic ranking: `{topic: rank}` |

### Provenance & Safety

| Field | Description |
|-------|-------------|
| `last_active_at` | ISO 8601 timestamp of most recent original tweet |
| `last_refresh_at` | ISO 8601 timestamp of last metrics update |
| `risk_flags` | Array of flags: `nsfw`, `political`, `controversy`, `spam`, etc. |
| `banned` | Boolean; if true, excluded from exports |
| `sources` | Array of source records with method, timestamp, evidence (tweet IDs) |
| `provenance_hash` | SHA-256 hash of key fields for audit trail |

---

## Usage

### Quick View

```bash
tools/influx-view              # View first 20 records with syntax highlighting
tools/influx-view --lines 10   # View first 10 records
```

### Quick Start

1. **Download latest dataset**:
   ```bash
   curl -L https://github.com/user/influx/releases/latest/download/latest.jsonl.gz -o latest.jsonl.gz
   gunzip latest.jsonl.gz
   ```

2. **Load and filter**:
   ```python
   import json

   with open("latest.jsonl") as f:
       authors = [json.loads(line) for line in f]

   # Filter: AI/Tech domain, English, score ≥ 60
   ai_authors = [
       a for a in authors
       if "ai_core" in a.get("topic_tags", [])
       and a.get("lang_primary") == "en"
       and a.get("score", 0) >= 60
   ]

   print(f"Found {len(ai_authors)} AI/Tech authors")
   ```

3. **Integrate with your pipeline**:
   - Use `handle` to construct X URLs: `https://x.com/{handle}`
   - Use `id` (author_id) for API calls
   - Use `score` and `rank_global` for prioritization

### Data Format

- **Primary format**: `data/latest/latest.jsonl.gz` (gzipped JSONL, one author per line)
- **Sorting**: Descending by `score`, then `followers_count`, then `handle` (lexicographic)
- **Versioning**: `data/latest/manifest.json` includes schema version, timestamp, count, SHA-256 checksum, and generation parameters
- **Snapshots**: Daily snapshots in `data/snapshots/YYYY-MM-DD/bigv-YYYYMMDD.jsonl.gz` (published as GitHub Releases)
- **Uncompressed sources**: `data/uncompressed/YYYY-MM-DD/` (milestone sources for reproducibility, latest only)
- **Quick browse**: `data/samples/top200.jsonl` (first 200 records, uncompressed for preview)

---

## Collection Pipeline

The pipeline uses **RUBE MCP Twitter tools** (free tier) exclusively:

1. **Radar** (`influx-radar`): Analyze keyword trends via `TWITTER_RECENT_SEARCH_COUNTS` (12h window)
2. **Harvest** (`influx-harvest`): Fetch tweets via `TWITTER_RECENT_SEARCH` (8 query groups, 2–3 pages each)
3. **Expand** (`influx-expand`): Extract authors and mentions from tweets; batch `USER_LOOKUP` to fill metadata
4. **Filter**: Apply entry thresholds (verified + ≥30k followers OR ≥50k followers), remove brands/officials via `lists/rules/brand_heuristics.yml`, flag risks via `lists/rules/risk_terms.yml`
5. **Score** (`influx-score`): Compute activity/quality/relevance scores (30-day window)
6. **Export** (`influx-export`): Generate `data/latest/latest.jsonl.gz` with manifest
7. **Validate** (`influx-validate`): Check schema compliance, provenance hashes, manifest integrity

### Update Cadence

- **Incremental refresh**: Every 6–12 hours (update metrics for existing authors, discover new authors)
- **Daily snapshot**: Full export published as GitHub Release (tag: `YYYYMMDD`)
- **Weekly recalc**: Full score recalculation to prevent drift

---

## Governance

### Quality Gates

**Entry thresholds**:
- (Verified AND followers ≥ 30k) OR followers ≥ 50k
- At least 5 original tweets in past 30 days
- Language: `en` or `ja` preferred (others allowed with manual review)

**Brand/official filtering**:
- Name/bio keywords: "Official", "Team", "Support", "PR", "Press", "Media", "News", "Corp", "Store"
- Organization verification (`verified=org`) always flagged
- Domain patterns: `.gov`, `.edu`, news/media domains, e-commerce domains

**Risk filtering** (auto-exclude):
- NSFW, spam, scam, hate speech indicators
- Political officials, campaign accounts
- Controversial/inflammatory content (flagged for manual review)

### Contributing

**Adding authors** (via PR):
1. Provide handle and reason (e.g., "AI researcher at X, author of Y paper")
2. Include 2+ recent (within 30d) original tweet links as evidence
3. Ensure author meets entry thresholds and passes filters
4. Submit PR; CI will validate schema and run filters
5. Maintainers review and merge (or request changes)

**Reporting issues**:
- False positives (wrongly excluded): Open issue with handle and reason
- False negatives (wrongly included): Open issue with handle and evidence
- Heuristic improvements: Propose changes to `lists/rules/*.yml`

**Requesting removal**:
- Authors who wish to be excluded: Open issue or contact maintainers
- Account will be added to `banned` list in next cycle (removed from exports)

### License & Disclaimer

**License**: [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE)
- ✅ Share, remix, build upon for any purpose (including commercial)
- ✅ Attribution required
- ❌ No warranty; use at your own risk

**Disclaimer**:
- This dataset aggregates **publicly available information** from X (Twitter)
- No private, sensitive, or non-public data is collected or stored
- Inclusion does not imply endorsement; exclusion does not imply criticism
- The dataset is provided "as is" without warranty of any kind
- Users must comply with X Terms of Service and applicable laws
- Authors may request removal at any time (contact via GitHub Issues)

---

## Roadmap

### M0 (Week 1) — Bootstrap ✅ In Progress
- [x] Repository structure, schema v1.0.0, LICENSE, README
- [x] Brand/risk heuristics (YAML rules)
- [ ] CLI tools: `influx-radar`, `influx-harvest`, `influx-expand`, `influx-score`, `influx-export`, `influx-validate`
- [ ] First collection run: 400–600 authors via three-path bootstrap
- [ ] CI: schema validation, lint, manifest checks
- [ ] Release: `data/latest/latest.jsonl.gz` with manifest

### M1 (Weeks 2–3) — Scale & Refine
- [ ] Incremental refresh automation (6–12h cadence)
- [ ] Scale to 2k–3k authors
- [ ] Improve heuristics based on manual review (sample 100/week)
- [ ] Daily snapshot automation (GitHub Actions + Releases)
- [ ] Sharding by topic/language (when count > 1.5k)

### M2 (Weeks 4–6) — Production & Analytics
- [ ] Reach 5k–8k authors; maintain churn < 20%/week
- [ ] Parquet export for analysis workflows
- [ ] Visualization dashboard (independent site)
- [ ] Weekly full recalculation (prevent metric drift)
- [ ] Network analysis: co-mentions, topic clusters

---

## Technical Details

**Tools**: Python 3.10+, RUBE MCP (Twitter tools), SQLite (state), DuckDB (optional analytics), JSON Schema validation

**Rate limits**: Respect X API rate limits (300 requests/15min for search, 900/15min for user lookup); exponential backoff, batch requests

**State management**: `state/influx.db` (SQLite) for persistent author data, metrics history, banned list

**Reproducibility**: All data includes provenance (sources, timestamps, hashes); manifest includes generation parameters

---

## Contact & Support

- **Issues**: [GitHub Issues](https://github.com/user/influx/issues)
- **Discussions**: [GitHub Discussions](https://github.com/user/influx/discussions)
- **License**: [CC BY 4.0](LICENSE)

---

**influx** — *high-signal creator index*
