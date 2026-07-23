---
name: seo-image-gen
description: "面向 SEO 素材的 AI 图片生成：OG/社媒预览图、博客首图、schema 配图、产品图、信息图。基于 nanobanana-mcp 调用 Gemini 实现，需安装 banana 扩展。当用户说\"生成图片\"、\"OG 图\"、\"社媒预览图\"、\"首图\"、\"博客配图\"、\"产品图\"、\"信息图\"、\"SEO 配图\"、\"生成配图\"、\"生成图标\" 或 \"generate image\", \"OG image\", \"social preview\", \"hero image\", \"blog image\", \"product photo\", \"infographic\", \"seo image\", \"create visual\", \"image-gen\", \"favicon\", \"schema image\", \"pinterest pin\", \"generate visual\", \"banner\", \"thumbnail\" 时使用本技能。"
argument-hint: "[og|hero|product|infographic|custom|batch] <description>"
user-invocable: true
license: MIT
compatibility: "Requires nanobanana MCP server"
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# SEO 图片生成：面向 SEO 素材的 AI 图片生成（扩展）

通过 banana 创意总监（Creative Director）流水线调用 Gemini 的图片生成能力，
产出可直接投入使用的 SEO 场景图片。将各类 SEO 需求映射到对应的领域模式
（domain mode）、宽高比与默认分辨率。

## 架构说明

