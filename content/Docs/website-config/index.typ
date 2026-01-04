#import "../index.typ": template, tufted
#show: template.with(title: "网站配置")

= 网站结构

模板主要由 4 个部分组成：

- `config.typ` - 核心布局配置文件
- `content/` - 存储所有网页内容
- `assets/` - 存储共享的资源，例如全局 CSS、JS 脚本、ICON 等
- `Makefile` 或 `build.py` - 用于构建网站的脚本

== 可用函数

`tufted` 包目前提供了以下三个函数：

- `tufted-web` - 主模板
- `margin-note` - 在边栏中放置内容（功能有限）
- `full-width` - 将内容放在全宽容器中（功能有限）

具体使用见 #link("../typst-example/")[Typst 功能速览与样例]。

== 主要配置

在 `config.typ` 中，你可以通过自定义从 `tufted` 包导入的 `tufted-web` 模板来定义自己的模板。你可以在这里配置顶部导航栏链接和网站标题：

```typst
#import "@preview/tufted:0.1.0"

#let template = tufted.tufted-web.with(
  // 顶部导航栏的链接和标签
  header-links: (
    "/": "首页",
    "/Blog/": "博客",
    "/CV/": "简历",
    "/About/": "关于",
  ),
  // 网站标题
  title: "我的个人网站",
)
```

== 层级结构与继承

网站遵循层级结构。根目录从 `../config.typ` 导入，而子页面从其父目录的 `../index.typ` 文件导入，这样就能实现继承关系，无需从项目根路径导入。

`content/` 目录中所有的 `**/index.typ` 文件都会成为可访问的页面，其路径对应文件夹的路径（例如 `content/Blog/index.typ` → `example.github.io/Blog`）。使用 `#link("相对/路径/")[点击我]` 来链接到其他页面或目录中其他文件，详细链接用法可参见 #link("../typst-example/")[Typst 功能速览与样例]。

你可以在任何层级修改定义，子页面都会继承这些更改。例如，要改变页面标题，可以从父级导入定义并修改 `template`：

```typst
#import "../index.typ": template, tufted
// 该页面及其所有子页面都将在浏览器标签中显示为 "新标题"
#show: template.with(title: "新标题")
```
