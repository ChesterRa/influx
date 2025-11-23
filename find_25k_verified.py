#!/usr/bin/env python3

import json
import sys


def load_dataset_handles(filename):
    """Load all handles from the main dataset"""
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


def analyze_batch_file(filename, main_dataset_handles):
    """Analyze a batch file for 25K verified threshold candidates"""
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
        print(f"Warning: {filename} not found")
    except Exception as e:
        print(f"Error processing {filename}: {e}")

    return results


def main():
    # Load main dataset handles
    print("Loading main dataset handles...")
    main_handles = load_dataset_handles(
        "/home/dodd/dev/influx/data/latest/latest.jsonl"
    )
    print(f"Loaded {len(main_handles)} handles from main dataset")

    # Batch files to analyze
    batch_files = [
        "/home/dodd/dev/influx/m09_final_new.jsonl",
        "/home/dodd/dev/influx/m10_processed.jsonl",
        "/home/dodd/dev/influx/m1_processed.jsonl",
        "/home/dodd/dev/influx/canada_new_batch.jsonl",
        "/home/dodd/dev/influx/africa_batch.jsonl",
        "/home/dodd/dev/influx/m09_25k_processed.jsonl",
        "/home/dodd/dev/influx/threshold_25k_processed.jsonl",
        "/home/dodd/dev/influx/data/batches/africa_processed_20251123_161026.jsonl",
        "/home/dodd/dev/influx/data/batches/asia_pacific_processed_20251123_161055.jsonl",
        "/home/dodd/dev/influx/data/batches/europe_processed_20251123_161118.jsonl",
        "/home/dodd/dev/influx/data/batches/m32_processed.jsonl",
        "/home/dodd/dev/influx/data/batches/m30_processed_final.jsonl",
    ]

    total_candidates = []

    print("\nAnalyzing batch files for 25K-49K verified candidates...")
    for batch_file in batch_files:
        candidates = analyze_batch_file(batch_file, main_handles)
        if candidates:
            print(f"\n{batch_file}:")
            for candidate in candidates:
                print(
                    f"  - @{candidate['handle']} ({candidate['name']}): {candidate['followers']:,} followers"
                )
                if candidate["quality_score"]:
                    print(f"    Quality Score: {candidate['quality_score']}")
            total_candidates.extend(candidates)
        else:
            print(f"{batch_file}: No candidates found")

    print(f"\n" + "=" * 60)
    print(f"SUMMARY")
    print(f"=" * 60)
    print(f"Total new 25K-49K verified candidates found: {len(total_candidates)}")

    if total_candidates:
        print(f"\nCandidates by follower count:")
        for candidate in sorted(
            total_candidates, key=lambda x: x["followers"], reverse=True
        ):
            print(
                f"  - @{candidate['handle']} ({candidate['name']}): {candidate['followers']:,} followers"
            )

        print(f"\nThese candidates could help reach the 279-289 target range.")
        print(f"Current dataset has {len(main_handles)} authors.")
        print(
            f"Adding these {len(total_candidates)} would bring it to {len(main_handles) + len(total_candidates)} authors."
        )
    else:
        print("No new 25K-49K verified candidates found in the batch files.")


if __name__ == "__main__":
    main()
