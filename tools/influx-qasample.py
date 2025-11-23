#!/usr/bin/env python3
"""
Generate QA sample for manual review of brand/official flag accuracy.
"""

import json
import sys
import argparse
import random
from pathlib import Path
from typing import Dict, List

def load_dataset(data_path: Path) -> List[Dict]:
    """Load dataset from JSONL file."""
    with open(data_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def stratified_sample(records: List[Dict], n: int = 50) -> List[Dict]:
    """Generate stratified sample for QA review."""
    # Separate by flags
    org_flagged = [r for r in records if r.get('is_org', False)]
    official_flagged = [r for r in records if r.get('is_official', False)]
    clean = [r for r in records if not r.get('is_org', False) and not r.get('is_official', False)]

    sample = []

    # Sample flagged accounts (prioritize these)
    # Take all flagged accounts if less than n/2, otherwise sample
    flagged = org_flagged + official_flagged
    if len(flagged) <= n // 2:
        sample.extend(flagged)
        remaining = n - len(flagged)
    else:
        sample.extend(random.sample(flagged, n // 2))
        remaining = n - n // 2

    # Fill remaining with clean accounts
    if remaining > 0 and len(clean) >= remaining:
        sample.extend(random.sample(clean, remaining))
    elif remaining > 0:
        sample.extend(clean)  # Take all if less than remaining

    # Sort by score for review
    sample.sort(key=lambda r: r.get('meta', {}).get('score', 0), reverse=True)
    return sample[:n]

def format_qa_csv(records: List[Dict], output_path: Path):
    """Write QA sample as CSV for manual review."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("handle,name,followers,verified,is_org,is_official,score,review_notes,fp_org,fp_official\n")

        for record in records:
            handle = record.get('handle', '')
            name = record.get('name', '').replace(',', ' ')  # Remove commas for CSV
            followers = record.get('followers_count', 0)
            verified = record.get('verified', 'none')
            is_org = record.get('is_org', False)
            is_official = record.get('is_official', False)
            score = record.get('meta', {}).get('score', 0)

            f.write(f"{handle},{name},{followers},{verified},{is_org},{is_official},{score},,,\n")

def main():
    parser = argparse.ArgumentParser(description='Generate QA sample for manual review')
    parser.add_argument('input', help='Input JSONL file')
    parser.add_argument('--output', default='qa_sample.csv', help='Output CSV file')
    parser.add_argument('--n', type=int, default=50, help='Sample size')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    args = parser.parse_args()

    if args.seed:
        random.seed(args.seed)

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist")
        sys.exit(1)

    # Load dataset
    records = load_dataset(input_path)
    print(f"Loaded {len(records)} records from {input_path}")

    # Generate stats
    org_count = sum(1 for r in records if r.get('is_org', False))
    official_count = sum(1 for r in records if r.get('is_official', False))
    clean_count = len(records) - org_count - official_count

    print(f"Dataset composition:")
    print(f"  Flagged as org: {org_count} ({org_count/len(records)*100:.1f}%)")
    print(f"  Flagged as official: {official_count} ({official_count/len(records)*100:.1f}%)")
    print(f"  Clean (no flags): {clean_count} ({clean_count/len(records)*100:.1f}%)")

    # Generate stratified sample
    sample = stratified_sample(records, args.n)
    print(f"\nGenerated QA sample of {len(sample)} records")

    # Count flags in sample
    sample_org = sum(1 for r in sample if r.get('is_org', False))
    sample_official = sum(1 for r in sample if r.get('is_official', False))
    sample_clean = len(sample) - sample_org - sample_official

    print(f"Sample composition:")
    print(f"  Flagged as org: {sample_org}")
    print(f"  Flagged as official: {sample_official}")
    print(f"  Clean: {sample_clean}")

    # Write CSV
    format_qa_csv(sample, output_path)
    print(f"\nQA sample written to {output_path}")
    print("\nReview instructions:")
    print("1. Open the CSV file")
    print("2. For each record, check if is_org/is_official flags are correct")
    print("3. Add notes in review_notes column")
    print("4. Set fp_org=TRUE if is_org flag is incorrect (false positive)")
    print("5. Set fp_official=TRUE if is_official flag is incorrect (false positive)")
    print("6. Target FP rate: ≤3.3% (≤1-2 false positives in 50 samples)")

if __name__ == '__main__':
    main()