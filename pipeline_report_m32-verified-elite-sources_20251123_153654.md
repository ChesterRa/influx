# Pipeline Execution Report

Batch: lists/seeds/m32-verified-elite-sources.csv
Started: [2025-11-23T15:36:54.294804] INFO: Starting pipeline for lists/seeds/m32-verified-elite-sources.csv
Completed: 2025-11-23T15:36:54.377136

## 📋 Execution Log

- [2025-11-23T15:36:54.294804] INFO: Starting pipeline for lists/seeds/m32-verified-elite-sources.csv
- [2025-11-23T15:36:54.294835] INFO: Running: Harvest batch lists/seeds/m32-verified-elite-sources.csv
- [2025-11-23T15:36:54.294838] INFO: Command: ./tools/influx-harvest bulk --handles-file lists/seeds/m32-verified-elite-sources.csv --out data/batches/m32-verified-elite-sources_harvested.jsonl --min-followers 50000 --verified-min-followers 30000
- [2025-11-23T15:36:54.377100] ERROR: ❌ Failed: Harvest batch lists/seeds/m32-verified-elite-sources.csv
- [2025-11-23T15:36:54.377123] ERROR: Error output: [ERROR] No prefetched users provided.
[ACTION] Use a RUBE-capable environment to fetch Twitter users (e.g., TWITTER_USER_LOOKUP_BY_USERNAMES), save JSONL, then re-run with --prefetched-users <file>

- [2025-11-23T15:36:54.377131] ERROR: Pipeline failed at step: Harvest

## 📊 Summary

- **Steps Completed**: 0
- **Steps Failed**: 1
- **Success Rate**: 0.0%