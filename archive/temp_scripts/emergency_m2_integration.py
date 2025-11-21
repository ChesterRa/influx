#!/usr/bin/env python3
"""
Emergency M2 Data Integration Script
Merge M2 Phase 2 results into main dataset and identify gaps
"""

import json
from pathlib import Path
from datetime import datetime, timezone


def load_jsonl(file_path):
    """Load JSONL file into list of dicts"""
    data = []
    with open(file_path, "r") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def save_jsonl(data, file_path):
    """Save list of dicts to JSONL file"""
    with open(file_path, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")


def integrate_m2_data():
    """Emergency integration of M2 Phase 2 results"""

    # Load datasets
    main_file = Path("/home/dodd/dev/influx/data/latest/latest.jsonl")
    m2_file = Path(
        "/home/dodd/dev/influx/archive/temp_work_m2_phase2/m2_phase2_final_scored.jsonl"
    )
    backup_file = Path(
        "/home/dodd/dev/influx/data/latest/latest_backup_before_integration.jsonl"
    )

    print("Loading datasets...")
    main_authors = load_jsonl(main_file)
    m2_authors = load_jsonl(m2_file)

    print(f"Main dataset: {len(main_authors)} authors")
    print(f"M2 Phase 2: {len(m2_authors)} authors")

    # Create backup
    save_jsonl(main_authors, backup_file)
    print(f"Backup created: {backup_file}")

    # Create lookup for M2 data
    m2_lookup = {author["handle"]: author for author in m2_authors}

    # Integration statistics
    integrated = 0
    with_metrics = 0
    remaining = 0

    # Process main dataset
    for author in main_authors:
        handle = author["handle"]

        if handle in m2_lookup:
            # Integrate M2 data
            m2_author = m2_lookup[handle]

            # Update with M2 scores and metrics
            if "meta" not in author:
                author["meta"] = {}

            # Copy M2 scores
            if "m2_scores" in m2_author.get("meta", {}):
                author["meta"]["m2_scores"] = m2_author["meta"]["m2_scores"]

            # Copy activity metrics
            if "activity_metrics" in m2_author.get("meta", {}):
                author["meta"]["activity_metrics"] = m2_author["meta"][
                    "activity_metrics"
                ]
                with_metrics += 1

            # Update main score if M2 composite available
            m2_composite = (
                m2_author.get("meta", {}).get("m2_scores", {}).get("composite_score")
            )
            if m2_composite:
                author["meta"]["score"] = m2_composite

            # Update refresh timestamp
            author["meta"]["last_refresh_at"] = datetime.now(timezone.utc).isoformat()

            integrated += 1
        else:
            remaining += 1

    # Save integrated dataset
    save_jsonl(main_authors, main_file)

    # Generate report
    print(f"\n=== INTEGRATION REPORT ===")
    print(f"Authors integrated: {integrated}")
    print(f"Authors with activity_metrics: {with_metrics}")
    print(f"Authors remaining for API processing: {remaining}")
    print(f"Coverage: {with_metrics / len(main_authors) * 100:.1f}%")

    # Score distribution
    scores = [a.get("meta", {}).get("score", 0) for a in main_authors]
    print(f"Score range: {min(scores):.1f} - {max(scores):.1f}")
    print(f"Zero scores: {sum(1 for s in scores if s == 0)}")

    # Create list of remaining handles
    remaining_handles = [
        a["handle"] for a in main_authors if a["handle"] not in m2_lookup
    ]

    remaining_file = Path("/home/dodd/dev/influx/temp_remaining_handles.txt")
    with open(remaining_file, "w") as f:
        for handle in remaining_handles:
            f.write(f"{handle}\n")

    print(f"\nRemaining handles saved to: {remaining_file}")
    print(f"Ready for batch API processing: {len(remaining_handles)} authors")

    return integrated, with_metrics, remaining


if __name__ == "__main__":
    integrate_m2_data()
