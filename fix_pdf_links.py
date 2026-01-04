#!/usr/bin/env python3
"""
修复博客文章中的 PDF 文件链接路径

将所有 PDF 链接从 #link("xxx.pdf") 修改为 #link("imgs/xxx.pdf")
因为 PDF 文件实际存储在 imgs/ 子目录中。
"""

import re
from pathlib import Path

BLOG_DIR = Path("content/Blog")

def fix_pdf_links(file_path):
    """
    修复 PDF 链接路径，添加 imgs/ 前缀

    参数:
        file_path: index.typ 文件路径

    返回:
        bool: 是否进行了修改
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        # 匹配 #link("xxx.pdf") 格式，保持后面的内容（如 [text]）不变
        # 排除: 包含 / 的路径、http:// 或 https:// 开头的链接
        # 使用 lookbehind 保持 URL 后面的内容
        def replace_link(match):
            url = match.group(1)
            # 如果已经包含 imgs/ 或是外部链接，不替换
            if "/" in url or url.startswith("http"):
                return match.group(0)
            return f'#link("imgs/{url}")'

        pattern = r'#link\("([^"]+\.pdf)"\)'
        content = re.sub(pattern, replace_link, content)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"❌ 错误: {file_path} - {e}")
        return False

def main():
    """主程序"""
    print("开始修复 PDF 文件链接...")
    print(f"扫描目录: {BLOG_DIR}")
    print()

    fixed_count = 0
    checked_count = 0

    for index_file in BLOG_DIR.rglob("index.typ"):
        checked_count += 1
        if fix_pdf_links(index_file):
            print(f"✅ 修复: {index_file.relative_to(BLOG_DIR)}")
            fixed_count += 1

    print()
    print(f"扫描了 {checked_count} 个文件")
    print(f"修复了 {fixed_count} 个文件")

    if fixed_count > 0:
        print()
        print("下一步:")
        print("  1. 运行: python build.py build --force")
        print("  2. 运行: python build.py preview")
        print("  3. 在浏览器中测试 PDF 链接")
        print("  4. 提交: git add . && git commit -m '修复 PDF 文件链接路径' && git push")

if __name__ == "__main__":
    main()
