#!/usr/bin/env python3
"""
Replace mock M1 data with real Twitter data
"""

import json
import hashlib
from datetime import datetime

# Real data from Twitter API
real_data = {
    "jason": {
        "id": "3840",
        "name": "@jason",
        "username": "Jason",
        "verified": "blue",
        "verified_type": "blue",
        "description": "first investor in https://t.co/M6cblbFld9 Host: @twistartups @theallinpod; I also invest in 100 startups a year @launch & @founderuni jason@calacanis.com for life",
        "created_at": "2006-08-05T23:31:27.000Z",
        "followers_count": 1034455,
        "public_metrics": {
            "followers_count": 1034455,
            "following_count": 5738,
            "like_count": 118819,
            "listed_count": 16476,
            "media_count": 13478,
            "tweet_count": 64940,
        },
    },
    "sacca": {
        "id": "586",
        "name": "Chris Sacca 🇺🇸",
        "username": "sacca",
        "verified": "blue",
        "verified_type": "blue",
        "description": "In love w/ @crystale & our 3 girls. Had fun on @ABCSharkTank.  Been working hard to unf**k the planet at Lowercarbon.",
        "created_at": "2006-07-13T09:05:49.000Z",
        "followers_count": 1511971,
        "public_metrics": {
            "followers_count": 1511971,
            "following_count": 958,
            "like_count": 337046,
            "listed_count": 11597,
            "media_count": 2098,
            "tweet_count": 77474,
        },
    },
    "leerobinson": {
        "id": "22008252",
        "name": "Lee Robinson",
        "username": "LeeRobinson",
        "verified": "none",
        "verified_type": "none",
        "description": "",
        "created_at": "2009-02-26T13:32:52.000Z",
        "followers_count": 34,
        "public_metrics": {
            "followers_count": 34,
            "following_count": 125,
            "like_count": 0,
            "listed_count": 0,
            "media_count": 0,
            "tweet_count": 0,
        },
    },
    "jerryneumann": {
        "id": "385704320",
        "name": "Jerry Neumann",
        "username": "JerryNeumann",
        "verified": "none",
        "verified_type": "none",
        "description": "",
        "created_at": "2011-10-05T23:52:52.000Z",
        "followers_count": 3,
        "public_metrics": {
            "followers_count": 3,
            "following_count": 0,
            "like_count": 0,
            "listed_count": 0,
            "media_count": 0,
            "tweet_count": 1,
        },
    },
    "timoreilly": {
        "id": "2384071",
        "name": "Tim O'Reilly",
        "username": "timoreilly",
        "verified": "blue",
        "verified_type": "blue",
        "description": "Founder and CEO, O'Reilly Media. Watching the alpha geeks, sharing their stories, helping the future unfold. Didn't pay for a blue check, cannot make it go away",
        "created_at": "2007-03-27T01:14:05.000Z",
        "followers_count": 1549296,
        "public_metrics": {
            "followers_count": 1549296,
            "following_count": 2131,
            "like_count": 27240,
            "listed_count": 22972,
            "media_count": 798,
            "tweet_count": 47122,
        },
    },
    "davewiner": {
        "id": "3839",
        "name": "Dave Winer",
        "username": "davewiner",
        "verified": "blue",
        "verified_type": "blue",
        "description": "OG blogger, podcaster, developed first apps in many categories. \n\nhttps://t.co/6wu3TQYvJr\n\nIt's even worse than it appears. 😀",
        "created_at": "2006-08-05T23:04:08.000Z",
        "followers_count": 64336,
        "public_metrics": {
            "followers_count": 64336,
            "following_count": 3653,
            "like_count": 18553,
            "listed_count": 4641,
            "media_count": 5771,
            "tweet_count": 215389,
        },
    },
    "jasoncalacanis": {
        "id": "1004",
        "name": "JasonMC",
        "username": "Jasoncalacanis",
        "verified": "none",
        "verified_type": "none",
        "description": "My new account is @jason, this is my backup account. if I ever get banned or hacked I will be here. 🦄",
        "created_at": "2006-07-15T09:04:54.000Z",
        "followers_count": 6308,
        "public_metrics": {
            "followers_count": 6308,
            "following_count": 27,
            "like_count": 104,
            "listed_count": 721,
            "media_count": 6,
            "tweet_count": 847,
        },
    },
    "sivers": {
        "id": "2206131",
        "name": "Derek Sivers",
        "username": "sivers",
        "verified": "blue",
        "verified_type": "blue",
        "description": 'Author of "Useful Not True", "How to Live", "Hell Yeah or No". Former musician, circus performer, entrepreneur, and speaker. Everything is at https://t.co/fuY6AJRuz5',
        "created_at": "2007-03-25T20:44:33.000Z",
        "followers_count": 282785,
        "public_metrics": {
            "followers_count": 282785,
            "following_count": 9125,
            "like_count": 111,
            "listed_count": 4186,
            "media_count": 172,
            "tweet_count": 9478,
        },
    },
    "fried": {
        "id": "245387878",
        "name": "Fried Investment Group",
        "username": "fried",
        "verified": "blue",
        "verified_type": "blue",
        "description": "Fried LLC is a privately held alternative investment firm founded by serial entrepreneur and investor @JordanFried",
        "created_at": "2011-01-31T15:46:21.000Z",
        "followers_count": 525,
        "public_metrics": {
            "followers_count": 525,
            "following_count": 1,
            "like_count": 388,
            "listed_count": 16,
            "media_count": 0,
            "tweet_count": 15,
        },
    },
    "amywebb": {
        "id": "9500242",
        "name": "Amy Webb 🤷🏻‍♀️",
        "username": "amywebb",
        "verified": "blue",
        "verified_type": "blue",
        "description": "CEO of FTSG. Quantitative Futurist. Prof @NYUStern. 4x bestselling author. Competitive cyclist.",
        "created_at": "2007-10-17T14:50:09.000Z",
        "followers_count": 72750,
        "public_metrics": {
            "followers_count": 72750,
            "following_count": 2871,
            "like_count": 13931,
            "listed_count": 2366,
            "media_count": 6202,
            "tweet_count": 40751,
        },
    },
    "caseynewton": {
        "id": "69426451",
        "name": "Casey Newton",
        "username": "CaseyNewton",
        "verified": "blue",
        "verified_type": "blue",
        "description": "Writing @platformer. Co-hosting Hard Fork @nytimes. Posting good tweets to Instagram stories @crumbler. casey@platformer.news | https://t.co/9KuJb8XCrr",
        "created_at": "2009-08-27T22:37:09.000Z",
        "followers_count": 199842,
        "public_metrics": {
            "followers_count": 199842,
            "following_count": 964,
            "like_count": 204301,
            "listed_count": 4227,
            "media_count": 1016,
            "tweet_count": 10053,
        },
    },
    "karaswisher": {
        "id": "5763262",
        "name": "Kara Swisher",
        "username": "karaswisher",
        "verified": "blue",
        "verified_type": "blue",
        "description": '"Vitriolic" and now "shrill"media lady, though dogs can hear me loud and clear',
        "created_at": "2007-05-04T10:32:22.000Z",
        "followers_count": 1448325,
        "public_metrics": {
            "followers_count": 1448325,
            "following_count": 2161,
            "like_count": 108825,
            "listed_count": 15371,
            "media_count": 1988,
            "tweet_count": 33350,
        },
    },
    "profgalloway": {
        "id": "9273802",
        "name": "Scott Galloway",
        "username": "profgalloway",
        "verified": "blue",
        "verified_type": "blue",
        "description": "Product of big government @ucla @ucberkeley | Prof Marketing @NYUStern | Right of Center-Left | #ProfGPod @PivotPod | Strategy Sprint @section_school",
        "created_at": "2007-10-06T02:08:16.000Z",
        "followers_count": 580549,
        "public_metrics": {
            "followers_count": 580549,
            "following_count": 0,
            "like_count": 68492,
            "listed_count": 6473,
            "media_count": 4754,
            "tweet_count": 42837,
        },
    },
    "anand": {
        "id": "18823314",
        "name": "anand",
        "username": "anand",
        "verified": "none",
        "verified_type": "none",
        "description": "",
        "created_at": "2009-01-10T01:44:21.000Z",
        "followers_count": 22,
        "public_metrics": {
            "followers_count": 22,
            "following_count": 0,
            "like_count": 0,
            "listed_count": 12,
            "media_count": 1,
            "tweet_count": 42,
        },
    },
    "parismartineau": {
        "id": "57724877",
        "name": "paris martineau",
        "username": "parismartineau",
        "verified": "none",
        "verified_type": "none",
        "description": "investigative journalist @consumerreports, previously @theinformation @wired / tech podcastin' @twit / send tips: 267.797.8655 (signal) / paris@cr.org",
        "created_at": "2009-07-17T18:58:46.000Z",
        "followers_count": 21136,
        "public_metrics": {
            "followers_count": 21136,
            "following_count": 2106,
            "like_count": 17887,
            "listed_count": 403,
            "media_count": 1349,
            "tweet_count": 5970,
        },
    },
    "timwu": {
        "id": "15627325",
        "name": "Timwu",
        "username": "Timwu",
        "verified": "none",
        "verified_type": "none",
        "description": "",
        "created_at": "2008-07-28T03:32:57.000Z",
        "followers_count": 5,
        "public_metrics": {
            "followers_count": 5,
            "following_count": 304,
            "like_count": 2,
            "listed_count": 0,
            "media_count": 0,
            "tweet_count": 0,
        },
    },
    "juliusk": {
        "id": "15218045",
        "name": "Julius Kerschinske",
        "username": "juliusk",
        "verified": "none",
        "verified_type": "none",
        "description": "Born and raised in a village in Nebraska. I tweet about #Mizzou #Clemson and nerdy things. #GoTigers",
        "created_at": "2008-06-24T10:20:29.000Z",
        "followers_count": 191,
        "public_metrics": {
            "followers_count": 191,
            "following_count": 198,
            "like_count": 283,
            "listed_count": 2,
            "media_count": 1,
            "tweet_count": 78,
        },
    },
    "david": {
        "id": "14138343",
        "name": "David Noël 🇪🇺",
        "username": "David",
        "verified": "none",
        "verified_type": "none",
        "description": "Executive & Leadership Coach • Partner at ForChiefs • Co-Founder and podcast co-host of @rolemodels • @SoundCloud alum",
        "created_at": "2008-03-13T09:04:04.000Z",
        "followers_count": 21973,
        "public_metrics": {
            "followers_count": 21973,
            "following_count": 19,
            "like_count": 2674,
            "listed_count": 1148,
            "media_count": 531,
            "tweet_count": 18808,
        },
    },
    "jasonfried": {
        "id": "14372143",
        "name": "Jason Fried",
        "username": "jasonfried",
        "verified": "blue",
        "verified_type": "blue",
        "description": "Started & runs 37signals (makers of Basecamp, HEY, and ONCE). Non-serial entrepreneur, serial author. DM or email me at jason@hey.com.",
        "created_at": "2008-04-13T01:31:17.000Z",
        "followers_count": 312131,
        "public_metrics": {
            "followers_count": 312131,
            "following_count": 224,
            "like_count": 9961,
            "listed_count": 10339,
            "media_count": 1764,
            "tweet_count": 52010,
        },
    },
    "wired": {
        "id": "1344951",
        "name": "WIRED",
        "username": "WIRED",
        "verified": "business",
        "verified_type": "business",
        "description": "Where tomorrow is realized || Sign up for our newsletters: https://t.co/Tl6GImvc8R",
        "created_at": "2007-03-17T09:57:25.000Z",
        "followers_count": 9370396,
        "public_metrics": {
            "followers_count": 9370396,
            "following_count": 442,
            "like_count": 6900,
            "listed_count": 80715,
            "media_count": 38680,
            "tweet_count": 185630,
        },
    },
}


