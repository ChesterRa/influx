#!/usr/bin/env python3
"""
Process RUBE MCP response data into influx schema format
"""

import json
import hashlib
from datetime import datetime, timezone

# RUBE MCP response data (extracted from successful call)
response_data = [
    {
        "created_at": "2006-08-05T23:31:27.000Z",
        "description": "first investor in https://t.co/M6cblbFld9 Host: @twistartups @theallinpod; I also invest in 100 startups a year @launch & @founderuni jason@calacanis.com for life",
        "id": "3840",
        "name": "@jason",
        "public_metrics": {
            "followers_count": 1034472,
            "following_count": 5738,
            "like_count": 118820,
            "listed_count": 16476,
            "media_count": 13478,
            "tweet_count": 64941,
        },
        "username": "Jason",
        "verified": False,
    },
    {
        "created_at": "2006-07-13T09:05:49.000Z",
        "description": "In love w/ @crystale & our 3 girls. Had fun on @ABCSharkTank.  Been working hard to unf**k planet at Lowercarbon.",
        "id": "586",
        "name": "Chris Sacca 🇺🇸",
        "public_metrics": {
            "followers_count": 1511968,
            "following_count": 958,
            "like_count": 337046,
            "listed_count": 11597,
            "media_count": 2098,
            "tweet_count": 77473,
        },
        "username": "sacca",
        "verified": False,
    },
    {
        "created_at": "2007-03-27T01:14:05.000Z",
        "description": "Founder and CEO, O'Reilly Media. Watching for alpha geeks, sharing their stories, helping future unfold. Didn't pay for a blue check, cannot make it go away",
        "id": "2384071",
        "name": "Tim O'Reilly",
        "public_metrics": {
            "followers_count": 1549297,
            "following_count": 2131,
            "like_count": 27240,
            "listed_count": 22971,
            "media_count": 798,
            "tweet_count": 47122,
        },
        "username": "timoreilly",
        "verified": False,
    },
    {
        "created_at": "2006-08-05T23:04:08.000Z",
        "description": "OG blogger, podcaster, developed first apps in many categories. \n\nhttps://t.co/6wu3TQYvJr\n\nIt's even worse than it appears. 😀",
        "id": "3839",
        "name": "Dave Winer",
        "public_metrics": {
            "followers_count": 64337,
            "following_count": 3653,
            "like_count": 18553,
            "listed_count": 4641,
            "media_count": 5771,
            "tweet_count": 215389,
        },
        "username": "davewiner",
        "verified": False,
    },
    {
        "created_at": "2007-03-25T20:44:33.000Z",
        "description": 'Author of "Useful Not True", "How to Live", "Hell Yeah or No". Former musician, circus performer, entrepreneur, and speaker. Everything is at https://t.co/fuY6AJRuz5',
        "id": "2206131",
        "name": "Derek Sivers",
        "public_metrics": {
            "followers_count": 282783,
            "following_count": 9125,
            "like_count": 111,
            "listed_count": 4185,
            "media_count": 172,
            "tweet_count": 9478,
        },
        "username": "sivers",
        "verified": False,
    },
    {
        "created_at": "2007-02-01T23:05:04.000Z",
        "description": "Incompressible",
        "id": "745273",
        "name": "Naval",
        "public_metrics": {
            "followers_count": 2947948,
            "following_count": 0,
            "like_count": 271431,
            "listed_count": 28487,
            "media_count": 310,
            "tweet_count": 26828,
        },
        "username": "naval",
        "verified": False,
    },
    {
        "created_at": "2013-11-06T12:51:04.000Z",
        "description": "Author of Network State. Founder of Network School.",
        "id": "2178012643",
        "name": "Balaji",
        "public_metrics": {
            "followers_count": 1221614,
            "following_count": 3920,
            "like_count": 241669,
            "listed_count": 18664,
            "media_count": 5367,
            "tweet_count": 30721,
        },
        "username": "balajis",
        "verified": False,
    },
    {
        "created_at": "2006-07-16T22:01:55.000Z",
        "description": "AI is cool i guess",
        "id": "1605",
        "name": "Sam Altman",
        "public_metrics": {
            "followers_count": 4137009,
            "following_count": 975,
            "like_count": 1019,
            "listed_count": 25313,
            "media_count": 375,
            "tweet_count": 7289,
        },
        "username": "sama",
        "verified": False,
    },
    {
        "created_at": "2007-03-14T04:14:58.000Z",
        "description": "Tech founder & investor. Personal views only. Official account: @davidsacks47",
        "id": "1137701",
        "name": "David Sacks",
        "public_metrics": {
            "followers_count": 1416528,
            "following_count": 3429,
            "like_count": 84018,
            "listed_count": 12052,
            "media_count": 1204,
            "tweet_count": 13655,
        },
        "username": "DavidSacks",
        "verified": False,
    },
    {
        "created_at": "2010-08-27T20:13:59.000Z",
        "description": "",
        "id": "183749519",
        "name": "Paul Graham",
        "public_metrics": {
            "followers_count": 2079579,
            "following_count": 780,
            "like_count": 146512,
            "listed_count": 19347,
            "media_count": 1748,
            "tweet_count": 50735,
        },
        "username": "paulg",
        "verified": False,
    },
    {
        "created_at": "2008-01-02T19:47:19.000Z",
        "description": "President & CEO @ycombinator —Founder @Initialized—designer/engineer who helps founders—SF Dem accelerating the boom loop—haters not allowed in my sauna",
        "id": "11768582",
        "name": "Garry Tan",
        "public_metrics": {
            "followers_count": 624280,
            "following_count": 5367,
            "like_count": 234280,
            "listed_count": 7197,
            "media_count": 3912,
            "tweet_count": 65901,
        },
        "username": "garrytan",
        "verified": False,
    },
    {
        "created_at": "2009-06-02T20:12:29.000Z",
        "description": "",
        "id": "44196397",
        "name": "Elon Musk",
        "public_metrics": {
            "followers_count": 229242264,
            "following_count": 1228,
            "like_count": 184224,
            "listed_count": 165327,
            "media_count": 4244,
            "tweet_count": 89611,
        },
        "username": "elonmusk",
        "verified": False,
    },
    {
        "created_at": "2006-03-21T20:50:14.000Z",
        "description": "no state is the best state",
        "id": "12",
        "name": "jack",
        "public_metrics": {
            "followers_count": 6362865,
            "following_count": 3,
            "like_count": 36486,
            "listed_count": 33018,
            "media_count": 2957,
            "tweet_count": 30191,
        },
        "username": "jack",
        "verified": False,
    },
]

