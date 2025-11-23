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

# Duplicate, placeholder ID, mock/fixture check, manifest consistency
python3 - "$INPUT" "$MANIFEST" <<'PY'
import json, sys, hashlib, re
from collections import Counter
from pathlib import Path
input_path = Path(sys.argv[1])
man_path = Path(sys.argv[2])

PLACEHOLDER_PREFIX = '1234567890000000'
MOCK_PREFIXES = ('test_', 'mock_', 'fixture_', 'sample_', 'tmp_')

data = [json.loads(line) for line in input_path.read_text().splitlines() if line.strip()]
handles = [item.get('handle') for item in data]
counts = Counter(handles)
dups = [h for h,c in counts.items() if c>1]
if dups:
    print(f"ERROR: duplicate handles detected: {dups[:5]} (total dup handles={len(dups)})", file=sys.stderr)
    sys.exit(1)

fake_ids = [item.get('id') for item in data if str(item.get('id','')).startswith(PLACEHOLDER_PREFIX) or not str(item.get('id','')).isdigit()]
if fake_ids:
    print(f"ERROR: detected placeholder/non-numeric ids (prefix {PLACEHOLDER_PREFIX}), count={len(fake_ids)}; aborting", file=sys.stderr)
    sys.exit(1)

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
print(f"OK: duplicates=0, placeholder_ids=0, mock_handles=0, count={len(data)}, sha256 matches manifest {sha}")
PY

# Strict validation
python3 tools/influx-validate --strict -s "$SCHEMA" -m "$MANIFEST" "$INPUT"

echo "pipeline_guard: PASS for $INPUT"
