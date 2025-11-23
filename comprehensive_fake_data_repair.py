#!/usr/bin/env python3
"""
Comprehensive fake data repair - remove ALL types of fake data:
1. Entries with fake sequential provenance hashes (123456789...)
2. Entries that have been flagged as having fake metrics
3. Entries with placeholder metrics (5000/10000/500/1000 pattern)
4. Entries with placeholder IDs
"""

import json
import hashlib
from pathlib import Path

# Input/Output paths
input_file = Path("data/latest/latest.jsonl")
output_file = Path("data/latest/latest_comprehensive_clean.jsonl")
backup_file = Path("data/latest/latest_backup_before_comprehensive_clean.jsonl")

# Statistics
total_count = 0
removed_count = 0
kept_count = 0
reason_for_removal = []

# Create backup
if not backup_file.exists():
    print(f"Creating backup: {backup_file}")
    with open(input_file, 'r') as src, open(backup_file, 'w') as dst:
        dst.write(src.read())

print(f"Processing {input_file} → {output_file}")

def is_fake_data(data):
    """Check if data contains any fake patterns"""
    reasons = []
    
    # 1. Fake provenance hash pattern
    prov_hash = data.get('provenance_hash', '')
    if prov_hash and '1234567890' in prov_hash:
        reasons.append("fake_provenance_hash")
    
    # 2. Flagged fake metrics in sources
    sources = data.get('meta', {}).get('sources', [])
    for source in sources:
        if source.get('method') == 'fake_metrics_fix':
            reasons.append("fake_metrics_fix")
            break
    
    # 3. Placeholder metrics pattern
    activity_metrics = data.get('meta', {}).get('activity_metrics', {})
    if (activity_metrics.get('tweet_count') == 5000 and 
        activity_metrics.get('like_count') == 10000 and
        activity_metrics.get('media_count') == 500 and
        activity_metrics.get('listed_count') == 1000):
        reasons.append("placeholder_metrics")
    
    # 4. Placeholder ID pattern
    author_id = str(data.get('id', ''))
    if author_id.startswith('123456789'):
        reasons.append("placeholder_id")
    
    # 5. Short ID pattern (real Twitter IDs are much longer)
    if len(author_id) <= 8 and author_id.isdigit():
        reasons.append("short_fake_id")
    
    # 6. Suspicious name patterns matching handle exactly (fake placeholder)
    handle = data.get('handle', '')
    name = data.get('name', '')
    if handle and name and handle.lower() == name.lower() and len(handle) < 10:
        reasons.append("name_handle_match")
    
    return reasons

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        total_count += 1
        try:
            data = json.loads(line.strip())
            
            # Check for fake data patterns
            fake_reasons = is_fake_data(data)
            
            if fake_reasons:
                removed_count += 1
                handle = data.get('handle', 'unknown')
                for reason in fake_reasons:
                    reason_for_removal.append(f"{handle}:{reason}")
                continue
                
            # Keep valid entry
            outfile.write(line)
            kept_count += 1
            
        except json.JSONDecodeError:
            print(f"Error decoding line: {line}")
            continue

print(f"\n=== Comprehensive Fake Data Removal Summary ===")
print(f"Total entries processed: {total_count}")
print(f"Entries removed: {removed_count}")
print(f"Entries kept: {kept_count}")

if removed_count > 0:
    print(f"\nRemoval reasons:")
    from collections import Counter
    reason_counts = Counter(reason_for_removal)
    for reason, count in reason_counts.most_common():
        print(f"  {reason}: {count}")

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
manifest['last_updated'] = "2025-11-23T00:15:00Z"
manifest['total_authors'] = kept_count

# Add note about fake data removal
if 'notes' not in manifest:
    manifest['notes'] = []
manifest['notes'].append(f"Comprehensive clean: {removed_count} fake entries removed (provenance hashes, fake metrics, placeholder data)")

# Write updated manifest
with open(manifest_file, 'w') as f:
    json.dump(manifest, f, indent=2)

print("Manifest updated successfully!")
print(f"\nNext steps:")
print(f"1. Replace data/latest/latest.jsonl with data/latest/latest_comprehensive_clean.jsonl")
print(f"2. Run pipeline guard: ./scripts/pipeline_guard.sh data/latest/latest.jsonl data/latest/manifest.json schema/bigv.schema.json")
print(f"3. Validate: ./tools/influx-validate --strict -s schema/bigv.schema.json -m data/latest/manifest.json data/latest/latest.jsonl")
