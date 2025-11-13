<!-- Generated on 2025-11-13T07:15:00+00:00 by manual SUBPOR creation per PeerA request -->

# T000004 - M1 Manual Scale (151→1.5k-2k authors, 4-5 weeks) - Owner: peerB - Stage: active - Timebox: 4-5wk

- Goal/Scope (<=3 lines):
  - Scale influencer index from 151 (M0.1 baseline) to 1.5k-2k authors over 4-5 weeks via manual CSV curation + curated X Lists, maintaining M0's 100% precision bar and schema compliance
  - Target weekly increments of ~250-300 authors across 5-6 bootstrap domains (AI/Tech, Creator, Business, Finance, Science, Design) per Domain Coverage Plan (POR.md:55-79)
  - Method: manual CSV extraction from GitHub org pages, curated X Lists, domain-specific expert seeds → batch TWITTER_USER_LOOKUP validation → filter enforcement (entry thresholds + brand/risk heuristics) → proxy scoring → daily snapshot export
- Non-Goals (<=2 lines):
  - API automation workflows (GitHub seed expansion, Twitter following-graph) - blocked by T000003 OAuth limitations; deferred to M2
  - Advanced scoring models beyond proxy v0 (follower-based formula: 20*log10(followers/1000) + verified_boost) - defer to M2 adaptive features
- Deliverable & Interface (path/format/user-visible change):
  - data/latest/latest.jsonl.gz: Final M1 dataset with manifest.count ∈ [1500,2000], SHA-256 verified, 100% schema-compliant
  - data/snapshots/YYYY-MM-DD/: Daily snapshots via .github/workflows/snapshot.yml (cron 02:00 UTC)
  - lists/seeds/m04-*.csv through m08-*.csv: Weekly batch seed files (~250-300 handles each with source_url provenance)
  - .cccc/work/m1/: Incremental batch artifacts (harvest.filtered.jsonl, velocity logs, QA samples per batch)
- Acceptance (3-5 observable items):
  [ ] Weekly batch releases (≥250 authors/week for weeks 1-4, ≥150/week for week 5 buffer) with cumulative CI green status
  [ ] Final M1 deliverable: data/latest/latest.jsonl.gz with manifest.count ∈ [1500,2000], SHA-256 verified, score distribution reasonable (proxy v0: mean 40-60, range 0-100)
  [ ] Zero brand/official contamination in spot-check samples (N=30 per batch via manual review using .cccc/work/review/brand_fp.sample.csv methodology)
  [ ] QA validation: 50-record sample per 300-author batch with second-review signoff on edge cases
  [ ] Provenance tracking: 100% of authors have sources array with method/fetched_at/evidence fields populated
- Probe (cheapest decisive): **M1 Batch 0.5 (≤2 days)**: Collect 50-100 authors manually from 1-2 domains (AI/Tech + Business), run through complete pipeline (CSV → USER_LOOKUP → filter → score → validate → export), measure actual curation velocity (records/hour), QC pass rate, and filter precision to empirically validate 250-300/week assumption before committing to full 4-5 week timeline. Evidence targets: .cccc/work/m1/batch05/harvest.filtered.jsonl (≥50 records), validation 100% pass, velocity log showing ≥15-20 records/hour sustained rate.
- Kill Criteria (when to stop/pivot): If actual curation velocity <150 records/week (vs projected 250-300/week) after batch 0.5 probe, re-scope M1 downward (target 1k-1.2k authors over 6-8 weeks with additional curator resources) or pivot to semi-automated hybrid approach if Twitter API unblocks
- Implementation Approach (<=3 bullets):
  - **Phase 1: Batch 0.5 Probe (≤2 days)**: Manually curate 50-100 high-confidence authors (AI/Tech + Business domains), measure velocity (records/hour) and QC overhead, validate filter precision on first real-world batch
  - **Phase 2: Weekly Increments (Weeks 1-4)**: Target ~250-300 authors/week using domain rotation (AI/Tech → Creator/Platform → Business/Finance → Science/Design), daily CSV→JSONL pipeline runs, filter enforcement per d2-pipeline-contract.md, QA spot-checks (N=30 sample/batch)
  - **Phase 3: Buffer Week (Week 5)**: Target ≥150 authors to reach 1.5k-2k cumulative, final QA sweep (100-record validation sample), score distribution analysis, prepare M1 release artifacts
