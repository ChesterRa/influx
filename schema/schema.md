# BigV Author Schema Documentation

**Version**: 1.0.0
**Schema File**: [bigv.schema.json](bigv.schema.json)
**Updated**: 2025-11-13

## Overview

The BigV Author Schema defines the structure for high-quality X (Twitter) influencer records in the **influx** dataset. Each record represents a single author (Twitter user) with:

- **Core identity** (id, handle, name, verification, followers)
- **Metadata** (language, topics)
- **30-day metrics** (activity, engagement)
- **Quality scoring** (composite score, rankings)
- **Provenance** (sources, timestamps, audit hash)
- **Safety** (risk flags, banned status)

## Schema Principles

1. **Simplicity**: Core fields only; extensions go in `ext`
2. **Versioning**: Semver in manifest; backward-compatible additions via `ext`
3. **Auditability**: Every record includes `sources` and `provenance_hash`
4. **Reproducibility**: Timestamps (`last_active_at`, `last_refresh_at`, `fetched_at`) enable time-travel queries
5. **Safety**: `risk_flags` and `banned` support content moderation

---

## Field Reference

### Core Identity

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Twitter author_id (primary key). Numeric string (e.g., "44196397"). Permanent, survives handle changes. |
| `handle` | string | ✅ | Twitter username without @ (e.g., "karpathy"). 1-15 chars, alphanumeric + underscore. Case-insensitive unique key. |
| `name` | string | ✅ | Display name (e.g., "Andrej Karpathy"). May contain Unicode, emoji. 1-100 chars. |
| `verified` | string | ✅ | Verification status: `none`, `blue` (X Blue subscriber), `org` (organization), `legacy` (pre-2023 verified). |
| `followers_count` | integer | ✅ | Current follower count (snapshot at `last_refresh_at`). Used for entry thresholds and ranking. |

**Notes**:
- `id` is immutable; `handle` can change (use `id` as primary key in databases)
- `verified=org` accounts are flagged by `is_org=true` and typically excluded

### Brand/Official Flags

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `is_org` | boolean | `false` | True if heuristics identify account as brand/company/media (see [brand_heuristics.yml](../lists/rules/brand_heuristics.yml)) |
| `is_official` | boolean | `false` | True if heuristics identify account as official/team/support/PR |

**Notes**:
- Accounts with `is_org=true` or `is_official=true` are excluded from the dataset (unless manually whitelisted)
- Heuristics include name/bio keywords, domain patterns, and `verified=org`

