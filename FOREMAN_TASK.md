Title: Foreman Task Brief (Project-specific)

Purpose (free text)
- Continue strategic expansion of high-quality X/Twitter influencer index from current 353 unique authors (canonical: data/latest/latest.jsonl, strict-validated 2025-11-21 03:07Z; manifest refreshed, score version pending confirmation) toward 5k-10k target, focusing on 50k+ follower quality authors while maintaining 100% schema compliance and zero-cost operational model. M1 扩容为首要目标，其余目标依优先级降序执行。

Current objectives (ranked, short)
- 1) P0 M1 Expansion (PEER 执行): 基于 353 严格版，继续 50k+ 粉丝高质量作者扩容，先冲 1k，再向 5k-10k 迈进；保持 ≥15 records/hour，批处理落盘 `.cccc/work/foreman/<timestamp>/`
- 2) P1 Scoring Confirmation/Upgrade (PEER 执行): 确认当前 `meta.score` 模型并切换/标注为 activity(30%)+quality(50%)+relevance(20%)，≥95% 非零覆盖，更新 manifest 的 `score_version/score_formula/score_note`
- 3) P2 Data Hygiene Standardization (PEER 执行): 每批后 dedup `data/latest/latest.jsonl` → `python3 tools/influx-validate --strict -s schema/bigv.schema.json -m data/latest/manifest.json data/latest/latest.jsonl` → 重建 `manifest.json`（count/sha/score_version）
- 4) P3 Automation Preparation (PEER 执行): 固化 lists/following/GitHub org 批处理脚手架，支撑持续扩容

Standing work (edit freely)
- Truth source maintenance: Keep `data/latest/latest.jsonl` canonical; after each batch，dedup + `influx-validate --strict` → rebuild `manifest.json`
- Strict status: 当前 strict 通过（353/353）；后续批次必须保持 strict 通过
- Daily quality check: Run influx-validate on canonical file; fail-fast on schema/brand/risk violations
- Weekly batch processing: Execute lists/following/GitHub org batches; store artifacts in `.cccc/work/foreman/<timestamp>/`
- Scoring coverage: Track and improve ≥95% non-zero coverage on activity+quality+relevance; record version in manifest
- Quality gate enforcement: Only `influx-harvest` ingest; no bypass imports
- Velocity tracking: Maintain ≥15 records/hour sustainable rate

Useful references
- PROJECT.md (strategic overview; canonical count 353, strict-validated 2025-11-21 03:07Z)
- docs/por/POR.md (portfolio board and M1-M3 roadmap)
- docs/por/T000004-m1-manual-scale/SUBPOR.md (active scaling task status)
- docs/por/M2-Phase2-Completion-Criteria.md (95% coverage target)
- docs/por/M3-Automation-Process-Optimization-Framework.md (scaling strategy)
- data/latest/latest.jsonl (canonical, strict-validated 353 rows); data/latest/manifest.json (refreshed: count=353, score_version pending confirmation)
- .cccc/work/foreman/ (execution history and artifacts)

How to act each run
- Do one useful, non-interactive step within the time box (≤ 30m).
- Save temporary outputs to .cccc/work/foreman/<YYYYMMDD-HHMMSS>/.
- Write one message to .cccc/mailbox/foreman/to_peer.md with header To: Both|PeerA|PeerB and wrap body in <TO_PEER>..</TO_PEER>.

Escalation
- If a decision is needed, write a 6–10 line RFD and ask the peer.

Safety
- Do not modify orchestrator code/policies; provide checkable artifacts.
