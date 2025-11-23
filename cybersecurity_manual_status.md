# Cybersecurity Candidates - Manual Processing Required

## Status Update
PeerA has reprocessed M12 batch, adding 4 new authors (total: 259).  
Cybersecurity candidates discovered earlier remain ready for processing.

## Processing Blockage
RUBE MCP environment not available in current context for `influx-harvest` pipeline.

## Ready Candidates
1. **STÖK (@stokfredrik)** - 135,953 followers ✅
2. **Phillip Wylie (@PhillipWylie)** - 51,682 followers ✅

## Manual Processing Workflow
```bash
# When RUBE MCP available:
./tools/influx-harvest bulk --handles-file cybersecurity_candidates.csv --out cybersecurity_harvested.jsonl --min-followers 50000 --verified-min-followers 30000

# Score and merge:
python add_meta_score.py cybersecurity_harvested.jsonl cybersecurity_scored.jsonl
python merge_new_authors.py cybersecurity_scored.jsonl

# Validate:
./tools/influx-validate --strict -s schema/bigv.schema.json -m data/latest/manifest.json data/latest/latest.jsonl
```

## Strategic Impact
- **Current**: 259 authors (100% validation compliant)
- **Potential**: +2 cybersecurity authors = 261 total
- **M1 Progress**: 52.2% of 500 minimum target

## Recommendation
Coordinate with PeerA for RUBE MCP environment access to process these candidates through the official pipeline.

---
*Discovery complete, pipeline processing blocked by environment constraints*