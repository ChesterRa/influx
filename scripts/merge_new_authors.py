#!/usr/bin/env python3
"""
merge_new_authors.py: Safe batch integration with mandatory quality gates.

This script enforces the zero-tolerance quality policy by requiring:
1. pipeline_guard.sh validation (duplicates, placeholders, fake data)
2. Strict schema compliance
3. Proper manifest updates

Usage:
    python merge_new_authors.py NEW_AUTHORS.jsonl
"""

import argparse
import json
import sys
import subprocess
import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def run_pipeline_guard(input_file: str, manifest_file: str, schema_file: str) -> bool:
    """Run pipeline_guard.sh quality checks"""
    try:
        result = subprocess.run(
            ["./scripts/pipeline_guard.sh", input_file, manifest_file, schema_file],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"[INFO] pipeline_guard passed: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] pipeline_guard failed: {e.stderr.strip()}")
        return False


def run_strict_validation(
    input_file: str, manifest_file: str, schema_file: str
) -> bool:
    """Run strict schema validation"""
    try:
        result = subprocess.run(
            [
                "./tools/influx-validate",
                "--strict",
                "-s",
                schema_file,
                "-m",
                manifest_file,
                input_file,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"[INFO] Strict validation passed: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Strict validation failed: {e.stderr.strip()}")
        return False


def backup_current_dataset() -> str:
    """Create backup of current dataset"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"data/latest/latest.jsonl.backup.{timestamp}"

    if Path("data/latest/latest.jsonl").exists():
        shutil.copy2("data/latest/latest.jsonl", backup_file)
        print(f"[INFO] Created backup: {backup_file}")
        return backup_file
    else:
        print("[WARN] No existing dataset to backup")
        return ""


def merge_datasets(main_file: str, new_file: str, output_file: str) -> int:
    """Merge new authors into main dataset"""
    # Load existing data
    existing_data = []
    if Path(main_file).exists():
        with open(main_file, "r", encoding="utf-8") as f:
            existing_data = [json.loads(line) for line in f if line.strip()]

    # Load new data
    with open(new_file, "r", encoding="utf-8") as f:
        new_data = [json.loads(line) for line in f if line.strip()]

    # Get existing handles for deduplication
    existing_handles = {item.get("handle") for item in existing_data}

    # Filter out duplicates from new data
    unique_new = [
        item for item in new_data if item.get("handle") not in existing_handles
    ]

    if len(unique_new) != len(new_data):
        dup_count = len(new_data) - len(unique_new)
        print(f"[INFO] Filtered out {dup_count} duplicates from new batch")

    # Merge datasets
    merged_data = existing_data + unique_new

    # Sort by score desc, followers_count desc, handle asc
    merged_data.sort(
        key=lambda x: (
            -x.get("meta", {}).get("quality_score", 0),
            -x.get("followers_count", 0),
            x.get("handle", ""),
        )
    )

    # Write merged data
    with open(output_file, "w", encoding="utf-8") as f:
        for item in merged_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    return len(unique_new)


def update_manifest(output_file: str, manifest_file: str, added_count: int):
    """Update manifest.json with new count and SHA256"""
    # Calculate SHA256
    with open(output_file, "rb") as f:
        sha256_hash = hashlib.sha256(f.read()).hexdigest()

    # Load existing manifest
    manifest = {}
    if Path(manifest_file).exists():
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

    # Update manifest
    manifest.update(
        {
            "count": sum(
                1 for line in Path(output_file).read_text().splitlines() if line.strip()
            ),
            "sha256": sha256_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "schema_version": "v1.0.0",
            "score_version": "v2_activity_quality_relevance",
            "score_formula": "weighted_sum: engagement_30d*0.4 + follower_growth_30d*0.3 + tweet_frequency_7d*0.2 + network_centrality*0.1",
            "score_note": "M2 scoring model with activity, quality, and relevance factors",
            "source_file": output_file,
            "sort_order": "score_desc,followers_desc,handle_asc",
        }
    )

    # Write updated manifest
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(
        f"[INFO] Updated manifest: {manifest['count']} authors, SHA256: {sha256_hash[:16]}..."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Merge new authors with mandatory quality gates"
    )
    parser.add_argument("new_authors_file", help="New authors JSONL file to merge")
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate only, do not merge"
    )

    args = parser.parse_args()

    new_file = args.new_authors_file
    main_file = "data/latest/latest.jsonl"
    manifest_file = "data/latest/manifest.json"
    schema_file = "schema/bigv.schema.json"

    # Validate inputs
    if not Path(new_file).exists():
        print(f"[ERROR] New authors file not found: {new_file}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Processing new authors batch: {new_file}")

    # Step 1: Run pipeline_guard on new file
    print("[STEP 1] Running pipeline_guard quality checks...")
    if not run_pipeline_guard(new_file, manifest_file, schema_file):
        print(
            "[ERROR] pipeline_guard validation failed - aborting merge", file=sys.stderr
        )
        sys.exit(1)

    # Step 2: Run strict validation on new file
    print("[STEP 2] Running strict schema validation...")
    if not run_strict_validation(new_file, manifest_file, schema_file):
        print("[ERROR] Strict validation failed - aborting merge", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("[INFO] Dry run completed - all validations passed")
        sys.exit(0)

    # Step 3: Backup current dataset
    print("[STEP 3] Creating backup...")
    backup_file = backup_current_dataset()

    # Step 4: Merge datasets
    print("[STEP 4] Merging datasets...")
    temp_file = f"data/latest/latest_temp.jsonl"
    added_count = merge_datasets(main_file, new_file, temp_file)

    if added_count == 0:
        print("[INFO] No new authors to add (all duplicates)")
        Path(temp_file).unlink()
        sys.exit(0)

    # Step 5: Validate merged dataset
    print("[STEP 5] Validating merged dataset...")
    if not run_pipeline_guard(temp_file, manifest_file, schema_file):
        print(
            "[ERROR] Merged dataset failed pipeline_guard - rolling back",
            file=sys.stderr,
        )
        Path(temp_file).unlink()
        sys.exit(1)

    if not run_strict_validation(temp_file, manifest_file, schema_file):
        print(
            "[ERROR] Merged dataset failed strict validation - rolling back",
            file=sys.stderr,
        )
        Path(temp_file).unlink()
        sys.exit(1)

    # Step 6: Replace main dataset
    print("[STEP 6] Replacing main dataset...")
    shutil.move(temp_file, main_file)

    # Step 7: Update manifest
    print("[STEP 7] Updating manifest...")
    update_manifest(main_file, manifest_file, added_count)

    # Step 8: Update release files
    print("[STEP 8] Updating release files...")
    shutil.copy2(main_file, "data/release/influx-latest.jsonl")

    # Compress release file
    try:
        subprocess.run(["gzip", "-kf", "data/release/influx-latest.jsonl"], check=True)
        print("[INFO] Created compressed release file")
    except subprocess.CalledProcessError:
        print("[WARN] Failed to compress release file")

    # Copy manifest to release
    shutil.copy2(manifest_file, "data/release/manifest.json")

    print(f"[SUCCESS] Merged {added_count} new authors")
    print(f"[INFO] Backup: {backup_file}")
    print(
        f"[INFO] Dataset: {sum(1 for line in Path(main_file).read_text().splitlines() if line.strip())} authors"
    )


if __name__ == "__main__":
    main()
