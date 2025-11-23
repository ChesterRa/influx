#!/usr/bin/env python3
"""
Comprehensive Quality Control System for Influx Dataset
Implements P0 quality control mechanisms per Foreman directive
"""

import json
import sys
import hashlib
import re
import argparse
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime


class QualityController:
    """Comprehensive quality control for influx dataset"""

    def __init__(self, schema_path: str = "schema/bigv.schema.json"):
        self.schema_path = Path(schema_path)
        self.placeholder_prefix = "1234567890000000"
        self.mock_prefixes = ("test_", "mock_", "fixture_", "sample_", "tmp_")
        self.brand_heuristics = self._load_brand_rules()
        self.risk_terms = self._load_risk_terms()

    def _load_brand_rules(self) -> List[str]:
        """Load brand heuristics from rules file"""
        try:
            with open("lists/rules/brand_heuristics.yml", "r") as f:
                content = f.read()
                # Extract patterns from YAML (simplified)
                patterns = []
                for line in content.split("\n"):
                    if ":" in line and not line.strip().startswith("#"):
                        pattern = line.split(":")[0].strip()
                        if pattern and not pattern.startswith("-"):
                            patterns.append(pattern.lower())
                return patterns
        except FileNotFoundError:
            return [
                "official",
                "team",
                "company",
                "corp",
                "inc",
                "llc",
                "news",
                "media",
            ]

    def _load_risk_terms(self) -> List[str]:
        """Load risk terms from rules file"""
        try:
            with open("lists/rules/risk_terms.yml", "r") as f:
                content = f.read()
                terms = []
                for line in content.split("\n"):
                    if ":" in line and not line.strip().startswith("#"):
                        term = line.split(":")[0].strip()
                        if term and not term.startswith("-"):
                            terms.append(term.lower())
                return terms
        except FileNotFoundError:
            return ["nsfw", "adult", "hate", "political", "spam"]

    def validate_dataset(
        self, data_path: str, manifest_path: str
    ) -> Tuple[bool, List[str]]:
        """Comprehensive dataset validation"""
        errors = []
        warnings = []

        # Load data
        data_path_obj = Path(data_path)
        if not data_path_obj.exists():
            return False, [f"Dataset file not found: {data_path}"]

        data = []
        try:
            for line in data_path_obj.read_text().splitlines():
                if line.strip():
                    data.append(json.loads(line))
        except json.JSONDecodeError as e:
            return False, [f"JSON decode error: {e}"]

        # Load manifest
        manifest_path_obj = Path(manifest_path)
        if not manifest_path_obj.exists():
            return False, [f"Manifest file not found: {manifest_path}"]

        try:
            manifest = json.loads(manifest_path_obj.read_text())
        except json.JSONDecodeError as e:
            return False, [f"Manifest JSON decode error: {e}"]

        # 1. Basic integrity checks
        integrity_errors = self._check_integrity(data)
        errors.extend(integrity_errors)

        # 2. Schema compliance
        schema_errors = self._check_schema_compliance(data)
        errors.extend(schema_errors)

        # 3. Quality gates
        quality_errors = self._check_quality_gates(data)
        errors.extend(quality_errors)

        # 4. Manifest consistency
        manifest_errors = self._check_manifest_consistency(
            data, manifest, data_path_obj
        )
        errors.extend(manifest_errors)

        # 5. Business rule validation
        business_errors = self._check_business_rules(data)
        errors.extend(business_errors)

        # 6. Provenance validation
        provenance_errors = self._check_provenance(data)
        errors.extend(provenance_errors)

        success = len(errors) == 0
        return success, errors + warnings

    def _check_integrity(self, data: List[Dict]) -> List[str]:
        """Check data integrity"""
        errors = []

        # Duplicate handles
        handles = [item.get("handle") for item in data if item.get("handle")]
        handle_counts = Counter(handles)
        duplicates = [h for h, count in handle_counts.items() if count > 1]
        if duplicates:
            errors.append(
                f"DUPLICATE_HANDLES: {len(duplicates)} duplicates found: {duplicates[:5]}"
            )

        # Placeholder IDs
        placeholder_ids = [
            item.get("id")
            for item in data
            if str(item.get("id", "")).startswith(self.placeholder_prefix)
            or not str(item.get("id", "")).isdigit()
        ]
        if placeholder_ids:
            errors.append(
                f"PLACEHOLDER_IDS: {len(placeholder_ids)} placeholder IDs detected"
            )

        # Mock/test handles
        mock_handles = [
            h for h in handles if h and h.lower().startswith(self.mock_prefixes)
        ]
        if mock_handles:
            errors.append(
                f"MOCK_HANDLES: {len(mock_handles)} mock/test handles: {mock_handles[:5]}"
            )

        # Suspicious follower counts
        suspicious_followers = []
        for item in data:
            fc = item.get("followers_count")
            if isinstance(fc, int) and fc > 0 and fc % 1000 == 0:
                suspicious_followers.append((item.get("handle"), fc))
        if suspicious_followers:
            errors.append(
                f"SUSPICIOUS_FOLLOWERS: {len(suspicious_followers)} with round numbers ending in 000"
            )

        return errors

    def _check_schema_compliance(self, data: List[Dict]) -> List[str]:
        """Check schema compliance"""
        errors = []

        required_fields = [
            "id",
            "handle",
            "name",
            "verified",
            "followers_count",
            "is_org",
            "is_official",
            "lang_primary",
            "topic_tags",
            "meta",
        ]

        for i, item in enumerate(data):
            # Required fields
            for field in required_fields:
                if field not in item:
                    errors.append(
                        f"MISSING_FIELD: Record {i} missing required field '{field}'"
                    )

            # Data types
            if not isinstance(item.get("followers_count"), int):
                errors.append(
                    f"INVALID_TYPE: Record {i} followers_count must be integer"
                )

            if not isinstance(item.get("is_org"), bool):
                errors.append(f"INVALID_TYPE: Record {i} is_org must be boolean")

            if not isinstance(item.get("is_official"), bool):
                errors.append(f"INVALID_TYPE: Record {i} is_official must be boolean")

            # Meta structure
            meta = item.get("meta", {})
            if not isinstance(meta, dict):
                errors.append(f"INVALID_TYPE: Record {i} meta must be object")
            else:
                if "score" not in meta:
                    errors.append(f"MISSING_FIELD: Record {i} meta.score missing")
                if not isinstance(meta.get("score"), (int, float)):
                    errors.append(f"INVALID_TYPE: Record {i} meta.score must be number")

        return errors

    def _check_quality_gates(self, data: List[Dict]) -> List[str]:
        """Check quality gates"""
        errors = []

        for i, item in enumerate(data):
            # Entry threshold
            followers = item.get("followers_count", 0)
            verified = item.get("verified")
            is_verified = verified in ["blue", "org", "legacy"]

            threshold_met = (is_verified and followers >= 30000) or followers >= 50000
            if not threshold_met:
                errors.append(
                    f"THRESHOLD_FAILED: Record {i} ({item.get('handle')}) below entry threshold"
                )

            # Brand/organization exclusion
            if item.get("is_org", True):
                errors.append(
                    f"ORG_EXCLUDED: Record {i} ({item.get('handle')}) is_org=true not allowed"
                )

            # Official account exclusion
            if item.get("is_official", True):
                errors.append(
                    f"OFFICIAL_EXCLUDED: Record {i} ({item.get('handle')}) is_official=true not allowed"
                )

        return errors

    def _check_manifest_consistency(
        self, data: List[Dict], manifest: Dict, data_path: Path
    ) -> List[str]:
        """Check manifest consistency"""
        errors = []

        # Count consistency
        manifest_count = manifest.get("count")
        if manifest_count is not None and manifest_count != len(data):
            errors.append(
                f"MANIFEST_COUNT_MISMATCH: manifest={manifest_count}, actual={len(data)}"
            )

        # SHA256 consistency
        actual_sha = hashlib.sha256(data_path.read_bytes()).hexdigest()
        manifest_sha = manifest.get("sha256")
        if manifest_sha and manifest_sha != actual_sha:
            errors.append(
                f"MANIFEST_SHA_MISMATCH: manifest={manifest_sha}, actual={actual_sha}"
            )

        return errors

    def _check_business_rules(self, data: List[Dict]) -> List[str]:
        """Check business rules"""
        errors = []

        for i, item in enumerate(data):
            handle = item.get("handle", "").lower()
            name = item.get("name", "").lower()

            # Brand heuristics
            for pattern in self.brand_heuristics:
                if pattern in handle or pattern in name:
                    errors.append(
                        f"BRAND_HEURISTIC: Record {i} matches brand pattern '{pattern}'"
                    )
                    break

            # Risk terms
            bio = item.get("bio", "").lower() if item.get("bio") else ""
            for term in self.risk_terms:
                if term in handle or term in name or term in bio:
                    errors.append(f"RISK_TERM: Record {i} contains risk term '{term}'")
                    break

        return errors

    def _check_provenance(self, data: List[Dict]) -> List[str]:
        """Check provenance information"""
        errors = []

        for i, item in enumerate(data):
            meta = item.get("meta", {})

            # Sources array
            sources = meta.get("sources", [])
            if not isinstance(sources, list) or len(sources) == 0:
                errors.append(f"MISSING_SOURCES: Record {i} missing sources array")
                continue

            # Source structure
            for j, source in enumerate(sources):
                if not isinstance(source, dict):
                    errors.append(
                        f"INVALID_SOURCE: Record {i} source {j} must be object"
                    )
                    continue

                required_source_fields = ["method", "fetched_at", "evidence"]
                for field in required_source_fields:
                    if field not in source:
                        errors.append(
                            f"MISSING_SOURCE_FIELD: Record {i} source {j} missing '{field}'"
                        )

            # Provenance hash
            if "provenance_hash" not in meta:
                errors.append(
                    f"MISSING_PROVENANCE_HASH: Record {i} missing provenance_hash"
                )

        return errors

    def generate_quality_report(
        self, data_path: str, manifest_path: str
    ) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        success, errors = self.validate_dataset(data_path, manifest_path)

        # Load data for metrics
        data_path_obj = Path(data_path)
        data = []
        if data_path_obj.exists():
            for line in data_path_obj.read_text().splitlines():
                if line.strip():
                    data.append(json.loads(line))

        # Calculate metrics
        metrics = {
            "total_records": len(data),
            "validation_passed": success,
            "error_count": len(errors),
            "errors_by_category": self._categorize_errors(errors),
            "quality_metrics": self._calculate_quality_metrics(data),
            "timestamp": datetime.utcnow().isoformat(),
            "data_path": str(data_path),
            "manifest_path": str(manifest_path),
        }

        return {
            "success": success,
            "metrics": metrics,
            "errors": errors,
            "recommendations": self._generate_recommendations(errors, metrics),
        }

    def _categorize_errors(self, errors: List[str]) -> Dict[str, int]:
        """Categorize errors by type"""
        categories = {
            "integrity": 0,
            "schema": 0,
            "quality_gates": 0,
            "manifest": 0,
            "business_rules": 0,
            "provenance": 0,
        }

        for error in errors:
            if (
                "DUPLICATE" in error
                or "PLACEHOLDER" in error
                or "MOCK" in error
                or "SUSPICIOUS" in error
            ):
                categories["integrity"] += 1
            elif "MISSING_FIELD" in error or "INVALID_TYPE" in error:
                categories["schema"] += 1
            elif (
                "THRESHOLD" in error
                or "ORG_EXCLUDED" in error
                or "OFFICIAL_EXCLUDED" in error
            ):
                categories["quality_gates"] += 1
            elif "MANIFEST" in error:
                categories["manifest"] += 1
            elif "BRAND" in error or "RISK" in error:
                categories["business_rules"] += 1
            elif "SOURCE" in error or "PROVENANCE" in error:
                categories["provenance"] += 1

        return categories

    def _calculate_quality_metrics(self, data: List[Dict]) -> Dict[str, Any]:
        """Calculate quality metrics"""
        if not data:
            return {}

        # Entry threshold compliance
        threshold_compliant = 0
        org_excluded = 0
        official_excluded = 0
        verified_count = 0

        for item in data:
            followers = item.get("followers_count", 0)
            verified = item.get("verified")
            is_verified = verified in ["blue", "org", "legacy"]

            if (is_verified and followers >= 30000) or followers >= 50000:
                threshold_compliant += 1

            if not item.get("is_org", True):
                org_excluded += 1

            if not item.get("is_official", True):
                official_excluded += 1

            if is_verified:
                verified_count += 1

        # Follower distribution
        follower_counts = [item.get("followers_count", 0) for item in data]
        follower_counts.sort(reverse=True)

        return {
            "entry_threshold_compliance": threshold_compliant / len(data) * 100,
            "org_exclusion_compliance": org_excluded / len(data) * 100,
            "official_exclusion_compliance": official_excluded / len(data) * 100,
            "verified_percentage": verified_count / len(data) * 100,
            "median_followers": follower_counts[len(follower_counts) // 2]
            if follower_counts
            else 0,
            "top_10_percent_followers": follower_counts[
                max(1, len(follower_counts) // 10) - 1
            ]
            if follower_counts
            else 0,
        }

    def _generate_recommendations(self, errors: List[str], metrics: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        if not errors:
            recommendations.append(
                "✅ Dataset passes all quality checks - ready for production"
            )
            return recommendations

        error_categories = self._categorize_errors(errors)

        if error_categories["integrity"] > 0:
            recommendations.append(
                "🔧 Remove duplicate handles, placeholder IDs, and mock/test data"
            )

        if error_categories["schema"] > 0:
            recommendations.append(
                "📋 Fix missing required fields and data type violations"
            )

        if error_categories["quality_gates"] > 0:
            recommendations.append(
                "🚯 Filter out org/official accounts and ensure entry threshold compliance"
            )

        if error_categories["manifest"] > 0:
            recommendations.append(
                "📊 Update manifest.json to match actual dataset count and SHA256"
            )

        if error_categories["business_rules"] > 0:
            recommendations.append("⚠️ Review brand heuristics and risk term filtering")

        if error_categories["provenance"] > 0:
            recommendations.append(
                "🔍 Add complete provenance information with sources and evidence"
            )

        # Quality metrics recommendations
        quality_metrics = metrics.get("quality_metrics", {})
        if quality_metrics.get("entry_threshold_compliance", 0) < 100:
            recommendations.append(
                "📈 Improve entry threshold compliance by filtering low-follower accounts"
            )

        if quality_metrics.get("org_exclusion_compliance", 0) < 100:
            recommendations.append(
                "🏢 Ensure all organization accounts are properly excluded"
            )

        return recommendations


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive Quality Control for Influx Dataset"
    )
    parser.add_argument(
        "--data", default="data/latest/latest.jsonl", help="Dataset file path"
    )
    parser.add_argument(
        "--manifest", default="data/latest/manifest.json", help="Manifest file path"
    )
    parser.add_argument(
        "--schema", default="schema/bigv.schema.json", help="Schema file path"
    )
    parser.add_argument("--report", help="Output quality report to file")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")

    args = parser.parse_args()

    qc = QualityController(args.schema)

    if args.report:
        report = qc.generate_quality_report(args.data, args.manifest)
        with open(args.report, "w") as f:
            json.dump(report, f, indent=2)

        if not args.quiet:
            print(f"Quality report saved to: {args.report}")
            print(f"Status: {'PASS' if report['success'] else 'FAIL'}")
            print(f"Errors: {report['metrics']['error_count']}")

        sys.exit(0 if report["success"] else 1)
    else:
        success, errors = qc.validate_dataset(args.data, args.manifest)

        if not args.quiet:
            print(f"Quality Control: {'PASS' if success else 'FAIL'}")
            if errors:
                print(f"Errors found: {len(errors)}")
                for error in errors[:10]:  # Show first 10 errors
                    print(f"  - {error}")
                if len(errors) > 10:
                    print(f"  ... and {len(errors) - 10} more errors")

        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
