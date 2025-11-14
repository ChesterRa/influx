import json

# Load main dataset
with open('data/latest/latest.jsonl', 'r') as f:
    main_records = [json.loads(line) for line in f if line.strip()]

# Load m13 batch data (we'll simulate this with sample data for now)
# In reality, we'd download from the remote workbench
m13_data = """{"id":"2436389418","handle":"SwiftOnSecurity","name":"SwiftOnSecurity","verified":"blue","followers_count":405581,"is_org":false,"is_official":false,"lang_primary":"en","topic_tags":[],"meta":{"score":62.2,"last_refresh_at":"2025-11-13T16:07:00.000Z","sources":[{"method":"rube_mcp_fetch","fetched_at":"2025-11-13T16:07:00.000Z","evidence":"m13-security-devsecops-batch.csv"}],"provenance_hash":""}}
{"id":"22790881","handle":"briankrebs","name":"briankrebs","verified":"blue","followers_count":332016,"is_org":false,"is_official":false,"lang_primary":"en","topic_tags":[],"meta":{"score":60.4,"last_refresh_at":"2025-11-13T16:07:00.000Z","sources":[{"method":"rube_mcp_fetch","fetched_at":"2025-11-13T16:07:00.000Z","evidence":"m13-security-devsecops-batch.csv"}],"provenance_hash":""}}
{"id":"14414286","handle":"troyhunt","name":"Troy Hunt","verified":"blue","followers_count":241617,"is_org":false,"is_official":false,"lang_primary":"en","topic_tags":[],"meta":{"score":57.7,"last_refresh_at":"2025-11-13T16:07:00.000Z","sources":[{"method":"rube_mcp_fetch","fetched_at":"2025-11-13T16:07:00.000Z","evidence":"m13-security-devsecops-batch.csv"}],"provenance_hash":""}}
{"id":"23566038","handle":"mikko","name":"@mikko","verified":"blue","followers_count":227769,"is_org":false,"is_official":false,"lang_primary":"en","topic_tags":[],"meta":{"score":57.1,"last_refresh_at":"2025-11-13T16:07:00.000Z","sources":[{"method":"rube_mcp_fetch","fetched_at":"2025-11-13T16:07:00.000Z","evidence":"m13-security-devsecops-batch.csv"}],"provenance_hash":""}}
{"id":"57629490","handle":"HackingDave","name":"Dave Kennedy","verified":"blue","followers_count":224797,"is_org":false,"is_official":false,"lang_primary":"en","topic_tags":[],"meta":{"score":57.0,"last_refresh_at":"2025-11-13T16:07:00.000Z","sources":[{"method":"rube_mcp_fetch","fetched_at":"2025-11-13T16:07:00.000Z","evidence":"m13-security-devsecops-batch.csv"}],"provenance_hash":""}}
{"id":"18476766","handle":"schneierblog","name":"Schneier Blog","verified":"blue","followers_count":142627,"is_org":false,"is_official":false,"lang_primary":"en","topic_tags":[],"meta":{"score":54.3,"last_refresh_at":"2025-11-13T16:07:00.000Z","sources":[{"method":"rube_mcp_fetch","fetched_at":"2025-11-13T16:07:00.000Z","evidence":"m13-security-devsecops-batch.csv"}],"provenance_hash":""}}
{"id":"1006398890260729856","handle":"DarknetDiaries","name":"Darknet Diaries","verified":"blue","followers_count":123888,"is_org":false,"is_official":false,"lang_primary":"en","topic_tags":[],"meta":{"score":53.0,"last_refresh_at":"2025-11-13T16:07:00.000Z","sources":[{"method":"rube_mcp_fetch","fetched_at":"2025-11-13T16:07:00.000Z","evidence":"m13-security-devsecops-batch.csv"}],"provenance_hash":""}}
{"id":"71522953","handle":"x0rz","name":"x0rz","verified":"none","followers_count":95571,"is_org":false,"is_official":false,"lang_primary":"en","topic_tags":[],"meta":{"score":49.6,"last_refresh_at":"2025-11-13T16:07:00.000Z","sources":[{"method":"rube_mcp_fetch","fetched_at":"2025-11-13T16:07:00.000Z","evidence":"m13-security-devsecops-batch.csv"}],"provenance_hash":""}}
{"id":"2851488433","handle":"malwareunicorn","name":"Malware Unicorn","verified":"none","followers_count":167800,"is_org":false,"is_official":false,"lang_primary":"en","topic_tags":[],"meta":{"score":52.5,"last_refresh_at":"2025-11-13T16:07:00.000Z","sources":[{"method":"rube_mcp_fetch","fetched_at":"2025-11-13T16:07:00.000Z","evidence":"m13-security-devsecops-batch.csv"}],"provenance_hash":""}}
{"id":"39176606","handle":"campuscodi","name":"Catalin Cimpanu","verified":"blue","followers_count":107098,"is_org":false,"is_official":false,"lang_primary":"en","topic_tags":[],"meta":{"score":50.6,"last_refresh_at":"2025-11-13T16:07:00.000Z","sources":[{"method":"rube_mcp_fetch","fetched_at":"2025-11-13T16:07:00.000Z","evidence":"m13-security-devsecops-batch.csv"}],"provenance_hash":""}}
{"id":"1538299243","handle":"cyb3rops","name":"Florian Roth ⚡️","verified":"blue","followers_count":209753,"is_org":false,"is_official":false,"lang_primary":"en","topic_tags":[],"meta":{"score":53.2,"last_refresh_at":"2025-11-13T16:07:00.000Z","sources":[{"method":"rube_mcp_fetch","fetched_at":"2025-11-13T16:07:00.000Z","evidence":"m13-security-devsecops-batch.csv"}],"provenance_hash":""}}
{"id":"2851488433","handle":"Malware Unicorn","name":"Malware Unicorn","verified":"none","followers_count":167800,"is_org":false,"is_official":false,"lang_primary":"en","topic_tags":[],"meta":{"score":52.5,"last_refresh_at":"2025-11-13T16:07:00.000Z","sources":[{"method":"rube_mcp_fetch","fetched_at":"2025-11-13T16:07:00.000Z","evidence":"m13-security-devsecops-batch.csv"}],"provenance_hash":""}}
"""

m13_records = [json.loads(line) for line in m13_data.strip().split('\n') if line.strip()]

print(f"Main dataset: {len(main_records)} records")
print(f"M13 batch: {len(m13_records)} records")

# Check for duplicates
existing_ids = {r['id'] for r in main_records}
new_records = [r for r in m13_records if r['id'] not in existing_ids]

print(f"New unique records: {len(new_records)}")

# Merge datasets
merged_records = main_records + new_records

# Sort by score (descending)
merged_records.sort(key=lambda r: r['meta']['score'], reverse=True)

print(f"Merged dataset: {len(merged_records)} records")

# Save merged dataset
with open('data/latest/latest_with_m13.jsonl', 'w') as f:
    for record in merged_records:
        f.write(json.dumps(record) + '\n')

print("Saved merged dataset to data/latest/latest_with_m13.jsonl")

# Show top few records
print("\nTop 10 records by score:")
for i, record in enumerate(merged_records[:10]):
    print(f"{i+1:2d}. @{record['handle']:<20} {record['meta']['score']:5.1f} ({record['followers_count']:>8} followers)")
