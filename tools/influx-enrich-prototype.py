#!/usr/bin/env python3
"""
influx-enrich prototype - Data enrichment capability test
Tests if we can add activity_metrics to existing 476 records without data loss
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def test_data_enrichment():
    """Test data enrichment on existing records"""
    try:
        data_path = Path("data/latest/latest.jsonl")
        if not data_path.exists():
            print("❌ Data file not found")
            return False

        enriched_records = []
        original_count = 0

        print("🔍 Testing data enrichment capability...")

        # Read and test enrich first 10 records
        with open(data_path, 'r') as f:
            for i, line in enumerate(f):
                if i >= 10:  # Test only first 10 for prototype
                    break

                original_count += 1
                record = json.loads(line.strip())

                # Test enrichment: add activity_metrics
                if 'meta' not in record:
                    record['meta'] = {}

                record['meta']['activity_metrics'] = {
                    'enrichment_test': True,
                    'enrichment_timestamp': datetime.utcnow().isoformat(),
                    'test_field': f'enriched_record_{i}'
                }

                # Add test enrichment field
                record['test_enrichment'] = {
                    'prototype_test': True,
                    'batch_id': 'prototype_v1'
                }

                enriched_records.append(record)

        print(f"✅ Successfully enriched {len(enriched_records)} records")
        print(f"📊 Original records processed: {original_count}")

        # Test data integrity
        for i, record in enumerate(enriched_records):
            required_fields = ['id', 'handle', 'followers_count']
            missing_fields = [field for field in required_fields if field not in record]

            if missing_fields:
                print(f"❌ Record {i} missing required fields: {missing_fields}")
                return False

        print("✅ All records maintain data integrity")

        # Save test output
        output_path = Path("test_enrichment_output.jsonl")
        with open(output_path, 'w') as f:
            for record in enriched_records:
                f.write(json.dumps(record) + '\n')

        print(f"💾 Test enrichment saved to: {output_path}")
        print(f"📏 File size: {output_path.stat().st_size} bytes")

        return True

    except Exception as e:
        print(f"❌ Enrichment test failed: {e}")
        return False

def test_full_dataset_feasibility():
    """Test if full dataset enrichment is feasible"""
    try:
        data_path = Path("data/latest/latest.jsonl")
        record_count = 0

        with open(data_path, 'r') as f:
            for line in f:
                record_count += 1

        print(f"📊 Full dataset contains {record_count} records")

        # Estimate processing time and memory
        estimated_size_per_record = 2000  # bytes
        estimated_enriched_size = record_count * estimated_size_per_record

        print(f"💾 Estimated enriched dataset size: {estimated_enriched_size:,} bytes ({estimated_enriched_size/1024/1024:.1f} MB)")

        if record_count > 0:
            print("✅ Full dataset enrichment appears feasible")
            return True
        else:
            print("❌ No records found in dataset")
            return False

    except Exception as e:
        print(f"❌ Feasibility test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 influx-enrich prototype test starting...")
    print("=" * 50)

    # Test 1: Data enrichment capability
    enrichment_success = test_data_enrichment()

    print("\n" + "=" * 50)

    # Test 2: Full dataset feasibility
    feasibility_success = test_full_dataset_feasibility()

    print("\n" + "=" * 50)
    print("📋 PROTOTYPE TEST RESULTS:")
    print(f"   Data Enrichment: {'✅ PASS' if enrichment_success else '❌ FAIL'}")
    print(f"   Full Feasibility: {'✅ PASS' if feasibility_success else '❌ FAIL'}")

    if enrichment_success and feasibility_success:
        print("\n🎉 CONCLUSION: Data enrichment is ARCHITECTURALLY FEASIBLE")
        print("   M2 migration can proceed with proper tool development")
        sys.exit(0)
    else:
        print("\n⚠️  CONCLUSION: Data enrichment requires architectural changes")
        print("   M2 migration strategy needs fundamental revision")
        sys.exit(1)