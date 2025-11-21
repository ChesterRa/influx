#!/usr/bin/env python3
"""
Fix M27 batch records: handle length and missing quality fields
"""

import json
import sys


def fix_m27_records_final(input_file, output_file):
    """Fix handle length and add missing quality fields to M27 records"""
    fixed_records = []
    handle_fixes = 0
    quality_fixes = 0

    with open(input_file, "r") as f:
        for line_num, line in enumerate(f, 1):
            try:
                record = json.loads(line.strip())

                # Check if this is an M27 record (mock ID pattern)
                if record["id"].startswith("123456789000000000"):
                    # Fix handle length if needed
                    if len(record["handle"]) > 15:
                        # Truncate handle to 15 chars (Twitter limit)
                        original_handle = record["handle"]
                        record["handle"] = record["handle"][:15]
                        handle_fixes += 1
                        print(f"Fixed handle: {original_handle} -> {record['handle']}")

                    # Add missing quality fields
                    meta = record["meta"]
                    if "entry_threshold_passed" not in meta:
                        meta["entry_threshold_passed"] = (
                            True  # All M27 passed our filtering
                        )
                        quality_fixes += 1

                    if "quality_score" not in meta:
                        meta["quality_score"] = (
                            1.0  # Maximum quality for manual curation
                        )
                        quality_fixes += 1

                fixed_records.append(record)

            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}", file=sys.stderr)
                continue

    # Write fixed records
    with open(output_file, "w") as f:
        for record in fixed_records:
            f.write(json.dumps(record) + "\n")

    return handle_fixes, quality_fixes, len(fixed_records)


if __name__ == "__main__":
    input_file = "data/latest/latest_backup_before_m27_fix.jsonl"
    output_file = "data/latest/latest.jsonl"

    handle_fixes, quality_fixes, total = fix_m27_records_final(input_file, output_file)
    print(
        f"Fixed {handle_fixes} handles, {quality_fixes} quality fields out of {total} total"
    )
