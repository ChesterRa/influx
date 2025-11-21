# M2 Phase 2 RUBE MCP Processing Instructions

Generated: 2025-11-19T14:18:22.493654
Total batches: 10
Batch size: 50 handles

## For Each Batch (Execute Sequentially):

### Batch 1: 50 handles

```bash
# Step 1: Fetch data via RUBE MCP
claude-code exec rube-fetch $(cat m2_rube_batch_001_handles.txt | sed 's/^/@/' | tr '\n' ' ')

# Step 2: Process fetched data (replace output filename as needed)
tools/influx-harvest x-lists \
  --list-urls m2_rube_batch_001_handles.txt \
  --prefetched-users rube_batch_001_output.jsonl \
  --out m2_rube_batch_001_refreshed.jsonl \
  --brand-rules lists/rules/brand_heuristics.yml

# Step 3: Apply M2 scoring
tools/influx-score update \
  --authors m2_rube_batch_001_refreshed.jsonl \
  --out m2_rube_batch_001_scored.jsonl \
  --model m2
```

### Batch 2: 50 handles

```bash
# Step 1: Fetch data via RUBE MCP
claude-code exec rube-fetch $(cat m2_rube_batch_002_handles.txt | sed 's/^/@/' | tr '\n' ' ')

# Step 2: Process fetched data (replace output filename as needed)
tools/influx-harvest x-lists \
  --list-urls m2_rube_batch_002_handles.txt \
  --prefetched-users rube_batch_002_output.jsonl \
  --out m2_rube_batch_002_refreshed.jsonl \
  --brand-rules lists/rules/brand_heuristics.yml

# Step 3: Apply M2 scoring
tools/influx-score update \
  --authors m2_rube_batch_002_refreshed.jsonl \
  --out m2_rube_batch_002_scored.jsonl \
  --model m2
```

### Batch 3: 50 handles

```bash
# Step 1: Fetch data via RUBE MCP
claude-code exec rube-fetch $(cat m2_rube_batch_003_handles.txt | sed 's/^/@/' | tr '\n' ' ')

# Step 2: Process fetched data (replace output filename as needed)
tools/influx-harvest x-lists \
  --list-urls m2_rube_batch_003_handles.txt \
  --prefetched-users rube_batch_003_output.jsonl \
  --out m2_rube_batch_003_refreshed.jsonl \
  --brand-rules lists/rules/brand_heuristics.yml

# Step 3: Apply M2 scoring
tools/influx-score update \
  --authors m2_rube_batch_003_refreshed.jsonl \
  --out m2_rube_batch_003_scored.jsonl \
  --model m2
```

### Batch 4: 50 handles

```bash
# Step 1: Fetch data via RUBE MCP
claude-code exec rube-fetch $(cat m2_rube_batch_004_handles.txt | sed 's/^/@/' | tr '\n' ' ')

# Step 2: Process fetched data (replace output filename as needed)
tools/influx-harvest x-lists \
  --list-urls m2_rube_batch_004_handles.txt \
  --prefetched-users rube_batch_004_output.jsonl \
  --out m2_rube_batch_004_refreshed.jsonl \
  --brand-rules lists/rules/brand_heuristics.yml

# Step 3: Apply M2 scoring
tools/influx-score update \
  --authors m2_rube_batch_004_refreshed.jsonl \
  --out m2_rube_batch_004_scored.jsonl \
  --model m2
```

### Batch 5: 50 handles

```bash
# Step 1: Fetch data via RUBE MCP
claude-code exec rube-fetch $(cat m2_rube_batch_005_handles.txt | sed 's/^/@/' | tr '\n' ' ')

# Step 2: Process fetched data (replace output filename as needed)
tools/influx-harvest x-lists \
  --list-urls m2_rube_batch_005_handles.txt \
  --prefetched-users rube_batch_005_output.jsonl \
  --out m2_rube_batch_005_refreshed.jsonl \
  --brand-rules lists/rules/brand_heuristics.yml

# Step 3: Apply M2 scoring
tools/influx-score update \
  --authors m2_rube_batch_005_refreshed.jsonl \
  --out m2_rube_batch_005_scored.jsonl \
  --model m2
```

