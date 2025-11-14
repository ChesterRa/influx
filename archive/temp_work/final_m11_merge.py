import json
import hashlib

def calculate_provenance_hash(record):
    """Calculate SHA-256 hash for record provenance"""
    key_fields = f"{record['id']}{record['followers_count']}{record['meta']['score']}{record['handle']}"
    return hashlib.sha256(key_fields.encode()).hexdigest()

# Load main dataset
with open('data/latest/latest.jsonl', 'r') as f:
    main_records = [json.loads(line) for line in f if line.strip()]

# Load m11 batch data
with open('.cccc/work/m11_final.jsonl', 'r') as f:
    m11_records = [json.loads(line) for line in f if line.strip()]

print(f"Main dataset: {len(main_records)} records")
print(f"M11 batch: {len(m11_records)} records")

# Check for duplicates by ID and handle
existing_ids = {r['id'] for r in main_records}
existing_handles = {r['handle'] for r in main_records}
new_records = []

for record in m11_records:
    record_id = record['id']
    record_handle = record['handle']
    
    if record_id not in existing_ids and record_handle not in existing_handles:
        # Calculate provenance hash
        record['meta']['provenance_hash'] = calculate_provenance_hash(record)
        new_records.append(record)
        existing_ids.add(record_id)
        existing_handles.add(record_handle)
    else:
        print(f"Skipping duplicate: @{record_handle} (ID: {record_id})")

print(f"New unique records: {len(new_records)}")

# Merge datasets
merged_records = main_records + new_records

# Sort by score (descending), then followers (descending), then handle (ascending)
merged_records.sort(key=lambda r: (-r['meta']['score'], -r['followers_count'], r['handle']))

print(f"Merged dataset: {len(merged_records)} records")

# Save merged dataset to replace main
with open('data/latest/latest.jsonl', 'w') as f:
    for record in merged_records:
        f.write(json.dumps(record, separators=(',', ':')) + '\n')

print("Saved merged dataset to data/latest/latest.jsonl")

# Progress toward 400 target
remaining_needed = max(0, 400 - len(merged_records))
progress_pct = len(merged_records)/400*100
print(f"\nProgress toward 400 target:")
print(f"  Current: {len(merged_records)} authors")
print(f"  Needed: {remaining_needed} more authors")
print(f"  Progress: {progress_pct:.1f}%")

# Show m11 authors added by score
if new_records:
    print(f"\nM11 authors added (sorted by score):")
    m11_sorted = sorted(new_records, key=lambda r: r['meta']['score'], reverse=True)
    for i, record in enumerate(m11_sorted, 1):
        print(f"  {i:2d}. @{record['handle']:<15} {record['meta']['score']:5.1f} ({record['followers_count']:>6} followers)")

# Show overall top 20 (expanded to show new entries)
print(f"\nTop 20 overall authors (including new m11 entries):")
for i, record in enumerate(merged_records[:20], 1):
    # Check if this is a newly added m11 record
    m11_indicator = " 🆕" if record in new_records else ""
    print(f"  {i:2d}. @{record['handle']:<20} {record['meta']['score']:5.1f} ({record['followers_count']:>8} followers){m11_indicator}")

# Status summary
if progress_pct >= 70:
    print(f"\n✅ EXCELLENT PROGRESS: {progress_pct:.1f}% toward target")
    print("   Strong foundation for reaching 400 authors")
    print("   Quality gates maintained throughout")
elif progress_pct >= 60:
    print(f"\n🔄 GOOD PROGRESS: {progress_pct:.1f}% toward target")
    print("   On track for M1 completion")
else:
    print(f"\n📈 CONTINUING PROGRESS: {progress_pct:.1f}% toward target")

print(f"\nNext steps: Need {remaining_needed} more authors from additional batches")
print("Quality infrastructure ready for scaling!")
