#!/usr/bin/env python3
"""
Deduplicate data/latest/latest.jsonl by keeping only the most recent version of each handle.
The most recent version is determined by last_refresh_at timestamp.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from datetime import datetime

def deduplicate_jsonl(input_file, output_file):
    """Remove duplicate handles, keeping the most recent version"""
    
    # Read all records
    records = []
    with open(input_file, 'r') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    print(f"Total records before deduplication: {len(records)}")
    
    # Group by handle
    handle_groups = defaultdict(list)
    for record in records:
        handle = record.get('handle')
        if handle:
            handle_groups[handle].append(record)
    
    # Find duplicates
    duplicates = {h: recs for h, recs in handle_groups.items() if len(recs) > 1}
    print(f"Found {len(duplicates)} handles with duplicates:")
    for handle, recs in duplicates.items():
        print(f"  - {handle}: {len(recs)} duplicates")
    
    # Keep only the most recent version for each handle
    deduped_records = []
    duplicates_removed = 0
    
    for handle, recs in handle_groups.items():
        if len(recs) == 1:
            deduped_records.append(recs[0])
        else:
            # Sort by last_refresh_at to find the most recent
            def get_timestamp(rec):
                ts = rec.get('meta', {}).get('last_refresh_at', '')
                if ts:
                    try:
                        return datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    except:
                        pass
                return datetime.min
            
            recs.sort(key=get_timestamp, reverse=True)
            deduped_records.append(recs[0])  # Keep the most recent
            duplicates_removed += len(recs) - 1
    
    print(f"Removed {duplicates_removed} duplicate records")
    print(f"Total records after deduplication: {len(deduped_records)}")
    
    # Write deduplicated data
    with open(output_file, 'w') as f:
        for record in deduped_records:
            f.write(json.dumps(record) + '\n')
    
    return len(deduped_records), duplicates_removed

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "data/latest/latest.jsonl"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "data/latest/latest_deduped.jsonl"
    
    # Create backup first
    backup_file = f"{input_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    Path(input_file).rename(backup_file)
    print(f"Created backup: {backup_file}")
    
    # Deduplicate
    final_count, removed_count = deduplicate_jsonl(backup_file, output_file)
    
    # Replace original
    Path(output_file).rename(input_file)
    print(f"Replaced original file with deduplicated version")
    
    print(f"\nSummary:")
    print(f"  Original records: {final_count + removed_count}")
    print(f"  Duplicates removed: {removed_count}")
    print(f"  Final records: {final_count}")
    print(f"  Backup saved: {backup_file}")
