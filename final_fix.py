#!/usr/bin/env python3
"""
最终修复：处理所有剩余的编译错误
"""

import re
from pathlib import Path

BLOG_DIR = Path("content/Blog")

def fix_angle_brackets(content):
    """转义所有的 < 和 > 字符"""
    # 将所有 < 和 > 替换为转义形式
    # 但要避免破坏已有的链接 #link("...")[...]

    lines = []
    for line in content.split('\n'):
        # 如果是链接行或标题行，跳过
        if '#link(' in line or line.strip().startswith('#'):
            lines.append(line)
            continue

        # 转义 < 和 >
        line = line.replace('<', '\\<')
        line = line.replace('>', '\\>')
        lines.append(line)

    return '\n'.join(lines)

def fix_escaped_angle_brackets(content):
    """移除已转义的 < 和 >（因为我们会在上面重新处理）"""
    # 这个函数先不使用，让 fix_angle_brackets 统一处理
    return content

def fix_hash_in_code(content):
    """修复代码块中的 # 字符问题"""
    lines = content.split('\n')
    result = []

    for line in lines:
        # 跳过 Typst 命令行
        if line.strip().startswith('#link(') or line.strip().startswith('#image(') or line.strip().startswith('#block'):
            result.append(line)
            continue

        # 在列表项中，如果行首有单独的 #，可能是 Markdown 的残留
        # 需要删除或转义
        if re.match(r'^\d+\.\s*#\s+\w', line):
            line = re.sub(r'^\s*#\s+', ' ', line)

        result.append(line)

    return '\n'.join(result)

def fix_file(file_path):
    """修复单个文件"""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        # 按顺序应用修复
        content = fix_hash_in_code(content)
        content = fix_angle_brackets(content)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主程序"""
    print("Final fix for remaining compilation errors...")

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
