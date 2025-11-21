#!/usr/bin/env python3
"""
M2 Phase 2 Strategic Execution Automation
Hybrid approach: Process existing metrics + RUBE MCP batch integration
Target: 531 authors with complete M2 scoring within 36 hours
"""

import subprocess
import json
import os
import time
from pathlib import Path
from datetime import datetime


class M2Phase2Executor:
    def __init__(self):
        self.batch_size = 50
        self.processed_batches = []
        self.failed_batches = []

    def analyze_current_state(self):
        """Analyze current data collection state"""
        print("🔍 Analyzing current M2 Phase 2 state...")

        with_authors = []
        without_authors = []

        with open("data/latest/latest.jsonl", "r") as f:
            for line in f:
                if line.strip():
                    author = json.loads(line)
                    if "activity_metrics" in author.get("meta", {}):
                        with_authors.append(author)
                    else:
                        without_authors.append(author)

        print(f"📊 Current State Analysis:")
        print(f"   Authors WITH activity_metrics: {len(with_authors)} (13.4%)")
        print(f"   Authors WITHOUT activity_metrics: {len(without_authors)} (86.6%)")
        print(f"   Total authors: {len(with_authors) + len(without_authors)}")

        return with_authors, without_authors

    def process_existing_metrics(self, authors_with_metrics):
        """Process authors who already have activity metrics"""
        print(
            f"🚀 Processing {len(authors_with_metrics)} authors with existing metrics..."
        )

        # Write authors with metrics for immediate M2 scoring
        with open("m2_ready_authors.jsonl", "w") as f:
            for author in authors_with_metrics:
                f.write(json.dumps(author) + "\n")

        # Apply M2 scoring
        cmd = [
            "./tools/influx-score",
            "update",
            "--authors",
            "m2_ready_authors.jsonl",
            "--out",
            "m2_ready_scored.jsonl",
            "--model",
            "m2",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(
                f"✅ Successfully scored {len(authors_with_metrics)} authors with existing metrics"
            )
            return "m2_ready_scored.jsonl"
        else:
            print(f"❌ Error scoring existing metrics: {result.stderr}")
            return None

    def create_rube_batches(self, authors_without_metrics):
        """Create batch files for RUBE MCP processing"""
        print(
            f"📦 Creating RUBE MCP batches for {len(authors_without_metrics)} authors..."
        )

        handles = [author["handle"] for author in authors_without_metrics]
        batch_files = []

        for i in range(0, len(handles), self.batch_size):
            batch = handles[i : i + self.batch_size]
            batch_num = i // self.batch_size + 1
            batch_file = f"m2_rube_batch_{batch_num:03d}_handles.txt"

            with open(batch_file, "w") as f:
                f.write("\n".join(batch))

            batch_files.append((batch_num, batch_file, len(batch)))
            print(f"   Created batch {batch_num}: {len(batch)} handles")

        return batch_files

    def generate_rube_instructions(self, batch_files):
        """Generate detailed RUBE MCP processing instructions"""
        print("📋 Generating RUBE MCP processing instructions...")

        instructions = "# M2 Phase 2 RUBE MCP Processing Instructions\n\n"
        instructions += f"Generated: {datetime.now().isoformat()}\n"
        instructions += f"Total batches: {len(batch_files)}\n"
        instructions += f"Batch size: {self.batch_size} handles\n\n"

        instructions += "## For Each Batch (Execute Sequentially):\n\n"

        for batch_num, batch_file, handle_count in batch_files:
            instructions += f"### Batch {batch_num}: {handle_count} handles\n\n"
            instructions += f"```bash\n"
            instructions += f"# Step 1: Fetch data via RUBE MCP\n"
            instructions += f"claude-code exec rube-fetch $(cat {batch_file} | sed 's/^/@/' | tr '\\n' ' ')\n\n"
            instructions += (
                f"# Step 2: Process fetched data (replace output filename as needed)\n"
            )
            instructions += f"tools/influx-harvest x-lists \\\n"
            instructions += f"  --list-urls {batch_file} \\\n"
            instructions += (
                f"  --prefetched-users rube_batch_{batch_num:03d}_output.jsonl \\\n"
            )
            instructions += (
                f"  --out m2_rube_batch_{batch_num:03d}_refreshed.jsonl \\\n"
            )
            instructions += f"  --brand-rules lists/rules/brand_heuristics.yml\n\n"
            instructions += f"# Step 3: Apply M2 scoring\n"
            instructions += f"tools/influx-score update \\\n"
            instructions += (
                f"  --authors m2_rube_batch_{batch_num:03d}_refreshed.jsonl \\\n"
            )
            instructions += f"  --out m2_rube_batch_{batch_num:03d}_scored.jsonl \\\n"
            instructions += f"  --model m2\n"
            instructions += f"```\n\n"

        # Write instructions file
        with open("M2_Phase2_RUBE_Instructions.md", "w") as f:
            f.write(instructions)

        print("✅ RUBE MCP instructions written to M2_Phase2_RUBE_Instructions.md")
        return instructions

    def create_monitoring_dashboard(self):
        """Create progress monitoring dashboard"""
        dashboard = """# M2 Phase 2 Progress Dashboard

## Execution Status
- **Start Time**: {start_time}
- **Total Authors**: 531
- **Authors with existing metrics**: 71 (13.4%)
- **Authors requiring RUBE MCP**: 460 (86.6%)
- **Batch Size**: 50 handles
- **Total Batches**: 10

## Progress Tracking
| Batch | Status | Handles | Output File | Completed At |
|-------|--------|---------|-------------|--------------|
| Ready | ✅ | 71 | m2_ready_scored.jsonl | {start_time} |
| 001 | ⏳ | 50 | m2_rube_batch_001_scored.jsonl | - |
| 002 | ⏳ | 50 | m2_rube_batch_002_scored.jsonl | - |
| ... | ... | ... | ... | ... |

## Success Metrics
- [ ] All 531 authors processed with M2 metrics
- [ ] Zero-score crisis eliminated (0.0 → meaningful scores)
- [ ] Score distribution in 20-95 range
- [ ] 100% schema compliance
- [ ] Processing time < 36 hours

## Risk Mitigation
- **API Rate Limits**: 15-minute delays between batches
- **Data Integrity**: Validation after each batch
- **Rollback Capability**: Original data preserved
""".format(start_time=datetime.now().isoformat())

        with open("M2_Phase2_Dashboard.md", "w") as f:
            f.write(dashboard)

        print("✅ Progress dashboard created: M2_Phase2_Dashboard.md")

    def execute(self):
        """Execute complete M2 Phase 2 strategy"""
        print("🚀 Starting M2 Phase 2 Strategic Execution...")
        print("🎯 Target: 531 authors with enhanced activity metrics")
        print("⏱️  Timeline: 24-36 hours\n")

        # Step 1: Analyze current state
        with_authors, without_authors = self.analyze_current_state()

        # Step 2: Process existing metrics
        ready_scored_file = self.process_existing_metrics(with_authors)

        # Step 3: Create RUBE batches
        batch_files = self.create_rube_batches(without_authors)

        # Step 4: Generate RUBE instructions
        self.generate_rube_instructions(batch_files)

        # Step 5: Create monitoring dashboard
        self.create_monitoring_dashboard()

        print("\n🎯 M2 Phase 2 Strategic Execution Plan Complete!")
        print("📋 Next Steps:")
        print("   1. Follow M2_Phase2_RUBE_Instructions.md for batch processing")
        print("   2. Update progress in M2_Phase2_Dashboard.md")
        print("   3. Monitor for API rate limits and data quality")
        print(
            f"\n⏱️  Estimated completion: {datetime.fromtimestamp(time.time() + 36 * 3600).isoformat()}"
        )


if __name__ == "__main__":
    executor = M2Phase2Executor()
    executor.execute()
