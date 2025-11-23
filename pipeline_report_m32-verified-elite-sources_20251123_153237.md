# Pipeline Execution Report

Batch: lists/seeds/m32-verified-elite-sources.csv
Started: [2025-11-23T15:32:37.574101] INFO: Starting pipeline for lists/seeds/m32-verified-elite-sources.csv
Completed: 2025-11-23T15:32:37.592797

## 📋 Execution Log

- [2025-11-23T15:32:37.574101] INFO: Starting pipeline for lists/seeds/m32-verified-elite-sources.csv
- [2025-11-23T15:32:37.574147] INFO: Running: Harvest batch lists/seeds/m32-verified-elite-sources.csv
- [2025-11-23T15:32:37.574151] INFO: Command: ./tools/influx-harvest bulk --handles-file lists/seeds/m32-verified-elite-sources.csv --out data/batches/m32-verified-elite-sources_harvested.jsonl --min-followers 50000 --verified-min-followers 30000
- [2025-11-23T15:32:37.592762] ERROR: ❌ Failed: Harvest batch lists/seeds/m32-verified-elite-sources.csv
- [2025-11-23T15:32:37.592784] ERROR: Error output:   File "/home/dodd/dev/influx/./tools/influx-harvest", line 610
    print(f"
          ^
SyntaxError: unterminated f-string literal (detected at line 610)

- [2025-11-23T15:32:37.592792] ERROR: Pipeline failed at step: Harvest

## 📊 Summary

- **Steps Completed**: 0
- **Steps Failed**: 1
- **Success Rate**: 0.0%