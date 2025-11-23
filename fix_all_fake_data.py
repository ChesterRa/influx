#!/usr/bin/env python3
"""
Fix all fake data entries from dataset
Remove any entries with rube_* IDs or other fake data patterns
"""

import json
import hashlib
import sys
from pathlib import Path

def generate_provenance_hash(record):
    """Generate SHA256 provenance hash for a record"""
    hash_str = f"{record['id']}{record['followers_count']}{record.get('last_active_at', '')}"
    return hashlib.sha256(hash_str.encode()).hexdigest()

def is_fake_data(record):
    """Check if a record contains fake data"""
    # Check for rube_* IDs
    if record.get('id', '').startswith('rube_'):
        return True
    
    # Check for placeholder follower counts ending in 000
    followers = record.get('followers_count', 0)
    if followers > 0 and str(followers).endswith('000'):
        # Only flag as fake if significant (>10k) and has other fake patterns
        if followers > 10000:
            # Additional checks for fake data patterns
            if (record.get('tweet_count', 0) == 0 and 
                record.get('created_at', '').endswith('2023-01-01T00:00:00.000Z')):
                return True
    
    return False

def main():
    input_file = Path('data/latest/latest.jsonl')
    output_file = Path('data/latest/latest_fixed.jsonl')
    backup_file = Path('data/latest/latest_backup_before_fix.jsonl')
    
    # Create backup
    if input_file.exists():
        with open(input_file, 'r') as f_in, open(backup_file, 'w') as f_backup:
            f_backup.write(f_in.read())
        print(f"Created backup: {backup_file}")
    
    # Process records
    cleaned_records = []
    fake_count = 0
    
    with open(input_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
                
            try:
                record = json.loads(line)
                
                if is_fake_data(record):
                    fake_count += 1
                    print(f"Removed fake data: line {line_num}, id={record.get('id')}, handle={record.get('handle')}")
                    continue
                
                # Update provenance hash
                if 'provenance_hash' in record:
                    record['provenance_hash'] = generate_provenance_hash(record)
                
                cleaned_records.append(record)
                
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
                continue
    
    # Write cleaned data
    with open(output_file, 'w') as f_out:
        for record in cleaned_records:
            f_out.write(json.dumps(record) + '\n')
    
    print(f"\nSummary:")
    print(f"- Original records: {fake_count + len(cleaned_records)}")
    print(f"- Fake records removed: {fake_count}")
    print(f"- Clean records: {len(cleaned_records)}")
    print(f"- Output file: {output_file}")
    
    # Verify no fake data remains
    remaining_fake = sum(1 for record in cleaned_records if is_fake_data(record))
    if remaining_fake > 0:
        print(f"WARNING: {remaining_fake} fake records still remain!")
        sys.exit(1)
    
    print("✅ All fake data successfully removed!")

if __name__ == '__main__':
    main()