- Evidence (minimal refs):
  - filters.implementation: commit:6fd9487 (tools/influx-harvest with brand/risk filters per d2-pipeline-contract.md:105-123)
  - snapshot.automation: commit:060d273 (.github/workflows/snapshot.yml daily cron)
  - filter.baseline: .cccc/work/review/brand_fp.sample.csv (20 boundary cases), brand_fp.validation.txt (M0 Precision=100% baseline)
  - (pending batch 0.5): .cccc/work/m1/batch05/harvest.filtered.jsonl, velocity.log, qa_sample.csv
- Risks/Dependencies (1 line each):
  - Risk: Actual curation velocity <<250/week invalidates 4-5 week timeline; Mitigation: Batch 0.5 probe measures real velocity before full commitment, allows re-scoping
  - Risk: Brand/risk filter FP rate 15-25% (per .cccc/work/review/brand_fp.validation.txt projection) degrades precision; Mitigation: QA spot-checks (N=30/batch) + heuristics tuning via observed FP patterns
  - Dependency: Twitter API TWITTER_USER_LOOKUP_BY_USERNAMES functional (currently blocked by client-not-enrolled); Mitigation: Manual CSV export as fallback (proven in M0.1 with 151 authors)
  - Dependency: Daily snapshot automation (.github/workflows/snapshot.yml) operational before batch 1; Mitigation: Manual export fallback if workflow fails
- Next (single, decidable, <=30 minutes): **M1 Week 1 Batch Execution** - Manual-prefetch fallback: manually collect user data for m05 AI/Tech handles (25 usernames) from X profile pages or use cached data; run influx-harvest pipeline with --prefetched-users flag; generate .cccc/work/m1/week1/harvest.raw.jsonl + velocity.log + qa_sample.csv (N=30); validate 100% schema compliance; target ≥20 passing records from 25 inputs. (Note: TWITTER_USER_LOOKUP_BY_USERNAMES blocked by client-not-enrolled, manual CSV workflow proven in M0.1)

