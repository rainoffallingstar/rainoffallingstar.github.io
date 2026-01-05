#!/usr/bin/env python3
"""
终极修复：处理所有 Markdown 残留语法
"""

import re
from pathlib import Path

BLOG_DIR = Path("content/Blog")

def fix_markdown_headers(content):
    """修复所有 Markdown 标题格式"""
    lines = content.split('\n')
    result = []

    for line in lines:
        # 修复 ##### (5个#) -> =====
        if re.match(r'^#####\s+', line):
            line = re.sub(r'^#####\s+', '===== ', line)
        # 修复 ###### (6个#) -> ======
        elif re.match(r'^######\s+', line):
            line = re.sub(r'^######\s+', '====== ', line)
        # 修复 #### (4个#) -> ====
        elif re.match(r'^####\s+', line):
            line = re.sub(r'^####\s+', '==== ', line)

        result.append(line)

    return '\n'.join(result)

def fix_inline_comments(content):
    """修复行尾的 # 注释"""
    lines = content.split('\n')
    result = []

    for line in lines:
        # 如果行尾有 # 后跟文字，将其改为文本
        # 但不要破坏 #link 或 #image 等命令
        if '#' in line and not '#link(' in line and not '#image(' in line and not '#block' in line:
            # 查找行尾的 # 注释
            match = re.search(r'\s+#\s+[^\s#]', line)
            if match:
                # 将 # 后的内容保持，但移除 #
                line = re.sub(r'\s+#\s+', ' — ', line)

        result.append(line)

    return '\n'.join(result)

def fix_file(file_path):
    """修复单个文件"""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        # 按顺序应用修复
        content = fix_markdown_headers(content)
        content = fix_inline_comments(content)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主程序"""
    print("Ultimate fix for Markdown remnants...")

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
