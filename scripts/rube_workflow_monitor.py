#!/usr/bin/env python3
"""
RUBE MCP Workflow Monitor and Execution Orchestrator

Provides monitoring, execution orchestration, and management capabilities
for RUBE MCP workflows including:
- Active session monitoring
- Workflow progress tracking
- Error recovery and retry logic
- Performance metrics and reporting
"""

import json
import sys
import time
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from rube_mcp_config import RubeMCPConfig
from rube_mcp_integration import RubeMCPIntegration


@dataclass
class WorkflowStatus:
    """Data class for workflow status information"""
    session_id: str
    workflow_type: str
    status: str
    created_at: str
    total_handles: int
    processed_handles: int
    successful_batches: int
    failed_batches: int
    authors_added: int
    progress_percentage: float
    estimated_completion: Optional[str]
    current_step: str


class RubeWorkflowMonitor:
    """Monitor and orchestrate RUBE MCP workflows"""
    
    def __init__(self, config_dir: str = "config"):
        self.config = RubeMCPConfig(config_dir)
        self.output_settings = self.config.get_output_settings()
        
    def get_active_workflows(self) -> List[WorkflowStatus]:
        """Get list of all active workflow sessions"""
        config_dir = Path(self.config.config_dir)
        active_sessions = []
        
        # Check for current session file
        current_session = self.config.get_current_session()
        if current_session:
            status = self._parse_session_status(current_session)
            if status:
                active_sessions.append(status)
        
        # Check for incomplete sessions in config directory
        for session_file in config_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    if session_data.get("status") in ["active", "running"]:
                        status = self._parse_session_status(session_data)
                        if status:
                            active_sessions.append(status)
            except Exception as e:
                print(f"[WARNING] Failed to parse session file {session_file}: {e}", file=sys.stderr)
        
        return active_sessions
    
    def _parse_session_status(self, session_data: Dict[str, Any]) -> Optional[WorkflowStatus]:
        """Parse session data into WorkflowStatus"""
        try:
            session_id = session_data.get("session_id", "")
            workflow_type = session_data.get("workflow_type", "unknown")
            status = session_data.get("status", "unknown")
            created_at = session_data.get("created_at", "")
            
            stats = session_data.get("stats", {})
            total_handles = stats.get("total_handles", 0)
            processed_handles = stats.get("processed_handles", 0)
            successful_fetches = stats.get("successful_fetches", 0)
            failed_fetches = stats.get("failed_fetches", 0)
            authors_added = stats.get("authors_added", 0)
            
            # Calculate progress
            progress_percentage = (processed_handles / total_handles * 100) if total_handles > 0 else 0
            
            # Estimate completion time
            estimated_completion = None
            if processed_handles > 0 and total_handles > processed_handles:
                elapsed = self._calculate_elapsed_time(created_at)
                if elapsed > 0:
                    rate = processed_handles / elapsed
                    remaining_handles = total_handles - processed_handles
                    remaining_time = remaining_handles / rate
                    estimated_completion = self._format_time_remaining(remaining_time)
            
            # Determine current step
            current_step = self._determine_current_step(session_data)
            
            return WorkflowStatus(
                session_id=session_id,
                workflow_type=workflow_type,
                status=status,
                created_at=created_at,
                total_handles=total_handles,
                processed_handles=processed_handles,
                successful_batches=successful_fetches,
                failed_batches=failed_fetches,
                authors_added=authors_added,
                progress_percentage=progress_percentage,
                estimated_completion=estimated_completion,
                current_step=current_step
            )
            
        except Exception as e:
            print(f"[ERROR] Failed to parse session status: {e}", file=sys.stderr)
            return None
    
    def _calculate_elapsed_time(self, created_at: str) -> float:
        """Calculate elapsed time in seconds since creation"""
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            return (now - created).total_seconds()
        except:
            return 0
    
    def _format_time_remaining(self, seconds: float) -> str:
        """Format time remaining in human readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    def _determine_current_step(self, session_data: Dict[str, Any]) -> str:
        """Determine current step based on session data"""
        batches = session_data.get("batches", [])
        if not batches:
            return "initializing"
        
        completed_batches = sum(1 for batch in batches if "completed_at" in batch)
        total_batches = len(batches)
        
        if completed_batches == 0:
            return "processing_batches"
        elif completed_batches < total_batches:
            return f"processing_batches ({completed_batches}/{total_batches})"
        else:
            return "finalizing"
    
    def monitor_active_workflow(self, session_id: Optional[str] = None, interval: int = 30) -> None:
        """Monitor active workflow(s) with specified interval"""
        print(f"[INFO] Starting workflow monitor (interval: {interval}s)", file=sys.stderr)
        
        try:
            while True:
                active_workflows = self.get_active_workflows()
                
                if not active_workflows:
                    print("[INFO] No active workflows found", file=sys.stderr)
                    break
                
                # Filter by session ID if specified
                if session_id:
                    active_workflows = [w for w in active_workflows if w.session_id == session_id]
                    if not active_workflows:
                        print(f"[INFO] No active workflow found with session ID: {session_id}", file=sys.stderr)
                        break
                
                # Display status
                timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
                print(f"\n[{timestamp}] Workflow Status:", file=sys.stderr)
                
                for workflow in active_workflows:
                    self._display_workflow_status(workflow)
                
                # Check if all workflows are completed
                all_completed = all(w.status in ["completed", "failed"] for w in active_workflows)
                if all_completed:
                    print("[INFO] All workflows completed", file=sys.stderr)
                    break
                
                # Wait for next check
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n[INFO] Monitor stopped by user", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] Monitor error: {e}", file=sys.stderr)
    
    def _display_workflow_status(self, workflow: WorkflowStatus) -> None:
        """Display workflow status in formatted way"""
        progress_bar = self._create_progress_bar(workflow.progress_percentage)
        
        print(f"  Session: {workflow.session_id}", file=sys.stderr)
        print(f"  Type: {workflow.workflow_type} | Status: {workflow.status}", file=sys.stderr)
        print(f"  Progress: {workflow.processed_handles}/{workflow.total_handles} handles ({workflow.progress_percentage:.1f}%)", file=sys.stderr)
        print(f"  {progress_bar}", file=sys.stderr)
        print(f"  Batches: {workflow.successful_batches} success, {workflow.failed_batches} failed", file=sys.stderr)
        print(f"  Authors added: {workflow.authors_added}", file=sys.stderr)
        print(f"  Current step: {workflow.current_step}", file=sys.stderr)
        if workflow.estimated_completion:
            print(f"  ETA: {workflow.estimated_completion}", file=sys.stderr)
        print("", file=sys.stderr)
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create ASCII progress bar"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percentage:.1f}%"
    
    def get_workflow_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get workflow execution history"""
        config_dir = Path(self.config.config_dir)
        history = []
        
        # Find all session files
        session_files = sorted(config_dir.glob("session_*.json"), reverse=True)[:limit]
        
        for session_file in session_files:
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    # Extract key information
                    history_item = {
                        "session_id": session_data.get("session_id"),
                        "workflow_type": session_data.get("workflow_type"),
                        "status": session_data.get("status"),
                        "created_at": session_data.get("created_at"),
                        "completed_at": session_data.get("completed_at"),
                        "stats": session_data.get("stats", {}),
                        "batch_count": len(session_data.get("batches", []))
                    }
                    history.append(history_item)
            except Exception as e:
                print(f"[WARNING] Failed to parse history file {session_file}: {e}", file=sys.stderr)
        
        return history
    
    def retry_failed_workflow(self, session_id: str, output_file: str) -> bool:
        """Retry a failed workflow by reprocessing failed batches"""
        try:
            # Find session file
            config_dir = Path(self.config.config_dir)
            session_file = config_dir / f"session_{session_id}.json"
            
            if not session_file.exists():
                print(f"[ERROR] Session file not found: {session_file}", file=sys.stderr)
                return False
            
            # Load session data
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            if session_data.get("status") != "failed":
                print(f"[ERROR] Session {session_id} is not in failed status", file=sys.stderr)
                return False
            
            # Extract failed batches
            batches = session_data.get("batches", [])
            failed_batches = [batch for batch in batches if batch.get("result", {}).get("success") == False]
            
            if not failed_batches:
                print(f"[INFO] No failed batches found in session {session_id}", file=sys.stderr)
                return True
            
            print(f"[INFO] Retrying {len(failed_batches)} failed batches from session {session_id}", file=sys.stderr)
            
            # Initialize integration for retry
            integration = RubeMCPIntegration()
            
            # Process failed batches
            retry_results = []
            for batch in failed_batches:
                batch_data = {
                    "batch_id": batch["batch_id"] + "_retry",
                    "handles": batch["handles"],
                    "categories": batch.get("categories", {}),
                    "handle_count": batch["handle_count"]
                }
                
                result = integration.process_single_batch(batch_data)
                retry_results.append(result)
                
                if result["success"]:
                    print(f"[INFO] Retry successful for batch {batch['batch_id']}: {result['users_passed']} users", file=sys.stderr)
                else:
                    print(f"[ERROR] Retry failed for batch {batch['batch_id']}: {result.get('error', 'Unknown error')}", file=sys.stderr)
            
            # Save retry results
            if not integration.save_results(retry_results, output_file):
                return False
            
            # Print retry summary
            successful_retries = sum(1 for r in retry_results if r["success"])
            total_users_retried = sum(r["users_passed"] for r in retry_results if r["success"])
            
            print(f"\n[RETRY SUMMARY]", file=sys.stderr)
            print(f"  Failed batches retried: {len(failed_batches)}", file=sys.stderr)
            print(f"  Successful retries: {successful_retries}", file=sys.stderr)
            print(f"  Users recovered: {total_users_retried}", file=sys.stderr)
            print(f"  Output: {output_file}", file=sys.stderr)
            
            return successful_retries > 0
            
        except Exception as e:
            print(f"[ERROR] Failed to retry workflow: {e}", file=sys.stderr)
            return False
    
    def generate_performance_report(self, days: int = 7) -> str:
        """Generate performance report for recent workflows"""
        try:
            # Get workflow history
            history = self.get_workflow_history(limit=50)
            
            # Filter by date range
            cutoff_date = datetime.now(timezone.utc).timestamp() - (days * 24 * 3600)
            recent_history = []
            
            for item in history:
                try:
                    created_at = datetime.fromisoformat(item.get("created_at", "").replace('Z', '+00:00')).timestamp()
                    if created_at >= cutoff_date:
                        recent_history.append(item)
                except:
                    continue
            
            if not recent_history:
                return f"No workflow data found in the last {days} days"
            
            # Calculate metrics
            total_workflows = len(recent_history)
            completed_workflows = sum(1 for item in recent_history if item.get("status") == "completed")
            failed_workflows = sum(1 for item in recent_history if item.get("status") == "failed")
            
            total_handles = sum(item.get("stats", {}).get("total_handles", 0) for item in recent_history)
            total_authors = sum(item.get("stats", {}).get("authors_added", 0) for item in recent_history)
            
            # Calculate success rate
            success_rate = (completed_workflows / total_workflows * 100) if total_workflows > 0 else 0
            
            # Calculate average throughput
            total_time = 0
            workflows_with_time = 0
            
            for item in recent_history:
                try:
                    if item.get("created_at") and item.get("completed_at"):
                        start = datetime.fromisoformat(item["created_at"].replace('Z', '+00:00'))
                        end = datetime.fromisoformat(item["completed_at"].replace('Z', '+00:00'))
                        total_time += (end - start).total_seconds()
                        workflows_with_time += 1
                except:
                    continue
            
            avg_throughput = (total_authors / total_time * 3600) if total_time > 0 else 0
            
            # Generate report
            report = f"""
RUBE MCP Workflow Performance Report (Last {days} Days)
{'=' * 60}

Workflow Summary:
- Total Workflows: {total_workflows}
- Completed: {completed_workflows} ({success_rate:.1f}%)
- Failed: {failed_workflows} ({100-success_rate:.1f}%)

Processing Summary:
- Total Handles Processed: {total_handles:,}
- Total Authors Added: {total_authors:,}
- Average Success Rate: {success_rate:.1f}%

Performance Metrics:
- Average Throughput: {avg_throughput:.1f} authors/hour
- Average Processing Time: {total_time/max(workflows_with_time, 1):.1f} seconds/workflow

Recent Workflows:
"""
            
            # Add recent workflow details
            for item in recent_history[:10]:  # Show last 10
                session_id = item.get("session_id", "unknown")[:16]
                status = item.get("status", "unknown")
                authors = item.get("stats", {}).get("authors_added", 0)
                created = item.get("created_at", "")[:19]
                report += f"- {session_id} | {status:10} | {authors:4} authors | {created}\n"
            
            return report
            
        except Exception as e:
            return f"Failed to generate performance report: {e}"


