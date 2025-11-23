#!/usr/bin/env python3
"""
Remove placeholder IDs from dataset
"""

import json


def remove_placeholders(input_file, output_file):
    """Remove profiles with placeholder IDs"""
    profiles = []
    placeholders_removed = 0

    with open(input_file, "r") as f:
        for line in f:
            if line.strip():
                profile = json.loads(line)
                profile_id = profile.get("id", "")
                if not profile_id.startswith("123456789"):
                    profiles.append(profile)
                else:
                    placeholders_removed += 1

    with open(output_file, "w") as f:
        for profile in profiles:
            f.write(json.dumps(profile) + "\n")

    return len(profiles), placeholders_removed


# Remove placeholders
real_count, placeholder_count = remove_placeholders(
    "data/latest/latest.jsonl", "data/latest/latest_real_only.jsonl"
)
print(f"Real profiles: {real_count}")
print(f"Placeholder profiles removed: {placeholder_count}")

# Update dataset
import hashlib
from datetime import datetime, timezone


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


# Replace dataset and update manifest
import shutil

shutil.move("data/latest/latest_real_only.jsonl", "data/latest/latest.jsonl")
new_hash = calculate_sha256("data/latest/latest.jsonl")
update_manifest("data/latest/manifest.json", real_count, new_hash)

print(f"Dataset updated: {real_count} real profiles")
print(f"New SHA256: {new_hash}")
