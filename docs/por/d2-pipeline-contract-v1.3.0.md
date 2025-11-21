# Pipeline Contract Update v1.3.0

## M2 Scoring Model Production Standardization

### Executive Update
**STATUS**: M2 scoring model successfully deployed as production standard, replacing M1 proxy scoring across all operations.

### Production Scoring Standard

#### M2 Composite Scoring Formula
```
Score = Activity(30%) + Quality(50%) + Relevance(20%)
```

**Activity Metrics (30%)**:
- tweet_count: 30-day original tweet volume
- like_count: Engagement metrics from public APIs
- media_count: Content creation patterns
- listed_count: Community recognition indicators
- following_count: Network engagement metrics

**Quality Metrics (50%)**:
- verification_status: Blue/verified/none enhancement
- followers_count: Raw influence metrics
- engagement_ratios: Reply/retweet quality indicators
- content_quality: Originality and value contribution signals

**Relevance Metrics (20%)**:
- domain_expertise: Technical leadership and specialization
- topic_alignment: AI/Tech/domain-specific relevance
- industry_impact: Thought leadership and innovation influence

### Single-Path Pipeline Enforcement

#### Mandatory Data Processing Flow
```
1. Author Discovery → influx-harvest (ONLY)
2. Data Validation → influx-validate --strict
3. M2 Scoring → influx-score update
4. Quality Assurance → schema compliance check
5. Dataset Export → influx-export latest
```

#### Quality Gates
- **Entry Threshold**: (verified=true AND followers>=30k) OR followers>=50k
- **Brand Filtering**: brand_heuristics.yml with automated validation
- **Risk Filtering**: risk_terms.yml with explicit content screening
- **Schema Compliance**: bigv.schema.json with strict validation

### Infrastructure Requirements

#### Toolchain Standards
- **influx-harvest**: Enhanced with activity metrics capture
- **influx-score**: M2 composite scoring implementation
- **influx-validate**: Strict schema and business rule validation
- **influx-export**: Production dataset export with M2 scores

#### API Integration
- **Source**: Twitter v2 Free Tier (zero cost)
- **Endpoints**: Public user endpoints for activity metrics
- **Rate Management**: Intelligent batching and request optimization
- **Cost Model**: $0/year operational sustainability

### Quality Assurance Standards

#### Schema Compliance
- **Required Fields**: All fields in bigv.schema.json mandatory
- **Data Types**: Strict type enforcement for all JSON fields
- **Validation Rate**: 100% compliance required for production deployment

#### Brand/Risk Enforcement
- **Brand Detection**: Automated heuristic filtering with manual verification
- **Risk Screening**: Explicit term-based content filtering
- **False Positive Rate**: <3.3% maximum tolerance threshold
- **Manual Review**: N=30-50 samples per batch for quality validation

### Production Deployment Protocol

#### Data Processing Standards
```
INPUT: Author handles (CSV format)
PROCESS: influx-harvest → activity metrics capture
SCORE: influx-score update (M2 formula)
VALIDATE: influx-validate --strict
EXPORT: influx-export latest (with M2 scores)
```

#### Quality Control Flow
```
BATCH PROCESSING:
1. Prefetch user data via RUBE MCP
2. Harvest with activity metrics
3. Apply M2 scoring formula
4. Validate schema compliance
5. QA sample review (N=30-50)
6. Export production dataset
7. Update manifest.json
```

### Success Criteria

#### Technical Excellence
- **M2 Coverage**: 100% of authors with meaningful scores (4.5-52.9 range)
- **Quality Rate**: 100% schema compliance, zero brand contamination
- **Data Integrity**: Unique ID validation, provenance tracking complete
- **Infrastructure**: Zero-cost model maintained, production stability ensured

#### Operational Excellence
- **Processing Velocity**: 50-100+ authors/day with automated quality gates
- **Error Rate**: <1% across all batch operations
- **Update Frequency**: Weekly activity metrics refresh for 95%+ authors
- **Scalability**: Proven infrastructure ready for 10x expansion

---
*Pipeline Contract Status: UPDATED v1.3.0 - M2 Production Standard Established*
*Next Action: Begin M1 scaling with M2 production standards*
