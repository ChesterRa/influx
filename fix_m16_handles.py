#!/usr/bin/env python3
"""
Fix handles that exceed Twitter's 15-character limit or contain invalid characters
"""

import json


def fix_handles(input_file, output_file):
    fixed_count = 0

    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            author = json.loads(line.strip())
            handle = author["handle"]

            # Fix handles that are too long or contain invalid characters
            if len(handle) > 15 or "-" in handle:
                original_handle = handle

                # Replace dashes with underscores and truncate to 15 characters
                handle = handle.replace("-", "_")[:15]
                author["handle"] = handle
                fixed_count += 1

                print(f"Fixed: {original_handle} -> {handle}")

            # Write fixed record
            outfile.write(json.dumps(author) + "\n")

    print(f"Fixed {fixed_count} handles")
    return fixed_count


if __name__ == "__main__":
    fix_handles(
        "data/latest/latest_with_m16.jsonl", "data/latest/latest_m16_fixed.jsonl"
    )
