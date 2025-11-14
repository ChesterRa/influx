# T000002-d2-bootstrap: GitHub Seeds Probe

**Status**: ✓ COMPLETE
**Date**: 2025-11-13
**Owner**: PeerB
**Timebox**: 0.5d

## Objective

Validate minimum viable harvest pipeline (OpenAI/Anthropic/Huggingface teams) with schema-compliant output including placeholder meta fields.

## Approach

**Strategic Pivot**: GitHub API blocked on OAuth → Manual CSV seeds + Twitter verification (PROJECT.md §4.3.2, 10% M0 approach).

### Execution Steps

1. **Manual seed curation** (.cccc/work/foreman/manual_seeds.txt)
   - 60 Twitter handles from public team pages (OpenAI, Anthropic, Huggingface)
   - Filtered to 58 valid handles (≤15 chars, valid pattern)

2. **Twitter API batch verification** (TWITTER_USER_LOOKUP_BY_USERNAMES)
   - Verified 48/58 profiles (83% hit rate)
   - 9 handles not found: AkshatRastogi7, _joecarlini, _joshachiam, _willfalcon, amanrsanger, clefourrier, mervenoyann, polynoamial, reach_vb

3. **Schema-compliant JSONL generation**
   - Format: bigv.schema.json v1.0.0
   - Placeholder meta per Foreman directive (Option A):
     - `score`: 0.0 (placeholder)
     - `last_refresh_at`: 2025-11-13T03:13:38Z
     - `sources`: [method=manual_seed, evidence=curated team list]
     - `provenance_hash`: SHA-256 of id|username|followers|method|timestamp

4. **Validation**
   - `python3 tools/influx-validate -s schema/bigv.schema.json github_seeds.sample.jsonl`
   - Result: ✓ 48/48 records valid

## Results

- **Output**: `github_seeds.sample.jsonl` (48 records, 22.6KB)
- **Acceptance**: ✓ ≥40 handles (48 delivered, 120% of target)
- **Schema compliance**: ✓ 100% (48/48 validated)
- **Provenance**: ✓ All records include method=manual_seed with evidence

## Sample Profiles

```
AlecRad (Alec Radford): 60.2k followers, verified:blue
DarioAmodei (Dario Amodei): 85.8k followers, verified:blue
DrJimFan (Jim Fan): 139k followers, verified:blue
EMostaque (Emad Mostaque): 323k followers, verified:blue
jackclarkSF (Jack Clark): 97.8k followers, verified:blue
```

## One-time Command

```bash
# Manual CSV approach (executed via RUBE workbench)
python3 -c "
import json
from composio import run_composio_tool, upload_local_file
# ... (see workbench session: influx-harvest-twitter-verify)
"
```

## Trade-offs

- **Pro**: Immediate execution (no OAuth blocker), high-quality seed list, validates full pipeline
- **Con**: Manual curation required, 17% attrition (handles not found/invalid)
- **Next**: Implement GitHub API path once OAuth completes (automated org member discovery)

## Evidence

- File: `.cccc/work/foreman/probe-20251113/github_seeds.sample.jsonl` (48 records)
- Validation: `influx-validate -s schema/bigv.schema.json github_seeds.sample.jsonl :: ✓ 48/48`
- Commit: [pending]

---

## M0 Export and Snapshot Commands (Added: 2025-11-13T06:15:00Z)

Per Foreman#000051, documenting one-click export and validation commands:

### Export to Latest (Authoritative Release)

```bash
# Export scored authors to data/latest/
python3 tools/influx-export latest \
  --input .cccc/work/m03/complete_scored.jsonl \
  --out data/latest/

# Validate
python3 tools/influx-validate \
  -s schema/bigv.schema.json \
  data/latest/latest.jsonl.gz
```

**Expected output**: `data/latest/latest.jsonl.gz` + `manifest.json`

### Generate Daily Snapshot

```bash
# Export to data/snapshots/YYYY-MM-DD/
python3 tools/influx-export snapshot \
  --date 2025-11-13 \
  --input .cccc/work/m03/complete_scored.jsonl \
  --out data/snapshots

# Validate
python3 tools/influx-validate \
  -s schema/bigv.schema.json \
  data/snapshots/2025-11-13/bigv-20251113.jsonl.gz
```

**Expected output**: `data/snapshots/2025-11-13/bigv-20251113.jsonl.gz` + `manifest.json`

### M0.3 Results (151 authors)

- **Latest**: SHA-256 `107af7d9e86a45f48561b26e5f93a5bc1a825dda1c8a7ff948f469689bdf70ab`
- **Snapshot 2025-11-13**: SHA-256 `107af7d9e86a45f48561b26e5f93a5bc1a825dda1c8a7ff948f469689bdf70ab` (identical)
- **Validation**: 151/151 records pass (100%)
- **Score**: mean 52.3, range 0.0-100.0
