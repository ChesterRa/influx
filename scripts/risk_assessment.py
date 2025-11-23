#!/usr/bin/env python3
"""
Risk Assessment Tool
Implements comprehensive risk flagging based on content analysis
"""

import json
import sys
import re
import yaml
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import Counter


class RiskAssessment:
    """Comprehensive risk assessment for influencer accounts"""

    def __init__(self):
        self.risk_rules = self._load_risk_rules()
        self.brand_rules = self._load_brand_rules()

    def _load_risk_rules(self) -> Dict[str, Any]:
        """Load risk assessment rules"""
        try:
            with open("lists/rules/risk_terms.yml", "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load risk rules: {e}", file=sys.stderr)
            return {}

    def _load_brand_rules(self) -> Dict[str, Any]:
        """Load brand heuristics for context"""
        try:
            with open("lists/rules/brand_heuristics.yml", "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load brand rules: {e}", file=sys.stderr)
            return {}

    def assess_risk(self, record: Dict[str, Any]) -> List[str]:
        """Assess risk flags for a single record"""
        risk_flags = []

        # Get text fields for analysis
        handle = record.get("handle", "").lower()
        name = record.get("name", "").lower()
        bio = record.get("description", "").lower()
        location = record.get("location", "").lower()

        # Assess each risk category
        for category, rules in self.risk_rules.items():
            if category in ["version", "processing_rules"]:
                continue

            flags = self._assess_category(category, rules, handle, name, bio, location)
            risk_flags.extend(flags)

        # Remove duplicates while preserving order
        seen = set()
        unique_flags = []
        for flag in risk_flags:
            if flag not in seen:
                seen.add(flag)
                unique_flags.append(flag)

        return unique_flags

    def _assess_category(
        self,
        category: str,
        rules: Dict[str, Any],
        handle: str,
        name: str,
        bio: str,
        location: str,
    ) -> List[str]:
        """Assess risk for a specific category"""
        flags = []

        if not isinstance(rules, dict):
            return flags

        # Bio keywords
        bio_keywords = rules.get("bio_keywords", [])
        if isinstance(bio_keywords, list):
            for keyword in bio_keywords:
                if keyword.lower() in bio:
                    flag_name = rules.get("flag_name", category)
                    if flag_name not in flags:
                        flags.append(flag_name)
                    break

        # Name keywords
        name_keywords = rules.get("name_keywords", [])
        if isinstance(name_keywords, list):
            for keyword in name_keywords:
                if keyword.lower() in name:
                    flag_name = rules.get("flag_name", category)
                    if flag_name not in flags:
                        flags.append(flag_name)
                    break

        # Name patterns (regex)
        name_patterns = rules.get("name_patterns", [])
        if isinstance(name_patterns, list):
            for pattern in name_patterns:
                if re.search(pattern.lower(), name, re.IGNORECASE):
                    flag_name = rules.get("flag_name", category)
                    if flag_name not in flags:
                        flags.append(flag_name)
                    break

        # Emoji patterns
        emoji_patterns = rules.get("emoji_patterns", [])
        if isinstance(emoji_patterns, list):
            for pattern in emoji_patterns:
                if re.search(pattern, bio):
                    flag_name = rules.get("flag_name", category)
                    if flag_name not in flags:
                        flags.append(flag_name)
                    break

        # Excessive hashtags
        excessive_hashtags = rules.get("excessive_hashtags", 0)
        if excessive_hashtags > 0:
            hashtag_count = bio.count("#")
            if hashtag_count >= excessive_hashtags:
                flag_name = rules.get("flag_name", category)
                if flag_name not in flags:
                    flags.append(flag_name)

        return flags

    def assess_dataset(
        self, dataset_path: str, output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Assess risk for entire dataset"""
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

        # Assess risk for each record
        risk_results = []
        risk_distribution = Counter()
        total_records = len(records)

        for record in records:
            risk_flags = self.assess_risk(record)

            # Update record with risk flags
            record_with_risk = record.copy()
            record_with_risk["risk_flags"] = risk_flags

            # Determine if should be auto-excluded
            auto_exclude = self._should_auto_exclude(risk_flags)
            if auto_exclude:
                record_with_risk["banned"] = True

            risk_results.append(record_with_risk)

            # Track distribution
            for flag in risk_flags:
                risk_distribution[flag] += 1

        # Calculate statistics
        records_with_risks = sum(1 for r in risk_results if r["risk_flags"])
        records_banned = sum(1 for r in risk_results if r.get("banned", False))

        assessment = {
            "dataset_path": str(dataset_path),
            "total_records": total_records,
            "records_with_risk_flags": records_with_risks,
            "records_banned": records_banned,
            "risk_coverage": (records_with_risks / total_records) * 100
            if total_records > 0
            else 0,
            "ban_rate": (records_banned / total_records) * 100
            if total_records > 0
            else 0,
            "risk_distribution": dict(risk_distribution),
            "top_risks": risk_distribution.most_common(10),
            "assessment_timestamp": str(Path().resolve()),
        }

        # Write output if specified
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Sort by risk (safe records first)
            risk_results.sort(
                key=lambda r: (
                    1 if r.get("banned", False) else 0,  # Banned records last
                    len(r.get("risk_flags", [])),  # More risk flags last
                    -r.get("quality_score", 0),  # Lower quality last
                    r.get("handle", ""),
                )
            )

            lines = [json.dumps(r, ensure_ascii=False) for r in risk_results]
            output_file.write_text("\n".join(lines) + "\n")

            assessment["output_path"] = str(output_path)
            assessment["output_sha256"] = self._calculate_sha256(str(output_file))

        return assessment

    def _should_auto_exclude(self, risk_flags: List[str]) -> bool:
        """Determine if record should be auto-excluded based on risk flags"""
        if not risk_flags:
            return False

        # Check processing rules
        processing_rules = self.risk_rules.get("processing_rules", {})

        # Multi-flag threshold
        multi_flag_threshold = processing_rules.get("multi_flag_threshold", 2)
        if len(risk_flags) >= multi_flag_threshold:
            return True

        # Check individual flag severity
        for flag in risk_flags:
            # Find the rule for this flag
            for category, rules in self.risk_rules.items():
                if isinstance(rules, dict) and rules.get("flag_name") == flag:
                    auto_exclude = rules.get("auto_exclude", False)
                    severity = rules.get("severity", "low")

                    # Auto-exclude for high severity or explicit auto_exclude
                    if auto_exclude or severity in ["high", "critical"]:
                        return True
                    break

        return False

    def _calculate_sha256(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        import hashlib

        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def generate_risk_report(
        self, dataset_path: str, output_path: Optional[str] = None
    ) -> str:
        """Generate comprehensive risk assessment report"""
        try:
            assessment = self.assess_dataset(dataset_path, output_path)

            report = ["# Risk Assessment Report\n"]
            report.append(f"Dataset: {assessment['dataset_path']}")
            report.append(f"Assessed: {assessment['assessment_timestamp']}\n")

            # Executive Summary
            report.append("## 🚨 Executive Summary\n")
            report.append(f"- **Total Records**: {assessment['total_records']}")
            report.append(
                f"- **Records with Risk Flags**: {assessment['records_with_risk_flags']} ({assessment['risk_coverage']:.1f}%)"
            )
            report.append(
                f"- **Records Banned**: {assessment['records_banned']} ({assessment['ban_rate']:.1f}%)"
            )
            report.append(f"- **Risk Coverage**: {assessment['risk_coverage']:.1f}%\n")

            # Risk Distribution
            if assessment["risk_distribution"]:
                report.append("## 📊 Risk Distribution\n")
                for risk, count in assessment["top_risks"]:
                    percentage = (count / assessment["total_records"]) * 100
                    report.append(f"- **{risk}**: {count} records ({percentage:.1f}%)")
                report.append("")

            # Recommendations
            report.append("## 🎯 Recommendations\n")

            if assessment["ban_rate"] > 5:
                report.append("- 🔴 HIGH BAN RATE: Review risk assessment rules")
            elif assessment["ban_rate"] > 2:
                report.append("- 🟡 MODERATE BAN RATE: Monitor risk patterns")
            else:
                report.append("- 🟢 LOW BAN RATE: Risk assessment working well")

            if assessment["risk_coverage"] < 10:
                report.append("- ⚠️ LOW RISK COVERAGE: Consider expanding risk rules")
            elif assessment["risk_coverage"] > 30:
                report.append("- ⚠️ HIGH RISK COVERAGE: Review seed quality")
            else:
                report.append("- ✅ APPROPRIATE RISK COVERAGE: Good balance")

            report.append("")

            # Sample flagged records
            if output_path and Path(output_path).exists():
                report.append("## 📋 Sample Flagged Records\n")

                with open(output_path) as f:
                    flagged_records = []
                    for line in f.readlines()[:10]:  # First 10 records
                        if line.strip():
                            record = json.loads(line)
                            if record.get("risk_flags") or record.get("banned"):
                                flagged_records.append(record)

                for i, record in enumerate(flagged_records[:5], 1):
                    handle = record.get("handle", "unknown")
                    risks = record.get("risk_flags", [])
                    banned = record.get("banned", False)
                    status = "🚫 BANNED" if banned else "⚠️ FLAGGED"

                    report.append(f"{i}. **{handle}** - {status}")
                    report.append(
                        f"   - Risks: {', '.join(risks) if risks else 'None'}"
                    )
                    report.append(
                        f"   - Followers: {record.get('followers_count', 'N/A')}"
                    )
                    report.append("")

            return "\n".join(report)

        except Exception as e:
            return f"# Risk Assessment Report\n\nError: {e}"


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python risk_assessment.py <dataset.jsonl> [output.jsonl] [--report]"
        )
        print("  --report: Generate detailed risk report")
        sys.exit(1)

    dataset_path = sys.argv[1]
    output_path = (
        sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
    )
    generate_report = "--report" in sys.argv

    assessor = RiskAssessment()

    if generate_report:
        report = assessor.generate_risk_report(dataset_path, output_path)
        print(report)
    else:
        assessment = assessor.assess_dataset(dataset_path, output_path)
        print(json.dumps(assessment, indent=2))


if __name__ == "__main__":
    main()
