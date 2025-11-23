Title: Foreman Task Brief (Project-specific)

Purpose (principles)
- 监工与审核：只认可“严格通过且去重后的唯一作者数”进度；阻断旁路、行数灌水、未打分/未校验的产出。
- 发布规范：真相源=data/latest/latest.jsonl，发布=data/release/*；二者必须一致、可审计。

Current objectives (ranked, stable)
0）之前的M1列表中出现了大量的假数据，叮嘱PEER们亲自认真执行假数据的修复工作，坚决杜绝一切假数据。
1) 质量闸：每批必须跑 `./scripts/pipeline_guard.sh data/latest/latest.jsonl data/latest/manifest.json schema/bigv.schema.json`（去重+manifest 对齐+strict），未通过不得写入 latest/release。
2) 评分治理：manifest 必须准确填写 `score_version/score_formula/score_note`，与实际模型一致（目标 activity+quality+relevance，≥95% 非零覆盖）。
3) 进度定义：只统计严格通过、去重后的唯一作者数；发现行数灌水或旁路文件，立即退回并归档。
4) 发布纪律：仅 `influx-harvest` 产物可入真相源；中间/备份文件归档到 archive/。

Standing work
- 每批审核：确认已跑 pipeline_guard，strict 通过后才覆盖 data/latest 与 data/release；未通过立即退回。
- 计数/一致性：核对 manifest count/sha 与文件一致，dup_count=0；不符不得发布。
- 评分检查：确认 manifest 记录的评分版本与实际模型一致；缺失时阻止发布并要求补齐。
- 入口检查：拒绝非官方入口产物；旁路文件移入 archive，行数不计。
- 审计记录：在 `.cccc/work/foreman/<timestamp>/` 留 QA 记录（批次路径、pipeline_guard、strict 结果、发布同步）。

Useful references
- PROJECT.md（战略概览；真相源 data/latest/latest.jsonl，严格校验）
- data/latest/latest.jsonl + manifest.json（真相源）
- data/release/（面向发布的文件）
