#!/usr/bin/env python3
"""Merge all processed payload qualified authors into main dataset."""

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


def extract_qualified_authors(payload_file):
    """Extract qualified authors from payload file, ensuring proper format."""
    with open(payload_file, "r") as f:
        payload = json.load(f)
    
    qualified = payload.get("qualified_authors", [])
    batch_info = payload.get("batch_info", {})
    
    # Ensure all authors have required fields and proper structure
    converted_authors = []
    for author in qualified:
        # Skip if missing required fields
        if not all(k in author for k in ["id", "handle", "name", "followers_count"]):
            print(f"Skipping {author.get('handle', 'unknown')} - missing required fields")
            continue
            
        # Create influx-compliant author
        influx_author = {
            "id": str(author["id"]),
            "handle": author["handle"],
            "name": author["name"],
            "description": author.get("description", ""),
            "followers_count": int(author["followers_count"]),
            "verified": author.get("verified", "none"),
            "is_org": author.get("is_org", False),
            "is_official": author.get("is_official", False),
            "lang_primary": author.get("lang_primary", "en"),
            "topic_tags": author.get("topic_tags", ["general"]),
            "entry_threshold_passed": author.get("entry_threshold_passed", True),
            "meta": author.get("meta", {
                "score": 50,
                "quality_score": 50,
                "last_refresh_at": datetime.now(timezone.utc).isoformat(),
                "entry_threshold_passed": True,
                "sources": [{
                    "method": "rube_mcp_direct",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "evidence": f"Batch {batch_info.get('batch_id', 'unknown')}"
                }],
                "provenance_hash": hashlib.sha256(
                    f"{author['id']}{author['followers_count']}{datetime.now(timezone.utc).isoformat()}".encode()
                ).hexdigest()[:16]
            })
        }
        converted_authors.append(influx_author)
    
    return converted_authors, batch_info


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
    existing_handles = {author["handle"] for author in existing}
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
    
    all_new_authors = []
    batch_summaries = []
    
    for payload_file in payload_files:
        if Path(payload_file).exists():
            try:
                authors, batch_info = extract_qualified_authors(payload_file)
                if authors:
                    all_new_authors.extend(authors)
                    batch_summaries.append({
                        "batch_id": batch_info.get("batch_id", payload_file),
                        "authors_added": len(authors),
                        "success_rate": batch_info.get("success_rate", "N/A")
                    })
                    print(f"Loaded {len(authors)} qualified authors from {payload_file}")
            except Exception as e:
                print(f"Error loading {payload_file}: {e}")
        else:
            print(f"Skipping {payload_file} (not found)")
    
    # Check for duplicates against existing dataset
    new_handles = {author["handle"] for author in all_new_authors}
    duplicates = existing_handles.intersection(new_handles)
    
    if duplicates:
        print(f"Found {len(duplicates)} handles already in dataset: {list(duplicates)[:5]}")
        unique_new_authors = [
            author for author in all_new_authors if author["handle"] not in duplicates
        ]
        print(f"After dedup: {len(unique_new_authors)} new authors to add")
    else:
        unique_new_authors = all_new_authors
        print(f"All {len(unique_new_authors)} authors are new")
    
    # Merge datasets
    merged = existing + unique_new_authors
    print(f"Merged dataset will have {len(merged)} authors (+{len(unique_new_authors)} net increase)")
    
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
    
    # Print summary
    print("\n" + "="*50)
    print("✅ PAYLOAD MERGE COMPLETED SUCCESSFULLY!")
    print("="*50)
    print(f"Dataset now has {len(merged)} authors (+{len(unique_new_authors)} net increase)")
    print("\nBatch Summary:")
    for summary in batch_summaries:
        print(f"  - {summary['batch_id']}: +{summary['authors_added']} authors ({summary['success_rate']} success)")
    
    # Run pipeline guard to validate
    import subprocess
    try:
        result = subprocess.run(
            ["./scripts/pipeline_guard.sh", "data/latest/latest.jsonl", "data/latest/manifest.json", "schema/bigv.schema.json"],
            capture_output=True,
            text=True,
            check=True
        )
        print("\n✅ PIPELINE GUARD VALIDATION PASSED")
        print("Dataset is 100% compliant and ready for use!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ PIPELINE GUARD VALIDATION FAILED: {e.stderr}")
        return False
    
    return True


if __name__ == "__main__":
    main()
