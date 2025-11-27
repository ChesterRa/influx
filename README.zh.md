# influx

基于开源多 Agent 框架 [CCCC](https://github.com/ChesterRa/cccc) 的功能性示范项目，提供高价值的 X.com 热门推主清单（influencer list，强调个人非品牌/官方），直接下载即可使用。本仓库仅包含“可下载使用”的最小集；完整生产流程需要 CCCC + RUBE MCP（Twitter 工具）来抓取数据。

[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE) [![Schema](https://img.shields.io/badge/schema-v1.0.0-green.svg)](schema/bigv.schema.json)

## 这是什么
- 一份严格过滤的热门推主名单（个人账号，非品牌/官方），目标规模 5k–10k。
- 当前发布：`data/release/influx-latest.jsonl`（365 条）及 `manifest.json`（含 count/sha256/schema_version/timestamp/score_version）。
- 已包含的开源最小集：发布数据、`scripts/pipeline_guard.sh`、`schema/bigv.schema.json`、规则（`lists/rules/brand_heuristics.yml`、`lists/rules/risk_terms.yml`）、示例 `data/prefetched.sample.jsonl`（本地过滤演示用）。
- 面向使用者直接消费数据，无需运行生产流水线。

## 为什么有价值
- **抓取/聚合**：高信噪比白名单，降低无关账号的抓取成本。
- **研究/监测**：便于趋势跟踪、社区分析、影响力网络研究。
- **产品冷启动**：可直接导入高质量作者列表，用于推荐/舆情/预警等场景。

## 列表定义（筛选条件）
- 个人账号，品牌/官方/机构号剔除（brand heuristics）。
- 阈值：Verified 且 ≥30k，或 ≥50k 粉丝。
- 活跃度：保留近 30 天活跃度字段（metrics_30d*），过于陈旧的账号在上游被过滤。
- 证据：每条记录包含 `sources.evidence` + `fetched_at`，便于核验与追溯。
- 硬防线：handle 和 id 全局唯一；占位 ID、粉丝“000”、mock/test 前缀、非数字 ID 一律拒绝；strict schema 校验。

## 下载
- 最新数据：[`data/release/influx-latest.jsonl`](data/release/influx-latest.jsonl)
- 压缩版：[`data/release/influx-latest.jsonl.gz`](data/release/influx-latest.jsonl.gz)
- Manifest：[`data/release/manifest.json`](data/release/manifest.json)

## 快速使用
```bash
cp data/release/influx-latest.jsonl .
# 或压缩版
cp data/release/influx-latest.jsonl.gz . && gunzip influx-latest.jsonl.gz
```
```python
import json

with open("influx-latest.jsonl") as f:
    authors = [json.loads(line) for line in f]

# 示例：筛选英文 AI 领域作者，score ≥ 60
ai_authors = [
    a for a in authors
    if "ai_core" in a.get("topic_tags", [])
    and a.get("lang_primary") == "en"
    and a.get("score", 0) >= 60
]
print(len(ai_authors))
```

## 数据模型（摘要）
- 完整 schema：`schema/bigv.schema.json`
- 关键字段：`id`（author_id）、`handle`、`name`、`verified`、`followers_count`、`lang_primary`、`topic_tags`、`metrics_30d*`、`meta.sources`（含 evidence/fetched_at）、`provenance_hash`。

## 生产方式（了解即可，使用者无需运行）
- 完整流程需：CCCC + RUBE MCP（Twitter 工具）获取用户 → 生成 prefetched JSONL → 用 `influx-harvest x-lists|bulk --prefetched-users <file>` 过滤 → 运行 `scripts/pipeline_guard.sh`（去重 handle/id、证据必填、占位/“000”拒绝、strict schema）→ 发布到 `data/release/`。
- 本仓库仅提供数据、guard、schema、规则及示例，不包含 MCP 抓取部分。

## 许可
- Apache-2.0（代码与数据一致）。

## 致谢
- 基于 CCCC 多 Agent 框架完成数据生成与校验；感谢所有贡献者的清洗与审计工作。