def create_real_record(handle, real_info, topic_tags):
    """Create a proper record with real data"""

    # Determine if meets entry threshold
    followers = real_info["followers_count"]
    verified = real_info["verified"] == "blue"
    entry_threshold = (verified and followers >= 30000) or followers >= 50000

    if not entry_threshold:
        return None

    # Create activity metrics
    metrics = real_info["public_metrics"]
    activity_metrics = {
        "account_created_at": real_info["created_at"],
        "tweet_count": metrics["tweet_count"],
        "total_like_count": metrics["like_count"],
        "media_count": metrics["media_count"],
        "listed_count": metrics["listed_count"],
        "following_count": metrics["following_count"],
        "last_captured_at": datetime.utcnow().isoformat() + "+00:00",
    }

    # Create record
    record = {
        "id": real_info["id"],
        "handle": handle,
        "name": real_info["name"],
        "verified": real_info["verified"],
        "followers_count": followers,
        "is_org": False,  # Assume individual unless org account
        "is_official": False,
        "lang_primary": "en",
        "topic_tags": topic_tags,
        "meta": {
            "score": 0.0,  # Will be calculated later
            "last_refresh_at": datetime.utcnow().isoformat() + "+00:00",
            "sources": [
                {
                    "method": "rube_mcp_real_data",
                    "fetched_at": datetime.utcnow().isoformat() + "+00:00",
                    "evidence": f"@{handle} - Real Twitter API data via RUBE MCP",
                }
            ],
            "provenance_hash": "",
            "activity_metrics": activity_metrics,
            "entry_threshold_passed": entry_threshold,
            "quality_score": 0.0,  # Will be calculated later
        },
        "public_metrics": metrics,
        "username": real_info["username"],
        "description": real_info["description"],
        "verified_type": real_info["verified_type"],
        "created_at": real_info["created_at"],
    }

    # Calculate provenance hash
    record_str = json.dumps(record, sort_keys=True)
    record["meta"]["provenance_hash"] = hashlib.sha256(record_str.encode()).hexdigest()

    return record


def main():
    # Read original CSV to get topic tags
    import csv

    topic_map = {}
    with open("lists/seeds/m1-top20-new-targets.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            topic_map[row["handle"]] = [row["category"]]

    # Create real data records
    real_records = []
    for handle, real_info in real_data.items():
        if handle in topic_map:
            record = create_real_record(handle, real_info, topic_map[handle])
            if record:
                real_records.append(record)
                print(
                    f"Created real record for {handle} ({real_info['followers_count']} followers)"
                )
            else:
                print(f"Skipped {handle} - below entry threshold")

    # Write to file
    output_file = "data/tmp_m1_real_data.jsonl"
    with open(output_file, "w") as f:
        for record in real_records:
            f.write(json.dumps(record) + "\n")

    print(f"\nCreated {len(real_records)} real records")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
