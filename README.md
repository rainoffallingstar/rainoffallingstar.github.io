# rainoffallingstar's Blog

基于 [Tufted-Blog-Template](https://github.com/Yousa-Mirage/Tufted-Blog-Template) 的个人博客，使用 Typst 编写内容，Python 自动构建并部署到 GitHub Pages。

站点地址：**https://blog.rainoffallingstar.com**

## 技术栈

- 内容编写: [Typst](https://typst.app/)
- 静态站点生成: Tufted（`tufted-lib/`，随上游同步）
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
│   └── index.typ      # 首页归档数据（posts 数组）
├── tufted-lib/        # 模板实现（随上游同步，勿手改）
├── assets/            # 样式与脚本
│   ├── tufted.css     # 上游功能层
│   ├── theme.css      # 上游主题变量
│   ├── custom.css     # 用户覆盖入口
│   ├── site.css       # 本站视觉层（改样式在这里）
│   ├── site.js        # 本站脚本
│   ├── icons/         # RSS / 明暗图标
│   └── scripts/       # 上游脚本（目录、返回顶部、复制等）
├── build.py           # 构建脚本（HTML / PDF / RSS / sitemap）
├── config.typ         # 站点配置
├── CNAME              # 自定义域名（部署真源）
└── .github/
    ├── workflows/
    │   ├── deploy.yml # 自动构建与部署
    │   └── update.yml # 每两周从上游同步模板
    └── .templatesyncignore  # 同步时排除的本站文件
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

仓库在 `githubversion` 分支有变更时，会由 `.github/workflows/deploy.yml` 自动构建并发布到 GitHub Pages（`gh-pages` 分支）。

构建会产出的文件：

```text
_site/
├── index.html
├── Blog/ About/ Links/ Docs/ CV/   # 各页面
├── feed.xml        # RSS（全文输出）
├── sitemap.xml     # 站点地图
├── robots.txt      # 指向 sitemap
├── assets/
└── CNAME
```

## 自定义域名

站点通过自定义域名 `blog.rainoffallingstar.com` 访问。

**域名在三处定义，改域名必须三处同时改：**

| 位置 | 作用 |
| --- | --- |
| `CNAME`（仓库根目录） | GitHub Pages 读取的域名文件，只写裸域名，不带协议和斜杠 |
| `config.typ` 的 `site-url` | 生成 `canonical`、`sitemap.xml`、`feed.xml`、Open Graph 的绝对 URL |
| `.github/workflows/deploy.yml` 的 `cname:` | 部署 action 写入 `gh-pages` 的域名，必须与 `CNAME` 一致 |

### 注意事项

- **不要手改 `gh-pages` 分支上的 `CNAME`**。该分支是构建产物，下次部署会从主分支的 `CNAME` 覆盖回去。
- 部署工作流在发布前会校验 `CNAME` 存在且非空，写错会让 CI 直接失败，而不是静默丢掉域名。
- 更换域名后，还要到域名服务商（Cloudflare）把记录改为指向 `rainoffallingstar.github.io` 的 CNAME，并**先关闭代理（灰云 / DNS only）**，等 GitHub 签发完 TLS 证书后再按需开启。
- 确认部署状态：

```bash
gh api repos/rainoffallingstar/rainoffallingstar.github.io/pages \
  --jq '{cname, https_enforced, status}'
curl -sSI https://blog.rainoffallingstar.com/ | head -1
```

`https_enforced` 应为 `true`，且 HTTP 会 301 跳转到 HTTPS。

## 与上游模板同步

`tufted-lib/`、`assets/tufted.css`、`assets/theme.css`、`assets/scripts/` 等来自上游模板。

- **不要直接修改这些文件**，否则下次同步会被覆盖。
- 本站定制的样式写在 `assets/site.css`，配置写在 `config.typ`。
- `.github/workflows/update.yml` 每两周向上游拉取一次改动并开 PR。
- 本站自有文件已列入 `.github/.templatesyncignore`，同步时会被跳过。新增需要保留的文件时，记得也加进去。

## 许可证

[MIT License](./LICENSE)
