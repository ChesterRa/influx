# Uncompressed Source Files

**Purpose**: Preserve readable, uncompressed JSONL sources for reproducibility and review.

**Policy**: Minimal storage - latest milestone only. Older versions replaced on new releases.

## Directory Structure

```
data/uncompressed/
  └── YYYY-MM-DD/              # Date of milestone release
      └── complete_scored.m0.jsonl  # M0 source (151 authors, 66 KB)
```

## Current Files

- **2025-11-13/complete_scored.m0.jsonl**: M0 milestone (151 authors, scored with v0_proxy formula)
  - SHA-256: matches `data/latest/latest.jsonl.gz` (uncompressed)
  - Source for: data/latest/latest.jsonl.gz, data/snapshots/2025-11-13/bigv-20251113.jsonl.gz

## Lifecycle

- **On new milestone**: Replace previous directory with current (e.g., M1 replaces M0)
- **Git**: Committed (files ≤500KB)
- **Large files**: Use compression; defer Git LFS until >5MB threshold

## Validation

```bash
# Verify integrity
python3 tools/influx-validate -s schema/bigv.schema.json data/uncompressed/2025-11-13/complete_scored.m0.jsonl
```

## See Also

- [data/samples/](../samples/README.md): Preview samples for quick browsing
- [data/latest/](../latest/): Compressed releases
- [.gitignore](../../.gitignore): Ignored intermediate files
