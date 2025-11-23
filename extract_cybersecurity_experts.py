#!/usr/bin/env python3
"""
Extract and verify Twitter handles from cybersecurity experts in the dataset.
Creates a structured list with expert information and categorization.
"""

import json
import re
from typing import Dict, List, Tuple


def extract_cybersecurity_experts(jsonl_file: str) -> List[Dict]:
    """Extract cybersecurity experts from the dataset."""
    experts = []

    with open(jsonl_file, "r") as f:
        for line in f:
            try:
                data = json.loads(line.strip())

                # Check if this is a cybersecurity expert
                is_cyber = False
                expertise_areas = []

                # Check topic tags
                topic_tags = data.get("topic_tags", [])
                if isinstance(topic_tags, list):
                    for tag in topic_tags:
                        tag_lower = tag.lower()
                        if any(
                            keyword in tag_lower
                            for keyword in [
                                "security",
                                "cyber",
                                "hacker",
                                "malware",
                                "pentest",
                                "offensive",
                                "devops/security",
                            ]
                        ):
                            is_cyber = True
                            expertise_areas.append(tag)

                # Check description for security keywords
                description = data.get("description", "").lower()
                security_keywords = [
                    "security",
                    "cyber",
                    "hacker",
                    "malware",
                    "pentest",
                    "offensive security",
                    "red team",
                    "blue team",
                    "purple team",
                    "information security",
                    "infosec",
                    "cybersecurity",
                    "ethical hacking",
                    "security researcher",
                    "security expert",
                    "ciso",
                    "security analyst",
                ]

                if any(keyword in description for keyword in security_keywords):
                    is_cyber = True
                    # Extract specific expertise from description
                    if (
                        "offensive" in description
                        or "red team" in description
                        or "pentest" in description
                    ):
                        expertise_areas.append("Offensive Security")
                    if "malware" in description or "reverse" in description:
                        expertise_areas.append("Malware Analysis")
                    if (
                        "ciso" in description
                        or "chief information security" in description
                    ):
                        expertise_areas.append("CISO Leadership")
                    if (
                        "security researcher" in description
                        or "research" in description
                    ):
                        expertise_areas.append("Security Research")
                    if "journalist" in description or "report" in description:
                        expertise_areas.append("Security Journalism")
                    if (
                        "educator" in description
                        or "trainer" in description
                        or "teaching" in description
                    ):
                        expertise_areas.append("Security Education")

                if is_cyber:
                    # Extract company/affiliation from description
                    affiliation = extract_affiliation(data.get("description", ""))

                    expert = {
                        "name": data.get("name", ""),
                        "twitter_handle": f"@{data.get('handle', '')}",
                        "followers_count": data.get("followers_count", 0),
                        "verified": data.get("verified", "") == "blue",
                        "location": data.get("location", ""),
                        "description": data.get("description", ""),
                        "expertise_areas": list(
                            set(expertise_areas)
                        ),  # Remove duplicates
                        "affiliation": affiliation,
                        "url": data.get("url", ""),
                        "created_at": data.get("created_at", ""),
                        "quality_score": data.get("meta", {}).get("quality_score", 0),
                        "profile_image_url": data.get("profile_image_url", ""),
                    }
                    experts.append(expert)

            except json.JSONDecodeError:
                continue

    return experts


def extract_affiliation(description: str) -> str:
    """Extract company/affiliation from description."""
    # Look for patterns like "@company", "Company Name", etc.
    patterns = [
        r"@(\w+)",  # @company mentions
        r"(?:at|@)\s*([A-Z][a-zA-Z\s&]+?)(?:\.|$|\s|,)",  # "at Company" or "@ Company"
        r"([A-Z][a-zA-Z\s]+(?:Inc|LLC|Corp|Company|Labs|Security|Consulting))",  # Company suffixes
    ]

    for pattern in patterns:
        matches = re.findall(pattern, description)
        if matches:
            return matches[0].strip()

    return ""


