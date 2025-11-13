#!/usr/bin/env python3
"""
Data cleaning tool for influx dataset.
Adds missing is_org/is_official fields and applies entry threshold filtering.
"""

import json
import sys
import argparse
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Set

def load_brand_heuristics(rules_path: Path) -> Dict:
    """Load brand heuristics rules from YAML file."""
    with open(rules_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def matches_keywords(text: str, keywords: List[str]) -> bool:
    """Check if text matches any keyword (case-insensitive, word boundary)."""
    if not text:
        return False

    text_lower = text.lower()
    for keyword in keywords:
        # Word boundary match using regex
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, text_lower):
            return True
    return False

def calculate_brand_flags(profile: Dict, heuristics: Dict) -> Tuple[bool, bool]:
    """
    Calculate is_org and is_official flags based on heuristics.
    Returns (is_org, is_official)
    """
    name = profile.get('name', '')
    handle = profile.get('handle', '')
    verified = profile.get('verified', 'none')

    # Initialize scores
    org_score = 0.0
    official_score = 0.0

    weights = heuristics.get('confidence_weights', {})

    # Name keyword matching
    name_keywords = heuristics.get('name_keywords', {})

    # Official indicators
    official_indicators = name_keywords.get('official_indicators', [])
    if matches_keywords(name, official_indicators):
        official_score += weights.get('name_keyword_match', 0.6)

    # Corporate indicators
    corporate_indicators = name_keywords.get('corporate_indicators', [])
    if matches_keywords(name, corporate_indicators):
        org_score += weights.get('name_keyword_match', 0.6)

    # Brand/commerce indicators
    brand_commerce = name_keywords.get('brand_commerce', [])
    if matches_keywords(name, brand_commerce):
        org_score += weights.get('name_keyword_match', 0.6)

    # Verification status rules
    verification_rules = heuristics.get('verification_rules', {})
    if verification_rules.get('flag_org_verification', False) and verified == 'org':
        org_score += weights.get('org_verification', 1.0)

    # Check exceptions
    exceptions = set(heuristics.get('exceptions', []))
    if handle in exceptions:
        return False, False

    # Apply threshold
    flag_threshold = heuristics.get('flag_threshold', 0.7)

    is_org = org_score >= flag_threshold
    is_official = official_score >= flag_threshold

    return is_org, is_official

def passes_entry_threshold(profile: Dict) -> bool:
    """
    Check if profile passes entry threshold:
    (verified=true AND followers>=30k) OR followers>=50k
    """
    verified = profile.get('verified', 'none')
    followers = profile.get('followers_count', 0)

    is_verified = verified in ['blue', 'org', 'legacy']
    verified_min = is_verified and followers >= 30000
    unverified_min = followers >= 50000

    return verified_min or unverified_min

def clean_dataset(input_path: Path, output_path: Path, heuristics_path: Path,
                 remove_below_threshold: bool = True) -> Dict:
    """Clean the dataset by adding filters and applying threshold rules."""

    print(f"Loading dataset from {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        records = [json.loads(line) for line in f if line.strip()]

    print(f"Loaded {len(records)} records")

    # Load heuristics
    heuristics = load_brand_heuristics(heuristics_path)
    print(f"Loaded brand heuristics from {heuristics_path}")

    # Process records
    cleaned_records = []
    below_threshold = []
    flagged_org = []
    flagged_official = []

    for i, record in enumerate(records):
        # Add missing fields with defaults
        if 'is_org' not in record:
            record['is_org'], record['is_official'] = calculate_brand_flags(record, heuristics)
        else:
            # Field exists, keep as is
            pass

        # Check threshold
        if not passes_entry_threshold(record):
            below_threshold.append(record)
            if remove_below_threshold:
                continue

        # Track flagged accounts
        if record.get('is_org', False):
            flagged_org.append(record['handle'])
        if record.get('is_official', False):
            flagged_official.append(record['handle'])

        cleaned_records.append(record)

        if (i + 1) % 50 == 0:
            print(f"Processed {i + 1}/{len(records)} records")

    # Write cleaned records
    print(f"Writing {len(cleaned_records)} cleaned records to {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in cleaned_records:
            f.write(json.dumps(record, separators=(',', ':')) + '\n')

    # Generate report
    report = {
        'input_count': len(records),
        'output_count': len(cleaned_records),
        'removed_below_threshold': len(below_threshold),
        'flagged_org': len(flagged_org),
        'flagged_official': len(flagged_official),
        'below_threshold_handles': [r['handle'] for r in below_threshold],
        'flagged_org_handles': flagged_org,
        'flagged_official_handles': flagged_official
    }

    return report

def main():
    parser = argparse.ArgumentParser(description='Clean influx dataset')
    parser.add_argument('input', help='Input JSONL file')
    parser.add_argument('output', help='Output JSONL file')
    parser.add_argument('--brand-rules', default='lists/rules/brand_heuristics.yml',
                       help='Brand heuristics rules file')
    parser.add_argument('--remove-below-threshold', action='store_true',
                       help='Remove records below entry threshold')
    parser.add_argument('--report', help='Write report to JSON file')

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    heuristics_path = Path(args.brand_rules)

    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist")
        sys.exit(1)

    if not heuristics_path.exists():
        print(f"Error: Heuristics file {heuristics_path} does not exist")
        sys.exit(1)

    # Clean dataset
    report = clean_dataset(input_path, output_path, heuristics_path, args.remove_below_threshold)

    # Print summary
    print("\n=== Cleaning Summary ===")
    print(f"Input records: {report['input_count']}")
    print(f"Output records: {report['output_count']}")
    print(f"Removed below threshold: {report['removed_below_threshold']}")
    print(f"Flagged as org: {report['flagged_org']}")
    print(f"Flagged as official: {report['flagged_official']}")

    if report['below_threshold_handles']:
        print(f"\nBelow threshold handles: {', '.join(report['below_threshold_handles'])}")

    if report['flagged_org_handles']:
        print(f"\nFlagged org handles: {', '.join(report['flagged_org_handles'])}")

    if report['flagged_official_handles']:
        print(f"\nFlagged official handles: {', '.join(report['flagged_official_handles'])}")

    # Write report if requested
    if args.report:
        with open(args.report, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport written to {args.report}")

if __name__ == '__main__':
    main()