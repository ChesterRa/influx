#!/usr/bin/env python3
import json
import math
from datetime import datetime

def calculate_quality_score(followers_count, verified):
    """Calculate quality score using the proxy formula"""
    verified_boost = {"blue": 10, "legacy": 5, "none": 0}.get(verified, 0)
    base_score = 20 * math.log10(max(followers_count / 1000, 0.1))  # Avoid log(0)
    quality_score = min(base_score + verified_boost, 100)  # Cap at 100
    return round(quality_score, 1)

def add_quality_fields():
    input_file = "/home/dodd/dev/influx/data/latest/latest.jsonl"
    output_file = "/home/dodd/dev/influx/data/latest/latest.jsonl"
    
    updated_records = []
    
    # Read all records
    with open(input_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                record = json.loads(line.strip())
                
                # Add entry_threshold_passed
                followers_count = record.get('followers_count', 0)
                record['entry_threshold_passed'] = followers_count >= 50000
                
                # Add quality_score
                verified = record.get('verified', 'none')
                record['quality_score'] = calculate_quality_score(followers_count, verified)
                
                updated_records.append(record)
                
                if line_num % 50 == 0:
                    print(f"Processed {line_num} records...")
                    
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
                continue
    
    # Write all records back to the same file
    with open(output_file, 'w') as f:
        for record in updated_records:
            f.write(json.dumps(record) + '\n')
    
    print(f"Updated {len(updated_records)} records with quality fields")
    
    # Print some statistics
    threshold_passed = sum(1 for r in updated_records if r.get('entry_threshold_passed', False))
    avg_score = sum(r.get('quality_score', 0) for r in updated_records) / len(updated_records)
    
    print(f"Records passing 50k threshold: {threshold_passed}/{len(updated_records)}")
    print(f"Average quality score: {avg_score:.1f}")
    
    # Show some examples
    print("\nExample records:")
    for i, record in enumerate(updated_records[:3]):
        print(f"  {i+1}. {record['handle']}: "
              f"followers={record['followers_count']:,}, "
              f"threshold_passed={record['entry_threshold_passed']}, "
              f"quality_score={record['quality_score']}")

if __name__ == "__main__":
    add_quality_fields()
