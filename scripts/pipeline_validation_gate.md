# Pipeline Validation Gate Implementation

## Pre-Merge Validation Script

```bash
#!/bin/bash
# pipeline_guard.sh - Enforce single-path pipeline

set -e

INPUT_FILE=${1:-"data/latest/latest.jsonl"}
MANIFEST_FILE=${2:-"data/latest/manifest.json"}
SCHEMA_FILE=${3:-"schema/bigv.schema.json"}

echo "🔍 Running pipeline validation gate..."

# 1. Schema validation
if ! ./tools/influx-validate --strict -s "$SCHEMA_FILE" -m "$MANIFEST_FILE" "$INPUT_FILE"; then
    echo "❌ SCHEMA VALIDATION FAILED - Reject merge"
    exit 1
fi

# 2. Manifest alignment check
ACTUAL_COUNT=$(wc -l < "$INPUT_FILE")
MANIFEST_COUNT=$(jq -r '.count' "$MANIFEST_FILE")

if [ "$ACTUAL_COUNT" != "$MANIFEST_COUNT" ]; then
    echo "❌ MANIFEST COUNT MISMATCH - Reject merge"
    echo "Actual: $ACTUAL_COUNT, Manifest: $MANIFEST_COUNT"
    exit 1
fi

# 3. Provenance hash validation
if grep -q "temp_hash\|fake\|mock\|test" "$INPUT_FILE"; then
    echo "❌ INVALID PROVENANCE DETECTED - Reject merge"
    exit 1
fi

# 4. Follower count sanity check
if jq -r '.followers_count' "$INPUT_FILE" | grep -q "000$"; then
    echo "❌ SUSPICIOUS FOLLOWER COUNTS (ending in 000) - Reject merge"
    exit 1
fi

echo "✅ PIPELINE VALIDATION PASSED - Merge approved"
```

## Integration Points

1. **Pre-commit hook**: Run `pipeline_guard.sh` before any dataset changes
2. **CI/CD gate**: Block PRs that fail validation
3. **Manual merge requirement**: All data must pass through `influx-harvest` pipeline

## Zero Manual Entry Policy

- **ALLOWED**: `influx-harvest bulk --handles-file ... --out ...`
- **FORBIDDEN**: Direct JSON manipulation, manual field additions, schema bypasses
- **EXCEPTION**: Emergency fixes with peer review and validation gate bypass

## Implementation Timeline

- **Immediate**: Add script to repository
- **Next 24h**: Integrate with all merge workflows  
- **48h**: Full enforcement with pre-commit hooks