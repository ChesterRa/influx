#!/usr/bin/env python3
"""
Continue Quality Enhancement Processing
Process remaining batches 3-5 for critical quality enhancement
"""

import json
import subprocess
from datetime import datetime, timezone


def load_quality_enhancement_plan():
    """Load the quality enhancement plan"""
    with open("quality_enhancement_plan.json", "r") as f:
        return json.load(f)


def process_remaining_batch(batch_num, authors):
    """Process remaining quality enhancement batch"""
    print(f"\n🚀 PROCESSING QUALITY ENHANCEMENT BATCH {batch_num}")
    print(f"Authors: {len(authors)}")
    print(f"Total followers: {sum(a['followers'] for a in authors):,}")

    # Create handles file
    handles_file = f"quality_enhancement_batch_{batch_num}_handles.txt"
    with open(handles_file, "w") as f:
        f.write("\n".join([author["handle"] for author in authors]))

    # Step 1: Enhanced metrics collection
    output_file = f"quality_enhancement_batch_{batch_num}_refreshed.jsonl"
    cmd1 = [
        "./tools/influx-harvest",
        "bulk",
        "--handles-file",
        handles_file,
        "--out",
        output_file,
        "--batch-size",
        str(len(authors)),
        "--brand-rules",
        "lists/rules/brand_heuristics.yml",
        "--risk-rules",
        "lists/rules/risk_terms.yml",
    ]

    print(f"  📡 Capturing enhanced activity metrics...")
    result = subprocess.run(cmd1, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ❌ Error in batch {batch_num}: {result.stderr}")
        return None

    # Step 2: Apply M2 scoring
    scored_file = f"quality_enhancement_batch_{batch_num}_scored.jsonl"
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
        return None

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

    # Load and enhance scored authors with improvement tracking
    enhanced_authors = []
    with open(scored_file, "r") as f:
        for line in f:
            if line.strip():
                author_data = json.loads(line)
                handle = author_data.get("handle", "")

                # Find original author info for improvement tracking
                original_author = next(
                    (a for a in authors if a["handle"] == handle), None
                )

                if original_author:
                    # Add quality enhancement metadata
                    author_data["meta"]["quality_enhancement"] = True
                    author_data["meta"]["previous_score"] = original_author.get(
                        "current_score", 0
                    )
                    author_data["meta"]["score_improvement"] = author_data["meta"][
                        "score"
                    ] - original_author.get("current_score", 0)
                    author_data["meta"]["score_model"] = "m2_enhanced_v1"
                    author_data["meta"]["data_source"] = "twitter_api_enhanced"

                    enhanced_authors.append(author_data)

    # Save enhanced results
    with open(scored_file, "w") as f:
        for author in enhanced_authors:
            f.write(json.dumps(author) + "\n")

    # Calculate batch statistics
    total_improvement = sum(
        author["meta"]["score_improvement"] for author in enhanced_authors
    )
    avg_improvement = (
        total_improvement / len(enhanced_authors) if enhanced_authors else 0
    )

    print(f"✅ Batch {batch_num} COMPLETE:")
    print(f"  Authors processed: {len(enhanced_authors)}")
    print(f"  Total score improvement: {total_improvement:.1f} points")
    print(f"  Average improvement: {avg_improvement:.1f} points")
    print(f"  Results saved: {scored_file}")

    return enhanced_authors


def main():
    """Continue quality enhancement for remaining batches"""
    print("🚀 CONTINUING QUALITY ENHANCEMENT")
    print("=" * 50)

    # Load plan
    plan = load_quality_enhancement_plan()
    batches = plan["batches"]

    # Process remaining batches (3-5)
    remaining_batches = batches[2:]  # Skip first 2 batches already done

    all_processed_authors = []

    for batch in remaining_batches:
        batch_num = batch["batch_num"]
        authors = batch["authors"]

        processed_authors = process_remaining_batch(batch_num, authors)
        if processed_authors:
            all_processed_authors.extend(processed_authors)

    # Combine all batch results
    print(f"\n🔗 COMBINING ALL QUALITY ENHANCEMENT RESULTS...")

    all_batch_files = [
        "quality_enhancement_batch_1_scored.jsonl",
        "quality_enhancement_batch_2_scored.jsonl",
        "quality_enhancement_batch_3_scored.jsonl",
        "quality_enhancement_batch_4_scored.jsonl",
        "quality_enhancement_batch_5_scored.jsonl",
    ]

    combined_file = "data/latest/quality_enhancement_complete.jsonl"
    with open(combined_file, "w") as outfile:
        for batch_file in all_batch_files:
            try:
                with open(batch_file, "r") as infile:
                    outfile.write(infile.read())
            except FileNotFoundError:
                print(f"⚠️  Batch file not found: {batch_file}")

    # Generate final report
    all_authors = []
    for batch_file in all_batch_files:
        try:
            with open(batch_file, "r") as f:
                for line in f:
                    if line.strip():
                        all_authors.append(json.loads(line))
        except FileNotFoundError:
            continue

    if all_authors:
        total_improvement = sum(
            author["meta"]["score_improvement"] for author in all_authors
        )
        avg_improvement = total_improvement / len(all_authors)

        print(f"\n📊 QUALITY ENHANCEMENT COMPLETE:")
        print(f"  Total authors processed: {len(all_authors)}")
        print(f"  Total score improvement: {total_improvement:.1f} points")
        print(f"  Average improvement: {avg_improvement:.1f} points")
        print(f"  Results saved: {combined_file}")

        # Show top improvements
        top_improvements = sorted(
            all_authors, key=lambda x: x["meta"]["score_improvement"], reverse=True
        )[:10]
        print(f"\n🏆 TOP 10 SCORE IMPROVEMENTS:")
        for i, author in enumerate(top_improvements, 1):
            improvement = author["meta"]["score_improvement"]
            old_score = author["meta"]["previous_score"]
            new_score = author["meta"]["score"]
            print(f"  {i:2d}. {author['name']} (@{author['handle']}):")
            print(f"      {old_score:.1f} → {new_score:.1f} (+{improvement:.1f})")

    print(f"\n🎯 QUALITY ENHANCEMENT EXECUTION COMPLETE")


if __name__ == "__main__":
    main()
