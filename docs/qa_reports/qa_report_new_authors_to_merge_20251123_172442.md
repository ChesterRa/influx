# QA抽查 Report

**Batch File:** data/batches/new_authors_to_merge.jsonl
**Timestamp:** 2025-11-23T08:24:42.548050+00:00
**Total Records:** 8
**Sampled Records:** 5
**Result:** ❌ FAILED

## Summary

✗ QA FAILED: 5 violations found
  Critical: 5, Major: 0, Minor: 0
  Violation types: {'evidence_missing': 2, 'official_account': 3}
  Critical violations affecting: arstechnica, WIRED, verge

## Violations

### Critical Violations

- **WIRED** (ID: 1344951): Source 0: insufficient evidence content
- **WIRED** (ID: 1344951): Official account not allowed
- **arstechnica** (ID: 717313): Official account not allowed
- **verge** (ID: 275686563): Source 0: insufficient evidence content
- **verge** (ID: 275686563): Official account not allowed

## Recommendations

- **REJECT BATCH** - Critical violations found
- Address all violations before resubmission
- Review evidence collection process
