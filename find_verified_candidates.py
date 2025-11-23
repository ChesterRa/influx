#!/usr/bin/env python3
"""
Find verified authors with 30K-49K followers from batch files
who are not already in the main dataset.
"""

import json
import sys
from pathlib import Path


def load_main_dataset_handles():
    """Load all handles from main dataset to avoid duplicates."""
    handles = set()
    main_file = Path("/home/dodd/dev/influx/data/latest/latest.jsonl")

    if main_file.exists():
        with open(main_file, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    handle = data.get("handle") or data.get("user_id")
                    if handle:
                        handles.add(handle.lower())

    return handles


def find_verified_candidates(batch_files, main_handles):
    """Find verified authors with 30K-49K followers not in main dataset."""
    candidates = []

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
                    except json.JSONDecodeError:
                        continue

                    # Get handle and check if already in main dataset
                    handle = data.get("handle") or data.get("user_id")
                    if not handle or handle.lower() in main_handles:
                        continue

                    # Check verification status
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

        except Exception as e:
            print(f"Error processing {batch_file}: {e}", file=sys.stderr)
            continue

    return candidates


def main():
    # Load main dataset handles
    print("Loading main dataset handles...")
    main_handles = load_main_dataset_handles()
    print(f"Loaded {len(main_handles)} handles from main dataset")

    # List of batch files to search
    batch_files = [
        "/home/dodd/dev/influx/data/batches/africa_processed_20251123_161026.jsonl",
        "/home/dodd/dev/influx/data/batches/asia_pacific_processed_20251123_161055.jsonl",
        "/home/dodd/dev/influx/data/batches/europe_processed_20251123_161118.jsonl",
        "/home/dodd/dev/influx/data/batches/canada_processed.jsonl",
        "/home/dodd/dev/influx/data/batches/m08_ai_processed.jsonl",
        "/home/dodd/dev/influx/data/batches/m09_ai_founders_manual.jsonl",
        "/home/dodd/dev/influx/data/batches/m09_ai_founders_raw.jsonl",
        "/home/dodd/dev/influx/data/batches/m19-vc-investing.jsonl",
        "/home/dodd/dev/influx/data/batches/m24_processed_20251123_144746.jsonl",
        "/home/dodd/dev/influx/data/batches/m30_processed_final.jsonl",
        "/home/dodd/dev/influx/data/batches/m32_processed.jsonl",
        "/home/dodd/dev/influx/africa_batch.jsonl",
        "/home/dodd/dev/influx/canada_batch.jsonl",
        "/home/dodd/dev/influx/canada_fixed_batch.jsonl",
        "/home/dodd/dev/influx/canada_new_batch.jsonl",
        "/home/dodd/dev/influx/sea_batch.jsonl",
        "/home/dodd/dev/influx/m09_25k_batch.jsonl",
        "/home/dodd/dev/influx/m13_new_batch.jsonl",
        "/home/dodd/dev/influx/threshold_25k_batch.jsonl",
        "/home/dodd/dev/influx/verified_25k_batch.jsonl",
    ]

    # Find candidates
    print("Searching for verified candidates (30K-49K followers)...")
    candidates = find_verified_candidates(batch_files, main_handles)

    # Sort by follower count (descending)
    candidates.sort(key=lambda x: x["followers_count"], reverse=True)

    # Display results
    print(f"\nFound {len(candidates)} verified candidates with 30K-49K followers:")
    print("=" * 80)

    for i, candidate in enumerate(candidates[:20], 1):  # Show top 20
        print(f"{i:2d}. @{candidate['handle']} ({candidate['name']})")
        print(
            f"    Followers: {candidate['followers_count']:,} | Verified: {candidate['verified']}"
        )
        print(f"    Location: {candidate['location']}")
        print(f"    Description: {candidate['description'][:100]}...")
        print(f"    Source: {candidate['source_file']}")
        print()

    # Summary by geographic region
    regions = {}
    for candidate in candidates:
        source = candidate["source_file"]
        if "africa" in source.lower():
            region = "Africa"
        elif "asia_pacific" in source.lower() or "sea" in source.lower():
            region = "Asia-Pacific"
        elif "europe" in source.lower():
            region = "Europe"
        elif "canada" in source.lower():
            region = "Canada"
        elif "ai" in source.lower() or "m09" in source.lower():
            region = "AI/Tech"
        elif "vc" in source.lower() or "m19" in source.lower():
            region = "VC/Investing"
        else:
            region = "Other"

        regions[region] = regions.get(region, 0) + 1

    print("Regional Distribution:")
    print("=" * 30)
    for region, count in sorted(regions.items()):
        print(f"{region}: {count}")

    print(f"\nTotal candidates available: {len(candidates)}")
    print(
        f"Needed to reach 279-289 target: {max(0, 279 - 272)}-{max(0, 289 - 272)} authors"
    )

    return candidates


if __name__ == "__main__":
    candidates = main()
