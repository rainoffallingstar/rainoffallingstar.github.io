# rainoffallingstar's Blog

基于 [Tufted Blog](https://github.com/Myriad-Dreamin/tufted) 的个人博客，使用 Typst 编写内容，Python 自动构建部署。

## 技术栈

- **内容编写**: [Typst](https://typst.app/) - 现代化的排版系统
- **静态站点生成**: [Tufted Blog](https://github.com/Myriad-Dreamin/tufted) - 基于 Tufte CSS 设计
- **构建工具**: Python + Typst CLI
- **部署**: GitHub Pages + GitHub Actions

## 特点

- 📝 使用 Typst 语言编写，语法简洁优雅
- 🎨 Tufte CSS 设计风格，宽大侧边栏，适合阅读
- 🌙 支持深色模式
- 📱 响应式设计，移动端友好
- ⚡️ 自动构建部署（GitHub Actions）

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
│   ├── About/        # 关于页面
│   ├── Links/        # 友链页面
│   └── index.typ     # 首页
├── assets/           # 静态资源
│   ├── copy-code.js
│   ├── custom.css
│   └── tufted.css
├── config.typ        # 站点配置
├── build.py          # 构建脚本
├── .github/
│   └── workflows/
│       └── deploy.yml  # GitHub Actions 配置
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
