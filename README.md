# rainoffallingstar's Blog

基于 [Tufted Blog](https://github.com/Myriad-Dreamin/tufted) 的个人博客，使用 Typst 编写内容，Python 自动构建部署。

## 技术栈

- **内容编写**: [Typst](https://typst.app/) - 现代化的排版系统
- **静态站点生成**: [Tufted Blog](https://github.com/Myriad-Dreamin/tufted) - 基于 Tufte CSS 设计
- **构建工具**: Python + Typst CLI
- **部署**: GitHub Pages + GitHub Actions
- **文献追踪**: AI 驱动的 PubMed 文献自动抓取与评分（追觅功能）

## 特点

- 📝 使用 Typst 语言编写，语法简洁优雅
- 🎨 Tufte CSS 设计风格，宽大侧边栏，适合阅读
- 🌙 支持深色模式
- 📱 响应式设计，移动端友好
- ⚡️ 自动构建部署（GitHub Actions）
- 🔬 **追觅** - 每日自动抓取 PubMed 最新文献，AI 评分与推荐

## 本地运行

### 环境要求

1. **安装 Typst**

   访问 [Typst 官网](https://typst.app/open-source/#download) 下载安装

2. **验证安装**

   ```bash
   typst --version
   python --version
   ```

### 构建网站

```bash
# 完整构建（HTML + PDF）
python build.py build

# 强制重新构建
python build.py build --force

# 仅构建 HTML
python build.py html

# 仅构建 PDF
python build.py pdf

# 清理构建输出
python build.py clean
```

### 本地预览

```bash
# 启动预览服务器（默认端口 8000）
python build.py preview

# 使用自定义端口
python build.py preview -p 3000
```

然后访问 http://localhost:8000

## 目录结构

```
.
├── content/           # 网站内容（Typst 文件）
│   ├── Blog/         # 博客文章
│   ├── ZhuiMi/       # 追觅 - 文献追踪
│   ├── About/        # 关于页面
│   ├── Links/        # 友链页面
│   └── index.typ     # 首页
├── assets/           # 静态资源
│   ├── copy-code.js
│   ├── custom.css
│   └── tufted.css
├── scripts/          # 脚本工具
│   ├── zhuimi_update.py    # 追觅更新脚本
│   ├── config/
│   │   └── zhuimi_config.yaml
│   ├── follow.opml         # RSS 订阅源
│   └── pubmed_feeds.json   # PubMed 源列表
├── config.typ        # 站点配置
├── build.py          # 构建脚本
├── .github/
│   └── workflows/
│       ├── deploy.yml      # 网站部署
│       └── zhuimi.yml      # 追觅自动更新
└── _site/            # 构建输出（Git 忽略）
```

## 写文章

### 创建新文章

1. 在 `content/Blog/` 下创建新目录，格式：`YYYY-MM-DD-title/`
2. 在目录中创建 `index.typ` 文件

### 文章模板

```typst
#import "../../config.typ": template, tufted
#show: template.with(title: "文章标题")

= 文章标题

这里是文章内容...

== 二级标题

正文内容...

### 三级标题

更多内容...
```

### Typst 语法示例

```typst
# 粗体
*斜体*

# 链接
#link("https://example.com")[链接文字]

# 图片
#image("imgs/image.png")

# 代码块
```rust
fn main() {
    println!("Hello, World!");
}
```

# 列表
- 项目 1
- 项目 2

+ 编号项目 1
+ 编号项目 2
```

## 追觅 - 文献追踪功能

### 功能说明

追觅是本博客的 AI 驱动文献追踪功能，每日自动：

1. 从 26 个 PubMed RSS 源抓取最新文献（最近 3 天）
2. 使用 AI 对每篇文章进行 4 维度评分：
   - **研究分数** - 创新性、方法严谨性、数据可靠性
   - **社会影响** - 公众关注度、政策相关性
   - **血液相关性** - 血液疾病相关性、可借鉴性
   - **推荐度** - 综合推荐指数
3. 生成中文推荐理由
4. 自动过滤低质量文章（推荐度=0 或 血液相关性=0）
5. 生成 Typst 格式日报并发布

### 配置 GitHub Secrets

要启用追觅功能，需要在 GitHub 仓库中配置以下 Secrets：

#### 步骤 1: 进入 GitHub Secrets 设置

1. 访问仓库页面：https://github.com/rainoffallingstar/rainoffallingstar.github.io
2. 点击 `Settings` 标签
3. 在左侧菜单中找到 `Secrets and variables` → `Actions`
4. 点击 `New repository secret` 添加新的 Secret

#### 步骤 2: 添加以下三个 Secrets

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `OPENAI_BASE_URL` | OpenAI 兼容 API 的基础 URL | `http://110.41.44.194:3000` |
| `OPENAI_API_KEY` | API 密钥 | `sk-xxxxxxxxxxxxxx` |
| `OPENAI_MODEL` | 使用的模型名称 | `deepseek-ai/DeepSeek-V3.2-thinking` |

**注意**：
- `OPENAI_BASE_URL` 会自动添加 `/v1` 后缀，无需手动添加
- 请确保 API 密钥有足够的配额用于每日评分
- 模型名称需要与你的 API 服务商提供的名称一致

#### 步骤 3: 验证配置

添加完 Secrets 后，可以通过以下方式验证：

1. 访问 `Actions` 标签
2. 选择 `ZhuiMi Daily Literature Update` 工作流
3. 点击 `Run workflow` 手动触发测试
4. 查看运行日志确认是否成功

### 本地测试追觅功能

```bash
# 设置环境变量
export OPENAI_BASE_URL=http://110.41.44.194:3000
export OPENAI_API_KEY=your-api-key
export OPENAI_MODEL=deepseek-ai/DeepSeek-V3.2-thinking

# 运行追觅更新
python scripts/zhuimi_update.py
```

### 追觅配置文件

编辑 `scripts/config/zhuimi_config.yaml` 可自定义：

```yaml
# RSS抓取配置
rss:
  days_window: 3  # 抓取最近几天的文章
  max_feeds: 100  # 最多使用的RSS源数量

# AI评分配置
ai:
  model: "deepseek-ai/DeepSeek-V3.2-thinking"
  max_tokens: 300
  temperature: 0.3

# 报告配置
report:
  sort_by: "recommendation"  # 按推荐度排序
  max_articles: 200         # 每日最多分析文章数
```

### 自动运行

追觅功能通过 GitHub Actions 每天自动运行：

- **运行时间**：每天北京时间早上 6:00（UTC 22:00）
- **运行方式**：自动抓取、评分、生成报告、提交到仓库
- **手动触发**：可在 Actions 页面手动运行

查看追觅报告：访问 `/ZhuiMi/` 页面

## 部署

网站使用 GitHub Actions 自动构建部署：

1. 修改内容后提交到 `githubversion` 分支
2. GitHub Actions 自动触发构建
3. 构建完成后自动部署到 GitHub Pages

查看构建状态：https://github.com/rainoffallingstar/rainoffallingstar.github.io/actions

## 自定义域名

如需使用自定义域名：

1. 编辑 `CNAME` 文件，填入你的域名
2. 在域名服务商处配置 DNS 解析到 GitHub Pages

## 许可证

[MIT License](./LICENSE)
