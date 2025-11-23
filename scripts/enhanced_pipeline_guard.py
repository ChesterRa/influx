#!/usr/bin/env python3
"""
Enhanced Pipeline Guard with Comprehensive Quality Control
Integrates comprehensive_quality_control.py with existing pipeline_guard.sh
"""

import json
import sys
import subprocess
import argparse
from pathlib import Path


def run_strict_validation(
    dataset_path: str, schema_path: str, manifest_path: str
) -> tuple[bool, str]:
    """Run influx-validate --strict"""
    try:
        result = subprocess.run(
            [
                "python3",
                "tools/influx-validate",
                "--strict",
                "-s",
                schema_path,
                "-m",
                manifest_path,
                dataset_path,
            ],
            capture_output=True,
            text=True,
            cwd="/home/dodd/dev/influx",
        )

        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, f"Validation error: {e}"


def run_comprehensive_qc(dataset_path: str, manifest_path: str) -> tuple[bool, str]:
    """Run comprehensive quality control"""
    try:
        result = subprocess.run(
            [
                "python3",
                "scripts/comprehensive_quality_control.py",
                "--data",
                dataset_path,
                "--manifest",
                manifest_path,
            ],
            capture_output=True,
            text=True,
            cwd="/home/dodd/dev/influx",
        )

        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, f"Quality control error: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Pipeline Guard with Comprehensive QC"
    )
    parser.add_argument("dataset", help="Dataset file path")
    parser.add_argument("manifest", help="Manifest file path")
    parser.add_argument("schema", help="Schema file path")
    parser.add_argument(
        "--comprehensive", action="store_true", help="Run comprehensive quality control"
    )
    parser.add_argument("--report", help="Generate quality report to file")

    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    manifest_path = Path(args.manifest)
    schema_path = Path(args.schema)

    # File existence checks
    if not dataset_path.exists():
        print(f"ERROR: Dataset file not found: {dataset_path}", file=sys.stderr)
        sys.exit(1)

    if not manifest_path.exists():
        print(f"ERROR: Manifest file not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    if not schema_path.exists():
        print(f"ERROR: Schema file not found: {schema_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Pipeline Guard: Validating {dataset_path}")

    # 1. Run strict validation
    print("Running strict validation...")
    valid, output = run_strict_validation(
        str(dataset_path), str(schema_path), str(manifest_path)
    )
    if not valid:
        print(f"STRICT VALIDATION FAILED:\n{output}", file=sys.stderr)
        sys.exit(1)
    print("✓ Strict validation passed")

    # 2. Run comprehensive quality control if requested
    if args.comprehensive:
        print("Running comprehensive quality control...")

        if args.report:
            # Generate report
            valid, output = run_comprehensive_qc(str(dataset_path), str(manifest_path))
            if not valid:
                print(f"COMPREHENSIVE QC FAILED:\n{output}", file=sys.stderr)
                sys.exit(1)
            print("✓ Comprehensive quality control passed")
            print(f"Quality report: {args.report}")
        else:
            # Run validation only
            valid, output = run_comprehensive_qc(str(dataset_path), str(manifest_path))
            if not valid:
                print(f"COMPREHENSIVE QC FAILED:\n{output}", file=sys.stderr)
                sys.exit(1)
            print("✓ Comprehensive quality control passed")

    print(f"Pipeline Guard: PASS for {dataset_path}")


if __name__ == "__main__":
    main()
