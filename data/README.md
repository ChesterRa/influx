# Influx Data Directory

Professional data management structure for influencer intelligence platform.

## Directory Structure

```
data/
├── latest/
│   ├── latest.jsonl          # Main dataset (525+ authors, 100% quality compliance)
│   └── manifest.json         # Dataset metadata and version info
├── processed_batches/        # Archived batch results (with documentation)
├── samples/                  # Sample datasets for testing and development
├── snapshots/                # Historical snapshots for recovery
└── uncompressed/             # Legacy compressed data archives
```

## Core Dataset

**File**: `latest/latest.jsonl`
- **Current Status**: 525+ authors, 100% quality compliance
- **Schema**: Full author profiles with activity metrics
- **Quality Gates**: Brand heuristics + entry thresholds + validation
- **Update Pattern**: Incremental merges from processed batches

## Quality Assurance

All data in `latest.jsonl` has passed through:
1. **Brand Heuristics Filter** - Removes corporate/official accounts
2. **Entry Threshold Validation** - Minimum followers and profile completeness
3. **Schema Compliance** - Mandatory fields validation
4. **Manual Review** - Human verification for edge cases

## Processing Pipeline

```
CSV Seed Lists → Twitter API (RUBE MCP) → Quality Gates → Main Dataset
```

- **Single-Path Architecture**: No branching, mandatory quality gates
- **Zero Tolerance**: Any quality failure rejects entire batch
- **Incremental**: New authors merged without affecting existing data

## Archive Strategy

- **Processed Batches**: Maintain complete processing history
- **Snapshots**: Point-in-time recovery capability
- **Documentation**: Every directory includes comprehensive README
- **Clean Structure**: No redundant files, clear naming conventions

## Current Metrics

- **Authors**: 525+ individual accounts
- **Quality**: 100% compliance with filtering rules
- **Domains**: 23+ specialized domains covered
- **Growth**: Active scaling toward 1.5k-2k target

Last updated: 2025-11-14