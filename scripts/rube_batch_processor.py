#!/usr/bin/env python3
"""
RUBE MCP Batch Processor with Advanced Error Handling

Provides robust batch processing capabilities including:
- Intelligent retry logic with exponential backoff
- Circuit breaker pattern for repeated failures
- Comprehensive error categorization and recovery
- Batch isolation and failure containment
"""

import json
import sys
import time
import random
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading

from rube_mcp_integration import RubeMCPIntegration
from rube_mcp_config import RubeMCPConfig


class ErrorType(Enum):
    """Categories of errors that can occur during processing"""
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    NETWORK = "network"
    API_ERROR = "api_error"
    DATA_FORMAT = "data_format"
    VALIDATION = "validation"
    UNKNOWN = "unknown"


@dataclass
class ProcessingError:
    """Structured error information"""
    error_type: ErrorType
    message: str
    timestamp: datetime
    batch_id: str
    retry_count: int = 0
    original_exception: Optional[Exception] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchResult:
    """Result of batch processing"""
    batch_id: str
    success: bool
    users_processed: int = 0
    users_passed: int = 0
    processing_time: float = 0.0
    errors: List[ProcessingError] = field(default_factory=list)
    retry_attempts: int = 0
    data: List[Dict] = field(default_factory=list)


class CircuitBreaker:
    """Circuit breaker pattern for handling repeated failures"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 300):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self.lock:
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                    print(f"[INFO] Circuit breaker moving to HALF_OPEN state", file=sys.stderr)
                else:
                    raise Exception("Circuit breaker is OPEN - blocking call")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if self.last_failure_time is None:
            return False
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            print(f"[WARNING] Circuit breaker OPENED after {self.failure_count} failures", file=sys.stderr)


class RubeBatchProcessor:
    """Advanced batch processor with error handling and retry logic"""
    
    def __init__(self, config_dir: str = "config"):
        self.config = RubeMCPConfig(config_dir)
        self.integration = RubeMCPIntegration(config_dir)
        self.circuit_breaker = CircuitBreaker()
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 1.0
        self.max_delay = 60.0
        self.jitter_factor = 0.1
        
        # Error statistics
        self.error_stats = {
            ErrorType.RATE_LIMIT: 0,
            ErrorType.TIMEOUT: 0,
            ErrorType.NETWORK: 0,
            ErrorType.API_ERROR: 0,
            ErrorType.DATA_FORMAT: 0,
            ErrorType.VALIDATION: 0,
            ErrorType.UNKNOWN: 0
        }
    
    def categorize_error(self, exception: Exception, context: Dict[str, Any] = None) -> ErrorType:
        """Categorize error type based on exception and context"""
        error_message = str(exception).lower()
        context = context or {}
        
        # Rate limit errors
        if any(keyword in error_message for keyword in ["rate limit", "too many requests", "429"]):
            return ErrorType.RATE_LIMIT
        
        # Timeout errors
        if any(keyword in error_message for keyword in ["timeout", "timed out"]) or \
           context.get("timeout_occurred", False):
            return ErrorType.TIMEOUT
        
        # Network errors
        if any(keyword in error_message for keyword in ["network", "connection", "dns", "unreachable"]):
            return ErrorType.NETWORK
        
        # API errors
        if any(keyword in error_message for keyword in ["api error", "500", "502", "503", "504"]) or \
           context.get("api_error", False):
            return ErrorType.API_ERROR
        
        # Data format errors
        if any(keyword in error_message for keyword in ["json", "parse", "format", "schema"]):
            return ErrorType.DATA_FORMAT
        
        # Validation errors
        if any(keyword in error_message for keyword in ["validation", "invalid", "missing field"]):
            return ErrorType.VALIDATION
        
        return ErrorType.UNKNOWN
    
    def calculate_retry_delay(self, retry_count: int, error_type: ErrorType) -> float:
        """Calculate retry delay with exponential backoff and jitter"""
        # Different base delays for different error types
        base_delays = {
            ErrorType.RATE_LIMIT: 5.0,    # Longer for rate limits
            ErrorType.TIMEOUT: 2.0,        # Moderate for timeouts
            ErrorType.NETWORK: 3.0,        # Longer for network issues
            ErrorType.API_ERROR: 4.0,       # Longer for API errors
            ErrorType.DATA_FORMAT: 1.0,      # Shorter for data format issues
            ErrorType.VALIDATION: 1.0,      # Shorter for validation issues
            ErrorType.UNKNOWN: 2.0           # Moderate for unknown errors
        }
        
        base_delay = base_delays.get(error_type, self.base_delay)
        
        # Exponential backoff
        exponential_delay = min(base_delay * (2 ** retry_count), self.max_delay)
        
        # Add jitter to prevent thundering herd
        jitter = exponential_delay * self.jitter_factor * random.random()
        
        return exponential_delay + jitter
    
    def process_batch_with_retry(self, batch_data: Dict[str, Any]) -> BatchResult:
        """Process a single batch with retry logic and error handling"""
        batch_id = batch_data["batch_id"]
        start_time = time.time()
        
        print(f"[INFO] Processing batch {batch_id} with retry logic", file=sys.stderr)
        
        result = BatchResult(
            batch_id=batch_id,
            success=False,
            users_processed=0,
            users_passed=0,
            processing_time=0.0,
            errors=[],
            retry_attempts=0,
            data=[]
        )
        
        retry_count = 0
        last_error_type = None
        
        while retry_count <= self.max_retries:
            try:
                # Use circuit breaker for API calls
                if retry_count > 0:
                    print(f"[INFO] Retry attempt {retry_count}/{self.max_retries} for batch {batch_id}", file=sys.stderr)
                
                # Process batch through integration
                batch_result = self.circuit_breaker.call(
                    self.integration.process_single_batch, batch_data
                )
                
                if batch_result["success"]:
                    # Successful processing
                    result.success = True
                    result.users_processed = batch_result["users_processed"]
                    result.users_passed = batch_result["users_passed"]
                    result.data = batch_result.get("users", [])
                    result.retry_attempts = retry_count
                    
                    processing_time = time.time() - start_time
                    result.processing_time = processing_time
                    
                    print(f"[INFO] Batch {batch_id} completed successfully after {retry_count} retries", file=sys.stderr)
                    return result
                else:
                    # Processing failed but no exception
                    error_msg = batch_result.get("error", "Unknown processing error")
                    raise Exception(error_msg)
                
            except Exception as e:
                retry_count += 1
                
                # Categorize error
                error_type = self.categorize_error(e, {"batch_id": batch_id})
                
                # Create structured error
                processing_error = ProcessingError(
                    error_type=error_type,
                    message=str(e),
                    timestamp=datetime.now(timezone.utc),
                    batch_id=batch_id,
                    retry_count=retry_count,
                    original_exception=e,
                    context={
                        "batch_size": batch_data.get("handle_count", 0),
                        "retry_count": retry_count
                    }
                )
                
                result.errors.append(processing_error)
                self.error_stats[error_type] += 1
                last_error_type = error_type
                
                print(f"[ERROR] Batch {batch_id} failed (attempt {retry_count}): {error_type.value} - {str(e)}", file=sys.stderr)
                
                # Check if we should retry
                if retry_count > self.max_retries:
                    print(f"[ERROR] Max retries exceeded for batch {batch_id}", file=sys.stderr)
                    break
                
                # Calculate delay and wait
                delay = self.calculate_retry_delay(retry_count, error_type)
                print(f"[INFO] Waiting {delay:.1f}s before retry {retry_count}/{self.max_retries}", file=sys.stderr)
                time.sleep(delay)
        
        # All retries failed
        processing_time = time.time() - start_time
        result.processing_time = processing_time
        result.retry_attempts = retry_count - 1  # Subtract 1 because count is incremented at end
        
        print(f"[ERROR] Batch {batch_id} failed after {retry_count - 1} retries, final error: {last_error_type.value if last_error_type else 'unknown'}", file=sys.stderr)
        return result
    
    def process_batches_with_isolation(self, batches: List[Dict[str, Any]], 
                                   max_parallel: int = 3) -> List[BatchResult]:
        """Process batches with failure isolation"""
        print(f"[INFO] Processing {len(batches)} batches with failure isolation", file=sys.stderr)
        
        results = []
        failed_batches = []
        
        # Process in smaller groups for better isolation
        batch_groups = [batches[i:i + max_parallel] for i in range(0, len(batches), max_parallel)]
        
        for group_idx, batch_group in enumerate(batch_groups):
            print(f"[INFO] Processing batch group {group_idx + 1}/{len(batch_groups)} ({len(batch_group)} batches)", file=sys.stderr)
            
            # Process each batch in group sequentially for isolation
            group_results = []
            for batch in batch_group:
                result = self.process_batch_with_retry(batch)
                group_results.append(result)
                results.append(result)
                
                if not result.success:
                    failed_batches.append(batch)
                    print(f"[WARNING] Batch {result.batch_id} failed, continuing with isolation", file=sys.stderr)
            
            # Small delay between groups
            if group_idx < len(batch_groups) - 1:
                time.sleep(2.0)
        
        # Log isolation summary
        successful_batches = sum(1 for r in results if r.success)
        total_authors = sum(r.users_passed for r in results if r.success)
        
        print(f"\n[ISOLATION SUMMARY]", file=sys.stderr)
        print(f"  Total batches: {len(batches)}", file=sys.stderr)
        print(f"  Successful batches: {successful_batches}", file=sys.stderr)
        print(f"  Failed batches: {len(failed_batches)}", file=sys.stderr)
        print(f"  Total authors added: {total_authors}", file=sys.stderr)
        
        # Print error statistics
        if any(self.error_stats.values()):
            print(f"\n[ERROR STATISTICS]", file=sys.stderr)
            for error_type, count in self.error_stats.items():
                if count > 0:
                    print(f"  {error_type.value}: {count}", file=sys.stderr)
        
        return results
    
    def create_retry_plan(self, failed_results: List[BatchResult]) -> List[Dict[str, Any]]:
        """Create retry plan for failed batches based on error analysis"""
        retry_plan = []
        
        for result in failed_results:
            if not result.success:
                # Analyze errors to determine retry strategy
                retry_errors = []
                non_retry_errors = []
                
                for error in result.errors:
                    # Certain errors are not worth retrying
                    if error.error_type in [ErrorType.DATA_FORMAT, ErrorType.VALIDATION]:
                        non_retry_errors.append(error)
                    else:
                        retry_errors.append(error)
                
                if retry_errors:
                    # Create retry batch
                    retry_batch = {
                        "batch_id": result.batch_id + "_retry",
                        "original_batch_id": result.batch_id,
                        "retry_reason": "mixed_errors",
                        "retry_errors": [e.error_type.value for e in retry_errors],
                        "handle_count": 0,  # Will be filled by caller
                        "handles": [],  # Will be filled by caller
                        "categories": {},  # Will be filled by caller
                        "priority": self._calculate_retry_priority(result)
                    }
                    retry_plan.append(retry_batch)
                
                if non_retry_errors:
                    print(f"[INFO] Batch {result.batch_id} has non-retryable errors: {[e.error_type.value for e in non_retry_errors]}", file=sys.stderr)
        
        # Sort retry plan by priority (highest first)
        retry_plan.sort(key=lambda x: x["priority"], reverse=True)
        
        return retry_plan
    
    def _calculate_retry_priority(self, result: BatchResult) -> float:
        """Calculate retry priority based on error types and batch size"""
        priority = 0.0
        
        # Base priority from batch size (larger batches get higher priority)
        priority += result.users_processed / 100.0
        
        # Adjust based on error types
        error_types = [error.error_type for error in result.errors]
        
        # Network and timeout errors get higher priority (likely transient)
        if ErrorType.NETWORK in error_types or ErrorType.TIMEOUT in error_types:
            priority += 10.0
        
        # Rate limit gets medium priority
        if ErrorType.RATE_LIMIT in error_types:
            priority += 5.0
        
        # API errors get lower priority
        if ErrorType.API_ERROR in error_types:
            priority += 2.0
        
        # Data format and validation errors get very low priority
        if ErrorType.DATA_FORMAT in error_types or ErrorType.VALIDATION in error_types:
            priority -= 5.0
        
        return max(0.0, priority)
    
    def save_error_report(self, results: List[BatchResult], output_dir: str) -> str:
        """Save detailed error report for analysis"""
        try:
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            report_file = Path(output_dir) / f"error_report_{timestamp}.json"
            
            # Collect all errors
            all_errors = []
            for result in results:
                for error in result.errors:
                    all_errors.append({
                        "batch_id": error.batch_id,
                        "error_type": error.error_type.value,
                        "message": error.message,
                        "timestamp": error.timestamp.isoformat(),
                        "retry_count": error.retry_count,
                        "context": error.context
                    })
            
            # Create report
            report = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "summary": {
                    "total_batches": len(results),
                    "successful_batches": sum(1 for r in results if r.success),
                    "failed_batches": sum(1 for r in results if not r.success),
                    "total_errors": len(all_errors),
                    "error_statistics": {error_type.value: count for error_type, count in self.error_stats.items() if count > 0}
                },
                "errors": all_errors,
                "batch_results": [
                    {
                        "batch_id": result.batch_id,
                        "success": result.success,
                        "users_processed": result.users_processed,
                        "users_passed": result.users_passed,
                        "processing_time": result.processing_time,
                        "retry_attempts": result.retry_attempts,
                        "error_count": len(result.errors),
                        "error_types": [error.error_type.value for error in result.errors]
                    }
                    for result in results
                ]
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            print(f"[INFO] Error report saved to: {report_file}", file=sys.stderr)
            return str(report_file)
            
        except Exception as e:
            print(f"[ERROR] Failed to save error report: {e}", file=sys.stderr)
            return ""


def main():
    """CLI interface for batch processor"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="RUBE MCP Batch Processor with Advanced Error Handling"
    )
    parser.add_argument(
        "input_file", help="Input file with handles (CSV or text format)"
    )
    parser.add_argument(
        "output_file", help="Output JSONL file for processed results"
    )
    parser.add_argument(
        "--batch-size", type=int, default=75,
        help="Number of handles per batch (default: 75)"
    )
    parser.add_argument(
        "--max-parallel", type=int, default=3,
        help="Maximum parallel batches (default: 3)"
    )
    parser.add_argument(
        "--max-retries", type=int, default=3,
        help="Maximum retry attempts per batch (default: 3)"
    )
    parser.add_argument(
        "--config-dir", default="config",
        help="Configuration directory (default: config)"
    )
    parser.add_argument(
        "--error-report-dir", default="archive/error_reports",
        help="Directory for error reports (default: archive/error_reports)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize processor
        processor = RubeBatchProcessor(args.config_dir)
        processor.max_retries = args.max_retries
        
        # Ensure error report directory exists
        Path(args.error_report_dir).mkdir(parents=True, exist_ok=True)
        
        # Start workflow session
        session_id = processor.config.create_session("batch_processor_with_retry")
        print(f"[INFO] Started batch processor session: {session_id}", file=sys.stderr)
        
        # Load handles and create batches
        handles = processor.integration.load_handles_from_file(args.input_file)
        if not handles:
            print("[ERROR] No handles found in input file", file=sys.stderr)
            return 1
        
        print(f"[INFO] Loaded {len(handles)} handles from {args.input_file}", file=sys.stderr)
        
        batches = processor.integration.create_batches(handles, args.batch_size)
        print(f"[INFO] Created {len(batches)} batches for processing", file=sys.stderr)
        
        # Add batches to session
        for batch in batches:
            processor.config.add_batch_to_session(batch)
        
        # Process batches with isolation
        results = processor.process_batches_with_isolation(batches, args.max_parallel)
        
        # Save successful results
        successful_results = [r for r in results if r.success]
        if successful_results:
            all_users = []
            for result in successful_results:
                all_users.extend(result.data)
            
            # Save to output file
            output_path = Path(args.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for user in all_users:
                    f.write(json.dumps(user, ensure_ascii=False) + '\n')
            
            print(f"[INFO] Saved {len(all_users)} processed users to: {args.output_file}", file=sys.stderr)
        else:
            print("[WARNING] No successful batches to save", file=sys.stderr)
        
        # Save error report
        failed_results = [r for r in results if not r.success]
        if failed_results:
            error_report_file = processor.save_error_report(results, args.error_report_dir)
            print(f"[INFO] Error report with {len(failed_results)} failed batches saved", file=sys.stderr)
        
        # Close session
        session_summary = processor.config.close_session("completed")
        
        # Print final summary
        total_passed = sum(r.users_passed for r in results if r.success)
        total_failed = len(failed_results)
        
        print(f"\n[FINAL SUMMARY]", file=sys.stderr)
        print(f"  Session ID: {session_id}", file=sys.stderr)
        print(f"  Input file: {args.input_file}", file=sys.stderr)
        print(f"  Output file: {args.output_file}", file=sys.stderr)
        print(f"  Handles processed: {len(handles)}", file=sys.stderr)
        print(f"  Authors added: {total_passed}", file=sys.stderr)
        print(f"  Successful batches: {len(successful_results)}", file=sys.stderr)
        print(f"  Failed batches: {total_failed}", file=sys.stderr)
        if total_failed > 0:
            print(f"  Check error report for failure details", file=sys.stderr)
        
        return 0 if len(successful_results) > 0 else 1
        
    except Exception as e:
        print(f"[ERROR] Batch processor failed: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
