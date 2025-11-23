#!/usr/bin/env python3
"""
Remove below-threshold profiles from batch 29
"""

import json
import hashlib
from datetime import datetime, timezone


def remove_below_threshold(input_file, output_file):
    """Remove profiles that don't meet entry threshold"""

    # Read existing data
    records = []
    with open(input_file, "r") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    # Filter out below-threshold profiles
    fixed_records = []
    removed_count = 0

    for record in records:
        followers = record.get("followers_count", 0)
        verified = record.get("verified", False)
        entry_threshold_passed = (verified and followers >= 30000) or followers >= 50000

        # Keep record if it meets threshold OR is not from batch 29
        if (
            entry_threshold_passed
            or record.get("provenance") != "twitter_user_lookup_batch_29"
        ):
            fixed_records.append(record)
        else:
            removed_count += 1
            print(
                f"Removing {record.get('handle', 'unknown')} - {followers:,} followers, verified: {verified}"
            )

    # Write fixed data
    with open(output_file, "w") as f:
        for record in fixed_records:
            f.write(json.dumps(record) + "\n")

    print(f"Removed {removed_count} below-threshold profiles")
    print(f"Kept {len(fixed_records)} records")
    print(f"Saved to: {output_file}")

    return fixed_records


def update_manifest(count):
    """Update manifest with new count and SHA256"""

    # Calculate SHA256
    sha256_hash = hashlib.sha256()
    with open("data/latest/latest.jsonl", "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)

    manifest = {
        "count": count,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "schema_version": "1.0.0",
        "sha256": sha256_hash.hexdigest(),
        "description": "Influx dataset - high-signal X influencer index",
        "last_batch": "batch_29_missing_placeholders_filtered",
        "quality_gates": "strict_compliance",
    }

    with open("data/latest/manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(
        f"Updated manifest: {count} records, SHA256: {sha256_hash.hexdigest()[:16]}..."
    )


def main():
    # Remove below-threshold profiles
    remove_below_threshold("data/latest/latest.jsonl", "data/latest/latest_fixed.jsonl")

    # Replace original
    import shutil

    shutil.move("data/latest/latest_fixed.jsonl", "data/latest/latest.jsonl")

    # Update manifest
    with open("data/latest/latest.jsonl", "r") as f:
        count = sum(1 for line in f if line.strip())

    update_manifest(count)
    print("✅ Removed below-threshold profiles and updated manifest")


if __name__ == "__main__":
    main()
