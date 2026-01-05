#!/usr/bin/env python3
"""
移除所有 Markdown 星号标记（* 和 **）
"""

import re
from pathlib import Path

BLOG_DIR = Path("content/Blog")

def remove_all_asterisks(content):
    """移除所有星号标记"""
    # 移除所有 ** 粗体标记
    content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)

    # 移除所有 * 斜体标记
    content = re.sub(r'\*(.+?)\*', r'\1', content)

    # 移除剩余的单独 * 字符（转义的或未转义的）
    content = content.replace('\\*', '')
    content = content.replace('*', '')

    return content

def fix_file(file_path):
    """修复单个文件"""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        # 移除所有星号标记
        content = remove_all_asterisks(content)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主程序"""
    print("Removing all asterisk markers...")

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
