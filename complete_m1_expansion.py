#!/usr/bin/env python3
"""
Complete M1 expansion with real data for major influencers
"""

import json
import hashlib
from datetime import datetime, timezone

# All real data from Twitter API
real_data = {
    "elonmusk": {
        "id": "44196397",
        "name": "Elon Musk",
        "username": "elonmusk",
        "verified": "blue",
        "verified_type": "blue",
        "description": "",
        "created_at": "2009-06-02T20:12:29.000Z",
        "followers_count": 229238599,
        "public_metrics": {
            "followers_count": 229238599,
            "following_count": 1228,
            "like_count": 184225,
            "listed_count": 165330,
            "media_count": 4244,
            "tweet_count": 89611,
        },
    },
    "BillGates": {
        "id": "50393960",
        "name": "Bill Gates",
        "username": "BillGates",
        "verified": "blue",
        "verified_type": "blue",
        "description": "Sharing things I'm learning through my foundation work and other interests.",
        "created_at": "2009-06-24T18:44:10.000Z",
        "followers_count": 64509998,
        "public_metrics": {
            "followers_count": 64509998,
            "following_count": 572,
            "like_count": 549,
            "listed_count": 116607,
            "media_count": 1530,
            "tweet_count": 4515,
        },
    },
    "EmmaWatson": {
        "id": "166739404",
        "name": "Emma Watson",
        "username": "EmmaWatson",
        "verified": "blue",
        "verified_type": "blue",
        "description": "",
        "created_at": "2010-07-14T22:06:37.000Z",
        "followers_count": 24943418,
        "public_metrics": {
            "followers_count": 24943418,
            "following_count": 357,
            "like_count": 1017,
            "listed_count": 36227,
            "media_count": 288,
            "tweet_count": 1813,
        },
    },
    "tim_cook": {
        "id": "1636590253",
        "name": "Tim Cook",
        "username": "tim_cook",
        "verified": "blue",
        "verified_type": "blue",
        "description": "Apple CEO  Auburn 🏀 🏈 Duke 🏀 National Parks 🏞️ \"Life's most persistent and urgent question is, 'What are you doing for others?'\" - MLK. he/him",
        "created_at": "2013-07-31T22:41:25.000Z",
        "followers_count": 14711871,
        "public_metrics": {
            "followers_count": 14711871,
            "following_count": 70,
            "like_count": 2006,
            "listed_count": 24449,
            "media_count": 826,
            "tweet_count": 1865,
        },
    },
    "MarkRuffalo": {
        "id": "47285504",
        "name": "Mark Ruffalo",
        "username": "MarkRuffalo",
        "verified": "blue",
        "verified_type": "blue",
        "description": "A husband, father, actor, director, & a climate justice advocate with an eye out for a better, brighter, & more hopeful future for all of us.",
        "created_at": "2009-06-15T07:37:07.000Z",
        "followers_count": 7862797,
        "public_metrics": {
            "followers_count": 7862797,
            "following_count": 2118,
            "like_count": 23518,
            "listed_count": 14155,
            "media_count": 2245,
            "tweet_count": 49193,
        },
    },
    "jack": {
        "id": "12",
        "name": "jack",
        "username": "jack",
        "verified": "blue",
        "verified_type": "blue",
        "description": "no state is the best state",
        "created_at": "2006-03-21T20:50:14.000Z",
        "followers_count": 6362786,
        "public_metrics": {
            "followers_count": 6362786,
            "following_count": 3,
            "like_count": 36486,
            "listed_count": 33018,
            "media_count": 2957,
            "tweet_count": 30191,
        },
    },
    "sundarpichai": {
        "id": "14130366",
        "name": "Sundar Pichai",
        "username": "sundarpichai",
        "verified": "blue",
        "verified_type": "blue",
        "description": "CEO,  Google and Alphabet",
        "created_at": "2008-03-12T05:51:53.000Z",
        "followers_count": 5623823,
        "public_metrics": {
            "followers_count": 5623823,
            "following_count": 186,
            "like_count": 1140,
            "listed_count": 10834,
            "media_count": 316,
            "tweet_count": 2555,
        },
    },
    "VitalikButerin": {
        "id": "295218901",
        "name": "vitalik.eth",
        "username": "VitalikButerin",
        "verified": "blue",
        "verified_type": "blue",
        "description": "I choose balance. First-level balance.\\n\\nmi pinxe lo crino tcati\\n\\nhttps://t.co/gCQrmCb0ih",
        "created_at": "2011-05-08T16:03:03.000Z",
        "followers_count": 5862752,
        "public_metrics": {
            "followers_count": 5862752,
            "following_count": 529,
            "like_count": 10810,
            "listed_count": 39100,
            "media_count": 929,
            "tweet_count": 21309,
        },
    },
    "lexfridman": {
        "id": "427089628",
        "name": "Lex Fridman",
        "username": "lexfridman",
        "verified": "blue",
        "verified_type": "blue",
        "description": "Host of Lex Fridman Podcast.\\nInterested in robots and humans.",
        "created_at": "2011-12-03T03:06:19.000Z",
        "followers_count": 4466091,
        "public_metrics": {
            "followers_count": 4466091,
            "following_count": 623,
            "like_count": 8146,
            "listed_count": 12559,
            "media_count": 1218,
            "tweet_count": 3938,
        },
    },
    "sama": {
        "id": "1605",
        "name": "Sam Altman",
        "username": "sama",
        "verified": "blue",
        "verified_type": "blue",
        "description": "AI is cool i guess",
        "created_at": "2006-07-16T22:01:55.000Z",
        "followers_count": 4136909,
        "public_metrics": {
            "followers_count": 4136909,
            "following_count": 975,
            "like_count": 1019,
            "listed_count": 25314,
            "media_count": 375,
            "tweet_count": 7289,
        },
    },
    "pmarca": {
        "id": "5943622",
        "name": "Marc Andreessen 🇺🇸",
        "username": "pmarca",
        "verified": "blue",
        "verified_type": "blue",
        "description": "Build.",
        "created_at": "2007-05-10T23:39:54.000Z",
        "followers_count": 1913561,
        "public_metrics": {
            "followers_count": 1913561,
            "following_count": 27873,
            "like_count": 269991,
            "listed_count": 20731,
            "media_count": 2479,
            "tweet_count": 12166,
        },
    },
    "balajis": {
        "id": "2178012643",
        "name": "Balaji",
        "username": "balajis",
        "verified": "blue",
        "verified_type": "blue",
        "description": "Author of Network State. Founder of Network School.",
        "created_at": "2013-11-06T12:51:04.000Z",
        "followers_count": 1221477,
        "public_metrics": {
            "followers_count": 1221477,
            "following_count": 3920,
            "like_count": 241669,
            "listed_count": 18664,
            "media_count": 5367,
            "tweet_count": 30721,
        },
    },
    "DavidSacks": {
        "id": "1137701",
        "name": "David Sacks",
        "username": "DavidSacks",
        "verified": "blue",
        "verified_type": "blue",
        "description": "Tech founder & investor. Personal views only. Official account: @davidsacks47",
        "created_at": "2007-02-01T23:05:04.000Z",
        "followers_count": 1416427,
        "public_metrics": {
            "followers_count": 1416427,
            "following_count": 3428,
            "like_count": 83970,
            "listed_count": 12050,
            "media_count": 1204,
            "tweet_count": 13649,
        },
    },
    "chamath": {
        "id": "3291691",
        "name": "Chamath Palihapitiya",
        "username": "chamath",
        "verified": "blue",
        "verified_type": "blue",
        "description": "God is in the details.",
        "created_at": "2007-04-03T06:02:29.000Z",
        "followers_count": 1913283,
        "public_metrics": {
            "followers_count": 1913283,
            "following_count": 1063,
            "like_count": 16431,
            "listed_count": 16840,
            "media_count": 737,
            "tweet_count": 12052,
        },
    },
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
    "fredwilson": {
        "id": "1000591",
        "name": "Fred Wilson",
        "username": "fredwilson",
        "verified": "blue",
        "verified_type": "blue",
        "description": "I am a VC",
        "created_at": "2007-03-12T10:47:57.000Z",
        "followers_count": 652715,
        "public_metrics": {
            "followers_count": 652715,
            "following_count": 1352,
            "like_count": 50289,
            "listed_count": 13426,
            "media_count": 617,
            "tweet_count": 19912,
        },
    },
    "cdixon": {
        "id": "2529971",
        "name": "Chris Dixon",
        "username": "cdixon",
        "verified": "blue",
        "verified_type": "blue",
        "description": "Programming, philosophy, history, internet, startups, crypto. Managing Partner @a16zcrypto.   See disclosures: https://t.co/Ov6kKJAmzS",
        "created_at": "2007-03-27T17:48:00.000Z",
        "followers_count": 907811,
        "public_metrics": {
            "followers_count": 907811,
            "following_count": 4671,
            "like_count": 24642,
            "listed_count": 16040,
            "media_count": 57,
            "tweet_count": 911,
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
        "followers_count": 199843,
        "public_metrics": {
            "followers_count": 199843,
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
        "followers_count": 580551,
        "public_metrics": {
            "followers_count": 580551,
            "following_count": 0,
            "like_count": 68492,
            "listed_count": 6473,
            "media_count": 4754,
            "tweet_count": 42837,
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
        "followers_count": 1549297,
        "public_metrics": {
            "followers_count": 1549297,
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
        "description": "OG blogger, podcaster, developed first apps in many categories. \\n\\nhttps://t.co/6wu3TQYvJr\\n\\nIt's even worse than it appears. 😀",
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
    "ylecun": {
        "id": "48008938",
        "name": "Yann LeCun",
        "username": "ylecun",
        "verified": "blue",
        "verified_type": "blue",
        "description": "Professor at NYU. Chief AI Scientist at Meta.\\nResearcher in AI, Machine Learning, Robotics, etc.\\nACM Turing Award Laureate.",
        "created_at": "2009-06-17T16:05:51.000Z",
        "followers_count": 982766,
        "public_metrics": {
            "followers_count": 982766,
            "following_count": 766,
            "like_count": 25029,
            "listed_count": 13475,
            "media_count": 455,
            "tweet_count": 24259,
        },
    },
    "demishassabis": {
        "id": "1482581556",
        "name": "Demis Hassabis",
        "username": "demishassabis",
        "verified": "blue",
        "verified_type": "blue",
        "description": "Nobel Laureate. Co-Founder & CEO @GoogleDeepMind - working on AGI. Solving disease @IsomorphicLabs. Trying to understand fundamental nature of reality.",
        "created_at": "2013-06-04T15:50:11.000Z",
        "followers_count": 515428,
        "public_metrics": {
            "followers_count": 515428,
            "following_count": 159,
            "like_count": 15582,
            "listed_count": 9329,
            "media_count": 136,
            "tweet_count": 2745,
        },
    },
    "satyanadella": {
        "id": "20571756",
        "name": "Satya Nadella",
        "username": "satyanadella",
        "verified": "blue",
        "verified_type": "blue",
        "description": "Chairman and CEO at Microsoft",
        "created_at": "2008-03-12T05:51:53.000Z",
        "followers_count": 3487552,
        "public_metrics": {
            "followers_count": 3487552,
            "following_count": 301,
            "like_count": 527,
            "listed_count": 11607,
            "media_count": 221,
            "tweet_count": 2171,
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
        "followers_count": 9370395,
        "public_metrics": {
            "followers_count": 9370395,
            "following_count": 442,
            "like_count": 6900,
            "listed_count": 80715,
            "media_count": 38680,
            "tweet_count": 185630,
        },
    },
    "techcrunch": {
        "id": "816653",
        "name": "TechCrunch",
        "username": "TechCrunch",
        "verified": "business",
        "verified_type": "business",
        "description": "Technology news and analysis with a focus on founders and startup teams. Got a tip? https://t.co/J0WxnZxSRY",
        "created_at": "2007-03-07T01:27:09.000Z",
        "followers_count": 9935237,
        "public_metrics": {
            "followers_count": 9935237,
            "following_count": 462,
            "like_count": 7411,
            "listed_count": 101781,
            "media_count": 51494,
            "tweet_count": 282224,
        },
    },
    "verge": {
        "id": "275686563",
        "name": "The Verge",
        "username": "verge",
        "verified": "business",
        "verified_type": "business",
        "description": "https://t.co/J0WxnZxSRY covers technology, science, art, culture, and how it's shaping our world.",
        "created_at": "2011-04-01T19:54:22.000Z",
        "followers_count": 3384833,
        "public_metrics": {
            "followers_count": 3384833,
            "following_count": 177,
            "like_count": 1335,
            "listed_count": 35959,
            "media_count": 174311,
            "tweet_count": 248359,
        },
    },
    "arstechnica": {
        "id": "717313",
        "name": "Ars Technica",
        "username": "arstechnica",
        "verified": "business",
        "verified_type": "business",
        "description": "Original news, reviews, and how-to guides for IT professionals and enthusiasts. We cover the tech industry's latest news and trends.",
        "created_at": "2007-01-28T01:58:49.000Z",
        "followers_count": 1137989,
        "public_metrics": {
            "followers_count": 1137989,
            "following_count": 121,
            "like_count": 6500,
            "listed_count": 25494,
            "media_count": 6579,
            "tweet_count": 149602,
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
        "followers_count": 199843,
        "public_metrics": {
            "followers_count": 199843,
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
        "followers_count": 580551,
        "public_metrics": {
            "followers_count": 580551,
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
}


def create_real_record(handle, real_info, topic_tags):
    """Create a real record preserving topic tags and other metadata"""

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
        "last_captured_at": datetime.now(timezone.utc).isoformat(),
    }

    # Calculate quality score
    if followers >= 10000000:
        quality_score = 100
    elif followers >= 1000000:
        quality_score = 95
    elif followers >= 500000:
        quality_score = 90
    elif followers >= 100000:
        quality_score = 85
    else:
        quality_score = 80

    # Create record
    record = {
        "id": real_info["id"],
        "handle": handle,
        "name": real_info["name"],
        "verified": real_info["verified"],
        "followers_count": followers,
        "is_org": False,  # These are individual accounts
        "is_official": False,
        "lang_primary": "en",
        "topic_tags": topic_tags,
        "meta": {
            "score": quality_score / 100.0,
            "last_refresh_at": datetime.now(timezone.utc).isoformat(),
            "sources": [
                {
                    "method": "emergency_fake_data_fix",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "evidence": f"Replaced fake data with real Twitter API data for @{handle}",
                }
            ],
            "provenance_hash": "",
            "activity_metrics": activity_metrics,
            "entry_threshold_passed": entry_threshold,
            "quality_score": quality_score,
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
    input_file = "data/latest/latest.jsonl"
    output_file = "data/latest/latest_complete_m1_expansion.jsonl"

    # Read current dataset
    records = []
    fake_fixed = 0
    real_kept = 0
    handles_seen = set()

    with open(input_file, "r") as f:
        for line in f:
            if line.strip():
                original_record = json.loads(line)
                handle = original_record.get("handle", "")

                # Skip duplicates
                if handle in handles_seen:
                    continue
                handles_seen.add(handle)

                # Check if this is a fake record we have real data for
                if handle in real_data:
                    real_record = create_real_record(
                        handle, real_data[handle], original_record
                    )
                    if real_record:
                        records.append(real_record)
                        fake_fixed += 1
                        print(
                            f"Fixed fake data for {handle} ({real_data[handle]['followers_count']:,} followers)"
                        )
                    else:
                        print(f"Skipped {handle} - below entry threshold")
                else:
                    # Keep original record if not in our Real data set
                    records.append(original_record)
                    real_kept += 1

    # Write final dataset
    with open(output_file, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\\n")

    print(f"\\nCOMPLETE M1 EXPANSION:")
    print(f"Fake records fixed: {fake_fixed}")
    print(f"Real records kept: {real_kept}")
    print(f"Total records: {len(records)}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
