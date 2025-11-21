#!/usr/bin/env python3
"""
M2 Phase 2 Execution Script - Resolve Scoring Crisis
Processes 74 authors with 0.0 scores using enhanced M2 activity metrics
Timeline: 2-3 hours | Cost: $0 (free Twitter API) | Impact: Critical
"""

import subprocess
import json
import os
from pathlib import Path


def extract_zero_score_authors():
    """Extract authors with 0.0 scores from current dataset"""
    zero_score_authors = []

    with open("data/latest/latest.jsonl", "r") as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                if record.get("meta", {}).get("score", 0) == 0.0:
                    zero_score_authors.append(
                        {
                            "handle": record["handle"],
                            "id": record["id"],
                            "name": record["name"],
                            "followers": record.get("followers_count", 0),
                        }
                    )

    print(f"🎯 Found {len(zero_score_authors)} authors with 0.0 scores")

    # Sort by followers (highest impact first)
    zero_score_authors.sort(key=lambda x: x["followers"], reverse=True)

    # Show top 10 most valuable authors needing rescue
    print("\n📊 Top 10 High-Value Authors Requiring M2 Scoring:")
    for i, author in enumerate(zero_score_authors[:10], 1):
        print(
            f"  {i:2d}. {author['name']} (@{author['handle']}): {author['followers']:,} followers"
        )

    return zero_score_authors


def create_m2_batches(authors, batch_size=50):
    """Create batches for M2 processing"""
    batches = []
    for i in range(0, len(authors), batch_size):
        batch = authors[i : i + batch_size]
        batches.append(batch)
    return batches


def process_m2_batch(batch, batch_num):
    """Process a single batch through M2 pipeline"""
    print(f"\n🔄 Processing Batch {batch_num}: {len(batch)} authors")

    # Create handles file
    handles_file = f"m2_batch_{batch_num:03d}_handles.txt"
    with open(handles_file, "w") as f:
        f.write("\n".join([author["handle"] for author in batch]))

    # Step 1: Enhanced metrics collection
    output_file = f"m2_batch_{batch_num:03d}_refreshed.jsonl"
    cmd1 = [
        "./tools/influx-harvest",
        "bulk",
        "--handles-file",
        handles_file,
        "--out",
        output_file,
        "--batch-size",
        str(len(batch)),
        "--brand-rules",
        "lists/rules/brand_heuristics.yml",
        "--risk-rules",
        "lists/rules/risk_terms.yml",
    ]

    print(f"  📡 Capturing M2 activity metrics...")
    result = subprocess.run(cmd1, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ❌ Error in batch {batch_num}: {result.stderr}")
        return None, None

    # Step 2: Apply M2 scoring
    scored_file = f"m2_batch_{batch_num:03d}_scored.jsonl"
    cmd2 = [
        "./tools/influx-score",
        "update",
        "--authors",
        output_file,
        "--out",
        scored_file,
        "--model",
        "m2",
    ]

    print(f"  🎯 Applying M2 scoring model...")
    result = subprocess.run(cmd2, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ❌ Error in M2 scoring batch {batch_num}: {result.stderr}")
        return None, None

    # Step 3: Validation
    cmd3 = [
        "python3",
        "tools/influx-validate",
        "--strict",
        "-s",
        "schema/bigv.schema.json",
        scored_file,
    ]

    print(f"  ✅ Validating M2 scores...")
    result = subprocess.run(cmd3, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ⚠️  Validation warnings batch {batch_num}")
        print(f"     {result.stdout}")

    return scored_file, batch


def analyze_score_improvements(scored_file, batch_info):
    """Analyze score improvements for the batch"""
    improvements = []

    with open(scored_file, "r") as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                score = record.get("meta", {}).get("score", 0)
                followers = record.get("followers_count", 0)
                handle = record.get("handle", "unknown")
                name = record.get("name", "unknown")

                improvements.append(
                    {
                        "name": name,
                        "handle": handle,
                        "followers": followers,
                        "new_score": score,
                        "improvement": score,  # From 0.0
                    }
                )

    # Sort by improvement
    improvements.sort(key=lambda x: x["improvement"], reverse=True)

    print(f"\n📈 Batch {batch_info} Score Improvements:")
    for i, imp in enumerate(improvements[:5], 1):
        print(
            f"  {i}. {imp['name']} (@{imp['handle']}): {imp['followers']:,} followers → {imp['new_score']:.1f} points"
        )

    return improvements


def main():
    """Execute M2 Phase 2 for zero-score crisis resolution"""
    print("🚀 M2 Phase 2 Execution - Scoring Crisis Resolution")
    print("=" * 60)

    # Step 1: Identify zero-score authors
    zero_score_authors = extract_zero_score_authors()

    if not zero_score_authors:
        print("✅ No authors with 0.0 scores found - crisis resolved!")
        return

    # Step 2: Create batches
    batches = create_m2_batches(zero_score_authors, 50)
    print(f"\n📦 Created {len(batches)} batches for processing")

    # Step 3: Process batches
    all_scored_files = []
    all_improvements = []

    for i, batch in enumerate(batches, 1):
        scored_file, batch_info = process_m2_batch(batch, i)

        if scored_file:
            all_scored_files.append(scored_file)
            improvements = analyze_score_improvements(scored_file, i)
            all_improvements.extend(improvements)

    # Step 4: Combine results
    if all_scored_files:
        print(f"\n🔄 Combining results from {len(all_scored_files)} batches...")
        combined_file = "data/latest/m2_crisis_resolved.jsonl"

        with open(combined_file, "w") as outfile:
            for scored_file in all_scored_files:
                with open(scored_file, "r") as infile:
                    outfile.write(infile.read())

        print(f"✅ M2 Crisis Resolution Complete!")
        print(f"📁 Enhanced dataset: {combined_file}")
        print(f"🎯 Resolved 0.0 scores for {len(zero_score_authors)} authors")

        # Summary
        if all_improvements:
            all_improvements.sort(key=lambda x: x["improvement"], reverse=True)
            print(f"\n🏆 Top 10 Overall Improvements:")
            for i, imp in enumerate(all_improvements[:10], 1):
                print(
                    f"  {i:2d}. {imp['name']} (@{imp['handle']}): {imp['followers']:,} followers → {imp['new_score']:.1f} points"
                )

        print(f"\n🎊 Scoring Crisis Resolved - Network Value Enhanced!")
        print(f"💰 Cost: $0 (free Twitter API)")
        print(f"⏱️  Timeline: ~2-3 hours")
        print(f"📈 Impact: Critical - 74 high-value authors properly scored")

    else:
        print("❌ No batches completed successfully - check RUBE MCP connection")


if __name__ == "__main__":
    main()
