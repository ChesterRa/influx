# influx - X/Twitter 影响力作者索引

## 核心目标
构建"高活跃、非官号、非品牌"的跨领域 BigV 作者索引（目标 5k-10k），服务 xoperator 等下游系统的作者优先抓取与行业观察。

**原则**: 质量 > 数量 | 证据可追溯 | 更新可持续 | 对外友好

---

## 项目立意与价值

### 为什么需要 influx？

**问题**: X/Twitter 是技术社区的主要讨论场所，但海量内容中高质量信号分散、难以追踪。xoperator 等下游系统需要稳定的"高活跃、非官号、非品牌"作者列表来优先抓取内容，避免淹没在噪音中。

**现状困境**:
- **官方 API 限制**: Twitter API v2 免费层无法支撑大规模作者发现（following-graph、list members 等端点受限或需付费）
- **手工维护成本高**: 人工策展无法持续更新、难以保证质量一致性
- **现有工具盲区**: 社区缺乏"非品牌、非官号"的技术领域作者索引，现有榜单多为粉丝数排名，缺乏质量过滤

**influx 解决方案**:
- **专注质量**: 严格入池阈值 + brand/risk 过滤 → 确保"个人影响力作者"而非机构/品牌号
- **跨领域覆盖**: AI/Tech、Security、DevOps、Creator、Business 等多领域，避免单一赛道饱和
- **持续更新**: 工具链支持增量更新、schema 演进、质量门禁
- **开放友好**: JSONL 格式、清晰 schema、CC BY 4.0 许可、溯源证据完整

### 潜在价值

#### 1. 下游系统优化 (xoperator, 情报工具)
- **作者优先抓取**: 按 score 排序，优先抓取高质量作者推文 → 提升内容 signal/noise 比
- **冷启动加速**: 新系统无需从零构建作者列表，直接消费 influx → 节省 2-4 周初始策展时间
- **领域深耕**: topic_tags 支持领域过滤 (ai_core, gpu, security) → 垂直场景精准投喂

#### 2. 研究与观察
- **行业趋势分析**: 追踪领域 KOL 动态 → 识别热点话题、技术趋势、社区共识
- **社交网络研究**: 提供高质量节点样本 → 支持 X 生态研究、影响力传播分析
- **榜单基准**: 提供"技术影响力"榜单 vs 纯粉丝数排名 → 更能反映实际话语权

#### 3. 生态价值
- **工具层**: 可作为 RSS 阅读器、推文归档工具、AI 训练数据源的"作者白名单"
- **平台层**: 技术社区平台 (论坛、newsletter) 可导入作者列表 → 快速引入高质量创作者
- **可视化层**: 支持 influencer network 可视化、领域 map 构建

#### 4. 长期可持续性
- **规模上限**: 5k-10k (不追求"百科全书"式几万条) → 保持质量门槛、避免噪音膨胀
- **更新节奏**: 6-12h 增量刷新 → 保持时效性，但不过度消耗 API quota
- **治理透明**: 公开 brand/risk 过滤规则、接受社区 PR、提供 banned 机制 → 可审计、可信任

---

## 开发与治理原则

### 质量优先原则
- **Filter-First**: 所有数据必经管道过滤 (entry threshold + brand/risk rules)，绝不"先入库再清洗"
- **Validate-Always**: 每次导出强制 schema 校验 (influx-validate)，CI 自动拦截不合规数据
- **Manual QA**: 每批次 N=30-50 人工抽检，Brand/Risk FP rate ≤3.3% 为验收标准

### 证据可追溯原则
- **Provenance Hash**: 每条记录含 sha256(id+followers+last_active_at+metrics) → 检测篡改
- **Sources Array**: 记录 method (manual_seed, github_seed, following) + fetched_at + evidence → 可回溯数据来源
- **Manifest Lock**: data/latest/manifest.json 包含 count, SHA-256, timestamp → 版本完整性验证

### 增量演进原则
- **Schema 演进**: 遵循 semver (新增字段 minor, 破坏性改动 major)，旧字段弃用≥90天
- **工具独立**: 采集/评分/导出/校验分离 → 单一工具故障不影响全流程
- **预留扩展**: ext 字段支持定制需求，不破坏主 schema

### 开放友好原则
- **格式通用**: JSONL (streaming processing) + 可选 Parquet (分析件)
- **许可宽松**: CC BY 4.0 (保留署名, 允许二次开发)
- **API 无依赖**: 不强制付费 X API，基于 RUBE MCP 免费层 + 手工策展组合

