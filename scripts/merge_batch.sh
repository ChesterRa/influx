#!/usr/bin/env bash
# merge_batch.sh - Safely merge a batch file into the main dataset with quality enforcement
# Usage: ./scripts/merge_batch.sh <batch_file> [dataset_file] [manifest_file] [schema_file]
#
# This script enforces zero-tolerance quality policy by:
# 1. Creating a temporary merged file
# 2. Running pipeline_guard.sh to check for duplicates and quality violations
# 3. Only committing the merge if pipeline_guard passes
# 4. Updating manifest with new count and SHA256

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BATCH_FILE=${1:-}
DATASET=${2:-data/latest/latest.jsonl}
MANIFEST=${3:-data/latest/manifest.json}
SCHEMA=${4:-schema/bigv.schema.json}

# Validate inputs
if [[ -z "$BATCH_FILE" ]]; then
    echo -e "${RED}ERROR: batch file required${NC}" >&2
    echo "Usage: $0 <batch_file> [dataset_file] [manifest_file] [schema_file]" >&2
    exit 1
fi

if [[ ! -f "$BATCH_FILE" ]]; then
    echo -e "${RED}ERROR: batch file not found: $BATCH_FILE${NC}" >&2
    exit 1
fi

if [[ ! -f "$DATASET" ]]; then
    echo -e "${RED}ERROR: dataset file not found: $DATASET${NC}" >&2
    exit 1
fi

if [[ ! -f "$MANIFEST" ]]; then
    echo -e "${RED}ERROR: manifest file not found: $MANIFEST${NC}" >&2
    exit 1
fi

if [[ ! -f "$SCHEMA" ]]; then
    echo -e "${RED}ERROR: schema file not found: $SCHEMA${NC}" >&2
    exit 1
fi

# Check batch file is not empty
BATCH_COUNT=$(wc -l < "$BATCH_FILE" | tr -d ' ')
if [[ "$BATCH_COUNT" -eq 0 ]]; then
    echo -e "${RED}ERROR: batch file is empty: $BATCH_FILE${NC}" >&2
    exit 1
fi

CURRENT_COUNT=$(wc -l < "$DATASET" | tr -d ' ')

echo -e "${YELLOW}=== Batch Merge with Quality Enforcement ===${NC}"
echo "Batch file:   $BATCH_FILE ($BATCH_COUNT records)"
echo "Dataset:      $DATASET ($CURRENT_COUNT records)"
echo "Manifest:     $MANIFEST"
echo "Schema:       $SCHEMA"
echo ""

# Create backup
BACKUP_FILE="${DATASET}.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${YELLOW}Creating backup: $BACKUP_FILE${NC}"
cp "$DATASET" "$BACKUP_FILE"

# Create temporary merged file
TEMP_MERGED=$(mktemp)
trap "rm -f $TEMP_MERGED" EXIT

echo -e "${YELLOW}Merging batch into temporary file...${NC}"
cat "$DATASET" "$BATCH_FILE" > "$TEMP_MERGED"
MERGED_COUNT=$(wc -l < "$TEMP_MERGED" | tr -d ' ')
echo "Merged count: $MERGED_COUNT records"

# Create temporary manifest for validation
TEMP_MANIFEST=$(mktemp)
trap "rm -f $TEMP_MERGED $TEMP_MANIFEST" EXIT

TEMP_SHA=$(sha256sum "$TEMP_MERGED" | awk '{print $1}')
python3 <<PY > "$TEMP_MANIFEST"
import json
from pathlib import Path
from datetime import datetime, timezone

manifest = json.loads(Path('$MANIFEST').read_text())
manifest['count'] = $MERGED_COUNT
manifest['sha256'] = '$TEMP_SHA'
manifest['timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
manifest['score_note'] = 'Batch merge in progress: $(basename $BATCH_FILE)'
print(json.dumps(manifest, indent=2))
PY

echo ""
echo -e "${YELLOW}Running pipeline_guard.sh for quality enforcement...${NC}"
if ./scripts/pipeline_guard.sh "$TEMP_MERGED" "$TEMP_MANIFEST" "$SCHEMA"; then
    echo ""
    echo -e "${GREEN}✓ QUALITY GATE PASSED${NC}"
    echo ""
    echo -e "${YELLOW}Committing merge...${NC}"

    # Commit the merge
    cp "$TEMP_MERGED" "$DATASET"
    cp "$TEMP_MANIFEST" "$MANIFEST"

    # Update release files
    echo -e "${YELLOW}Updating release files...${NC}"
    cp "$DATASET" data/release/influx-latest.jsonl
    gzip -c data/release/influx-latest.jsonl > data/release/influx-latest.jsonl.gz
    cp "$MANIFEST" data/release/manifest.json

    echo ""
    echo -e "${GREEN}=== MERGE COMPLETED SUCCESSFULLY ===${NC}"
    echo "Previous count: $CURRENT_COUNT"
    echo "Batch added:    $BATCH_COUNT"
    echo "New count:      $MERGED_COUNT"
    echo "Backup saved:   $BACKUP_FILE"
    echo ""
    echo -e "${GREEN}Release files synchronized${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}✗ QUALITY GATE FAILED${NC}" >&2
    echo -e "${RED}Merge aborted - duplicates or quality violations detected${NC}" >&2
    echo "Dataset unchanged: $DATASET"
    echo "Backup preserved: $BACKUP_FILE"
    echo ""
    echo "To investigate the issue, run:"
    echo "  ./scripts/pipeline_guard.sh $TEMP_MERGED $TEMP_MANIFEST $SCHEMA"
    exit 1
fi
