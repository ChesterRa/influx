#!/usr/bin/env python3
"""
Diagnostic script to check batch file contents
"""

import json
import sys
from pathlib import Path


def analyze_batch_files():
    """Analyze batch files to understand their contents."""

    batch_files = [
        "/home/dodd/dev/influx/data/batches/africa_processed_20251123_161026.jsonl",
        "/home/dodd/dev/influx/data/batches/asia_pacific_processed_20251123_161055.jsonl",
        "/home/dodd/dev/influx/data/batches/europe_processed_20251123_161118.jsonl",
        "/home/dodd/dev/influx/canada_batch.jsonl",
        "/home/dodd/dev/influx/canada_fixed_batch.jsonl",
        "/home/dodd/dev/influx/canada_new_batch.jsonl",
        "/home/dodd/dev/influx/africa_batch.jsonl",
        "/home/dodd/dev/influx/sea_batch.jsonl",
    ]

    total_records = 0
    verified_count = 0
    follower_ranges = {"<10k": 0, "10k-30k": 0, "30k-50k": 0, "50k-100k": 0, ">100k": 0}
    sample_records = []

    for batch_file in batch_files:
        if not Path(batch_file).exists():
            print(f"File not found: {batch_file}")
            continue

        print(f"\nAnalyzing: {batch_file}")
        file_records = 0
        file_verified = 0

        try:
            with open(batch_file, "r") as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)
                        file_records += 1
                        total_records += 1

                        # Check verification
                        verified = data.get("verified", "none")
                        if verified == "blue":
                            verified_count += 1
                            file_verified += 1

                        # Check follower count
                        followers = data.get("followers_count", 0)
                        if followers < 10000:
                            follower_ranges["<10k"] += 1
                        elif followers < 30000:
                            follower_ranges["10k-30k"] += 1
                        elif followers < 50000:
                            follower_ranges["30k-50k"] += 1
                        elif followers < 100000:
                            follower_ranges["50k-100k"] += 1
                        else:
                            follower_ranges[">100k"] += 1

                        # Collect sample records
                        if (
                            len(sample_records) < 10
                            and verified == "blue"
                            and 30000 <= followers <= 49000
                        ):
                            sample_records.append(
                                {
                                    "handle": data.get("handle"),
                                    "name": data.get("name"),
                                    "followers_count": followers,
                                    "verified": verified,
                                    "description": data.get("description", ""),
                                    "source_file": Path(batch_file).name,
                                }
                            )

                    except json.JSONDecodeError as e:
                        print(f"  JSON error at line {line_num}: {e}")
                        continue

        except Exception as e:
            print(f"  Error reading file: {e}")
            continue

        print(f"  Records: {file_records}, Verified: {file_verified}")

    print(f"\n=== SUMMARY ===")
    print(f"Total records analyzed: {total_records}")
    print(f"Total verified accounts: {verified_count}")
    print(f"Follower count distribution:")
    for range_name, count in follower_ranges.items():
        print(f"  {range_name}: {count}")

    print(f"\nSample verified accounts (30K-50K followers):")
    for i, record in enumerate(sample_records, 1):
        print(f"{i}. @{record['handle']} ({record['name']})")
        print(
            f"   Followers: {record['followers_count']:,} | Verified: {record['verified']}"
        )
        print(f"   Description: {record['description'][:80]}...")
        print(f"   Source: {record['source_file']}")
        print()


if __name__ == "__main__":
    analyze_batch_files()
