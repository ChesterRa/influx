#!/usr/bin/env python3
"""Update manifest with new count and timestamp"""

import json
import hashlib
from datetime import datetime

def main():
    # Read current dataset
    with open('data/latest/latest.jsonl', 'r') as f:
        lines = f.readlines()

    # Calculate hash
    content = ''.join(lines)
    sha256_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

    # Update manifest
    manifest = {
        "schema_version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + '+00:00',
        "count": len(lines),
        "sha256": sha256_hash,
        "source_file": "data/latest/latest.jsonl",
        "sort_order": "score desc, followers_count desc, handle asc",
        "score_version": "v0_proxy_no_metrics",
        "score_formula": "20*log10(followers/1000) + verified_boost, clipped [0,100]",
        "score_note": "M0 proxy pending 30d metrics collection (M1)"
    }

    with open('data/latest/manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"Updated manifest: count={len(lines)}, sha256={sha256_hash[:16]}...")

if __name__ == '__main__':
    main()