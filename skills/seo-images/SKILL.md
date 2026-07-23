---
name: seo-images
description: >
  图片优化分析技能，覆盖 SEO 与性能表现：检查 alt text、文件大小、格式、响应式图片、
  懒加载、CLS 预防、图片 SERP 排名（通过 DataForSEO），以及图片文件优化
  （WebP/AVIF 格式转换、IPTC/XMP 元数据注入）。当用户说"图片优化"、"image optimization"、
  "alt text"、"图片 SEO"、"image SEO"、"图片大小"、"image size"、"图片审计"、
  "image audit"、"优化图片"、"optimize images"、"图片元数据"、"image metadata"、
  "图片 SERP"、"image SERP"、"转换为 webp"、"convert to webp"、"图片文件优化"、
  "image file optimize" 时使用本技能。
user-invocable: true
argument-hint: "[url]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# 图片优化分析

## 检查项

### Alt Text（替代文本）
- 所有 `<img>` 元素都应有 alt 属性（装饰性图片除外：`role="presentation"`）
- 描述性强：描述图片内容本身，而非 "image.jpg" 或 "photo" 这类占位词
- 在自然的语境下包含相关关键词，而不是堆砌关键词
- 长度：10-125 个字符

**好的示例：**
- "Professional plumber repairing kitchen sink faucet"
- "Red 2024 Toyota Camry sedan front view"
- "Team meeting in modern office conference room"

**差的示例：**
- "image.jpg"（文件名，不是描述）
- "plumber plumbing plumber services"（关键词堆砌）
- "Click here"（缺乏描述性）

### 文件大小

**按图片类别分级的阈值：**

| 图片类别 | 目标值 | 警告值 | 严重值 |
|----------------|--------|---------|----------|
| 缩略图 | < 50KB | > 100KB | > 200KB |
| 内容图片 | < 100KB | > 200KB | > 500KB |
| Hero/横幅图片 | < 200KB | > 300KB | > 700KB |

在不损失画质的前提下，建议将图片压缩至目标阈值以内。

### 格式
| 格式 | 浏览器支持率 | 使用场景 |
|--------|-----------------|----------|
| WebP | 97%+ | 默认推荐格式 |
| AVIF | 92%+ | 压缩率最佳，较新 |
| JPEG | 100% | 照片类图片的兜底格式 |
| PNG | 100% | 需要透明度的图形 |
| SVG | 100% | 图标、Logo、插画 |

建议优先使用 WebP/AVIF 而非 JPEG/PNG。检查是否使用了带格式回退的 `<picture>` 元素。

#### 推荐的 `<picture>` 元素写法

采用渐进增强策略，优先使用压缩效率最高的格式：

```html
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="Descriptive alt text" width="800" height="600" loading="lazy" decoding="async">
</picture>
```

浏览器会自动使用其支持的第一种格式。当前浏览器支持率：AVIF 93.8%，WebP 95.3%。

#### JPEG XL：一个新兴格式

2025 年 11 月，Google 的 Chromium 团队推翻了 2022 年的决定，宣布将使用基于 Rust 的解码器在 Chrome 中恢复对 JPEG XL 的支持。该实现功能已完备，但尚未进入 Chrome 稳定版。JPEG XL 支持对 JPEG 进行无损重压缩（约节省 20% 体积且画质零损失），有损压缩表现也具有竞争力。目前还不适合投入生产环境，但值得持续关注其后续落地情况。

### 响应式图片
- 使用 `srcset` 属性提供多种尺寸
- 使用与布局断点匹配的 `sizes` 属性
- 适配不同设备像素比的分辨率

```html
<img
  src="image-800.jpg"
  srcset="image-400.jpg 400w, image-800.jpg 800w, image-1200.jpg 1200w"
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
  alt="Description"
>
```

### 懒加载
- 首屏以下的图片使用 `loading="lazy"`
- 首屏内/Hero 图片切勿懒加载（会拖累 LCP）
- 检查使用的是原生懒加载还是基于 JavaScript 的懒加载

```html
<!-- 首屏以下 - 懒加载 -->
<img src="photo.jpg" loading="lazy" alt="Description">

<!-- 首屏内 - 立即加载（默认行为） -->
<img src="hero.jpg" alt="Hero image">
```

#### 检测到的懒加载方式（`lazy_method` 字段）

`scripts/parse_html.py` 会通过每张图片条目上的 `lazy_method` 字段，识别该图片使用的懒加载机制，共有五种取值：

