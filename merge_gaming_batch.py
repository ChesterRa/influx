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

    return manifest


def main():
    # Load existing dataset
    existing_profiles = load_dataset("data/latest/latest.jsonl")
    existing_handles = {p["handle"] for p in existing_profiles}

    # Load new gaming batch
    new_profiles = load_dataset("tmp_gaming_scored_fixed.jsonl")

    # Filter out duplicates
    new_unique = [p for p in new_profiles if p["handle"] not in existing_handles]

    print(f"Existing profiles: {len(existing_profiles)}")
    print(f"New profiles: {len(new_profiles)}")
    print(f"New unique profiles: {len(new_unique)}")

    if not new_unique:
        print("No new profiles to add")
        return

    # Merge and sort by score (descending), then followers (descending), then handle (ascending)
    merged_profiles = existing_profiles + new_unique
    merged_profiles.sort(
        key=lambda p: (-p["meta"]["score"], -p["followers_count"], p["handle"])
    )

    # Save merged dataset
    save_dataset("data/latest/latest.jsonl", merged_profiles)

    # Update manifest
    manifest = update_manifest(len(merged_profiles))

    print(f"✅ Merged {len(new_unique)} new gaming profiles")
    print(f"📊 Total dataset: {len(merged_profiles)} authors")
    print(f"🔐 SHA256: {manifest['sha256'][:16]}...")


if __name__ == "__main__":
    main()
