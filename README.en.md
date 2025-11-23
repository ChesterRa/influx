# influx

High-signal X/Twitter creator index — built as a functional demo on the open-source multi-agent framework [CCCC](https://github.com/ChesterRa/cccc). Ready-to-use whitelist of influential individual accounts (non-brand/non-official), curated for downstream ingestion.

[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE) [![Schema](https://img.shields.io/badge/schema-v1.0.0-green.svg)](schema/bigv.schema.json)

## What this is
- A rigorously filtered list of active, individual X.com authors (no brands/official accounts), aimed at 5k–10k high-value entries.
- Current release: `data/release/influx-latest.jsonl` (302 records) with matching `manifest.json` (count/sha256/schema_version/timestamp/score_version).
- Delivered data only; no need to run the pipeline to use it.

## Why it’s useful
- **Content ingestion / ranking**: high signal-to-noise whitelist reduces crawl and processing cost.
- **Research / monitoring**: supports trend tracking, community analysis, influence-network studies.
- **Product bootstrapping**: import a quality author set for recommendations, alerting, sentiment/market intel.

## What’s in the list (selection criteria)
- Individuals only; brand/official/organization accounts are excluded via heuristics.
- Entry thresholds: (Verified AND followers ≥30k) OR followers ≥50k.
- Recency: keeps recent activity fields (metrics_30d*); very stale accounts are filtered out upstream.
- Evidence required: every record carries `sources.evidence` + `fetched_at` for auditability.
- Hard guards: handle and id globally unique; placeholder/“000” followers, mock/test prefixes, non-numeric or placeholder IDs are rejected; strict schema validation enforced.

## Download
- Latest data: `data/release/influx-latest.jsonl` (or `.gz`)
- Manifest: `data/release/manifest.json`
> If published on GitHub, these files will be available directly in the repo/release assets.

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
- Full schema: `schema/bigv.schema.json`
- Key fields: `id` (author_id), `handle`, `name`, `verified`, `followers_count`, `lang_primary`, `topic_tags`, `metrics_30d*`, `meta.sources` (with evidence/fetched_at), `provenance_hash`.

## How this is produced (for context, not required to use)
- Two-step, no-local-MCP flow: fetch Twitter users in an MCP-capable environment → save prefetched JSONL → run `influx-harvest x-lists|bulk --prefetched-users <file>` here → enforce `scripts/pipeline_guard.sh` (dedup handle/id, evidence required, placeholder/000 rejection, strict schema) → publish to `data/release/`.
- Only prefetched JSONL inputs are accepted; no manual edits to `latest`.

## License
- Apache-2.0 (covers code and released data).

## Credits
- Built on CCCC multi-agent framework; thanks to contributors for curation, filtering, and QA.