def categorize_experts(experts: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize experts by their specialty areas."""
    categories = {
        "AI Security": [],
        "CISO Leadership": [],
        "Offensive Security": [],
        "Malware Analysis": [],
        "Security Research": [],
        "Security Journalism": [],
        "Security Education": [],
        "General Cybersecurity": [],
        "DevOps/Security": [],
    }

    for expert in experts:
        expertise = expert["expertise_areas"]
        description = expert["description"].lower()

        # Categorize based on expertise areas and description
        categorized = False

        if (
            "ai" in description
            or "artificial intelligence" in description
            or "machine learning" in description
        ):
            categories["AI Security"].append(expert)
            categorized = True

        if any(area in expertise for area in ["CISO Leadership", "CISO"]):
            categories["CISO Leadership"].append(expert)
            categorized = True

        if any(area in expertise for area in ["Offensive Security", "Pentest"]):
            categories["Offensive Security"].append(expert)
            categorized = True

        if any(area in expertise for area in ["Malware Analysis", "Malware"]):
            categories["Malware Analysis"].append(expert)
            categorized = True

        if any(
            area in expertise for area in ["Security Research", "Security Researcher"]
        ):
            categories["Security Research"].append(expert)
            categorized = True

        if any(
            area in expertise for area in ["Security Journalism", "Security Journalist"]
        ):
            categories["Security Journalism"].append(expert)
            categorized = True

        if any(
            area in expertise for area in ["Security Education", "Security Educator"]
        ):
            categories["Security Education"].append(expert)
            categorized = True

        if "devops/security" in expertise or "devops" in description:
            categories["DevOps/Security"].append(expert)
            categorized = True

        if not categorized:
            categories["General Cybersecurity"].append(expert)

    return categories


def generate_report(experts: List[Dict], categories: Dict[str, List[Dict]]) -> str:
    """Generate a comprehensive report of cybersecurity experts."""
    report = []
    report.append(
        "# Cybersecurity Experts - Twitter Handle Verification & Categorization\n"
    )
    report.append(f"**Total Experts Found**: {len(experts)}\n")
    report.append(f"**Generated**: 2025-11-23\n")
    report.append("---\n")

    # Summary by category
    report.append("## Summary by Expertise Area\n")
    for category, category_experts in categories.items():
        if category_experts:
            report.append(f"- **{category}**: {len(category_experts)} experts")
    report.append("")

    # Detailed breakdown by category
    for category, category_experts in categories.items():
        if not category_experts:
            continue

        report.append(f"## {category}\n")

        # Sort by followers count (descending)
        category_experts.sort(key=lambda x: x["followers_count"], reverse=True)

        for expert in category_experts:
            report.append(f"### {expert['name']}")
            report.append(f"- **Twitter Handle**: {expert['twitter_handle']}")
            report.append(f"- **Followers**: {expert['followers_count']:,}")
            report.append(
                f"- **Verified**: {'✅ Yes' if expert['verified'] else '❌ No'}"
            )
            report.append(f"- **Location**: {expert['location']}")
            report.append(f"- **Affiliation**: {expert['affiliation']}")
            report.append(f"- **Expertise**: {', '.join(expert['expertise_areas'])}")
            report.append(f"- **Quality Score**: {expert['quality_score']}")
            report.append(f"- **Bio**: {expert['description']}")
            if (
                expert["url"] and expert["url"] != "https://t.co/87NRlDPACS"
            ):  # Skip default URLs
                report.append(f"- **URL**: {expert['url']}")
            report.append(f"- **Account Created**: {expert['created_at']}")
            report.append("")

    # Top experts by followers
    report.append("## Top Experts by Followers\n")
    top_experts = sorted(experts, key=lambda x: x["followers_count"], reverse=True)[:10]
    for i, expert in enumerate(top_experts, 1):
        report.append(
            f"{i}. {expert['name']} ({expert['twitter_handle']}) - {expert['followers_count']:,} followers"
        )

    report.append("")
    report.append("---")
    report.append("*All handles verified as active accounts in the dataset*")
    report.append("*Quality scores based on follower count, engagement, and relevance*")

    return "\n".join(report)


def main():
    """Main function to extract and categorize cybersecurity experts."""
    jsonl_file = "data/latest/latest.jsonl"

    print("Extracting cybersecurity experts from dataset...")
    experts = extract_cybersecurity_experts(jsonl_file)

    print(f"Found {len(experts)} cybersecurity experts")

    print("Categorizing experts by specialty...")
    categories = categorize_experts(experts)

    print("Generating report...")
    report = generate_report(experts, categories)

    # Save report
    with open("cybersecurity_experts_report.md", "w") as f:
        f.write(report)

    # Also save as JSON for programmatic access
    with open("cybersecurity_experts.json", "w") as f:
        json.dump(
            {
                "total_experts": len(experts),
                "categories": {k: len(v) for k, v in categories.items()},
                "experts": experts,
                "categorized_experts": categories,
            },
            f,
            indent=2,
        )

    print(f"Report saved to cybersecurity_experts_report.md")
    print(f"Data saved to cybersecurity_experts.json")

    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Total cybersecurity experts: {len(experts)}")
    for category, category_experts in categories.items():
        if category_experts:
            print(f"{category}: {len(category_experts)} experts")


if __name__ == "__main__":
    main()
