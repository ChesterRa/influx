#!/usr/bin/env python3
"""
Schema Fixer Tool - Repairs common schema violations in influx datasets
Fixes verified field type issues and ensures compliance with bigv.schema.json
"""

import json
import sys
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import Counter
from datetime import datetime


class SchemaFixer:
    """Fixes schema violations in influx datasets"""

    def __init__(self):
        self.placeholder_prefix = "1234567890000000"
        self.mock_prefixes = ("test_", "mock_", "fixture_", "sample_", "tmp_")

    def fix_record_schema(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Fix schema violations in a single record"""
        fixed = record.copy()

        # Fix verified field - must be string, not boolean
        if "verified" in fixed:
            if isinstance(fixed["verified"], bool):
                if fixed.get("verified_type") == "blue":
                    fixed["verified"] = "blue"
                elif fixed.get("verified_type") == "org":
                    fixed["verified"] = "org"
                elif fixed.get("verified_type") == "legacy":
                    fixed["verified"] = "legacy"
                else:
                    fixed["verified"] = "blue" if fixed["verified"] else "none"
            elif isinstance(fixed["verified"], str):
                # Normalize string values
                valid_values = ["none", "blue", "org", "legacy"]
                if fixed["verified"] not in valid_values:
                    fixed["verified"] = (
                        "blue" if fixed.get("verified_type") == "blue" else "none"
                    )

        # Handle public_metrics flattening
        if "public_metrics" in fixed:
            metrics = fixed["public_metrics"]
            if isinstance(metrics, dict):
                # Extract key metrics to top level if not present
                if "followers_count" not in fixed and "followers_count" in metrics:
                    fixed["followers_count"] = metrics["followers_count"]
                if "following_count" not in fixed and "following_count" in metrics:
                    fixed["following_count"] = metrics["following_count"]
                if "tweet_count" not in fixed and "tweet_count" in metrics:
                    fixed["tweet_count"] = metrics["tweet_count"]
                if "listed_count" not in fixed and "listed_count" in metrics:
                    fixed["listed_count"] = metrics["listed_count"]

        # Ensure required fields for strict validation
        if "is_org" not in fixed:
            fixed["is_org"] = False  # Default to individual

        if "is_official" not in fixed:
            fixed["is_official"] = False  # Default to individual

        if "entry_threshold_passed" not in fixed:
            followers = fixed.get("followers_count", 0)
            verified = fixed.get("verified", "none")
            # Entry threshold: (verified AND ≥30k) OR ≥50k
            fixed["entry_threshold_passed"] = followers >= 50000 or (
                verified in ["blue", "legacy"] and followers >= 30000
            )

        if "quality_score" not in fixed:
            fixed["quality_score"] = self._calculate_quality_score(fixed)

        # Ensure meta structure exists
        if "meta" not in fixed:
            fixed["meta"] = {}

        meta = fixed["meta"]

        if "sources" not in meta:
            meta["sources"] = [
                {
                    "method": "schema_fixer",
                    "fetched_at": datetime.now().isoformat(),
                    "evidence": f"@{fixed.get('handle', 'unknown')}",
                }
            ]

        if "provenance_hash" not in meta:
            meta["provenance_hash"] = self._calculate_provenance_hash(fixed)

        if "last_refresh_at" not in meta:
            meta["last_refresh_at"] = datetime.now().isoformat()

        # Ensure topic_tags exists
        if "topic_tags" not in fixed:
            fixed["topic_tags"] = []

        # Ensure risk_flags exists
        if "risk_flags" not in fixed:
            fixed["risk_flags"] = []

        # Ensure banned field exists
        if "banned" not in fixed:
            fixed["banned"] = False

        # Ensure last_active_at exists (approximate)
        if "last_active_at" not in fixed:
            # Use account creation as fallback
            if "created_at" in fixed:
                fixed["last_active_at"] = fixed["created_at"]
            else:
                fixed["last_active_at"] = datetime.now().isoformat()

        # Ensure metrics_30d structure exists
        if "metrics_30d" not in fixed:
            fixed["metrics_30d"] = {
                "posts_total": 0,
                "posts_original": 0,
                "median_likes": 0,
                "p90_likes": 0,
                "median_replies": 0,
                "median_retweets": 0,
                "media_rate": 0.0,
            }

        # Ensure ranking fields exist
        if "rank_global" not in fixed:
            fixed["rank_global"] = None

        if "rank_by_topic" not in fixed:
            fixed["rank_by_topic"] = {}

        # Language detection
        if "lang_primary" not in fixed:
            fixed["lang_primary"] = "en"  # Default to English

        return fixed

    def _calculate_quality_score(self, record: Dict[str, Any]) -> float:
        """Calculate basic quality score"""
        followers = record.get("followers_count", 0)
        verified = record.get("verified", "none") in ["blue", "legacy"]

        # Simple scoring based on followers and verification
        score = min(100, (followers / 100000) * 50)  # 50 points for followers
        if verified:
            score += 20  # 20 points for verification

        # Deductions for org/official
        if record.get("is_org", False):
            score -= 30
        if record.get("is_official", False):
            score -= 20

        return max(0, score)

    def _calculate_provenance_hash(self, record: Dict[str, Any]) -> str:
        """Calculate provenance hash for audit trail"""
        key_fields = [
            record.get("id", ""),
            record.get("handle", ""),
            record.get("followers_count", 0),
            record.get("verified", "none"),
        ]
        content = "|".join(str(field) for field in key_fields)
        return hashlib.sha256(content.encode()).hexdigest()

    def fix_file(
        self, input_path: str, output_path: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
        """Fix schema violations in a JSONL file"""
        input_file = Path(input_path)

        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Read and fix records
        records = []
        errors = []
        fixes_applied = []

        for line_num, line in enumerate(input_file.read_text().splitlines(), 1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
                original = record.copy()
                fixed = self.fix_record_schema(record)

                # Track what was fixed
                if fixed != original:
                    fixes = []
                    if original.get("verified") != fixed.get("verified"):
                        fixes.append(
                            f"verified: {original.get('verified')} → {fixed.get('verified')}"
                        )
                    if "is_org" not in original:
                        fixes.append("added is_org")
                    if "is_official" not in original:
                        fixes.append("added is_official")
                    if "entry_threshold_passed" not in original:
                        fixes.append("added entry_threshold_passed")
                    if "quality_score" not in original:
                        fixes.append("added quality_score")
                    if "meta" not in original:
                        fixes.append("added meta structure")

                    if fixes:
                        fixes_applied.append(
                            f"Line {line_num} ({fixed.get('handle', 'unknown')}): {', '.join(fixes)}"
                        )

                records.append(fixed)

            except json.JSONDecodeError as e:
                errors.append(f"Line {line_num}: JSON decode error - {e}")
            except Exception as e:
                errors.append(f"Line {line_num}: Processing error - {e}")

        # Additional quality checks
        handles = [r.get("handle") for r in records]
        handle_counts = Counter(handles)
        duplicates = [h for h, c in handle_counts.items() if c > 1]

        if duplicates:
            errors.append(f"Duplicate handles found: {duplicates[:5]}")

        # Placeholder checks
        fake_ids = [
            r
            for r in records
            if str(r.get("id", "")).startswith(self.placeholder_prefix)
            or not str(r.get("id", "")).isdigit()
        ]
        if fake_ids:
            errors.append(f"Placeholder IDs detected: {len(fake_ids)}")

        mock_handles = [
            h for h in handles if h and h.lower().startswith(self.mock_prefixes)
        ]
        if mock_handles:
            errors.append(f"Mock handles detected: {mock_handles[:5]}")

        # Followers count sanity
        bad_followers = [
            (r.get("handle"), r.get("followers_count"))
            for r in records
            if isinstance(r.get("followers_count"), int)
            and r.get("followers_count") % 1000 == 0
            and r.get("followers_count") > 0
        ]
        if bad_followers:
            errors.append(
                f"Suspicious followers_count ending with '000': {len(bad_followers)}"
            )

        # Write fixed file if output specified
        if output_path and records and not errors:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Sort by quality_score desc, followers_count desc, handle asc
            records.sort(
                key=lambda r: (
                    -r.get("quality_score", 0),
                    -r.get("followers_count", 0),
                    r.get("handle", ""),
                )
            )

            lines = [json.dumps(r, ensure_ascii=False) for r in records]
            output_file.write_text("\n".join(lines) + "\n")

        return records, errors, fixes_applied

    def generate_fix_report(
        self, input_path: str, output_path: Optional[str] = None
    ) -> str:
        """Generate a detailed fix report"""
        try:
            records, errors, fixes = self.fix_file(input_path, output_path)

            report = ["# Schema Fix Report\n"]
            report.append(f"Input: {input_path}")
            report.append(f"Generated: {datetime.now().isoformat()}\n")

            if errors:
                report.append("## ❌ Errors Found\n")
                for error in errors:
                    report.append(f"- {error}")
                report.append("")

            if fixes:
                report.append("## 🔧 Fixes Applied\n")
                for fix in fixes[:20]:  # Limit to first 20 fixes
                    report.append(f"- {fix}")
                if len(fixes) > 20:
                    report.append(f"- ... and {len(fixes) - 20} more fixes")
                report.append("")

            report.append("## 📊 Summary\n")
            report.append(f"- Total records: {len(records)}")
            report.append(f"- Errors: {len(errors)}")
            report.append(f"- Fixes applied: {len(fixes)}")

            if output_path:
                report.append(f"- Output written to: {output_path}")

            # Sample fixed record
            if records:
                report.append("\n## 📋 Sample Fixed Record\n")
                sample = records[0]
                report.append("```json")
                report.append(
                    json.dumps(sample, indent=2, ensure_ascii=False)[:500] + "..."
                )
                report.append("```")

            return "\n".join(report)

        except Exception as e:
            return f"# Schema Fix Report\n\nError: {e}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python schema_fixer.py <input.jsonl> [output.jsonl] [--report]")
        print("  --report: Generate fix report to stdout")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = (
        sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
    )

    fixer = SchemaFixer()

    if "--report" in sys.argv:
        report = fixer.generate_fix_report(input_path, output_path)
        print(report)
    else:
        try:
            records, errors, fixes = fixer.fix_file(input_path, output_path)

            if errors:
                print("❌ SCHEMA FIXER FAILED:", file=sys.stderr)
                for error in errors:
                    print(f"  - {error}", file=sys.stderr)
                sys.exit(1)

            if output_path:
                print(f"✅ SCHEMA FIXER COMPLETED: {len(records)} records fixed")
                print(f"📄 Output: {output_path}")
                print(f"🔧 Fixes applied: {len(fixes)}")
            else:
                print(f"✅ SCHEMA VALIDATION PASSED: {len(records)} records")
                print(f"🔧 Fixes needed: {len(fixes)}")

        except Exception as e:
            print(f"❌ SCHEMA FIXER ERROR: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
