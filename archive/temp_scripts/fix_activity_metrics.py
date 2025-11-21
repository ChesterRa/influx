#!/usr/bin/env python3
"""
Fix activity_metrics validation errors by removing activity_metrics from meta objects.
Only activity_metrics in ext.activity_metrics are allowed by the schema.
"""

import json
import sys
from pathlib import Path


def fix_activity_metrics(input_file, output_file):
    """Remove activity_metrics from meta objects while preserving ext.activity_metrics."""

    fixed_count = 0
    total_records = 0
    records_with_meta_activity_metrics = []

    print(f"Processing {input_file}...")

    with (
        open(input_file, "r", encoding="utf-8") as infile,
        open(output_file, "w", encoding="utf-8") as outfile,
    ):
        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
                total_records += 1

                # Check if activity_metrics exists in meta object
                if "meta" in record and "activity_metrics" in record["meta"]:
                    # Store info for reporting
                    handle = record.get("handle", "unknown")
                    records_with_meta_activity_metrics.append(
                        f"Line {line_num}: {handle}"
                    )

                    # Remove activity_metrics from meta
                    del record["meta"]["activity_metrics"]
                    fixed_count += 1

                # Write the (potentially) fixed record
                outfile.write(json.dumps(record, separators=(",", ":")) + "\n")

            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
                continue

    print(f"\nProcessing complete:")
    print(f"  Total records: {total_records}")
    print(f"  Records fixed: {fixed_count}")
    print(f"  Records with meta.activity_metrics removed:")
    for record_info in records_with_meta_activity_metrics:
        print(f"    {record_info}")

    return fixed_count, total_records


if __name__ == "__main__":
    input_file = "/home/dodd/dev/influx/data/latest/latest.jsonl"
    output_file = "/home/dodd/dev/influx/data/latest/latest_fixed.jsonl"

    # Create backup
    backup_file = "/home/dodd/dev/influx/data/latest/latest_backup_before_fix.jsonl"
    if not Path(backup_file).exists():
        Path(input_file).rename(backup_file)
        print(f"Created backup: {backup_file}")
    else:
        print(f"Backup already exists: {backup_file}")
        # Copy from backup to work with original data
        import shutil

        shutil.copy2(backup_file, input_file)

    # Fix the file
    fixed_count, total_records = fix_activity_metrics(input_file, output_file)

    # Replace original with fixed version
    Path(output_file).rename(input_file)
    print(f"Updated original file: {input_file}")

    print(f"\nSummary: Fixed {fixed_count} out of {total_records} records")
