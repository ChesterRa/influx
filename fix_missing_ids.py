#!/usr/bin/env python3
"""
Add missing ID field to batch 28 records
"""

import json
import hashlib
from datetime import datetime, timezone


def fix_missing_ids(input_file, output_file):
    """Add missing ID field using original_id from meta"""

    # Read existing data
    records = []
    with open(input_file, "r") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    # Fix missing IDs
    fixed_records = []
    for record in records:
        # Skip records that already have proper IDs
        if "id" in record and not str(record["id"]).startswith("123456789"):
            fixed_records.append(record)
            continue

        # Get original_id from meta if available
        original_id = record.get("meta", {}).get("original_id")
        if original_id:
            record["id"] = original_id
        else:
            # Generate a unique ID based on handle if no original_id
            handle = record.get("handle", "")
            record["id"] = f"fixed_{hashlib.md5(handle.encode()).hexdigest()[:16]}"

        fixed_records.append(record)

    # Write fixed data
    with open(output_file, "w") as f:
        for record in fixed_records:
            f.write(json.dumps(record) + "\n")

    print(f"Fixed missing IDs in {len(fixed_records)} records")
    print(f"Saved to: {output_file}")

    return fixed_records


def update_manifest(count):
    """Update manifest with new count and SHA256"""

    # Calculate SHA256
    sha256_hash = hashlib.sha256()
    with open("data/latest/latest.jsonl", "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)

    manifest = {
        "count": count,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "schema_version": "1.0.0",
        "sha256": sha256_hash.hexdigest(),
        "description": "Influx dataset - high-signal X influencer index",
        "last_batch": "batch_28_missing_placeholders_fixed",
        "quality_gates": "strict_compliance",
    }

    with open("data/latest/manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(
        f"Updated manifest: {count} records, SHA256: {sha256_hash.hexdigest()[:16]}..."
    )


def main():
    # Fix missing IDs
    fix_missing_ids("data/latest/latest.jsonl", "data/latest/latest_fixed.jsonl")

    # Replace original
    import shutil

    shutil.move("data/latest/latest_fixed.jsonl", "data/latest/latest.jsonl")

    # Update manifest
    with open("data/latest/latest.jsonl", "r") as f:
        count = sum(1 for line in f if line.strip())

    update_manifest(count)
    print("✅ Fixed missing IDs and updated manifest")


if __name__ == "__main__":
    main()
