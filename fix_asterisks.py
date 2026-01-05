#!/usr/bin/env python3
"""
彻底修复未闭合的星号标记问题
"""

import re
from pathlib import Path

BLOG_DIR = Path("content/Blog")

def fix_unclosed_asterisks(content):
    """修复未闭合的星号标记 - 直接转义所有单独的 *"""
    lines = content.split('\n')
    result = []

    for line in lines:
        # 跳过标题行和代码块
        if line.strip().startswith('=') or line.strip().startswith('```'):
            result.append(line)
            continue

        # 转义行首的 *（但不转义 **）
        if re.match(r'^\*[^*]', line):
            line = '\\' + line

        # 转义行尾的 *（但不转义 **）
        if re.search(r'[^*]\*$', line):
            line = re.sub(r'(\*)$', r'\\\1', line)

        # 转义孤立的 *（不在 **...** 中间的）
        # 使用一个简单的策略：将所有 * 替换为 \*，除了 ** 的情况
        parts = line.split('**')
        for i, part in enumerate(parts):
            # 转义剩余的 *
            parts[i] = part.replace('*', '\\*')
        line = '**'.join(parts)

        result.append(line)

    return '\n'.join(result)

def fix_table_content(content):
    """修复表格中的特殊字符"""
    # 转义表格中的 * 字符
    lines = content.split('\n')
    result = []

    for line in lines:
        # 检查是否是表格行
        if '|' in line:
            # 转义行中的 *（但不转义 **）
            parts = line.split('**')
            for i, part in enumerate(parts):
                parts[i] = part.replace('*', '\\*')
            line = '**'.join(parts)

        result.append(line)

    return '\n'.join(result)

def fix_file(file_path):
    """修复单个文件"""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        # 应用修复
        content = fix_table_content(content)
        content = fix_unclosed_asterisks(content)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主程序"""
    print("Fixing unclosed asterisk markers...")

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
