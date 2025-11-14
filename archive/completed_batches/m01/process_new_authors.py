#!/usr/bin/env python3
"""Process M0.1 new authors from Twitter API response"""
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# Twitter API response (24 successful profiles)
twitter_data = [
    {"created_at":"2016-07-21T17:39:06.000Z","description":"Philosopher & ethicist trying to make AI be good @AnthropicAI.\nPersonal account. All opinions come from my training data.","id":"756181721997987848","name":"Amanda Askell","profile_image_url":"https://pbs.twimg.com/profile_images/1808357270516125696/-s0TTWR8_normal.jpg","public_metrics":{"followers_count":57080,"following_count":659,"like_count":9029,"listed_count":1027,"media_count":248,"tweet_count":5105},"url":"https://t.co/5eYSq7KsOw","username":"AmandaAskell","verified":True,"verified_type":"blue"},
    {"created_at":"2009-06-17T16:05:51.000Z","description":"Professor at NYU. Chief AI Scientist at Meta.\nResearcher in AI, Machine Learning, Robotics, etc.\nACM Turing Award Laureate.","id":"48008938","name":"Yann LeCun","profile_image_url":"https://pbs.twimg.com/profile_images/1483577865056702469/rWA-3_T7_normal.jpg","public_metrics":{"followers_count":975526,"following_count":766,"like_count":24896,"listed_count":13399,"media_count":455,"tweet_count":24216},"url":"https://t.co/POp7IBHfXy","username":"ylecun","verified":True,"verified_type":"blue"},
    {"created_at":"2009-08-25T17:09:25.000Z","description":"Co-founder @ndea. Co-founder @arcprize. Creator of Keras and ARC-AGI. Author of 'Deep Learning with Python'.","id":"68746721","name":"François Chollet","profile_image_url":"https://pbs.twimg.com/profile_images/1611009368765468673/lLWbGjjj_normal.jpg","public_metrics":{"followers_count":584681,"following_count":820,"like_count":10152,"listed_count":8445,"media_count":1443,"tweet_count":24611},"url":"https://t.co/6miFIZSFAQ","username":"fchollet","verified":True,"verified_type":"blue"},
    {"created_at":"2014-11-10T11:05:07.000Z","description":"Building @SakanaAILabs 🧠","id":"2895499182","name":"hardmaru","profile_image_url":"https://pbs.twimg.com/profile_images/1678402467078234113/XN5Oy2UP_normal.jpg","public_metrics":{"followers_count":366820,"following_count":1767,"like_count":144548,"listed_count":4365,"media_count":4426,"tweet_count":25634},"url":"https://t.co/cVQF43wg32","username":"hardmaru","verified":True,"verified_type":"blue"},
    {"created_at":"2015-08-07T15:02:40.000Z","description":"","id":"3407271909","name":"Welch Labs","profile_image_url":"https://pbs.twimg.com/profile_images/629745654114312192/EQjE2nne_normal.jpg","public_metrics":{"followers_count":4375,"following_count":52,"like_count":183,"listed_count":43,"media_count":80,"tweet_count":221},"username":"welchlabs","verified":False,"verified_type":"none"},
    {"created_at":"2011-12-03T03:06:19.000Z","description":"Host of Lex Fridman Podcast.\nInterested in robots and humans.","id":"427089628","name":"Lex Fridman","profile_image_url":"https://pbs.twimg.com/profile_images/1854713863817646088/nTmsz7jR_normal.jpg","public_metrics":{"followers_count":4461379,"following_count":616,"like_count":8140,"listed_count":12541,"media_count":1215,"tweet_count":3927},"url":"https://t.co/eBRkEqtwUb","username":"lexfridman","verified":True,"verified_type":"blue"},
    {"created_at":"2015-10-16T21:59:52.000Z","description":"VP of Research & Deep Learning Lead, Google DeepMind. Gemini co-lead.\n\nPast: AlphaStar, AlphaFold, AlphaCode, WaveNet, seq2seq, distillation, TF.","id":"3918111614","name":"Oriol Vinyals","profile_image_url":"https://pbs.twimg.com/profile_images/677499217993007104/Uartsv8s_normal.jpg","public_metrics":{"followers_count":185532,"following_count":86,"like_count":1368,"listed_count":3646,"media_count":244,"tweet_count":1403},"url":"https://t.co/1K0DjHojv6","username":"OriolVinyalsML","verified":True,"verified_type":"blue"},
    {"created_at":"2013-06-04T15:50:11.000Z","description":"Nobel Laureate. Co-Founder & CEO @GoogleDeepMind - working on AGI. Solving disease @IsomorphicLabs. Trying to understand the fundamental nature of reality.","id":"1482581556","name":"Demis Hassabis","profile_image_url":"https://pbs.twimg.com/profile_images/1963993428200415232/4uxhiMYX_normal.jpg","public_metrics":{"followers_count":507365,"following_count":156,"like_count":15121,"listed_count":9189,"media_count":129,"tweet_count":2698},"url":"https://t.co/HBuykkIl9e","username":"demishassabis","verified":True,"verified_type":"blue"},
    {"created_at":"2017-09-22T18:32:35.000Z","description":"Chief Scientist, Google DeepMind & Google Research. Gemini Lead. Opinions stated here are my own, not those of Google. TensorFlow, MapReduce, Bigtable, ...","id":"911297187664949248","name":"Jeff Dean","profile_image_url":"https://pbs.twimg.com/profile_images/935325968280907776/AcBo6zJc_normal.jpg","public_metrics":{"followers_count":374129,"following_count":6315,"like_count":39460,"listed_count":6279,"media_count":473,"tweet_count":8716},"url":"https://t.co/hNIDIR4c7g","username":"JeffDean","verified":True,"verified_type":"blue"},
    {"created_at":"2016-11-04T06:57:37.000Z","description":"Sharing AI research. Early work on AI (GPT-J, LAION, scaling, MoE). Ex ML PhD (GT) & Google.","id":"794433401591693312","name":"Aran Komatsuzaki","profile_image_url":"https://pbs.twimg.com/profile_images/1561220982328754176/JOYS5kab_normal.jpg","public_metrics":{"followers_count":149843,"following_count":315,"like_count":15018,"listed_count":1641,"media_count":2525,"tweet_count":6494},"url":"https://t.co/aZGCShojNY","username":"arankomatsuzaki","verified":True,"verified_type":"blue"},
    {"created_at":"2019-09-19T03:45:10.000Z","description":"working on AGI alignment. prev: GPT-Neo, the Pile, LM evals, RL overoptimization, scaling SAEs to GPT-4. EleutherAI cofounder.","id":"1174529814264332289","name":"Leo Gao","profile_image_url":"https://pbs.twimg.com/profile_images/1258559367747530753/3uI8vU62_normal.jpg","public_metrics":{"followers_count":9809,"following_count":553,"like_count":6435,"listed_count":229,"media_count":201,"tweet_count":1490},"url":"https://t.co/pkHYJjFlEa","username":"nabla_theta","verified":True,"verified_type":"blue"},
    {"created_at":"2017-02-07T23:22:48.000Z","description":"LLM developer, AI agents, synthetic data, scalable alignment, forecasting, behavioral uploading. Transhumanist.\n\nAll tweets public domain under CC0 1.0.","id":"829108178059096064","name":"John David Pressman","profile_image_url":"https://pbs.twimg.com/profile_images/1850957204570193920/pBuQN2tH_normal.jpg","public_metrics":{"followers_count":8742,"following_count":772,"like_count":77622,"listed_count":256,"media_count":1755,"tweet_count":16807},"url":"https://t.co/nzj0ckOXK7","username":"jd_pressman","verified":True,"verified_type":"blue"},
    {"created_at":"2008-10-26T20:04:45.000Z","description":"Busy inventing the shipwreck. @Penn. Past: @johnshopkins, @UCSC, @Amazon, @Twitter ||Art: #NLProc, Vision, Speech, #DeepLearning || Life: 道元, improv, running 🌈","id":"16984977","name":"Delip Rao e/σ","profile_image_url":"https://pbs.twimg.com/profile_images/1521801057965264896/bo8B1BjJ_normal.jpg","public_metrics":{"followers_count":63004,"following_count":5192,"like_count":48646,"listed_count":953,"media_count":5068,"tweet_count":53967},"url":"https://t.co/h4RGsXZ0jV","username":"deliprao","verified":True,"verified_type":"blue"},
    {"created_at":"2012-10-07T02:06:16.000Z","description":"ML/AI research engineer. Ex stats professor.\nAuthor of \"Build a Large Language Model From Scratch\" (https://t.co/O8LAAMRzzW) & reasoning (https://t.co/5TueQKx2Fk)","id":"865622395","name":"Sebastian Raschka","profile_image_url":"https://pbs.twimg.com/profile_images/1661187442043486209/a3E4t1eV_normal.jpg","public_metrics":{"followers_count":367446,"following_count":1100,"like_count":23281,"listed_count":4435,"media_count":2013,"tweet_count":18901},"url":"https://t.co/HrtQQ5tgJl","username":"rasbt","verified":True,"verified_type":"blue"},
    {"created_at":"2010-08-06T04:58:18.000Z","description":"🇦🇺 Co-founder: @AnswerDotAI & @FastDotAI ;\nPrev: professor @ UQ; Stanford fellow; @kaggle president; @fastmail/@enlitic/etc founder\nhttps://t.co/16UBFTX7mo","id":"175282603","name":"Jeremy Howard","profile_image_url":"https://pbs.twimg.com/profile_images/1279600070145437696/eocLhSLu_normal.jpg","public_metrics":{"followers_count":264031,"following_count":6186,"like_count":10030,"listed_count":5372,"media_count":2867,"tweet_count":64229},"url":"https://t.co/3lh0uQDdfN","username":"jeremyphoward","verified":True,"verified_type":"blue"},
    {"created_at":"2025-10-22T21:49:13.000Z","description":"Dedicated to beautiful @wandb curves. I enjoy long training runs on the beach.","id":"1981115564795056129","name":"wan deeee bee","profile_image_url":"https://pbs.twimg.com/profile_images/1985415730142330882/geeLXTgD_normal.jpg","public_metrics":{"followers_count":19,"following_count":1,"like_count":25,"listed_count":0,"media_count":2,"tweet_count":3},"username":"weights_biases","verified":True,"verified_type":"blue"},
    {"created_at":"2016-09-22T01:13:35.000Z","description":"The AI community building the future. https://t.co/VkRPD0Vclr","id":"778764142412984320","name":"Hugging Face","profile_image_url":"https://pbs.twimg.com/profile_images/1348748676282388482/nr8ZuLBE_normal.jpg","public_metrics":{"followers_count":583119,"following_count":210,"like_count":8493,"listed_count":7178,"media_count":451,"tweet_count":12314},"url":"https://t.co/A337WqHDnG","username":"huggingface","verified":True,"verified_type":"blue"},
    {"created_at":"2009-04-21T06:59:33.000Z","description":"Making AI helpful for everyone. Show thinking ↓","id":"33838201","name":"Google AI","profile_image_url":"https://pbs.twimg.com/profile_images/1924554705503715328/0-HDhohz_normal.jpg","public_metrics":{"followers_count":2334898,"following_count":25,"like_count":241,"listed_count":25933,"media_count":1302,"tweet_count":3067},"url":"https://t.co/Bz9VfUNifq","username":"GoogleAI","verified":True,"verified_type":"business"},
    {"created_at":"2021-01-25T22:45:28.000Z","description":"We're an AI safety and research company that builds reliable, interpretable, and steerable AI systems. Talk to our AI assistant @claudeai on https://t.co/FhDI3KQh0n.","id":"1353836358901501952","name":"Anthropic","profile_image_url":"https://pbs.twimg.com/profile_images/1798110641414443008/XP8gyBaY_normal.jpg","public_metrics":{"followers_count":678989,"following_count":35,"like_count":1469,"listed_count":7690,"media_count":500,"tweet_count":1215},"url":"https://t.co/w94SABjAXZ","username":"AnthropicAI","verified":True,"verified_type":"business"},
    {"created_at":"2015-12-06T22:51:08.000Z","description":"OpenAI's mission is to ensure that artificial general intelligence benefits all of humanity. We're hiring: https://t.co/dJGr6Lg202","id":"4398626122","name":"OpenAI","profile_image_url":"https://pbs.twimg.com/profile_images/1885410181409820672/ztsaR0JW_normal.jpg","public_metrics":{"followers_count":4492195,"following_count":4,"like_count":1205,"listed_count":25533,"media_count":445,"tweet_count":1500},"url":"https://t.co/3bPlZZjXod","username":"OpenAI","verified":True,"verified_type":"business"},
    {"created_at":"2023-09-18T22:26:33.000Z","description":"We've moved, follow us at @AIatMeta for the latest on AI research and innovation from Meta.","id":"1703898138854170624","name":"AI at Meta","profile_image_url":"https://pbs.twimg.com/profile_images/1707096745270972416/De97lTSa_normal.png","public_metrics":{"followers_count":6595,"following_count":0,"like_count":0,"listed_count":166,"media_count":0,"tweet_count":0},"url":"https://t.co/MC9FpVHKBf","username":"metaai","verified":False,"verified_type":"none"},
    {"created_at":"2020-07-09T02:11:22.000Z","description":"We'll help you make it like nobody's business. Multimodal media generation and editing tools to get your idea to production. Self-deploy? 👍 Need a partner? 🤝","id":"1281048162602369024","name":"Stability AI","profile_image_url":"https://pbs.twimg.com/profile_images/1952432488648724480/9CFXnHx6_normal.png","public_metrics":{"followers_count":246074,"following_count":10,"like_count":975,"listed_count":3272,"media_count":315,"tweet_count":841},"url":"https://t.co/Y5YXjpuD8O","username":"StabilityAI","verified":True,"verified_type":"blue"},
    {"created_at":"2023-06-09T19:17:25.000Z","description":"Frontier AI in your hands. https://t.co/VdyEwpQsiy Apps: https://t.co/1vZA5XdBYo https://t.co/rj5G4u5sHu","id":"1667249535519805451","name":"Mistral AI","profile_image_url":"https://pbs.twimg.com/profile_images/1943557042897063936/chh4Ugsb_normal.png","public_metrics":{"followers_count":159958,"following_count":0,"like_count":2,"listed_count":1911,"media_count":32,"tweet_count":92},"username":"MistralAI","verified":True,"verified_type":"blue"},
    {"created_at":"2023-10-16T23:43:49.000Z","description":"","id":"1714064605029289984","name":".","profile_image_url":"https://pbs.twimg.com/profile_images/1770599776838717441/GViTICUU_normal.jpg","public_metrics":{"followers_count":0,"following_count":0,"like_count":1,"listed_count":0,"media_count":0,"tweet_count":0},"username":"MosaicML","verified":False,"verified_type":"none"}
]

