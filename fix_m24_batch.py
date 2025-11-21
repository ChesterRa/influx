#!/usr/bin/env python3
"""
Fix missing entry_threshold_passed and quality_score fields for M24 batch
"""

import json
import sys
import math
import hashlib
from pathlib import Path


def should_pass_threshold(record):
    """Apply entry threshold logic"""
    followers = record.get("followers_count", 0)
    verified = record.get("verified") in ["blue", "org", "legacy"]

    # Entry threshold: (verified=true AND followers>=30k) OR followers>=50k
    if verified and followers >= 30000:
        return True
    elif followers >= 50000:
        return True
    else:
        return False


def calculate_quality_score(record):
    """Calculate quality score based on proxy formula for now"""
    followers = record.get("followers_count", 0)
    verified = record.get("verified") in ["blue", "org", "legacy"]

    # Proxy formula: 20*log10(followers/1000) + verified_boost
    if followers < 1000:
        base_score = 0
    else:
        base_score = 20 * (math.log10(followers / 1000))

    verified_boost = 10 if verified else 0
    score = min(100, max(0, base_score + verified_boost))

    return round(score, 1)


def update_provenance_hash(record):
    """Recalculate provenance hash with updated fields"""
    # Use id, followers, last_active_at, and key metrics
    hash_data = f"{record['id']}|{record['followers_count']}"
    if "activity_metrics" in record.get("meta", {}):
        last_captured = record["meta"]["activity_metrics"].get("last_captured_at", "")
        hash_data += f"|{last_captured}"

    return hashlib.sha256(hash_data.encode()).hexdigest()


def fix_record(record):
    """Fix a single record"""
    # Ensure meta exists
    if "meta" not in record:
        record["meta"] = {}

    # Move existing fields from top-level to meta if they exist there
    if "entry_threshold_passed" in record:
        record["meta"]["entry_threshold_passed"] = record.pop("entry_threshold_passed")
    if "quality_score" in record:
        record["meta"]["quality_score"] = record.pop("quality_score")

    # Add missing fields if not present
    if "entry_threshold_passed" not in record["meta"]:
        record["meta"]["entry_threshold_passed"] = should_pass_threshold(record)

    if "quality_score" not in record["meta"]:
        # Use the score from the scoring process
        record["meta"]["quality_score"] = record["meta"].get(
            "score", calculate_quality_score(record)
        )

    # Update provenance hash
    record["meta"]["provenance_hash"] = update_provenance_hash(record)

    return record


def main():
    if len(sys.argv) != 3:
        print("Usage: python fix_m24_batch.py <input_file> <output_file>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"ERROR: {input_file} not found")
        sys.exit(1)

    records = []
    fixed_count = 0

    print(f"Reading {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
                fixed_record = fix_record(record)
                records.append(fixed_record)
                fixed_count += 1

            except json.JSONDecodeError as e:
                print(f"ERROR parsing line {line_num}: {e}")
                continue

    print(f"Fixed {fixed_count} records")

    # Write fixed data
    print(f"Writing {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, separators=(",", ":")) + "\n")

    print(f"✅ Fixed {len(records)} records written to {output_file}")


if __name__ == "__main__":
    main()
