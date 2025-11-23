# influx

High-signal X/Twitter influencer list — functional demo built on the open-source multi-agent framework [CCCC](https://github.com/ChesterRa/cccc). Ready-to-use whitelist of influential individual accounts (non-brand/non-official), curated for downstream ingestion. This open-source bundle is a **download-and-use** minimal set; the full production flow requires CCCC + RUBE MCP (Twitter tools) for data fetching.

[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE) [![Schema](https://img.shields.io/badge/schema-v1.0.0-green.svg)](schema/bigv.schema.json)

**Languages:** English (this file) · [中文](README.zh.md)

## What this is
- A rigorously filtered list of active, individual X.com authors (no brands/officials), aiming for 5k–10k high-value entries.
- Current release (302 records):  
  - JSONL: [`data/release/influx-latest.jsonl`](data/release/influx-latest.jsonl)  
  - Gzipped: [`data/release/influx-latest.jsonl.gz`](data/release/influx-latest.jsonl.gz)  
  - Manifest: [`data/release/manifest.json`](data/release/manifest.json)
- Delivered as data only; you don’t need to run the pipeline to use it.
- Components included here (minimal open-source set):
  - Data: `data/release/` (latest JSONL + manifest)
  - Guard: `scripts/pipeline_guard.sh`
  - Schema: `schema/bigv.schema.json`
  - Rules: `lists/rules/brand_heuristics.yml`, `lists/rules/risk_terms.yml`
  - Sample prefetched JSONL: `data/prefetched.sample.jsonl` (for local filter demo)

## Why it’s useful
- **Content ingestion/ranking:** high signal-to-noise whitelist reduces crawl and processing cost.
- **Research/monitoring:** supports trend tracking, community analysis, influence-network studies.
- **Product bootstrapping:** import a quality author set for recommendations, alerting, sentiment/market intel.

## What’s in the list (selection criteria)
- Individuals only; brand/official/organization accounts excluded via heuristics.
- Thresholds: (Verified AND followers ≥30k) OR followers ≥50k.
- Recency: keeps recent activity fields (metrics_30d*); stale accounts are filtered upstream.
- Evidence: every record carries `sources.evidence` + `fetched_at` for auditability.
- Hard guards: handle and id globally unique; placeholder/“000” followers, mock/test prefixes, non-numeric IDs rejected; strict schema validation enforced.

## Quick use
```bash
cp data/release/influx-latest.jsonl .
# or compressed
cp data/release/influx-latest.jsonl.gz . && gunzip influx-latest.jsonl.gz
```
```python
import json

with open("influx-latest.jsonl") as f:
    authors = [json.loads(line) for line in f]

# Example: English AI authors, score >= 60
ai_authors = [
    a for a in authors
    if "ai_core" in a.get("topic_tags", [])
    and a.get("lang_primary") == "en"
    and a.get("score", 0) >= 60
]
print(len(ai_authors))
```

## Data model (summary)
- Full schema: [`schema/bigv.schema.json`](schema/bigv.schema.json)
- Key fields: `id` (author_id), `handle`, `name`, `verified`, `followers_count`, `lang_primary`, `topic_tags`, `metrics_30d*`, `meta.sources` (with evidence/fetched_at), `provenance_hash`.

## How it’s produced (context; requires external deps)
- Full flow requires: **CCCC + RUBE MCP (Twitter tools)** to fetch users → prefetched JSONL → run `influx-harvest x-lists|bulk --prefetched-users <file>` → enforce `scripts/pipeline_guard.sh` (dedup handle/id, evidence required, placeholder/“000” rejection, strict schema) → publish to `data/release/`.
- This repo ships the minimal set (data + guard + schema + rules + sample prefetched); MCP fetching is not included here.

## License
- Apache-2.0 (covers code and released data).

## Credits
- Built on the CCCC multi-agent framework; thanks to all contributors for curation, filtering, and QA.
