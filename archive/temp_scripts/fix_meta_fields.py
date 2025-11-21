#!/usr/bin/env python3
"""
Fix schema validation errors by moving disallowed fields from meta to ext.

This script addresses the issue where activity_metrics and other fields
are in meta but should be in ext according to the schema.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set


def fix_meta_fields(input_file: str, output_file: str | None = None) -> Tuple[int, int]:
    """
    Move disallowed fields from meta to ext in the JSONL file.

    Args:
        input_file: Path to input JSONL file
        output_file: Path to output file (defaults to input_file for in-place fix)

    Returns:
        Tuple of (total_records, fixed_records)
    """
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    actual_output_file = output_file or input_file

    # Allowed fields in meta according to schema
    allowed_meta_fields = {
        "score",
        "rank_global",
        "last_active_at",
        "last_refresh_at",
        "sources",
        "provenance_hash",
    }

    total_records = 0
    fixed_records = 0
    records = []

    print(f"Reading records from {input_file}...")

    # Read all records
    with open(input_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
                total_records += 1

                # Check if meta has disallowed fields
                meta = record.get("meta", {})
                disallowed_fields = set(meta.keys()) - allowed_meta_fields

                if disallowed_fields:
                    print(
                        f"Line {line_num}: Moving {len(disallowed_fields)} disallowed fields from meta to ext for {record.get('handle', 'unknown')} (id: {record.get('id', 'unknown')})"
                    )
                    print(f"  Disallowed fields: {', '.join(disallowed_fields)}")

                    # Initialize ext if it doesn't exist
                    if "ext" not in record:
                        record["ext"] = {}

                    # Move disallowed fields from meta to ext
                    for field in disallowed_fields:
                        record["ext"][field] = meta[field]
                        del meta[field]

                    fixed_records += 1

                records.append(record)

            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}", file=sys.stderr)
                continue

    print(
        f"\nProcessed {total_records} records, fixing {fixed_records} records with disallowed meta fields"
    )

    # Write fixed records
    with open(actual_output_file, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, separators=(",", ":")) + "\n")

    return total_records, fixed_records


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_meta_fields.py <input_file> [output_file]")
        print(
            "If output_file is not specified, the input file will be updated in-place."
        )
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        total, fixed = fix_meta_fields(input_file, output_file)
        print(f"✅ Successfully fixed {fixed} out of {total} records")

        if fixed > 0:
            updated_file = output_file or input_file
            print(f"📝 File updated: {updated_file}")
            print("\nRun validation to confirm:")
            print(f"./tools/influx-validate -s schema/bigv.schema.json {updated_file}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
