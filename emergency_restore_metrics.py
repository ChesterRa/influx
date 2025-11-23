#!/usr/bin/env python3
"""
Emergency script to restore real public_metrics from raw harvested data using ID matching.
This fixes the catastrophic data corruption where all metrics were zeroed.
"""

import json
import os
import shutil
from datetime import datetime


def restore_real_metrics_by_id():
    """Restore real metrics from raw data files using ID matching"""

    # Create emergency backup
    backup_file = f"data/latest/latest.jsonl.emergency_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2("data/latest/latest.jsonl", backup_file)
    print(f"Created emergency backup: {backup_file}")

    # Load current corrupted data
    current_data = []
    with open("data/latest/latest.jsonl", "r") as f:
        for line in f:
            current_data.append(json.loads(line))

    print(f"Loaded {len(current_data)} accounts from current dataset")

    # Create ID to account mapping from current data
    id_to_current_account = {}
    for account in current_data:
        account_id = account.get("id")
        if account_id:
            id_to_current_account[account_id] = account

    print(f"Mapped {len(id_to_current_account)} account IDs")

    # Load real metrics from raw files
    raw_metrics = {}

    raw_files = [
        "data/uncompressed/users_fetched_m19.jsonl",
        "data/uncompressed/users_fetched_m24.jsonl",
        "data/uncompressed/users_fetched_m18.jsonl",
        "data/uncompressed/users_fetched_m26_m27.jsonl",
    ]

    for raw_file in raw_files:
        if not os.path.exists(raw_file):
            continue

        print(f"Loading metrics from {raw_file}...")
        with open(raw_file, "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    account_id = data.get("id")
                    if account_id and "public_metrics" in data:
                        raw_metrics[account_id] = {
                            "public_metrics": data["public_metrics"],
                            "username": data.get("username"),
                            "name": data.get("name"),
                            "description": data.get("description"),
                            "verified_type": data.get("verified_type"),
                            "created_at": data.get("created_at"),
                        }
                except json.JSONDecodeError:
                    continue

    print(f"Loaded real metrics for {len(raw_metrics)} account IDs")

    # Restore metrics to current data
    restored_count = 0
    restored_accounts = []

    for account_id, current_account in id_to_current_account.items():
        if account_id in raw_metrics:
            # Restore real metrics and additional fields
            raw_data = raw_metrics[account_id]
            current_account["public_metrics"] = raw_data["public_metrics"]

            # Also restore missing fields if they're missing or empty
            if not current_account.get("username") and raw_data.get("username"):
                current_account["username"] = raw_data["username"]
            if not current_account.get("name") and raw_data.get("name"):
                current_account["name"] = raw_data["name"]
            if not current_account.get("description") and raw_data.get("description"):
                current_account["description"] = raw_data["description"]
            if not current_account.get("verified_type") and raw_data.get(
                "verified_type"
            ):
                current_account["verified_type"] = raw_data["verified_type"]
            if not current_account.get("created_at") and raw_data.get("created_at"):
                current_account["created_at"] = raw_data["created_at"]

            restored_count += 1
            handle = current_account.get("handle", "UNKNOWN")
            followers = current_account["public_metrics"].get("followers_count", 0)
            tweets = current_account["public_metrics"].get("tweet_count", 0)
            restored_accounts.append(
                f"@{handle}: {followers:,} followers, {tweets:,} tweets"
            )

    # Save restored data
    output_file = "data/latest/latest_restored.jsonl"
    with open(output_file, "w") as f:
        for account in current_data:
            f.write(json.dumps(account) + "\n")

    print(f"\nRestored real metrics for {restored_count} accounts")
    print(f"Saved to: {output_file}")

    # Show sample of restored accounts
    print("\nSample of restored accounts:")
    for i, account_desc in enumerate(restored_accounts[:10]):
        print(f"  {i + 1}. {account_desc}")

    # Replace the original file if restoration was successful
    if restored_count > 0:
        shutil.copy2(output_file, "data/latest/latest.jsonl")
        print(f"\n✓ Replaced original file with restored data")
    else:
        print(f"\n⚠ No accounts were restored. Keeping original file.")

    return restored_count, output_file


if __name__ == "__main__":
    restored_count, output_file = restore_real_metrics_by_id()
    print(f"\n✓ Emergency restoration complete: {restored_count} accounts restored")
