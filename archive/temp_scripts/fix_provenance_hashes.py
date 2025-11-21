#!/usr/bin/env python3
"""
Fix provenance_hash validation errors by regenerating proper SHA-256 hashes.

This script addresses the issue where 151 records have 40-character placeholder
hashes instead of the required 64-character SHA-256 hashes.
"""

import json
import hashlib
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple


def is_valid_hash(hash_str: str) -> bool:
    """Check if hash is a valid 64-character hex string (SHA-256)"""
    return bool(re.match(r"^[A-Fa-f0-9]{64}$", hash_str))


def compute_provenance_hash(record: Dict) -> str:
    """
    Compute SHA-256 provenance hash from canonical record fields.

    This follows the same pattern as influx-harvest's compute_provenance_hash
    but works with the schema format rather than Twitter API format.
    """
    # Extract canonical fields for hashing
    canonical = {
        "id": record.get("id", ""),
        "handle": record.get("handle", ""),
        "name": record.get("name", ""),
        "followers_count": record.get("followers_count", 0),
        "verified": record.get("verified", "none"),
    }

    # Sort keys and compact JSON (no spaces)
    canonical_json = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def fix_provenance_hashes(
    input_file: str, output_file: str | None = None
) -> Tuple[int, int]:
    """
    Fix provenance hashes in the JSONL file.

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

                # Check if provenance_hash needs fixing
                current_hash = record.get("meta", {}).get("provenance_hash", "")

                if not is_valid_hash(current_hash):
                    print(
                        f"Line {line_num}: Fixing invalid hash '{current_hash}' for {record.get('handle', 'unknown')} (id: {record.get('id', 'unknown')})"
                    )

                    # Generate new hash
                    new_hash = compute_provenance_hash(record)

                    # Update the record
                    if "meta" not in record:
                        record["meta"] = {}
                    record["meta"]["provenance_hash"] = new_hash

                    fixed_records += 1

                records.append(record)

            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}", file=sys.stderr)
                continue

    print(f"\nProcessed {total_records} records, fixing {fixed_records} invalid hashes")

    # Write fixed records
    with open(actual_output_file, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, separators=(",", ":")) + "\n")

    return total_records, fixed_records


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_provenance_hashes.py <input_file> [output_file]")
        print(
            "If output_file is not specified, the input file will be updated in-place."
        )
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        total, fixed = fix_provenance_hashes(input_file, output_file)
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
