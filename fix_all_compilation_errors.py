#!/usr/bin/env python3
"""
修复所有 Typst 编译错误
"""

import re
from pathlib import Path

BLOG_DIR = Path("content/Blog")

def fix_backslash_escapes(content):
    """删除不必要的反斜杠转义符"""
    # 删除 \> (转义的大于号)
    content = re.sub(r'\\>', '>', content)

    # 删除 \ 后跟空格、标点或中文
    content = re.sub(r'\\([ \u4e00-\u9fff.,;:!?()])', r'\1', content)

    # 保留必要的转义（\", \`, \\, \n, \r, \t）
    # 其他反斜杠删除
    lines = []
    for line in content.split('\n'):
        # 跳过代码块
        if line.strip().startswith('#block.raw') or line.strip().startswith('```'):
            lines.append(line)
            continue

        # 删除不必要的反斜杠
        fixed = re.sub(r'\\([^"\'`nrt])', r'\1', line)
        lines.append(fixed)

    return '\n'.join(lines)

def fix_fullwidth_chars(content):
    """替换全角字符为半角"""
    # 全角字母数字
    char_map = {
        '０': '0', '１': '1', '２': '2', '３': '3', '４': '4',
        '５': '5', '６': '6', '７': '7', '８': '8', '９': '9',
        'Ａ': 'A', 'Ｂ': 'B', 'Ｃ': 'C', 'Ｄ': 'D', 'Ｅ': 'E',
        'Ｆ': 'F', 'Ｇ': 'G', 'Ｈ': 'H', 'Ｉ': 'I', 'Ｊ': 'J',
        'Ｋ': 'K', 'Ｌ': 'L', 'Ｍ': 'M', 'Ｎ': 'N', 'Ｏ': 'O',
        'Ｐ': 'P', 'Ｑ': 'Q', 'Ｒ': 'R', 'Ｓ': 'S', 'Ｔ': 'T',
        'Ｕ': 'U', 'Ｖ': 'V', 'Ｗ': 'W', 'Ｘ': 'X', 'Ｙ': 'Y',
        'Ｚ': 'Z',
        'ａ': 'a', 'ｂ': 'b', 'ｃ': 'c', 'ｄ': 'd', 'ｅ': 'e',
        'ｆ': 'f', 'ｇ': 'g', 'ｈ': 'h', 'ｉ': 'i', 'ｊ': 'j',
        'ｋ': 'k', 'ｌ': 'l', 'ｍ': 'm', 'ｎ': 'n', 'ｏ': 'o',
        'ｐ': 'p', 'ｑ': 'q', 'ｒ': 'r', 'ｓ': 's', 'ｔ': 't',
        'ｕ': 'u', 'ｖ': 'v', 'ｗ': 'w', 'ｘ': 'x', 'ｙ': 'y',
        'ｚ': 'z',
        '＋': '+', '－': '-', '（': '(', '）': ')',
    }

    for full, half in char_map.items():
        content = content.replace(full, half)

    return content

def fix_footnote_refs(content):
    """删除 Markdown 脚注引用标记"""
    # 删除 [^] 模式
    content = re.sub(r'\[\^\]\s*', '', content)
    return content

def fix_code_blocks(content):
    """修复未闭合的代码块"""
    # 查找连续的 #block.raw(" 并修复
    lines = content.split('\n')
    result = []
    in_raw_block = False
    raw_block_count = 0

    for line in lines:
        if '#block.raw("' in line:
            if in_raw_block:
                # 这是一个错误：连续的 #block.raw(
                # 将第二个改为闭合 "
                line = line.replace('#block.raw("', '")')
                in_raw_block = False
                raw_block_count = 0
            else:
                in_raw_block = True
                raw_block_count += 1

        result.append(line)

    return '\n'.join(result)

def fix_file(file_path):
    """修复单个文件"""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        # 按顺序应用修复
        content = fix_backslash_escapes(content)
        content = fix_fullwidth_chars(content)
        content = fix_footnote_refs(content)
        content = fix_code_blocks(content)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主程序"""
    print("Fixing all compilation errors...")

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
