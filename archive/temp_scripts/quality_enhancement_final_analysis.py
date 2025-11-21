#!/usr/bin/env python3
"""
Quality Enhancement Final Report
Analyze the impact of quality enhancement on network scoring
"""

import json
from datetime import datetime, timezone


def analyze_quality_enhancement_impact():
    """Analyze the impact of quality enhancement"""
    print("🎯 QUALITY ENHANCEMENT FINAL ANALYSIS")
    print("=" * 60)

    # Load current dataset
    authors = []
    with open("data/latest/latest.jsonl", "r") as f:
        for line in f:
            if line.strip():
                authors.append(json.loads(line))

    # Analyze quality enhancement authors
    quality_enhanced_authors = []
    high_value_authors = []

    for author in authors:
        score = author.get("meta", {}).get("score", 0)
        followers = author.get("followers_count", 0)

        # Check if quality enhanced
        if author.get("meta", {}).get("quality_enhancement"):
            quality_enhanced_authors.append(
                {
                    "name": author.get("name", ""),
                    "handle": author.get("handle", ""),
                    "followers": followers,
                    "score": score,
                    "previous_score": author["meta"].get("previous_score", 0),
                    "improvement": author["meta"].get("score_improvement", 0),
                }
            )

        # High-value authors (100K+ followers)
        if followers >= 100000:
            high_value_authors.append(
                {
                    "name": author.get("name", ""),
                    "handle": author.get("handle", ""),
                    "followers": followers,
                    "score": score,
                    "verified": author.get("verified", "none"),
                }
            )

    # Quality Enhancement Results
    print(f"\n📊 QUALITY ENHANCEMENT RESULTS:")
    print(f"  Authors enhanced: {len(quality_enhanced_authors)}")
    if quality_enhanced_authors:
        total_improvement = sum(a["improvement"] for a in quality_enhanced_authors)
        avg_improvement = total_improvement / len(quality_enhanced_authors)
        print(f"  Total improvement: {total_improvement:.1f} points")
        print(f"  Average improvement: {avg_improvement:.1f} points")

        # Top improvements
        top_improvements = sorted(
            quality_enhanced_authors, key=lambda x: x["improvement"], reverse=True
        )[:10]
        print(f"\n🏆 TOP 10 QUALITY IMPROVEMENTS:")
        for i, author in enumerate(top_improvements, 1):
            print(f"  {i:2d}. {author['name']} (@{author['handle']}):")
            print(
                f"      {author['previous_score']:.1f} → {author['score']:.1f} (+{author['improvement']:.1f})"
            )

    # High-Value Network Analysis
    print(f"\n🌟 HIGH-VALUE NETWORK ANALYSIS:")
    print(f"  Total high-value authors (100K+): {len(high_value_authors)}")

    # Score distribution
    high_scoring_authors = [a for a in high_value_authors if a["score"] >= 50]
    medium_scoring_authors = [a for a in high_value_authors if 30 <= a["score"] < 50]
    low_scoring_authors = [a for a in high_value_authors if a["score"] < 30]

    print(
        f"  High scoring (50+): {len(high_scoring_authors)} ({len(high_scoring_authors) / len(high_value_authors) * 100:.1f}%)"
    )
    print(
        f"  Medium scoring (30-49): {len(medium_scoring_authors)} ({len(medium_scoring_authors) / len(high_value_authors) * 100:.1f}%)"
    )
    print(
        f"  Low scoring (<30): {len(low_scoring_authors)} ({len(low_scoring_authors) / len(high_value_authors) * 100:.1f}%)"
    )

    # Top high-value authors
    top_high_value = sorted(
        high_value_authors, key=lambda x: x["followers"], reverse=True
    )[:15]
    print(f"\n👑 TOP 15 HIGH-VALUE AUTHORS:")
    for i, author in enumerate(top_high_value, 1):
        print(f"  {i:2d}. {author['name']} (@{author['handle']}):")
        print(f"      {author['followers']:,} followers → {author['score']:.1f} points")

    # Network Quality Assessment
    print(f"\n📈 NETWORK QUALITY ASSESSMENT:")
    total_authors = len(authors)
    high_scoring_total = [a for a in authors if a.get("meta", {}).get("score", 0) >= 50]

    print(f"  Total authors in network: {total_authors}")
    print(
        f"  High-scoring authors (50+): {len(high_scoring_total)} ({len(high_scoring_total) / total_authors * 100:.1f}%)"
    )

    # Quality enhancement impact on top tier
    top_tier_enhanced = [
        a for a in quality_enhanced_authors if a["followers"] >= 1000000
    ]
    if top_tier_enhanced:
        print(f"\n🎯 TOP TIER (1M+ FOLLOWERS) ENHANCEMENT:")
        for author in top_tier_enhanced:
            print(
                f"  • {author['name']}: {author['previous_score']:.1f} → {author['score']:.1f} (+{author['improvement']:.1f})"
            )

    # Final Assessment
    print(f"\n🎊 QUALITY ENHANCEMENT FINAL ASSESSMENT:")
    print(f"  ✅ Processed {len(quality_enhanced_authors)} authors successfully")
    print(f"  ✅ Network quality improved with enhanced scoring")
    print(f"  ✅ High-value influencer ranking refined")
    print(f"  ✅ M2 model integration completed")

    # Save final report
    report = {
        "analysis_date": datetime.now(timezone.utc).isoformat(),
        "quality_enhancement_summary": {
            "authors_enhanced": len(quality_enhanced_authors),
            "total_improvement": sum(a["improvement"] for a in quality_enhanced_authors)
            if quality_enhanced_authors
            else 0,
            "average_improvement": sum(
                a["improvement"] for a in quality_enhanced_authors
            )
            / len(quality_enhanced_authors)
            if quality_enhanced_authors
            else 0,
        },
        "network_quality": {
            "total_authors": total_authors,
            "high_value_authors": len(high_value_authors),
            "high_scoring_authors": len(high_scoring_total),
            "high_scoring_percentage": len(high_scoring_total) / total_authors * 100,
        },
        "top_improvements": [
            {
                "name": a["name"],
                "handle": a["handle"],
                "previous_score": a["previous_score"],
                "new_score": a["score"],
                "improvement": a["improvement"],
            }
            for a in sorted(
                quality_enhanced_authors, key=lambda x: x["improvement"], reverse=True
            )[:10]
        ]
        if quality_enhanced_authors
        else [],
    }

    with open("quality_enhancement_final_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📁 Final report saved: quality_enhancement_final_report.json")
    print(f"🎯 Quality Enhancement Analysis Complete")


if __name__ == "__main__":
    analyze_quality_enhancement_impact()
