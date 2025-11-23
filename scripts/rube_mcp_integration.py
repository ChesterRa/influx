#!/usr/bin/env python3
"""
RUBE MCP Integration for Influx

Comprehensive integration script that handles:
- RUBE MCP session management
- Batch user data fetching from Twitter/X
- Data transformation to influx schema
- Quality filtering and validation
- Integration with existing influx pipeline
"""

import json
import sys
import os
import subprocess
import time
import hashlib
import csv
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

# Add parent directory to path to import influx modules
sys.path.append(str(Path(__file__).parent.parent))
from tools.influx_harvest import (
    check_brand_heuristics, check_risk_flags, passes_entry_threshold,
    transform_to_schema, compute_provenance_hash, load_yaml_rules
)

from rube_mcp_config import RubeMCPConfig


class RubeMCPIntegration:
    """Main integration class for RUBE MCP workflows"""
    
    def __init__(self, config_dir: str = "config"):
        self.config = RubeMCPConfig(config_dir)
        self.current_session = None
        self.workflow_settings = self.config.get_workflow_settings()
        self.output_settings = self.config.get_output_settings()
        
        # Ensure output directories exist
        Path(self.output_settings.get("backup_dir", "data/backups")).mkdir(parents=True, exist_ok=True)
        Path(self.output_settings.get("temp_dir", "tmp")).mkdir(parents=True, exist_ok=True)
        Path(self.output_settings.get("results_dir", "archive/rube_results")).mkdir(parents=True, exist_ok=True)
    
    def start_workflow(self, workflow_type: str = "bulk_harvest") -> str:
        """Start a new RUBE MCP workflow session"""
        session_id = self.config.create_session(workflow_type)
        self.current_session = self.config.get_current_session()
        return session_id
    
    def load_handles_from_file(self, file_path: str) -> List[Tuple[str, str]]:
        """Load handles from CSV or text file
        
        Returns:
            List of (handle, category) tuples
        """
        handles = []
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Handles file not found: {file_path}")
        
        try:
            if file_path.suffix.lower() == '.csv':
                # CSV format with 'handle' column
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        handle = row.get('handle', '').strip().lstrip('@')
                        category = row.get('category', '').strip() or self._extract_category_from_filename(file_path.stem)
                        if handle:
                            handles.append((handle, category))
            else:
                # Text format - one handle per line
                category = self._extract_category_from_filename(file_path.stem)
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        handle = line.strip().lstrip('@')
                        if handle and not handle.startswith('#'):
                            handles.append((handle, category))
        
        except Exception as e:
            raise Exception(f"Failed to read handles file {file_path}: {e}")
        
        return handles
    
    def _extract_category_from_filename(self, filename: str) -> str:
        """Extract category from filename (e.g., m21-healthtech -> healthtech)"""
        parts = filename.split('-', 1)
        if len(parts) > 1:
            return parts[1].replace('_', ' ').replace('-', ' ')
        return filename
    
    def create_batches(self, handles: List[Tuple[str, str]], batch_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """Create batches of handles for processing"""
        if not batch_size:
            batch_size = self.workflow_settings.get("max_parallel_batches", 3) * 25  # Default 75 handles per batch
        
        batches = []
        for i in range(0, len(handles), batch_size):
            batch_handles = handles[i:i + batch_size]
            batch_data = {
                "batch_id": f"batch_{i+1:03d}",
                "handles": [h[0] for h in batch_handles],
                "categories": {h[0]: h[1] for h in batch_handles},
                "handle_count": len(batch_handles)
            }
            batches.append(batch_data)
        
        return batches
    
    def execute_rube_batch(self, batch_data: Dict[str, Any]) -> Tuple[bool, List[Dict], str]:
        """Execute a single RUBE MCP batch to fetch user data
        
        Returns:
            (success, users_data, error_message)
        """
        session_id = self.current_session.get("session_id") if self.current_session else "manual"
        batch_id = batch_data["batch_id"]
        handles = batch_data["handles"]
        
        print(f"[INFO] Executing batch {batch_id}: {len(handles)} handles", file=sys.stderr)
        
        # Prepare RUBE MCP tool call
        rube_tools = [{
            "tool_slug": "TWITTER_USER_LOOKUP_BY_USERNAMES",
            "arguments": {
                "usernames": handles,
                "user_fields": [
                    "created_at", "description", "id", "name", 
                    "public_metrics", "verified_type", "username", 
                    "profile_image_url", "location", "url", "protected"
                ],
                "expansions": ["pinned_tweet_id"],
                "tweet_fields": ["created_at", "public_metrics", "text"]
            }
        }]
        
        try:
            # Get memory for RUBE MCP
            memory = self.config.get_memory_for_rube()
            
            # Execute via RUBE MCP using subprocess
            cmd = [
                sys.executable, "-c", f"""
import json
import sys
from rube_RUBE_MULTI_EXECUTE_TOOL import rube_RUBE_MULTI_EXECUTE_TOOL

tools = {json.dumps(rube_tools)}
session_id = "{session_id}"
memory = {json.dumps(memory)}

try:
    result = rube_RUBE_MULTI_EXECUTE_TOOL(
        tools=tools,
        session_id=session_id,
        thought="Fetch Twitter user data for batch {batch_id}",
        memory=memory,
        current_step="FETCHING_USERS",
        current_step_metric=f"0/{len(handles)} users",
        next_step="PROCESSING_RESPONSE",
        sync_response_to_workbench=False
    )
    print(json.dumps(result))
except Exception as e:
    error_result = {{
        "successful": False,
        "error": str(e),
        "data": {{"results": []}}
    }}
    print(json.dumps(error_result))
    sys.exit(1)
"""
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                return False, [], f"RUBE MCP execution failed: {result.stderr}"
            
            # Parse response
            try:
                response = json.loads(result.stdout)
                if not response.get("successful", False):
                    error_msg = response.get("error", "Unknown RUBE MCP error")
                    return False, [], f"RUBE MCP API error: {error_msg}"
                
                # Extract user data from response
                users_data = []
                if "data" in response and "results" in response["data"]:
                    for tool_result in response["data"]["results"]:
                        if tool_result.get("successful") and "response" in tool_result:
                            response_data = tool_result["response"]
                            if "data" in response_data:
                                if isinstance(response_data["data"], list):
                                    users_data.extend(response_data["data"])
                                elif isinstance(response_data["data"], dict):
                                    users_data.append(response_data["data"])
                
                print(f"[INFO] Batch {batch_id} completed: {len(users_data)} users fetched", file=sys.stderr)
                
                # Update memory with batch completion
                self.config.update_memory("twitter", [f"Batch {batch_id} completed: {len(users_data)} users"])
                
                return True, users_data, ""
                
            except json.JSONDecodeError as e:
                return False, [], f"Failed to parse RUBE MCP response: {e}"
                
        except subprocess.TimeoutExpired:
            return False, [], f"Batch {batch_id} timed out after 5 minutes"
            
        except Exception as e:
            return False, [], f"Unexpected error in batch {batch_id}: {e}"
    
    def apply_filters_and_transform(self, users_data: List[Dict], batch_data: Dict[str, Any]) -> List[Dict]:
        """Apply brand/risk filters and transform to influx schema"""
        if not users_data:
            return []
        
        # Load filter rules
        brand_rules = load_yaml_rules("lists/rules/brand_heuristics.yml")
        risk_rules = load_yaml_rules("lists/rules/risk_terms.yml")
        
        processed_users = []
        filter_stats = {
            'total': 0,
            'entry_threshold_fail': 0,
            'brand_filtered': 0,
            'risk_filtered': 0,
            'passed': 0
        }
        
        for user in users_data:
            if not isinstance(user, dict):
                continue
                
            filter_stats['total'] += 1
            username = user.get('username', '')
            
            # Apply entry threshold check
            if not passes_entry_threshold(user):
                filter_stats['entry_threshold_fail'] += 1
                continue
            
            # Apply brand heuristics
            is_brand, brand_conf, brand_matches = check_brand_heuristics(user, brand_rules, False)
            if is_brand:
                filter_stats['brand_filtered'] += 1
                print(f"[FILTER] Brand: @{username} (conf={brand_conf:.2f}, rules={brand_matches})", file=sys.stderr)
                continue
            
            # Apply risk flags
            risk_flags, risk_matches = check_risk_flags(user, risk_rules, set())
            if risk_flags:
                filter_stats['risk_filtered'] += 1
                print(f"[FILTER] Risk: @{username} (flags={risk_flags}, rules={risk_matches})", file=sys.stderr)
                continue
            
            # Transform to influx schema
            category = batch_data["categories"].get(username, "")
            record = transform_to_schema(user, method='rube_mcp_integration', category=category,
                                     brand_rules=brand_rules, allow_brands=False)
            processed_users.append(record)
            filter_stats['passed'] += 1
        
        print(f"[INFO] Batch {batch_data['batch_id']} filter results: {filter_stats['passed']}/{filter_stats['total']} passed", file=sys.stderr)
        return processed_users
    
    def process_single_batch(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single batch and return result"""
        start_time = time.time()
        
        # Execute RUBE MCP batch
        success, users_data, error_msg = self.execute_rube_batch(batch_data)
        
        if not success:
            return {
                "batch_id": batch_data["batch_id"],
                "success": False,
                "error": error_msg,
                "handle_count": batch_data["handle_count"],
                "users_processed": 0,
                "users_passed": 0,
                "processing_time": time.time() - start_time
            }
        
        # Apply filters and transform
        processed_users = self.apply_filters_and_transform(users_data, batch_data)
        
        return {
            "batch_id": batch_data["batch_id"],
            "success": True,
            "handle_count": batch_data["handle_count"],
            "users_processed": len(users_data),
            "users_passed": len(processed_users),
            "processing_time": time.time() - start_time,
            "users": processed_users
        }
    
    def process_batches_parallel(self, batches: List[Dict[str, Any]], max_parallel: Optional[int] = None) -> List[Dict]:
        """Process multiple batches in parallel"""
        if not max_parallel:
            max_parallel = self.workflow_settings.get("max_parallel_batches", 3)
        
        all_results = []
        
        print(f"[INFO] Processing {len(batches)} batches with max {max_parallel} parallel", file=sys.stderr)
        
        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            # Submit all batch jobs
            future_to_batch = {
                executor.submit(self.process_single_batch, batch): batch 
                for batch in batches
            }
            
            # Process completed batches
            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    result = future.result(timeout=600)  # 10 minute timeout per batch
                    all_results.append(result)
                    
                    # Update session with batch result
                    self.config.update_batch_result(result["batch_id"], result)
                    
                    if result["success"]:
                        print(f"[INFO] Batch {result['batch_id']} completed successfully: {result['users_passed']} users", file=sys.stderr)
                    else:
                        print(f"[ERROR] Batch {result['batch_id']} failed: {result.get('error', 'Unknown error')}", file=sys.stderr)
                        
                except TimeoutError:
                    error_result = {
                        "batch_id": batch["batch_id"],
                        "success": False,
                        "error": "Batch timed out after 10 minutes",
                        "handle_count": batch["handle_count"],
                        "users_processed": 0,
                        "users_passed": 0,
                        "processing_time": 600
                    }
                    all_results.append(error_result)
                    self.config.update_batch_result(batch["batch_id"], error_result)
                    print(f"[ERROR] Batch {batch['batch_id']} timed out", file=sys.stderr)
                    
                except Exception as e:
                    error_result = {
                        "batch_id": batch["batch_id"],
                        "success": False,
                        "error": f"Batch processing exception: {e}",
                        "handle_count": batch["handle_count"],
                        "users_processed": 0,
                        "users_passed": 0,
                        "processing_time": 0
                    }
                    all_results.append(error_result)
                    self.config.update_batch_result(batch["batch_id"], error_result)
                    print(f"[ERROR] Batch {batch['batch_id']} exception: {e}", file=sys.stderr)
        
        return all_results
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str) -> bool:
        """Save processing results to JSONL file"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for result in results:
                    if result.get("success") and "users" in result:
                        for user in result["users"]:
                            f.write(json.dumps(user, ensure_ascii=False) + '\n')
            
            print(f"[INFO] Results saved to: {output_file}", file=sys.stderr)
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save results: {e}", file=sys.stderr)
            return False
    
    def save_summary_report(self, results: List[Dict[str, Any]], output_dir: str) -> str:
        """Save summary report of processing results"""
        try:
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            report_file = Path(output_dir) / f"rube_report_{timestamp}.json"
            
            # Calculate summary stats
            total_handles = sum(r["handle_count"] for r in results)
            total_processed = sum(r["users_processed"] for r in results)
            total_passed = sum(r["users_passed"] for r in results)
            successful_batches = sum(1 for r in results if r["success"])
            failed_batches = len(results) - successful_batches
            total_time = sum(r["processing_time"] for r in results)
            
            summary = {
                "session_id": self.current_session.get("session_id") if self.current_session else "unknown",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "summary": {
                    "total_batches": len(results),
                    "successful_batches": successful_batches,
                    "failed_batches": failed_batches,
                    "total_handles": total_handles,
                    "users_fetched": total_processed,
                    "users_passed_filters": total_passed,
                    "success_rate": successful_batches / len(results) if results else 0,
                    "filter_pass_rate": total_passed / total_processed if total_processed > 0 else 0,
                    "total_processing_time_seconds": total_time,
                    "average_throughput_users_per_hour": (total_processed / total_time) * 3600 if total_time > 0 else 0
                },
                "batch_results": results
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            
            print(f"[INFO] Summary report saved to: {report_file}", file=sys.stderr)
            return str(report_file)
            
        except Exception as e:
            print(f"[ERROR] Failed to save summary report: {e}", file=sys.stderr)
            return ""
    
    def run_full_workflow(self, input_file: str, output_file: str, batch_size: Optional[int] = None, 
                        max_parallel: Optional[int] = None) -> bool:
        """Run complete RUBE MCP workflow from input to output"""
        try:
            # Start workflow session
            session_id = self.start_workflow("rube_mcp_integration")
            print(f"[INFO] Started RUBE MCP workflow: {session_id}", file=sys.stderr)
            
            # Load handles
            handles = self.load_handles_from_file(input_file)
            if not handles:
                print("[ERROR] No handles found in input file", file=sys.stderr)
                return False
            
            print(f"[INFO] Loaded {len(handles)} handles from {input_file}", file=sys.stderr)
            
            # Create batches
            batches = self.create_batches(handles, batch_size)
            print(f"[INFO] Created {len(batches)} batches for processing", file=sys.stderr)
            
            # Add batches to session
            for batch in batches:
                self.config.add_batch_to_session(batch)
            
            # Process batches
            results = self.process_batches_parallel(batches, max_parallel)
            
            # Save results
            if not self.save_results(results, output_file):
                return False
            
            # Save summary report
            results_dir = self.output_settings.get("results_dir", "archive/rube_results")
            report_file = self.save_summary_report(results, results_dir)
            
            # Close session
            session_summary = self.config.close_session("completed")
            
            # Print final summary
            total_passed = sum(r["users_passed"] for r in results)
            print(f"\n[SUMMARY] RUBE MCP Workflow Completed:", file=sys.stderr)
            print(f"  Session ID: {session_id}", file=sys.stderr)
            print(f"  Input file: {input_file}", file=sys.stderr)
            print(f"  Output file: {output_file}", file=sys.stderr)
            print(f"  Handles processed: {len(handles)}", file=sys.stderr)
            print(f"  Authors passed filters: {total_passed}", file=sys.stderr)
            print(f"  Success rate: {sum(1 for r in results if r['success'])}/{len(results)} batches", file=sys.stderr)
            if report_file:
                print(f"  Report: {report_file}", file=sys.stderr)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Workflow failed: {e}", file=sys.stderr)
            if self.current_session:
                self.config.close_session("failed")
            return False


def main():
    """CLI interface for RUBE MCP integration"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="RUBE MCP Integration for Influx - Automated user data fetching and processing"
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
        "--config-dir", default="config",
        help="Configuration directory (default: config)"
    )
    
    args = parser.parse_args()
    
    # Initialize integration
    integration = RubeMCPIntegration(args.config_dir)
    
    # Run workflow
    success = integration.run_full_workflow(
        input_file=args.input_file,
        output_file=args.output_file,
        batch_size=args.batch_size,
        max_parallel=args.max_parallel
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
