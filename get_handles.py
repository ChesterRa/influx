import csv
import re
import sys

def get_valid_twitter_handles(input_csv_path):
    valid_handles = []
    twitter_username_pattern = re.compile(r"^[A-Za-z0-9_]{1,15}$")

    with open(input_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            handle = row.get('handle')
            if handle and twitter_username_pattern.match(handle):
                valid_handles.append(handle)
            elif handle:
                print(f"Skipping invalid handle (regex mismatch): {handle}", file=sys.stderr)
            else:
                print(f"Skipping row with missing handle: {row}", file=sys.stderr)
                
    return valid_handles

if __name__ == "__main__":
    input_file = "lists/seeds/m16-creator-economy-batch.csv"
    
    handles_to_fetch = get_valid_twitter_handles(input_file)
    for handle in handles_to_fetch:
        print(handle)
