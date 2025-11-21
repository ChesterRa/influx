#!/usr/bin/env python3
"""
Rebuild manifest.json with correct count, SHA, and metadata
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

def calculate_file_sha256(filepath):
    """Calculate SHA256 hash of file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def count_records(filepath):
    """Count non-empty lines in JSONL file"""
    count = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                count += 1
    return count

def rebuild_manifest():
    data_file = Path('data/latest/latest.jsonl')
    manifest_file = Path('data/latest/manifest.json')
    
    if not data_file.exists():
        print(f"ERROR: {data_file} not found")
        return False
    
    # Calculate file metrics
    record_count = count_records(data_file)
    file_sha256 = calculate_file_sha256(data_file)
    
    # Create manifest
    manifest = {
        "schema_version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "count": record_count,
        "sha256": file_sha256,
        "source_file": "data/latest/latest.jsonl",
        "sort_order": "score desc, followers_count desc, handle asc",
        "score_version": "v0_proxy_no_metrics",
        "score_formula": "20*log10(followers/1000) + verified_boost, clipped [0,100]",
        "score_note": "M1 manual expansion - proxy scoring pending 30d metrics collection (M2)"
    }
    
    # Write manifest
    print(f"Writing manifest with {record_count} records...")
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, separators=(',', ': '))
    
    print(f"✅ Manifest rebuilt:")
    print(f"  Records: {record_count}")
    print(f"  SHA256: {file_sha256}")
    print(f"  File: {manifest_file}")
    
    return True

if __name__ == '__main__':
    rebuild_manifest()
