#!/usr/bin/env python3
"""
Batch Prioritization and Processing Tool
Identifies high-value unprocessed batches for efficient pipeline execution
"""

import json
import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter
from datetime import datetime


class BatchPrioritizer:
    """Analyzes and prioritizes unprocessed batches for pipeline processing"""

    def __init__(self):
        self.data_dir = Path("data")
        self.seeds_dir = Path("lists/seeds")
        self.batches_dir = Path("data/batches")
        self.current_dataset = self._load_current_handles()

    def _load_current_handles(self) -> set:
        """Load handles from current main dataset"""
        try:
            with open(self.data_dir / "latest" / "latest.jsonl") as f:
                return {json.loads(line)["handle"] for line in f if line.strip()}
        except FileNotFoundError:
            return set()

    def _analyze_seed_file(self, seed_file: Path) -> Dict[str, Any]:
        """Analyze a seed file for quality and potential value"""
        try:
            content = seed_file.read_text()
            lines = [
                line
                for line in content.split("\n")
                if line.strip() and not line.startswith("handle,")
            ]

            handles = []
            for line in lines:
                if "," in line:
                    handle = line.split(",")[0].strip()
                    if handle and len(handle) > 2 and "@" not in handle:
                        handles.append(handle)

            # Quality assessment
            quality_score = 0
            if len(handles) >= 10:
                quality_score += 2  # Good size
            elif len(handles) >= 5:
                quality_score += 1

            # Check for complete handles (not just first names)
            complete_handles = [
                h for h in handles if "." in h or "_" in h or len(h) > 8
            ]
            if complete_handles:
                ratio = len(complete_handles) / len(handles) if handles else 0
                if ratio > 0.7:
                    quality_score += 3  # High-quality handles
                elif ratio > 0.4:
                    quality_score += 2  # Medium-quality handles
                elif ratio > 0.2:
                    quality_score += 1  # Some quality handles

            # Check for topic diversity (from filename)
            filename = seed_file.name.lower()
            topic_keywords = {
                "ai": ["ai", "ml", "machine", "learning", "research"],
                "gaming": ["gaming", "game", "esports"],
                "security": ["security", "cyber", "devsecops"],
                "climate": ["climate", "sustainability", "green"],
                "fintech": ["fintech", "finance", "bitcoin", "crypto"],
                "creator": ["creator", "economy"],
                "vc": ["vc", "invest", "venture"],
                "geographic": [
                    "geographic",
                    "africa",
                    "asia",
                    "europe",
                    "america",
                    "india",
                    "canada",
                ],
            }

            detected_topics = []
            for topic, keywords in topic_keywords.items():
                if any(keyword in filename for keyword in keywords):
                    detected_topics.append(topic)

            return {
                "file": seed_file.name,
                "total_handles": len(handles),
                "complete_handles": len(complete_handles),
                "quality_score": quality_score,
                "topics": detected_topics,
                "handles": handles[:10],  # Sample for review
            }

        except Exception as e:
            return {"file": seed_file.name, "error": str(e)}

    def _check_processed_status(self, seed_file: Path) -> bool:
        """Check if a seed file has already been processed"""
        base_name = seed_file.stem.replace("-", "_").replace("geographic_", "")

        # Look for corresponding processed batch
        for batch_file in self.batches_dir.glob("*.jsonl"):
            if base_name in batch_file.name:
                # Check if batch has content and passes validation
                try:
                    with open(batch_file) as f:
                        content = f.read().strip()
                        if content and len(content.split("\n")) > 1:
                            return True
                except:
                    pass
        return False

    def analyze_unprocessed_batches(self) -> List[Dict[str, Any]]:
        """Analyze all unprocessed seed files"""
        results = []

        for seed_file in self.seeds_dir.glob("*.csv"):
            if seed_file.name == "README.md":
                continue

            is_processed = self._check_processed_status(seed_file)
            if is_processed:
                continue

            analysis = self._analyze_seed_file(seed_file)
            analysis["processed"] = False
            analysis["priority"] = self._calculate_priority(analysis)
            results.append(analysis)

        # Sort by priority (highest first)
        results.sort(key=lambda x: x["priority"], reverse=True)
        return results

    def _calculate_priority(self, analysis: Dict[str, Any]) -> int:
        """Calculate processing priority for a batch"""
        priority = 0

        # Base score from quality assessment
        priority += analysis.get("quality_score", 0)

        # Bonus for high handle count
        handle_count = analysis.get("total_handles", 0)
        if handle_count >= 30:
            priority += 3
        elif handle_count >= 20:
            priority += 2
        elif handle_count >= 10:
            priority += 1

        # Topic bonuses
        topics = analysis.get("topics", [])
        if "ai" in topics:
            priority += 2  # AI is high priority
        if "geographic" in topics:
            priority += 1  # Geographic diversity
        if "vc" in topics:
            priority += 1  # Investor coverage

        # Penalty for low-quality handles
        complete_ratio = analysis.get("complete_handles", 0) / max(
            analysis.get("total_handles", 1), 1
        )
        if complete_ratio < 0.3:
            priority -= 2  # Low-quality handles

        return max(0, priority)

    def generate_processing_plan(self, top_n: int = 5) -> str:
        """Generate a prioritized processing plan"""
        unprocessed = self.analyze_unprocessed_batches()

        plan = ["# Batch Processing Plan\n"]
        plan.append(f"Generated: {datetime.now().isoformat()}")
        plan.append(f"Current dataset: {len(self.current_dataset)} authors")
        plan.append(f"Unprocessed batches: {len(unprocessed)}\n")

        if not unprocessed:
            plan.append("✅ All seed batches have been processed!")
            return "\n".join(plan)

        plan.append("## Top Priority Batches\n")

        for i, batch in enumerate(unprocessed[:top_n], 1):
            plan.append(f"### {i}. {batch['file']}")
            plan.append(f"- **Priority Score**: {batch['priority']}")
            plan.append(
                f"- **Handles**: {batch['total_handles']} total, {batch.get('complete_handles', 0)} complete"
            )
            plan.append(f"- **Topics**: {', '.join(batch.get('topics', ['unknown']))}")
            plan.append(f"- **Sample handles**: {', '.join(batch.get('handles', []))}")

            # Processing recommendation
            if batch["priority"] >= 6:
                plan.append(f"- **Recommendation**: 🚀 Process immediately")
            elif batch["priority"] >= 4:
                plan.append(f"- **Recommendation**: ✅ Process this week")
            else:
                plan.append(
                    f"- **Recommendation**: ⚠️  Review handles before processing"
                )

            plan.append("")

        plan.append("## Processing Commands\n")
        plan.append("For high-priority batches, use:")
        plan.append("```bash")
        plan.append("./tools/influx-harvest bulk --handles-file lists/seeds/{FILE} \\")
        plan.append("  --out data/batches/{PROCESSED_NAME}.jsonl \\")
        plan.append("  --min-followers 50000 --verified-min-followers 30000")
        plan.append("```")

        return "\n".join(plan)


def main():
    prioritizer = BatchPrioritizer()

    if len(sys.argv) > 1 and sys.argv[1] == "--plan":
        top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        print(prioritizer.generate_processing_plan(top_n))
    else:
        unprocessed = prioritizer.analyze_unprocessed_batches()
        print(f"Found {len(unprocessed)} unprocessed batches")

        for batch in unprocessed[:10]:
            print(
                f"{batch['file']}: priority={batch['priority']}, handles={batch['total_handles']}"
            )


if __name__ == "__main__":
    main()
