#!/usr/bin/env python3
"""
修复迁移后的博客文章中的 Typst 语法错误
"""

import re
from pathlib import Path

BLOG_DIR = Path("content/Blog")

def fix_headings(content):
    """修复标题层级转换问题"""
    lines = content.split('\n')
    result = []

    for line in lines:
        # 修复 ##### 标题（应该是 ====）
        if line.startswith('##### '):
            line = line.replace('##### ', '==== ', 1)
        # 修复 ###### 标题（应该是 =====）
        elif line.startswith('###### '):
            line = line.replace('###### ', '===== ', 1)
        # 修复 ####### 标题（应该是 ======）
        elif line.startswith('####### '):
            line = line.replace('####### ', '====== ', 1)

        result.append(line)

    return '\n'.join(result)

def fix_asterisk_emphasis(content):
    """修复星号强调标记问题"""
    # 匹配行内单独的 * 标记（不是成对的 **）
    # 先保护已经正确的 **...** 模式
    content = re.sub(r'\*\*([^*]+?)\*\*', r'__BOLD__\1__BOLD__', content)

    # 修复未闭合的 * 标记 - 转义它们
    # 这里需要小心处理，避免破坏正确的标记
    lines = content.split('\n')
    result = []

    for line in lines:
        # 跳过标题行
        if line.strip().startswith('=') or line.strip().startswith('#'):
            result.append(line)
            continue

        # 计算行中 * 的数量
        asterisk_count = line.count('*')

        # 如果是奇数个 *，说明有未闭合的标记
        if asterisk_count % 2 != 0:
            # 转义所有未配对的 *
            # 简单策略：转义行中所有的 *
            line = line.replace('*', '\\*')

        result.append(line)

    content = '\n'.join(result)

    # 恢复 **...** 标记
    content = content.replace('__BOLD__', '*')

    return content

def fix_markdown_headings(content):
    """修复残留的 Markdown 标题格式（### 或 ####）"""
    lines = content.split('\n')
    result = []

    for line in lines:
        # 修复 ### 标题（转换为 ==）
        if re.match(r'^###\s+', line):
            line = re.sub(r'^###\s+', '== ', line)
        # 修复 #### 标题（转换为 ===）
        elif re.match(r'^####\s+', line):
            line = re.sub(r'^####\s+', '=== ', line)
        # 修复 ##### 标题（转换为 ====）
        elif re.match(r'^#####+\s+', line):
            hashes = len(re.match(r'^(#+)\s+', line).group(1))
            equals = '=' * (hashes - 1)
            line = re.sub(r'^#+\s+', equals + ' ', line)

        result.append(line)

    return '\n'.join(result)

def fix_math_notation(content):
    """修复数学公式中的星号问题"""
    # 将数学公式中的 * 转义
    # 例如：Vt*respiratory rate -> Vt\*respiratory rate
    # 但要避免破坏已经正确的 ** 粗体标记

    lines = content.split('\n')
    result = []

    for line in lines:
        # 检查是否包含数学公式的特征
        if any(pattern in line for pattern in ['=', '(', ')', '[', ']', '/', '+', '-', '<', '>']):
            # 如果行中包含 * 但不是 **（粗体），转义它
            if '*' in line and '**' not in line:
                line = line.replace('*', '\\*')
            # 如果行中包含 * 后面跟着字母或数字（乘法），转义它
            elif re.search(r'\*[\w\d]', line):
                line = re.sub(r'(?<!\*)\*(?!\*)', r'\\*', line)

        result.append(line)

    return '\n'.join(result)

def fix_unclosed_delimiters(content):
    """修复各种未闭合的分隔符"""
    # 修复 *** 标记（可能是粗体+斜体的错误写法）
    content = re.sub(r'\*\*\*(.+?)\*\*\*', r'*\1*', content)

    # 修复 \* 标记（转义的星号）
    content = content.replace('\\*', '*')

    # 修复连续的 * 号
    content = re.sub(r'\*{5,}', '', content)

    return content

def fix_file(file_path):
    """修复单个文件"""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        # 应用所有修复
        content = fix_markdown_headings(content)
        content = fix_headings(content)
        content = fix_asterisk_emphasis(content)
        content = fix_math_notation(content)
        content = fix_unclosed_delimiters(content)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主程序"""
    print("Starting to fix migrated posts...")

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
