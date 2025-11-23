#!/usr/bin/env python3

import json


def load_dataset_handles(filename):
    """Load all handles from main dataset"""
    handles = set()
    with open(filename, "r") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                handle = data.get("handle") or data.get("username")
                if handle:
                    handles.add(handle.lower())
    return handles


def verify_candidates():
    """Verify the found candidates are genuine and not duplicates"""

    # Load main dataset handles
    main_handles = load_dataset_handles(
        "/home/dodd/dev/influx/data/latest/latest.jsonl"
    )

    # Found candidates (removing test user and duplicates)
    candidates = [
        {"handle": "amanrsanger", "name": "Aman Sanger", "followers": 45748},
        {"handle": "cHHillee", "name": "Horace He", "followers": 43344},
        {"handle": "HamelHusain", "name": "Hamel Husain", "followers": 40436},
        {
            "handle": "AnimaAnandkumar",
            "name": "Prof. Anima Anandkumar",
            "followers": 34805,
        },
        {"handle": "dankrad", "name": "Dankrad Feist", "followers": 34424},
        {"handle": "reach_vb", "name": "Vaibhav (VB) Srivastav", "followers": 33791},
        {"handle": "aidangomez", "name": "Aidan Gomez", "followers": 32669},
        {"handle": "TheRealAdamG", "name": "Adam.GPT", "followers": 30053},
        {"handle": "cwolferesearch", "name": "Cameron R. Wolfe", "followers": 27695},
    ]

    print("Verifying 25K-49K verified candidates:")
    print("=" * 50)

    verified_candidates = []
    for candidate in candidates:
        handle_lower = candidate["handle"].lower()

        if handle_lower in main_handles:
            print(f"❌ @{candidate['handle']} - Already in main dataset")
        else:
            print(
                f"✅ @{candidate['handle']} ({candidate['name']}): {candidate['followers']:,} followers - NEW"
            )
            verified_candidates.append(candidate)

    print(f"\n" + "=" * 50)
    print(f"VERIFICATION SUMMARY")
    print(f"=" * 50)
    print(f"Total genuine candidates: {len(verified_candidates)}")
    print(f"Current dataset size: {len(main_handles)}")
    print(f"Potential new size: {len(main_handles) + len(verified_candidates)}")

    if len(verified_candidates) > 0:
        print(
            f"\nThese {len(verified_candidates)} candidates could help reach the 279-289 target range!"
        )
        print(
            f"Adding them would bring the dataset to {len(main_handles) + len(verified_candidates)} authors."
        )

        print(f"\nCandidate details:")
        for candidate in sorted(
            verified_candidates, key=lambda x: x["followers"], reverse=True
        ):
            print(
                f"  - @{candidate['handle']} ({candidate['name']}): {candidate['followers']:,} followers"
            )
    else:
        print("No new candidates found that aren't already in the dataset.")


if __name__ == "__main__":
    verify_candidates()
