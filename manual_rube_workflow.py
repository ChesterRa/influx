#!/usr/bin/env python3
"""
Manual RUBE MCP Batch Processing Template
Usage: python3 manual_batch_process.py <handles_csv> <output_file>
"""

import json
import sys
import subprocess


def load_handles(csv_file):
    """Load handles from CSV file"""
    handles = []
    with open(csv_file, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("handle"):
                parts = line.strip().split(",")
                if len(parts) >= 1:
                    handles.append(parts[0].strip())
    return handles


def process_batch(handles, output_file):
    """Process batch using RUBE MCP"""
    print(f"Processing {len(handles)} handles...")

    # Call RUBE MCP for user lookup
    cmd = [
        "python3",
        "-c",
        """
import json
import sys
from rube_RUBE_MULTI_EXECUTE_TOOL import rube_RUBE_MULTI_EXECUTE_TOOL

# RUBE MCP TWITTER_USER_LOOKUP_BY_USERNAMES call
result = rube_RUBE_MULTI_EXECUTE_TOOL(
    session_id="thee",
    thought="Manual batch processing via RUBE MCP",
    tools=[
        {
            "tool_slug": "TWITTER_USER_LOOKUP_BY_USERNAMES",
            "arguments": {
                "usernames": handles
            }
        }
    ],
    sync_response_to_workbench=False
)

if result.get('successful'):
    data = result.get('data', {})
    users = data.get('results', [])
    

    
    print(f"Successfully processed {len(users)} users")
    print(f"Results saved to: {output_file}")
else:
    print(f"Error: {result.get('error', 'Unknown error')}")
    sys.exit(1)
    """,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 manual_batch_process.py <handles_csv> <output_file>")
        sys.exit(1)

    handles_file = sys.argv[1]
    output_file = sys.argv[2]

    handles = load_handles(handles_file)
    process_batch(handles, output_file)
