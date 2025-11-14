# Contributing to Influx

## 🚨 **CRITICAL: SINGLE-PATH DATA INGESTION POLICY**

### **MANDATORY: influx-harvest EXCLUSIVITY**
**ALL data added to this project MUST AND CAN ONLY be processed through the `tools/influx-harvest` pipeline.**

```
❌ FORBIDDEN:
- Manual JSON editing
- Custom scripts
- Direct API calls
- ANY bypass of influx-harvest

✅ REQUIRED:
tools/influx-harvest → Prefetch → Harvest → Score → Merge → Export → Validate
```

**Why this exists**: The project's core mission is to build a **high-quality, trustworthy author index**. Any circumvention of the quality gates will directly lead to project failure.

---

## **Data Addition Workflow**

### **For New Author Batches**

1. **Prepare CSV seed list** in `lists/seeds/` following naming convention:
   ```
   m##-domain-batch.csv (e.g., m15-web3-batch.csv)
   ```

2. **Process ONLY through influx-harvest**:
   ```bash
   # From project root
   tools/influx-harvest lists/seeds/your-batch.csv
   ```

3. **Quality Gates Automatically Enforced**:
   - Brand heuristics filtering (v2.0)
   - Entry threshold validation (10K+ followers)
   - Schema compliance checks
   - Individual account verification

4. **Update Documentation**:
   - Update `data/latest/manifest.json`
   - Record progress in `velocity.log`
   - Archive processed batches to `data/processed_batches/`

### **Quality Standards**

All authors in the main dataset MUST meet **ALL** criteria:

| Requirement | Threshold | Enforced by |
|-------------|-----------|-------------|
| Followers | ≥ 10,000 | influx-harvest |
| Account Type | Individual only | Brand heuristics |
| Completeness | 100% profile data | Schema validation |
| Quality Score | 0.0 - 1.0 | Scoring algorithm |

**ZERO TOLERANCE POLICY**: Any violation (corporate accounts, official accounts, below threshold) results in batch rejection.

---

## **Development Process**

### **Code Changes**

1. **Fork and create feature branch**
2. **All changes must preserve quality standards**
3. **CI/CD automatically enforces compliance**:
   - Schema validation for all JSONL files
   - **STRICT validation for main branch**: `influx-validate --strict`
   - Quality gate compliance verification

4. **Pull Request Requirements**:
   - Clear description of changes
   - Impact on data quality assessment
   - No shortcuts around quality gates

### **Quality Assurance**

#### **Schema Validation**
```bash
# Regular validation (development)
python tools/influx-validate -s schema/bigv.schema.json data/latest/latest.jsonl

# Strict validation (main branch enforcement)
python tools/influx-validate --strict -s schema/bigv.schema.json data/latest/latest.jsonl
```

#### **Quality Gate Compliance**
The `--strict` flag enforces:
- Required quality fields present (`is_org`, `is_official`, `entry_threshold_passed`, `quality_score`)
- No organizational/official accounts
- Minimum follower counts
- Valid quality score ranges

---

## **Project Structure Compliance**

```
influx/
├── data/latest/           # Main dataset (quality controlled)
│   ├── latest.jsonl      # Primary author database
│   ├── latest.jsonl.gz   # Compressed version
│   └── manifest.json     # Dataset metadata
├── lists/seeds/          # Input CSV files for influx-harvest
├── data/processed_batches/  # Archive of processed data
├── tools/
│   ├── influx-harvest    # ❗ ONLY data ingestion tool
│   └── influx-validate   # Schema and quality validation
└── lists/rules/
    └── brand_heuristics.yml  # v2.0 quality filtering rules
```

---

## **Quality Crisis Prevention**

### **Red Flags - IMMEDIATE ACTION REQUIRED**
If you encounter any of these, STOP and report:

1. **Corporate/Organizational Accounts**: Any `is_org: true` records in final dataset
2. **Missing Quality Fields**: Records lacking `quality_score` or other required fields
3. **Below Threshold**: Accounts with < 10,000 followers
4. **Manual Data Editing**: Direct modification of JSONL files
5. **Bypass Scripts**: Any tool that circumvents influx-harvest

### **Quality Verification Commands**
```bash
# Check for org accounts (should return 0)
grep '"is_org": true' data/latest/latest.jsonl | wc -l

# Verify quality fields presence
python tools/influx-validate --strict -s schema/bigv.schema.json data/latest/latest.jsonl

# Check dataset health
python tools/influx-harvest --stats
```

---

## **Getting Started**

### **Prerequisites**
- Python 3.11+
- Dependencies from `requirements.txt`
- Twitter API access (for influx-harvest)

### **First Contribution**
1. **Read PROJECT.md** - Understand project goals and architecture
2. **Study existing batches** - Review `lists/seeds/` for format examples
3. **Run validation locally** - Ensure your changes pass quality gates
4. **Create issue** - Discuss your planned contribution before starting

### **Quality Tools**
```bash
# Validate data format
python tools/influx-validate -s schema/bigv.schema.json your-data.jsonl

# Process new batch (ONLY way to add authors)
python tools/influx-harvest lists/seeds/your-new-batch.csv

# Check dataset statistics
python tools/influx-harvest --stats data/latest/latest.jsonl
```

---

## **Enforcement**

### **CI/CD Protection**
- **Pull Requests**: Schema validation only
- **Main Branch**: STRICT validation with quality gate compliance
- **Automatic Failures**: Any quality violation blocks merge

### **Manual Review**
All changes to `data/latest/` must demonstrate:
1. **Quality Compliance**: 100% individual author accounts
2. **Process Compliance**: Processed through influx-harvest only
3. **Documentation**: Updated manifest and logs

---

## **⚠️  CONSEQUENCES**

### **Quality Violations**
- **Immediate PR rejection**
- **Issue creation for cleanup**
- **Potential project rollback requirements**
- **Review of contribution privileges**

### **Process Violations**
- **Warning first**
- **PR blocked until compliance**
- **Documentation requirements**
- **Community review for repeated violations**

---

## **Questions & Support**

1. **Check existing issues** - Your question may be answered
2. **Review PROJECT.md** - Architecture and goals
3. **Examine successful batches** - Learn from examples in `lists/seeds/`
4. **Ask before implementing** - Quality is our top priority

### **Quality Standards Reminder**
> "The core mission is to build a high-quality, trustworthy author index. Any circumvention of quality gates will directly lead to project failure."

**When in doubt: err on the side of quality, ask for review, and NEVER bypass influx-harvest.**

---

*This contributing guide enforces the Foreman directive: "所有数据入库必须且只能通过 `tools/influx-harvest` 工具处理。"*