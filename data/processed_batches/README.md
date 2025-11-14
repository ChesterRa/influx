# Processed Batches Archive

This directory contains JSONL files from influencer batches that have been successfully processed and merged into the main dataset.

## File Structure

Files in this directory follow the naming convention:
- `batch-name.jsonl` - Cleaned, quality-filtered batch data
- `batch-name-users.jsonl` - Raw Twitter API user responses

## Archive Purpose

These files serve as:
1. **Audit Trail** - Complete processing history
2. **Recovery Source** - Ability to recreate datasets if needed
3. **Quality Reference** - Before/after filtering comparison
4. **Debug Resource** - Tool development and testing

## Current Status

All batches in this archive have been:
- Processed through `influx-harvest` pipeline
- Quality filtered with brand heuristics
- Successfully merged into `../latest/latest.jsonl`
- Verified for schema compliance

Processing date: 2025-11-14