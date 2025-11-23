#!/usr/bin/env python3
"""
Foreman Task: Fake Data Crisis Cleanup
Removes official accounts and any fake/placeholder data from Influx dataset
"""

import json
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Set

def load_jsonl(file_path: str) -> List[Dict]:
    """Load JSONL file"""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {file_path}: {e}", file=sys.stderr)
        sys.exit(1)
    return data

def save_jsonl(data: List[Dict], file_path: str) -> None:
    """Save JSONL file"""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def compute_sha256_jsonl(data: List[Dict]) -> str:
    """Compute SHA256 hash of JSONL data"""
    content = '\n'.join(json.dumps(item, ensure_ascii=False, sort_keys=True) for item in data)
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def is_fake_data(record: Dict) -> tuple[bool, str]:
    """Check if record is fake/contaminated data"""
    
    # STRICT: Official accounts not allowed
    if record.get('is_official') is True:
        return True, "Official account (is_official=true)"
    
    # STRICT: Org accounts not allowed
    if record.get('is_org') is True:
        return True, "Org account (is_org=true)"
    
    # Check for placeholder/fake IDs
    author_id = record.get('id', '')
    if author_id and all(c == '0' for c in str(author_id)):
        return True, f"Placeholder ID: {author_id}"
    
    # Check for test/mock handles
    handle = record.get('handle', '').lower()
    fake_patterns = ['test_', 'mock_', 'placeholder_', 'fake_', 'tmp_', 'temp_']
    if any(handle.startswith(pattern) for pattern in fake_patterns):
        return True, f"Test/Mock handle: {handle}"
    
    # Check for missing critical fields
    required_fields = ['id', 'handle', 'name', 'followers_count']
    for field in required_fields:
        if not record.get(field):
            return True, f"Missing required field: {field}"
    
    # Check for invalid followers count
    followers = record.get('followers_count', 0)
    if not isinstance(followers, int) or followers < 0:
        return True, f"Invalid followers count: {followers}"
    
    # Check for fake follower patterns (ending with 000)
    if followers > 0 and str(followers).endswith('000') and followers >= 1000:
        return True, f"Suspicious followers count ending with 000: {followers}"
    
    return False, ""

def filter_dataset(data: List[Dict]) -> tuple[List[Dict], List[Dict]]:
    """Filter out fake/contaminated records"""
    clean_data = []
    fake_data = []
    
    for record in data:
        is_fake, reason = is_fake_data(record)
        if is_fake:
            record['removal_reason'] = reason
            fake_data.append(record)
        else:
            clean_data.append(record)
    
    return clean_data, fake_data

def update_manifest(manifest_path: str, new_count: int, new_sha256: str) -> None:
    """Update manifest with new count and SHA256"""
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except FileNotFoundError:
        print(f"WARNING: Manifest not found: {manifest_path}", file=sys.stderr)
        manifest = {}
    
    manifest.update({
        'count': new_count,
        'sha256': new_sha256,
        'timestamp': '2025-11-23T05:30:00Z',  # Current timestamp
        'score_version': 'v0_proxy_no_metrics',
        'score_formula': '20*log10(followers/1000) + verified_boost, clipped [0,100]',
        'score_note': 'M0 proxy pending 30d metrics collection (M1) - CLEANED'
    })
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 foreman_fake_data_cleanup.py <input.jsonl> <manifest.json>", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    manifest_file = sys.argv[2]
    
    print("🔍 FOREMAN TASK: Fake Data Crisis Cleanup")
    print("=" * 50)
    
    # Load current data
    print(f"📂 Loading dataset: {input_file}")
    data = load_jsonl(input_file)
    print(f"📊 Initial record count: {len(data)}")
    
    # Filter fake data
    print("🧹 Filtering fake/contaminated records...")
    clean_data, fake_data = filter_dataset(data)
    
    print(f"✅ Clean records: {len(clean_data)}")
    print(f"❌ Fake records removed: {len(fake_data)}")
    
    # Print removal reasons
    if fake_data:
        print("\n📋 Removal Summary:")
        reasons = {}
        for record in fake_data:
            reason = record.get('removal_reason', 'Unknown')
            reasons[reason] = reasons.get(reason, 0) + 1
        
        for reason, count in sorted(reasons.items()):
            print(f"  • {reason}: {count}")
        
        # Save removed records for audit
        backup_file = input_file.replace('.jsonl', '.removed_fake.jsonl')
        save_jsonl(fake_data, backup_file)
        print(f"\n💾 Removed records saved to: {backup_file}")
    
    # Compute new hash
    new_sha256 = compute_sha256_jsonl(clean_data)
    print(f"🔐 New SHA256: {new_sha256[:16]}...")
    
    # Save clean data
    temp_file = input_file.replace('.jsonl', '.cleaned.jsonl')
    save_jsonl(clean_data, temp_file)
    print(f"💾 Clean data saved to: {temp_file}")
    
    # Update manifest
    update_manifest(manifest_file, len(clean_data), new_sha256)
    print(f"📄 Manifest updated: {manifest_file}")
    
    # Quality check
    print("\n✅ QUALITY CHECK:")
    official_count = sum(1 for r in clean_data if r.get('is_official') is True)
    org_count = sum(1 for r in clean_data if r.get('is_org') is True)
    
    print(f"  • Official accounts: {official_count} (MUST BE 0)")
    print(f"  • Org accounts: {org_count} (MUST BE 0)")
    print(f"  • Clean records: {len(clean_data)}")
    print(f"  • Fake removed: {len(fake_data)}")
    
    if official_count == 0 and org_count == 0 and len(fake_data) > 0:
        print("\n🎉 FAKE DATA CRISIS RESOLVED!")
        print("Dataset is now 100% compliant with strict validation.")
        return 0
    else:
        print("\n⚠️  Issues remain - manual review required.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