| `lazy_method` | 识别到的信号 | 常见技术栈 |
|---|---|---|
| `native` | `loading="lazy"` HTML 属性 | 现代浏览器、原生 HTML |
| `perfmatters` | `data-perfmatters-src`/`-srcset` 或 class 中含 `perfmatters-lazy` | WordPress + Perfmatters 插件 |
| `ewww` | `data-ewww-src` / `data-eio` 或 class 中含 `lazyload-eio` | WordPress + EWWW Image Optimizer |
| `js-generic` | `data-src` / `data-lazy-src` / `data-original` / `data-srcset` 或 class 中含 `lazyload`/`lazyloaded`/`lazy` | Lazysizes、vanilla-lazyload、jQuery 插件 |
| `none` | 未检测到相应属性或 class 信号 | 该页面未对此图片做懒加载 |

在审计图片 SEO 时，应将 `lazy_method` 与 `loading` 一并报告，让用户了解网站是否在使用 JS 驱动的懒加载方案（此时原生的 `loading="lazy"` 属性有意缺失，并非缺陷）。

### 为 LCP 图片添加 `fetchpriority="high"`

为 Hero/LCP 图片添加 `fetchpriority="high"`，使其在浏览器的网络请求队列中被优先下载：

```html
<img src="hero.webp" fetchpriority="high" alt="Hero image description" width="1200" height="630">
```

**关键提示：** 首屏内/LCP 图片切勿懒加载。对 LCP 图片使用 `loading="lazy"` 会直接损害 LCP 得分。`loading="lazy"` 应仅用于首屏以下的图片。

### 为非 LCP 图片添加 `decoding="async"`

为非 LCP 图片添加 `decoding="async"`，避免图片解码阻塞主线程：

```html
<img src="photo.webp" alt="Description" width="600" height="400" loading="lazy" decoding="async">
```

### CLS 预防

- 所有 `<img>` 元素都应设置 `width` 和 `height` 属性
- 也可用 `aspect-ratio` CSS 作为替代方案
- 标记出缺少尺寸信息的图片

```html
<!-- 好 - 已设置尺寸 -->
<img src="photo.jpg" width="800" height="600" alt="Description">

<!-- 好 - CSS 宽高比 -->
<img src="photo.jpg" style="aspect-ratio: 4/3" alt="Description">

<!-- 差 - 未设置尺寸 -->
<img src="photo.jpg" alt="Description">
```

### 文件命名
- 描述性命名：如 `blue-running-shoes.webp` 而非 `IMG_1234.jpg`
- 使用连字符、小写字母，不含特殊字符
- 包含相关关键词

### CDN 使用情况
- 检查图片是否通过 CDN 分发（不同域名、CDN 响应头）
- 对图片密集型站点建议使用 CDN
- 检查是否配置了边缘缓存响应头

## 输出

### 图片审计摘要

| 指标 | 状态 | 数量 |
|--------|--------|-------|
| 图片总数 | - | XX |
| 缺少 Alt Text | ❌ | XX |
| 体积超标（>200KB） | ⚠️ | XX |
| 格式不合规 | ⚠️ | XX |
| 缺少尺寸信息 | ⚠️ | XX |
| 未启用懒加载 | ⚠️ | XX |

### 优化优先级清单

按文件体积影响排序（体积可压缩空间最大的排在前面）：

| 图片 | 当前大小 | 格式 | 问题 | 预估可节省空间 |
|-------|--------------|--------|--------|--------------|
| ... | ... | ... | ... | ... |

### 建议
1. 将 X 张图片转换为 WebP 格式（预计节省 XX KB）
2. 为 X 张图片补充 alt text
3. 为 X 张图片补充尺寸信息
4. 对 X 张首屏以下图片启用懒加载
5. 压缩 X 张体积超标的图片

---

## 图片 SERP 分析

当 DataForSEO MCP 可用时，为图片审计补充竞品数据。

### `/seo images serp <keyword>`

将站内图片与 Google Images 的 SERP 排名进行交叉对比。

**工作流程：**
1. 通过 `serp_google_images_live_advanced` 获取结果（depth=100）
2. 提取：主要域名、图片类型、alt text 规律
3. 输出竞品图片 SERP 全景图

**输出：**

