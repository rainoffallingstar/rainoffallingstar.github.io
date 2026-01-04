#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix all remaining Typst syntax issues
"""

import re
from pathlib import Path


BLOG_DIR = Path("content/Blog")


def fix_file(file_path: Path):
    """Fix all common issues."""
    content = file_path.read_text(encoding='utf-8')
    original = content

    # Fix 1: Remove categories parameter (not supported by tufted template)
    content = re.sub(r', categories:\s*\([^)]+\)', '', content)

    # Fix 2: Replace #blockquote with proper quote syntax
    content = re.sub(r'#blockquote\[', '#quote-block[', content)

    # Fix 3: Fix escaped ## (from fix_comments.py) back to ==
    content = re.sub(r'\\## ', '== ', content)

    # Fix 4: Fix escaped # followed by text (these should just be regular lines)
    content = re.sub(r'^\\# +(.+)$', r'\1', content, flags=re.MULTILINE)

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
