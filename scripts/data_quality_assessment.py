#!/usr/bin/env python3
"""
Data Quality Assessment Tool
Comprehensive analysis of dataset quality and processing readiness
"""

import json
import sys
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime


class DataQualityAssessment:
    """Comprehensive data quality assessment for influx dataset"""

    def __init__(self):
        self.quality_metrics = {}

    def assess_dataset_quality(self, dataset_path: str) -> Dict[str, Any]:
        """Perform comprehensive quality assessment"""
        dataset_file = Path(dataset_path)

        if not dataset_file.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

        records = []
        for line in dataset_file.read_text().splitlines():
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON line: {e}", file=sys.stderr)

        return self._analyze_records(records, dataset_path)

    def _analyze_records(
        self, records: List[Dict[str, Any]], source_path: str
    ) -> Dict[str, Any]:
        """Analyze dataset records for quality metrics"""

        # Basic counts
        total_records = len(records)
        if total_records == 0:
            return {"error": "No records found"}

        # Field completeness
        field_completeness = {}
        for field in [
            "id",
            "handle",
            "name",
            "verified",
            "followers_count",
            "is_org",
            "is_official",
            "entry_threshold_passed",
            "quality_score",
            "topic_tags",
            "risk_flags",
            "meta",
        ]:
            present = sum(1 for r in records if r.get(field) is not None)
            field_completeness[field] = {
                "count": present,
                "percentage": (present / total_records) * 100,
            }

        # Schema compliance
        schema_compliant = 0
        verified_field_issues = 0
        missing_required_fields = 0

        for record in records:
            # Check verified field type
            if "verified" in record:
                if not isinstance(record["verified"], str):
                    verified_field_issues += 1
                else:
                    schema_compliant += 1

            # Check required fields
            required_fields = ["id", "handle", "followers_count"]
            missing = [f for f in required_fields if not record.get(f)]
            if missing:
                missing_required_fields += 1

        # Quality gate compliance
        entry_threshold_passed = sum(
            1 for r in records if r.get("entry_threshold_passed", False)
        )
        org_accounts = sum(1 for r in records if r.get("is_org", False))
        official_accounts = sum(1 for r in records if r.get("is_official", False))

        # Follower distribution
        followers = [
            r.get("followers_count", 0)
            for r in records
            if isinstance(r.get("followers_count"), int)
        ]
        follower_stats = {
            "min": min(followers) if followers else 0,
            "max": max(followers) if followers else 0,
            "median": sorted(followers)[len(followers) // 2] if followers else 0,
            "mean": sum(followers) // len(followers) if followers else 0,
            "over_50k": sum(1 for f in followers if f >= 50000),
            "over_100k": sum(1 for f in followers if f >= 100000),
            "over_1m": sum(1 for f in followers if f >= 1000000),
        }

        # Verification distribution
        verification_counts = Counter(r.get("verified", "none") for r in records)

        # Topic diversity
        all_topics = []
        for record in records:
            topics = record.get("topic_tags", [])
            if isinstance(topics, list):
                all_topics.extend(topics)
        topic_diversity = Counter(all_topics)

        # Risk flags
        all_risks = []
        for record in records:
            risks = record.get("risk_flags", [])
            if isinstance(risks, list):
                all_risks.extend(risks)
        risk_distribution = Counter(all_risks)

        # Quality score distribution
        quality_scores = [
            r.get("quality_score", 0)
            for r in records
            if isinstance(r.get("quality_score"), (int, float))
        ]
        quality_stats = {
            "min": min(quality_scores) if quality_scores else 0,
            "max": max(quality_scores) if quality_scores else 0,
            "median": sorted(quality_scores)[len(quality_scores) // 2]
            if quality_scores
            else 0,
            "mean": sum(quality_scores) // len(quality_scores) if quality_scores else 0,
            "high_quality": sum(1 for s in quality_scores if s >= 70),
            "medium_quality": sum(1 for s in quality_scores if 40 <= s < 70),
            "low_quality": sum(1 for s in quality_scores if s < 40),
        }

        # Data freshness
        last_refresh_dates = []
        for record in records:
            meta = record.get("meta", {})
            if isinstance(meta, dict) and "last_refresh_at" in meta:
                try:
                    last_refresh_dates.append(meta["last_refresh_at"])
                except:
                    pass

        freshness = {
            "records_with_timestamp": len(last_refresh_dates),
            "most_recent": max(last_refresh_dates) if last_refresh_dates else None,
            "oldest": min(last_refresh_dates) if last_refresh_dates else None,
        }

        # Provenance analysis
        sources = []
        for record in records:
            meta = record.get("meta", {})
            if isinstance(meta, dict) and "sources" in meta:
                record_sources = meta["sources"]
                if isinstance(record_sources, list):
                    for source in record_sources:
                        if isinstance(source, dict) and "method" in source:
                            sources.append(source["method"])
        source_distribution = Counter(sources)

        # Overall quality score (0-100)
        overall_quality = self._calculate_overall_quality(
            {
                "field_completeness": field_completeness,
                "schema_compliance_rate": (schema_compliant / total_records) * 100,
                "entry_threshold_rate": (entry_threshold_passed / total_records) * 100,
                "org_rate": (org_accounts / total_records) * 100,
                "quality_score_avg": quality_stats["mean"],
                "data_freshness": len(last_refresh_dates) / total_records * 100,
            }
        )

        return {
            "dataset_path": str(source_path),
            "assessment_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_records": total_records,
                "overall_quality_score": overall_quality,
                "schema_compliance_rate": (schema_compliant / total_records) * 100,
                "entry_threshold_rate": (entry_threshold_passed / total_records) * 100,
            },
            "field_completeness": field_completeness,
            "schema_issues": {
                "verified_field_issues": verified_field_issues,
                "missing_required_fields": missing_required_fields,
            },
            "quality_gates": {
                "entry_threshold_passed": entry_threshold_passed,
                "org_accounts": org_accounts,
                "official_accounts": official_accounts,
            },
            "follower_distribution": follower_stats,
            "verification_distribution": dict(verification_counts),
            "topic_diversity": dict(topic_diversity),
            "risk_distribution": dict(risk_distribution),
            "quality_score_distribution": quality_stats,
            "data_freshness": freshness,
            "source_distribution": dict(source_distribution),
            "recommendations": self._generate_recommendations(
                {
                    "overall_quality": overall_quality,
                    "schema_compliance": (schema_compliant / total_records) * 100,
                    "entry_threshold_rate": (entry_threshold_passed / total_records)
                    * 100,
                    "org_rate": (org_accounts / total_records) * 100,
                    "field_completeness": field_completeness,
                }
            ),
        }

    def _calculate_overall_quality(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score (0-100)"""
        score = 0

        # Field completeness (30 points)
        avg_completeness = sum(
            v["percentage"] for v in metrics["field_completeness"].values()
        ) / len(metrics["field_completeness"])
        score += (avg_completeness / 100) * 30

        # Schema compliance (25 points)
        score += (metrics["schema_compliance_rate"] / 100) * 25

        # Entry threshold compliance (20 points)
        score += (metrics["entry_threshold_rate"] / 100) * 20

        # Low org account rate (15 points) - lower is better
        org_penalty = min(metrics["org_rate"], 20)  # Cap at 20%
        score += ((20 - org_penalty) / 20) * 15

        # Data freshness (10 points)
        score += (metrics["data_freshness"] / 100) * 10

        return min(100, max(0, score))

    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        if metrics["overall_quality"] < 70:
            recommendations.append("🔴 LOW QUALITY: Major improvements needed")
        elif metrics["overall_quality"] < 85:
            recommendations.append("🟡 MEDIUM QUALITY: Some improvements recommended")
        else:
            recommendations.append("🟢 HIGH QUALITY: Dataset meets standards")

        if metrics["schema_compliance"] < 95:
            recommendations.append(
                "Fix schema violations (verified field type, missing fields)"
            )

        if metrics["entry_threshold_rate"] < 90:
            recommendations.append("Filter accounts not meeting entry thresholds")

        if metrics["org_rate"] > 10:
            recommendations.append("Review and filter organization accounts")

        # Field-specific recommendations
        low_completeness = [
            k for k, v in metrics["field_completeness"].items() if v["percentage"] < 90
        ]
        if low_completeness:
            recommendations.append(
                f"Improve completeness of: {', '.join(low_completeness)}"
            )

        return recommendations

    def generate_quality_report(self, dataset_path: str) -> str:
        """Generate comprehensive quality report"""
        try:
            assessment = self.assess_dataset_quality(dataset_path)

            report = ["# Data Quality Assessment Report\n"]
            report.append(f"Dataset: {assessment['dataset_path']}")
            report.append(f"Assessed: {assessment['assessment_timestamp']}\n")

            # Executive Summary
            summary = assessment["summary"]
            report.append("## 📊 Executive Summary\n")
            report.append(
                f"- **Overall Quality Score**: {summary['overall_quality_score']:.1f}/100"
            )
            report.append(f"- **Total Records**: {summary['total_records']}")
            report.append(
                f"- **Schema Compliance**: {summary['schema_compliance_rate']:.1f}%"
            )
            report.append(
                f"- **Entry Threshold Compliance**: {summary['entry_threshold_rate']:.1f}%\n"
            )

            # Recommendations
            report.append("## 🎯 Recommendations\n")
            for rec in assessment["recommendations"]:
                report.append(f"- {rec}")
            report.append("")

            # Field Completeness
            report.append("## 📋 Field Completeness\n")
            for field, stats in assessment["field_completeness"].items():
                status = (
                    "✅"
                    if stats["percentage"] >= 90
                    else "⚠️"
                    if stats["percentage"] >= 70
                    else "❌"
                )
                report.append(
                    f"- {status} **{field}**: {stats['percentage']:.1f}% ({stats['count']}/{summary['total_records']})"
                )
            report.append("")

            # Quality Gates
            report.append("## 🚪 Quality Gate Compliance\n")
            gates = assessment["quality_gates"]
            report.append(
                f"- **Entry Threshold Passed**: {gates['entry_threshold_passed']}/{summary['total_records']} ({summary['entry_threshold_rate']:.1f}%)"
            )
            report.append(
                f"- **Org Accounts**: {gates['org_accounts']}/{summary['total_records']} ({(gates['org_accounts'] / summary['total_records'] * 100):.1f}%)"
            )
            report.append(
                f"- **Official Accounts**: {gates['official_accounts']}/{summary['total_records']} ({(gates['official_accounts'] / summary['total_records'] * 100):.1f}%)"
            )
            report.append("")

            # Schema Issues
            if (
                assessment["schema_issues"]["verified_field_issues"] > 0
                or assessment["schema_issues"]["missing_required_fields"] > 0
            ):
                report.append("## ⚠️ Schema Issues\n")
                if assessment["schema_issues"]["verified_field_issues"] > 0:
                    report.append(
                        f"- **Verified Field Issues**: {assessment['schema_issues']['verified_field_issues']} records"
                    )
                if assessment["schema_issues"]["missing_required_fields"] > 0:
                    report.append(
                        f"- **Missing Required Fields**: {assessment['schema_issues']['missing_required_fields']} records"
                    )
                report.append("")

            # Top Topics
            if assessment["topic_diversity"]:
                report.append("## 🏷️ Top Topics\n")
                topics = sorted(
                    assessment["topic_diversity"].items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:10]
                for topic, count in topics:
                    report.append(f"- **{topic}**: {count} authors")
                report.append("")

            # Quality Score Distribution
            quality_dist = assessment["quality_score_distribution"]
            report.append("## 📈 Quality Score Distribution\n")
            report.append(f"- **Average**: {quality_dist['mean']:.1f}")
            report.append(
                f"- **High Quality (≥70)**: {quality_dist['high_quality']} authors"
            )
            report.append(
                f"- **Medium Quality (40-69)**: {quality_dist['medium_quality']} authors"
            )
            report.append(
                f"- **Low Quality (<40)**: {quality_dist['low_quality']} authors"
            )
            report.append("")

            return "\n".join(report)

        except Exception as e:
            return f"# Data Quality Assessment Report\n\nError: {e}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python data_quality_assessment.py <dataset.jsonl> [--report]")
        print("  --report: Generate detailed quality report")
        sys.exit(1)

    dataset_path = sys.argv[1]
    generate_report = "--report" in sys.argv

    assessor = DataQualityAssessment()

    if generate_report:
        report = assessor.generate_quality_report(dataset_path)
        print(report)
    else:
        assessment = assessor.assess_dataset_quality(dataset_path)
        print(json.dumps(assessment, indent=2))


if __name__ == "__main__":
    main()
