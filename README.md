# influx

> **High-signal X/Twitter creator index** — curated, evidence-based 5k–10k target; 全流程基于开源多 Agent 框架 [CCCC](https://github.com/ChesterRa/cccc)。

[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Schema Version](https://img.shields.io/badge/schema-v1.0.0-green.svg)](schema/bigv.schema.json)

## 概览 / Overview

- 立意 / Goal: 提供高活跃、非品牌/官方的大V白名单，服务抓取优先级、行业观察与研究。
- 现状 / Status: 171 条，100% 真实 ID，已剔除粉丝数尾数“000”的疑似占位，0 占位；score_version = v1_activity_quality_relevance，manifest sha256=a819bdaec751fb8579ba0968a85c4919cc8ea958d841da0ac4b6cffd2811a379，timestamp=2025-11-22T04:21:18Z。
- 占位清单 / Placeholder TODO: 已清空；粉丝数“000”占位已并入 pipeline_guard。
- 防护 / Guardrails: `scripts/pipeline_guard.sh` 拒绝占位/非数字 ID、mock/test 前缀 handle、重复、粉丝数尾数“000”、manifest 不一致；发布前必跑。
- 方法 / Method: 依托 CCCC 多-Agent 协作框架运行 influx-harvest/score/validate，使用免费层 API，发布严格校验的数据与 manifest。
- 许可 / License: Apache-2.0（代码与数据一致）。

## 面向用户 / For Users（无需跑流水线）

- 下载 / Download: `data/release/influx-latest.jsonl`（171 条严格合规，0 占位/0 mock/0 粉丝尾数“000”）或 `data/release/influx-latest.jsonl.gz`
- Manifest: `data/release/manifest.json`（count、sha256、score_version、timestamp）
- 用途 / Use: 直接用于抓取、排序、分析；高活跃、非品牌/官方作者白名单。

## 面向贡献者 / For Contributors

- 真相源 = `data/latest/latest.jsonl`，发布 = `data/release/*`（两者必须一致）。
- 发布前必跑：`./scripts/pipeline_guard.sh data/latest/latest.jsonl data/latest/manifest.json schema/bigv.schema.json`（现已增加占位 ID 拒绝、去重、manifest 对齐、strict 校验）。
- 评分模型必须在 manifest 中标注 `score_version/score_formula/score_note`（当前 v1 activity+quality+relevance，≥95% 覆盖）。
- 仅允许 `influx-harvest` 产物入库；旁路/临时文件归档，不计进度。
- 占位/粉丝数“000”已清空；如再出现直接拒绝，不得入库。

## Story / 项目价值

- **Purpose**: 高信噪比作者索引，支持 xoperator 等下游抓取优先级、生态情报与研究。
- **原则 Principles**: 质量优先（5k–10k 上限）、证据可追溯、免费层可持续、品牌/官方过滤、严格校验、开源可审计。

### Non-Goals

- Encyclopedia-scale collection (>15k authors)
- Browser automation or paid X API usage
- Black-box scoring or proprietary methods
- Storage of private or sensitive data

---

## Data Model

See [schema/bigv.schema.json](schema/bigv.schema.json) for the full JSON Schema v1.0.0.

### Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Twitter author_id (primary key) |
| `handle` | string | Username without @ (unique) |
| `name` | string | Display name |
| `verified` | string | Verification status: `none`, `blue`, `org`, `legacy` |
| `followers_count` | int | Current follower count |
| `lang_primary` | string | Primary language (ISO 639-1: `en`, `ja`, etc.) |
| `topic_tags` | [string] | Domain tags: `ai_core`, `gpu`, `creator_platform`, `ecosystem`, etc. |

### Metrics (30-day rolling window)

All metrics under `metrics_30d` are computed over the most recent 30 days:

| Field | Description |
|-------|-------------|
| `posts_total` | Total tweets (including replies, retweets) |
| `posts_original` | Original tweets only (excludes replies, retweets) |
| `median_likes` | Median likes per original tweet |
| `p90_likes` | 90th percentile likes per original tweet |
| `median_replies` | Median replies per original tweet |
| `median_retweets` | Median retweets per original tweet |
| `media_rate` | Fraction of original tweets with media (0–1) |

### Scoring & Ranking

| Field | Description |
|-------|-------------|
| `score` | Composite score (0–100): 30% activity + 50% quality + 20% relevance |
| `rank_global` | Global rank by score (1 = highest) |
| `rank_by_topic` | Per-topic ranking: `{topic: rank}` |

### Provenance & Safety

| Field | Description |
|-------|-------------|
| `last_active_at` | ISO 8601 timestamp of most recent original tweet |
| `last_refresh_at` | ISO 8601 timestamp of last metrics update |
| `risk_flags` | Array of flags: `nsfw`, `political`, `controversy`, `spam`, etc. |
| `banned` | Boolean; if true, excluded from exports |
| `sources` | Array of source records with method, timestamp, evidence (tweet IDs) |
| `provenance_hash` | SHA-256 hash of key fields for audit trail |

---

## Usage

### Quick View

```bash
tools/influx-view              # View first 20 records with syntax highlighting
tools/influx-view --lines 10   # View first 10 records
```

### Quick Start（直接用现成数据）

1. **载入本仓库附带的最新数据**:
   ```bash
   cp data/release/influx-latest.jsonl .
   # 或使用压缩版
   cp data/release/influx-latest.jsonl.gz . && gunzip influx-latest.jsonl.gz
   ```

2. **加载与筛选示例**:
   ```python
   import json

   with open("influx-latest.jsonl") as f:
       authors = [json.loads(line) for line in f]

   # 示例：筛选 AI/Tech 英文作者，score ≥ 60
   ai_authors = [
       a for a in authors
       if "ai_core" in a.get("topic_tags", [])
       and a.get("lang_primary") == "en"
       and a.get("score", 0) >= 60
   ]

   print(f"Found {len(ai_authors)} AI/Tech authors")
   ```

3. **集成到你自己的流程**:
   - `handle` → `https://x.com/{handle}`
   - `id` (author_id) → API 调用
   - `score/rank_*` → 优先级排序

### Data Format

- **Primary format**: `data/latest/latest.jsonl.gz` (gzipped JSONL, one author per line)
- **Sorting**: Descending by `score`, then `followers_count`, then `handle` (lexicographic)
- **Versioning**: `data/latest/manifest.json` includes schema version, timestamp, count, SHA-256 checksum, and generation parameters
- **Snapshots**: Daily snapshots in `data/snapshots/YYYY-MM-DD/bigv-YYYYMMDD.jsonl.gz` (published as GitHub Releases)
- **Uncompressed sources**: `data/uncompressed/YYYY-MM-DD/` (milestone sources for reproducibility, latest only)
- **Quick browse**: `data/samples/top200.jsonl` (first 200 records, uncompressed for preview)

---

## Collection Pipeline

The pipeline uses **RUBE MCP Twitter tools** (free tier) exclusively:

1. **Radar** (`influx-radar`): Analyze keyword trends via `TWITTER_RECENT_SEARCH_COUNTS` (12h window)
2. **Harvest** (`influx-harvest`): Fetch tweets via `TWITTER_RECENT_SEARCH` (8 query groups, 2–3 pages each)
3. **Expand** (`influx-expand`): Extract authors and mentions from tweets; batch `USER_LOOKUP` to fill metadata
4. **Filter**: Apply entry thresholds (verified + ≥30k followers OR ≥50k followers), remove brands/officials via `lists/rules/brand_heuristics.yml`, flag risks via `lists/rules/risk_terms.yml`
5. **Score** (`influx-score`): Compute activity/quality/relevance scores (30-day window)
6. **Export** (`influx-export`): Generate `data/latest/latest.jsonl.gz` with manifest
7. **Validate** (`influx-validate`): Check schema compliance, provenance hashes, manifest integrity

### Update Cadence

- **Incremental refresh**: Every 6–12 hours (update metrics for existing authors, discover new authors)
- **Daily snapshot**: Full export published as GitHub Release (tag: `YYYYMMDD`)
- **Weekly recalc**: Full score recalculation to prevent drift

---

## Governance

### Quality Gates

**Entry thresholds**:
- (Verified AND followers ≥ 30k) OR followers ≥ 50k
- At least 5 original tweets in past 30 days
- Language: `en` or `ja` preferred (others allowed with manual review)

**Brand/official filtering**:
- Name/bio keywords: "Official", "Team", "Support", "PR", "Press", "Media", "News", "Corp", "Store"
- Organization verification (`verified=org`) always flagged
- Domain patterns: `.gov`, `.edu`, news/media domains, e-commerce domains

**Risk filtering** (auto-exclude):
- NSFW, spam, scam, hate speech indicators
- Political officials, campaign accounts
- Controversial/inflammatory content (flagged for manual review)

### Contributing

**Adding authors** (via PR):
1. Provide handle and reason (e.g., "AI researcher at X, author of Y paper")
2. Include 2+ recent (within 30d) original tweet links as evidence
3. Ensure author meets entry thresholds and passes filters
4. Submit PR; CI will validate schema and run filters
5. Maintainers review and merge (or request changes)

**Reporting issues**:
- False positives (wrongly excluded): Open issue with handle and reason
- False negatives (wrongly included): Open issue with handle and evidence
- Heuristic improvements: Propose changes to `lists/rules/*.yml`

**Requesting removal**:
- Authors who wish to be excluded: Open issue or contact maintainers
- Account will be added to `banned` list in next cycle (removed from exports)

### License & Disclaimer

- **当前状态**: 统一使用 Apache-2.0（代码与数据一致）。
- **免责声明**: No warranty; use at your own risk。

**Disclaimer**:
- This dataset aggregates **publicly available information** from X (Twitter)
- No private, sensitive, or non-public data is collected or stored
- Inclusion does not imply endorsement; exclusion does not imply criticism
- The dataset is provided "as is" without warranty of any kind
- Users must comply with X Terms of Service and applicable laws
- Authors may request removal at any time (contact via GitHub Issues)

---

## Roadmap

### M0 (Week 1) — Bootstrap ✅ In Progress
- [x] Repository structure, schema v1.0.0, LICENSE, README
- [x] Brand/risk heuristics (YAML rules)
- [ ] CLI tools: `influx-radar`, `influx-harvest`, `influx-expand`, `influx-score`, `influx-export`, `influx-validate`
- [ ] First collection run: 400–600 authors via three-path bootstrap
- [ ] CI: schema validation, lint, manifest checks
- [ ] Release: `data/latest/latest.jsonl.gz` with manifest

### M1 (Weeks 2–3) — Scale & Refine
- [ ] Incremental refresh automation (6–12h cadence)
- [ ] Scale to 2k–3k authors
- [ ] Improve heuristics based on manual review (sample 100/week)
- [ ] Daily snapshot automation (GitHub Actions + Releases)
- [ ] Sharding by topic/language (when count > 1.5k)

### M2 (Weeks 4–6) — Production & Analytics
- [ ] Reach 5k–8k authors; maintain churn < 20%/week
- [ ] Parquet export for analysis workflows
- [ ] Visualization dashboard (independent site)
- [ ] Weekly full recalculation (prevent metric drift)
- [ ] Network analysis: co-mentions, topic clusters

---

## Technical Details

**Tools**: Python 3.10+, RUBE MCP (Twitter tools), SQLite (state), DuckDB (optional analytics), JSON Schema validation

**Rate limits**: Respect X API rate limits (300 requests/15min for search, 900/15min for user lookup); exponential backoff, batch requests

**State management**: `state/influx.db` (SQLite) for persistent author data, metrics history, banned list

**Reproducibility**: All data includes provenance (sources, timestamps, hashes); manifest includes generation parameters

---

## Contact & Support

- **Issues**: [GitHub Issues](https://github.com/user/influx/issues)
- **Discussions**: [GitHub Discussions](https://github.com/user/influx/discussions)
- **License**: [Apache-2.0](LICENSE)

---

**influx** — *high-signal creator index*
