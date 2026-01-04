#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix <中文> labels and underscore issues
"""

import re
from pathlib import Path


BLOG_DIR = Path("content/Blog")


def fix_file(file_path: Path):
    """Fix <中文> patterns and underscores."""
    content = file_path.read_text(encoding='utf-8')
    original = content

    # Fix 1: <中文> patterns - these are being parsed as link labels
    # Replace <中文> with just 中文 or escape angle brackets
    # Looking for patterns like <张怡微> and converting to just text
    content = re.sub(r'<([\u4e00-\u9fff\w]+)>', r'\1', content)

    # Fix 2: Unclosed delimiters from underscores
    # In academic notes, _word_ should be escaped as \_word\_
    # Look for standalone _text_ patterns (not part of Typst syntax)
    # This is tricky - we need to identify _ that are used for emphasis in Markdown
    # but not Typst's subscript syntax

    # For now, let's escape underscores that appear to be for emphasis
    # Pattern: _english_word_ or _mixed_ where it's likely Markdown emphasis
    # But be careful not to break actual Typst syntax

    # Simple heuristic: escape _ when surrounding alphanumeric text
    # that doesn't look like it's meant to be subscript
    content = re.sub(r'_([a-zA-Z][a-zA-Z0-9]*[a-zA-Z0-9])_', r'_\1_', content)

    # Also handle patterns like _word_ with Chinese characters around
    # content = re.sub(r'([^\s])_([\w]+)_([^\s])', r'\1_\2_\3', content)

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
