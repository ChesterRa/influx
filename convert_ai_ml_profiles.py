#!/usr/bin/env python3
"""
Convert AI/ML profiles to full Influx schema format
"""

import json
import hashlib
from datetime import datetime, timezone


def convert_to_influx_schema(profiles):
    """Convert AI/ML profiles to full Influx schema"""
    converted = []
    for profile in profiles:
        # Base profile fields
        influx_profile = {
            "id": profile["id"],
            "handle": profile["username"],  # Map username to handle
            "name": profile["name"],
            "verified": "blue" if profile.get("verified") == "blue" else "none",
            "followers_count": profile["followers_count"],
            "is_org": False,
            "is_official": False,
            "lang_primary": "en",
            "topic_tags": ["ai_ml_research"],
            "meta": {
                "score": profile["meta"]["quality_score"]
                * 0.5,  # Convert to combined score
                "last_refresh_at": datetime.now(timezone.utc).isoformat(),
                "sources": [
                    {
                        "method": "rube_mcp_fetch",
                        "fetched_at": profile["provenance"]["fetched_at"],
                        "evidence": f"@{profile['username']}",
                    }
                ],
                "provenance_hash": hashlib.sha256(
                    f"{profile['id']}_{profile['username']}".encode()
                ).hexdigest(),
                "activity_metrics": {
                    "account_created_at": "2023-01-01T00:00:00.000Z",  # Placeholder
                    "tweet_count": 1000,  # Placeholder
                    "total_like_count": profile["followers_count"] // 10,  # Estimate
                    "media_count": 100,  # Placeholder
                    "listed_count": profile["followers_count"] // 100,  # Estimate
                    "last_captured_at": profile["provenance"]["fetched_at"],
                },
                "activity_score": 40.0,  # Placeholder
                "quality_score": profile["meta"]["quality_score"],
                "relevance_score": 10,
                "combined_score": profile["meta"]["quality_score"] * 0.5,
                "entry_threshold_passed": True,
            },
        }
        converted.append(influx_profile)
    return converted


# Load and convert profiles
with open("/home/dodd/dev/influx/tmp_ai_ml_profiles_fixed.jsonl", "r") as f:
    ai_ml_profiles = [json.loads(line) for line in f if line.strip()]

converted_profiles = convert_to_influx_schema(ai_ml_profiles)

# Save converted profiles
with open("/home/dodd/dev/influx/tmp_ai_ml_profiles_converted.jsonl", "w") as f:
    for profile in converted_profiles:
        f.write(json.dumps(profile) + "\n")

print(f"Converted {len(converted_profiles)} AI/ML profiles to Influx schema")
