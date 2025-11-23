#!/usr/bin/env python3
"""
Dataset Flattener Tool
Flattens critical fields from meta structure to top level for schema compliance
"""

import json
import sys
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime


class DatasetFlattener:
    """Flattens nested fields for schema compliance"""

    def __init__(self):
        pass

    def flatten_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten critical fields from meta to top level"""
        flattened = record.copy()

        # Get meta structure
        meta = record.get("meta", {})
        if not isinstance(meta, dict):
            meta = {}

        # Flatten critical fields to top level
        critical_fields = [
            "quality_score",
            "entry_threshold_passed",
            "last_refresh_at",
            "provenance_hash",
            "activity_score",
            "relevance_score",
            "combined_score",
        ]

        for field in critical_fields:
            if field in meta and field not in flattened:
                flattened[field] = meta[field]

        # Ensure boolean conversion for entry_threshold_passed
        if "entry_threshold_passed" in flattened:
            value = flattened["entry_threshold_passed"]
            if isinstance(value, str):
                flattened["entry_threshold_passed"] = value.lower() in [
                    "true",
                    "1",
                    "yes",
                ]
            elif value is None:
                # Calculate based on followers and verification
                followers = record.get("followers_count", 0)
                verified = record.get("verified", "none")
                flattened["entry_threshold_passed"] = followers >= 50000 or (
                    verified in ["blue", "legacy"] and followers >= 30000
                )

        # Ensure numeric quality_score
        if "quality_score" in flattened:
            try:
                score = flattened["quality_score"]
                if isinstance(score, str):
                    flattened["quality_score"] = float(score)
                elif score is None:
                    flattened["quality_score"] = 0.0
            except (ValueError, TypeError):
                flattened["quality_score"] = 0.0

        # Flatten activity_metrics if needed
        if "activity_metrics" in meta and isinstance(meta["activity_metrics"], dict):
            activity = meta["activity_metrics"]
            # Extract key metrics to top level if not present
            activity_fields = [
                "tweet_count",
                "total_like_count",
                "media_count",
                "listed_count",
                "following_count",
            ]
            for field in activity_fields:
                if field in activity and field not in flattened:
                    flattened[field] = activity[field]

        return flattened

    def flatten_dataset(
        self, input_path: str, output_path: str
    ) -> Tuple[int, List[str]]:
        """Flatten all records in a dataset"""
        input_file = Path(input_path)
        output_file = Path(output_path)

        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Read records
        records = []
        for line_num, line in enumerate(input_file.read_text().splitlines(), 1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
                flattened = self.flatten_record(record)
                records.append(flattened)
            except json.JSONDecodeError as e:
                print(
                    f"Warning: Line {line_num} JSON decode error: {e}", file=sys.stderr
                )
            except Exception as e:
                print(
                    f"Warning: Line {line_num} processing error: {e}", file=sys.stderr
                )

        # Sort by quality_score desc, followers_count desc, handle asc
        records.sort(
            key=lambda r: (
                -r.get("quality_score", 0),
                -r.get("followers_count", 0),
                r.get("handle", ""),
            )
        )

        # Write flattened dataset
        output_file.parent.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps(r, ensure_ascii=False) for r in records]
        output_file.write_text("\n".join(lines) + "\n")

        # Generate summary
        total_records = len(records)
        entry_passed = sum(1 for r in records if r.get("entry_threshold_passed", False))
        quality_scores = [
            r.get("quality_score", 0)
            for r in records
            if isinstance(r.get("quality_score"), (int, float))
        ]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

        summary = [
            f"Total records: {total_records}",
            f"Entry threshold passed: {entry_passed}/{total_records} ({(entry_passed / total_records) * 100:.1f}%)",
            f"Average quality score: {avg_quality:.1f}",
            f"Records with quality scores: {len(quality_scores)}/{total_records}",
        ]

        return total_records, summary

    def update_manifest(self, dataset_path: str, manifest_path: str):
        """Update manifest with new dataset info"""
        dataset_file = Path(dataset_path)
        manifest_file = Path(manifest_path)

        if not dataset_file.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

        if not manifest_file.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        # Count records and calculate SHA256
        record_count = sum(
            1 for line in dataset_file.read_text().splitlines() if line.strip()
        )
        sha256 = hashlib.sha256(dataset_file.read_bytes()).hexdigest()

        # Load and update manifest
        manifest = json.loads(manifest_file.read_text())
        manifest.update(
            {
                "count": record_count,
                "sha256": sha256,
                "timestamp": datetime.now().isoformat(),
                "source_file": str(dataset_file),
                "processing_note": "Flattened meta fields to top level for schema compliance",
            }
        )

        manifest_file.write_text(json.dumps(manifest, indent=2))

        return record_count, sha256


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: python dataset_flattener.py <input.jsonl> <output.jsonl> [--update-manifest]"
        )
        print("  --update-manifest: Also update data/latest/manifest.json")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    update_manifest = "--update-manifest" in sys.argv

    flattener = DatasetFlattener()

    try:
        total_records, summary = flattener.flatten_dataset(input_path, output_path)

        print(f"✅ Dataset Flattened: {total_records} records")
        for line in summary:
            print(f"   {line}")

        if update_manifest:
            try:
                count, sha = flattener.update_manifest(
                    output_path, "data/latest/manifest.json"
                )
                print(f"✅ Manifest Updated: {count} records, SHA256: {sha[:16]}...")
            except Exception as e:
                print(f"❌ Manifest update failed: {e}", file=sys.stderr)

        print(f"📄 Output: {output_path}")

    except Exception as e:
        print(f"❌ Dataset flattening failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
