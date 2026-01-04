#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Replace #quote-block with proper quote formatting
In Tufted, use blockquote or just indent text
"""

import re
from pathlib import Path


BLOG_DIR = Path("content/Blog")


def fix_file(file_path: Path):
    """Replace quote-block with proper syntax."""
    content = file_path.read_text(encoding='utf-8')
    original = content

    # Replace #quote-block[...] with simple text block
    # For Tufted style, we can just use the text directly or use a different approach
    # Simple approach: remove #quote-block and keep content, add spacing

    def replace_quote_block(match):
        inner_content = match.group(1)
        # Just return the content, Typst will handle it as regular text
        return '\n' + inner_content + '\n'

    content = re.sub(r'#quote-block\[([\s\S]*?)\]', replace_quote_block, content)

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
