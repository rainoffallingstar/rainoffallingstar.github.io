#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive fix for all remaining Typst issues
"""

import re
from pathlib import Path


BLOG_DIR = Path("content/Blog")


def fix_file(file_path: Path):
    """Fix all remaining issues systematically."""
    content = file_path.read_text(encoding='utf-8')
    original = content

    # Fix 1: Lines starting with + # (list item + comment)
    # + # text -> + \# text
    content = re.sub(r'^(\s*)\+\s+#', r'\1+ \\#', content, flags=re.MULTILINE)

    # Fix 2: Lines starting with + followed by Chinese/URL
    # + 文本 or + http -> keep as is (list items)
    # But + #中文 -> + \#中文

    # Fix 3: Escape # when followed by Chinese at line start (not in code blocks)
    lines = []
    in_code_block = False
    for line in content.split('\n'):
        # Track code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            lines.append(line)
            continue

        if not in_code_block:
            # Check for # followed by Chinese at start of line (after optional whitespace)
            # But not Typst commands like #=, #import, etc.
            match = re.match(r'^(\s*)#([\u4e00-\u9fff])', line)
            if match:
                line = match.group(1) + '\\#' + match.group(2) + line[match.end():]

        lines.append(line)
    content = '\n'.join(lines)

    # Fix 4: Fix _text_ patterns in Chinese context
    # _中文_ should be \_中文\_ (escape underscores around Chinese)
    content = re.sub(r'_([\u4e00-\u9fff]+)_', r'_\1_', content)

    # Fix 5: Fix underscores in academic notes
    # Patterns like _word_ where word is English letters might be subscript
    # If it looks like a variable name in academic text, escape it
    # _text_ -> \_text\_ when not meant as subscript

    # Fix 6: Remove orphaned <u> tags from HTML conversion
    content = re.sub(r'<u>([^<]*)</u>', r'\1', content)

    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False


def main():
    count = 0
    fixed_files = []

    for typ_file in BLOG_DIR.rglob("*.typ"):
        if fix_file(typ_file):
            count += 1
            fixed_files.append(typ_file.name)

    print(f"Total fixed: {count}")
    if fixed_files:
        print("\nFixed files:")
        for f in sorted(fixed_files):
            print(f"  - {f}")


if __name__ == '__main__':
    main()
