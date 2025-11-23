# AGENTS.md - Influx Project Development Guide
## Build/Test Commands and Code Style Guidelines

---

## 🛠️ BUILD/TEST COMMANDS

### Primary Quality Gate
```bash
# Validate dataset (primary quality gate)
./tools/influx-validate --strict -s schema/bigv.schema.json -m data/latest/manifest.json data/latest/latest.jsonl
```

### Dataset Operations
```bash
# View dataset samples
./tools/influx-view [--lines N]

# Harvest new authors
./tools/influx-harvest bulk --handles-file BATCH.csv --out OUTPUT.jsonl --min-followers 50000 --verified-min-followers 30000

# Score authors
python add_quality_fields.py INPUT.jsonl OUTPUT.jsonl

# Merge new authors
python merge_new_authors.py SCORED_FILE.jsonl
```

---

## 🐍 PYTHON CODE STYLE GUIDELINES

### Python Structure
- Use `#!/usr/bin/env python3` shebang in all tools
- Import order: stdlib → third-party → local modules
- Type hints required for function signatures
- Docstrings for all public functions (triple quotes)

### Data Processing
- Always validate with `influx-validate --strict` before merges
- Maintain 100% strict compliance (no org/official accounts)
- Use SHA256 provenance hashes for audit trails
- Create backups before any dataset modifications

### Error Handling
- Use try/except blocks for file operations
- Exit with proper codes (0=success, 1=error)
- Print errors to stderr, success to stdout
- Validate JSON schema before processing

### Naming Conventions
- Files: kebab-case (e.g., `add_quality_fields.py`)
- Variables: snake_case
- Constants: UPPER_SNAKE_CASE
- Functions: snake_case with descriptive names

### Dataset Operations
- Always check for duplicate handles before merging
- Sort by: score desc, followers_count desc, handle asc
- Update manifest.json with count and SHA256 after changes
- Maintain entry thresholds: 50k followers (30k for verified)

### Quality Gates
- `is_org: false` (no brand/media accounts)
- `is_official: false` (no official/team/PR accounts)
- `entry_threshold_passed: true` (meets minimum criteria)
- `quality_score: 0-100` range in meta

---

## 📋 DATA PROCESSING STANDARDS

### Validation Requirements
- **Strict Compliance**: 100% records must pass `influx-validate --strict`
- **Entry Threshold**: `(verified=true AND followers>=30k) OR followers>=50k`
- **Brand Filtering**: Exclude org/official/media accounts
- **Risk Filtering**: Remove NSFW/political/hate content
- **Provenance**: SHA256 hashes for audit trails

### Pipeline Standards
- **Single Path**: All data must use `influx-harvest` pipeline
- **No Bypass**: Never import data directly without quality gates
- **Quality First**: Maintain perfect validation over speed

---

## 🔧 DEVELOPMENT WORKFLOW

### 1. Preparation
- Check current dataset status
- Identify available seed batches
- Create temporary working directory
- Backup current dataset

### 2. Execution
- Fetch user data via RUBE MCP
- Process through influx-harvest with quality gates
- Validate strict compliance
- Score and merge new authors

### 3. Integration
- Update manifest.json with new count and SHA256
- Validate final dataset
- Archive working files

### 4. Quality Assurance
- Run strict validation on complete dataset
- Manual QA sample (N=30) for each batch
- Document all processing steps and outcomes

---

## 📊 SUCCESS METRICS

### Batch Processing
- **Success Rate**: Target 60-80% per domain
- **Quality**: 100% strict validation compliance
- **Velocity**: 15+ records/hour sustainable
- **Throughput**: 250-350 authors per week

### Dataset Health
- **Validation**: 367/367 records strictly compliant
- **Growth**: +19 net authors from recent batches
- **Quality**: Zero technical debt
- **Pipeline**: Single-path operational excellence

---

## 🎯 AGENT INSTRUCTIONS

### For AI Coding Agents
When working in this repository, follow these guidelines:

#### Code Generation
- **Quality First**: Always prioritize data quality over quantity
- **Schema Compliance**: Ensure all generated data matches `bigv.schema.json`
- **Validation**: Run `influx-validate --strict` before any integration
- **Provenance**: Include SHA256 hashes for auditability
- **Error Handling**: Use try/except blocks, proper exit codes

#### File Operations
- **Safety First**: Create backups before modifications
- **Atomic Changes**: Make small, reversible changes
- **Validation**: Validate after each operation
- **Documentation**: Update relevant documentation

#### Testing
- **Unit Tests**: Test individual components
- **Integration Tests**: Test complete workflow
- **Quality Gates**: Never bypass validation requirements

#### Security
- **No Secrets**: Never expose API keys or sensitive data
- **Input Validation**: Validate all inputs before processing
- **Audit Trail**: Maintain provenance hashes

---

## 📝 MAINTENANCE GUIDELINES

### Regular Tasks
- **Daily**: Validate dataset, check pipeline status
- **Weekly**: Review quality metrics, update documentation
- **Monthly**: Comprehensive quality audit, update success metrics

### Code Quality
- **Reviews**: All code changes require peer review
- **Testing**: All new features require comprehensive testing
- **Documentation**: Keep all guides current and accurate

---

**Last Updated**: 2025-11-21
**Version**: 1.0.0