def main():
    """CLI interface for workflow monitor"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="RUBE MCP Workflow Monitor and Management"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor active workflows")
    monitor_parser.add_argument("--session-id", help="Specific session ID to monitor")
    monitor_parser.add_argument("--interval", type=int, default=30, 
                             help="Monitor interval in seconds (default: 30)")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List active workflows")
    
    # history command
    history_parser = subparsers.add_parser("history", help="Show workflow history")
    history_parser.add_argument("--limit", type=int, default=10,
                             help="Number of recent workflows to show (default: 10)")
    
    # retry command
    retry_parser = subparsers.add_parser("retry", help="Retry failed workflow")
    retry_parser.add_argument("session_id", help="Session ID to retry")
    retry_parser.add_argument("output_file", help="Output file for retry results")
    
    # report command
    report_parser = subparsers.add_parser("report", help="Generate performance report")
    report_parser.add_argument("--days", type=int, default=7,
                           help="Number of days to include (default: 7)")
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = RubeWorkflowMonitor()
    
    if args.command == "monitor":
        monitor.monitor_active_workflow(args.session_id, args.interval)
        
    elif args.command == "list":
        active_workflows = monitor.get_active_workflows()
        if not active_workflows:
            print("No active workflows")
        else:
            for workflow in active_workflows:
                print(f"{workflow.session_id} | {workflow.workflow_type} | {workflow.status} | {workflow.progress_percentage:.1f}%")
                
    elif args.command == "history":
        history = monitor.get_workflow_history(args.limit)
        if not history:
            print("No workflow history found")
        else:
            print("Recent Workflows:")
            for item in history:
                session_id = item.get("session_id", "unknown")[:16]
                status = item.get("status", "unknown")
                authors = item.get("stats", {}).get("authors_added", 0)
                created = item.get("created_at", "")[:19]
                print(f"- {session_id} | {status:10} | {authors:4} authors | {created}")
                
    elif args.command == "retry":
        success = monitor.retry_failed_workflow(args.session_id, args.output_file)
        sys.exit(0 if success else 1)
        
    elif args.command == "report":
        report = monitor.generate_performance_report(args.days)
        print(report)


if __name__ == "__main__":
    main()
