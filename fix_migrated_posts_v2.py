#!/usr/bin/env python3
"""
深度修复迁移后的博客文章中的 Typst 语法错误
"""

import re
from pathlib import Path

BLOG_DIR = Path("content/Blog")

def fix_angle_brackets(content):
    """修复尖括号问题（Typst 将 <...> 解释为 label）"""
    # 将所有 < 和 > 转义
    content = content.replace('<', '\\<')
    content = content.replace('>', '\\>')
    return content

def fix_markdown_headings_in_content(content):
    """修复内容中残留的 Markdown 标题"""
    lines = content.split('\n')
    result = []

    for line in lines:
        # 修复 == ### 模式（重复的标题标记）
        if re.match(r'^==\s+###', line):
            line = re.sub(r'^==\s+###\s*', '== ', line)
        elif re.match(r'^==\s+####', line):
            line = re.sub(r'^==\s+####\s*', '=== ', line)

        result.append(line)

    return '\n'.join(result)

def fix_italic_asterisks(content):
    """修复斜体星号问题（*文本*）"""
    # 移除未闭合的 * 标记
    # 匹配 *\* 模式并转换为普通文本
    content = re.sub(r'\\\*\*', '**', content)  # 恢复转义的 **

    # 移除行尾的 ** 或 *
    lines = content.split('\n')
    result = []

    for line in lines:
        # 跳过标题行
        if line.strip().startswith('='):
            result.append(line)
            continue

        # 移除行尾未闭合的 * 或 **
        line = re.sub(r'\*+$', '', line)

        result.append(line)

    return '\n'.join(result)

def fix_complex_patterns(content):
    """修复复杂模式"""
    # 修复 *\* 模式（转义+斜体的组合）
    content = re.sub(r'\\\*\\\*', '*', content)
    content = re.sub(r'\\\*', '*', content)

    return content

def fix_raw_markdown_tables(content):
    """处理原始 Markdown 表格（可能需要转换为纯文本）"""
    # 简单策略：将表格中的 <br/> 替换为换行符
    content = content.replace('<br/>', '\n')

    return content

def fix_file(file_path):
    """修复单个文件"""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        # 按顺序应用修复
        content = fix_markdown_headings_in_content(content)
        content = fix_angle_brackets(content)
        content = fix_italic_asterisks(content)
        content = fix_complex_patterns(content)
        content = fix_raw_markdown_tables(content)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主程序"""
    print("Starting deep fix of migrated posts...")

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
