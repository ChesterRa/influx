#!/usr/bin/env python3
"""
Fix verified field values to match schema enum
"""

import json
import hashlib
from datetime import datetime, timezone


def fix_verified_values(input_file, output_file):
    """Fix verified field to match schema enum values"""

    # Read existing data
    records = []
    with open(input_file, "r") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    # Fix verified field values
    fixed_records = []
    for record in records:
        verified = record.get("verified", "")
        verified_type = record.get("meta", {}).get("verified_type", "none")

        # Map to schema enum values
        if verified == "true" or verified is True:
            if verified_type == "blue":
                record["verified"] = "blue"
            elif verified_type == "business":
                record["verified"] = "business"
            elif verified_type == "org":
                record["verified"] = "org"
            elif verified_type == "legacy":
                record["verified"] = "legacy"
            else:
                record["verified"] = "blue"  # Default for verified accounts
        elif verified == "false" or verified is False:
            record["verified"] = "none"
        else:
            # Already in correct format or unknown
            if verified not in ["none", "blue", "org", "legacy", "business"]:
                record["verified"] = "none"

        fixed_records.append(record)

    # Write fixed data
    with open(output_file, "w") as f:
        for record in fixed_records:
            f.write(json.dumps(record) + "\n")

    print(f"Fixed verified values in {len(fixed_records)} records")
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
        "last_batch": "batch_28_missing_placeholders_final",
        "quality_gates": "strict_compliance",
    }

    with open("data/latest/manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(
        f"Updated manifest: {count} records, SHA256: {sha256_hash.hexdigest()[:16]}..."
    )


def main():
    # Fix verified values
    fix_verified_values("data/latest/latest.jsonl", "data/latest/latest_fixed.jsonl")

    # Replace original
    import shutil

    shutil.move("data/latest/latest_fixed.jsonl", "data/latest/latest.jsonl")

    # Update manifest
    with open("data/latest/latest.jsonl", "r") as f:
        count = sum(1 for line in f if line.strip())

    update_manifest(count)
    print("✅ Fixed verified values and updated manifest")


if __name__ == "__main__":
    main()
