# Seed Lists Directory

This directory contains CSV seed lists for influencer discovery and curation.

## File Naming Convention

- `m##-domain-batch.csv` - Domain-specific seed lists (e.g., `m08-ai-research-batch.csv`)
- `github-orgs.csv` - GitHub organizations seed list
- `m##-numbered` indicates processing order in M1 execution phase

## Usage

Seed lists are processed by the `influx-harvest` pipeline using the single-path quality gate system:
1. **Data Fetching** - Twitter API integration via RUBE MCP
2. **Quality Filtering** - Brand heuristics + entry thresholds
3. **Schema Validation** - Mandatory field compliance
4. **Merge to Latest** - Clean authors added to `data/latest/latest.jsonl`

## Quality Standards

- Individual accounts only (no corporate/official accounts)
- Minimum 10,000 followers
- Complete profile data (name, bio, verified status)
- 100% quality compliance required

## Processing Status

Current authors in main dataset: 525+
Target for M1 complete: 1,500-2,000 authors

Last updated: 2025-11-14