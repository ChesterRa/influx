#!/usr/bin/env python3
import json
import hashlib
import sys


def generate_proper_hash(user_id, username, timestamp):
    """Generate proper SHA256 hash"""
    content = f"{user_id}_{username}_{timestamp}"
    return hashlib.sha256(content.encode()).hexdigest()


def fix_m23_records():
    """Fix validation errors in M23 records"""
    input_file = "data/latest/latest.jsonl"
    output_file = "data/latest/latest_fixed.jsonl"

    fixed_records = []

    with open(input_file, "r") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue

            record = json.loads(line)

            # Fix M23 records (lines 1093-1101)
            if line_num >= 1093 and line_num <= 1101:
                # Fix provenance hash
                timestamp = record["meta"]["last_refresh_at"]
                proper_hash = generate_proper_hash(
                    record["id"], record["handle"], timestamp
                )
                record["meta"]["provenance_hash"] = proper_hash

                # Fix verification status
                if record["verified"] == "business":
                    record["verified"] = "org"

                # Fix is_org for NVIDIA
                if record["handle"] == "nvidia":
                    record["is_org"] = True

            fixed_records.append(record)

    # Write fixed records
    with open(output_file, "w") as f:
        for record in fixed_records:
            f.write(json.dumps(record) + "\n")

    print(f"✅ Fixed {len(fixed_records)} records")
    print(f"📁 Saved to: {output_file}")

    # Count M23 records
    m23_count = sum(1 for i in range(1092, 1101) if i < len(fixed_records))
    print(f"📊 M23 records processed: {m23_count}")


if __name__ == "__main__":
    fix_m23_records()
