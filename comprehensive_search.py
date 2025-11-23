#!/usr/bin/env python3
"""
Comprehensive search for verified candidates across all batch files
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
                handle = data.get("handle") or data.get("user_id")
                if handle:
                    handles.add(handle.lower())

    return handles


def comprehensive_search():
    """Search all batch files comprehensively."""
    main_handles = load_main_dataset_handles()

    # All possible batch files
    batch_files = []

    # Add all jsonl files in data/batches/
    batch_dir = Path("/home/dodd/dev/influx/data/batches")
    if batch_dir.exists():
        batch_files.extend([str(f) for f in batch_dir.glob("*.jsonl")])

    # Add all jsonl files in data/processed_batches/
    processed_dir = Path("/home/dodd/dev/influx/data/processed_batches")
    if processed_dir.exists():
        batch_files.extend([str(f) for f in processed_dir.glob("*.jsonl")])

    # Add batch files in root directory
    root_dir = Path("/home/dodd/dev/influx")
    batch_files.extend([str(f) for f in root_dir.glob("*batch.jsonl")])

    # Remove duplicates
    batch_files = list(set(batch_files))

    print(f"Searching {len(batch_files)} batch files...")

    candidates = []
    total_records = 0
    verified_30k_50k = 0

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
                        total_records += 1

                        # Get handle
                        handle = data.get("handle") or data.get("user_id")
                        if not handle:
                            continue

                        # Skip if already in main dataset
                        if handle.lower() in main_handles:
                            continue

                        # Check verification
                        verified = data.get("verified", "none")
                        if verified != "blue":
                            continue

                        # Check follower count (30K-49K range)
                        followers = data.get("followers_count", 0)
                        if not (30000 <= followers <= 49000):
                            continue

                        # Check quality criteria
                        if data.get("is_org", False) or data.get("is_official", False):
                            continue

                        # Check for risk flags
                        risk_flags = data.get("risk_flags", [])
                        if risk_flags:
                            continue

                        verified_30k_50k += 1

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
            print(f"Error reading {batch_file}: {e}", file=sys.stderr)
            continue

    # Sort by follower count (descending)
    candidates.sort(key=lambda x: x["followers_count"], reverse=True)

    print(f"\n=== SEARCH RESULTS ===")
    print(f"Total records analyzed: {total_records}")
    print(f"Verified accounts (30K-50K) not in main dataset: {verified_30k_50k}")
    print(f"Qualified candidates: {len(candidates)}")

    if candidates:
        print(f"\n=== QUALIFIED CANDIDATES ===")
        for i, candidate in enumerate(candidates, 1):
            print(f"{i}. @{candidate['handle']} ({candidate['name']})")
            print(f"   Followers: {candidate['followers_count']:,}")
            print(f"   Verified: {candidate['verified']}")
            print(f"   Location: {candidate['location']}")
            print(f"   Description: {candidate['description'][:100]}...")
            print(f"   Source: {candidate['source_file']}")
            print()
    else:
        print("\nNo new verified candidates found in 30K-49K range.")

        # Let's also check what verified accounts exist in 20K-30K range
        print("\n=== CHECKING 20K-30K RANGE FOR POTENTIAL CANDIDATES ===")
        search_lower_range(main_handles, batch_files)


def search_lower_range(main_handles, batch_files):
    """Search for verified accounts in 20K-30K range."""
    lower_candidates = []

    for batch_file in batch_files:
        if not Path(batch_file).exists():
            continue

        try:
            with open(batch_file, "r") as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)

                        handle = data.get("handle") or data.get("user_id")
                        if not handle or handle.lower() in main_handles:
                            continue

                        verified = data.get("verified", "none")
                        if verified != "blue":
                            continue

                        followers = data.get("followers_count", 0)
                        if not (20000 <= followers <= 29000):
                            continue

                        if data.get("is_org", False) or data.get("is_official", False):
                            continue

                        risk_flags = data.get("risk_flags", [])
                        if risk_flags:
                            continue

                        lower_candidates.append(
                            {
                                "handle": handle,
                                "name": data.get("name", "Unknown"),
                                "followers_count": followers,
                                "description": data.get("description", ""),
                                "source_file": Path(batch_file).name,
                            }
                        )

                    except json.JSONDecodeError:
                        continue

        except Exception:
            continue

    if lower_candidates:
        lower_candidates.sort(key=lambda x: x["followers_count"], reverse=True)
        print(f"Found {len(lower_candidates)} verified candidates in 20K-30K range:")
        for i, candidate in enumerate(lower_candidates[:10], 1):
            print(f"{i}. @{candidate['handle']} ({candidate['name']})")
            print(f"   Followers: {candidate['followers_count']:,}")
            print(f"   Description: {candidate['description'][:80]}...")
            print()


if __name__ == "__main__":
    comprehensive_search()
