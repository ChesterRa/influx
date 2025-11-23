#!/usr/bin/env python3
"""
Safe author addition tool to prevent data corruption
"""

import json
import hashlib
import sys
from datetime import datetime, timezone


def safe_merge_datasets(base_file, new_authors_file, output_file):
    """Safely merge datasets without corruption"""

    # Read base dataset
    print(f"Reading base dataset from {base_file}")
    with open(base_file, "r") as f:
        base_lines = f.readlines()

    # Read new authors
    print(f"Reading new authors from {new_authors_file}")
    with open(new_authors_file, "r") as f:
        new_lines = f.readlines()

    # Combine datasets
    print("Combining datasets...")
    combined_lines = base_lines + new_lines

    # Remove duplicates by handle
    seen_handles = set()
    unique_lines = []
    duplicates_removed = 0

    for line in combined_lines:
        if not line.strip():
            continue

        try:
            record = json.loads(line)
            handle = record.get("handle", "")

            if handle in seen_handles:
                duplicates_removed += 1
                continue
            else:
                seen_handles.add(handle)
                unique_lines.append(line)
        except:
            continue

    print(f"Removed {duplicates_removed} duplicate entries")
    print(f"Total unique records: {len(unique_lines)}")

    # Write output with validation
    print(f"Writing to {output_file}")
    with open(output_file, "w") as f:
        for line in unique_lines:
            f.write(line)

    # Verify output
    with open(output_file, "r") as f:
        written_lines = f.readlines()

    if len(written_lines) != len(unique_lines):
        print(
            f"ERROR: Write verification failed! Expected {len(unique_lines)}, got {len(written_lines)}"
        )
        return False

    print("✅ Safe merge completed successfully")
    return True


def update_manifest(output_file):
    """Update manifest with new count and SHA256"""

    # Count records
    with open(output_file, "r") as f:
        lines = f.readlines()

    count = len(lines)

    # Calculate SHA256
    with open(output_file, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()

    # Update manifest
    with open("data/latest/manifest.json", "r") as f:
        manifest = json.load(f)

    manifest["count"] = count
    manifest["sha256"] = sha256

    with open("data/latest/manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Updated manifest: {count} records, SHA256: {sha256}")


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python3 safe_add_authors.py <base_dataset> <new_authors> <output_file>"
        )
        return 1

    base_file = sys.argv[1]
    new_authors_file = sys.argv[2]
    output_file = sys.argv[3]

    print(f"Safe author addition: {base_file} + {new_authors_file} → {output_file}")

    # Create backup before modification
    backup_file = (
        f"data/latest/latest.jsonl.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    print(f"Creating backup: {backup_file}")

    import shutil

    shutil.copy2("data/latest/latest.jsonl", backup_file)

    # Safe merge
    if safe_merge_datasets(base_file, new_authors_file, output_file):
        update_manifest(output_file)
        print("✅ Author addition completed successfully")
        return 0
    else:
        print("❌ Author addition failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
