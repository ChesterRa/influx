#!/usr/bin/env python3
"""
Remove accounts with zero metrics from the dataset.
These are fake data entries that need to be eliminated.
"""

import json
import shutil
from datetime import datetime


def remove_zero_metric_accounts():
    """Remove accounts with zero public_metrics"""

    # Create backup
    backup_file = f"data/latest/latest.jsonl.backup_zero_removal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2("data/latest/latest.jsonl", backup_file)
    print(f"Created backup: {backup_file}")

    # Load and filter data
    clean_accounts = []
    removed_accounts = []

    with open("data/latest/latest.jsonl", "r") as f:
        for line in f:
            data = json.loads(line)
            followers = data.get("public_metrics", {}).get("followers_count", 0)
            tweets = data.get("public_metrics", {}).get("tweet_count", 0)

            if followers > 0 or tweets > 0:
                clean_accounts.append(data)
            else:
                removed_accounts.append(data.get("handle", "UNKNOWN"))

    # Save clean data
    with open("data/latest/latest.jsonl", "w") as f:
        for account in clean_accounts:
            f.write(json.dumps(account) + "\n")

    print(f"\n✓ Removed {len(removed_accounts)} accounts with zero metrics")
    print(f"✓ Kept {len(clean_accounts)} accounts with real metrics")

    # Show removed accounts
    if len(removed_accounts) <= 20:
        print("\nRemoved accounts:")
        for handle in removed_accounts:
            print(f"  @{handle}")
    else:
        print(f"\nFirst 20 removed accounts:")
        for handle in removed_accounts[:20]:
            print(f"  @{handle}")
        print(f"  ... and {len(removed_accounts) - 20} more")

    # Show kept accounts
    print("\nSample kept accounts:")
    for i, account in enumerate(clean_accounts[:10]):
        handle = account.get("handle", "UNKNOWN")
        followers = account.get("public_metrics", {}).get("followers_count", 0)
        tweets = account.get("public_metrics", {}).get("tweet_count", 0)
        print(f"  {i + 1}. @{handle}: {followers:,} followers, {tweets:,} tweets")

    return len(clean_accounts), len(removed_accounts)


if __name__ == "__main__":
    kept, removed = remove_zero_metric_accounts()
    print(f"\n✓ Dataset cleanup complete: {kept} kept, {removed} removed")
