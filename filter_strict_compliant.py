#!/usr/bin/env python3
"""
Filter out records that don't pass strict validation, keeping only compliant records.
"""

import json
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

def main():
    input_file = 'data/latest/latest.jsonl'
    output_file = 'data/latest/latest_strict_compliant.jsonl'
    
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        valid_count = 0
        filtered_count = 0
        total_count = len(lines)
        
        with open(output_file, 'w') as f:
            for line in lines:
                try:
                    record = json.loads(line.strip())
                    
                    # Apply strict validation filters
                    is_org = record.get('is_org', False)
                    is_official = record.get('is_official', False)
                    followers = record.get('followers_count', 0)
                    
                    # Filter rules
                    if is_org or is_official:
                        filtered_count += 1
                        continue
                    
                    if followers < 10000:  # Minimum follower count
                        filtered_count += 1
                        continue
                    
                    if not calculate_entry_threshold(record):
                        filtered_count += 1
                        continue
                    
                    # Record passes all filters - write it
                    f.write(json.dumps(record) + '\n')
                    valid_count += 1
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing line: {e}")
                    filtered_count += 1
                    continue
        
        print(f"Successfully processed {total_count} records")
        print(f"Valid records: {valid_count}")
        print(f"Filtered records: {filtered_count}")
        print(f"Output written to: {output_file}")
        
        # Update the main file with strict compliant data
        import shutil
        backup_file = f'data/latest/latest_backup_before_strict_filter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jsonl'
        shutil.copy2(input_file, backup_file)
        shutil.copy2(output_file, input_file)
        
        print(f"Backup created: {backup_file}")
        print(f"Main file updated with strict compliant data")
        
        return valid_count
        
    except FileNotFoundError:
        print(f"Error: Could not find input file {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
