# Data Samples

**Purpose**: Quick-browse samples for users to preview data structure and content without decompression.

## Files

- **top200.jsonl**: Top 200 authors by score (uncompressed, ~90 KB)
  - Format: JSONL (one author per line)
  - Sorted: score desc → followers desc → handle asc
  - Source: `data/latest/latest.jsonl.gz` (first 200 records)

## Usage

```bash
# Preview first 10 records
head -n 10 data/samples/top200.jsonl | jq .

# Filter by topic (when topic_tags implemented)
grep '"topic_tags":\["ai_core"' data/samples/top200.jsonl | jq .

# Count by verified type
jq -r '.verified' data/samples/top200.jsonl | sort | uniq -c
```

## Maintenance

- **Update frequency**: On each release (sync with data/latest/latest.jsonl.gz)
- **Size limit**: ≤200 records (keep Git-friendly, ~100-200 KB range)
- **Full data**: Download `data/latest/latest.jsonl.gz` for complete dataset

## See Also

- [tools/influx-view](../../tools/influx-view): Syntax-highlighted viewer
- [data/uncompressed/](../uncompressed/README.md): Full uncompressed sources
- [README.md:Usage](../../README.md#usage): Integration examples
