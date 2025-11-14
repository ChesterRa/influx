import json
import hashlib

def calculate_provenance_hash(record):
    """Calculate SHA-256 hash for record provenance"""
    key_fields = f"{record['id']}{record['followers_count']}{record['meta']['score']}{record['handle']}"
    return hashlib.sha256(key_fields.encode()).hexdigest()

# Load main dataset
with open('data/latest/latest.jsonl', 'r') as f:
    main_records = [json.loads(line) for line in f if line.strip()]

# Load m13 batch data
with open('.cccc/work/m13_final.jsonl', 'r') as f:
    m13_records = [json.loads(line) for line in f if line.strip()]

print(f"Main dataset: {len(main_records)} records")
print(f"M13 batch: {len(m13_records)} records")

# Check for duplicates by ID
existing_ids = {r['id'] for r in main_records}
existing_handles = {r['handle'] for r in main_records}
new_records = []

for record in m13_records:
    if record['id'] not in existing_ids and record['handle'] not in existing_handles:
        # Calculate provenance hash
        record['meta']['provenance_hash'] = calculate_provenance_hash(record)
        new_records.append(record)
        existing_ids.add(record['id'])
        existing_handles.add(record['handle'])
    else:
        print(f"Skipping duplicate: @{record['handle']} (ID: {record['id']})")

print(f"New unique records: {len(new_records)}")

# Merge datasets
merged_records = main_records + new_records

# Sort by score (descending), then followers (descending), then handle (ascending)
merged_records.sort(key=lambda r: (-r['meta']['score'], -r['followers_count'], r['handle']))

print(f"Merged dataset: {len(merged_records)} records")

# Save merged dataset temporarily
with open('data/latest/latest_with_m13.jsonl', 'w') as f:
    for record in merged_records:
        f.write(json.dumps(record, separators=(',', ':')) + '\n')

print("Saved merged dataset to data/latest/latest_with_m13.jsonl")

# Show progress toward 400 target
remaining_needed = max(0, 400 - len(merged_records))
print(f"\nProgress toward 400 target:")
print(f"  Current: {len(merged_records)} authors")
print(f"  Needed: {remaining_needed} more authors")
print(f"  Progress: {len(merged_records)/400*100:.1f}%")

# Show top m13 authors by score
print(f"\nM13 authors added (sorted by score):")
m13_sorted = sorted(new_records, key=lambda r: r['meta']['score'], reverse=True)
for i, record in enumerate(m13_sorted, 1):
    print(f"  {i:2d}. @{record['handle']:<20} {record['meta']['score']:5.1f} ({record['followers_count']:>8} followers)")

# Show overall top 15
print(f"\nTop 15 overall authors:")
for i, record in enumerate(merged_records[:15], 1):
    print(f"  {i:2d}. @{record['handle']:<20} {record['meta']['score']:5.1f} ({record['followers_count']:>8} followers)")
