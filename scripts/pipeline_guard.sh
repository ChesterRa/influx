#!/usr/bin/env bash
set -euo pipefail

INPUT=${1:-data/latest/latest.jsonl}
MANIFEST=${2:-data/latest/manifest.json}
SCHEMA=${3:-schema/bigv.schema.json}

if [[ ! -f "$INPUT" ]]; then
  echo "ERROR: input file not found: $INPUT" >&2
  exit 1
fi
if [[ ! -f "$MANIFEST" ]]; then
  echo "ERROR: manifest file not found: $MANIFEST" >&2
  exit 1
fi
if [[ ! -f "$SCHEMA" ]]; then
  echo "ERROR: schema file not found: $SCHEMA" >&2
  exit 1
fi

# Duplicate, placeholder ID, mock/fixture check, evidence check, manifest consistency
python3 - "$INPUT" "$MANIFEST" <<'PY'
import json, sys, hashlib
from collections import Counter
from pathlib import Path
input_path = Path(sys.argv[1])
man_path = Path(sys.argv[2])

PLACEHOLDER_PREFIX = '1234567890000000'
MOCK_PREFIXES = ('test_', 'mock_', 'fixture_', 'sample_', 'tmp_')

data = [json.loads(line) for line in input_path.read_text().splitlines() if line.strip()]
handles = [item.get('handle') for item in data]
ids = [str(item.get('id', '')) for item in data]

# Handle uniqueness
dup_handles = [h for h,c in Counter(handles).items() if c>1]
if dup_handles:
    print(f"ERROR: duplicate handles detected: {dup_handles[:5]} (total dup handles={len(dup_handles)})", file=sys.stderr)
    sys.exit(1)

# ID uniqueness
dup_ids = [i for i,c in Counter(ids).items() if i and c>1]
if dup_ids:
    print(f"ERROR: duplicate ids detected: {dup_ids[:5]} (total dup ids={len(dup_ids)})", file=sys.stderr)
    sys.exit(1)

# Placeholder / non-numeric IDs
fake_ids = [item.get('id') for item in data if str(item.get('id','')).startswith(PLACEHOLDER_PREFIX) or not str(item.get('id','')).isdigit()]
if fake_ids:
    print(f"ERROR: detected placeholder/non-numeric ids (prefix {PLACEHOLDER_PREFIX}), count={len(fake_ids)}; aborting", file=sys.stderr)
    sys.exit(1)

# Twitter ID length validation (64-bit integer max 19 digits)
long_ids = []
for item in data:
    user_id = str(item.get('id', ''))
    if user_id and len(user_id) > 19:
        long_ids.append((item.get('handle', 'unknown'), user_id, len(user_id)))
if long_ids:
    print(f"ERROR: detected Twitter IDs exceeding 64-bit integer limit (max 19 digits), count={len(long_ids)}, sample={long_ids[:5]}", file=sys.stderr)
    sys.exit(1)

# Mock handles
mock_handles = [h for h in handles if h and h.lower().startswith(MOCK_PREFIXES)]
if mock_handles:
    print(f"ERROR: mock/test handles detected: {mock_handles[:5]} (total mock handles={len(mock_handles)})", file=sys.stderr)
    sys.exit(1)

# Followers count sanity: reject round-number placeholders ending with '000'
bad_followers = []
for item in data:
    fc = item.get('followers_count')
    if isinstance(fc, int) and fc % 1000 == 0:
        bad_followers.append((item.get('handle'), fc))
if bad_followers:
    print(f"ERROR: suspicious followers_count ending with '000' detected (possible placeholder), count={len(bad_followers)}, sample={bad_followers[:5]}", file=sys.stderr)
    sys.exit(1)

# Sequential placeholder followers (123456, 234567, etc.)
import re
sequential_followers = []
for item in data:
    fc = str(item.get('followers_count', ''))
    if re.match(r'^\d*(?:12345|23456|34567|45678|56789)', fc):
        sequential_followers.append((item.get('handle'), item.get('followers_count')))
if sequential_followers:
    print(f"ERROR: sequential placeholder followers_count detected (123456, 234567, etc.), count={len(sequential_followers)}, sample={sequential_followers[:5]}", file=sys.stderr)
    sys.exit(1)

# Placeholder URL detection in profile field
placeholder_urls = []
for item in data:
    url = item.get('url', '')
    if url and ('placeholder' in url.lower() or 't.co/placeholder' in url):
        placeholder_urls.append((item.get('handle'), url))
if placeholder_urls:
    print(f"ERROR: placeholder URLs detected in profile field, count={len(placeholder_urls)}, sample={placeholder_urls[:5]}", file=sys.stderr)
    sys.exit(1)

# Schema drift detection - metrics_30d is deprecated in favor of ext.activity_metrics
schema_drift = []
for item in data:
    if 'metrics_30d' in item:
        schema_drift.append(item.get('handle'))
if schema_drift:
    print(f"ERROR: schema drift detected - deprecated 'metrics_30d' field found (use 'ext.activity_metrics' instead), count={len(schema_drift)}, sample={schema_drift[:5]}", file=sys.stderr)
    sys.exit(1)

# Evidence required (sources.evidence + fetched_at)
missing_evidence = []
for item in data:
    srcs = item.get('sources') or item.get('meta', {}).get('sources') or []
    if not isinstance(srcs, list) or len(srcs)==0:
        missing_evidence.append(item.get('handle'))
        continue
    ok = False
    for s in srcs:
        if isinstance(s, dict) and s.get('evidence') and s.get('fetched_at'):
            ok = True
            break
    if not ok:
        missing_evidence.append(item.get('handle'))
if missing_evidence:
    print(f"ERROR: sources.evidence/fetched_at missing for {len(missing_evidence)} records, sample={missing_evidence[:5]}", file=sys.stderr)
    sys.exit(1)

# Provenance hash validation - prevent empty provenance_hash
empty_provenance = []
for item in data:
    prov_hash = item.get('provenance_hash', '')
    if not prov_hash or prov_hash == '':
        empty_provenance.append(item.get('handle'))
if empty_provenance:
    print(f"ERROR: empty provenance_hash detected (data corruption risk), count={len(empty_provenance)}, sample={empty_provenance[:5]}", file=sys.stderr)
    sys.exit(1)

sha = hashlib.sha256(input_path.read_bytes()).hexdigest()
manifest = json.loads(man_path.read_text())
mc = manifest.get('count')
if mc is not None and mc != len(data):
    print(f"ERROR: manifest count {mc} != actual {len(data)}", file=sys.stderr)
    sys.exit(1)
ms = manifest.get('sha256')
if ms and ms != sha:
    print(f"ERROR: manifest sha256 mismatch {ms} != {sha}", file=sys.stderr)
    sys.exit(1)
print(f"OK: dup_handles=0, dup_ids=0, placeholder_ids=0, mock_handles=0, long_ids=0, placeholder_urls=0, provenance_hash_ok, evidence_ok, count={len(data)}, sha256 matches manifest {sha}")
PY

# Strict validation
python3 tools/influx-validate --strict -s "$SCHEMA" -m "$MANIFEST" "$INPUT"

echo "pipeline_guard: PASS for $INPUT"
