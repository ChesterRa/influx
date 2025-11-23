#!/usr/bin/env python3
"""
RUBE MCP Configuration and Session Management

Handles configuration, session creation, and connection management for RUBE MCP workflows.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any


class RubeMCPConfig:
    """Configuration and session manager for RUBE MCP workflows"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "rube_mcp_config.json"
        self.session_file = self.config_dir / "current_session.json"
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        default_config = {
            "toolkit_settings": {
                "twitter": {
                    "batch_size": 100,
                    "rate_limit_delay": 1.0,
                    "timeout": 300,
                    "retry_attempts": 3
                },
                "github": {
                    "batch_size": 50,
                    "rate_limit_delay": 2.0,
                    "timeout": 600,
                    "retry_attempts": 2
                }
            },
            "workflow_settings": {
                "max_parallel_batches": 3,
                "quality_threshold": 50.0,
                "entry_threshold": {
                    "verified_min_followers": 30000,
                    "unverified_min_followers": 50000
                }
            },
            "output_settings": {
                "backup_dir": "data/backups",
                "temp_dir": "tmp",
                "results_dir": "archive/rube_results"
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults for any missing keys
                    return {**default_config, **loaded_config}
            except Exception as e:
                print(f"[WARNING] Failed to load config: {e}, using defaults", file=sys.stderr)
                return default_config
        else:
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save config: {e}", file=sys.stderr)
    
    def create_session(self, workflow_type: str = "bulk_harvest") -> str:
        """Create a new RUBE MCP session"""
        session_id = f"{workflow_type}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        
        session_data = {
            "session_id": session_id,
            "workflow_type": workflow_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "stats": {
                "total_handles": 0,
                "processed_handles": 0,
                "successful_fetches": 0,
                "failed_fetches": 0,
                "authors_added": 0
            },
            "batches": [],
            "memory": {
                "twitter": [],
                "github": []
            }
        }
        
        try:
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save session: {e}", file=sys.stderr)
            
        return session_id
    
    def get_current_session(self) -> Optional[Dict[str, Any]]:
        """Get current session data"""
        if not self.session_file.exists():
            return None
            
        try:
            with open(self.session_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load session: {e}", file=sys.stderr)
            return None
    
    def update_session(self, updates: Dict[str, Any]) -> bool:
        """Update current session with new data"""
        session = self.get_current_session()
        if not session:
            return False
            
        session.update(updates)
        
        try:
            with open(self.session_file, 'w') as f:
                json.dump(session, f, indent=2)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to update session: {e}", file=sys.stderr)
            return False
    
    def add_batch_to_session(self, batch_data: Dict[str, Any]) -> bool:
        """Add batch information to current session"""
        session = self.get_current_session()
        if not session:
            return False
            
        session["batches"].append(batch_data)
        
        # Update stats
        stats = session["stats"]
        stats["total_handles"] += batch_data.get("handle_count", 0)
        
        return self.update_session({"batches": session["batches"], "stats": stats})
    
    def update_batch_result(self, batch_id: str, result: Dict[str, Any]) -> bool:
        """Update batch result in current session"""
        session = self.get_current_session()
        if not session:
            return False
            
        # Find and update the batch
        for batch in session["batches"]:
            if batch.get("batch_id") == batch_id:
                batch["result"] = result
                batch["completed_at"] = datetime.now(timezone.utc).isoformat()
                
                # Update session stats
                stats = session["stats"]
                stats["processed_handles"] += batch.get("handle_count", 0)
                if result.get("success", False):
                    stats["successful_fetches"] += 1
                    stats["authors_added"] += result.get("authors_added", 0)
                else:
                    stats["failed_fetches"] += 1
                
                return self.update_session({"batches": session["batches"], "stats": stats})
        
        return False
    
    def close_session(self, status: str = "completed") -> Dict[str, Any]:
        """Close current session and return summary"""
        session = self.get_current_session()
        if not session:
            return {}
            
        session["status"] = status
        session["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        # Save session history
        history_file = self.config_dir / f"session_{session['session_id']}.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(session, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save session history: {e}", file=sys.stderr)
        
        # Clear current session
        try:
            self.session_file.unlink()
        except:
            pass
            
        return session
    
    def get_memory_for_rube(self) -> Dict[str, List[str]]:
        """Get memory data in format expected by RUBE MCP"""
        session = self.get_current_session()
        if not session:
            return {"twitter": [], "github": []}
            
        return session.get("memory", {"twitter": [], "github": []})
    
    def update_memory(self, app: str, memories: List[str]) -> bool:
        """Update memory for specific app"""
        session = self.get_current_session()
        if not session:
            return False
            
        if "memory" not in session:
            session["memory"] = {"twitter": [], "github": []}
            
        session["memory"][app].extend(memories)
        
        return self.update_session({"memory": session["memory"]})
    
    def get_toolkit_settings(self, toolkit: str) -> Dict[str, Any]:
        """Get settings for specific toolkit"""
        return self.config.get("toolkit_settings", {}).get(toolkit, {})
    
    def get_workflow_settings(self) -> Dict[str, Any]:
        """Get workflow settings"""
        return self.config.get("workflow_settings", {})
    
    def get_output_settings(self) -> Dict[str, Any]:
        """Get output settings"""
        return self.config.get("output_settings", {})


def main():
    """CLI for RUBE MCP configuration management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RUBE MCP Configuration Management")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # create-session command
    create_parser = subparsers.add_parser("create-session", help="Create new RUBE MCP session")
    create_parser.add_argument("--workflow-type", default="bulk_harvest", 
                           help="Type of workflow (default: bulk_harvest)")
    
    # get-session command
    get_parser = subparsers.add_parser("get-session", help="Get current session info")
    
    # close-session command
    close_parser = subparsers.add_parser("close-session", help="Close current session")
    close_parser.add_argument("--status", default="completed", 
                          help="Session status (default: completed)")
    
    # config command
    config_parser = subparsers.add_parser("show-config", help="Show current configuration")
    
    args = parser.parse_args()
    
    rube_config = RubeMCPConfig()
    
    if args.command == "create-session":
        session_id = rube_config.create_session(args.workflow_type)
        print(f"Created session: {session_id}")
        
    elif args.command == "get-session":
        session = rube_config.get_current_session()
        if session:
            print(json.dumps(session, indent=2))
        else:
            print("No active session")
            
    elif args.command == "close-session":
        session = rube_config.close_session(args.status)
        if session:
            print(f"Closed session: {session['session_id']}")
            print(json.dumps(session["stats"], indent=2))
        else:
            print("No active session to close")
            
    elif args.command == "show-config":
        print(json.dumps(rube_config.config, indent=2))


if __name__ == "__main__":
    main()
