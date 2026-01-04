# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Jekyll-based personal blog using the [TMaize Blog theme](https://github.com/TMaize/tmaize-blog). It's a minimal, lightweight theme (<20KB resources) with no frameworks, supporting dark mode, full-text search, and responsive design. The site is deployed via GitHub Pages at `rainoffallingstar.github.io`.

## Development Commands

### Start Local Development Server
```bash
bundle exec jekyll serve --watch --host=127.0.0.1 --port=8080
```
The `--watch` flag enables automatic rebuilding on file changes.

### Build for Production
```bash
bundle exec jekyll build --destination=dist
```

### Install Dependencies
```bash
gem install bundler
bundle install
```

### Generate Code Highlighting CSS
```bash
rougify style github > highlighting.css
```

## Architecture

### Content Structure

**Posts**: Blog posts are stored in `_posts/` with the naming convention `YYYY-MM-dd-title.md`. Each post requires front matter:
```yaml
---
layout: mypost
title: Post Title
categories: [category1, category2]
---
```

**Post Assets**: Assets for a post (images, downloads) go in `posts/YYYY/MM/DD/` corresponding to the post date. Reference them directly in markdown without any path prefix:
```markdown
![image description](image.png)
[download.zip](download.zip)
```

**Pages**: Standalone pages in `pages/` directory. Use `layout: page` for static pages.

### Layouts

- `_layouts/mypost.html` - Blog post layout with title, date, content, and optional adsense
- `_layouts/page.html` - Generic page layout

Both include:
- `_includes/head.html` - Meta tags, CSS links, dark theme initialization
- `_includes/header.html` - Navigation menu
- `_includes/footer.html` - Footer content
- `_includes/script.html` - JavaScript includes

### Theme System

Dark/light theme is client-side managed via JavaScript in `_includes/head.html`:
- Uses `sessionStorage.darkTheme` for per-session persistence
- Falls back to `prefers-color-scheme` media query
- Toggling theme sets `document.documentElement.className = 'dark'`
- CSS files are `static/css/theme-dark.css` and `static/css/common.css`

### Service Worker

`service-worker.js` implements aggressive caching:
- Cache key includes build timestamp: `blog_{{ site.time | date: "%Y%m%d%H%M%S" }}`
- Automatically discovers and caches all assets referenced in `index.html`
- Clears old cache versions on activate
- Uses `skipWaiting()` for immediate updates

### Configuration

Key configuration in `_config.yml`:
- `baseurl`: Set if deploying to subdirectory, otherwise empty
- `domainUrl`: Base URL for the site
- `menu`: Navigation menu items
- Feature flags: `extClickEffect`, `extAdsense`, `extMTA`, `extBaidu`, `extMath`
- `links`:友情链接 (friend links)

### File Naming Conventions

- Posts: `YYYY-MM-dd-title.md` (use hyphens, not underscores)
- Assets: `posts/YYYY/MM/DD/filename.ext`
- Pages can use `.html` or `.md` extension

### CSS Organization

Styles are versioned with build timestamp (`?t={{buildAt}}`):
- `static/css/common.css` - Shared styles
- `static/css/theme-dark.css` - Dark theme overrides
- `static/css/post.css` - Post-specific styles
- `static/css/page.css` - Page-specific styles
- `static/css/code-dark.css` / `code-light.css` - Syntax highlighting

## Ruby Dependencies

Fixed versions in `Gemfile`:
- `jekyll 3.8.5`
- `rouge 3.11.0` (syntax highlighting)
- `wdm` (Windows directory monitoring)
