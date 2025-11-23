#!/usr/bin/env python3
"""
Process AI research batch data into influx schema format
"""

import json
import hashlib
from datetime import datetime, timezone

# RUBE MCP response data (extracted from successful call)
response_data = [
    {
        "created_at": "2009-04-21T06:49:15.000Z",
        "description": "Building @EurekaLabsAI. Previously Director of AI @ Tesla, founding team @ OpenAI, CS231n/PhD @ Stanford. I like to train large deep neural nets.",
        "id": "33836629",
        "name": "Andrej Karpathy",
        "public_metrics": {
            "followers_count": 1480964,
            "following_count": 1028,
            "like_count": 20840,
            "listed_count": 18547,
            "media_count": 829,
            "tweet_count": 9831,
        },
        "username": "karpathy",
        "verified": False,
    },
    {
        "created_at": "2009-06-17T16:05:51.000Z",
        "description": "Professor at NYU. Chief AI Scientist at Meta.\nResearcher in AI, Machine Learning, Robotics, etc.\nACM Turing Award Laureate.",
        "id": "48008938",
        "name": "Yann LeCun",
        "public_metrics": {
            "followers_count": 982802,
            "following_count": 766,
            "like_count": 25029,
            "listed_count": 13483,
            "media_count": 455,
            "tweet_count": 24259,
        },
        "username": "ylecun",
        "verified": False,
    },
    {
        "created_at": "2010-11-18T03:39:11.000Z",
        "description": "Co-Founder of Coursera; Stanford CS adjunct faculty. Former head of Baidu AI Group/Google Brain. #ai #machinelearning #deeplearning #MOOCs",
        "id": "216939636",
        "name": "Andrew Ng",
        "public_metrics": {
            "followers_count": 1294147,
            "following_count": 1047,
            "like_count": 1660,
            "listed_count": 16334,
            "media_count": 441,
            "tweet_count": 1954,
        },
        "username": "AndrewYNg",
        "verified": False,
    },
    {
        "created_at": "2009-08-25T17:09:25.000Z",
        "description": "Co-founder @ndea. Co-founder @arcprize. Creator of Keras and ARC-AGI. Author of 'Deep Learning with Python'.",
        "id": "68746721",
        "name": "François Chollet",
        "public_metrics": {
            "followers_count": 588218,
            "following_count": 820,
            "like_count": 10166,
            "listed_count": 8482,
            "media_count": 1444,
            "tweet_count": 24642,
        },
        "username": "fchollet",
        "verified": False,
    },
    {
        "created_at": "2014-11-10T11:05:07.000Z",
        "description": "Building @SakanaAILabs 🧠",
        "id": "2895499182",
        "name": "hardmaru",
        "public_metrics": {
            "followers_count": 369037,
            "following_count": 1772,
            "like_count": 144583,
            "listed_count": 4383,
            "media_count": 4435,
            "tweet_count": 25682,
        },
        "username": "hardmaru",
        "verified": False,
    },
    {
        "created_at": "2017-09-22T18:32:35.000Z",
        "description": "Chief Scientist, Google DeepMind & Google Research. Gemini Lead. Opinions stated here are my own, not those of Google. TensorFlow, MapReduce, Bigtable, ...",
        "id": "911297187664949248",
        "name": "Jeff Dean",
        "public_metrics": {
            "followers_count": 382697,
            "following_count": 6330,
            "like_count": 39854,
            "listed_count": 6366,
            "media_count": 491,
            "tweet_count": 8799,
        },
        "username": "JeffDean",
        "verified": False,
    },
    {
        "created_at": "2010-08-06T04:58:18.000Z",
        "description": "🇺🇸 Co-founder: @AnswerDotAI & @FastDotAI ;\nPrev: professor @ UQ; Stanford fellow; @kaggle president; @fastmail/@enlitic/etc founder\nhttps://t.co/16UBFTX7mo",
        "id": "175282603",
        "name": "Jeremy Howard",
        "public_metrics": {
            "followers_count": 265075,
            "following_count": 6195,
            "like_count": 10031,
            "listed_count": 5386,
            "media_count": 2877,
            "tweet_count": 64330,
        },
        "username": "jeremyphoward",
        "verified": False,
    },
    {
        "created_at": "2016-11-04T06:57:37.000Z",
        "description": "Sharing AI research. Early work on AI (GPT-J, LAION, scaling, MoE). Ex ML PhD (GT) & Google.",
        "id": "794433401591693312",
        "name": "Aran Komatsuzaki",
        "public_metrics": {
            "followers_count": 150937,
            "following_count": 315,
            "like_count": 15012,
            "listed_count": 1642,
            "media_count": 2525,
            "tweet_count": 6495,
        },
        "username": "arankomatsuzaki",
        "verified": False,
    },
    {
        "created_at": "2015-12-21T15:46:59.000Z",
        "description": "Researcher at Cursor\nhttps://t.co/cZl0wTfqGz",
        "id": "4558314927",
        "name": "Sasha Rush",
        "public_metrics": {
            "followers_count": 73199,
            "following_count": 498,
            "like_count": 4390,
            "listed_count": 1340,
            "media_count": 1090,
            "tweet_count": 8257,
        },
        "username": "srush_nlp",
        "verified": False,
    },
    {
        "created_at": "2008-06-24T23:57:41.000Z",
        "description": "Boston. Public. Art. Independent thinker + tweeter.",
        "id": "15225574",
        "name": "Goodfellow",
        "public_metrics": {
            "followers_count": 640,
            "following_count": 675,
            "like_count": 1399,
            "listed_count": 18,
            "media_count": 157,
            "tweet_count": 601,
        },
        "username": "Goodfellow",
        "verified": False,
    },
    {
        "created_at": "2023-09-14T11:28:02.000Z",
        "description": "",
        "id": "1702283007090917376",
        "name": "Ilya Sutskever",
        "public_metrics": {
            "followers_count": 53,
            "following_count": 1,
            "like_count": 0,
            "listed_count": 1,
            "media_count": 0,
            "tweet_count": 0,
        },
        "username": "ilyasutskever",
        "verified": False,
    },
    {
        "created_at": "2009-01-29T04:38:56.000Z",
        "description": "",
        "id": "19696232",
        "name": "EricJang",
        "public_metrics": {
            "followers_count": 18,
            "following_count": 9,
            "like_count": 0,
            "listed_count": 0,
            "media_count": 0,
            "tweet_count": 38,
        },
        "username": "EricJang",
        "verified": False,
    },
    {
        "created_at": "2010-07-02T19:38:09.000Z",
        "description": "President & Co-Founder @OpenAI",
        "id": "162124540",
        "name": "Greg Brockman",
        "public_metrics": {
            "followers_count": 879935,
            "following_count": 32,
            "like_count": 1770,
            "listed_count": 8876,
            "media_count": 412,
            "tweet_count": 5605,
        },
        "username": "gdb",
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
            "topic_tags": ["ai_research"],
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
with open("data/tmp_ai_research.jsonl", "w") as f:
    for record in records:
        f.write(json.dumps(record) + "\n")

print(f"Saved {len(records)} records to data/tmp_ai_research.jsonl")