def passes_entry_filter(user):
    """Check if user passes entry filter: (verified AND followers≥30k) OR followers≥50k"""
    followers = user["public_metrics"]["followers_count"]
    verified = user["verified"]

    if verified and followers >= 30000:
        return True
    if followers >= 50000:
        return True
    return False

def convert_to_schema(user):
    """Convert Twitter API user to schema-compliant author record"""
    followers = user["public_metrics"]["followers_count"]

    # Map verified_type to our schema
    verified_type = user.get("verified_type", "none")
    if verified_type == "business":
        verified = "org"
    elif verified_type == "blue":
        verified = "blue"
    elif user.get("verified"):
        verified = "legacy"
    else:
        verified = "none"

    # Create author record
    author = {
        "id": user["id"],
        "handle": user["username"],
        "name": user["name"],
        "verified": verified,
        "followers_count": followers,
        "description": user.get("description", ""),
        "url": user.get("url", ""),
        "profile_image_url": user.get("profile_image_url", ""),
        "created_at": user.get("created_at", ""),
        "lang_primary": "en",
        "topic_tags": [],
        "meta": {
            "score": 0.0,
            "last_refresh_at": datetime.now(timezone.utc).isoformat(),
            "sources": [{
                "method": "manual_curation",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "evidence": "m01_team_pages"
            }]
        }
    }

    # Calculate provenance_hash
    canonical = json.dumps({
        "id": author["id"],
        "handle": author["handle"],
        "followers_count": author["followers_count"],
        "verified": author["verified"],
        "sources": author["meta"]["sources"]
    }, sort_keys=True, separators=(',', ':'))

    author["meta"]["provenance_hash"] = hashlib.sha256(canonical.encode()).hexdigest()

    return author

# Filter and convert
passed_count = 0
failed_count = 0
authors = []

for user in twitter_data:
    if passes_entry_filter(user):
        author = convert_to_schema(user)
        authors.append(author)
        passed_count += 1
        print(f"✓ PASS: @{user['username']} ({user['public_metrics']['followers_count']:,} followers, {user.get('verified_type', 'none')})")
    else:
        failed_count += 1
        print(f"✗ FAIL: @{user['username']} ({user['public_metrics']['followers_count']:,} followers, {user.get('verified_type', 'none')})")

# Write to JSONL
output_path = Path(".cccc/work/m01/new_authors.jsonl")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    for author in authors:
        line = json.dumps(author, ensure_ascii=False, separators=(',', ':'))
        f.write(line + "\n")

print(f"\n📊 Summary:")
print(f"  Total fetched: {len(twitter_data)}")
print(f"  Passed filter: {passed_count}")
print(f"  Failed filter: {failed_count}")
print(f"  Output: {output_path}")
print(f"\n✅ Ready to merge with existing 48 authors")
