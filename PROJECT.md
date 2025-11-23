（请保持本文件为“长期流程与原则”文档，避免写入易变的进度数字）
# influx - X/Twitter 影响力作者索引

## 核心目标与原则
- 构建高活跃、非官号、非品牌的跨领域 BigV 索引（目标量级 5k–10k，质量优先）。
- 原则：质量 > 数量；证据可追溯；流程可审计；对外友好（Apache-2.0）。
- 零容忍假数据：严禁 test/mock/tmp/占位 ID/凑行数，任何违规直接回滚并处罚。

## 生产流程（PEER 必遵循）
1) **采集/扩容**：两段式无本地 MCP 依赖——在具备 MCP 的环境批量获取 Twitter 用户 JSONL（prefetched），然后在本仓库用 `influx-harvest x-lists|bulk --prefetched-users <file>` 过滤入库。禁止在本仓库直连 MCP 或手填数据。
   - 必须附带 sources.evidence + fetched_at；无证据直接拒绝。
   - 入口检查：handle 与 id 必须全局唯一，粉丝尾数“000”拒绝。
2) **过滤/阈值**：入口即应用阈值——(verified 且 ≥30k) 或 ≥50k 粉丝；品牌/官方/机构号剔除。
3) **证据与溯源**：每条记录的 `sources` 必含 method + fetched_at + evidence（tweet/list/github 链接）；无证据不得入库。
   - **Grandfather Clause (2025-11-23)**: 2025-11-23T18:00Z 之前入库的记录允许 "@handle" 格式的 evidence；2025-11-23T18:00Z 之后的所有新批次必须提供完整 URL 证据（tweet/list/github 链接）。
4) **批次合并**：使用 `./scripts/merge_batch.sh <batch_file>` 强制合并批次，禁止手工 cat/追加。该脚本自动执行：创建备份、临时合并、pipeline_guard 校验、仅当通过后才更新 dataset 与 release。违规手工合并导致的质量问题直接回滚。
5) **校验与防造假**：merge_batch.sh 内置 pipeline_guard 强制检查：去重、拒绝占位/非数字 ID、拒绝 mock/test/tmp 前缀、拒绝粉丝数尾数"000"、manifest 对齐、strict schema 校验。任何违规自动中止合并。
6) **发布同步**：merge_batch.sh 自动同步 `data/release/influx-latest.jsonl(.gz)` 与 manifest；手工操作必须先过 pipeline_guard。
7) **差分与审计**：新增/修改应保留证据与采集命令记录，便于审计和回滚；禁止手工编辑 latest 以绕过流程。

## 防造假与质量红线
- 禁止：占位 ID、粉丝尾数“000”、手填或捏造指标、非存在账号、重复 handle、mock/test/tmp 前缀。
- 进度仅按“严格合规且去重后的唯一作者数”统计，未过质量闸的行数不计。
- 如发现单条假数据：整批退回并重新提交；重复违规者冻结提交权限。

## Seeds 治理（源头防控）
- 来源要求：公开可查证的 list/following/GitHub org/新闻证据；禁止猜测、低粉或不存在账号。
- CSV 要求：列含 `handle`、`evidence`（URL）、`source_type`、`fetched_at`；不得手填粉丝数。
- 准入阈值：种子层面即应用 ≥50k（或 verified+≥30k）标准，低于阈值直接删除。
- 提交流程：先用 `influx-harvest --lookup` 批量校验存在性/粉丝数/状态，再去重、过滤品牌/官方，最后再跑 pipeline_guard，合规后方可合并。

## 扩容策略（M1 优先）
- 方向：先补足高质量真实作者，再扩量；优先 lists/following/GitHub org 批量，高活跃技术/安全/AI/DevOps/创作者等领域。
- 节奏：每批次≥一次 pipeline_guard + 抽检；严禁以行数冲量。

## 发布规范
- 真相源：`data/latest/latest.jsonl` + `data/latest/manifest.json`；发布版：`data/release/influx-latest.jsonl(.gz)` + manifest，二者必须一致。
- Manifest 必填：count、sha256、schema_version、timestamp、score_version/score_formula/score_note、source_file、sort_order。

## 角色分工
- **PEER（执行）**：采集、清洗、跑 pipeline_guard、提交差分与证据、同步 release。
- **项目负责人**：审核差分与证据、抽检质量、维护 schema/脚本、决策许可/发布节奏。

## Schema 设计 (v1.0.0 摘要)
关键字段：`id`（author_id）、`handle`、`name`、`verified`、`followers_count`、`is_org`、`is_official`、`lang_primary`、`topic_tags`、`metrics_30d`、`meta`（score/last_refresh_at/sources/provenance_hash）。
完整 schema 见 `schema/bigv.schema.json`。
