#!/usr/bin/env python3
"""
Comprehensive fix for all influx dataset validation errors.

This script addresses all validation issues found in the dataset:
1. Invalid provenance_hash (40-char instead of 64-char SHA-256)
2. Score as string instead of number
3. Disallowed fields in meta (activity_metrics should be in ext)
4. Missing last_refresh_at field
5. Invalid verified field values
"""

import json
import hashlib
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set


def is_valid_hash(hash_str: str) -> bool:
    """Check if hash is a valid 64-character hex string (SHA-256)"""
    return bool(re.match(r"^[A-Fa-f0-9]{64}$", hash_str))


def compute_provenance_hash(record: Dict) -> str:
    """Compute SHA-256 provenance hash from canonical record fields"""
    canonical = {
        "id": record.get("id", ""),
        "handle": record.get("handle", ""),
        "name": record.get("name", ""),
        "followers_count": record.get("followers_count", 0),
        "verified": record.get("verified", "none"),
    }
    canonical_json = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def fix_all_validation_issues(
    input_file: str, output_file: str | None = None
) -> Tuple[int, int, int, int, int, int]:
    """
    Fix all validation issues in the JSONL file.

    Returns:
        Tuple of (total_records, hash_fixes, score_fixes, meta_fixes, refresh_fixes, verified_fixes)
    """
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    actual_output_file = output_file or input_file

    # Schema constraints
    allowed_meta_fields = {
        "score",
        "rank_global",
        "last_active_at",
        "last_refresh_at",
        "sources",
        "provenance_hash",
    }
    allowed_verified = {"none", "blue", "org", "legacy"}

    total_records = 0
    hash_fixes = 0
    score_fixes = 0
    meta_fixes = 0
    refresh_fixes = 0
    verified_fixes = 0
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
                record_modified = False

                # Fix 1: Invalid provenance_hash
                current_hash = record.get("meta", {}).get("provenance_hash", "")
                if not is_valid_hash(current_hash):
                    if current_hash:  # Only print if there was an existing hash
                        print(
                            f"Line {line_num}: Fixing invalid hash for {record.get('handle', 'unknown')}"
                        )
                    new_hash = compute_provenance_hash(record)
                    if "meta" not in record:
                        record["meta"] = {}
                    record["meta"]["provenance_hash"] = new_hash
                    hash_fixes += 1
                    record_modified = True

                # Fix 2: Score as string instead of number
                score = record.get("meta", {}).get("score")
                if isinstance(score, str):
                    try:
                        new_score = float(score)
                        record["meta"]["score"] = new_score
                        score_fixes += 1
                        record_modified = True
                    except ValueError:
                        pass  # Skip if can't convert

                # Fix 3: Disallowed fields in meta
                meta = record.get("meta", {})
                disallowed_fields = set(meta.keys()) - allowed_meta_fields
                if disallowed_fields:
                    if "ext" not in record:
                        record["ext"] = {}
                    for field in disallowed_fields:
                        record["ext"][field] = meta[field]
                        del meta[field]
                    meta_fixes += 1
                    record_modified = True

                # Fix 4: Missing last_refresh_at
                if "last_refresh_at" not in meta:
                    sources = meta.get("sources", [])
                    if sources:
                        first_source = sources[0]
                        fetched_at = first_source.get("fetched_at")
                        if fetched_at:
                            meta["last_refresh_at"] = fetched_at
                            refresh_fixes += 1
                            record_modified = True

                # Fix 5: Invalid verified field values
                verified = record.get("verified")
                if verified not in allowed_verified:
                    if verified == "business":
                        record["verified"] = "org"
                    else:
                        record["verified"] = "none"
                    verified_fixes += 1
                    record_modified = True

                records.append(record)

            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}", file=sys.stderr)
                continue

    print(f"\nSummary:")
    print(f"  Total records: {total_records}")
    print(f"  Hash fixes: {hash_fixes}")
    print(f"  Score fixes: {score_fixes}")
    print(f"  Meta field fixes: {meta_fixes}")
    print(f"  Last refresh fixes: {refresh_fixes}")
    print(f"  Verified field fixes: {verified_fixes}")

    # Write fixed records
    with open(actual_output_file, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, separators=(",", ":")) + "\n")

    return (
        total_records,
        hash_fixes,
        score_fixes,
        meta_fixes,
        refresh_fixes,
        verified_fixes,
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_all_validation.py <input_file> [output_file]")
        print("If output_file is not specified, input file will be updated in-place.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        total, h, s, m, r, v = fix_all_validation_issues(input_file, output_file)
        total_fixes = h + s + m + r + v
        print(f"\n✅ Successfully applied {total_fixes} fixes to {total} records")

        if total_fixes > 0:
            updated_file = output_file or input_file
            print(f"📝 File updated: {updated_file}")
            print("\nRun validation to confirm:")
            print(f"./tools/influx-validate -s schema/bigv.schema.json {updated_file}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
