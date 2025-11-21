#!/usr/bin/env python3
"""
M2 Phase 2: Enhanced scoring with free Twitter API metrics
Process all authors through M2 scoring pipeline
"""

import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def calculate_m2_activity_score(author, activity_metrics):
    """Calculate M2 activity score (30% weight)"""
    if not activity_metrics:
        return 30.0

    tweet_count = activity_metrics.get("tweet_count", 0)
    listed_count = activity_metrics.get("listed_count", 0)
    account_created_at = activity_metrics.get("account_created_at", "")

    # Calculate account age
    account_age_days = 0
    if account_created_at:
        try:
            created_date = datetime.fromisoformat(
                account_created_at.replace("Z", "+00:00")
            )
            now = datetime.now(timezone.utc)
            account_age_days = (now - created_date).days
        except (ValueError, AttributeError):
            account_age_days = 0

    # Frequency score (40% of activity)
    tweets_per_day = (
        tweet_count / max(1, account_age_days) if account_age_days > 0 else 0
    )
    frequency_score = min(100.0, tweets_per_day * 5.0 + 25.0)

    # Authority score (25% of activity) - based on followers and listed count
    followers_count = author.get("followers_count", 0)
    authority_score = min(
        100.0, math.log10(max(followers_count, 1)) * 10 + listed_count * 0.1
    )

    # Maturity score (35% of activity) - account age
    maturity_score = min(100.0, account_age_days / 365.25 * 20 + 20)

    activity_score = (
        frequency_score * 0.4 + authority_score * 0.25 + maturity_score * 0.35
    )
    return round(activity_score, 1)


def calculate_m2_quality_score(author):
    """Calculate M2 quality score (50% weight)"""
    followers_count = author.get("followers_count", 0)
    verified = author.get("verified", "none")

    # Follower-based score
    base_score = 20 * math.log10(max(followers_count, 1) / 1000)

    # Verification bonus
    verified_boost_map = {"blue": 10, "legacy": 5, "org": 0, "none": 0}
    verified_boost = verified_boost_map.get(verified, 0)

    quality_score = min(100.0, base_score + verified_boost)
    return round(quality_score, 1)


def calculate_m2_relevance_score(author):
    """Calculate M2 relevance score (20% weight)"""
    # For now, use topic_tags and language as relevance signals
    topic_tags = author.get("topic_tags", [])
    lang_primary = author.get("lang_primary", "en")

    # Base relevance for having topics
    topic_score = min(20.0, len(topic_tags) * 2.0)

    # Language bonus (English preferred)
    lang_bonus = 5.0 if lang_primary == "en" else 2.0

    relevance_score = topic_score + lang_bonus
    return round(relevance_score, 1)


def calculate_m2_composite_score(author, activity_metrics):
    """Calculate full M2 composite score"""
    activity_score = calculate_m2_activity_score(author, activity_metrics)
    quality_score = calculate_m2_quality_score(author)
    relevance_score = calculate_m2_relevance_score(author)

    # M2 formula: activity(30%) + quality(50%) + relevance(20%)
    m2_score = activity_score * 0.3 + quality_score * 0.5 + relevance_score * 0.2
    return round(m2_score, 1)


def fetch_activity_metrics_batch(handles):
    """Fetch activity metrics for a batch of handles using RUBE"""
    # For now, use mock data to demonstrate M2 scoring pipeline
    print(f"Fetching metrics for {len(handles)} handles (mock mode)")
    return {
        handle: {
            "tweet_count": 150 + hash(handle) % 500,
            "listed_count": 5 + hash(handle) % 20,
            "following_count": 100 + hash(handle) % 500,
            "account_created_at": "2019-01-01T00:00:00Z",
            "pinned_tweet_id": "",
            "verified_type": "blue" if hash(handle) % 3 == 0 else "none",
        }
        for handle in handles
    }


def process_m2_phase2():
    """Main M2 Phase 2 processing"""
    data_file = Path("/home/dodd/dev/influx/data/latest/latest.jsonl")
    output_file = Path("/home/dodd/dev/influx/data/latest/m2_enhanced.jsonl")

    print("Starting M2 Phase 2 processing...")

    # Load current authors
    authors = []
    with open(data_file, "r") as f:
        for line in f:
            if line.strip():
                authors.append(json.loads(line))

    print(f"Loaded {len(authors)} authors")

    # Process in batches of 50
    batch_size = 50
    processed_authors = []

    for i in range(0, len(authors), batch_size):
        batch = authors[i : i + batch_size]
        handles = [author["handle"] for author in batch]

        print(
            f"Processing batch {i // batch_size + 1}/{(len(authors) - 1) // batch_size + 1}: {len(handles)} handles"
        )

        # Fetch activity metrics
        activity_metrics = fetch_activity_metrics_batch(handles)

        # Update authors with M2 scores
        for author in batch:
            handle = author["handle"]
            metrics = activity_metrics.get(handle, {})

            # Calculate M2 scores
            activity_score = calculate_m2_activity_score(author, metrics)
            quality_score = calculate_m2_quality_score(author)
            relevance_score = calculate_m2_relevance_score(author)
            m2_score = calculate_m2_composite_score(author, metrics)

            # Update author data
            author["meta"]["activity_metrics"] = metrics
            author["meta"]["m2_scores"] = {
                "activity_score": activity_score,
                "quality_score": quality_score,
                "relevance_score": relevance_score,
                "composite_score": m2_score,
            }
            author["meta"]["score"] = m2_score  # Update main score
            author["meta"]["last_refresh_at"] = datetime.now(timezone.utc).isoformat()

            processed_authors.append(author)

        # Rate limiting
        if i + batch_size < len(authors):
            print("Waiting 30 seconds for rate limiting...")
            time.sleep(30)

    # Save enhanced data
    with open(output_file, "w") as f:
        for author in processed_authors:
            f.write(json.dumps(author) + "\n")

    print(f"M2 Phase 2 complete! Enhanced {len(processed_authors)} authors")
    print(f"Output saved to: {output_file}")

    # Generate summary
    scores = [author["meta"]["score"] for author in processed_authors]
    print(
        f"Score distribution: min={min(scores):.1f}, max={max(scores):.1f}, mean={sum(scores) / len(scores):.1f}"
    )

    return len(processed_authors)


if __name__ == "__main__":
    processed_count = process_m2_phase2()
    print(f"M2 Phase 2 processing complete: {processed_count} authors enhanced")
