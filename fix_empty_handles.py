#!/usr/bin/env python3
"""
Remove records with empty handles from dataset
"""

import json


def remove_empty_handles(input_file, output_file):
    removed_count = 0
    kept_count = 0

    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            author = json.loads(line.strip())
            handle = author.get("handle", "")

            # Remove records with empty handles
            if handle and handle.strip():
                outfile.write(json.dumps(author) + "\n")
                kept_count += 1
            else:
                removed_count += 1
                print(
                    f"Removed record with empty handle: ID {author.get('id', 'unknown')}"
                )

    print(f"Removed {removed_count} records with empty handles")
    print(f"Kept {kept_count} valid records")
    return kept_count, removed_count


if __name__ == "__main__":
    remove_empty_handles("data/latest/latest.jsonl", "data/latest/latest_fixed.jsonl")
