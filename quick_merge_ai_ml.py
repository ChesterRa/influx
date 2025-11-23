#!/usr/bin/env python3
"""
Quick merge for AI/ML company profiles with username field
"""

import json
import hashlib
from datetime import datetime, timezone


def load_dataset(filepath):
    """Load existing dataset"""
    profiles = []
    with open(filepath, "r") as f:
        for line in f:
            if line.strip():
                profiles.append(json.loads(line))
    return profiles


def save_dataset(filepath, profiles):
    """Save dataset with proper formatting"""
    with open(filepath, "w") as f:
        for profile in profiles:
            f.write(json.dumps(profile) + "\n")


def calculate_sha256(filepath):
    """Calculate SHA256 hash of file"""
    hash_sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def update_manifest(manifest_path, count, sha256_hash):
    """Update manifest with new count and hash"""
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    manifest["count"] = count
    manifest["sha256"] = sha256_hash
    manifest["last_updated"] = datetime.now(timezone.utc).isoformat()

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)


# Load existing dataset and new profiles
existing_profiles = load_dataset("data/latest/latest.jsonl")
with open("/home/dodd/dev/influx/tmp_batch_27_converted.jsonl", "r") as f:
    new_profiles = [json.loads(line) for line in f if line.strip()]

# Check for duplicates by username and ID
existing_usernames = {p.get("handle", p.get("username")) for p in existing_profiles}
existing_ids = {p["id"] for p in existing_profiles}

# Filter out duplicates
unique_new_profiles = []
for profile in new_profiles:
    if (
        profile.get("handle", profile.get("username")) not in existing_usernames
        and profile["id"] not in existing_ids
    ):
        unique_new_profiles.append(profile)

print(f"Existing profiles: {len(existing_profiles)}")
print(f"New profiles: {len(new_profiles)}")
print(f"Unique new profiles: {len(unique_new_profiles)}")

# Merge datasets
merged_profiles = existing_profiles + unique_new_profiles

# Sort by quality_score desc, followers_count desc, handle asc (existing) or username asc (new)
merged_profiles.sort(
    key=lambda x: (
        -x["meta"]["quality_score"],
        -x["followers_count"],
        x.get("handle", x.get("username", "")),
    )
)

# Save merged dataset
output_path = "data/latest/latest.jsonl"
save_dataset(output_path, merged_profiles)

# Calculate new hash and update manifest
new_hash = calculate_sha256(output_path)
update_manifest("data/latest/manifest.json", len(merged_profiles), new_hash)

print(f"Dataset updated: {len(merged_profiles)} total profiles")
print(f"Added {len(unique_new_profiles)} new AI/ML company profiles")
print(f"New SHA256: {new_hash}")

# Show some high-value additions
high_value = [p for p in unique_new_profiles if p["meta"]["quality_score"] >= 99]
print(f"High-value additions (quality_score >= 99): {len(high_value)}")
for profile in high_value[:5]:
    print(
        f"  - {profile['name']} (@{profile.get('handle', profile.get('username'))}): {profile['followers_count']:,} followers"
    )
