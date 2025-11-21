#!/usr/bin/env python3
"""
Merge new author records into main dataset while ensuring deduplication and validation.
"""

import json
import hashlib
from datetime import datetime, timezone

def load_existing_handles():
    """Load set of existing handles to avoid duplicates."""
    handles = set()
    try:
        with open('data/latest/latest.jsonl', 'r') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    handles.add(record['handle'])
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print("Warning: No existing data file found")
    return handles

def merge_new_authors():
    """Merge new authors with existing dataset."""
    existing_handles = load_existing_handles()
    
    # Load new authors
    new_authors = []
    new_file = '.cccc/work/foreman/20251120-231500/m27_web3_authors.jsonl'
    
    with open(new_file, 'r') as f:
        for line in f:
            record = json.loads(line.strip())
            if record['handle'] not in existing_handles:
                new_authors.append(record)
                existing_handles.add(record['handle'])
    
    print(f"Found {len(new_authors)} new unique authors")
    
    # Read existing records
    existing_records = []
    with open('data/latest/latest.jsonl', 'r') as f:
        for line in f:
            existing_records.append(json.loads(line.strip()))
    
    # Combine and sort
    all_records = existing_records + new_authors
    
    # Sort by score (descending) then followers (descending)
    all_records.sort(key=lambda x: (-x['meta'].get('score', 0), -x['followers_count']))
    
    # Write combined file
    output_file = 'data/latest/latest.jsonl'
    backup_file = f'data/latest/latest_backup_before_merge_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jsonl'
    
    import shutil
    shutil.copy2(output_file, backup_file)
    
    with open(output_file, 'w') as f:
        for record in all_records:
            f.write(json.dumps(record) + '\n')
    
    print(f"Merged {len(new_authors)} new authors")
    print(f"Total authors: {len(all_records)}")
    print(f"Backup created: {backup_file}")
    
    return len(all_records)

def main():
    total_authors = merge_new_authors()
    
    # Validate merged data
    print("\nRunning validation on merged data...")
    result = __import__('subprocess').run([
        'python3', 'tools/influx-validate', 
        '--strict', 
        '-s', 'schema/bigv.schema.json', 
        '-m', 'data/latest/manifest.json', 
        'data/latest/latest.jsonl'
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    if result.returncode == 0:
        print("✅ Validation passed!")
        
        # Update manifest
        print("Updating manifest...")
        update_manifest(total_authors)
    else:
        print("❌ Validation failed - please check issues")
    
    return result.returncode == 0

def update_manifest(total_authors):
    """Update manifest with new count and SHA."""
    # Calculate new SHA
    sha256_hash = hashlib.sha256()
    with open('data/latest/latest.jsonl', 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    
    new_sha = sha256_hash.hexdigest()
    
    # Update manifest
    manifest = {
        "schema_version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "count": total_authors,
        "sha256": new_sha,
        "source_file": "data/latest/latest.jsonl",
        "sort_order": "score desc, followers_count desc, handle asc",
        "score_version": "v0_proxy_no_metrics",
        "score_formula": "20*log10(followers/1000) + verified_boost, clipped [0,100]",
        "score_note": "M0 proxy pending 30d metrics collection (M1)"
    }
    
    with open('data/latest/manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Manifest updated: {total_authors} authors, SHA: {new_sha[:16]}...")

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