## REV (append-only)
- 2025-11-14 17:10 | peerB | **M1 SCALING CONTINUES - Quality Gates Proven Operational** (Foreman #000183): Successfully processed M13 Security (22 authors) and M12 Opensource (26 authors) batches using unified `influx-harvest` pipeline; critical schema mapping bug fixed (Twitter 'business' → schema 'org'); quality gates achieving perfect 0% brand contamination, 100% validation compliance; **Strategic Impact**: 324/400 authors (81.0% complete), 48 remaining to pause gate, pipeline ready for confident scaling; **Foreman Validation**: "Well done on navigating the recent quality crisis...continue to 400-author milestone with 100% quality compliance" | **Next**: Continue with remaining seed batches (m11, m14) using proven quality pipeline | **Evidence**: .cccc/work/m13_batch_execution_report.md, .cccc/work/m1/batch_m13_filtered.jsonl (22 records), .cccc/work/m1/batch_m12_filtered_fixed.jsonl (26 records), manifest.count=324, tools/influx-harvest schema fix commit
- 2025-11-14 16:45 | peerB | **PHASE 2 PIPELINE AUTOMATION COMPLETE** (P0 Crisis Prevention Established): Critical TODO elimination completed - all `influx-harvest` functions now enforce quality gates automatically; transform_to_schema function enhanced with mandatory `is_org`/`is_official` fields; official detection heuristics implemented across all harvest functions; brand/risk filtering fully operational; pipeline validation confirms 100% schema compliance; systematic manual bypass risk eliminated. **Strategic Impact**: Quality infrastructure now ready for confident scaling toward 400-author target; P0 crisis prevention infrastructure operational. | **Next**: Resume M1 batch processing with robust automated quality enforcement | **Evidence**: .cccc/work/phase2_completion_report.md, tools/influx-harvest commits, validation tests (276/276 records compliant)
- 2025-11-14 01:10 | peerA | **STRATEGIC PIVOT - Phase 2 Priority** (Aux Analysis #000146): REVISED decision - PAUSE batch merging until Phase 2 (automated filtering pipeline) complete; critical insight: manual merging before Phase 2 recreates P0 crisis conditions; core lesson: manual processes bypass quality gates; pivot from "grow now, fix later" to "fix first, then grow" | **Next**: Complete Phase 2 before resuming batch processing | **Evidence**: Aux strategic review, T000004 direction updated to Phase 2 priority
- 2025-11-14 01:07 | peerA | **FOREMAN OVERRIDE - Resume M1** (Foreman #000147): Strategic pivot overridden - directive to "proceed with next batch of author curation" and resume M1 scaling toward 400 target takes precedence over peer-level strategic caution; clarified directive to proceed with batch processing while maintaining pipeline validation | **Next**: Resume batch processing with quality validation | **Evidence**: Foreman #000147 explicit resumption directive
- 2025-11-13 19:13 | peerA | **Week 1 Pause Gate Confirmed** (Foreman #000119, User request): User requested testing checkpoint at Week 1 completion (~400 total: M0.3 baseline 151 + Week 1 increment ≥250). Pause gate defined in POR.md:42 as non-blocking checkpoint - user reviews ~400 dataset, decides: pause for xoperator integration testing OR continue M1 Week 2-5 execution. M1 final scope (1500-2000 authors) unchanged, acceptance criteria unchanged. Current progress: 200/400 (50%). | **Next**: Continue Week 1 execution toward 400 checkpoint | **Evidence**: POR.md:42, to_user.md (Chinese status report sent)
- 2025-11-13 17:12 | peerB | **M1 ACTIVE - Week 1 Preparation Complete** (Foreman #000102 Item 2): Week 1 scaffolding delivered: lists/seeds/m05-ai-tech-batch.csv (25 AI/Tech handles: karpathy, ylecun, AndrewYNg, sama, gdb, danielgross, swyx, bentossell, demishassabis, ID_AA_Carmack, jeffdean, jeremyphoward, rasbt, etc.), .cccc/work/m1/week1/ directory created | **Next**: Execute Week 1 batch (fetch 25 users via RUBE, run pipeline, generate artifacts) | **Evidence**: commit:7fc528d
- 2025-11-13 08:00 | peerA | **M1 COMMITMENT: PASS with adjusted timeline** - Batch 0.5 probe COMPLETE (PeerB #000091): 47/50 records (94%), 18.6 records/hour sustained velocity (within T000004:24 "15-20 records/hour" decision bracket), zero brand false positives (0/47), 88.7% pass rate (47/53) | **Decision**: Proceed with M1 execution (4-5 weeks, 1.5k-2k target); velocity extrapolates to 13.4-16.1 hours/week for 250-300 records (2-3 hours/day, 5-6 days/week) = SUSTAINABLE; expectation management: weeks 1-3 may trend toward 250/week lower bound, buffer week 5 absorbs variance | **Filter validation**: ZERO brand FPs ✅ (PERFECT precision), 1 risk FP (nic__carter Substack, 1.9% FP rate, acceptable), 5 entry threshold rejects (9.4%, expected), 100% schema compliance | **Evidence**: .cccc/work/m1/batch05/velocity.log, harvest.raw.jsonl (47 records), qa_sample.csv (N=30 stratified), validation.log (47/47 passed)
- 2025-11-13 07:35 | peerA | Updated Next section with explicit yield monitor instrumentation per Foreman #000084: velocity.log format (timestamp, records/hour, rejection rate by stage, QC overhead) | evidence: Foreman #000084 Item(align.pivot) + System #000085 Q4 convergent signal on ambiguous acceptance
- 2025-11-13 07:15 | peerB | T000004 PROPOSED - M1 manual scale SUBPOR created per PeerA #000090 request; goals 1.5k-2k/4-5wk, batch 0.5 probe defined, filter contract integrated | docs/por/T000004-m1-manual-scale/SUBPOR.md

## Aux (tactical, when used)
- (none yet)

- Maintenance note: update this sheet before major steps; keep REV concise.

<!-- Generated on 2025-11-13T07:15:00+00:00 by manual SUBPOR creation ; template_sha1=9ead40e3dc96f80aa7cddce3ac0062ac8329f48d -->
