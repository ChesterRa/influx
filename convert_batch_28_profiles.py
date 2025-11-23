#!/usr/bin/env python3
"""
Convert batch 28 profiles to Influx schema format
"""

import json
import hashlib
from datetime import datetime


def calculate_quality_score(profile):
    """Calculate quality score based on followers and verification"""
    followers = profile.get("followers", 0)
    verified = profile.get("verified", False)

    # Base score from followers (logarithmic scale)
    if followers >= 1000000:
        base_score = 95
    elif followers >= 500000:
        base_score = 90
    elif followers >= 100000:
        base_score = 85
    elif followers >= 50000:
        base_score = 80
    else:
        base_score = 75

    # Bonus for verification
    if verified:
        base_score += 5

    return min(base_score, 99)  # Cap at 99


def convert_to_influx_schema(profile):
    """Convert Twitter profile to Influx schema"""
    followers = profile.get("followers", 0)
    verified = profile.get("verified", False)

    # Determine entry threshold
    entry_threshold_passed = (verified and followers >= 30000) or followers >= 50000

    # Calculate quality score
    quality_score = calculate_quality_score(profile)

    # Create Influx record
    influx_record = {
        "handle": profile["username"],
        "name": profile["name"],
        "bio": profile.get("description", ""),
        "followers_count": followers,
        "following_count": 0,  # Not provided in this batch
        "verified": verified,
        "profile_image_url": "",  # Not provided in this batch
        "location": "",  # Not provided in this batch
        "website": "",  # Not provided in this batch
        "created_at": profile.get("created_at", ""),
        "is_org": False,  # Assume individual accounts
        "is_official": False,  # Assume not official accounts
        "entry_threshold_passed": entry_threshold_passed,
        "quality_score": quality_score,
        "provenance": "twitter_user_lookup_batch_28",
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "meta": {
            "source": "twitter_api_v2",
            "verified_type": profile.get("verified_type", "none"),
            "original_id": profile.get("id", ""),
            "batch_id": "batch_28_missing_placeholders",
        },
    }

    return influx_record


def main():
    # Load raw profiles
    with open("tmp_batch_28_raw.json", "r") as f:
        raw_profiles = json.load(f)

    # Convert to Influx schema
    influx_profiles = []
    for profile in raw_profiles:
        converted = convert_to_influx_schema(profile)
        influx_profiles.append(converted)

    # Save converted profiles
    with open("tmp_batch_28_converted.jsonl", "w") as f:
        for profile in influx_profiles:
            f.write(json.dumps(profile) + "\n")

    print(f"Converted {len(influx_profiles)} profiles to Influx schema")

    # Show summary
    total_followers = sum(p["followers_count"] for p in influx_profiles)
    verified_count = sum(1 for p in influx_profiles if p["verified"])
    avg_quality = sum(p["quality_score"] for p in influx_profiles) / len(
        influx_profiles
    )

    print(f"Summary:")
    print(f"- Total profiles: {len(influx_profiles)}")
    print(f"- Total followers: {total_followers:,}")
    print(f"- Verified accounts: {verified_count}")
    print(f"- Average quality score: {avg_quality:.1f}")
    print(f"- Saved to: tmp_batch_28_converted.jsonl")


if __name__ == "__main__":
    main()
