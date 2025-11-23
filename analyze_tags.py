import json
from collections import Counter

def analyze_topic_tags(file_path):
    tags_counter = Counter()
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip(): continue
            record = json.loads(line)
            tags = record.get('topic_tags', [])
            tags_counter.update(tags)
    
    print("Topic Tag Distribution:")
    for tag, count in tags_counter.most_common():
        print(f"- {tag}: {count}")

if __name__ == "__main__":
    analyze_topic_tags("data/latest/latest.jsonl")