本扩展构建在 [Claude Banana](https://github.com/AgriciDaniel/banana-claude) 之上，
这是 Claude Code 的独立 AI 图片生成技能。

本技能包含两个职责不同的组件：
- **SKILL.md**（本文件）：处理交互式的 `/seo image-gen` 命令，负责生成图片
- **Agent**（`agents/seo-image-gen.md`）：在 `/seo audit` 期间被调用的纯审计分析员，
  用于评估现有的 OG/社媒图片并产出生成计划（本身从不自动生成图片）

## 前置条件

使用本技能前需先安装 banana 扩展：
```bash
./extensions/banana/install.sh
```

**可用性检查：** 在使用任何图片生成工具前，先确认 `gemini_generate_image` 或
`set_aspect_ratio` 等工具是否可用，以验证 MCP 服务器已正确连接。若工具不可用，
应告知用户扩展尚未安装，并提供安装说明。

## 快速参考

| 命令 | 作用 |
|---------|-------------|
| `/seo image-gen og <description>` | 生成 OG/社媒预览图（1200x630 观感） |
| `/seo image-gen hero <description>` | 博客首图（宽屏、氛围感强） |
| `/seo image-gen product <description>` | 产品图（简洁风格，白底） |
| `/seo image-gen infographic <description>` | 信息图（竖版，信息密度高） |
| `/seo image-gen custom <description>` | 使用完整创意总监流水线的自定义图片 |
| `/seo image-gen batch <description> [N]` | 生成 N 个变体（默认：3 个） |

## SEO 图片使用场景

每种使用场景都对应预设好的 banana 参数：

| 使用场景 | 宽高比 | 分辨率 | 领域模式（Domain Mode） | 备注 |
|----------|-------------|------------|-------------|-------|
| **OG/社媒预览图** | `16:9` | `1K` | Product 或 UI/Web | 简洁、专业、便于叠加文字 |
| **博客首图** | `16:9` | `2K` | Cinema 或 Editorial | 富有氛围感、编辑质感 |
| **Schema 配图** | `4:3` | `1K` | Product | 简洁、描述性强，用于 schema ImageObject |
| **社媒方图** | `1:1` | `1K` | UI/Web | 针对各平台优化的方形图 |
| **产品图** | `4:3` | `2K` | Product | 白底、影棚灯光 |
| **信息图** | `2:3` | `4K` | Infographic | 信息密度高，竖版排版 |
| **Favicon/图标** | `1:1` | `512` | Logo | 极简、可缩放、易识别 |
| **Pinterest Pin** | `2:3` | `2K` | Editorial | 竖版长图卡片 |

## 生成流程

针对每一次生成请求：

1. **识别使用场景**：从命令或上下文中判断（og、hero、product 等）
2. **应用 SEO 默认参数**：参考上方使用场景表格
3. **设置宽高比**：通过 `set_aspect_ratio` MCP 工具
4. **构建 Reasoning Brief（推理简报）**：使用 banana 创意总监流水线：
   - 加载 `references/prompt-engineering.md` 获取 6 要素体系
   - 根据领域模式分配权重侧重（Subject 30%、Style 25%、Context 15% 等）
   - 描述要具体、有画面感：写出摄像机实际"看到"的内容
5. **生成**：通过 `gemini_generate_image` MCP 工具
6. **生成后 SEO 检查清单**（见下文）

### 检查预设方案

如果用户提到某个品牌或已配置 SEO 预设：
```bash
python3 scripts/presets.py list
```
加载匹配的预设并作为默认值套用。另请检查 `references/seo-image-presets.md`
中面向 SEO 场景的预设模板。

## 生成后 SEO 检查清单

每次生成成功后，指导用户完成以下事项：

1. **Alt 文本**：为生成的图片撰写描述性强、含关键词的 alt 文本
2. **文件命名**：改为 SEO 友好的命名格式：`keyword-description-widthxheight.webp`
3. **WebP 转换**：转换为 WebP 以获得最佳页面速度：
   ```bash
   magick output.png -quality 85 output.webp
   ```
4. **文件体积**：首图建议控制在 200KB 以内，缩略图建议控制在 100KB 以内
5. **Schema 标记**：为生成的图片建议使用 `ImageObject` schema：
   ```json
   {
     "@type": "ImageObject",
     "url": "https://example.com/images/keyword-description.webp",
     "width": 1200,
     "height": 630,
     "caption": "Descriptive caption with target keyword"
   }
   ```
6. **OG meta 标签**：对于社媒预览图，提醒用户添加：
   ```html
   <meta property="og:image" content="https://example.com/images/og-image.webp" />
   <meta property="og:image:width" content="1200" />
   <meta property="og:image:height" content="630" />
   <meta property="og:image:alt" content="Descriptive alt text" />
   ```

## 成本提示

图片生成会产生费用，务必保持透明：
- 生成前展示预估成本（尤其是批量生成时）
- 记录每次生成：`python3 scripts/cost_tracker.py log --model MODEL --resolution RES --prompt "brief"`
- 如用户询问用量情况，运行 `cost_tracker.py summary`

大致成本（gemini-3.1-flash）：
- 512 分辨率：约 $0.02/张
- 1K 分辨率：约 $0.04/张
- 2K 分辨率：约 $0.08/张
- 4K 分辨率：约 $0.16/张

## 模型路由

| 场景 | 模型 | 原因 |
|----------|-------|-----|
| OG 图、社媒预览图 | `gemini-3.1-flash-image-preview` @ 1K | 速度快、成本低 |
| 首图、产品图 | `gemini-3.1-flash-image-preview` @ 2K | 质量与细节兼顾 |
| 带文字的信息图 | `gemini-3.1-flash-image-preview` @ 2K，thinking: high | 文字渲染效果更好 |
| 快速草稿 | `gemini-2.5-flash-image` @ 512 | 快速迭代 |

## 错误处理

| 错误 | 解决方案 |
|-------|-----------|
| MCP 未配置 | 运行 `./extensions/banana/install.sh` |
| API key 无效 | 在 https://aistudio.google.com/apikey 获取新 key |
| 触发限流（429） | 等待 60 秒后重试。免费额度约为 10 RPM / 500 RPD |
| `IMAGE_SAFETY` | 改写提示词——参见 `references/prompt-engineering.md` 的 Safety 章节 |
| MCP 不可用 | 回退方案：`python3 scripts/generate.py --prompt "..." --aspect-ratio "16:9"` |
| 扩展未安装 | 展示安装说明：`./extensions/banana/install.sh` |

## 跨技能协同

- **seo-images**（分析）与 **seo-image-gen**（生成）配合：`/seo images` 的审计结果会识别出缺失或质量不佳的图片；用这些结论驱动 `/seo image-gen` 命令
- **seo-audit** 会调用 seo-image-gen 的 **agent**（而非本技能）来分析全站的 OG/社媒图片并产出优先级排序的生成计划
- **seo-schema** 可以消费生成的图片：生成完成后，建议为新素材添加指向它的 `ImageObject` schema 标记

## 参考文档

按需加载，切勿在启动时全部加载：
- `references/prompt-engineering.md`：6 要素体系、领域模式、模板
- `references/gemini-models.md`：模型规格、速率限制、能力说明
- `references/mcp-tools.md`：MCP 工具参数与返回值
- `references/post-processing.md`：ImageMagick/FFmpeg 流水线配方
- `references/cost-tracking.md`：定价与用量追踪
- `references/presets.md`：品牌预设管理
- `references/seo-image-presets.md`：SEO 专用预设模板

## 响应格式

每次生成后，始终提供：
1. **图片路径**：保存位置
2. **构建的提示词**：展示实际发送给 API 的内容（便于学习）
3. **参数设置**：模型、宽高比、分辨率
4. **SEO 检查清单**：alt 文本建议、文件命名、WebP 转换
5. **Schema 片段**：如适用，提供 ImageObject 或 og:image 标记
