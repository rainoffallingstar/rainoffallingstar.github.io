#!/usr/bin/env python3
"""
修复代码块格式问题
"""

import re
from pathlib import Path

BLOG_DIR = Path("content/Blog")

def fix_code_blocks(content):
    """修复代码块格式"""
    lines = content.split('\n')
    result = []
    in_code_block = False
    code_lang = ''

    for line in lines:
        # 检测 Markdown 代码块开始 ~~~
        if line.strip() == '~~~':
            if not in_code_block:
                in_code_block = True
                result.append('#block.raw(')
            else:
                in_code_block = False
                result.append(')')
            continue

        # 在代码块内，直接添加内容
        if in_code_block:
            result.append(line)
        else:
            result.append(line)

    return '\n'.join(result)

def fix_inline_code_in_imports(content):
    """修复 import 语句中的链接格式"""
    # 修复 `import #link("...")[name]` 格式
    # 改为正确的 `import name from "link"`

    # 这种格式在 Python 代码示例中是注释，不应该转换为 Typst 链接
    # 先保护代码块
    lines = content.split('\n')
    result = []
    in_code_block = False

    for line in lines:
        if '#block.raw(' in line or line.strip() == '~~~':
            in_code_block = True
        elif line.strip() == ')' and in_code_block:
            in_code_block = False

        # 在代码块中不处理链接
        if in_code_block or line.strip().startswith('#block.raw('):
            result.append(line)
        else:
            result.append(line)

    return '\n'.join(result)

def fix_file(file_path):
    """修复单个文件"""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        # 按顺序应用修复
        content = fix_code_blocks(content)
        content = fix_inline_code_in_imports(content)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主程序"""
    print("Fixing code block formatting...")

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
