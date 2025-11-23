#!/usr/bin/env python3
"""
Remove fake data records with empty/placeholder IDs from dataset.
This fixes the critical foreman requirement to eliminate all fake data.
"""
import json
import sys
import hashlib
from pathlib import Path

def remove_fake_data(input_path, output_path):
    """Remove records with empty/placeholder IDs."""
    fake_records = []
    valid_records = []
    
    with open(input_path, 'r') as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
                
            item = json.loads(line)
            item_id = str(item.get('id', ''))
            
            # Check for fake/placeholder IDs
            if item_id.startswith('1234567890000000') or not item_id.isdigit():
                fake_records.append((i, item.get('handle', 'N/A'), item_id))
                print(f"Removing fake record - Line {i}: Handle={item.get('handle', 'N/A')}, ID='{item_id}'")
            else:
                valid_records.append(item)
    
    print(f"\nSummary:")
    print(f"- Original records: {len(fake_records) + len(valid_records)}")
    print(f"- Fake records removed: {len(fake_records)}")
    print(f"- Valid records remaining: {len(valid_records)}")
    
    # Write cleaned data
    with open(output_path, 'w') as f:
        for item in valid_records:
            f.write(json.dumps(item) + '\n')
    
    # Calculate new hash
    with open(output_path, 'rb') as f:
        new_sha = hashlib.sha256(f.read()).hexdigest()
    
    print(f"- New SHA256: {new_sha}")
    
    return len(valid_records), new_sha, fake_records

if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'data/latest/latest.jsonl'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'data/latest/latest_cleaned.jsonl'
    
    if not Path(input_file).exists():
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)
    
    print("Removing fake data records...")
    count, sha, fake_records = remove_fake_data(input_file, output_file)
    
    if fake_records:
        print(f"\nAll {len(fake_records)} fake records have been removed.")
        print("Dataset is now clean and ready for validation.")
    else:
        print("\nNo fake records found.")
