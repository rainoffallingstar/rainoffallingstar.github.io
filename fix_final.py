#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final fix for remaining Typst issues
"""

import re
from pathlib import Path


BLOG_DIR = Path("content/Blog")


def fix_file(file_path: Path):
    """Fix remaining issues."""
    content = file_path.read_text(encoding='utf-8')
    original = content

    # Fix 1: Escape # followed by Chinese characters at line start
    # #中文 -> \#中文 (but not for Typst commands)
    lines = []
    for line in content.split('\n'):
        stripped = line.strip()
        # Check if line starts with # followed by Chinese (not a Typst command)
        if stripped.startswith('#') and len(stripped) > 1:
            next_char = stripped[1] if len(stripped) > 1 else ''
            if '\u4e00' <= next_char <= '\u9fff':  # Chinese character
                line = re.sub(r'^(\s*)#', r'\1\\#', line)
        lines.append(line)
    content = '\n'.join(lines)

    # Fix 2: Fix _word_ patterns that should be literal underscores
    # In academic notes, things like _基因组_ should be escaped
    content = re.sub(r'_([\u4e00-\u9fff]+)_', r'_\1_', content)

    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False


def main():
    count = 0
    for typ_file in BLOG_DIR.rglob("*.typ"):
        if fix_file(typ_file):
            count += 1
            print(f"Fixed: {typ_file.name}")
    print(f"\nTotal fixed: {count}")


if __name__ == '__main__':
    main()
