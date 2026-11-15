/**
 * 站点级交互补充（本站自有，不随上游模板同步）。
 *
 * 上游只提供主题切换、目录、返回顶部等；这里补一个页头滚动状态：
 * 页面离开顶部后给吸顶导航加一条极细的分隔线，避免内容与导航糊在一起。
 */
(() => {
  function init() {
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

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
