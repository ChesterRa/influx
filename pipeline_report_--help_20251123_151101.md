# Pipeline Execution Report

Batch: --help
Started: [2025-11-23T15:11:01.135027] INFO: Starting pipeline for --help
Completed: 2025-11-23T15:11:01.188832

## 📋 Execution Log

- [2025-11-23T15:11:01.135027] INFO: Starting pipeline for --help
- [2025-11-23T15:11:01.135053] INFO: Running: Harvest batch --help
- [2025-11-23T15:11:01.135057] INFO: Command: ./tools/influx-harvest bulk --handles-file --help --out data/batches/--help_harvested.jsonl --min-followers 50000 --verified-min-followers 30000
- [2025-11-23T15:11:01.188806] ERROR: ❌ Failed: Harvest batch --help
- [2025-11-23T15:11:01.188821] ERROR: Error output: usage: influx-harvest bulk [-h] [--handles-file HANDLES_FILE]
                           [--handles HANDLES] --out OUT
                           [--batch-size BATCH_SIZE]
                           [--parallel-batches PARALLEL_BATCHES]
                           [--default-category DEFAULT_CATEGORY]
                           [--min-followers MIN_FOLLOWERS]
                           [--verified-min-followers VERIFIED_MIN_FOLLOWERS]
                           [--brand-rules BRAND_RULES]
                           [--risk-rules RISK_RULES] [--allow-brands]
                           [--allow-risk ALLOW_RISK]
influx-harvest bulk: error: argument --handles-file: expected one argument

- [2025-11-23T15:11:01.188827] ERROR: Pipeline failed at step: Harvest

## 📊 Summary

- **Steps Completed**: 0
- **Steps Failed**: 1
- **Success Rate**: 0.0%