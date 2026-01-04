#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jekyll Markdown to Tufted Blog Typst Converter

Converts Jekyll blog posts to Tufted Blog format.
Usage:
    python convert_jekyll_to_tufted.py --test       # Convert 5 posts for testing
    python convert_jekyll_to_tufted.py --full       # Convert all posts
    python convert_jekyll_to_tufted.py --post FILE  # Convert specific post
"""

import argparse
import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import unicodedata


# ============================================================================
# Configuration
# ============================================================================

POSTS_DIR = Path("_posts")
ASSETS_DIR = Path("posts")
OUTPUT_DIR = Path("content/Blog")
CONTENT_TEMPLATE = """#import "../index.typ": template, tufted
#show: template{metadata}

{content}
"""

# 中文检测阈值（超过30%中文字符视为中文内容）
CHINESE_THRESHOLD = 0.3


# ============================================================================
# Helper Functions
# ============================================================================


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    # Pinyin transliteration for Chinese would be ideal, but for now use simple approach
    text = text.lower()
    # Remove common Chinese punctuation
    text = re.sub(r'[，。、；：？！""''（）【】《》\s\-—–]+', '-', text)
    # Remove special characters except alphanumeric, hyphen, Chinese
    text = re.sub(r'[^\w\u4e00-\u9fff-]+', '', text)
    # Remove consecutive hyphens
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    return text if text else 'untitled'


def is_chinese_text(text: str) -> bool:
    """Check if text is primarily Chinese."""
    if not text:
        return False
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    total_chars = sum(1 for c in text if c.isalnum() or '\u4e00' <= c <= '\u9fff')
    return total_chars > 0 and (chinese_chars / total_chars) > CHINESE_THRESHOLD


def extract_date_from_filename(filename: str) -> Optional[Tuple[str, str, str]]:
    """Extract date from Jekyll post filename (YYYY-MM-DD-title.md)."""
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})-', filename)
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None


def get_post_info_from_frontmatter(content: str) -> Dict[str, str]:
    """Extract metadata from YAML front matter."""
    metadata = {}
    frontmatter_match = re.match(r'^---$(.+?)^---$', content, re.MULTILINE | re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        # Extract title
        title_match = re.search(r'title:\s*(.+)', frontmatter)
        if title_match:
            title = title_match.group(1).strip()
            # Remove quotes if present
            title = title.strip('"\'')
            metadata['title'] = title
        # Extract categories
        categories_match = re.search(r'categories:\s*\[(.+)\]', frontmatter)
        if categories_match:
            categories = [c.strip().strip('"\'') for c in categories_match.group(1).split(',')]
            metadata['categories'] = categories
        # Extract date if present
        date_match = re.search(r'date:\s*(\d{4}-\d{2}-\d{2})', frontmatter)
        if date_match:
            metadata['date'] = date_match.group(1)
    return metadata


# ============================================================================
# Conversion Functions
# ============================================================================


def convert_headers(text: str) -> str:
    """Convert Markdown headers to Typst."""
    # Jekyll uses ### for h3, #### for h4, etc.
    # Typst uses = for h1, == for h2, === for h3
    # We need to shift: ### (h3 in MD) -> == (h2 in Typst for main content)

    # Handle ### (h3 in Jekyll, becomes h2/main section in Typst)
    text = re.sub(r'^###\s+(.+)$', r'== \1', text, flags=re.MULTILINE)

    # Handle #### (h4 in Jekyll, becomes h3/subsection in Typst)
    text = re.sub(r'^####\s+(.+)$', r'=== \1', text, flags=re.MULTILINE)

    # Handle ##### (h5 -> h4)
    text = re.sub(r'^#####\s+(.+)$', r'==== \1', text, flags=re.MULTILINE)

    # Handle ###### (h6 -> h5)
    text = re.sub(r'^######\s+(.+)$', r'===== \1', text, flags=re.MULTILINE)

    return text


def convert_bold_italic(text: str) -> str:
    """Convert Markdown bold/italic to Typst."""
    # Order is important! Process *** first, then **, then *

    # ***text*** -> *_text_*
    text = re.sub(r'\*\*\*(\*?)\*([^*]+)\*(\*?)\*\*\*', r'*\1_\2_\3*', text)

    # **text** -> *text*
    text = re.sub(r'\*\*([^*]+)\*\*', r'*\1*', text)

    # *text* -> _text_ (but not inside already processed **)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'_\1_', text)

    return text


def convert_links(text: str) -> str:
    """Convert Markdown links to Typst."""
    # [text](url) -> #link("url")[text]
    def link_replacer(match):
        text = match.group(1)
        url = match.group(2)
        return f'#link("{url}")[{text}]'

    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link_replacer, text)
    return text


def convert_images(text: str) -> str:
    """Convert Markdown images to Typst."""
    # ![alt](path) -> #image("imgs/path")
    def image_replacer(match):
        alt = match.group(1)
        path = match.group(2)
        return f'#image("imgs/{path}")'

    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', image_replacer, text)
    return text


def convert_footnotes(text: str) -> str:
    """Convert Markdown footnotes to Typst inline footnotes."""
    # Extract all footnotes
    footnote_pattern = r'\^\[(\d+)\]:(.+)'
    footnotes = {}

    for match in re.finditer(footnote_pattern, text, re.MULTILINE):
        num = match.group(1)
        content = match.group(2).strip()
        footnotes[num] = content

    # Remove footnote definitions
    text = re.sub(footnote_pattern, '', text, flags=re.MULTILINE)

    # Replace references with inline footnotes
    for num, content in footnotes.items():
        # Handle both [^1] and ^[1] formats
        for pattern in [r'\[\^' + num + r'\]', r'^\[' + num + r'\]']:
            text = re.sub(pattern, f'#footnote[{content}]', text)

    return text


def convert_blockquotes(text: str) -> str:
    """Convert Markdown blockquotes to Typst."""
    lines = text.split('\n')
    in_blockquote = False
    quote_lines = []
    result = []

    for line in lines:
        if line.startswith('> '):
            in_blockquote = True
            quote_lines.append(line[2:])
        elif line.startswith('>> '):
            # Nested quote, just dedent one level
            in_blockquote = True
            quote_lines.append(line[3:])
        else:
            if in_blockquote:
                result.append('#quote-block[')
                result.extend(quote_lines)
                result.append(']')
                quote_lines = []
                in_blockquote = False
            result.append(line)

    # Handle closing quote at end of file
    if in_blockquote and quote_lines:
        result.append('#quote-block[')
        result.extend(quote_lines)
        result.append(']')

    return '\n'.join(result)


def convert_lists(text: str) -> str:
    """Convert Markdown lists to Typst."""
    lines = text.split('\n')
    result = []

    for line in lines:
        # Convert ordered lists: 1. -> +
        if re.match(r'^\d+\.\s+', line):
            line = re.sub(r'^\d+\.\s+', '+ ', line)
        result.append(line)

    return '\n'.join(result)


def convert_code_blocks(text: str) -> str:
    """Handle code blocks - mostly preserve as-is."""
    # Typst uses same ``` syntax, so just ensure proper formatting
    return text


def remove_horizontal_rules(text: str) -> str:
    """Remove Markdown horizontal rules."""
    text = re.sub(r'^\s*---+\s*$', '', text, flags=re.MULTILINE)
    return text


def remove_html_tags(text: str) -> str:
    """Convert or remove common HTML tags."""
    # <u>underline</u> -> #underline[underline]
    text = re.sub(r'<u>([^<]+)</u>', r'#underline[\1]', text)

    # <strike>strikethrough</strike> -> #strike[strikethrough]
    text = re.sub(r'<strike>([^<]+)</strike>', r'#strike[\1]', text)
    text = re.sub(r'<s>([^<]+)</s>', r'#strike[\1]', text)
    text = re.sub(r'<del>([^<]+)</del>', r'#strike[\1]', text)

    # Remove font tags (CSS handles styling)
    text = re.sub(r'<font[^>]*>([^<]+)</font>', r'\1', text)

    # <span> tags - remove but keep content
    text = re.sub(r'<span[^>]*>([^<]+)</span>', r'\1', text)

    # <div> - convert to line breaks
    text = re.sub(r'<div[^>]*>', '\n', text)
    text = re.sub(r'</div>', '', text)

    # <br> -> \
    text = re.sub(r'<br\s*/?>', r'\\', text)

    # <center> -> #align(center)[
    def center_replacer(match):
        content = match.group(1)
        return f'#align(center)[{content}]'
    text = re.sub(r'<center>([^<]+)</center>', center_replacer, text)

    # Remove remaining HTML tags (simple approach)
    # text = re.sub(r'<[^>]+>', '', text)

    return text


def process_poetry_formatting(text: str) -> str:
    """Handle poetry-specific formatting."""
    # Chinese poetry lines often don't have line breaks in Markdown
    # but need them in Typst. Look for patterns like:
    # 句一，句二。
    # and add intentional breaks
    return text


# ============================================================================
# Main Conversion
# ============================================================================


def convert_markdown_to_typst(markdown_content: str, title: str, date: str, categories: List[str]) -> str:
    """Convert a Markdown post to Typst format."""

    # Remove YAML front matter
    content = re.sub(r'^---$.+?^---$\s*', '', markdown_content, flags=re.MULTILINE | re.DOTALL)

    # Apply conversions in order
    content = convert_footnotes(content)
    content = convert_blockquotes(content)
    content = remove_horizontal_rules(content)
    content = convert_headers(content)
    content = convert_bold_italic(content)
    content = convert_links(content)
    content = convert_images(content)
    content = convert_lists(content)
    content = remove_html_tags(content)
    content = process_poetry_formatting(content)

    # Determine language
    lang = "zh" if is_chinese_text(content) else "en"

    # Build metadata
    metadata_parts = []
    if title:
        metadata_parts.append(f'title: "{title}"')
    if date:
        try:
            dt = datetime.strptime(date, '%Y-%m-%d')
            metadata_parts.append(f'date: datetime(year: {dt.year}, month: {dt.month}, day: {dt.day})')
        except:
            pass
    if categories:
        cats_str = ', '.join(f'"{c}"' for c in categories)
        metadata_parts.append(f'categories: ({cats_str},)')

    metadata_str = '.with(' + ', '.join(metadata_parts) + ')' if metadata_parts else ''
    if lang:
        metadata_str += f'.with(lang: "{lang}")'

    # Wrap content in template
    result = CONTENT_TEMPLATE.format(metadata=metadata_str, content=content.strip())

    return result


def copy_post_assets(post_date: Tuple[str, str, str], post_slug: str, output_dir: Path):
    """Copy assets for a post if they exist."""
    year, month, day = post_date
    asset_source = ASSETS_DIR / year / month / day

    if asset_source.exists():
        asset_dest = output_dir / "imgs"
        asset_dest.mkdir(parents=True, exist_ok=True)

        # Copy all files from asset source
        for item in asset_source.iterdir():
            if item.is_file():
                shutil.copy2(item, asset_dest / item.name)
                print(f"  Copied asset: {item.name}")


def convert_post(post_file: Path, test_mode: bool = False) -> bool:
    """Convert a single Jekyll post to Tufted format."""
    print(f"\nConverting: {post_file.name}")

    # Read the post
    try:
        content = post_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  Error reading file: {e}")
        return False

    # Extract date from filename
    date_parts = extract_date_from_filename(post_file.name)
    if not date_parts:
        print(f"  Warning: Could not extract date from filename, skipping")
        return False

    year, month, day = date_parts
    date_str = f"{year}-{month}-{day}"

    # Extract metadata from front matter
    metadata = get_post_info_from_frontmatter(content)
    title = metadata.get('title', post_file.stem)
    categories = metadata.get('categories', [])
    post_date = metadata.get('date', date_str)

    # Create slug
    slug = slugify(title)
    output_dir = OUTPUT_DIR / f"{date_str}-{slug}"

    # Check if output already exists (in test mode, skip)
    if output_dir.exists():
        if test_mode:
            print(f"  Skipping (already exists): {output_dir}")
            return True

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Convert content
    typst_content = convert_markdown_to_typst(content, title, post_date, categories)

    # Write output
    output_file = output_dir / "index.typ"
    output_file.write_text(typst_content, encoding='utf-8')
    print(f"  Created: {output_file}")

    # Copy assets
    copy_post_assets(date_parts, slug, output_dir)

    return True


# ============================================================================
# Main Entry Point
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description='Convert Jekyll Markdown posts to Tufted Blog Typst format'
    )
    parser.add_argument('--test', action='store_true',
                        help='Convert only first 5 posts for testing')
    parser.add_argument('--full', action='store_true',
                        help='Convert all posts')
    parser.add_argument('--post', type=str,
                        help='Convert a specific post file')

    args = parser.parse_args()

    if not any([args.test, args.full, args.post]):
        parser.print_help()
        print("\nError: Please specify --test, --full, or --post FILE")
        return 1

    # Find all markdown posts
    if not POSTS_DIR.exists():
        print(f"Error: Posts directory not found: {POSTS_DIR}")
        return 1

    post_files = sorted(POSTS_DIR.glob('*.md'))

    if not post_files:
        print(f"No markdown posts found in {POSTS_DIR}")
        return 1

    # Filter posts based on arguments
    if args.post:
        post_file = Path(args.post)
        if not post_file.exists():
            print(f"Error: Post file not found: {post_file}")
            return 1
        post_files = [post_file]
    elif args.test:
        post_files = post_files[:5]
        print(f"Test mode: Converting first {len(post_files)} posts")
    else:
        print(f"Full mode: Converting all {len(post_files)} posts")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Convert posts
    success_count = 0
    fail_count = 0

    for post_file in post_files:
        if convert_post(post_file, test_mode=args.test):
            success_count += 1
        else:
            fail_count += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"Conversion complete!")
    print(f"  Success: {success_count}")
    print(f"  Failed:  {fail_count}")
    print(f"  Output directory: {OUTPUT_DIR.absolute()}")
    print(f"{'='*60}")

    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    exit(main())
