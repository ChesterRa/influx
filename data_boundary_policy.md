# Data Boundary Policy Implementation

## Policy Statement

**Single Source of Truth**: Only `data/latest/` and `data/batches/` (via influx-harvest pipeline) contain production data. All analysis files must be in `.cccc/work/scratch/` or `archive/manual_analysis/`.

## Implementation Actions

### ✅ Completed
1. **Archived Manual Files**: Moved 10 stale .jsonl files from root to `archive/manual_analysis/`
2. **Updated POR Targets**: Adjusted from 250→150-200 authors reflecting 84 baseline
3. **Cleaned Root Directory**: Removed temporary analysis artifacts

### 📋 Policy Boundaries

#### Production Data (Validated)
- `data/latest/latest.jsonl` - Current dataset (84 authors)
- `data/latest/manifest.json` - Dataset metadata
- `data/batches/` - influx-harvest processed batches only
- `data/release/` - Production releases

#### Analysis Workspace (Temporary)
- `.cccc/work/scratch/` - Active analysis files
- `archive/manual_analysis/` - Completed analysis
- Root directory: NO .jsonl files allowed

#### Quality Enforcement
- All production data must pass `influx-validate --strict`
- Provenance hashes required for all records
- Single-path pipeline through influx-harvest mandatory

## Risk Mitigation

### Technical Debt Prevention
- **No Manual .jsonl in Root**: Prevents confusion with production data
- **Archive Policy**: Analysis files moved after completion
- **Pipeline Guard**: Only influx-harvest outputs in production

### Quality Assurance
- **Strict Validation**: 100% compliance required
- **Provenance Tracking**: SHA256 hashes for audit trail
- **Single Source**: Eliminates duplicate/conflicting data

## Next Steps

### Immediate (Next 24h)
1. **Process M11 Batch**: 22 qualified authors through influx-harvest
2. **Update Documentation**: Add policy to PROJECT.md
3. **Reach 106 Authors**: First milestone in rebuild

### Short-term (Next 72h)
1. **Process M13 Security**: 10 qualified authors
2. **Implement Workspace Policy**: Formalize analysis file handling
3. **Reach 150 Authors**: Realistic target from clean baseline

## Compliance Status

- ✅ **Production Data**: 84 authors, 100% validated
- ✅ **Workspace Clean**: All manual files archived
- ✅ **Policy Updated**: POR targets aligned with reality
- ✅ **Pipeline Ready**: influx-harvest functional

---
*Policy Implementation Complete: 2025-11-23T02:15:00Z*
*Status: Ready for accelerated domain batch processing*