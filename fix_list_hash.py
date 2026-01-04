#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix list items starting with + # pattern
"""

import re
from pathlib import Path


BLOG_DIR = Path("content/Blog")


def fix_file(file_path: Path):
    """Fix + # pattern in list items."""
    content = file_path.read_text(encoding='utf-8')
    original = content

    # Fix: + # text -> + \# text (in list items, # should be escaped)
    # This catches patterns where # appears after + in a list
    content = re.sub(r'^(\s*)\+\s+\\#', r'\1+ \\#', content, flags=re.MULTILINE)

    # Also fix: + # text -> + \\# text (if not already escaped)
    content = re.sub(r'^(\s*)\+\s+#(?!\\)', r'\1+ \\#', content, flags=re.MULTILINE)

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
