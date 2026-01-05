#!/usr/bin/env python3
"""
修复双反斜杠和未闭合的星号标记
"""

import re
from pathlib import Path

BLOG_DIR = Path("content/Blog")

def fix_double_backslash(content):
    """修复双反斜杠问题 \\* -> \*"""
    content = content.replace('\\*', '*')  # 先移除所有转义
    return content

def fix_asterisks_properly(content):
    """正确处理星号标记 - 将所有 * 转义"""
    # 保护正确的 ** 粗体标记
    lines = []
    for line in content.split('\n'):
        # 跳过代码块
        if line.strip().startswith('```'):
            lines.append(line)
            continue

        # 跳过标题行
        if line.strip().startswith('='):
            lines.append(line)
            continue

        # 转义所有单独的 * 字符
        # 策略：将所有 * 替换为 \*，但保护 ** 模式
        line = re.sub(r'(?<!\\)\*(?!\*)', r'\\*', line)
        line = re.sub(r'(?<!\\)\*(?!\*)', r'\\*', line)  # 再次确保

        lines.append(line)

    return '\n'.join(lines)

def fix_file(file_path):
    """修复单个文件"""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        # 先移除双反斜杠
        content = fix_double_backslash(content)
        # 然后正确转义星号
        content = fix_asterisks_properly(content)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主程序"""
    print("Fixing double backslash and asterisk issues...")

    fixed_count = 0
    error_count = 0

    for index_file in BLOG_DIR.rglob("index.typ"):
        try:
            if fix_file(index_file):
                print(f"[OK] Fixed: {index_file.relative_to(BLOG_DIR)}")
                fixed_count += 1
        except Exception as e:
            print(f"[ERROR] {index_file.relative_to(BLOG_DIR)}: {e}")
            error_count += 1

    print(f"\nSummary:")
    print(f"  Fixed: {fixed_count} files")
    print(f"  Errors: {error_count} files")

if __name__ == "__main__":
    main()
