import json
import hashlib

def calculate_provenance_hash(record):
    """Calculate SHA-256 hash for record provenance"""
    key_fields = f"{record['id']}{record['followers_count']}{record['meta']['score']}{record['handle']}"
    return hashlib.sha256(key_fields.encode()).hexdigest()

# Load main dataset (use original cleaned dataset)
with open('data/latest/latest.jsonl', 'r') as f:
    main_records = [json.loads(line) for line in f if line.strip()]

# Load m12 batch data
with open('.cccc/work/m12_final.jsonl', 'r') as f:
    m12_records = [json.loads(line) for line in f if line.strip()]

print(f"Main dataset: {len(main_records)} records")
print(f"M12 batch: {len(m12_records)} records")

# Check for duplicates by ID and handle
existing_ids = {r['id'] for r in main_records}
existing_handles = {r['handle'] for r in main_records}
new_records = []

for record in m12_records:
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

# Show progress toward 400 target
remaining_needed = max(0, 400 - len(merged_records))
print(f"\nProgress toward 400 target:")
print(f"  Current: {len(merged_records)} authors")
print(f"  Needed: {remaining_needed} more authors")
print(f"  Progress: {len(merged_records)/400*100:.1f}%")

# Show m12 authors added by score
if new_records:
    print(f"\nM12 authors added (sorted by score):")
    m12_sorted = sorted(new_records, key=lambda r: r['meta']['score'], reverse=True)
    for i, record in enumerate(m12_sorted, 1):
        print(f"  {i:2d}. @{record['handle']:<15} {record['meta']['score']:5.1f} ({record['followers_count']:>6} followers)")

# Show overall top 15
print(f"\nTop 15 overall authors:")
for i, record in enumerate(merged_records[:15], 1):
    print(f"  {i:2d}. @{record['handle']:<20} {record['meta']['score']:5.1f} ({record['followers_count']:>8} followers)")

# Calculate how many more we need
print(f"\nRemaining to reach 400: {remaining_needed} authors")
if remaining_needed <= 30:
    print("✅ CLOSE TO TARGET! Need ~1 more batch")
elif remaining_needed <= 100:
    print("🔄 Good progress! Need 2-3 more batches")
else:
    print("📈 Need several more batches")
