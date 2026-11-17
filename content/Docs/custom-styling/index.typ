#import "../index.typ": template, tufted
#show: template.with(title: "自定义样式")

= 自定义样式

网站的视觉外观由 CSS 控制，字体、字号、颜色与栅格都无法在 Typst 中直接修改。如需调整，请修改 `assets/` 下的样式表。

== 视觉方向

整体参考 #link("https://astro-air.guoqi.dev/")[astro-air]：手写体、窄正文栏、大量留白、几乎不用边框和分隔线。浅色是白纸上的黑墨，深色是近黑底配橙色强调。

== 样式表加载顺序

模板按以下顺序加载样式，后加载的规则覆盖先加载的：

+ `tufte.min.css` —— 来自 CDN 的 Tufte 基础排版
+ `/assets/tufted.css` —— 模板功能层（栅格、代码块、表格、目录、归档条目）
+ `/assets/theme.css` —— 明暗主题变量与切换按钮图标
+ `/assets/fonts.css` —— 自托管手写字体的 `@font-face`，由 `tools/build_fonts.py` 生成
+ `/assets/custom.css` —— 内容级补丁（提示块、脚注角标）
+ `/assets/site.css` —— 本站视觉层（配色、栅格、页头、归档列表）

=== 各文件职责

- `assets/tufted.css`、`assets/theme.css`、`assets/scripts/`：由上游模板维护，**不要直接改**，否则下次同步会被覆盖。
- `assets/fonts.css`：由 `tools/build_fonts.py` 生成，不要手改。
- `assets/custom.css`：只放依赖 Typst 输出结构的补丁。
- `assets/site.css`：本站的全部视觉定制。

== 字体

三个字体都按 SIL Open Font License 1.1 授权，随仓库自带，不依赖 CDN：

#table(
  columns: 3,
  align: left,
  [字体], [用途], [文件],
  [Xiaolai 霞鹜小赖], [中文正文，毛笔手写风], [`assets/fonts/xiaolai/`],
  [Excalifont], [拉丁字母与数字], [`assets/fonts/excalifont/`],
  [WenKai Mono], [代码块], [`assets/fonts/mono/`],
)

完整的中文字体有二十多 MB，因此构建脚本会按站点实际用字（加上 GB2312 一级常用字）做子集，结果约 870 KB；拉丁字母单独成文件，纯英文页面不会下载中文字形。

新增文章若用到生僻字，重跑一次脚本即可：

```bash
uv run --with fonttools --with brotli python3 tools/build_fonts.py
```

== 设计令牌

`site.css` 顶部集中管理配色与字体，并且**同时映射到上游的 `--theme-*` 变量**，这样目录、返回顶部、代码块、页脚等上游组件会自动采用本站配色：

```css
html[data-theme="light"] {
    --paper: #ffffff;      /* 纸面 */
    --ink: #171717;        /* 正文墨色 */
    --ink-muted: #6b7280;  /* 次级文字 */
    --ink-faint: #9ca3af;  /* 三级文字 */
    --rule: rgb(0 0 0 / 10%);   /* 分隔线 */
    --accent: #2563eb;     /* 链接与悬停 */

    /* 映射给上游组件 */
    --theme-bg: var(--paper);
    --theme-text: var(--ink);
    --theme-heading: var(--ink-strong);
    /* ... */
}
```

深色模式把 `--accent` 换成橙色 `#f97316`，正文换成 `#ffffff`、底色 `#121212`。

== 栅格与边注

正文栏宽由 `--measure`（默认 `46rem`）控制，在页面中居中。Tufte 的边注（`.marginnote`）通过上游的 `--sidenote-*` 变量悬挂到正文栏右侧的留白里：

```css
@media (min-width: 1180px) {
    article > section {
        --sidenote-content-width: 1;
        --sidenote-column-start: 1.04;
        --sidenote-column-width: 0.34;
    }
}
```

