项目概览（influx）

  - 宗旨：构建一个“高活跃、非官号、非品牌、非低俗”的跨领域 BigV 作者索引，稳定服务下游（如 xoperator）的作者优先抓取与行业观察。
  - 原则：质量优先（活跃×相关×安全）> 数量；证据可追溯；格式通用；更新可持续；治理明确；对外友好。
  - 不做：几万规模的“百科全书式收集”；浏览器自动化抓网页；付费 X API；黑箱评分。

  范围与目标

  - 目标规模：5k–10k（强上限 15k）；每领域 800–1500 核心作者（AI/Tech、Creator/Platform、Ecosystem 等）。
  - 更新节奏：6–12 小时增量刷新；每日全量快照与发布；每周一次全量重算。
  - 下游场景：from: 作者优先抓取（xoperator）、研究/情报、生态分发、可视化。

  数据模型（Schema v1.0.0）

  - 主键
      - id: string（Twitter author_id，必填）
      - handle: string（@name 去 @，必填，唯一辅助键）
  - 基本属性
      - name: string
      - verified: string（none|blue|org|legacy）
      - followers_count: int
      - is_org: bool（品牌/媒体/机构）
      - is_official: bool（官方/团队/PR/Press/Support）
  - 语言/话题
      - lang_primary: string（en|ja|…，最近 30d 原帖多数表决）
      - lang_tags: [string]
      - topic_tags: [string]（如 ai_core/gpu/creator_platform/ecosystem）
  - 活跃与质量（滚动 30d）
      - metrics_30d.posts_total: int
      - metrics_30d.posts_original: int
      - metrics_30d.median_likes|median_replies|median_retweets: int
      - metrics_30d.p90_likes|p90_replies|p90_retweets: int
      - metrics_30d.media_rate: float（0–1）
      - metrics_30d.urls_topk: [string]
  - 评分与排序
      - score: float（0–100，activity 30% + quality 50% + relevance 20%）
      - rank_global: int
      - rank_by_topic: object（{topic: int}）
  - 溯源与合规
      - last_active_at: string（ISO 8601）
      - last_refresh_at: string（ISO 8601）
      - risk_flags: [string]（nsfw/political/controversy…）
      - banned: bool；ban_reason: string
      - sources: [ { method, fetched_at, window, evidence: [{tweet_id, type, created_at}] } ]
      - provenance_hash: string（sha256(id+followers+last_active_at+metrics_30d)）
  - 扩展
      - ext: object（预留，不破坏兼容）

  目录结构与产物

  - 根目录
      - README.md（用途、使用方法、许可、免责声明）
      - LICENSE（建议 CC BY 4.0）
      - schema/bigv.schema.json、schema.md（字段解释+示例）
      - lists/seeds/*.csv（种子 handle 列表：handle,name,note,source_url）
      - lists/rules/brand_heuristics.yml、risk_terms.yml（品牌/风险规则）
      - tools/（采集/扩展/打分/导出/校验脚本；详见下方工具设计）
      - ci/validate.yml（PR 校验 schema）、ci/snapshot.yml（定时构建与发布）
  - 数据目录（Git 存少量; 大数据放 Releases）
      - data/latest/
          - latest.jsonl.gz（按 score desc 排；权威发布）
          - manifest.json（schema_version、timestamp、count、sha256、生成参数）
      - data/snapshots/YYYY-MM-DD/
          - bigv-YYYYMMDD.jsonl.gz（全量快照）
          - shards/（可选，>10k 分片：topic/lang/hash 前缀）
          - manifest.json（快照元数据）
  - 排序与分片
      - 排序：score desc → followers_count desc → handle lex
      - 分片：topic/lang 复合 → author_id 哈希前缀（稳定切片）

  采集流水线（全 RUBE MCP 工具）

  - 雷达（热词）：TWITTER_RECENT_SEARCH_COUNTS
      - 对 80–120 词跑 12h 计数（granularity=hour）；评分 = 0.6level + 0.3slope + 0.1*accel（min-max 归一）
      - 输出 top40（radar.json），仅作“作者发现”的线索
  - 关键词抓取（小规模、高质量）：
      - 8 组 query（radar 分组），每组 2 页（必要时 3）；tweet_fields/expansions/user_fields 带齐（public_metrics、includes.users.public_metrics.followers_count）
  - 作者扩展：
      - 从原帖提取 author_id 与 entities.mentions[].username；对缺字段的一次性 USER_LOOKUP 批量补齐
  - 入池与过滤：
      - 入池阈值：verified 且 followers≥30k，或 followers≥50k
      - 去品牌/官号：rules/brand_heuristics.yml（Official/News/PR/Press/Team/Support/Corp/Media/Store/Shop 等关键词 + 域名特征）→ is_org/is_official
      - 风险：risk_terms.yml 命中 → risk_flags（默认不入池）
  - 打分与淘汰（score_update）：
      - activity：30d posts_original + 7d 权重 + 媒体比例
      - quality：中位 + p90（对数缩放）
      - relevance：与话题/语言匹配 + 热词共现
      - 上限与淘汰：每域 1500/全库 10k 上限，按 score + 最近活跃时间排序，末尾淘汰；banned 永久保留
  - 导出与发布：
      - validate（按 schema 校验）→ export_latest（latest.jsonl.gz + manifest）→ 每日发布 Release（tag=YYYYMMDD）

  工具设计（CLI 约定）

  - 雷达
      - influx-radar plan --window-hours 12 --granularity hour（生成 COUNT_ARGS-*.json、RADAR_MAP.json）
      - influx-radar analyze --top-k 40 [--apply-config]（输出 state/keywords/radar.json；可更新 keyword_buckets）
  - 采集
      - influx-harvest search --plan path/to/queries/*.json --pages 2（执行 8 组 query）
      - influx-expand mentions --input rube-slice-*.json --out authors.json（抽 author/mentions；批量 USER_LOOKUP）
  - 评分与导出
      - influx-score update --authors authors.json --window-days 30 --out scored.jsonl
      - influx-export latest --input scored.jsonl --out data/latest/latest.jsonl.gz
      - influx-validate --input data/latest/latest.jsonl.gz --schema schema/bigv.schema.json
  更新与快照策略

  - 增量刷新：每 6–12 小时，增量更新活跃/近 30d 指标与 score
  - 快照：每日全量快照到 snapshots/YYYY-MM-DD 并发布 Release；latest 指向最近版本
  - 重算：每周一次全量重算（避免指标漂移累计）

  治理与合规

  - 许可证：建议 CC BY 4.0（保留署名；便于传播与二次开发）
  - PR 规范：新增作者需附 2 条近 30d 原帖链接（evidence）；CI 跑 lint/validate，通过才合并
  - banned：支持人工标注 banned 与 ban_reason；validate 时排除
  - 免责声明：仅汇总公开信息，不存私密信息；遵循 X 平台 ToS；作者要求退出时在下一周期移除

  与 xoperator 的集成

  - 消费方式：xoperator 的 plan8 优先从 influx 的 data/latest/latest.jsonl.gz 读取作者，生成 from: 查询（BigV-first）；关键词组仅作兜底
  - 运营闸：不改变你的硬闸（粉丝≥50k、评论 5–100、likes≥5、views≥20k(存在时)、原帖、语言/年龄），floor=2 保障不断拍

  版本与演进（不返工）

  - Schema 演进：schema_semver 写入 manifest；新增字段 → minor；破坏性改动 → major；旧字段弃用≥90天
  - 预留 ext：所有定制字段挂在 ext，不破坏主 schema
  - 大规模时的分片：topic/lang+哈希前缀稳定切片（兼顾分析与 diff），manifest 记录切片hash
  - 格式：权威产物 JSONL.gz；Parquet 作为分析件（发布到 Releases）

  里程碑与进度（保守估计）

  - M0（第 1 周）：仓库骨架+schema+CI；首批 400–600 作者（AI/Tech、Creator/Platform、Ecosystem）；latest 发布
  - M1（第 2–3 周）：扩到 2k–3k；完善 heuristics 与风险标注
  - M2（第 4–6 周）：达到 5k–8k；Shards 与可视化（独立站）预研
  - 长期（季度）：维持 5k–10k，churn<20%/周；每月治理回顾

  指标与监控（质量/规模/健康）

  - 规模：record_count、每域覆盖、lang 分布
  - 质量：median/p90 likes/replies/retweets（30d）；score 的分布；banned 命中率
  - 健康：每轮增量±、新入/淘汰量、活跃新星“rising”计数（followers 20–50k 且 7d 斜率明显）

  风险与缓解

  - 配额/限流：严格分页上限；指数退避；重试策略；按 topic/lang 分批执行
  - 噪音污染：去品牌/官号 heuristic 与风险词表；人工抽查 topN；PR 门槛
  - 数据漂移：每周重算；manifest 固定参数；score 版本标注

  启动清单（立刻落地）

  - 建仓：influx（MIT/CC BY 4.0）；提交 docs/PLAN.md、schema、tools 骨架、CI
  - 导入种子：lists/seeds/*.csv（至少 400–600 作者）
  - 跑一轮：influx-radar plan → MCP 执行 → influx-radar analyze → influx-harvest search → influx-expand mentions → influx-score update → influx-export latest → 发布 Release
  - xoperator 侧：把 BigV-first 输入指向 influx 的 latest.jsonl.gz，保持现有运营闸与 floor=2

  命名与品牌

  - influx 名义：寓意“涌入/流量/活跃度”，与“活跃高质量作者流”的核心恰当；建议副标：influx – high‑signal creator index


  - 首批 400–600 作者我不会靠“人工大规模搜集”，而是用三路合成，全部可自动、可审计、成本低：
      1. 最近 24–48 小时的“关键词广搜→作者扩展”（60–70%）：用 RUBE 的 Recent Search 拉推文，再从 includes.users + entities.mentions 扩展作者，按 verified/followers 过滤入池；
      2. “组织/项目种子一次性导入”（20–30%）：公开团队/项目页面的个人作者（OpenAI/DeepMind/Anthropic/HF/PyTorch/vLLM/llama.cpp 等）+ 顶会演讲/OSS 维护者（CSV 导入）；统一用 USER_LOOKUP 校验；
      3. “精选公共 X Lists 的个人作者”（10%）：只吸收“个人创作者”成员（排官方/媒体/品牌），再用 USER_LOOKUP 校验；无法用 list API 就把列表导出为 CSV 种子。
  - 这三路合成后，统一去品牌/风险标注、30 天活动与质量打分、末尾淘汰；1 周拓展到 800–1500；不追“几万条”的库，ROI 很低。

  详细说明（可作为 influx 的启动答复附注）

  1. 路线与占比

  - 自动发现（60–70%）
      - 工具/方式：RUBE MCP 的 TWITTER_RECENT_SEARCH（8 组热词，12h 窗，每组 2–3 页），带 expansions/user_fields 拿到 includes.users.public_metrics.followers_count。
      - 从推文提取作者与 @mentions，批量 USER_LOOKUP 补齐（仅缺失时调），过滤入池：
          - 入池：verified 且 followers≥30k，或 followers≥50k；原帖为主；语言 en/ja 优先。
      - 好处：完全自动、成本低、时效强，“作者端热度”结合“话题端热度”，首拍即可产出 2–4 百个候选。
  - 组织/项目种子（20–30%）
      - 来源：公开团队/项目页（个人作者）与顶会演讲/OSS 维护者集合（仅个人，不含官方/品牌号）：
          - 研究/工程：OpenAI、DeepMind、Anthropic、Meta FAIR、Google/DeepMind/Brain、NVIDIA DevRel/架构师（个人）、Hugging Face 团队、PyTorch 维护者、vLLM、llama.cpp 等；
          - 创作者/平台观察：大型创作者教育/复盘账号（个人）、产品/生态个人观察者。
      - 实操：把这些页面上的 handle 收集成 seeds/*.csv（handle,name,note,source_url），脚本导入后 USER_LOOKUP 校验、去品牌/风险标注。
      - 好处：质量高、稳定，能快速填补作者池的“结构性空白”。
  - 精选公共 X Lists（10%）
      - 来源：信誉较高的“个人作者”主题 List（AI/ML、GPU/半导体、创作者生态、产品/平台），仅导入“个人”成员；媒体/品牌/PR/Team/Official 排除。
      - 实操：无法用 list API 就人工导出为 CSV 种子；导入后 USER_LOOKUP 校验。
      - 好处：快速拓面；入库前仍走去品牌/风控与打分。

  2. 质量闸与去品牌（一次性定好规则）

  - 入池阈值（其一）：
      - verified 且 followers≥30k；或 followers≥50k；
      - 最近 30 天原帖≥5 且语言 ∈ {en, ja}；
  - 去品牌/官方（启发式 + 风险词）：
      - 名称/用户名/简介含 Official/News/Press/PR/Team/Support/Corp/Media/Store/Shop 等 → is_org/is_official；
      - 简介与外链域名命中广告/品牌高频词 → is_org；
      - risk_terms（nsfw/political/controversy 等）命中 → risk_flags；
      - is_org/is_official/risk_flags 命中默认不入库（或标注但不参与抓取）；
  - 打分与排序（30 天窗口）：
      - activity（30%）：原帖计数 + 7 天活跃权重 + 媒体比例；
      - quality（50%）：median/p90 likes/replies/retweets 的对数缩放组合；
      - relevance（20%）：topic/lang 匹配 + 与热词的共现；
      - 每域上限（例如 1500），末尾淘汰，banned 永久保留但不参与排序。

  3. 为什么不靠“几万作者的大名单”

  - 幂律决定“高频产出作者很少”。抓几万会占用配额、极大噪音、稀释信噪比与审计成本，工程价值低。
  - 实战里，800–1500/域 + 动态维护足够覆盖 80% 的高价值讨论；全库 5k–10k 已经能服务绝大多数下游需求。
  - 我们要的是“稳定拿到可用候选”，不是“百科全书”。

  4. 具体落地（首拍）

  - 第 0 周（3–5 天）：
      - 跑 2–3 轮“自动发现”：8 组热词 × 12h × 每组 2–3 页 + mentions 扩展；
      - 导入 seeds/*.csv：从可信团队/项目页（个人作者）与顶会/OSS 维护者集合导入 100–200；
      - 精选 5–8 个高质量 X Lists（仅个人）导出 CSV（50–100）。
      - 合并、去品牌/风险、打分，首版 latest.jsonl.gz 目标 400–600。
  - 第 1 周：滚动增量，每 6–12h 运行一次；扩到 800–1500，发布第一周稳定版 release。
  - 后续：维持每日 release、每周全量重算；控制 churn（新增/淘汰）与覆盖率。

  5. 为什么这套方法“最高效稳定”

  - 全程 RUBE MCP（recent search / counts / user lookup），不需要付费 X API、不做浏览器自动化；字段齐全、可审计、容错好。
  - 请求量低（每拍 ~100–130 次），可持续；自动发现为主、一次性 seeds 加速；不依赖海量人力。
  - 质量通过多闸与分数排序控制；规模通过上限与淘汰控制；治理（banned/风险）可复制。