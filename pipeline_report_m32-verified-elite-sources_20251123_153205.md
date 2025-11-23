# Pipeline Execution Report

Batch: lists/seeds/m32-verified-elite-sources.csv
Started: [2025-11-23T15:32:04.987085] INFO: Starting pipeline for lists/seeds/m32-verified-elite-sources.csv
Completed: 2025-11-23T15:32:05.009389

## 📋 Execution Log

- [2025-11-23T15:32:04.987085] INFO: Starting pipeline for lists/seeds/m32-verified-elite-sources.csv
- [2025-11-23T15:32:04.987144] INFO: Running: Harvest batch lists/seeds/m32-verified-elite-sources.csv
- [2025-11-23T15:32:04.987150] INFO: Command: ./tools/influx-harvest bulk --handles-file lists/seeds/m32-verified-elite-sources.csv --out data/batches/m32-verified-elite-sources_harvested.jsonl --min-followers 50000 --verified-min-followers 30000
- [2025-11-23T15:32:05.009319] ERROR: ❌ Failed: Harvest batch lists/seeds/m32-verified-elite-sources.csv
- [2025-11-23T15:32:05.009365] ERROR: Error output:   File "/home/dodd/dev/influx/./tools/influx-harvest", line 608
    f.write(json.dumps(record, ensure_ascii=False) + '
                                                     ^
SyntaxError: unterminated string literal (detected at line 608)

- [2025-11-23T15:32:05.009379] ERROR: Pipeline failed at step: Harvest

## 📊 Summary

- **Steps Completed**: 0
- **Steps Failed**: 1
- **Success Rate**: 0.0%