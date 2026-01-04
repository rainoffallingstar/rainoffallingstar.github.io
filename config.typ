#import "@preview/tufted:0.1.0"

#let template = tufted.tufted-web.with(
  // 网站导航栏
  header-links: (
    "/": "首页",
    "/Blog/": "博客",
    "/Links/": "友链",
    "/About/": "关于",
  ),
  lang: "zh",
  title: "rainoffallingstar's Blog",
)
