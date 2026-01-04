#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix comment markers (#) at start of lines in Typst files
"""

import re
from pathlib import Path


BLOG_DIR = Path("content/Blog")


def fix_file(file_path: Path) -> bool:
    """Fix # comment markers that should be escaped."""
    content = file_path.read_text(encoding='utf-8')
    original = content

    lines = []
    for line in content.split('\n'):
        stripped = line.strip()
        # If line starts with # but is not a Typst command
        if stripped.startswith('#') and not any(stripped.startswith(cmd) for cmd in [
            '#=', '#==', '#===', '#====', '#=====', '#======',  # headers
            '#import', '#show', '#link', '#image', '#let',      # commands
            '#blockquote', '#footnote', '#figure',              # functions
            '```',                                            # code block
        ]):
            # Escape the #
            line = re.sub(r'^(\s*)#', r'\1\\#', line)
        lines.append(line)

    content = '\n'.join(lines)

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