窗口窄于 1180px 时边注会内联展开（上游行为）；窄屏下目录按钮也会收起，避免压住正文。

== 深色模式

主题由上游的 `assets/scripts/theme-toggle.js` 控制：

- 优先级：`sessionStorage`（本次浏览会话的手动选择）> 系统的 `prefers-color-scheme`
- 手动切换只在当前会话内有效，新会话会重新跟随系统

`assets/site.js` 在按钮点击时用 View Transitions 从点击位置做一次圆形扩散；系统开启「减少动态效果」时自动跳过。本站只在 `site.css` 里提供 `html[data-theme="dark"]` 的变量值，不要再写 `@media (prefers-color-scheme: dark)` 覆盖颜色，否则手动切换会失效。

== 页头、首页与页脚

页头由上游 `tufted-web` 生成，结构为：

```text
header.site-header > nav.site-nav
  .site-nav-links   ← 站名 + 栏目
  .site-nav-tools   ← RSS 图标、主题切换按钮
```

`site.css` 用绝对定位把站名放到第一行、栏目放到第二行，工具按钮放在右上角 —— 两行页头完全由 CSS 完成。导航项在 `config.typ` 的 `header-links` 中定义，第一项是返回首页的站名，其内容由 `site-logo`（`assets/logo.jpg` 的圆形标记）加 `site-wordmark` 组成：

```typst
#let site-logo = html.img(
  src: "/assets/logo.jpg",
  alt: "",
  class: "site-logo",
  width: 34,
  height: 34,
  // 尺寸写在 style 里，不依赖样式表
  style: "width:var(--site-logo-size,2.15rem);height:var(--site-logo-size,2.15rem);object-fit:cover;border-radius:50%",
  decoding: "async",
)

#let header-links = (
  "/": { site-logo; site-wordmark },
  "/Timeline/": "时间线",
  // ...
)
```

标记在 `site.css` 里用 `.site-logo` 做圆形裁切，随站名字号缩放（窄屏 1.9rem、桌面 2.15rem）；`assets/favicon.ico` 是同一张图更紧的头像裁切，供浏览器标签页使用。

首页导语来自 `config.typ` 的 `site-intro`，由 `template(intro: ...)` 渲染成 `.intro` 段落。页脚结构在 `footer-elements` 里：左侧版权与署名，右侧 RSS 订阅。

文章索引在 `content/_data/posts.typ` 的 `posts` 数组里，每项形如：

```typst
(date: "2022-11-04", title: "Workflow Machine Learning with Radio-mics", href: "/Blog/.../"),
```

目录名以下划线开头，`build.py` 不会把它编译成页面，只当作公共依赖 —— 改动后所有页面都会重建。

三个地方共用这份数据：

- `content/index.typ` 调用 `config.typ` 的 `latest-posts()`，按日期取最新的 `site-latest-count` 篇（默认 10），渲染成「最近更新」列表，末尾给出通往完整时间线的入口。
- `content/Timeline/index.typ` 调用 `archive()`，按年份分组展示全部文章。
- 每篇文章底部由 `config.typ` 的 `post-pager()` 自动追加「上一篇 / 下一篇」卡片。它用构建脚本传入的 `page-path` 在索引里定位当前文章：索引里没有的页面（首页、时间线、Docs 等）不显示翻页，文章 `.typ` 也不必声明自己排第几。方向按发布日期计算，**上一篇是更早发布的那篇**。

前两处用上游的 `tufted.blog-entry()` 渲染「日期列 + 标题列」，翻页卡片的结构与样式见 `config.typ` 的 `post-pager()` 与 `site.css` 第 8 节。

== 文章日期

`config.typ` 从构建脚本传入的 `page-path`（形如 `Blog/2025-12-31-标题`）里读取日期，自动在文章标题下渲染署名行。因此文章 `.typ` 不必写 `date:`；需要覆盖时传 `date: datetime(...)` 即可。