### Batch 6: 50 handles

```bash
# Step 1: Fetch data via RUBE MCP
claude-code exec rube-fetch $(cat m2_rube_batch_006_handles.txt | sed 's/^/@/' | tr '\n' ' ')

# Step 2: Process fetched data (replace output filename as needed)
tools/influx-harvest x-lists \
  --list-urls m2_rube_batch_006_handles.txt \
  --prefetched-users rube_batch_006_output.jsonl \
  --out m2_rube_batch_006_refreshed.jsonl \
  --brand-rules lists/rules/brand_heuristics.yml

# Step 3: Apply M2 scoring
tools/influx-score update \
  --authors m2_rube_batch_006_refreshed.jsonl \
  --out m2_rube_batch_006_scored.jsonl \
  --model m2
```

### Batch 7: 50 handles

```bash
# Step 1: Fetch data via RUBE MCP
claude-code exec rube-fetch $(cat m2_rube_batch_007_handles.txt | sed 's/^/@/' | tr '\n' ' ')

# Step 2: Process fetched data (replace output filename as needed)
tools/influx-harvest x-lists \
  --list-urls m2_rube_batch_007_handles.txt \
  --prefetched-users rube_batch_007_output.jsonl \
  --out m2_rube_batch_007_refreshed.jsonl \
  --brand-rules lists/rules/brand_heuristics.yml

# Step 3: Apply M2 scoring
tools/influx-score update \
  --authors m2_rube_batch_007_refreshed.jsonl \
  --out m2_rube_batch_007_scored.jsonl \
  --model m2
```

### Batch 8: 50 handles

```bash
# Step 1: Fetch data via RUBE MCP
claude-code exec rube-fetch $(cat m2_rube_batch_008_handles.txt | sed 's/^/@/' | tr '\n' ' ')

# Step 2: Process fetched data (replace output filename as needed)
tools/influx-harvest x-lists \
  --list-urls m2_rube_batch_008_handles.txt \
  --prefetched-users rube_batch_008_output.jsonl \
  --out m2_rube_batch_008_refreshed.jsonl \
  --brand-rules lists/rules/brand_heuristics.yml

# Step 3: Apply M2 scoring
tools/influx-score update \
  --authors m2_rube_batch_008_refreshed.jsonl \
  --out m2_rube_batch_008_scored.jsonl \
  --model m2
```

### Batch 9: 50 handles

```bash
# Step 1: Fetch data via RUBE MCP
claude-code exec rube-fetch $(cat m2_rube_batch_009_handles.txt | sed 's/^/@/' | tr '\n' ' ')

# Step 2: Process fetched data (replace output filename as needed)
tools/influx-harvest x-lists \
  --list-urls m2_rube_batch_009_handles.txt \
  --prefetched-users rube_batch_009_output.jsonl \
  --out m2_rube_batch_009_refreshed.jsonl \
  --brand-rules lists/rules/brand_heuristics.yml

# Step 3: Apply M2 scoring
tools/influx-score update \
  --authors m2_rube_batch_009_refreshed.jsonl \
  --out m2_rube_batch_009_scored.jsonl \
  --model m2
```

### Batch 10: 10 handles

```bash
# Step 1: Fetch data via RUBE MCP
claude-code exec rube-fetch $(cat m2_rube_batch_010_handles.txt | sed 's/^/@/' | tr '\n' ' ')

# Step 2: Process fetched data (replace output filename as needed)
tools/influx-harvest x-lists \
  --list-urls m2_rube_batch_010_handles.txt \
  --prefetched-users rube_batch_010_output.jsonl \
  --out m2_rube_batch_010_refreshed.jsonl \
  --brand-rules lists/rules/brand_heuristics.yml

# Step 3: Apply M2 scoring
tools/influx-score update \
  --authors m2_rube_batch_010_refreshed.jsonl \
  --out m2_rube_batch_010_scored.jsonl \
  --model m2
```

