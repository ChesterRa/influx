# QA抽查 Report

**Batch File:** m08_processed.jsonl
**Timestamp:** 2025-11-23T07:58:22.215429+00:00
**Total Records:** 10
**Sampled Records:** 10
**Result:** ❌ FAILED

## Summary

✗ QA FAILED: 17 violations found
  Critical: 17, Major: 0, Minor: 0
  Violation types: {'evidence_missing': 7, 'external_validation_failed': 10}
  Critical violations affecting: ylecun, fchollet, hardmaru, goodfellow_ian, JeffDean and 5 more

## Violations

### Critical Violations

- **karpathy** (ID: 33230155): Source 0: insufficient evidence content
- **karpathy** (ID: 33230155): Duplicate handle found in dataset: karpathy
- **ylecun** (ID: 20044644): Source 0: insufficient evidence content
- **ylecun** (ID: 20044644): Duplicate handle found in dataset: ylecun
- **AndrewYNg** (ID: 34188397): Duplicate handle found in dataset: AndrewYNg
- **fchollet** (ID: 35282205): Source 0: insufficient evidence content
- **fchollet** (ID: 35282205): Duplicate handle found in dataset: fchollet
- **hardmaru** (ID: 22841351): Source 0: insufficient evidence content
- **hardmaru** (ID: 22841351): Duplicate handle found in dataset: hardmaru
- **JeffDean** (ID: 105804702): Source 0: insufficient evidence content
- **JeffDean** (ID: 105804702): Duplicate handle found in dataset: JeffDean
- **sama** (ID: 44196397): Source 0: insufficient evidence content
- **sama** (ID: 44196397): Duplicate handle found in dataset: sama
- **demishassabis** (ID: 14398035): Duplicate handle found in dataset: demishassabis
- **goodfellow_ian** (ID: 14398035): Duplicate handle found in dataset: goodfellow_ian
- **gruber** (ID: 14398035): Source 0: insufficient evidence content
- **gruber** (ID: 14398035): Duplicate handle found in dataset: gruber

## Recommendations

- **REJECT BATCH** - Critical violations found
- Address all violations before resubmission
- Review evidence collection process
