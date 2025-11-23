#!/usr/bin/env python3
"""
Direct integration of real RUBE MCP data into influx dataset
Bypasses influx-harvest placeholder generation
"""

import json
import hashlib
from datetime import datetime, timezone


def transform_rube_data_to_schema(user_data):
    """Transform RUBE MCP response to influx schema format"""

    # Handle both direct user data and wrapped data
    if isinstance(user_data, dict) and "data" in user_data:
        user = user_data["data"]
    else:
        user = user_data

    now = datetime.now(timezone.utc).isoformat()

    # Extract metrics
    public_metrics = user.get("public_metrics", {})
    followers_count = public_metrics.get("followers_count", 0)
    verified_type = user.get("verified_type", "none")

    # Map verified type
    if verified_type == "blue":
        verified = "blue"
    elif verified_type in ["business", "government"]:
        verified = "org"
    else:
        verified = verified_type

    # Calculate quality score (M0 proxy)
    import math

    base_score = 20 * math.log10(max(followers_count, 1) / 1000)
    verified_boost_map = {"blue": 10, "legacy": 5, "org": 0, "none": 0}
    verified_boost = verified_boost_map.get(verified, 0)
    quality_score = min(100, max(0, base_score + verified_boost))

    # Activity metrics
    activity_metrics = {}
    if "created_at" in user:
        activity_metrics["account_created_at"] = user["created_at"]

    # Add all available public metrics
    metric_mapping = {
        "tweet_count": "tweet_count",
        "like_count": "total_like_count",
        "media_count": "media_count",
        "listed_count": "listed_count",
        "following_count": "following_count",
    }

    for api_field, schema_field in metric_mapping.items():
        if api_field in public_metrics:
            activity_metrics[schema_field] = public_metrics[api_field]

    activity_metrics["last_captured_at"] = now

    # Entry threshold
    verified_min = verified != "none" and followers_count >= 30000
    unverified_min = followers_count >= 50000
    entry_threshold_passed = verified_min or unverified_min

    # Provenance hash
    canonical = {
        "id": user.get("id", ""),
        "username": user.get("username", ""),
        "followers_count": followers_count,
        "verified": verified_type,
    }
    canonical_json = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    provenance_hash = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    # Build record
    record = {
        "id": user.get("id", ""),
        "handle": user.get("username", ""),
        "name": user.get("name", ""),
        "verified": verified,
        "followers_count": followers_count,
        "is_org": False,  # These are personal accounts
        "is_official": False,  # These are personal accounts
        "lang_primary": "en",
        "topic_tags": [],
        "meta": {
            "score": quality_score,
            "last_refresh_at": now,
            "sources": [
                {
                    "method": "rube_mcp_direct",
                    "fetched_at": now,
                    "evidence": f"@{user.get('username', '')}",
                }
            ],
            "provenance_hash": provenance_hash,
            "entry_threshold_passed": entry_threshold_passed,
            "quality_score": quality_score,
            "activity_metrics": activity_metrics,
        },
        "entry_threshold_passed": entry_threshold_passed,
        "quality_score": quality_score,
        "ext": {"activity_metrics": activity_metrics},
    }

    return record


def main():
    # Read the real RUBE MCP data I fetched earlier
    with open("tmp_m24_fetched.jsonl", "r") as f:
        lines = f.readlines()

    # Transform to influx schema
    records = []
    for line in lines:
        if not line.strip():
            continue
        try:
            user_data = json.loads(line)
            record = transform_rube_data_to_schema(user_data)
            records.append(record)
        except Exception as e:
            print(f"Error processing line: {e}")
            continue

    # Write output
    with open("m24_real_data.jsonl", "w") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Processed {len(records)} records")
    print("Output: m24_real_data.jsonl")


if __name__ == "__main__":
    main()
