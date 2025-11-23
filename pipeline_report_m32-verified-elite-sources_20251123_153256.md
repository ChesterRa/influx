# Pipeline Execution Report

Batch: lists/seeds/m32-verified-elite-sources.csv
Started: [2025-11-23T15:32:56.784982] INFO: Starting pipeline for lists/seeds/m32-verified-elite-sources.csv
Completed: 2025-11-23T15:32:56.879558

## 📋 Execution Log

- [2025-11-23T15:32:56.784982] INFO: Starting pipeline for lists/seeds/m32-verified-elite-sources.csv
- [2025-11-23T15:32:56.785089] INFO: Running: Harvest batch lists/seeds/m32-verified-elite-sources.csv
- [2025-11-23T15:32:56.785096] INFO: Command: ./tools/influx-harvest bulk --handles-file lists/seeds/m32-verified-elite-sources.csv --out data/batches/m32-verified-elite-sources_harvested.jsonl --min-followers 50000 --verified-min-followers 30000
- [2025-11-23T15:32:56.879519] ERROR: ❌ Failed: Harvest batch lists/seeds/m32-verified-elite-sources.csv
- [2025-11-23T15:32:56.879544] ERROR: Error output: [ERROR] No prefetched users provided.
[ACTION] Use a RUBE-capable environment to fetch Twitter users (e.g., TWITTER_USER_LOOKUP_BY_USERNAMES), save JSONL, then re-run with --prefetched-users <file>

- [2025-11-23T15:32:56.879552] ERROR: Pipeline failed at step: Harvest

## 📊 Summary

- **Steps Completed**: 0
- **Steps Failed**: 1
- **Success Rate**: 0.0%