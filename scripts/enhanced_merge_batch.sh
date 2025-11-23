#!/usr/bin/env bash
# enhanced_merge_batch.sh - Foreman-enforced batch merge with comprehensive QA
# Usage: ./scripts/enhanced_merge_batch.sh <batch_file> [operator]
#
# This script implements the foreman's zero-tolerance quality policy:
# 1. Runs comprehensive QA抽查 before merge
# 2. Creates audit trail record
# 3. Only proceeds if ALL quality gates pass
# 4. Logs all decisions and evidence

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BATCH_FILE=${1:-}
OPERATOR=${2:-"system"}
DATASET="data/latest/latest.jsonl"
MANIFEST="data/latest/manifest.json"
SCHEMA="schema/bigv.schema.json"

# Validate inputs
if [[ -z "$BATCH_FILE" ]]; then
    echo -e "${RED}ERROR: batch file required${NC}" >&2
    echo "Usage: $0 <batch_file> [operator]" >&2
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

BATCH_COUNT=$(wc -l < "$BATCH_FILE" | tr -d ' ')
CURRENT_COUNT=$(wc -l < "$DATASET" | tr -d ' ')

echo -e "${BLUE}=== FOREMAN ENFORCED BATCH MERGE ===${NC}"
echo -e "${YELLOW}Batch:        $BATCH_FILE ($BATCH_COUNT records)${NC}"
echo -e "${YELLOW}Dataset:      $DATASET ($CURRENT_COUNT records)${NC}"
echo -e "${YELLOW}Operator:     $OPERATOR${NC}"
echo -e "${YELLOW}Timestamp:    $(date -u +"%Y-%m-%dT%H:%M:%SZ")${NC}"
echo ""

# Step 1: Create audit trail record for validation
echo -e "${YELLOW}Step 1: Creating audit trail record...${NC}"
python3 ./scripts/batch_audit_trail.py validate "$BATCH_FILE" "$OPERATOR" > /dev/null

# Step 2: Run comprehensive QA抽查
echo -e "${YELLOW}Step 2: Running comprehensive QA抽查 (sample N=30)...${NC}"
if python3 ./scripts/foreman_qa_check.py "$BATCH_FILE" 30; then
    echo -e "${GREEN}✓ QA抽查 PASSED - No critical violations found${NC}"
    QA_PASSED=true
else
    echo -e "${RED}✗ QA抽查 FAILED - Critical violations detected${NC}" >&2
    QA_PASSED=false
fi
echo ""

# Step 3: Run pipeline guard for duplicate and quality checks
echo -e "${YELLOW}Step 3: Running pipeline_guard for quality enforcement...${NC}"
TEMP_MERGED=$(mktemp)
trap "rm -f $TEMP_MERGED" EXIT

cat "$DATASET" "$BATCH_FILE" > "$TEMP_MERGED"
TEMP_MANIFEST=$(mktemp)
trap "rm -f $TEMP_MERGED $TEMP_MANIFEST" EXIT

# Create temporary manifest
TEMP_SHA=$(sha256sum "$TEMP_MERGED" | awk '{print $1}')
python3 <<PY > "$TEMP_MANIFEST"
import json
from pathlib import Path
from datetime import datetime, timezone

