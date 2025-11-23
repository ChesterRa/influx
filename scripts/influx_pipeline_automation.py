#!/usr/bin/env python3
"""
Influx Pipeline Automation Tool
Orchestrates complete batch processing pipeline with quality gates
"""

import json
import sys
import subprocess
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass


class PipelineConfig:
    """Configuration for pipeline execution"""

    def __init__(self, batch_file: str, output_dir: str, **kwargs):
        self.batch_file = batch_file
        self.output_dir = output_dir
        self.min_followers = kwargs.get("min_followers", 50000)
        self.verified_min_followers = kwargs.get("verified_min_followers", 30000)
        self.skip_validation = kwargs.get("skip_validation", False)
        self.update_main = kwargs.get("update_main", False)
        self.generate_report = kwargs.get("generate_report", True)

        # Dynamic attributes set during pipeline execution
        self.harvested_file = ""
        self.risk_assessed_file = ""


class InfluxPipeline:
    """Complete pipeline automation for influx dataset processing"""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.pipeline_log = []

    def log(self, message: str, level: str = "INFO"):
        """Log pipeline step"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {level}: {message}"
        self.pipeline_log.append(log_entry)
        print(log_entry)

    def run_command(self, cmd: List[str], description: str) -> Tuple[bool, str]:
        """Run command and log results"""
        self.log(f"Running: {description}")
        self.log(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd="/home/dodd/dev/influx"
            )

            success = result.returncode == 0
            output = result.stdout + result.stderr

            if success:
                self.log(f"✅ Success: {description}")
            else:
                self.log(f"❌ Failed: {description}", "ERROR")
                self.log(f"Error output: {result.stderr}", "ERROR")

            return success, output

        except Exception as e:
            error_msg = f"Exception running {description}: {e}"
            self.log(error_msg, "ERROR")
            return False, error_msg

    def harvest_batch(self) -> Tuple[bool, str]:
        """Step 1: Harvest batch using influx-harvest"""
        batch_name = Path(self.config.batch_file).stem
        output_file = f"{self.config.output_dir}/{batch_name}_harvested.jsonl"

        cmd = [
            "./tools/influx-harvest",
            "bulk",
            "--handles-file",
            self.config.batch_file,
            "--out",
            output_file,
            "--min-followers",
            str(self.config.min_followers),
            "--verified-min-followers",
            str(self.config.verified_min_followers),
        ]

        success, output = self.run_command(
            cmd, f"Harvest batch {self.config.batch_file}"
        )

        if success:
            self.config.harvested_file = output_file

        return success, output

    def validate_harvested(self) -> Tuple[bool, str]:
        """Step 2: Validate harvested data"""
        if not hasattr(self.config, "harvested_file"):
            return False, "No harvested file to validate"

        cmd = [
            "python3",
            "tools/influx-validate",
            "--strict",
            "-s",
            "schema/bigv.schema.json",
            self.config.harvested_file,
        ]

        return self.run_command(cmd, "Validate harvested data")

    def assess_quality(self) -> Tuple[bool, str]:
        """Step 3: Quality assessment"""
        if not hasattr(self.config, "harvested_file"):
            return False, "No harvested file to assess"

        cmd = [
            "python3",
            "scripts/data_quality_assessment.py",
            self.config.harvested_file,
            "--report",
        ]

        return self.run_command(cmd, "Quality assessment")

    def assess_risk(self) -> Tuple[bool, str]:
        """Step 4: Risk assessment"""
        if not hasattr(self.config, "harvested_file"):
            return False, "No harvested file for risk assessment"

        risk_file = (
            self.config.harvested_file.replace(".jsonl", "_with_risk.jsonl")
            if self.config.harvested_file
            else ""
        )
        cmd = [
            "python3",
            "scripts/risk_assessment.py",
            self.config.harvested_file,
            risk_file,
        ]

        success, output = self.run_command(cmd, "Risk assessment")

        if success:
            self.config.risk_assessed_file = risk_file

        return success, output

    def final_validation(self) -> Tuple[bool, str]:
        """Step 5: Final validation"""
        file_to_validate = getattr(
            self.config,
            "risk_assessed_file",
            getattr(self.config, "harvested_file", None),
        )

        if not file_to_validate:
            return False, "No file available for final validation"

        cmd = [
            "./tools/influx-validate",
            "--strict",
            "-s",
            "schema/bigv.schema.json",
            "-m",
            "data/latest/manifest.json",
            file_to_validate,
        ]

        return self.run_command(cmd, "Final validation")

    def merge_with_main(self) -> Tuple[bool, str]:
        """Step 6: Merge with main dataset"""
        if not self.config.update_main:
            self.log("Skipping main dataset merge (not requested)")
            return True, "Skipped"

        file_to_merge = self.config.risk_assessed_file or self.config.harvested_file

        if not file_to_merge:
            return False, "No file available for merging"

        # Load current dataset
        try:
            with open("data/latest/latest.jsonl") as f:
                current_records = [json.loads(line) for line in f if line.strip()]
        except Exception as e:
            return False, f"Failed to load current dataset: {e}"

        # Load new records
        try:
            with open(file_to_merge) as f:
                new_records = [json.loads(line) for line in f if line.strip()]
        except Exception as e:
            return False, f"Failed to load new records: {e}"

        # Remove banned records from new data
        new_records = [r for r in new_records if not r.get("banned", False)]

        # Get existing handles
        existing_handles = {r.get("handle") for r in current_records}
        new_handles = {r.get("handle") for r in new_records}

        # Find truly new authors
        truly_new = [r for r in new_records if r.get("handle") not in existing_handles]

        if not truly_new:
            self.log("No new authors to add (all already exist)")
            return True, "No new authors"

        # Merge datasets
        merged_records = current_records + truly_new

        # Sort by quality_score desc, followers_count desc, handle asc
        merged_records.sort(
            key=lambda r: (
                -r.get("quality_score", 0),
                -r.get("followers_count", 0),
                r.get("handle", ""),
            )
        )

        # Write merged dataset
        try:
            lines = [json.dumps(r, ensure_ascii=False) for r in merged_records]
            with open("data/latest/latest.jsonl", "w") as f:
                f.write("\n".join(lines) + "\n")

            # Update manifest
            self._update_manifest(len(merged_records))

            self.log(f"✅ Merged {len(truly_new)} new authors")
            self.log(f"📊 Total dataset: {len(merged_records)} authors")

            return True, f"Added {len(truly_new)} authors"

        except Exception as e:
            return False, f"Failed to merge datasets: {e}"

    def _update_manifest(self, total_records: int):
        """Update manifest with new count and SHA256"""
        try:
            # Calculate SHA256
            with open("data/latest/latest.jsonl", "rb") as f:
                sha256 = hashlib.sha256(f.read()).hexdigest()

            # Load and update manifest
            with open("data/latest/manifest.json") as f:
                manifest = json.load(f)

            manifest.update(
                {
                    "count": total_records,
                    "sha256": sha256,
                    "timestamp": datetime.now().isoformat(),
                    "last_batch_processed": self.config.batch_file,
                    "processing_log": self.pipeline_log,
                }
            )

            with open("data/latest/manifest.json", "w") as f:
                json.dump(manifest, f, indent=2)

            self.log(f"✅ Manifest updated: {total_records} records")

        except Exception as e:
            self.log(f"❌ Failed to update manifest: {e}", "ERROR")

    def generate_pipeline_report(self) -> str:
        """Generate comprehensive pipeline report"""
        report = ["# Pipeline Execution Report\n"]
        report.append(f"Batch: {self.config.batch_file}")
        report.append(
            f"Started: {self.pipeline_log[0] if self.pipeline_log else 'Unknown'}"
        )
        report.append(f"Completed: {datetime.now().isoformat()}\n")

        report.append("## 📋 Execution Log\n")
        for log_entry in self.pipeline_log:
            report.append(f"- {log_entry}")

        report.append("\n## 📊 Summary\n")

        # Count successes and failures
        successes = sum(1 for entry in self.pipeline_log if "✅" in entry)
        failures = sum(1 for entry in self.pipeline_log if "❌" in entry)

        report.append(f"- **Steps Completed**: {successes}")
        report.append(f"- **Steps Failed**: {failures}")
        report.append(
            f"- **Success Rate**: {(successes / (successes + failures) * 100):.1f}%"
            if (successes + failures) > 0
            else "- **Success Rate**: N/A"
        )

        return "\n".join(report)

    def run_pipeline(self) -> bool:
        """Execute complete pipeline"""
        self.log(f"Starting pipeline for {self.config.batch_file}")

        # Pipeline steps
        steps = [
            ("Harvest", self.harvest_batch),
            ("Validate Harvested", self.validate_harvested),
            ("Quality Assessment", self.assess_quality),
            ("Risk Assessment", self.assess_risk),
            ("Final Validation", self.final_validation),
            ("Merge with Main", self.merge_with_main),
        ]

        pipeline_success = True

        for step_name, step_func in steps:
            try:
                success, output = step_func()
                if not success:
                    pipeline_success = False
                    if not self.config.skip_validation:
                        self.log(f"Pipeline failed at step: {step_name}", "ERROR")
                        break
                    else:
                        self.log(f"Step failed but continuing: {step_name}", "WARNING")
            except Exception as e:
                self.log(f"Step exception: {step_name} - {e}", "ERROR")
                pipeline_success = False
                if not self.config.skip_validation:
                    break

        # Generate report
        if self.config.generate_report:
            report = self.generate_pipeline_report()
            report_file = f"pipeline_report_{Path(self.config.batch_file).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

            with open(report_file, "w") as f:
                f.write(report)

            self.log(f"📄 Pipeline report: {report_file}")

        self.log(
            f"Pipeline {'completed successfully' if pipeline_success else 'completed with failures'}"
        )
        return pipeline_success


def main():
    if len(sys.argv) < 2:
        print("Usage: python influx_pipeline_automation.py <batch_file.csv> [options]")
        print("Options:")
        print("  --output-dir DIR     Output directory (default: data/batches)")
        print("  --min-followers N    Entry threshold (default: 50000)")
        print("  --verified-min N     Verified threshold (default: 30000)")
        print("  --skip-validation   Continue on validation failures")
        print("  --update-main       Merge with main dataset")
        print("  --no-report         Skip pipeline report generation")
        sys.exit(1)

    batch_file = sys.argv[1]

    # Parse arguments
    output_dir = "data/batches"
    min_followers = 50000
    verified_min_followers = 30000
    skip_validation = False
    update_main = False
    generate_report = True

    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == "--output-dir" and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
        elif arg == "--min-followers" and i + 1 < len(sys.argv):
            min_followers = int(sys.argv[i + 1])
        elif arg == "--verified-min" and i + 1 < len(sys.argv):
            verified_min_followers = int(sys.argv[i + 1])
        elif arg == "--skip-validation":
            skip_validation = True
        elif arg == "--update-main":
            update_main = True
        elif arg == "--no-report":
            generate_report = False

    # Create config and run pipeline
    config = PipelineConfig(
        batch_file=batch_file,
        output_dir=output_dir,
        min_followers=min_followers,
        verified_min_followers=verified_min_followers,
        skip_validation=skip_validation,
        update_main=update_main,
        generate_report=generate_report,
    )

    pipeline = InfluxPipeline(config)
    success = pipeline.run_pipeline()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