| 排名 | 域名 | 标题/Alt | 图片 URL | 页面 URL |
|------|--------|-----------|-----------|----------|
| 1 | example.com | "Blue running shoes..." | .../shoes.webp | /products/... |

**分析内容包括：**
- **域名占位统计**：哪些站点占据了最多的图片位（按数量取前 10）
- **Alt text 规律**：排名靠前图片中常见的标题/alt 写法
- **格式分布**：排名靠前的结果中 WebP、JPEG、PNG 的占比
- **机会评分**：哪些关键词你已有网页排名但没有图片曝光

若 DataForSEO MCP 不可用，应告知用户并建议安装该扩展。

---

## 图片文件优化

针对 SEO 优化图片文件：格式转换、元数据注入、压缩。

### `/seo images optimize <path>`

对图片文件进行 Web 与 SEO 优化：转换为 WebP/AVIF、注入 IPTC
元数据、压缩，并生成响应式变体。

**使用工具（按优先级排序）：**
- `exiftool` —— 读写 EXIF/IPTC/XMP（安装：`sudo apt install libimage-exiftool-perl`）
- `cwebp` —— WebP 转换（安装：`sudo apt install webp`）
- ImageMagick `convert` —— 格式转换、缩放（大多数系统已预装）
- FFmpeg —— 格式转换的兜底方案（已预装）

**运行前：**用 `which exiftool cwebp convert ffmpeg` 检查有哪些工具可用。

### 格式转换

将图片转换为现代格式，同时保留元数据：

```bash
# WebP（推荐默认格式）- 保留元数据
cwebp -q 82 -metadata all input.jpg -o output.webp

# 通过 ImageMagick 转 WebP（cwebp 未安装时的兜底方案）
convert input.jpg -quality 82 output.webp

# 通过 FFmpeg 转 AVIF（编码较慢，压缩率最佳）
ffmpeg -i input.jpg -c:v libaom-av1 -crf 30 -still-picture 1 output.avif

# 响应式变体（400w、800w、1200w）
convert input.jpg -resize 400x -quality 82 image-400.webp
convert input.jpg -resize 800x -quality 82 image-800.webp
convert input.jpg -resize 1200x -quality 82 image-1200.webp
```

### 元数据注入（面向 Google 富媒体结果的 IPTC）

Google Images 会在搜索结果中展示 IPTC 的 Creator、Credit Line 和 Copyright 信息。
这**不是排名因素**，但能改善富媒体结果的展示效果和品牌署名。

**使用 exiftool（首选）：**
```bash
# 读取全部元数据
exiftool image.jpg

# 为 Google Images 富媒体结果注入 IPTC + XMP 元数据
exiftool \
  -IPTC:ObjectName="Product Photo Description" \
  -IPTC:Caption-Abstract="Detailed image description" \
  -IPTC:By-line="Brand Name Photography" \
  -IPTC:Credit="Brand Name" \
  -IPTC:CopyrightNotice="Copyright 2026 Brand Name" \
  -IPTC:Source="brandname.com" \
  -XMP:Title="Product Photo Description" \
  -XMP:Description="Detailed image description" \
  -XMP:Creator="Brand Name Photography" \
  -XMP:Rights="Copyright 2026 Brand Name" \
  image.jpg

# 批量为目录下所有图片注入
exiftool -overwrite_original \
  -IPTC:By-line="Brand Name" \
  -IPTC:CopyrightNotice="Copyright 2026 Brand Name" \
  *.jpg *.webp *.png
```

**使用 ImageMagick（兜底方案）：**
```bash
identify -verbose image.jpg | head -50

convert input.jpg \
  -set comment "Product Photo Description" \
  -set IPTC:2:80 "Brand Name Photography" \
  -set IPTC:2:116 "Copyright 2026 Brand Name" \
  output.jpg
```

**重要提示：**WebP 支持 EXIF 和 XMP，但原生**不支持** IPTC。对于 WebP 文件，
应改用 XMP 字段而非 IPTC。exiftool 会自动处理这一转换。

### AI 生成图片：`DigitalSourceType`（Merchant Center 强制要求）

对于由生成式 AI 产出的产品图片，**Google Merchant Center 要求**必须携带
IPTC `DigitalSourceType: TrainedAlgorithmicMedia` 元数据。这是一项
运营层面的政策要求，而非排名因素——AI 生成图片如果 feed 中缺少该标签，
可能会被驳回（disapproved）。

信息来源：
https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
（该文档引用了 Merchant Center 关于 AI 媒体标注的底层政策）

