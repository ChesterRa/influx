#!/usr/bin/env python3
"""
Data protection script to prevent corruption
Monitors dataset quality and creates immutable snapshots
"""

import json
import hashlib
import os
import time
from datetime import datetime


def create_immutable_snapshot():
    """Create immutable snapshot of clean dataset"""

    snapshot_file = (
        f"data/latest/latest_immutable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    )

    # Read current dataset
    with open("data/latest/latest.jsonl", "r") as f:
        data = f.read()

    # Verify quality before snapshot
    lines = data.strip().split("\n")
    real_accounts = 0

    for line in lines:
        if line.strip():
            record = json.loads(line)
            followers = record.get("public_metrics", {}).get("followers_count", 0)
            tweets = record.get("public_metrics", {}).get("tweet_count", 0)

            if followers > 0 or tweets > 0:
                real_accounts += 1

    if real_accounts == 0:
        print("❌ CANNOT CREATE SNAPSHOT: No real accounts found!")
        return False

    # Create snapshot with read-only permissions
    with open(snapshot_file, "w") as f:
        f.write(data)

    # Make file read-only (owner read-only)
    os.chmod(snapshot_file, 0o444)

    print(f"✅ Created immutable snapshot: {snapshot_file}")
    print(f"   Real accounts: {real_accounts}")
    print(f"   Total records: {len(lines)}")

    return True


def verify_dataset_integrity():
    """Verify current dataset integrity"""

    try:
        with open("data/latest/latest.jsonl", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("❌ Dataset file not found!")
        return False

    total_records = len([l for l in lines if l.strip()])
    real_accounts = 0

    for line in lines:
        if line.strip():
            try:
                record = json.loads(line)
                followers = record.get("public_metrics", {}).get("followers_count", 0)
                tweets = record.get("public_metrics", {}).get("tweet_count", 0)

                if followers > 0 or tweets > 0:
                    real_accounts += 1
            except json.JSONDecodeError:
                print("❌ Invalid JSON found in dataset!")
                return False

    print(f"Dataset integrity check:")
    print(f"  Total records: {total_records}")
    print(f"  Real accounts: {real_accounts}")
    print(f"  Zero-metric accounts: {total_records - real_accounts}")

    if real_accounts == 0:
        print("❌ DATASET CORRUPTED: All accounts have zero metrics!")
        return False

    return True


def main():
    print("=== DATA PROTECTION CHECK ===")

    # Check current integrity
    if not verify_dataset_integrity():
        print("\n🚨 DATASET CORRUPTION DETECTED!")
        print("Creating protection snapshot...")

        # Try to find last good snapshot
        snapshot_files = [
            f for f in os.listdir("data/latest/") if f.startswith("latest_immutable_")
        ]

        if snapshot_files:
            latest_snapshot = sorted(snapshot_files)[-1]
            print(f"Restoring from latest snapshot: {latest_snapshot}")

            # Copy from snapshot (need to temporarily make it writable)
            os.chmod(f"data/latest/{latest_snapshot}", 0o644)
            with open(f"data/latest/{latest_snapshot}", "r") as src:
                with open("data/latest/latest.jsonl", "w") as dst:
                    dst.write(src.read())
            os.chmod(f"data/latest/{latest_snapshot}", 0o444)

            print("✅ Dataset restored from snapshot")
        else:
            print("❌ No clean snapshots found!")

        return False

    # Create new snapshot if dataset is clean
    print("\n✅ Dataset is clean - creating protection snapshot...")
    return create_immutable_snapshot()


if __name__ == "__main__":
    main()
