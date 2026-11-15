#import "../index.typ": template, tufted
#show: template.with(title: "自定义样式")

= 自定义样式

网站的视觉外观由 CSS 控制，字体、字号、颜色与栅格都无法在 Typst 中直接修改。如需调整，请修改 `assets/` 下的样式表。

== 样式表加载顺序

模板按以下顺序加载样式，后加载的规则覆盖先加载的：

+ `tufte.min.css` —— 来自 CDN 的 Tufte 基础排版
+ `/assets/tufted.css` —— 模板功能层（栅格、代码块、表格、目录、归档条目）
+ `/assets/theme.css` —— 明暗主题变量与切换按钮图标
+ `/assets/custom.css` —— 留给使用者的覆盖入口（本站为空）
+ `/assets/site.css` —— 本站视觉层（配色、字体、页头、归档列表）

=== 各文件职责

- `assets/tufted.css`、`assets/theme.css`：由上游模板维护，**不建议直接改**，否则下次同步会被覆盖。
- `assets/custom.css`：留给使用者的覆盖入口，位于 `site.css` 之前。
- `assets/site.css`：本站的全部定制。改配色、字体、间距、悬停效果都在这里。

== 设计令牌

`site.css` 顶部集中管理配色与字体，并且**同时映射到上游的 `--theme-*` 变量**，这样目录、返回顶部、代码块、页脚等上游组件会自动采用本站配色：

```css
html[data-theme="light"] {
    --paper: #fbfaf6;      /* 纸张底色 */
    --ink: #2b2a27;        /* 正文墨色 */
    --ink-muted: #6f6a5f;  /* 次级文字，5.15:1 */
    --ink-faint: #77726a;  /* 三级文字，4.57:1 */
    --rule: #e4dfd3;       /* 分隔线 */
    --accent: #2b4c7e;     /* 悬停点缀色 */

    /* 映射给上游组件 */
    --theme-bg: var(--paper);
    --theme-text: var(--ink);
    --theme-heading: var(--ink-strong);
    /* ... */
}
```

注意 `--column: 55%`：Tufte 的边注（`.marginnote`）靠负右边距悬挂在正文右侧的空白里，改动这个比例会让旁注错位。

== 深色模式

主题由上游的 `assets/scripts/theme-toggle.js` 控制：

- 优先级：`sessionStorage`（本次浏览会话的手动选择）> 系统的 `prefers-color-scheme`
- 手动切换只在当前会话内有效，新会话会重新跟随系统

本站只在 `site.css` 里提供 `html[data-theme="dark"]` 的变量值，不要再写 `@media (prefers-color-scheme: dark)` 覆盖颜色，否则手动切换会失效。

== 页头与归档

页头由上游 `tufted-web` 生成，结构为：

```text
header.site-header > nav.site-nav
  .site-nav-links   ← 导航项（首项为站名）
  .site-nav-tools   ← RSS 图标、主题切换按钮
```

导航项在 `config.typ` 的 `header-links` 中定义。图标由 CSS mask 绘制，颜色跟随 `--theme-icon`。

首页归档列表的数据在 `content/index.typ` 的 `posts` 数组里，每项形如：

```typst
(date: "2022-11-04", title: "Workflow Machine Learning with Radio-mics", href: "/Blog/.../"),
```

`config.typ` 的 `archive()` 会按年份分组，并用上游的 `tufted.blog-entry()` 渲染「日期列 + 标题列」。日期在标题中重复的前缀已剥离。
