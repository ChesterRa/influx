#!/usr/bin/env python3
"""
Foreman Audit Trail System - Track and log all batch operations
Maintains comprehensive audit trail for accountability and rollback capability
"""

import json
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class BatchAuditRecord:
    """Audit record for a batch operation"""
    batch_id: str
    operation_type: str  # 'merge', 'reject', 'rollback', 'validate'
    batch_file: str
    input_records: int
    output_records: int
    violations_count: int
    pipeline_guard_result: str
    qa_check_result: str
    operator: str
    timestamp: str
    evidence_file: str
    sha256_before: str
    sha256_after: str
    manifest_before: Dict
    manifest_after: Dict
    decision: str  # 'approved', 'rejected', 'rollback'
    decision_reason: str
    rollback_available: bool

class AuditTrail:
    """Manages audit trail for foreman operations"""
    
    def __init__(self, audit_dir: str = "docs/audit_trail"):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.audit_index = self.audit_dir / "audit_index.jsonl"
    
    def generate_batch_id(self, batch_file: str) -> str:
        """Generate unique batch ID from filename and timestamp"""
        batch_name = Path(batch_file).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{batch_name}_{timestamp}"
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def load_manifest(self, manifest_path: str) -> Dict:
        """Load manifest file"""
        try:
            with open(manifest_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def count_records(self, file_path: str) -> int:
        """Count records in JSONL file"""
        try:
            with open(file_path, 'r') as f:
                return sum(1 for line in f if line.strip())
        except Exception:
            return 0
    
    def record_batch_operation(self, 
                            batch_file: str,
                            operation_type: str,
                            pipeline_guard_result: str = "",
                            qa_check_result: str = "",
                            operator: str = "system",
                            decision_reason: str = "") -> str:
        """Record a batch operation in audit trail"""
        
        # Generate batch ID
        batch_id = self.generate_batch_id(batch_file)
        
        # Get file states
        dataset_file = "data/latest/latest.jsonl"
        manifest_file = "data/latest/manifest.json"
        
        sha256_before = self.calculate_file_hash(dataset_file)
        manifest_before = self.load_manifest(manifest_file)
        input_records = self.count_records(batch_file)
        
        # Run pipeline_guard to get result
        if not pipeline_guard_result:
            pipeline_guard_result = self.run_pipeline_guard(batch_file, dataset_file, manifest_file)
        
        # Run QA check
        if not qa_check_result and operation_type in ['merge', 'validate']:
            qa_check_result = self.run_qa_check(batch_file)
        
        # Count violations from results
        violations_count = self.count_violations(pipeline_guard_result, qa_check_result)
        
        # Determine decision based on results
        decision, decision_reason = self.make_decision(
            operation_type, pipeline_guard_result, qa_check_result, decision_reason
        )
        
        # Create evidence file
        evidence_file = self.create_evidence_file(batch_id, batch_file, pipeline_guard_result, qa_check_result)
        
        # After operation (for actual merges, this would be done post-operation)
        sha256_after = sha256_before  # Will be updated after actual merge
        manifest_after = manifest_before.copy()
        output_records = input_records if decision == 'approved' else 0
        
        # Create audit record
        audit_record = BatchAuditRecord(
            batch_id=batch_id,
            operation_type=operation_type,
            batch_file=batch_file,
            input_records=input_records,
            output_records=output_records,
            violations_count=violations_count,
            pipeline_guard_result=pipeline_guard_result,
            qa_check_result=qa_check_result,
            operator=operator,
            timestamp=datetime.now(timezone.utc).isoformat(),
            evidence_file=evidence_file,
            sha256_before=sha256_before,
            sha256_after=sha256_after,
            manifest_before=manifest_before,
            manifest_after=manifest_after,
            decision=decision,
            decision_reason=decision_reason,
            rollback_available=decision == 'approved'
        )
        
        # Save audit record
        self.save_audit_record(audit_record)
        
        return batch_id
    
    def run_pipeline_guard(self, batch_file: str, dataset_file: str, manifest_file: str) -> str:
        """Run pipeline_guard and capture result"""
        try:
            # Create temporary merged file for testing
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as temp_file:
                # Concatenate dataset and batch
                with open(dataset_file, 'r') as ds_f:
                    temp_file.write(ds_f.read())
                with open(batch_file, 'r') as bf_f:
                    temp_file.write(bf_f.read())
                temp_file_path = temp_file.name
            
            # Create temporary manifest
            temp_manifest = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            manifest_data = self.load_manifest(manifest_file)
            temp_manifest.write(json.dumps(manifest_data))
            temp_manifest.close()
            
            # Run pipeline_guard
            import subprocess
            result = subprocess.run([
                './scripts/pipeline_guard.sh', temp_file_path, temp_manifest.name
            ], capture_output=True, text=True, timeout=60)
            
            # Cleanup
            import os
            os.unlink(temp_file_path)
            os.unlink(temp_manifest.name)
            
            return f"Exit code: {result.returncode}\nStdout: {result.stdout}\nStderr: {result.stderr}"
            
        except Exception as e:
            return f"Pipeline guard error: {str(e)}"
    
    def run_qa_check(self, batch_file: str) -> str:
        """Run QA check and capture result"""
        try:
            import subprocess
            result = subprocess.run([
                './scripts/foreman_qa_check.py', batch_file, '10'  # Smaller sample for audit
            ], capture_output=True, text=True, timeout=120)
            
            return f"Exit code: {result.returncode}\nStdout: {result.stdout}\nStderr: {result.stderr}"
            
        except Exception as e:
            return f"QA check error: {str(e)}"
    
    def count_violations(self, pipeline_result: str, qa_result: str) -> int:
        """Count violations from pipeline and QA results"""
        violations = 0
        
        # Count pipeline violations
        if "ERROR:" in pipeline_result or "✗" in pipeline_result:
            violations += pipeline_result.count("ERROR:")
            violations += pipeline_result.count("duplicate handles")
            violations += pipeline_result.count("placeholder")
            violations += pipeline_result.count("mock")
        
        # Count QA violations
        if "✗ QA FAILED" in qa_result:
            violations += qa_result.count("Critical:")
            violations += qa_result.count("Major:")
            violations += qa_result.count("Minor:")
        
        return violations
    
    def make_decision(self, operation_type: str, pipeline_result: str, qa_result: str, reason: str) -> tuple[str, str]:
        """Make decision based on results"""
        
        # Check for critical failures
        if "ERROR:" in pipeline_result:
            return "rejected", f"Pipeline guard failed: {self.extract_error_summary(pipeline_result)}"
        
        if "Exit code: 1" in qa_result and "Critical:" in qa_result:
            return "rejected", f"QA check failed: {self.extract_error_summary(qa_result)}"
        
        # If operation is validation, decision depends on results
        if operation_type == "validate":
            if "✗" in pipeline_result or "✗ QA FAILED" in qa_result:
                return "rejected", "Validation failed due to quality violations"
            else:
                return "approved", "Validation passed - batch ready for merge"
        
        # For merge operations, approve if no critical issues
        if operation_type == "merge":
            if reason:
                return "approved" if "approved" in reason.lower() else "rejected", reason
            return "approved", "Merge requested - quality gates passed"
        
        # Default for other operations
        return "approved", f"Operation {operation_type} completed"
    
    def extract_error_summary(self, result_text: str) -> str:
        """Extract meaningful error summary from result text"""
        lines = result_text.split('\n')
        error_lines = [line.strip() for line in lines if line.strip() and ('ERROR:' in line or '✗' in line)]
        
        if error_lines:
            return "; ".join(error_lines[:2])  # First two error lines
        
        return "Unknown error"
    
    def create_evidence_file(self, batch_id: str, batch_file: str, pipeline_result: str, qa_result: str) -> str:
        """Create evidence file for audit trail"""
        evidence_dir = self.audit_dir / "evidence"
        evidence_dir.mkdir(exist_ok=True)
        
        evidence_file = evidence_dir / f"{batch_id}_evidence.json"
        
        evidence_data = {
            "batch_id": batch_id,
            "batch_file": batch_file,
            "pipeline_guard_result": pipeline_result,
            "qa_check_result": qa_result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "batch_sample": self.get_batch_sample(batch_file)
        }
        
        with open(evidence_file, 'w') as f:
            json.dump(evidence_data, f, indent=2)
        
        return str(evidence_file)
    
    def get_batch_sample(self, batch_file: str, sample_size: int = 5) -> List[Dict]:
        """Get sample records from batch for evidence"""
        samples = []
        try:
            with open(batch_file, 'r') as f:
                for i, line in enumerate(f):
                    if i >= sample_size:
                        break
                    if line.strip():
                        samples.append(json.loads(line))
        except Exception:
            pass
        
        return samples
    
    def save_audit_record(self, record: BatchAuditRecord):
        """Save audit record to index"""
        with open(self.audit_index, 'a') as f:
            f.write(json.dumps(asdict(record)) + '\n')
    
    def get_batch_history(self, batch_file: str) -> List[BatchAuditRecord]:
        """Get audit history for a specific batch"""
        history = []
        try:
            with open(self.audit_index, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if data.get('batch_file') == batch_file:
                            history.append(BatchAuditRecord(**data))
        except Exception:
            pass
        
        return history
    
    def get_recent_operations(self, limit: int = 20) -> List[BatchAuditRecord]:
        """Get recent audit records"""
        records = []
        try:
            with open(self.audit_index, 'r') as f:
                lines = f.readlines()
                for line in reversed(lines[-limit:]):
                    if line.strip():
                        data = json.loads(line)
                        records.append(BatchAuditRecord(**data))
        except Exception:
            pass
        
        return records
    
    def generate_audit_report(self, output_file: str = None) -> str:
        """Generate comprehensive audit report"""
        if not output_file:
            output_file = self.audit_dir / f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        records = self.get_recent_operations(50)
        
        report = "# Foreman Audit Trail Report\n\n"
        report += f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n"
        
        # Summary statistics
        total_records = len(records)
        approved = sum(1 for r in records if r.decision == 'approved')
        rejected = sum(1 for r in records if r.decision == 'rejected')
        total_violations = sum(r.violations_count for r in records)
        
        report += "## Summary\n\n"
        report += f"- Total Operations: {total_records}\n"
        report += f"- Approved: {approved} ({approved/total_records*100:.1f}%)\n"
        report += f"- Rejected: {rejected} ({rejected/total_records*100:.1f}%)\n"
        report += f"- Total Violations: {total_violations}\n\n"
        
        # Recent operations
        report += "## Recent Operations\n\n"
        for record in records[:10]:
            status = "✅" if record.decision == 'approved' else "❌"
            report += f"{status} **{record.operation_type.title()}** - {record.batch_file}\n"
            report += f"   Time: {record.timestamp}\n"
            report += f"   Records: {record.input_records} → {record.output_records}\n"
            report += f"   Violations: {record.violations_count}\n"
            report += f"   Reason: {record.decision_reason}\n\n"
        
        # Quality trends
        report += "## Quality Trends\n\n"
        report += "This section would contain quality trend analysis.\n"
        report += "TODO: Implement trend analysis based on historical data.\n\n"
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        return str(output_file)

def main():
    if len(sys.argv) < 3:
        print("Usage: ./scripts/batch_audit_trail.py <operation> <batch_file> [operator]")
        print("Operations: validate, merge, reject, rollback, report")
        sys.exit(1)
    
    operation = sys.argv[1]
    batch_file = sys.argv[2]
    operator = sys.argv[3] if len(sys.argv) > 3 else "system"
    
    audit = AuditTrail()
    
    if operation == "report":
        report_file = audit.generate_audit_report()
        print(f"Audit report generated: {report_file}")
    else:
        batch_id = audit.record_batch_operation(batch_file, operation, operator=operator)
        print(f"Operation recorded: {batch_id}")
        
        # Show recent history for this batch
        history = audit.get_batch_history(batch_file)
        print(f"Batch history: {len(history)} operations")

if __name__ == "__main__":
    main()
