#!/usr/bin/env python3
import json
import hashlib
from datetime import datetime

def format_profile(profile, source_info):
    """Format Twitter profile data to influx schema"""
    handle = profile['username']
    followers = profile['public_metrics']['followers_count']
    verified = profile['verified']
    verified_type = profile['verified_type']
    
    # Entry threshold check
    entry_threshold_passed = (verified and followers >= 30000) or followers >= 50000
    
    # Basic quality score (placeholder until we have proper scoring)
    base_score = 20 * (followers / 1000)  # Log scale
    if verified:
        base_score += 5
    
    # Determine verification status
    if verified_type == 'blue':
        verified_status = 'blue'
    elif verified_type == 'business':
        verified_status = 'org'
    elif verified_type == 'none':
        verified_status = 'none'
    else:
        verified_status = 'legacy'
    
    # Create provenance hash
    provenance_data = f"{profile['id']}{followers}{datetime.utcnow().isoformat()}"
    provenance_hash = hashlib.sha256(provenance_data.encode()).hexdigest()
    
    return {
        "id": profile['id'],
        "handle": handle,
        "name": profile['name'],
        "verified": verified_status,
        "followers_count": followers,
        "is_org": verified_type == 'business',  # Business verified = org
        "is_official": False,  # Will refine with better heuristics
        "lang_primary": "en",  # Default assumption
        "topic_tags": [],  # Will add based on source
        "meta": {
            "score": round(min(base_score, 100), 1),
            "last_refresh_at": datetime.utcnow().isoformat() + "Z",
            "sources": [{
                "method": "rube_mcp_fetch",
                "fetched_at": datetime.utcnow().isoformat() + "Z",
                "evidence": f"@{handle}"
            }],
            "provenance_hash": provenance_hash,
            "entry_threshold_passed": entry_threshold_passed,
            # Add mock activity metrics (will be replaced with real data)
            "activity_metrics": {
                "account_created_at": profile['created_at'],
                "tweet_count": profile['public_metrics']['tweet_count'],
                "total_like_count": profile['public_metrics']['like_count'],
                "media_count": profile['public_metrics']['media_count'],
                "listed_count": profile['public_metrics']['listed_count'],
                "last_captured_at": datetime.utcnow().isoformat() + "Z"
            },
            "activity_score": round(min(40 + (profile['public_metrics']['tweet_count'] / 1000), 100), 1),
            "quality_score": 95 if verified else 75,  # Verified profiles get higher quality
            "relevance_score": 10,  # Base relevance
            "combined_score": round(min(base_score, 100), 1)
        }
    }

def main():
    # Load current dataset to check for duplicates
    current_handles = set()
    with open('data/latest/latest.jsonl', 'r') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                current_handles.add(data['handle'])
    
    print(f"Current dataset size: {len(current_handles)}")
    
    # Load fetched profile data
    with open('/home/user/.composio/mex/post.json', 'r') as f:
        m24_data = json.load(f)
        m24_profiles = m24_data['results'][0]['response']['data'].get('data', [])
    
    with open('/home/user/.composio/mex/rear.json', 'r') as f:
        major_data = json.load(f)
        major_profiles = major_data['results'][0]['response']['data'].get('data', [])
    
    # Process and filter qualified profiles
    formatted_profiles = []
    
    # Determine source for each handle based on our batch files
    m24_handles = {'DavidSacks', 'JeffBezos', 'VitalikButerin', 'jackconte'}
    major_handles = {'MarkRuffalo', 'arstechnica', 'CaseyNewton', 'davewiner', 'fredwilson', 
                   'Jason', 'jasonfried', 'karaswisher', 'profgalloway', 'sivers', 
                   'TechCrunch', 'timoreilly', 'verge', 'WIRED'}
    
    for profile in m24_profiles + major_profiles:
        followers = profile['public_metrics']['followers_count']
        verified = profile['verified']
        
        # Entry threshold: (verified=true AND followers>=30k) OR followers>=50k
        if (verified and followers >= 30000) or followers >= 50000:
            # Skip if already in dataset
            if profile['username'] not in current_handles:
                # Determine source and category
                handle = profile['username']
                if handle in m24_handles:
                    source_info = {"method": "m24_top_tier", "category": "tech_investor"}
                    topic_tags = ['tech_infra', 'venture_capital']
                elif handle in major_handles:
                    source_info = {"method": "major_influencers", "category": "tech_media"}
                    topic_tags = ['tech_media']
                else:
                    source_info = {"method": "rube_mcp_fetch", "category": "unknown"}
                    topic_tags = []
                
                formatted = format_profile(profile, source_info)
                formatted['topic_tags'] = topic_tags
                formatted_profiles.append(formatted)
    
    print(f"New qualified profiles to add: {len(formatted_profiles)}")
    
    # Display some sample profiles
    for i, profile in enumerate(formatted_profiles[:5]):
        print(f"\n{i+1}. {profile['handle']}:")
        print(f"   - Followers: {profile['followers_count']:,}")
        print(f"   - Verified: {profile['verified']}")
        print(f"   - Score: {profile['meta']['score']}")
        print(f"   - Entry threshold: {profile['meta']['entry_threshold_passed']}")
    
    # Save to file
    with open('tmp_new_high_value_profiles.jsonl', 'w') as f:
        for profile in formatted_profiles:
            f.write(json.dumps(profile) + '\n')
    
    print(f"\nSaved {len(formatted_profiles)} profiles to tmp_new_high_value_profiles.jsonl")

if __name__ == "__main__":
    main()
