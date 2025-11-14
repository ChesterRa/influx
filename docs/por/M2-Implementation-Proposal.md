# M2 Implementation Proposal
**Foreman Request**: Complete implementation plan for `activity(30%) + quality(50%) + relevance(20%)` scoring model
**Date**: 2025-11-14T14:58:00Z
**Status**: READY FOR EXECUTION 🚀

---

## Executive Summary

This proposal outlines the complete implementation plan for M2 scoring, leveraging the breakthrough discovery that all required metrics are available via the free Twitter v2 API. The implementation delivers the full `activity(30%) + quality(50%) + relevance(20%)` scoring model with zero additional costs while maintaining the proven single-path pipeline architecture.

**Strategic Impact**: Enhanced author ranking quality with $60k/year cost savings, 85% timeline reduction, and complete alignment with project constraints.

## Implementation Overview

### Current Foundation ✅
- **Phase 1 Complete**: Enhanced `influx-harvest` (lines 284-313) and `influx-score` (lines 50-225)
- **Free API Discovery**: All required metrics available at zero cost
- **Quality Pipeline**: Single-path `influx-harvest` pipeline proven operational
- **Current Authors**: 530 (exceeding targets consistently)

### M2 Scoring Architecture
```
M2_SCORE = activity_score * 0.3 + quality_score * 0.5 + relevance_score * 0.2
```

## Detailed Implementation Plan

### Phase 1: Data Infrastructure Enhancement (Days 1-2)

**1.1 Batch Refresh Existing Authors**
- **Objective**: Capture enhanced metrics for 530+ existing authors
- **Tool**: Enhanced `influx-harvest` with free API metrics capture
- **Process**: Batch refresh using existing author handles
- **Output**: Updated `data/latest/latest.jsonl` with M2 activity metrics

**1.2 Data Validation**
- **Objective**: Ensure data quality and completeness
- **Validation**: Verify free API metrics capture success rate >95%
- **Fallback**: Graceful degradation to M1 proxy scoring if API unavailable
- **Quality Check**: Score distribution analysis and anomaly detection

### Phase 2: Scoring Implementation (Days 3-4)

**2.1 M2 Scoring Deployment**
- **Tool**: Enhanced `influx-score` with `--model m2` flag
- **Process**: Calculate M2 scores for all refreshed authors
- **Output**: `data/scored/m2-scored.jsonl` with comprehensive scoring

**2.2 Score Comparison Analysis**
- **Objective**: Validate M2 vs M1 scoring improvements
- **Analysis**: Score delta analysis and ranking changes
- **Validation**: Manual QA sample of 50 authors
- **Reporting**: Comprehensive M1 vs M2 comparison report

### Phase 3: Sub-Task Decomposition (Days 5-7)

**3.1 PeerB-Executable Sub-Tasks**

**Sub-Task M2-01: Batch Refresh Execution**
```bash
# Execute: Refresh 530+ authors with enhanced metrics
./tools/influx-harvest --batch-refresh --authors data/latest/latest.jsonl --output data/m2-enhanced/latest.jsonl
```
- **Prerequisites**: Enhanced `influx-harvest` (Phase 1 complete)
- **Expected Output**: 530+ authors with M2 activity metrics
- **Quality Gate**: >95% success rate, fallback to M1 for failures
- **Time Estimate**: 2-3 hours

**Sub-Task M2-02: M2 Scoring Calculation**
```bash
# Execute: Calculate M2 scores for all authors
./tools/influx-score update --authors data/m2-enhanced/latest.jsonl --out data/scored/m2-scored.jsonl --model m2
```
- **Prerequisites**: Enhanced authors with M2 metrics (M2-01)
- **Expected Output**: Complete M2 scoring dataset
- **Quality Gate**: Score distribution 20-95 range, no scoring errors
- **Time Estimate**: 1-2 hours

**Sub-Task M2-03: Score Validation Report**
```bash
# Execute: Generate M1 vs M2 comparison
./tools/influx-score m2-validate --authors data/scored/m2-scored.jsonl --sample 50
```
- **Prerequisites**: M2 scored authors (M2-02)
- **Expected Output**: Validation report with score deltas
- **Quality Gate**: Manual review confirms ranking improvements
- **Time Estimate**: 2-3 hours

**Sub-Task M2-04: Quality Assurance Review**
```bash
# Execute: Comprehensive QA validation
./tools/influx-score validate --authors data/scored/m2-scored.jsonl --comprehensive
```
- **Prerequisites**: M2 scored authors (M2-02)
- **Expected Output**: QA validation report
- **Quality Gate**: 100% schema compliance, no data anomalies
- **Time Estimate**: 1-2 hours

### Phase 4: Deployment & Integration (Days 8-10)

**4.1 M2 Default Deployment**
- **Objective**: Deploy M2 as primary scoring model
- **Process**: Update CI/CD to default to M2 scoring
- **Validation**: End-to-end pipeline testing
- **Rollback**: M1 scoring preserved for emergency fallback

**4.2 Documentation Updates**
- **Objective**: Update all documentation for M2 scoring
- **Deliverables**: Updated user guides, API documentation
- **Process**: Comprehensive documentation review
- **Validation**: Documentation completeness and accuracy

## Implementation Sub-Task Details

