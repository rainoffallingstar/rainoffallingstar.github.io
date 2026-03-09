# rainoffallingstar's Blog

基于 [Tufted Blog](https://github.com/Myriad-Dreamin/tufted) 的个人博客，使用 Typst 编写内容，Python 自动构建并部署到 GitHub Pages。

## 技术栈

- 内容编写: [Typst](https://typst.app/)
- 静态站点生成: Tufted
- 构建工具: Python + Typst CLI
- 部署: GitHub Actions + GitHub Pages

## 本地运行

### 环境要求

```bash
typst --version
python --version
```

### 常用命令

```bash
# 完整构建（HTML + PDF + 资源）
python build.py build

# 强制重建
python build.py build --force

# 仅构建 HTML / PDF
python build.py html
python build.py pdf

# 本地预览（默认 8000 端口）
python build.py preview

# 清理构建产物
python build.py clean
```

## 目录结构

```text
.
├── content/           # 网站内容（Typst）
│   ├── Blog/
│   ├── About/
│   ├── Links/
│   ├── Docs/
│   └── index.typ
├── assets/            # CSS/JS/图片等静态资源
├── build.py           # 构建脚本
├── config.typ         # 站点配置
└── .github/workflows/
    └── deploy.yml     # 自动构建与部署
```

## 写文章

1. 在 `content/Blog/` 下创建目录：`YYYY-MM-DD-title/`
2. 在目录中创建 `index.typ`
3. 提交到 `githubversion` 分支，触发自动部署

示例：

```typst
#import "../../config.typ": template, tufted
#show: template.with(title: "文章标题")

= 文章标题
正文内容...
```

## 部署

仓库在 `githubversion` 分支有变更时，会由 `.github/workflows/deploy.yml` 自动构建并发布到 GitHub Pages。

## 许可证

[MIT License](./LICENSE)
