#!/usr/bin/env python3
"""
Remove official/org accounts from dataset per strict validation rules
"""
import json
import sys
from pathlib import Path

def clean_dataset():
    input_file = Path('data/latest/latest.jsonl')
    output_file = Path('data/latest/latest_cleaned.jsonl')
    
    if not input_file.exists():
        print(f"ERROR: {input_file} not found")
        sys.exit(1)
    
    records = []
    removed_count = 0
    kept_count = 0
    
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            
            try:
                record = json.loads(line)
                
                # Filter out official/org accounts
                is_org = record.get('is_org', False)
                is_official = record.get('is_official', False)
                
                if is_org or is_official:
                    removed_count += 1
                    print(f"Removing official/org account: {record.get('handle', 'unknown')} (org={is_org}, official={is_official})")
                    continue
                
                # Apply entry threshold filter
                followers = record.get('followers_count', 0)
                verified = record.get('verified') in ['blue', 'org', 'legacy']
                
                # Entry threshold: (verified=true AND followers>=30k) OR followers>=50k
                if not ((verified and followers >= 30000) or followers >= 50000):
                    removed_count += 1
                    print(f"Removing below-threshold account: {record.get('handle', 'unknown')} ({followers} followers)")
                    continue
                
                records.append(record)
                kept_count += 1
                    
            except json.JSONDecodeError as e:
                print(f"ERROR parsing line {line_num}: {e}")
                continue
    
    print(f"\nSummary:")
    print(f"  Kept: {kept_count} records")
    print(f"  Removed: {removed_count} records")
    print(f"  Total processed: {kept_count + removed_count}")
    
    # Write cleaned data
    print(f"\nWriting {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, separators=(',', ':')) + '\n')
    
    print(f"✅ Cleaned {len(records)} records written to {output_file}")
    print(f"Next step: cp {output_file} data/latest/latest.jsonl")

if __name__ == '__main__':
    clean_dataset()
