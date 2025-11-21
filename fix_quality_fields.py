#!/usr/bin/env python3
"""
Fix missing required fields (entry_threshold_passed, quality_score) in existing data.
This script processes the current latest.jsonl and adds the missing fields to make
the data compliant with strict validation.
"""

import json
import hashlib
import sys
from datetime import datetime, timezone

def calculate_entry_threshold(record):
    """Calculate if record passes entry threshold based on current rules."""
    followers = record.get('followers_count', 0)
    verified = record.get('verified', 'none')
    is_org = record.get('is_org', False)
    is_official = record.get('is_official', False)
    
    # Entry threshold rules:
    # (verified=true AND followers>=30k) OR followers>=50k
    # AND not org/official
    if is_org or is_official:
        return False
    
    if verified in ['blue', 'org', 'legacy', 'business'] and followers >= 30000:
        return True
    elif followers >= 50000:
        return True
    
    return False

def calculate_quality_score(record):
    """Calculate quality score based on available metrics."""
    followers = record.get('followers_count', 0)
    verified = record.get('verified', 'none')
    is_org = record.get('is_org', False)
    is_official = record.get('is_official', False)
    
    # Base penalty for org/official accounts
    if is_org or is_official:
        return 0.0
    
    # Quality score based on followers and verification
    score = 0.0
    
    # Follower component (0-70 points)
    if followers >= 1000000:
        score += 70
    elif followers >= 500000:
        score += 60
    elif followers >= 100000:
        score += 50
    elif followers >= 50000:
        score += 40
    elif followers >= 30000:
        score += 30
    elif followers >= 10000:
        score += 20
    
    # Verification boost (0-30 points)
    if verified in ['blue', 'org', 'legacy', 'business']:
        score += 30
    else:
        score += 10  # Small boost for unverified but might be legitimate
    
    return min(score, 100.0)

def update_provenance_hash(record):
    """Update provenance hash with current record state."""
    # Create hash from key fields
    hash_data = f"{record['id']}|{record['followers_count']}|{record['handle']}|{record['name']}"
    if 'last_refresh_at' in record.get('meta', {}):
        hash_data += f"|{record['meta']['last_refresh_at']}"
    
    return hashlib.sha256(hash_data.encode('utf-8')).hexdigest()

def main():
    input_file = 'data/latest/latest.jsonl'
    output_file = 'data/latest/latest_fixed.jsonl'
    
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        updated_count = 0
        with open(output_file, 'w') as f:
            for line in lines:
                try:
                    record = json.loads(line.strip())
                    
                    # Update meta object
                    meta = record.get('meta', {})
                    
                    # Add missing required fields
                    meta['entry_threshold_passed'] = calculate_entry_threshold(record)
                    meta['quality_score'] = calculate_quality_score(record)
                    
                    # Update provenance hash
                    meta['provenance_hash'] = update_provenance_hash(record)
                    
                    # Ensure timestamp
                    if 'last_refresh_at' not in meta:
                        meta['last_refresh_at'] = datetime.now(timezone.utc).isoformat()
                    
                    record['meta'] = meta
                    
                    # Write updated record
                    f.write(json.dumps(record) + '\n')
                    updated_count += 1
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing line: {e}")
                    continue
        
        print(f"Successfully updated {updated_count} records")
        print(f"Output written to: {output_file}")
        
        # Backup and replace
        import shutil
        backup_file = f'data/latest/latest_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jsonl'
        shutil.copy2(input_file, backup_file)
        shutil.copy2(output_file, input_file)
        
        print(f"Backup created: {backup_file}")
        print(f"Original file updated with fixes")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
