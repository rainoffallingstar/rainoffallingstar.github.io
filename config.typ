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
#import "tufted-lib/byline.typ": article-byline

// ---------------------------------------------------------------------------
// 站点信息
// ---------------------------------------------------------------------------

#let site-title = "rainoffallingstar’s Blog"
// 页头只放一个短名（参考站的 wordmark 风格）；SEO 与 RSS 仍用 site-title
#let site-wordmark = "rainoffallingstar"
#let site-tagline = "凡是过往，皆为序章。"
#let site-author = "rainoffallingstar"
#let site-url = "https://blog.rainoffallingstar.com"
#let site-description = "笔记、阅读报告与旧存档。凡是过往，皆为序章。"

// 站名前的圆形标记。图片在 assets/logo.jpg，favicon.ico 是同一张图更紧的
// 头像裁切（16px 下也认得出）。alt 留空：紧随其后的文字已经是站名，
// 读屏软件不必把图片再念一遍。
#let site-logo = html.img(
  src: "/assets/logo.jpg",
  alt: "",
  class: "site-logo",
  width: 34,
  height: 34,
  decoding: "async",
)

// 第一项是站名（兼作返回首页），其余是栏目
#let header-links = (
  "/": { site-logo; site-wordmark },
  "/Timeline/": "时间线",
  "/Links/": "友链",
  "/About/": "关于",
)

// 首页导语：站名下方那一段说明文字
#let site-intro = "这里记录读过的书、写过的笔记，以及一些被时间筛过的旧稿。"

// 首页「最近更新」展示的篇数
#let site-latest-count = 10

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
    html.div(
      class: "footer-inner",
      {
        html.div(
          class: "footer-meta",
          {
            html.span[© #datetime.today().year() #site-author]
            html.span(class: "footer-sep")[·]
            html.span([
              由 #link("https://github.com/Yousa-Mirage/Tufted-Blog-Template")[Tufted-Blog-Template] 驱动
            ])
          },
        )
        html.a(
          class: "footer-rss",
          href: "/feed.xml",
          {
            html.span(class: "footer-rss-icon", "")
            html.span("RSS 订阅")
          },
        )
      },
    ),
  ),
  // 上游样式之后追加站点视觉层；自托管手写字体由 fonts.css 声明
  css: ("/assets/fonts.css", "/assets/custom.css", "/assets/site.css"),
  // 本站自有脚本（页头滚动状态）
  js-scripts: ("/assets/site.js",),
)

// 文章日期从构建脚本传入的 page-path 里取（目录名形如 2025-12-31-标题），
// 这样每篇文章不必在 .typ 里重复写日期。
#let page-path = sys.inputs.at("page-path", default: "")
#let page-date = {
  let m = page-path.match(regex("\d{4}-\d{2}-\d{2}"))
  if m == none { none } else { m.text }
}

#let template(
  title: "",
  lang: "zh",
  date: none,
  description: none,
  extra-info: none,
  hero: none,
  intro: none,
  content,
) = {
  let date = if date != none { date } else { page-date }

  // 文章署名：上游只在一级标题（HTML 的 h2）后插入署名，
  // 而本站文章惯用 `== 标题`（h3），所以这里补一条二级标题的规则。
  let byline-injected = state("site-byline", false)
  show heading.where(level: 2): it => {
    it
    context {
      if date != none and not byline-injected.get() {
        byline-injected.update(true)
        article-byline(author: site-author, date: date, extra-info: extra-info)
      }
    }
  }

  let body = {
    if hero != none {
      html.elem("div", attrs: (class: "hero"), {
        html.elem("h1", attrs: (class: "hero-title"), hero.title)
        if hero.at("subtitle", default: none) != none {
          html.elem("p", attrs: (class: "hero-tagline"), hero.subtitle)
        }
      })
    }
    if intro != none {
      html.elem("p", attrs: (class: "intro"), intro)
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

// ---------------------------------------------------------------------------
// 首页「最近更新」
//
// posts 与 /Timeline/ 共用 content/_data/posts.typ。这里按日期取最新的
// site-latest-count 篇，用与时间线相同的 blog-entry 排布，末尾给一个去往
// 完整时间线的入口。
// ---------------------------------------------------------------------------

#let latest-posts(posts) = {
  // 日期是补零的 YYYY-MM-DD，按字符串排序即按时间排序；sorted 没有
  // descending 参数，降序用 rev()
  let sorted = posts.sorted(key: post => post.date).rev()
  let latest = sorted.slice(0, calc.min(site-latest-count, sorted.len()))

  html.elem("section", attrs: (class: "recent-posts"), {
    html.elem("h2", attrs: (class: "recent-heading"), "最近更新")
    for post in latest {
      tufted.blog-entry(
        date: post.date.slice(5).replace("-", "."),
        path: post.href,
        title: post.title,
      )
    }
    html.div(
      class: "recent-more",
      html.a(href: "/Timeline/", "查看全部时间线 →"),
    )
  })
}
