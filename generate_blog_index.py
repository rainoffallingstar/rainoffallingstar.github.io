#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Blog Index from converted posts
"""

import os
import re
from pathlib import Path
from collections import defaultdict


BLOG_DIR = Path("content/Blog")
OUTPUT_FILE = BLOG_DIR / "index.typ"


def extract_post_info(post_dir: Path) -> dict:
    """Extract title and date from a post directory."""
    # Extract date from directory name (YYYY-MM-DD-slug)
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.+)', post_dir.name)
    if not match:
        return None

    year, month, day, slug = match.groups()
    date_str = f"{year}"

    # Try to read the index.typ to get the title
    index_file = post_dir / "index.typ"
    if not index_file.exists():
        return None

    content = index_file.read_text(encoding='utf-8')

    # Extract title from metadata
    title_match = re.search(r'title:\s*"([^"]+)"', content)
    if title_match:
        title = title_match.group(1)
    else:
        title = slug.replace('-', ' ').title()

    return {
        'dir_name': post_dir.name,
        'title': title,
        'year': year,
        'month': month,
        'day': day,
        'date_sort': f"{year}-{month}-{day}"
    }


def generate_blog_index():
    """Generate the blog index page."""

    # Get all post directories
    post_dirs = [d for d in BLOG_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')]

    # Extract post info
    posts = []
    for post_dir in sorted(post_dirs, reverse=True):
        info = extract_post_info(post_dir)
        if info:
            posts.append(info)

    # Group by year
    posts_by_year = defaultdict(list)
    for post in posts:
        posts_by_year[post['year']].append(post)

    # Sort posts within each year by date (newest first)
    for year in posts_by_year:
        posts_by_year[year].sort(key=lambda x: x['date_sort'], reverse=True)

    # Generate the index content
    lines = [
        '#import "../index.typ": template, tufted',
        '#show: template.with(title: "博客")',
        '',
        '= 博客 / Blog',
        ''
    ]

    # Add years in reverse chronological order
    for year in sorted(posts_by_year.keys(), reverse=True):
        lines.append(f"== {year}")
        lines.append("")

        for post in posts_by_year[year]:
            lines.append(f"- #link(\"{post['dir_name']}/\")[{post['title']}]")

        lines.append("")

    # Write the index
    OUTPUT_FILE.write_text('\n'.join(lines), encoding='utf-8')
    print(f"Generated blog index: {OUTPUT_FILE}")
    print(f"  Total years: {len(posts_by_year)}")
    print(f"  Total posts: {len(posts)}")


if __name__ == '__main__':
    generate_blog_index()