### 治理透明原则
- **规则公开**: lists/rules/brand_heuristics.yml + risk_terms.yml 明文可审计
- **Banned 机制**: 支持 banned=true + ban_reason → 尊重作者退出请求
- **PR 门槛**: 新增作者需附 evidence (2 条近 30d 原帖链接) → 防止批量低质量投放
- **版本控制**: Git 存小数据 (seeds, rules, tools)，大数据放 GitHub Releases → 历史可溯源

### 可持续更新原则
- **Manual + Automation 混合**: M1 manual CSV 证明可行，M2+ 探索有限自动化（X Lists, 付费 API）
- **质量闸常驻**: 即使自动化，仍保留 QA sample + 人工复审 → 避免自动化漂移
- **Velocity 监控**: 每批次记录 velocity (records/hour), 异常时触发人工介入
- **Churn 控制**: 新增/淘汰量每周<20% → 保持索引稳定性

### 经验驱动改进原则 (2025-11-14 教训)
- **"手工策展" ≠ "质量保证"**: 所有数据必经管道，包括手工种子 (教训 #000139)
- **TODO Placeholder 是技术债**: P0 TODO 必须在里程碑内关闭，不可无限延期
- **业务规则 vs Schema 校验**: influx-validate --strict 必须包含业务规则验证
- **全量审查 vs QA Sample**: 系统性问题需全量检查，QA sample 仅用于边界案例复审

---

## 当前状态 (2025-11-14)

### 数据集
- **规模**: 292 authors (M1 Week 1, 73% toward 400 pause gate)
- **批次**: m01-m03 (GitHub seeds) + m04-m14 (AI/Tech/Security/DevOps/OSS)
- **Schema**: v1.0.0 (bigv.schema.json)
- **产物**: data/latest/latest.jsonl + manifest.json

### 工具链
- ✅ `influx-harvest`: 作者发现 (GitHub seeds, following, x-lists)
- ✅ `influx-score`: 代理评分 (M1: log10(followers) + verified_boost)
- ✅ `influx-export`: JSONL.gz 导出 + manifest
- ✅ `influx-validate`: Schema 校验
- ✅ `influx-view`: 数据预览
- ✅ `influx-rube-bridge`: RUBE MCP 集成

### 执行状态
- **方法**: Manual CSV + Lists (GitHub 自动化因 RUBE MCP 限制不可行)
- **目标**: Week 1 达 400 authors → 用户决策 (继续 M1 或暂停测试)
- **下一步**: m12/m13/m11 batches (Security/DevOps/OSS domains) → 预期 +34 new

---

## 关键问题与教训 (2025-11-14 审查)

### ⚠️ 质量问题发现 (User #000139)

**问题描述**: 当前 292 条记录存在大量不合标准数据（官号、指标不达标）

**审查结果** (2025-11-14 00:25):
1. **19 authors (6.5%) 低于入池阈值**
   - 规则: `(verified=true AND followers>=30k) OR followers>=50k`
   - 实际: 19 人有 verified=blue 但 <30k followers
   - 案例: @mrm8488 (20.5k), @clefourrier (5.6k)

2. **292/292 (100%) 缺失过滤字段**
   - Schema 要求 `is_org` (品牌/机构) 和 `is_official` (官方/团队)
   - 实际: ALL records 缺失这两个字段
   - 影响: 无法过滤品牌/官号

3. **潜在品牌/团队账号**
   - 案例: @aantonop "Andreas (aantonop Team)" - 名称含 "Team" 关键词
   - 状态: 未经 brand_heuristics.yml 过滤

### 🔍 根因分析

**根因 1: M0/M1 手工策展绕过管道过滤**
- M0.1-M1 采用纯手工 CSV 策展 (sources: manual_curation, manual_seed)
- 未经 influx-harvest 管道处理 → 跳过入池阈值检查、品牌/风险过滤
- 导致低于阈值账号和缺失过滤字段进入数据集

**根因 2: 过滤逻辑从未实现**
- tools/influx-harvest L53, L80 有 TODO placeholder ("Apply brand/risk filters")
- lists/rules/brand_heuristics.yml + risk_terms.yml 已创建但从未执行
- POR.md R6 风险 "Pipeline filter enforcement gap" 已记录但未修复

**根因 3: Schema 校验不完整**
- influx-validate 仅检查 JSON Schema 结构合规 (id, handle, name, verified, followers_count, meta)
- 未校验 is_org/is_official 字段存在性 (schema 定义了但标为 optional)
- 未校验入池阈值逻辑

### 📋 修复计划 (P0 - 阻塞 M1 继续)

**Phase 1: 数据集清洗** (立即执行)
1. 对 292 条记录补充 is_org/is_official 字段:
   - 运行 brand_heuristics.yml 规则 (关键词匹配: Official/News/Press/Team/Support/Corp/Media)
   - 手动复审边界案例 (如 aantonop "Team")
2. 移除 19 条低于入池阈值记录
3. 重新导出 data/latest/ (预期: ~270 authors)

**Phase 2: 管道修复** (Week 1 剩余时间)
1. 实现 tools/influx-harvest 过滤逻辑:
   - 入池阈值检查函数 (verified+30k OR 50k)
   - brand_heuristics.yml 加载与匹配
   - risk_terms.yml 加载与匹配
   - 输出 is_org/is_official/risk_flags 字段
2. 增强 influx-validate:
   - 添加 is_org/is_official 必填检查
   - 添加入池阈值验证 (--strict mode)
3. 文档化过滤规则异常列表 (lists/rules/exceptions.yml)

**Phase 3: 回归测试** (Week 1 结束前)
1. 对清洗后数据集 (N=270) 生成 QA sample (N=50)
2. 手工审查 FP rate (target: ≤3.3% = 1-2 FPs)
3. 更新 POR.md Quality Gates 状态

**验收标准**:
- ✅ 100% records 有 is_org/is_official 字段
- ✅ 100% records 满足入池阈值
- ✅ Brand/Risk FP rate ≤3.3% (N=50 QA sample)
- ✅ influx-validate --strict 通过

---

## M1 执行摘要

### 战略转向
- **原计划**: GitHub org seeds + following-graph 自动化 → 2k-3k authors (2-3 weeks)
- **实际路径**: Manual CSV + Lists PRIMARY (GitHub 自动化不可行于 RUBE MCP free tier)
- **新目标**: 1.5k-2k authors (4-5 weeks), 质量优先

### 关键发现
1. **AI/Tech 网络饱和**: m04/m05/m08 三批次 100% 重叠 (0 new authors)
   - GitHub seed pool (OpenAI/Anthropic/HF/PyTorch) 已覆盖 AI/ML 核心网络
   - Pivot: Security/DevOps/Creator 领域预期 20-40% 新增率

2. **Schema 验证误报**: Aux 93268d 声称 `meta` optional (MAJOR issue)
   - 验证: meta IS required (schema:242), 292/292 合规
   - 教训: validation results > Aux claims

3. **过滤管道缺失**: R6 风险已实现 - 手工策展绕过质量闸
   - **修复中**: Phase 1-3 修复计划 (上文)

### 里程碑
- ✅ M0.1: 151 authors (manual CSV, 100% schema pass)
- 🔄 M1 Week 1: 292 → 400 (需清洗至 ~270 后继续)
- 🎯 M1 Complete: 1.5k-2k authors (4-5 weeks)

---

## Schema 设计 (v1.0.0)

### 核心字段
```json
{
  "id": "Twitter author_id (string)",
  "handle": "@username without @",
  "name": "Display name",
  "verified": "none|blue|org|legacy",
  "followers_count": "int",
  "is_org": "bool (品牌/媒体/机构)",
  "is_official": "bool (官方/团队/PR)",
  "lang_primary": "en|ja|...",
  "topic_tags": ["ai_core", "gpu", ...],
  "meta": {
    "score": "0-100 (M1: proxy; M2: activity+quality+relevance)",
    "last_refresh_at": "ISO 8601",
    "sources": [{"method": "manual_seed|github_seed|following", "fetched_at": "...", "evidence": "..."}],
    "provenance_hash": "sha256(...)"
  }
}
```

### 入池规则
- **阈值**: `(verified=true AND followers>=30k) OR followers>=50k`
- **过滤**: brand_heuristics.yml (is_org=true → exclude)
- **风险**: risk_terms.yml (nsfw/political/hate → exclude)

### 评分公式
- **M1 (proxy)**: `score = 20*log10(followers/1000) + verified_boost`
- **M2+ (full)**: `activity(30%) + quality(50%) + relevance(20%)` with 30d metrics

---

## 工具使用

### 数据采集
```bash
# 手工 CSV 种子 + RUBE MCP 预获取
tools/influx-rube-bridge --handles-file lists/seeds/m12-batch.csv
# → 生成 RUBE MCP 调用指令, 手工执行, 保存 users_fetched_m12.jsonl

# Harvest + 过滤 (Phase 2 后)
tools/influx-harvest x-lists \
  --list-urls lists/seeds/m12-batch.csv \
  --prefetched-users users_fetched_m12.jsonl \
  --brand-rules lists/rules/brand_heuristics.yml \
  --risk-rules lists/rules/risk_terms.yml \
  --out harvest.raw.jsonl

# 评分 + 导出
python3 tools/influx-score update --input harvest.raw.jsonl --out scored.jsonl
python3 tools/influx-export latest --input scored.jsonl --out data/latest/

# 校验
python3 tools/influx-validate -s schema/bigv.schema.json data/latest/latest.jsonl
```

### 数据清洗 (Phase 1)
```bash
# 生成待清洗报告
python3 tools/influx-audit --input data/latest/latest.jsonl \
  --check-threshold --check-filters --out audit_report.json

# 应用过滤规则 (补充 is_org/is_official)
python3 tools/influx-clean --input data/latest/latest.jsonl \
  --brand-rules lists/rules/brand_heuristics.yml \
  --risk-rules lists/rules/risk_terms.yml \
  --remove-below-threshold \
  --out data/latest/cleaned.jsonl

# 导出 + 校验
python3 tools/influx-export latest --input cleaned.jsonl --out data/latest/
python3 tools/influx-validate --strict -s schema/bigv.schema.json data/latest/latest.jsonl
```

---

## 快速恢复清单

下次恢复开发时按此清单执行:

### 1. 检查当前状态
```bash
cat data/latest/manifest.json  # 确认 count, SHA-256
python3 tools/influx-validate -s schema/bigv.schema.json data/latest/latest.jsonl
```

### 2. 检查阻塞
- 读取 `.cccc/mailbox/peerA/inbox/` (oldest-first)
- 查看 background Aux task 输出
- 确认 CI status (`.github/workflows/`)

### 3. 确认下一步
- **Phase 1 清洗未完成**: 优先执行数据清洗 (上文 Phase 1)
- **Phase 1 已完成**: 继续 m12/m13/m11 batches (non-AI domains)
- **已达 350+**: 准备 v0.1.0-alpha release + QA report

### 4. 标准管道
```bash
# Prefetch → Harvest → Score → Merge → Export → Validate
# (详见 "工具使用" 章节)
```

### 5. 记录进度
- 更新 manifest.json count
- 记录 velocity.log (新增/更新/pass rate)
- 生成 qa_sample.csv (N=30 per batch)

### 6. 决策点
- If author_count < 350 after m12/m13/m11 → 追加批次或手工策展
- If ≥350 → 准备 release + QA report
- If FP rate >5% → 微调 heuristics before 继续

---

## 风险与缓解

| ID | 风险 | 状态 | 缓解措施 |
|----|-----|------|---------|
| R1 | AI/Tech 批次持续 0% 新增 | ✅ Mitigated | Pivot to m12/m13/m11 (non-AI domains) |
| R2 | RUBE MCP API quota 耗尽 | Monitoring | Prefetch + cache strategy |
| R3 | Brand heuristics false positives | **ACTIVE** | Phase 1-3 修复计划 (清洗+管道实现) |
| R4 | 48h 内无法达到 400 | Contingency | 降低 threshold 或手工策展 |
| R5 | Following-graph API 不可用 | Accepted | Defer to M2 |
| **R6** | **Pipeline filter enforcement gap** | **CRITICAL** | **Phase 2 实现 influx-harvest 过滤逻辑** |

---

## 参考文档

- **Schema**: `schema/bigv.schema.json` + `schema/schema.md`
- **Pipeline Contract**: `docs/por/d2-pipeline-contract.md`
- **POR (Plan of Record)**: `docs/por/POR.md`
- **过滤规则**: `lists/rules/brand_heuristics.yml`, `lists/rules/risk_terms.yml`
- **CI**: `.github/workflows/validate.yml`

---

**文档版本**: 2025-11-14T00:30:00Z
**更新触发**: User #000139 质量问题反馈 + 清理冗余内容请求
**下次更新**: Phase 1 清洗完成或达到 350 authors