### Language & Topics

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `lang_primary` | string | ✅ | Primary language (ISO 639-1: `en`, `ja`, etc.). Inferred from majority of recent original tweets. |
| `lang_tags` | [string] | ❌ | Additional languages (if multilingual). Array of ISO 639-1 codes. |
| `topic_tags` | [string] | ❌ | Domain/topic tags (e.g., `["ai_core", "ml_engineering"]`). See [Topic Tags](#topic-tags) for enum values. |

**Topic Tags**:
- `ai_core`, `ai_research`, `ml_engineering`: AI/ML researchers, engineers, practitioners
- `gpu`, `hardware`, `semiconductors`: Hardware, chips, CUDA, system architecture
- `creator_platform`, `creator_economy`, `content`: Content creators, platform observers, media
- `ecosystem`, `devtools`, `oss`: Developer tools, open source, infrastructure
- `product`, `design`, `startup`: Product management, design, startups
- `policy`, `ethics`, `safety`: AI policy, ethics, safety research
- `other`: Uncategorized or multi-domain

### Metrics (30-day window)

All metrics under `metrics_30d` are computed over the **most recent 30 days** (from `last_refresh_at`).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `posts_total` | integer | ✅ | Total tweets (original + replies + retweets) |
| `posts_original` | integer | ✅ | Original tweets only (excludes replies, retweets). Used for quality scoring. |
| `median_likes` | integer | ✅ | Median likes per original tweet (robust to outliers) |
| `p90_likes` | integer | ✅ | 90th percentile likes per original tweet (captures high-performing tweets) |
| `median_replies` | integer | ❌ | Median replies per original tweet |
| `median_retweets` | integer | ❌ | Median retweets per original tweet |
| `p90_replies` | integer | ❌ | 90th percentile replies per original tweet |
| `p90_retweets` | integer | ❌ | 90th percentile retweets per original tweet |
| `media_rate` | number | ❌ | Fraction of original tweets with media (0–1). Images/videos often indicate higher effort. |
| `urls_topk` | [string] | ❌ | Top-k most frequently linked domains (e.g., `["arxiv.org", "github.com"]`). Used for topic/affiliation inference. |

**Notes**:
- **Median** (robust) + **p90** (high-end performance) provide balanced view of engagement
- Only original tweets count for quality metrics (replies/retweets are conversational, not content)
- `media_rate` and `urls_topk` are optional but useful for relevance scoring

**Example**:
```json
"metrics_30d": {
  "posts_total": 87,
  "posts_original": 42,
  "median_likes": 523,
  "p90_likes": 2104,
  "median_replies": 18,
  "median_retweets": 45,
  "p90_replies": 67,
  "p90_retweets": 203,
  "media_rate": 0.38,
  "urls_topk": ["arxiv.org", "github.com", "openai.com"]
}
```

### Scoring & Ranking

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `score` | number | ✅ | Composite quality score (0–100). Formula: 30% activity + 50% quality + 20% relevance. |
| `rank_global` | integer | ✅ | Global rank by score (1 = highest). Used for prioritization. |
| `rank_by_topic` | object | ❌ | Per-topic ranking (e.g., `{"ai_core": 15}`). Key = topic_tag, value = rank within that topic. |

**Scoring Formula** (v1.0.0):
1. **Activity (30%)**: Normalized posts_original / 30 days (higher = more active)
2. **Quality (50%)**: Log-scaled median + p90 engagement (likes, replies, retweets)
3. **Relevance (20%)**: Topic match + language match + high-signal domain links

**Notes**:
- Score is relative to the entire dataset (scores may shift as dataset grows)
- `rank_global` is stable for prioritization (lower rank = higher priority)
- `rank_by_topic` enables domain-specific filtering (e.g., "top 100 AI researchers")

### Provenance & Timestamps

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `last_active_at` | string (ISO 8601) | ✅ | Timestamp of most recent original tweet. Used to detect inactive accounts. |
| `last_refresh_at` | string (ISO 8601) | ✅ | Timestamp when this record was computed. All metrics reflect data as of this time. |
| `sources` | array | ✅ | Discovery sources (see [Sources](#sources) below) |
| `provenance_hash` | string | ✅ | SHA-256 hash of `(id + followers_count + last_active_at + metrics_30d)`. Enables audit trail and change detection. |

**Sources**:
Each source record includes:
- `method`: Discovery method (`github_seed`, `following_expansion`, `x_list`, `manual`, `keyword_search`)
- `fetched_at`: ISO 8601 timestamp when source was fetched
- `window_days`: Time window for metrics (typically 30)
- `seed_handle` (optional): If `method=following_expansion`, the seed author's handle
- `evidence` (optional): Array of evidence records (tweet IDs, GitHub URLs, etc.)

**Example**:
```json
"sources": [
  {
    "method": "github_seed",
    "fetched_at": "2025-11-12T10:00:00Z",
    "window_days": 30,
    "evidence": [
      {
        "type": "github_profile",
        "value": "https://github.com/karpathy",
        "created_at": "2025-11-12T10:00:00Z"
      }
    ]
  },
  {
    "method": "following_expansion",
    "fetched_at": "2025-11-12T12:00:00Z",
    "window_days": 30,
    "seed_handle": "ylecun",
    "evidence": []
  }
]
```

### Safety & Moderation

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `risk_flags` | [string] | `[]` | Risk/safety flags (e.g., `["nsfw", "spam"]`). See [risk_terms.yml](../lists/rules/risk_terms.yml) for definitions. |
| `banned` | boolean | `false` | If true, author is excluded from exports (user request, ToS violation, etc.) |
| `ban_reason` | string | ❌ | Human-readable reason for ban (required if `banned=true`) |

**Risk Flags**:
- `nsfw`: Adult content, explicit material
- `political`: Political officials, campaign accounts
- `controversy`: Inflammatory, conspiracy theories
- `spam`: Low-quality, promotional, follow-back schemes
- `hate_speech`: Hate symbols, extremist content
- `impersonation_risk`: Parody/fan accounts without clear disclosure
- `scam`: Phishing, investment scams, guaranteed returns

**Notes**:
- Accounts with `risk_flags` are excluded by default (unless manually reviewed and whitelisted)
- `banned` accounts remain in the state DB (for audit trail) but are excluded from `data/latest/latest.jsonl.gz`

### Extension Field

| Field | Type | Description |
|-------|------|-------------|
| `ext` | object | Extension field for custom/experimental data. Does not affect schema validation. Use for downstream-specific metadata. |

**Examples**:
```json
"ext": {
  "xoperator_priority": "high",
  "last_crawled": "2025-11-12T10:00:00Z",
  "custom_score": 92.5,
  "cluster_id": "ai-research-west-coast"
}
```

**Notes**:
- `ext` is schema-agnostic (no validation)
- Use `ext` to avoid breaking schema compatibility when adding custom fields
- Downstream tools (e.g., xoperator) can add their own metadata here

---

## Schema Evolution

### Versioning

Schema follows **Semantic Versioning** (semver):
- **Major** (X.0.0): Breaking changes (field removal, type change, required → optional)
- **Minor** (1.X.0): Backward-compatible additions (new optional fields)
- **Patch** (1.0.X): Clarifications, examples, docs (no schema changes)

**Version** is stored in:
1. `schema/bigv.schema.json` (top-level `version` field)
2. `data/latest/manifest.json` (downstream compatibility check)

### Deprecation Policy

- **90-day notice** before removing fields
- Deprecated fields marked in schema (`deprecated: true`) and docs
- Use `ext` for new experimental fields (promote to core in next minor version if proven useful)

### Compatibility Guarantee

- **Forward compatibility**: Old consumers can read new data (ignore unknown fields)
- **Backward compatibility**: New consumers can read old data (handle missing optional fields)

---

## Validation

### CLI Validation

```bash
# Validate a single record
influx-validate --input data/latest/latest.jsonl.gz --schema schema/bigv.schema.json

# Validate with strict mode (fails on warnings)
influx-validate --input data/latest/latest.jsonl.gz --schema schema/bigv.schema.json --strict
```

### Python Validation

```python
import json
import jsonschema

# Load schema
with open("schema/bigv.schema.json") as f:
    schema = json.load(f)

# Load record
with open("data/latest/latest.jsonl") as f:
    record = json.loads(f.readline())

# Validate
jsonschema.validate(instance=record, schema=schema)
print("✅ Record is valid")
```

### Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `required property 'id' missing` | Missing required field | Add `id` field |
| `'123abc' is not valid under pattern '^[0-9]+$'` | `id` contains non-digits | Ensure `id` is numeric string (Twitter author_id) |
| `'invalid' is not one of ['none', 'blue', 'org', 'legacy']` | Invalid `verified` value | Use only allowed enum values |
| `additionalProperties not allowed` | Unknown top-level field | Move custom fields to `ext` |

---

## Examples

### Minimal Record

```json
{
  "id": "44196397",
  "handle": "elonmusk",
  "name": "Elon Musk",
  "verified": "legacy",
  "followers_count": 152000000,
  "lang_primary": "en",
  "metrics_30d": {
    "posts_total": 150,
    "posts_original": 80,
    "median_likes": 50000,
    "p90_likes": 200000
  },
  "score": 95.2,
  "rank_global": 1,
  "last_active_at": "2025-11-13T00:00:00Z",
  "last_refresh_at": "2025-11-13T02:00:00Z",
  "sources": [
    {
      "method": "manual",
      "fetched_at": "2025-11-12T10:00:00Z",
      "window_days": 30
    }
  ],
  "provenance_hash": "a3f5e1c8b9d4f2e7a6b3c9d8e5f1a2b7c4d9e6f3a8b5c2d7e4f9a1b6c3d8e5f2"
}
```

### Full Record (with optional fields)

```json
{
  "id": "23839638",
  "handle": "karpathy",
  "name": "Andrej Karpathy",
  "verified": "blue",
  "followers_count": 823400,
  "is_org": false,
  "is_official": false,
  "lang_primary": "en",
  "lang_tags": ["en"],
  "topic_tags": ["ai_core", "ml_engineering"],
  "metrics_30d": {
    "posts_total": 87,
    "posts_original": 42,
    "median_likes": 523,
    "p90_likes": 2104,
    "median_replies": 18,
    "median_retweets": 45,
    "p90_replies": 67,
    "p90_retweets": 203,
    "media_rate": 0.38,
    "urls_topk": ["arxiv.org", "github.com", "openai.com"]
  },
  "score": 87.3,
  "rank_global": 15,
  "rank_by_topic": {
    "ai_core": 8,
    "ml_engineering": 5
  },
  "last_active_at": "2025-11-12T14:32:10Z",
  "last_refresh_at": "2025-11-13T02:00:00Z",
  "risk_flags": [],
  "banned": false,
  "sources": [
    {
      "method": "github_seed",
      "fetched_at": "2025-11-12T10:00:00Z",
      "window_days": 30,
      "evidence": [
        {
          "type": "github_profile",
          "value": "https://github.com/karpathy",
          "created_at": "2025-11-12T10:00:00Z"
        }
      ]
    },
    {
      "method": "following_expansion",
      "fetched_at": "2025-11-12T12:00:00Z",
      "window_days": 30,
      "seed_handle": "ylecun"
    }
  ],
  "provenance_hash": "b7e4f9a1c8d5e2a6f3b9c4d7e8f5a2b1c6d3e9f4a7b8c5d2e1f6a3b9c8d4e7f5",
  "ext": {
    "xoperator_priority": "high",
    "notes": "Stanford PhD, ex-OpenAI, Tesla Autopilot"
  }
}
```

---

## See Also

- [bigv.schema.json](bigv.schema.json) — JSON Schema file
- [brand_heuristics.yml](../lists/rules/brand_heuristics.yml) — Brand/official filtering rules
- [risk_terms.yml](../lists/rules/risk_terms.yml) — Risk/safety flagging rules
- [README.md](../README.md) — Project overview and usage
