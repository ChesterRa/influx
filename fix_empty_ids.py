#!/usr/bin/env python3
"""
Remove entries with empty IDs (the remaining 12 fake entries)
"""

import json
import hashlib
from pathlib import Path

# Input/Output paths
input_file = Path("data/latest/latest.jsonl")
output_file = Path("data/latest/latest_empty_ids_removed.jsonl")
backup_file = Path("data/latest/latest_backup_before_empty_id_removal.jsonl")

# Statistics
total_count = 0
removed_count = 0
kept_count = 0

# Create backup
if not backup_file.exists():
    print(f"Creating backup: {backup_file}")
    with open(input_file, 'r') as src, open(backup_file, 'w') as dst:
        dst.write(src.read())

print(f"Processing {input_file} → {output_file}")
print("Removing entries with empty IDs...")

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        total_count += 1
        try:
            data = json.loads(line.strip())
            author_id = str(data.get('id', ''))
            
            # Remove entries with empty IDs
            if not author_id or not author_id.isdigit():
                removed_count += 1
                handle = data.get('handle', 'unknown')
                print(f"Removing entry with empty ID: {handle}")
                continue
                
            # Keep valid entry
            outfile.write(line)
            kept_count += 1
            
        except json.JSONDecodeError:
            print(f"Error decoding line: {line}")
            continue

print(f"\n=== Empty ID Removal Summary ===")
print(f"Total entries processed: {total_count}")
print(f"Entries removed: {removed_count}")
print(f"Entries kept: {kept_count}")

# Calculate new SHA256
print("\nCalculating new SHA256 for cleaned dataset...")
sha256_hash = hashlib.sha256()
with open(output_file, 'rb') as f:
    # Read and update hash in chunks of 4K
    for byte_block in iter(lambda: f.read(4096), b""):
        sha256_hash.update(byte_block)
new_sha = sha256_hash.hexdigest()
print(f"New SHA256: {new_sha}")

# Update manifest with new count and SHA256
manifest_file = Path("data/latest/manifest.json")
print(f"\nUpdating {manifest_file}...")

with open(manifest_file, 'r') as f:
    manifest = json.load(f)

# Update manifest fields
manifest['count'] = kept_count
manifest['sha256'] = new_sha
manifest['last_updated'] = "2025-11-23T00:30:00Z"
manifest['total_authors'] = kept_count

# Add note about empty ID removal
if 'notes' not in manifest:
    manifest['notes'] = []
manifest['notes'].append(f"{removed_count} entries with empty IDs removed")

# Write updated manifest
with open(manifest_file, 'w') as f:
    json.dump(manifest, f, indent=2)

print("Manifest updated successfully!")
print(f"\nNext steps:")
print(f"1. Replace data/latest/latest.jsonl with data/latest/latest_empty_ids_removed.jsonl")
print(f"2. Run pipeline guard: ./scripts/pipeline_guard.sh data/latest/latest.jsonl data/latest/manifest.json schema/bigv.schema.json")
print(f"3. Validate: ./tools/influx-validate --strict -s schema/bigv.schema.json -m data/latest/manifest.json data/latest/latest.jsonl")