**审计命令：**

```bash
# 审计某目录下的 IPTC 标签情况（统计缺失、AI 生成、实拍等数量）
python3 scripts/iptc_ai_label.py audit ./images/ --json

# 审计单张图片
python3 scripts/iptc_ai_label.py audit ./hero.webp --json

# 为图片注入 AI 标签
python3 scripts/iptc_ai_label.py inject ./ai-hero.webp \
    --source-type trainedAlgorithmicMedia

# 其他可选值：
#   compositeSynthetic  （实拍与 AI 元素混合）
#   digitalCapture      （完全为实拍照片）
```

**原生 exiftool 等效命令**（供临时手动操作使用）：

```bash
# 手动注入
exiftool \
  -XMP-iptcExt:DigitalSourceType="https://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia" \
  ai-generated-product.jpg

# 审计：在目录中查找缺少该标签的图片
exiftool -if 'not $XMP-iptcExt:DigitalSourceType' \
  -filename -DigitalSourceType *.jpg *.webp *.png
```

IPTC 词表还定义了：
- `trainedAlgorithmicMedia` —— 完全由 AI 生成（适用于扩散模型生成的
  产品图片）
- `compositeSynthetic` —— 实拍与 AI 生成元素混合
- `digitalCapture` —— 完全为实拍照片（不含 AI 成分）

当对 AI 生成素材执行 `/seo images optimize` 时，应提示用户确认来源类型，
并自动注入对应的 IPTC 值。

对于**AI 生成的产品标题和描述**，Google Merchant Center 同样要求
在 feed 中单独标注和声明这些 AI 生成文本。这项要求在 feed 层面强制执行，
而非页面层面——需与 `seo-ecommerce` 交叉核对并在报告中标记。

### 元数据审计

```bash
# 用 exiftool 快速审计
exiftool -IPTC:all -XMP:all -EXIF:ImageDescription image.jpg

# 批量审计 - 查找缺少 IPTC Creator 的图片
exiftool -if 'not $IPTC:By-line' -filename *.jpg *.webp *.png
```

### 完整优化流水线

要实现图片 SEO 的最大化效果，对每张图片执行以下流水线：

1. **审计现有元数据**：`exiftool -IPTC:all -XMP:all image.jpg`
2. **注入 IPTC/XMP 元数据**：Creator、Copyright、Description
3. **转换为 WebP**：`cwebp -q 82 -metadata all image.jpg -o image.webp`
4. **生成响应式变体**：400w、800w、1200w
5. **验证元数据是否保留**：`exiftool image.webp`
6. **生成 `<picture>` HTML**：AVIF > WebP > JPEG 的回退链

### 对 Google Images 而言，哪些因素重要、哪些不重要

| 因素 | 影响程度 | 设置位置 |
|--------|--------|--------------|
| Alt text | **关键**（排名因素） | HTML `<img alt="">` |
| 文件名 | **高**（排名因素） | 文件系统（描述性、连字符命名） |
| 页面上下文 | **高**（排名因素） | 周边 HTML 内容 |
| 文件大小/速度 | **中**（通过 Core Web Vitals 间接影响） | 压缩与格式转换 |
| IPTC Creator/Copyright | **低**（仅影响展示） | 图片文件元数据 |
| EXIF 相机数据 | 无影响 | 与 SEO 无关 |
| IPTC Keywords | 无影响 | Google 会忽略这些字段 |

---

## 错误处理

| 场景 | 处理方式 |
|----------|--------|
| URL 无法访问 | 报告连接错误及状态码。建议核实 URL，并检查站点是否需要身份验证。 |
| 页面未检测到图片 | 报告未检测到 `<img>` 元素。建议检查图片是否通过 JavaScript 或 CSS background-image 加载。 |
| 图片位于 CDN 或需要身份验证 | 说明无法直接访问图片文件以分析体积。报告可获得的元数据（来自标记的 alt text、尺寸、格式），并标记出无法访问的资源。 |
| exiftool 未安装 | 回退使用 ImageMagick 处理元数据。建议：`sudo apt install libimage-exiftool-perl` |
| cwebp 未安装 | 回退使用 ImageMagick 或 FFmpeg 进行 WebP 转换。建议：`sudo apt install webp` |
| DataForSEO MCP 不可用 | 跳过"图片 SERP 分析"部分，说明该扩展未安装。 |
