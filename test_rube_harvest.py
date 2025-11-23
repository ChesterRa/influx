#!/usr/bin/env python3
"""
Test script to run influx-harvest within RUBE MCP session
"""

import sys
import os
import json
from pathlib import Path

# Add the tools directory to path
sys.path.insert(0, str(Path(__file__).parent / "tools"))

# Import and run influx-harvest directly
import importlib.util

spec = importlib.util.spec_from_file_location(
    "influx_harvest", Path(__file__).parent / "tools" / "influx-harvest"
)
if spec is None:
    raise ImportError("Could not load influx-harvest module")
influx_harvest = importlib.util.module_from_spec(spec)
if spec.loader is None:
    raise ImportError("Could not get loader for influx-harvest module")
spec.loader.exec_module(influx_harvest)

if __name__ == "__main__":
    # Simulate command line arguments
    sys.argv = [
        "influx-harvest",
        "bulk",
        "--handles",
        "elonmusk",
        "--out",
        "/tmp/test_rube_output.jsonl",
        "--default-category",
        "test",
        "--min-followers",
        "1000000",
    ]

    result = influx_harvest.main()
    print(f"Result: {result}")

    # Check output
    if os.path.exists("/tmp/test_rube_output.jsonl"):
        with open("/tmp/test_rube_output.jsonl", "r") as f:
            content = f.read()
            print(f"Output file content: {content}")
