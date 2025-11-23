# QA抽查 Report

**Batch File:** /home/dodd/dev/influx/data/batches/geographic_combined_20251123.jsonl
**Timestamp:** 2025-11-23T07:41:54.497660+00:00
**Total Records:** 9
**Sampled Records:** 9
**Result:** ❌ FAILED

## Summary

✗ QA FAILED: 6 violations found
  Critical: 6, Major: 0, Minor: 0
  Violation types: {'evidence_missing': 5, 'external_validation_failed': 1}
  Critical violations affecting: kim, JackMa, taavet, Vinny

## Violations

### Critical Violations

- **Vinny** (ID: 2507565574): Source 0: insufficient evidence content
- **kim** (ID: 17243913): Source 0: insufficient evidence content
- **JackMa** (ID: 29138438): Source 0: insufficient evidence content
- **JackMa** (ID: 29138438): Duplicate handle found in dataset: JackMa
- **JackMa** (ID: 1239332857807384576): Source 0: insufficient evidence content
- **taavet** (ID: 1784181): Source 0: insufficient evidence content

## Recommendations

- **REJECT BATCH** - Critical violations found
- Address all violations before resubmission
- Review evidence collection process
