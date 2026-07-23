---
name: seo-plan
description: >
  面向新建或既有网站的战略性 SEO 规划。涵盖行业专属模板、竞品分析、
  内容策略与实施路线图。当用户说"SEO 规划"、"SEO 策略"、"内容策略"、
  "关键词策略"、"内容日历"、"站点架构"、"SEO 路线图" 或
  "SEO plan", "SEO strategy", "SEO planning", "content strategy",
  "keyword strategy", "content calendar", "site architecture", "SEO roadmap"
  时使用本技能。
user-invocable: true
argument-hint: "[business-type]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# 战略性 SEO 规划

## 流程

### 1. 需求摸底
- 业务类型、目标受众、竞争对手、目标诉求
- 现有站点评估（如已上线）
- 预算与时间线约束
- 关键绩效指标（KPI）

### 2. 竞品分析
- 确定前 5 名竞争对手
- 分析其内容策略、schema 使用情况、技术架构
- 找出关键词差距和内容机会点
- 评估其 E-E-A-T 信号
- 估算其域名权重（Domain Authority）

### 3. 架构设计
- 从 `assets/` 目录加载行业模板
- 设计 URL 层级结构与内容支柱
- 规划内部链接策略
- 应用质量门槛后的站点地图结构
- 面向用户旅程的信息架构

### 4. 内容策略
- 相对竞争对手的内容差距
- 页面类型及预估数量
- 博客/资源主题与发布节奏
- E-E-A-T 建设方案（作者简介、资质、经验信号）
- 带优先级排序的内容日历

### 5. 技术基础
- 托管与性能需求
- 各页面类型的 schema 标记方案
- Core Web Vitals 基线目标
- AI 搜索适配需求
- 移动优先考量

### 6. 实施路线图（4 个阶段）

#### 第 1 阶段：基础建设（第 1-4 周）
- 技术搭建与基础设施
- 核心页面（首页、关于我们、联系方式、主要服务页）
- 关键 schema 实施
- 分析与追踪工具搭建

#### 第 2 阶段：扩张期（第 5-12 周）
- 主要页面的内容创作
- 博客上线及初始文章发布
- 内部链接结构搭建
- 本地 SEO 配置（如适用）

#### 第 3 阶段：规模化（第 13-24 周）
- 进阶内容开发
- 链接建设与外联
- GEO 优化
- 性能优化

#### 第 4 阶段：权威建设（第 7-12 个月）
- 思想领导力内容
- PR 与媒体曝光
- 进阶 schema 实施
- 持续优化

## 行业模板

从 `assets/` 目录加载：
- `saas.md`：SaaS/软件公司
- `local-service.md`：本地服务型企业
- `ecommerce.md`：电商网站
- `publisher.md`：内容发布者/媒体
- `agency.md`：代理机构与咨询公司
- `generic.md`：通用商业模板

## 输出

### 交付物
- `SEO-STRATEGY.md`：完整战略方案
- `COMPETITOR-ANALYSIS.md`：竞品洞察
- `CONTENT-CALENDAR.md`：内容路线图
- `IMPLEMENTATION-ROADMAP.md`：分阶段行动计划
- `SITE-STRUCTURE.md`：URL 层级与架构

### KPI 目标
| 指标 | 基线 | 3 个月 | 6 个月 | 12 个月 |
|--------|----------|---------|---------|----------|
| 自然流量 | ... | ... | ... | ... |
| 关键词排名 | ... | ... | ... | ... |
| 域名权重 | ... | ... | ... | ... |
| 已索引页面数 | ... | ... | ... | ... |
| Core Web Vitals | ... | ... | ... | ... |

### 成功标准
- 每个阶段都有明确、可衡量的目标
- 资源需求已明确
- 依赖关系已识别
- 风险应对策略已制定

## DataForSEO 集成（可选）

如果 DataForSEO MCP 工具可用，可使用 `dataforseo_labs_google_competitors_domain`
与 `dataforseo_labs_google_domain_intersection` 获取真实的竞品情报，使用
`dataforseo_labs_bulk_traffic_estimation` 估算流量，使用
`kw_data_google_ads_search_volume` 与 `dataforseo_labs_bulk_keyword_difficulty`
进行关键词研究，使用 `business_data_business_listings_search` 获取本地商家数据。

## 错误处理

| 场景 | 处理动作 |
|----------|--------|
| 未识别的业务类型 | 回退使用 `generic.md` 模板，告知用户未找到对应的行业专属模板，改用通用商业模板继续 |
| 未提供网站 URL | 切换为新站规划模式，跳过需要真实 URL 的现有站点评估和竞品差距分析 |
| 未找到行业模板 | 检查 `assets/` 目录中可用的模板；若请求的模板文件缺失，改用 `generic.md` 并在输出中注明缺失情况 |
