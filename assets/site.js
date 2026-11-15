/**
 * 站点级交互补充（本站自有，不随上游模板同步）。
 *
 * 上游已经提供了主题切换、目录、返回顶部等；这里只补三件事：
 *
 * 1. 页头滚动状态：页面离开顶部后给导航加一条极细的分隔线。
 * 2. 导航的当前栏目标记：上游不输出 aria-current，这里按 URL 补上，
 *    样式见 site.css 的 .site-nav-links a[aria-current="page"]。
 * 3. 主题切换的圆形揭示：上游 theme-toggle.js 直接改 data-theme，
 *    没有动画。这里在捕获阶段拦下按钮点击，用 View Transitions
 *    从点击位置做一次圆形扩散，动画中间再「重放」一次点击，
 *    让上游继续负责存储、aria 与系统同步 —— 本站不复制它的逻辑。
 */
(() => {
  const root = document.documentElement;

  /* ----------------------------------------------------------------------
     1. 页头滚动状态
     ---------------------------------------------------------------------- */

  function initHeader() {
    const header = document.querySelector("header.site-header:not(:empty)");
    if (!header) return;

    let ticking = false;
    function sync() {
      header.classList.toggle("is-scrolled", window.scrollY > 4);
      ticking = false;
    }

    sync();
    window.addEventListener(
      "scroll",
      () => {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(sync);
      },
      { passive: true },
    );
  }

  /* ----------------------------------------------------------------------
     2. 导航的当前栏目标记

     首页精确匹配 "/"，其余栏目按「路径前缀」匹配，这样 /Timeline/、
     /Blog/xxx/ 之类都能归到正确的栏目。
     ---------------------------------------------------------------------- */

  function initCurrentNav() {
    const links = document.querySelectorAll(".site-nav-links a[href]");
    if (!links.length) return;

    const path = window.location.pathname;
    let best = null;
    let bestLength = -1;

    links.forEach((link) => {
      const href = new URL(link.href, window.location.origin).pathname;
      const isHome = href === "/";
      const matches = isHome ? path === "/" : path.startsWith(href);
      if (matches && href.length > bestLength) {
        best = link;
        bestLength = href.length;
      }
    });

    // 首项是站名，不当作栏目标记
    if (best && best !== links[0]) {
      best.setAttribute("aria-current", "page");
    }
  }

  /* ----------------------------------------------------------------------
     3. 主题切换的圆形揭示
     ---------------------------------------------------------------------- */

  function prefersReducedMotion() {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function setOrigin(x, y) {
    const radius = Math.hypot(
      Math.max(x, window.innerWidth - x),
      Math.max(y, window.innerHeight - y),
    );
    root.style.setProperty("--theme-x", `${x}px`);
    root.style.setProperty("--theme-y", `${y}px`);
    root.style.setProperty("--theme-radius", `${radius}px`);
  }

  function initThemeReveal() {
    if (!document.startViewTransition) return;

    // 重放点击时避免再次进入本拦截逻辑
    let replaying = false;

    document.addEventListener(
      "click",
      (event) => {
        const button = event.target.closest?.("#theme-toggle");
        if (!button || replaying) return;
        if (prefersReducedMotion()) return;

        // 键盘触发时没有坐标，退化为按钮中心
        const rect = button.getBoundingClientRect();
        const x = event.detail === 0 ? rect.left + rect.width / 2 : event.clientX;
        const y = event.detail === 0 ? rect.top + rect.height / 2 : event.clientY;
        setOrigin(x, y);

        // 阻止上游立即切换，改由 View Transition 包裹
        event.stopPropagation();
        event.preventDefault();

        root.classList.add("is-theme-transitioning");
        const transition = document.startViewTransition(() => {
          replaying = true;
          button.click();
          replaying = false;
        });
        transition.finished.finally(() => {
          root.classList.remove("is-theme-transitioning");
        });
      },
      true,
    );
  }

  /* ----------------------------------------------------------------------
     启动
     ---------------------------------------------------------------------- */

  function init() {
    initHeader();
    initCurrentNav();
    initThemeReveal();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
