#import "../index.typ": template, tufted
#show: template.with(title: "网站配置")

= 网站结构

模板主要由 5 个部分组成：

- `config.typ` - 站点配置与模板入口
- `tufted-lib/` - 上游模板实现（无需修改）
- `content/` - 存储所有网页内容
- `assets/` - 样式、脚本与图标
- `build.py` - 构建脚本（HTML、PDF、RSS、sitemap）

== 可用函数

`config.typ` 从 `tufted-lib/tufted.typ` 导入并重新导出，页面里可以直接用：

- `template` - 站点外壳（本站对 `tufted-web` 的薄包装，增加首页 hero 区）
- `archive(posts)` - 首页按年份分组的目录式列表
- `tufted.blog-entry` - 带日期列的博客条目
- `tufted.margin-note` - 在右侧边栏中放置内容
- `tufted.full-width` - 让内容占满整行
- `tufted.icon-link` - 在导航栏添加自定义 SVG 图标链接

具体使用见 #link("../typst-example/")[Typst 功能速览与样例]。

== 主要配置

站点配置集中在 `config.typ`：

```typst
// 站点信息
#let site-title = "rainoffallingstar’s Blog"
#let site-wordmark = "rainoffallingstar"
#let site-tagline = "凡是过往，皆为序章。"
#let site-author = "rainoffallingstar"
#let site-url = "https://blog.rainoffallingstar.com"

// 站名前的圆形标记（图片在 assets/logo.jpg）
#let site-logo = html.img(
  src: "/assets/logo.jpg",
  alt: "",
  class: "site-logo",
  decoding: "async",
)

// 导航项：第一项是站名，兼作返回首页
#let header-links = (
  "/": { site-logo; site-wordmark },
  "/Links/": "友链",
  "/About/": "关于",
)
```

模板本体由上游提供，本站只传入站点参数：

```typst
#let site = tufted.tufted-web.with(
  header-links: header-links,
  website-title: site-title,
  website-url: site-url,        // 用于 canonical / sitemap / RSS
  author: site-author,
  description: site-description,
  feed-dir: ("/Blog/",),        // 生成 RSS 并在导航栏显示订阅图标
  css: ("/assets/custom.css", "/assets/site.css"),
  footer-elements: ( /* ... */ ),
)
```

== 可选参数

上游 `tufted-web` 支持的主要参数：

- `title` —— 页面标题（浏览器标签页与元数据）。
- `description` —— 页面描述，用于 SEO 与社交预览。
- `date` —— 发布日期。RSS 需要它，缺失的文章会被跳过。
- `lang` —— `<html lang>`，默认 `"zh"`。
- `header-icons` —— 导航栏图标链接，用 `tufted.icon-link()` 生成。
- `margin-citations` —— 把 author-date 引用的完整条目显示在边栏。
- `footer-elements` / `header-elements` —— 自定义页脚与页眉内容。

页面写法：

```typst
#import "../config.typ": template, tufted
#show: template.with(
  title: "文章标题",
  description: "一句话摘要",
  date: datetime(year: 2025, month: 4, day: 16),
)
```

=== 关于日期

`build.py` 生成 `sitemap.xml` 和 `feed.xml` 时，会从以下位置取日期：

1. HTML 里的 `<meta name="date">`（由 `date:` 参数生成）
2. 目录名中的 `YYYY-MM-DD`

目录名里没有标准日期的文章需要显式传 `date:`，否则不会进入 RSS。

== 自动构建产物

`python build.py build` 除 HTML/PDF 外还会生成：

- `sitemap.xml` —— 需要 `website-url` 才能生成
- `robots.txt` —— 指向 sitemap
- `feed.xml` —— 需要 `feed-dir`，并且每篇文章要有日期

== 层级结构与继承

网站遵循层级结构。根目录从 `../config.typ` 导入，而子页面从其父目录的 `../index.typ` 文件导入。

`content/` 目录中所有的 `**/index.typ` 文件都会成为可访问的页面，其路径对应文件夹的路径（例如 `content/Blog/index.typ` → `example.github.io/Blog`）。

== 与上游同步

本仓库基于 #link("https://github.com/Yousa-Mirage/Tufted-Blog-Template")[Tufted-Blog-Template]。
`.github/workflows/update.yml` 会每两周向上游拉取一次改动并开 PR。

本站自有文件已写入 `.github/.templatesyncignore`，同步时不会被覆盖：
`content/`、`config.typ`、`assets/custom.css`、`assets/site.css`、部署工作流等。
