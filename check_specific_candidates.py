#!/usr/bin/env python3
"""
Check specific candidates against main dataset
"""

import json
from pathlib import Path


def load_main_dataset_handles():
    """Load all handles from main dataset."""
    handles = set()
    main_file = Path("/home/dodd/dev/influx/data/latest/latest.jsonl")

    with open(main_file, "r") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                handle = data.get("handle") or data.get("user_id")
                if handle:
                    handles.add(handle.lower())

    return handles


def check_specific_candidates():
    """Check the specific candidates found."""
    main_handles = load_main_dataset_handles()

    candidates = [
        "/home/dodd/dev/influx/data/batches/asia_pacific_processed_20251123_161055.jsonl",
        "/home/dodd/dev/influx/data/batches/europe_processed_20251123_161118.jsonl",
    ]

    found_candidates = []

    for batch_file in candidates:
        with open(batch_file, "r") as f:
            for line in f:
                if not line.strip():
                    continue

                data = json.loads(line)
                handle = data.get("handle") or data.get("user_id")

                if not handle:
                    continue

                # Check if already in main dataset
                if handle.lower() in main_handles:
                    print(f"@{handle} already exists in main dataset")
                    continue

                # Check verification and follower count
                verified = data.get("verified", "none")
                followers = data.get("followers_count", 0)

                if verified == "blue" and 30000 <= followers <= 49000:
                    found_candidates.append(data)

    print(f"\nFound {len(found_candidates)} new verified candidates:")
    for i, candidate in enumerate(found_candidates, 1):
        print(f"{i}. @{candidate.get('handle')} ({candidate.get('name')})")
        print(f"   Followers: {candidate.get('followers_count'):,}")
        print(f"   Verified: {candidate.get('verified')}")
        print(f"   Description: {candidate.get('description', 'N/A')}")
        print(f"   Location: {candidate.get('location', 'N/A')}")
        print()


if __name__ == "__main__":
    check_specific_candidates()
