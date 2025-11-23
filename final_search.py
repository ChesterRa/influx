#!/usr/bin/env python3
"""
Final comprehensive search for verified candidates with flexible field handling
"""

import json
import sys
from pathlib import Path


def load_main_dataset_handles():
    """Load all handles from main dataset."""
    handles = set()
    main_file = Path("/home/dodd/dev/influx/data/latest/latest.jsonl")

    with open(main_file, "r") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                handle = (
                    data.get("handle") or data.get("user_id") or data.get("username")
                )
                if handle:
                    handles.add(handle.lower())

    return handles


def final_search():
    """Final comprehensive search."""
    main_handles = load_main_dataset_handles()

    # All possible batch files
    batch_files = []

    # Add all jsonl files in various directories
    for directory in [
        "/home/dodd/dev/influx/data/batches",
        "/home/dodd/dev/influx/data/processed_batches",
        "/home/dodd/dev/influx",
    ]:
        batch_dir = Path(directory)
        if batch_dir.exists():
            batch_files.extend([str(f) for f in batch_dir.glob("*.jsonl")])

    # Remove duplicates
    batch_files = list(set(batch_files))

    print(f"Searching {len(batch_files)} batch files...")

    candidates = []
    all_verified = []

    for batch_file in batch_files:
        if not Path(batch_file).exists():
            continue

        try:
            with open(batch_file, "r") as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)

                        # Get handle (flexible field names)
                        handle = (
                            data.get("handle")
                            or data.get("user_id")
                            or data.get("username")
                        )
                        if not handle:
                            continue

                        # Skip if already in main dataset
                        if handle.lower() in main_handles:
                            continue

                        # Check verification
                        verified = data.get("verified", "none")
                        if verified != "blue":
                            continue

                        # Check follower count
                        followers = data.get("followers_count", 0)

                        # Collect all verified accounts for analysis
                        all_verified.append(
                            {
                                "handle": handle,
                                "name": data.get("name", "Unknown"),
                                "followers_count": followers,
                                "verified": verified,
                                "source_file": Path(batch_file).name,
                            }
                        )

                        # Check if in our target range (30K-49K)
                        if not (30000 <= followers <= 49000):
                            continue

                        # Check quality criteria
                        if data.get("is_org", False) or data.get("is_official", False):
                            continue

                        # Check for risk flags
                        risk_flags = data.get("risk_flags", [])
                        if risk_flags:
                            continue

                        # Add to candidates
                        candidates.append(
                            {
                                "handle": handle,
                                "name": data.get("name", "Unknown"),
                                "followers_count": followers,
                                "verified": verified,
                                "description": data.get("description", ""),
                                "location": data.get("location", ""),
                                "source_file": Path(batch_file).name,
                                "line_num": line_num,
                            }
                        )

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            continue

    # Sort candidates by follower count
    candidates.sort(key=lambda x: x["followers_count"], reverse=True)
    all_verified.sort(key=lambda x: x["followers_count"], reverse=True)

    print(f"\n=== SEARCH RESULTS ===")
    print(f"Total verified accounts found (not in main dataset): {len(all_verified)}")
    print(f"Qualified candidates (30K-49K): {len(candidates)}")

    if candidates:
        print(f"\n=== QUALIFIED CANDIDATES (30K-49K) ===")
        for i, candidate in enumerate(candidates, 1):
            print(f"{i}. @{candidate['handle']} ({candidate['name']})")
            print(f"   Followers: {candidate['followers_count']:,}")
            print(f"   Location: {candidate['location']}")
            print(f"   Description: {candidate['description'][:100]}...")
            print(f"   Source: {candidate['source_file']}")
            print()
    else:
        print("\n=== NO CANDIDATES IN 30K-49K RANGE ===")

        # Show closest candidates below 30K
        below_30k = [v for v in all_verified if v["followers_count"] < 30000]
        below_30k.sort(key=lambda x: x["followers_count"], reverse=True)

        if below_30k:
            print(f"\n=== CLOSEST CANDIDATES BELOW 30K ===")
            for i, candidate in enumerate(below_30k[:10], 1):
                print(f"{i}. @{candidate['handle']} ({candidate['name']})")
                print(f"   Followers: {candidate['followers_count']:,}")
                print(f"   Source: {candidate['source_file']}")
                print()

        # Show candidates just above 49K
        above_49k = [v for v in all_verified if 49000 < v["followers_count"] < 100000]
        above_49k.sort(key=lambda x: x["followers_count"])

        if above_49k:
            print(f"\n=== CLOSEST CANDIDATES ABOVE 49K ===")
            for i, candidate in enumerate(above_49k[:10], 1):
                print(f"{i}. @{candidate['handle']} ({candidate['name']})")
                print(f"   Followers: {candidate['followers_count']:,}")
                print(f"   Source: {candidate['source_file']}")
                print()

    print(f"Current dataset size: 272")
    print(f"Target range: 279-289")
    print(f"Needed: {max(0, 279 - 272)}-{max(0, 289 - 272)} authors")

    return candidates


if __name__ == "__main__":
    final_search()
