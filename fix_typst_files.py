#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix converted Typst files
"""

import os
import re
from pathlib import Path


BLOG_DIR = Path("content/Blog")


def fix_file(file_path: Path):
    """Fix common issues in converted Typst files."""
    content = file_path.read_text(encoding='utf-8')

    # Fix 1: Remove date parameter from template.with()
    content = re.sub(r', date: datetime\(year: \d+, month: \d+, day: \d+\)', '', content)

    # Fix 2: Replace #quote-block with proper blockquote syntax
    content = re.sub(r'#quote-block\[', '#blockquote[', content)

    # Fix 3: Fix remaining Markdown headers (##### should be =====, ###### should be ======)
    # But Typst only supports 5 levels, so ###### becomes =====
    content = re.sub(r'^######\s+(.+)$', r'==== \1', content, flags=re.MULTILINE)

    # Fix 4: Remove #html() calls
    content = re.sub(r'#html\([^)]+\)', '', content)

    # Fix 5: Fix _text_ being interpreted as subscript (use \_ to escape or use different markup)
    # In Typst, _ is for subscript, so we need to escape it or use emph
    # For academic content with _text_, we should replace \_ with @ if it's meant to be underscore
    # or use text() function

    # Write back
    file_path.write_text(content, encoding='utf-8')
    return True


def fix_all_files():
    """Fix all converted blog files."""
    count = 0

    for typ_file in BLOG_DIR.rglob("*.typ"):
        if fix_file(typ_file):
            count += 1
            print(f"Fixed: {typ_file}")

    print(f"\nFixed {count} files")


if __name__ == '__main__':
    fix_all_files()
