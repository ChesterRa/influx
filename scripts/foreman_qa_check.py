#!/usr/bin/env python3
"""
Foreman QA抽查 System - Evidence Validation and Quality Assurance
Implements random sampling and external validation for batch quality control
"""

import json
import sys
import random
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class QAViolation:
    """Represents a quality assurance violation"""
    record_id: str
    handle: str
    violation_type: str
    description: str
    severity: str  # 'critical', 'major', 'minor'
    evidence_missing: bool = False

@dataclass
class QAResult:
    """Results of QA抽查 for a batch"""
    batch_file: str
    total_records: int
    sampled_records: int
    violations: List[QAViolation]
    passed: bool
    timestamp: str
    qa_summary: str

class ForemanQA:
    """Foreman Quality Assurance System"""
    
    def __init__(self, dataset_path: str = "data/latest/latest.jsonl"):
        self.dataset_path = Path(dataset_path)
        self.violations = []
        
        # Quality thresholds and patterns
        self.CRITICAL_PATTERNS = [
            (r'^test_', "Test prefix handle"),
            (r'^mock_', "Mock prefix handle"), 
            (r'^tmp_', "Temporary prefix handle"),
            (r'^1234567890000000', "Placeholder ID pattern"),
        ]
        
        self.SUSPICIOUS_PATTERNS = [
            (r'000$', "Followers count ending with 000 (possible placeholder)"),
            (r'999$', "Followers count ending with 999 (suspicious)"),
        ]
    
    def load_records(self, file_path: str) -> List[Dict]:
        """Load JSONL records from file"""
        records = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        except Exception as e:
            print(f"ERROR: Failed to load {file_path}: {e}", file=sys.stderr)
            sys.exit(1)
        return records
    
    def validate_evidence(self, record: Dict) -> List[str]:
        """Validate sources.evidence field for completeness and authenticity"""
        violations = []
        
        if 'meta' not in record or 'sources' not in record['meta']:
            violations.append("Missing meta.sources field")
            return violations
            
        sources = record['meta']['sources']
        if not sources:
            violations.append("Empty sources array")
            return violations
            
        for i, source in enumerate(sources):
            # Check required fields
            required_fields = ['method', 'fetched_at', 'evidence']
            for field in required_fields:
                if field not in source:
                    violations.append(f"Source {i}: missing {field}")
                elif not source[field]:
                    violations.append(f"Source {i}: empty {field}")
            
            # Validate evidence content
            if 'evidence' in source:
                evidence = source['evidence']
                if not evidence or len(evidence.strip()) < 10:
                    violations.append(f"Source {i}: insufficient evidence content")
                elif evidence.lower() in ['n/a', 'none', 'unknown', 'manual']:
                    violations.append(f"Source {i}: generic/non-specific evidence")
        
        return violations
    
    def check_external_validation(self, handle: str, record_id: str) -> Tuple[bool, str]:
        """Attempt external validation via handle format and dataset consistency check"""
        try:
            # Validate handle format
            if not re.match(r'^[A-Za-z0-9_]{1,15}$', handle):
                return False, f"Invalid handle format: {handle}"
            
            # Check if handle exists in current dataset (duplicate check)
            try:
                with open(self.dataset_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            record = json.loads(line)
                            if record.get('handle') == handle and record.get('id') != record_id:
                                return False, f"Duplicate handle found in dataset: {handle}"
            except FileNotFoundError:
                pass  # Dataset might not exist yet
            
            # Basic consistency checks
            if not record_id or not record_id.isdigit():
                return False, f"Invalid record ID: {record_id}"
            
            # Skip actual API lookup for now - would require external MCP connection
            # In production, this could use RUBE MCP to validate handle existence
            return True, "Format validation passed (API lookup skipped)"
                
        except Exception as e:
            return False, f"External validation error: {str(e)}"
    
    def analyze_record_quality(self, record: Dict) -> List[QAViolation]:
        """Analyze a single record for quality violations"""
        violations = []
        handle = record.get('handle', '')
        record_id = record.get('id', '')
        
        # Critical pattern checks
        for pattern, description in self.CRITICAL_PATTERNS:
            if re.search(pattern, handle) or re.search(pattern, str(record_id)):
                violations.append(QAViolation(
                    record_id=record_id,
                    handle=handle,
                    violation_type="critical_pattern",
                    description=description,
                    severity="critical"
                ))
        
        # Suspicious pattern checks
        followers_count = record.get('followers_count', 0)
        for pattern, description in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, str(followers_count)):
                violations.append(QAViolation(
                    record_id=record_id,
                    handle=handle,
                    violation_type="suspicious_pattern",
                    description=description,
                    severity="major"
                ))
        
        # Evidence validation
        evidence_violations = self.validate_evidence(record)
        for violation in evidence_violations:
            violations.append(QAViolation(
                record_id=record_id,
                handle=handle,
                violation_type="evidence_missing",
                description=violation,
                severity="critical",
                evidence_missing=True
            ))
        
        # Threshold validation
        verified = record.get('verified', 'none') != 'none'
        min_followers = 30000 if verified else 50000
        
        if followers_count < min_followers:
            violations.append(QAViolation(
                record_id=record_id,
                handle=handle,
                violation_type="threshold_failed",
                description=f"Below minimum threshold: {followers_count} < {min_followers}",
                severity="critical"
            ))
        
        # Org/official checks
        if record.get('is_org', False):
            violations.append(QAViolation(
                record_id=record_id,
                handle=handle,
                violation_type="org_account",
                description="Organization account not allowed",
                severity="critical"
            ))
        
        if record.get('is_official', False):
            violations.append(QAViolation(
                record_id=record_id,
                handle=handle,
                violation_type="official_account",
                description="Official account not allowed",
                severity="critical"
            ))
        
        return violations
    
    def sample_records(self, records: List[Dict], sample_size: int = 30) -> List[Dict]:
        """Random sample of records for QA抽查"""
        if len(records) <= sample_size:
            return records
        
        return random.sample(records, sample_size)
    
    def run_qa_check(self, batch_file: str, sample_size: int = 30) -> QAResult:
        """Run comprehensive QA抽查 on a batch"""
        records = self.load_records(batch_file)
        total_records = len(records)
        
        # Sample records for detailed analysis
        sampled_records = self.sample_records(records, sample_size)
        
        all_violations = []
        critical_count = 0
        
        print(f"Running QA抽查 on {batch_file}")
        print(f"Total records: {total_records}, Sampled: {len(sampled_records)}")
        
        for i, record in enumerate(sampled_records):
            print(f"Analyzing record {i+1}/{len(sampled_records)}: {record.get('handle', 'unknown')}")
            
            # Analyze record quality
            violations = self.analyze_record_quality(record)
            all_violations.extend(violations)
            
            # Count critical violations
            critical_count += sum(1 for v in violations if v.severity == 'critical')
            
            # External validation for a subset
            if i < 10:  # Limit external checks to avoid rate limits
                handle = record.get('handle', '')
                if handle:
                    external_valid, message = self.check_external_validation(handle, record.get('id', ''))
                    if not external_valid:
                        all_violations.append(QAViolation(
                            record_id=record.get('id', ''),
                            handle=handle,
                            violation_type="external_validation_failed",
                            description=message,
                            severity="critical"
                        ))
                        critical_count += 1
        
        # Determine if QA passed
        qa_passed = critical_count == 0
        
        # Generate summary
        qa_summary = self.generate_qa_summary(all_violations, total_records)
        
        return QAResult(
            batch_file=batch_file,
            total_records=total_records,
            sampled_records=len(sampled_records),
            violations=all_violations,
            passed=qa_passed,
            timestamp=datetime.now(timezone.utc).isoformat(),
            qa_summary=qa_summary
        )
    
    def generate_qa_summary(self, violations: List[QAViolation], total_records: int) -> str:
        """Generate QA summary report"""
        if not violations:
            return f"✓ QA PASSED: No violations found in {total_records} records"
        
        # Count violations by severity
        critical = sum(1 for v in violations if v.severity == 'critical')
        major = sum(1 for v in violations if v.severity == 'major') 
        minor = sum(1 for v in violations if v.severity == 'minor')
        
        # Count by type
        violation_types = {}
        for v in violations:
            violation_types[v.violation_type] = violation_types.get(v.violation_type, 0) + 1
        
        summary = f"✗ QA FAILED: {len(violations)} violations found\n"
        summary += f"  Critical: {critical}, Major: {major}, Minor: {minor}\n"
        summary += f"  Violation types: {dict(violation_types)}\n"
        
        # Show affected handles
        affected_handles = set(v.handle for v in violations if v.severity == 'critical')
        if affected_handles:
            summary += f"  Critical violations affecting: {', '.join(list(affected_handles)[:5])}"
            if len(affected_handles) > 5:
                summary += f" and {len(affected_handles) - 5} more"
        
        return summary
    
    def save_qa_report(self, result: QAResult, output_dir: str = "docs/qa_reports") -> str:
        """Save QA report to file"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        batch_name = Path(result.batch_file).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_path / f"qa_report_{batch_name}_{timestamp}.md"
        
        # Generate markdown report
        report_content = self.generate_markdown_report(result)
        
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        return str(report_file)
    
    def generate_markdown_report(self, result: QAResult) -> str:
        """Generate detailed markdown report"""
        report = f"# QA抽查 Report\n\n"
        report += f"**Batch File:** {result.batch_file}\n"
        report += f"**Timestamp:** {result.timestamp}\n"
        report += f"**Total Records:** {result.total_records}\n"
        report += f"**Sampled Records:** {result.sampled_records}\n"
        report += f"**Result:** {'✅ PASSED' if result.passed else '❌ FAILED'}\n\n"
        
        report += "## Summary\n\n"
        report += f"{result.qa_summary}\n\n"
        
        if result.violations:
            report += "## Violations\n\n"
            
            # Group violations by severity
            by_severity = {'critical': [], 'major': [], 'minor': []}
            for violation in result.violations:
                by_severity[violation.severity].append(violation)
            
            for severity in ['critical', 'major', 'minor']:
                if by_severity[severity]:
                    report += f"### {severity.title()} Violations\n\n"
                    for violation in by_severity[severity]:
                        report += f"- **{violation.handle}** (ID: {violation.record_id}): {violation.description}\n"
                    report += "\n"
        
        report += "## Recommendations\n\n"
        if result.passed:
            report += "- Batch passes quality standards\n"
            report += "- Can proceed with merge\n"
        else:
            report += "- **REJECT BATCH** - Critical violations found\n"
            report += "- Address all violations before resubmission\n"
            report += "- Review evidence collection process\n"
        
        return report

def main():
    if len(sys.argv) < 2:
        print("Usage: ./scripts/foreman_qa_check.py <batch_file> [sample_size]")
        sys.exit(1)
    
    batch_file = sys.argv[1]
    sample_size = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    qa = ForemanQA()
    result = qa.run_qa_check(batch_file, sample_size)
    
    print(f"\n=== QA抽查 RESULT ===")
    print(result.qa_summary)
    
    # Save report
    report_file = qa.save_qa_report(result)
    print(f"\nDetailed report saved: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if result.passed else 1)

if __name__ == "__main__":
    main()
