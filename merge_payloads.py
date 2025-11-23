#!/usr/bin/env python3
"""Merge processed payloads into the main dataset."""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path


def load_dataset(filepath):
    """Load dataset from JSONL file."""
    profiles = []
    with open(filepath, "r") as f:
        for line in f:
            if line.strip():
                profiles.append(json.loads(line))
    return profiles


def save_dataset(filepath, profiles):
    """Save dataset to JSONL file."""
    with open(filepath, "w") as f:
        for profile in profiles:
            f.write(json.dumps(profile) + "\n")


def load_payload(filepath):
    """Load and extract qualified authors from payload file."""
    with open(filepath, "r") as f:
        payload = json.load(f)
    
    # Extract qualified authors from the payload
    qualified = payload.get("qualified_authors", [])
    
    # Convert to influx schema format
    converted = []
    for author in qualified:
        # Map payload fields to influx schema
        influx_author = {
            "id": str(author["id"]),
            "handle": author["username"],
            "name": author["name"],
            "description": author.get("description", ""),
            "followers_count": author["followers_count"],
            "verified": "blue" if author.get("verified") else "none",
            "is_org": False,  # Assume false for qualified authors
            "is_official": False,  # Assume false for qualified authors
            "lang_primary": "en",  # Default to English
            "topic_tags": [author.get("category", "general")],
            "entry_threshold_passed": author.get("entry_threshold_passed", True),
            "meta": {
                "score": author.get("quality_score", 50),
                "quality_score": author.get("quality_score", 50),
                "last_refresh_at": datetime.now(timezone.utc).isoformat(),
                "entry_threshold_passed": author.get("entry_threshold_passed", True),
                "sources": [{
                    "method": "rube_mcp_direct",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "evidence": f"Payload from {payload.get('batch_info', {}).get('source_file', 'unknown')}"
                }],
                "provenance_hash": hashlib.sha256(
                    f"{author['id']}{author['followers_count']}{datetime.now(timezone.utc).isoformat()}".encode()
                ).hexdigest()[:16]
            }
        }
        converted.append(influx_author)
    
    return converted


def update_manifest(count, filepath="data/latest/manifest.json"):
    """Update manifest with new count and SHA256."""
    with open(filepath, "r") as f:
        manifest = json.load(f)

    # Update basic fields
    manifest["count"] = count
    manifest["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Calculate new SHA256
    dataset_content = Path("data/latest/latest.jsonl").read_bytes()
    manifest["sha256"] = hashlib.sha256(dataset_content).hexdigest()

    with open(filepath, "w") as f:
        json.dump(manifest, f, indent=2)


def main():
    # Load existing dataset
    existing = load_dataset("data/latest/latest.jsonl")
    print(f"Loaded {len(existing)} existing authors")
    
    # Payload files to merge
    payload_files = [
        "tmp_m16_payload.json",
        "tmp_m17_payload.json", 
        "tmp_m18_payload.json",
        "tmp_m19_payload.json",
        "tmp_m20_payload.json",
        "tmp_m24_payload.json",
        "tmp_m25_payload.json"
    ]
    
    new_authors = []
    for payload_file in payload_files:
        if Path(payload_file).exists():
            try:
                authors = load_payload(payload_file)
                new_authors.extend(authors)
                print(f"Loaded {len(authors)} authors from {payload_file}")
            except Exception as e:
                print(f"Error loading {payload_file}: {e}")
        else:
            print(f"Skipping {payload_file} (not found)")
    
    print(f"Loaded {len(new_authors)} total new authors from payloads")
    
    # Check for duplicates
    existing_handles = {author["handle"] for author in existing}
    new_handles = {author["handle"] for author in new_authors}
    duplicates = existing_handles.intersection(new_handles)
    
    if duplicates:
        print(f"Warning: {len(duplicates)} duplicate handles found: {list(duplicates)[:5]}")
        new_authors = [
            author for author in new_authors if author["handle"] not in duplicates
        ]
        print(f"After dedup: {len(new_authors)} new authors to add")
    
    # Merge datasets
    merged = existing + new_authors
    print(f"Merged dataset will have {len(merged)} authors (+{len(new_authors)} net increase)")
    
    # Sort by score (descending), then followers (descending), then handle (ascending)
    merged.sort(key=lambda x: (-x["meta"]["score"], -x["followers_count"], x["handle"]))
    
    # Backup current dataset
    backup_file = f"data/latest/latest.jsonl.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    Path("data/latest/latest.jsonl").rename(backup_file)
    print(f"Backed up current dataset to {backup_file}")
    
    # Save merged dataset
    save_dataset("data/latest/latest.jsonl", merged)
    
    # Update manifest
    update_manifest(len(merged))
    
    print("✅ Payload merge completed successfully!")
    print(f"Dataset now has {len(merged)} authors (+{len(new_authors)} net increase)")
    
    # Run pipeline guard to validate
    import subprocess
    try:
        result = subprocess.run(
            ["./scripts/pipeline_guard.sh", "data/latest/latest.jsonl", "data/latest/manifest.json", "schema/bigv.schema.json"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Pipeline guard validation PASSED")
    except subprocess.CalledProcessError as e:
        print(f"❌ Pipeline guard validation FAILED: {e.stderr}")
        return False
    
    return True


if __name__ == "__main__":
    main()
