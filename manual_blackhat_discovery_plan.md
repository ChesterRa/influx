# Manual Pivot Execution Plan - BlackHat 2024 Speakers

## Phase 1: Conference Speaker Discovery

### Target Conference: BlackHat 2024
**Rationale**: Premier cybersecurity conference, high-profile individual speakers, active Twitter presence

### Discovery Process
1. **Speaker List Extraction**: 
   - BlackHat 2024 official website → speaker list
   - Filter for individual speakers (not corporate representatives)
   - Focus on technical presenters, keynotes, workshop instructors

2. **Twitter Handle Verification**:
   - Search speaker names + "Twitter" 
   - Verify through official BlackHat speaker bios
   - Cross-reference with LinkedIn profiles

3. **Quality Filtering**:
   - Minimum 50k followers (30k for verified)
   - Individual accounts only (no corporate/official accounts)
   - Active posting patterns (last 30 days)

### Expected Yield
- **Target**: 15-20 qualified speakers
- **Success Rate**: 60-70% expected to meet entry thresholds
- **Quality Score**: 70-90 range based on followers + verification

### Integration Pipeline
1. **Manual Discovery** → Speaker list + Twitter handles
2. **RUBE MCP Single Tool** → User profile verification
3. **Quality Scoring** → Followers + verification + activity
4. **Schema Conversion** → Proper dataset format
5. **Validation** → influx-validate --strict compliance
6. **Merge** → Main dataset with manifest update

### Next 2-Hour Execution
**Immediate Action**: Extract BlackHat 2024 speaker list
**Time Estimate**: 2 hours for speaker discovery + initial verification
**Expected Output**: 20-30 potential Twitter handles for processing