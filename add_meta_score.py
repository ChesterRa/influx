#!/usr/bin/env python3
"""
Add missing meta.score field to batch 28 records
"""

import json
import hashlib
from datetime import datetime, timezone


def add_meta_score(input_file, output_file):
    """Add missing meta.score field using quality_score"""

    # Read existing data
    records = []
    with open(input_file, "r") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    # Add missing meta.score
    fixed_records = []
    for record in records:
        # Ensure meta object exists
        if "meta" not in record:
            record["meta"] = {}

        # Add score if missing
        if "score" not in record["meta"]:
            # Use quality_score as fallback
            quality_score = record.get("quality_score", 0)
            record["meta"]["score"] = quality_score

        fixed_records.append(record)

    # Write fixed data
    with open(output_file, "w") as f:
        for record in fixed_records:
            f.write(json.dumps(record) + "\n")

    print(f"Added meta.score to {len(fixed_records)} records")
    print(f"Saved to: {output_file}")

    return fixed_records


def update_manifest(count, output_file="data/latest/latest.jsonl"):
    """Update manifest with new count and SHA256"""

    # Calculate SHA256
    sha256_hash = hashlib.sha256()
    with open(output_file, "rb") as f:
        while chunk := f.read(4096):
            sha256_hash.update(chunk)

    manifest = {
        "count": count,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "schema_version": "1.0.0",
        "sha256": sha256_hash.hexdigest(),
        "description": "Influx dataset - high-signal X influencer index",
        "last_batch": "batch_28_missing_placeholders_complete",
        "quality_gates": "strict_compliance",
    }

    with open("data/latest/manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(
        f"Updated manifest: {count} records, SHA256: {sha256_hash.hexdigest()[:16]}..."
    )


def main():
    import sys

    # Use command line args or defaults
    input_file = sys.argv[1] if len(sys.argv) > 1 else "data/latest/latest.jsonl"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "data/latest/latest_fixed.jsonl"

    # Add meta.score
    add_meta_score(input_file, output_file)

    # Replace original if working on main dataset
    if input_file == "data/latest/latest.jsonl":
        import shutil

        shutil.move(output_file, input_file)
        final_file = input_file
    else:
        final_file = output_file

    # Update manifest
    with open(final_file, "r") as f:
        count = sum(1 for line in f if line.strip())

    update_manifest(count, final_file)
    print("✅ Added meta.score and updated manifest")


if __name__ == "__main__":
    main()