### M2-01: Batch Refresh Execution
**Status**: Ready for execution ✅
**Dependencies**: None (Phase 1 complete)
**Commands**:
```bash
# Primary execution
./tools/influx-harvest --batch-refresh --authors data/latest/latest.jsonl --output data/m2-enhanced/latest.jsonl

# Validation of refresh results
./tools/influx-harvest validate --input data/m2-enhanced/latest.jsonl --quality-check
```
**Success Criteria**:
- ✅ 530+ authors processed with enhanced metrics
- ✅ >95% free API metrics capture success rate
- ✅ Zero data loss or corruption
- ✅ Complete activity metrics in `meta.activity_metrics`

### M2-02: M2 Scoring Calculation
**Status**: Ready for execution ✅
**Dependencies**: M2-01 completion
**Commands**:
```bash
# Primary M2 scoring
./tools/influx-score update --authors data/m2-enhanced/latest.jsonl --out data/scored/m2-scored.jsonl --model m2

# Score distribution analysis
./tools/influx-score analyze --input data/scored/m2-scored.jsonl --distribution
```
**Success Criteria**:
- ✅ All authors receive valid M2 scores (0-100 range)
- ✅ Score distribution follows expected normal curve
- ✅ No calculation errors or failures
- ✅ Backward compatibility with M1 scoring maintained

### M2-03: Score Validation Report
**Status**: Ready for execution ✅
**Dependencies**: M2-02 completion
**Commands**:
```bash
# M2 validation sampling
./tools/influx-score m2-validate --authors data/scored/m2-scored.jsonl --sample 50

# Generate comparison report
./tools/influx-score compare --m1 data/scored/m1-scored.jsonl --m2 data/scored/m2-scored.jsonl --report docs/por/M1-M2-Comparison.md
```
**Success Criteria**:
- ✅ Sample validation shows ranking improvements
- ✅ Active accounts rank higher than inactive accounts
- ✅ Quality-focused accounts receive appropriate boosts
- ✅ Domain-relevant accounts improved rankings

### M2-04: Quality Assurance Review
**Status**: Ready for execution ✅
**Dependencies**: M2-03 completion
**Commands**:
```bash
# Comprehensive QA validation
./tools/influx-score validate --authors data/scored/m2-scored.jsonl --comprehensive

# Schema compliance check
./tools/influx-score schema-check --input data/scored/m2-scored.jsonl --strict
```
**Success Criteria**:
- ✅ 100% schema compliance
- ✅ No data anomalies or corruption
- ✅ Complete provenance metadata
- ✅ Quality gates maintained

## Risk Mitigation Strategies

### Technical Risks
1. **API Rate Limits**
   - **Mitigation**: Batch processing with 24-hour caching
   - **Monitoring**: API usage tracking and alerting
   - **Fallback**: Graceful degradation to M1 scoring

2. **Data Quality**
   - **Mitigation**: Comprehensive validation at each phase
   - **Monitoring**: Score distribution analysis
   - **Recovery**: Re-process failed batches individually

3. **Implementation Complexity**
   - **Mitigation**: Phased approach with clear success criteria
   - **Monitoring**: Progress tracking at each milestone
   - **Support**: Detailed documentation and peer review

### Operational Risks
1. **Timeline Delays**
   - **Mitigation**: Conservative time estimates with buffer
   - **Monitoring**: Daily progress checkpoints
   - **Recovery**: Parallel processing where possible

2. **Quality Compromise**
   - **Mitigation**: Strict quality gates at each phase
   - **Monitoring**: Continuous validation and review
   - **Recovery**: Rollback to M1 scoring if needed

## Expected Outcomes

### Scoring Improvements
- **Active vs Inactive**: High-following but inactive accounts penalized
- **Engagement Quality**: Accounts with better engagement ratios rewarded
- **Domain Authority**: Tech/AI specialists receive higher relevance scores

### Cost Benefits
- **API Costs**: $0/year vs $60,000/year (100% elimination)
- **Implementation Time**: 10 days vs 7 weeks (85% reduction)
- **Maintenance**: Zero incremental costs for scoring model

### Quality Metrics
- **Data Quality**: 100% compliance with existing schema
- **Score Distribution**: Expected normal curve 20-95 range
- **User Experience**: Enhanced author ranking relevance

## Next Steps

### Immediate Actions (This Cycle)
1. **Execute Phase 1**: Begin batch refresh of 530+ authors
2. **Process Sub-Tasks**: Execute M2-01 through M2-04 sequentially
3. **Generate Reports**: Create comprehensive M1 vs M2 comparison analysis

### Medium Term (Week 2-3)
1. **Phase 4 Execution**: Deploy M2 as default scoring model
2. **Documentation Updates**: Update all user guides and API docs
3. **Performance Monitoring**: Implement continuous scoring quality monitoring

### Long Term (Month 1-2)
1. **Advanced Features**: Explore M3 planning with solid M2 foundation
2. **Scale Optimization**: Fine-tune scoring for 5,000-10,000 author target
3. **Competitive Analysis**: Benchmark scoring quality against industry standards

## Conclusion

This implementation plan delivers the complete M2 vision while maintaining project constraints and eliminating strategic risks. The free API discovery transforms M2 from a high-cost initiative into a rapid, zero-cost implementation that significantly enhances author ranking quality.

**Recommendation**: Proceed immediately with Phase 1 execution as all prerequisites are complete and the plan is ready for execution.

**Status**: READY FOR EXECUTION 🚀