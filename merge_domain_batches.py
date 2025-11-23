#!/usr/bin/env python3
import json
import hashlib
from datetime import datetime, timezone


def load_dataset(filepath):
    profiles = []
    with open(filepath, "r") as f:
        for line in f:
            if line.strip():
                profiles.append(json.loads(line))
    return profiles


def save_dataset(filepath, profiles):
    with open(filepath, "w") as f:
        for profile in profiles:
            f.write(json.dumps(profile) + "\n")


def update_manifest(count):
    manifest_path = "data/latest/manifest.json"
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    manifest["total_authors"] = count
    manifest["count"] = count
    manifest["last_updated"] = datetime.now(timezone.utc).isoformat()

    # Create SHA256 hash
    dataset_content = json.dumps(load_dataset("data/latest/latest.jsonl"))
    manifest["sha256"] = hashlib.sha256(dataset_content.encode()).hexdigest()

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)


# Load existing dataset
existing = load_dataset("data/latest/latest.jsonl")
print(f"Loaded {len(existing)} existing authors")

# Load new users from domain batches
batch_files = [
    "archive/manual_analysis/m11_sample_valid.jsonl",
    "archive/manual_analysis/m13_security_manual.jsonl",
    "archive/temp_files_20251122/tmp_m11_tech_ceos_compliant.jsonl",
]

new_authors = []
for batch_file in batch_files:
    try:
        batch_authors = load_dataset(batch_file)
        new_authors.extend(batch_authors)
        print(f"Loaded {len(batch_authors)} authors from {batch_file}")
    except FileNotFoundError:
        print(f"Warning: {batch_file} not found, skipping")

print(f"Loaded {len(new_authors)} total new authors from domain batches")

# Check for duplicates
existing_handles = {author["handle"] for author in existing}
new_handles = {author["handle"] for author in new_authors}
duplicates = existing_handles.intersection(new_handles)

if duplicates:
    print(f"Warning: {len(duplicates)} duplicate handles found: {duplicates}")
    new_authors = [
        author for author in new_authors if author["handle"] not in duplicates
    ]

# Merge datasets
merged = existing + new_authors
print(f"Merged dataset now has {len(merged)} authors")

# Sort by score (descending), then followers (descending), then handle (ascending)
merged.sort(key=lambda x: (-x["meta"]["score"], -x["followers_count"], x["handle"]))

# Save merged dataset
save_dataset("data/latest/latest.jsonl", merged)

# Update manifest
update_manifest(len(merged))

print("✅ Domain batch merge completed successfully!")
print(f"Dataset now has {len(merged)} authors (+{len(new_authors)} net increase)")
