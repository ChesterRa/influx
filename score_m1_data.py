#!/usr/bin/env python3
"""
Score M1 real data records
"""

import json
import hashlib
from datetime import datetime, timezone


def calculate_score(record):
    """Calculate quality score based on followers and engagement"""
    followers = record.get("followers_count", 0)
    verified = record.get("verified") == "blue"

    # Base score from followers (logarithmic scale)
    if followers >= 1000000:
        base_score = 100
    elif followers >= 500000:
        base_score = 90
    elif followers >= 100000:
        base_score = 80
    elif followers >= 50000:
        base_score = 70
    else:
        base_score = 50

    # Bonus for verified
    if verified:
        base_score += 10

    return min(base_score, 100)


def main():
    input_file = "data/tmp_m1_real_data.jsonl"
    output_file = "data/tmp_m1_real_data_scored.jsonl"

    records = []
    with open(input_file, "r") as f:
        for line in f:
            if line.strip():
                record = json.loads(line)

                # Calculate scores
                quality_score = calculate_score(record)

                # Update meta
                if "meta" not in record:
                    record["meta"] = {}

                record["meta"]["quality_score"] = quality_score
                record["meta"]["score"] = quality_score / 100.0  # Normalize to 0-1

                # Update provenance hash
                record_str = json.dumps(record, sort_keys=True)
                record["meta"]["provenance_hash"] = hashlib.sha256(
                    record_str.encode()
                ).hexdigest()

                records.append(record)

    # Write scored records
    with open(output_file, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    print(f"Scored {len(records)} records")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