manifest = json.loads(Path('$MANIFEST').read_text())
manifest['count'] = $(wc -l < "$TEMP_MERGED" | tr -d ' ')
manifest['sha256'] = '$TEMP_SHA'
manifest['timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
manifest['score_note'] = 'Pre-merge validation: $(basename $BATCH_FILE)'
print(json.dumps(manifest, indent=2))
PY

if ./scripts/pipeline_guard.sh "$TEMP_MERGED" "$TEMP_MANIFEST" "$SCHEMA"; then
    echo -e "${GREEN}✓ PIPELINE_GUARD PASSED - No duplicates or violations${NC}"
    PIPELINE_PASSED=true
else
    echo -e "${RED}✗ PIPELINE_GUARD FAILED - Quality violations detected${NC}" >&2
    PIPELINE_PASSED=false
fi
echo ""

# Step 4: Decision Gate
echo -e "${BLUE}Step 4: FOREMAN DECISION GATE${NC}"
echo ""

if [[ "$QA_PASSED" == "true" && "$PIPELINE_PASSED" == "true" ]]; then
    echo -e "${GREEN}✅ FOREMAN APPROVAL GRANTED${NC}"
    echo -e "${GREEN}All quality gates passed - proceeding with merge${NC}"
    echo ""
    
    # Step 5: Execute merge with safety
    echo -e "${YELLOW}Step 5: Executing safe merge...${NC}"
    
    # Create backup
    BACKUP_FILE="${DATASET}.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}Creating backup: $BACKUP_FILE${NC}"
    cp "$DATASET" "$BACKUP_FILE"
    
    # Commit the merge
    cp "$TEMP_MERGED" "$DATASET"
    
    # Update manifest
    cp "$TEMP_MANIFEST" "$MANIFEST"
    
    # Update release files
    echo -e "${YELLOW}Updating release files...${NC}"
    cp "$DATASET" data/release/influx-latest.jsonl
    gzip -c data/release/influx-latest.jsonl > data/release/influx-latest.jsonl.gz
    cp "$MANIFEST" data/release/manifest.json
    
    MERGED_COUNT=$(wc -l < "$DATASET" | tr -d ' ')
    NET_GAIN=$((MERGED_COUNT - CURRENT_COUNT))
    
    echo ""
    echo -e "${GREEN}=== MERGE COMPLETED SUCCESSFULLY ===${NC}"
    echo -e "${GREEN}Previous count: $CURRENT_COUNT${NC}"
    echo -e "${GREEN}Batch added:    $BATCH_COUNT${NC}"
    echo -e "${GREEN}New count:      $MERGED_COUNT${NC}"
    echo -e "${GREEN}Net gain:       $NET_GAIN${NC}"
    echo -e "${GREEN}Backup saved:   $BACKUP_FILE${NC}"
    echo -e "${GREEN}Release files synchronized${NC}"
    echo ""
    
    # Step 6: Record successful merge in audit trail
    echo -e "${YELLOW}Step 6: Recording successful merge in audit trail...${NC}"
    python3 ./scripts/batch_audit_trail.py merge "$BATCH_FILE" "$OPERATOR" > /dev/null
    
    echo -e "${GREEN}✅ Foreman oversight complete - audit trail updated${NC}"
    echo ""
    
    # Show compliance status
    echo -e "${BLUE}Compliance Status:${NC}"
    echo -e "${GREEN}✓ Zero tolerance for fake data enforced${NC}"
    echo -e "${GREEN}✓ QA抽查 evidence validation passed${NC}"
    echo -e "${GREEN}✓ Pipeline guard quality checks passed${NC}"
    echo -e "${GREEN}✓ Audit trail recorded${NC}"
    echo -e "${GREEN}✓ Release files synchronized${NC}"
    
    exit 0
    
else
    echo -e "${RED}❌ FOREMAN REJECTION${NC}" >&2
    echo -e "${RED}Quality gates failed - merge ABORTED${NC}" >&2
    echo ""
    
    if [[ "$QA_PASSED" == "false" ]]; then
        echo -e "${RED}✗ QA抽查 failed - See QA report for details${NC}" >&2
    fi
    
    if [[ "$PIPELINE_PASSED" == "false" ]]; then
        echo -e "${RED}✗ Pipeline guard failed - See pipeline_guard output for details${NC}" >&2
    fi
    
    echo ""
    echo -e "${YELLOW}Dataset unchanged: $DATASET${NC}"
    echo -e "${YELLOW}Batch rejected: $BATCH_FILE${NC}"
    echo ""
    
    # Record rejection in audit trail
    echo -e "${YELLOW}Recording rejection in audit trail...${NC}"
    python3 ./scripts/batch_audit_trail.py reject "$BATCH_FILE" "$OPERATOR" > /dev/null
    
    echo -e "${RED}✅ Foreman oversight complete - rejection recorded${NC}"
    echo ""
    
    echo -e "${BLUE}To resolve issues:${NC}"
    echo "1. Review QA report: ./scripts/foreman_qa_check.py $BATCH_FILE"
    echo "2. Fix all violations and resubmit"
    echo "3. Ensure all records have proper sources.evidence"
    echo "4. Verify no duplicates, placeholders, or org accounts"
    
    exit 1
fi
