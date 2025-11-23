#!/usr/bin/env python3

import json
import sys
import os


def load_dataset_handles(filename):
    """Load all handles from main dataset"""
    handles = set()
    try:
        with open(filename, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    handle = data.get("handle") or data.get("username")
                    if handle:
                        handles.add(handle.lower())
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return set()
    return handles


def find_verified_candidates(filename, main_dataset_handles):
    """Find verified accounts in 25K-49K range"""
    results = []

    try:
        with open(filename, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)

                    # Get handle and check if already in main dataset
                    handle = data.get("handle") or data.get("username")
                    if not handle:
                        continue

                    handle_lower = handle.lower()
                    if handle_lower in main_dataset_handles:
                        continue  # Skip duplicates

                    # Check verification status
                    verified = data.get("verified", "none")
                    if verified != "blue":
                        continue  # Only want verified accounts

                    # Check follower count (25K-49K range)
                    followers = data.get("followers_count", 0)
                    if followers < 25000 or followers >= 50000:
                        continue

                    # Check quality criteria
                    is_org = data.get("is_org", False)
                    is_official = data.get("is_official", False)

                    if is_org or is_official:
                        continue  # Skip org/official accounts

                    # Check if entry threshold passed
                    entry_threshold = data.get("entry_threshold_passed", True)
                    if not entry_threshold:
                        continue

                    # Get quality score if available
                    quality_score = None
                    if "meta" in data and "quality_score" in data["meta"]:
                        quality_score = data["meta"]["quality_score"]
                    elif "quality_score" in data:
                        quality_score = data["quality_score"]

                    results.append(
                        {
                            "handle": handle,
                            "name": data.get("name", "Unknown"),
                            "followers": followers,
                            "verified": verified,
                            "quality_score": quality_score,
                            "source": filename,
                        }
                    )

    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return []

    return results


def search_all_jsonl_files(base_path, main_handles):
    """Search all JSONL files for candidates"""
    all_candidates = []

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".jsonl") and not file.startswith("latest"):
                full_path = os.path.join(root, file)
                candidates = find_verified_candidates(full_path, main_handles)
                if candidates:
                    print(f"\n{full_path}:")
                    for candidate in candidates:
                        print(
                            f"  - @{candidate['handle']} ({candidate['name']}): {candidate['followers']:,} followers"
                        )
                        if candidate["quality_score"]:
                            print(f"    Quality Score: {candidate['quality_score']}")
                    all_candidates.extend(candidates)

    return all_candidates


def main():
    # Load main dataset handles
    print("Loading main dataset handles...")
    main_handles = load_dataset_handles(
        "/home/dodd/dev/influx/data/latest/latest.jsonl"
    )
    print(f"Loaded {len(main_handles)} handles from main dataset")

    # Search all JSONL files
    print("\nSearching all JSONL files for 25K-49K verified candidates...")
    all_candidates = search_all_jsonl_files("/home/dodd/dev/influx", main_handles)

    print(f"\n" + "=" * 60)
    print(f"SUMMARY")
    print(f"=" * 60)
    print(f"Total new 25K-49K verified candidates found: {len(all_candidates)}")

    if all_candidates:
        print(f"\nCandidates by follower count:")
        for candidate in sorted(
            all_candidates, key=lambda x: x["followers"], reverse=True
        ):
            print(
                f"  - @{candidate['handle']} ({candidate['name']}): {candidate['followers']:,} followers"
            )

        print(f"\nThese candidates could help reach 279-289 target range.")
        print(f"Current dataset has {len(main_handles)} authors.")
        print(
            f"Adding these {len(all_candidates)} would bring it to {len(main_handles) + len(all_candidates)} authors."
        )
    else:
        print("No new 25K-49K verified candidates found in any JSONL files.")


if __name__ == "__main__":
    main()
