# QA抽查 Report

**Batch File:** data/batches/new_authors_to_merge.jsonl
**Timestamp:** 2025-11-23T08:38:44.043588+00:00
**Total Records:** 8
**Sampled Records:** 8
**Result:** ❌ FAILED

## Summary

✗ QA FAILED: 6 violations found
  Critical: 6, Major: 0, Minor: 0
  Violation types: {'official_account': 4, 'evidence_missing': 2}
  Critical violations affecting: verge, WIRED, arstechnica, TechCrunch

## Violations

### Critical Violations

- **arstechnica** (ID: 717313): Official account not allowed
- **TechCrunch** (ID: 816653): Official account not allowed
- **verge** (ID: 275686563): Source 0: insufficient evidence content
- **verge** (ID: 275686563): Official account not allowed
- **WIRED** (ID: 1344951): Source 0: insufficient evidence content
- **WIRED** (ID: 1344951): Official account not allowed

## Recommendations

- **REJECT BATCH** - Critical violations found
- Address all violations before resubmission
- Review evidence collection process
