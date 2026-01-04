// 主题切换功能
(function() {
  'use strict';

  const themeToggle = document.getElementById('theme-toggle');
  if (!themeToggle) return;

  // 从 localStorage 读取主题偏好，默认使用系统偏好
  const savedTheme = localStorage.getItem('theme');
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  // 确定当前主题（保存的优先，其次使用系统偏好）
  let currentTheme = savedTheme;
  if (!currentTheme) {
    currentTheme = systemPrefersDark ? 'dark' : 'light';
  }

  // 应用主题
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    updateButtonIcon(theme);
  }

  // 更新按钮图标和提示
  function updateButtonIcon(theme) {
    if (theme === 'dark') {
      themeToggle.textContent = '☀️';
      themeToggle.title = '切换到浅色模式';
    } else {
      themeToggle.textContent = '🌙';
      themeToggle.title = '切换到深色模式';
    }
  }

  // 切换主题
  themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  });

  // 初始化主题
  applyTheme(currentTheme);

  // 监听系统主题变化（如果用户没有手动设置过）
  if (!savedTheme) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      const newTheme = e.matches ? 'dark' : 'light';
      applyTheme(newTheme);
    });
  }
})();
