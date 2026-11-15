// ============================================================================
// 站点配置 / Site configuration
//
// 模板实现来自上游 Tufted-Blog-Template（tufted-lib/），这里只做站点定制：
//   #import "../config.typ": template, tufted
//   #show: template.with(title: "页面标题")
//
// 视觉样式见 assets/site.css。
// ============================================================================

#import "tufted-lib/tufted.typ" as tufted

// ---------------------------------------------------------------------------
// 站点信息
// ---------------------------------------------------------------------------

#let site-title = "rainoffallingstar’s Blog"
#let site-tagline = "凡是过往，皆为序章。"
#let site-author = "rainoffallingstar"
#let site-url = "https://blog.rainoffallingstar.com"
#let site-description = "笔记、阅读报告与旧存档。凡是过往，皆为序章。"

// 第一项是站名（兼作返回首页），其余是栏目
#let header-links = (
  "/": site-title,
  "/Links/": "友链",
  "/About/": "关于",
)

// ---------------------------------------------------------------------------
// 站点外壳
//
// 直接复用上游 tufted-web：它负责 SEO 元数据、RSS 发现链接、导航、
// 目录、返回顶部、公式复制、代码块等全部基础设施。
// 这里额外包一层，用于注入首页的 hero 区（上游没有这个概念）。
// ---------------------------------------------------------------------------

#let site = tufted.tufted-web.with(
  header-links: header-links,
  website-title: site-title,
  website-url: site-url,
  author: site-author,
  description: site-description,
  favicon: "/assets/favicon.ico",
  lang: "zh",
  // 生成 feed.xml，并在导航栏显示 RSS 图标
  feed-dir: ("/Blog/",),
  footer-elements: (
    [© #datetime.today().year() #site-author],
    [
      Powered by #link("https://github.com/Yousa-Mirage/Tufted-Blog-Template")[Tufted-Blog-Template]
    ],
  ),
  // 上游样式之后追加站点视觉层
  css: ("/assets/custom.css", "/assets/site.css"),
  // 本站自有脚本（页头滚动状态）
  js-scripts: ("/assets/site.js",),
)

#let template(
  title: "",
  lang: "zh",
  date: none,
  description: none,
  extra-info: none,
  hero: none,
  content,
) = {
  let body = {
    if hero != none {
      html.elem("div", attrs: (class: "hero"), {
        html.elem("h1", attrs: (class: "hero-title"), hero.title)
        if hero.at("subtitle", default: none) != none {
          html.elem("p", attrs: (class: "hero-tagline"), hero.subtitle)
        }
      })
    }
    content
  }

  show: site.with(
    title: title,
    lang: lang,
    date: date,
    description: if description == none { site-description } else { description },
    extra-info: extra-info,
  )
  body
}

// ---------------------------------------------------------------------------
// 首页归档
//
// posts 为 (date: "YYYY-MM-DD", title: "...", href: "/Blog/.../") 的数组。
// 按年份分组，条目使用上游的 tufted.blog-entry（日期列 + 标题列）。
// ---------------------------------------------------------------------------

#let archive(posts) = {
  let years = ()
  let groups = (:)
  for post in posts {
    let year = post.date.slice(0, 4)
    if year not in groups {
      groups.insert(year, ())
      years.push(year)
    }
    groups.at(year).push(post)
  }

  for year in years {
    html.elem("section", attrs: (class: "year-group"), {
      html.elem("h2", attrs: (class: "year"), year)
      for post in groups.at(year) {
        tufted.blog-entry(
          date: post.date.slice(5).replace("-", "."),
          path: post.href,
          title: post.title,
        )
      }
    })
  }
}
