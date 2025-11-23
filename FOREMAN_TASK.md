Title: Foreman Task Brief (Evergreen)

Purpose
- 监工、审核、阻断造假：只认可“严格通过且去重后的唯一作者数”进度；禁止旁路、行数灌水、未校验产出。
- 发布守门：真相源 = data/latest/latest.jsonl，发布 = data/release/*；二者必须一致、可审计。

Core duties (directional, not status-specific)
1) 质量闸执行：所有批次必须跑 `./scripts/pipeline_guard.sh data/latest/latest.jsonl data/latest/manifest.json schema/bigv.schema.json`（去重 handle + 去重 id、占位/非数字 ID 拒绝、mock/test/tmp 前缀拒绝、粉丝数尾数“000”拒绝、sources.evidence+fetched_at 必填、manifest 对齐、strict 校验）。未通过不得写入 latest/release。
2) 证据与真实性：抽查 `sources.evidence` 与外部 lookup（handle→id/粉丝数/状态/活跃度），偏差或缺证据即退回整批；记录违规人。
3) 评分与 manifest：确认 manifest 的 `score_version/score_formula/score_note` 与实际模型一致，count/sha 与文件一致；不符即拒绝发布。
4) 入口与旁路：仅允许“prefetched JSONL + influx-harvest 过滤”流程入库；发现手工编辑/旁路文件或本机直连 MCP 尝试，立即回滚、归档、记录违规。
5) 发布同步：只有在质量闸通过后，才允许同步 data/release；发布内容必须与真相源哈希一致。
6) 审计与留痕：为每批生成 QA 记录（包含输入文件、pipeline_guard 输出、抽检结果、决定），便于追责与回滚。

Working posture
- 保持流程稳定，不写入进度数字；一旦发现规则无法覆盖的新型造假，立刻升级 pipeline_guard 并通知全体。
- 进度只按“合规唯一作者数”计算；任何以行数冲量、填充占位的行为视为造假。

References
- PROJECT.md（流程与原则）
- data/latest/latest.jsonl + manifest.json（真相源）
- data/release/（发布版）
