
import json
import sys

def passes_entry_threshold_debug(user):
    verified = user.get('verified_type', 'none')
    followers = user.get('followers_count', 0)
    
    print(f'[THRESHOLD_DEBUG] User: {user.get("username")}, Followers: {followers:,}, Verified: {verified}')
    
    is_verified = verified in ['blue', 'org', 'legacy']
    verified_min = is_verified and followers >= 30000
    unverified_min = followers >= 50000
    result = verified_min or unverified_min
    
    print(f'[THRESHOLD_DEBUG] is_verified: {is_verified}, verified_min: {verified_min}, unverified_min: {unverified_min}, result: {result}')
    return result

# Load and test users
users = []
with open('m24_prefixed_users.jsonl', 'r') as f:
    for line in f:
        users.append(json.loads(line))

print(f'Testing {len(users)} users with threshold debug:')
passed_count = 0
for user in users:
    if passes_entry_threshold_debug(user):
        passed_count += 1

print(f'
Passed: {passed_count}/{len(users)}')