# Convert to influx schema
records = []
for user in response_data:
    followers = user["public_metrics"]["followers_count"]
    verified = "blue" if user["verified"] else "none"

    # Apply entry threshold filter (50k followers)
    entry_pass = followers >= 50000
    if entry_pass:
        record = {
            "id": user["id"],
            "handle": user["username"],
            "name": user["name"],
            "verified": verified,
            "followers_count": followers,
            "is_org": False,
            "is_official": False,
            "lang_primary": "en",
            "topic_tags": ["vc_investing"],
            "meta": {
                "score": min(90, followers / 100000),  # Simple score based on followers
                "last_refresh_at": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
                "sources": [
                    {
                        "method": "rube_mcp_direct",
                        "fetched_at": datetime.now(timezone.utc)
                        .isoformat()
                        .replace("+00:00", "Z"),
                        "evidence": f"@{user['username']}",
                    }
                ],
                "provenance_hash": hashlib.sha256(
                    f"{user['id']}{followers}{datetime.now(timezone.utc).isoformat()}".encode()
                ).hexdigest()[:64],
                "entry_threshold_passed": True,
                "quality_score": min(90, followers / 100000),
            },
        }
        records.append(record)

print(
    f"Processed {len(records)} high-quality records from {len(response_data)} total users"
)

# Write to file
with open("data/tmp_m1_direct.jsonl", "w") as f:
    for record in records:
        f.write(json.dumps(record) + "\n")

print(f"Saved {len(records)} records to data/tmp_m1_direct.jsonl")
