// 主题切换功能 - 简化版
(function () {
  "use strict";

  console.log("Theme toggle script loaded");

  // 等待 DOM 加载完成
  function initThemeToggle() {
    const themeToggle = document.getElementById("theme-toggle");
    console.log("Looking for theme-toggle button:", themeToggle);

    if (!themeToggle) {
      console.log("Button not found, retrying...");
      setTimeout(initThemeToggle, 100);
      return;
    }

    console.log("Button found, initializing...");

    // 从 localStorage 读取主题偏好
    let currentTheme = localStorage.getItem("theme");

    // 如果没有保存的主题，使用系统偏好
    if (!currentTheme) {
      const systemPrefersDark = window.matchMedia(
        "(prefers-color-scheme: dark)",
      ).matches;
      currentTheme = systemPrefersDark ? "dark" : "light";
    }

    // 应用主题函数
    function applyTheme(theme) {
      console.log("Applying theme:", theme);
      document.documentElement.setAttribute("data-theme", theme);

      // 更新按钮图标
      if (theme === "dark") {
        themeToggle.textContent = "☀️";
        themeToggle.title = "切换到浅色模式";
      } else {
        themeToggle.textContent = "🌙";
        themeToggle.title = "切换到深色模式";
      }
    }

    // 初始化主题
    applyTheme(currentTheme);

    // 移除旧的事件监听器（如果有）
    const newButton = themeToggle.cloneNode(true);
    themeToggle.parentNode.replaceChild(newButton, themeToggle);

    // 添加点击事件
    newButton.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();

      const currentTheme =
        document.documentElement.getAttribute("data-theme") || "light";
      const newTheme = currentTheme === "dark" ? "light" : "dark";

      console.log(
        "Toggle clicked, switching from",
        currentTheme,
        "to",
        newTheme,
      );

      applyTheme(newTheme);
      localStorage.setItem("theme", newTheme);
    });

    console.log("Theme toggle initialized successfully");
  }

  // 页面加载完成后初始化
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initThemeToggle);
  } else {
    initThemeToggle();
  }
})();
