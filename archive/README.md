# Archive Directory

This directory contains archived files from the influx project cleanup on 2025-11-14.

## Directory Structure

### `completed_batches/`
Contains completed batch work files (CSV, JSONL) and directories from batches m01-m04 that have been fully processed and are no longer active.

### `completed_seeds/`
Contains seed CSV files for completed batches (m01-m05) that are no longer needed for active processing.

### `foreman_sessions/`
Contains 99 timestamped foreman session directories that were cluttering the work directory. These are backup session logs that can be removed if disk space is needed.

### `temp_work/`
Contains temporary Python scripts, session exports, and utility files that were created during batch processing but are no longer needed for active work.

## Active Work Location

Active work files for current batches (m08-m14) and ongoing M1 execution remain in:
- `/.cccc/work/` - Current batch processing files
- `/lists/seeds/` - Active seed files (m08-m14)
- `/data/latest/` - Current data files