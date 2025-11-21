#!/usr/bin/env python3
"""
Fix missing last_refresh_at fields by using fetched_at from sources.

This script addresses the issue where records are missing the required
last_refresh_at field in meta, but have fetched_at in sources.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def fix_missing_last_refresh(
    input_file: str, output_file: str | None = None
) -> Tuple[int, int]:
    """
    Add missing last_refresh_at fields using fetched_at from sources.

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

                # Check if last_refresh_at is missing
                meta = record.get("meta", {})
                sources = meta.get("sources", [])

                if "last_refresh_at" not in meta and sources:
                    # Use fetched_at from the first source
                    first_source = sources[0]
                    fetched_at = first_source.get("fetched_at")

                    if fetched_at:
                        print(
                            f"Line {line_num}: Adding last_refresh_at '{fetched_at}' for {record.get('handle', 'unknown')} (id: {record.get('id', 'unknown')})"
                        )
                        meta["last_refresh_at"] = fetched_at
                        fixed_records += 1
                    else:
                        print(
                            f"Line {line_num}: Warning - No fetched_at found in sources for {record.get('handle', 'unknown')}",
                            file=sys.stderr,
                        )

                records.append(record)

            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}", file=sys.stderr)
                continue

    print(
        f"\nProcessed {total_records} records, fixing {fixed_records} missing last_refresh_at fields"
    )

    # Write fixed records
    with open(actual_output_file, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, separators=(",", ":")) + "\n")

    return total_records, fixed_records


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_missing_last_refresh.py <input_file> [output_file]")
        print("If output_file is not specified, input file will be updated in-place.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        total, fixed = fix_missing_last_refresh(input_file, output_file)
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
