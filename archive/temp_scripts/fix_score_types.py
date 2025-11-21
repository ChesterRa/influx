#!/usr/bin/env python3
"""
Fix score type validation errors by converting string scores to numbers.

This script addresses the issue where scores are stored as strings instead of numbers.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def fix_score_types(input_file: str, output_file: str | None = None) -> Tuple[int, int]:
    """
    Fix score types in the JSONL file by converting strings to numbers.

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

                # Check if score needs fixing
                score = record.get("meta", {}).get("score")

                if isinstance(score, str):
                    try:
                        # Convert string score to float
                        new_score = float(score)
                        print(
                            f"Line {line_num}: Converting score '{score}' to {new_score} for {record.get('handle', 'unknown')} (id: {record.get('id', 'unknown')})"
                        )

                        # Update the record
                        if "meta" not in record:
                            record["meta"] = {}
                        record["meta"]["score"] = new_score

                        fixed_records += 1
                    except ValueError:
                        print(
                            f"Line {line_num}: Warning - Could not convert score '{score}' to number for {record.get('handle', 'unknown')}",
                            file=sys.stderr,
                        )

                records.append(record)

            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}", file=sys.stderr)
                continue

    print(f"\nProcessed {total_records} records, fixing {fixed_records} score types")

    # Write fixed records
    with open(actual_output_file, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, separators=(",", ":")) + "\n")

    return total_records, fixed_records


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_score_types.py <input_file> [output_file]")
        print(
            "If output_file is not specified, the input file will be updated in-place."
        )
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        total, fixed = fix_score_types(input_file, output_file)
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
