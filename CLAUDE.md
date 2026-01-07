# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Tufted Blog** using the [Tufted](https://github.com/Myriad-Dreamin/tufted) template. Content is written in [Typst](https://typst.app/) (a modern typesetting system) and built to static HTML via a Python build script. The site is deployed via GitHub Pages at `rainoffallingstar.github.io`.

**Key difference from Jekyll**: This is NOT a Jekyll blog. All content is authored in `.typ` files under `content/` and compiled using the Typst CLI, not Ruby/Jekyll.

## Development Commands

### Build the Site
```bash
# Full build (HTML + PDF + assets) with incremental compilation
python build.py build

# Force full rebuild (ignore incremental checks)
python build.py build --force
```

### Partial Builds
```bash
# HTML only
python build.py html

# PDF only (files with "PDF" in filename)
python build.py pdf

# Assets only
python build.py assets
```

### Clean and Preview
```bash
# Clean generated files
python build.py clean

# Start local preview server (auto-opens browser)
python build.py preview

# Custom port
python build.py preview -p 3000
```

### Environment Requirements
- **Typst CLI**: Must be installed and in PATH (https://typst.app/open-source/#download)
- **Python**: 3.6+ (build script uses uv for dependency management, but no external dependencies required)

## Architecture

### Content Structure

**Typst Files**: All content is in `content/` as `.typ` files:
- `content/index.typ` - Homepage
- `content/Blog/YYYY-MM-DD-title/index.typ` - Blog posts (date-based directory naming)
- `content/About/index.typ`, `content/Links/index.typ` - Standalone pages
- `content/Docs/` - Documentation pages
- `content/CV/index.typ` - Resume/CV page

**PDF Output**: Files with "PDF" in their filename (e.g., `CV-PDF.typ`, `sample-PDF.typ`) are compiled to PDF instead of HTML.

**Post Assets**: Images and other resources should be placed in the same directory as the `index.typ` file. Reference them directly:
```typst
#image("image.png")
```

### Configuration

**Site Config**: `config.typ` contains global settings:
```typst
#import "@preview/tufted:0.1.0"

#let template = tufted.tufted-web.with(
  header-links: (
    "/": "首页",
    "/Links/": "友链",
    "/About/": "关于",
  ),
  lang: "zh",
  title: "rainoffallingstar's Blog",
)
```

**Build Config**: `build.py` handles:
- Incremental compilation (only rebuilds changed files)
- Dependency tracking via `#import` statements in `.typ` files
- HTML injection (favicon, scripts) into compiled output
- Static asset copying from `assets/` to `_site/assets/`

### Build System Details

**Incremental Compilation**: The build system tracks:
- Source file modification times
- Dependencies via `#import` statements (including transitive dependencies)
- Non-.typ assets in the same directory as source files
- Global dependencies (`config.typ`, `content/_*/`)

**Output**: All generated files go to `_site/`:
- HTML files mirror the `content/` directory structure
- PDFs are generated alongside HTML for files with "PDF" in filename
- `assets/` is copied to `_site/assets/`

### Template System

Each content file imports and applies the template:
```typst
#import "../../config.typ": template, tufted
#show: template.with(title: "Page Title")

= Heading

Content here...
```

The template is from `@preview/tufted:0.1.0` and provides Tufte CSS-inspired styling with wide sidebars suitable for academic/content-heavy sites.

### Static Assets

Located in `assets/`:
- `tufted.css` - Main stylesheet (Tufte CSS)
- `custom.css` - Custom overrides
- `copy-code.js`, `line-numbers.js`, `format-headings.js` - Interactive features
- `favicon.ico` - Site favicon

These are injected into compiled HTML via `HEAD_INJECTION` in `build.py`.

### Deployment

**GitHub Actions** (`.github/workflows/deploy.yml`):
- Triggers on push to `githubversion` branch
- Uses `typst-community/setup-typst@v4` to install Typst
- Runs `python build.py build --force` for clean build
- Deploys `_site/` to GitHub Pages via `peaceiris/actions-gh-pages@v3`
- Copies `CNAME` file if present (for custom domains)

### File Naming Conventions

- Blog posts: `content/Blog/YYYY-MM-DD-title/index.typ` (use hyphens, not underscores)
- PDF exports: Include "PDF" in the filename (e.g., `CV-PDF.typ`)
- Standalone pages: `content/SectionName/index.typ`

### Typst Syntax Quick Reference

```typst
#show: template.with(title: "Title")  # Apply template

= Level 1 Heading
== Level 2 Heading
=== Level 3 Heading

#bold[**Bold text**]
#emphasize[*Italic text*]

#link("https://example.com")[Link text]

#image("path/to/image.png")

#block(
  fill: rgb("f0f0f0"),
  inset: 10pt,
  [Sidebar content]
)

// Code blocks (styled by tufted.css)
```python
code here
```

- List item
- Another item

+ Numbered item
+ Another numbered item
```

## Common Patterns

### Creating a New Blog Post
1. Create directory: `content/Blog/YYYY-MM-DD-post-title/`
2. Create `index.typ` with:
```typst
#import "../../../config.typ": template, tufted
#show: template.with(title: "Post Title")

= Post Title

Date: 2024-01-01

Content...
```

### Adding Images
Place image in the same directory as `index.typ`, reference as:
```typst
#image("filename.png")
```

### Changing Navigation
Edit `header-links` in `config.typ`.

### Troubleshooting Build Issues
- If changes don't appear: Try `python build.py build --force`
- If Typst not found: Ensure Typst CLI is installed and in PATH
- Check output in `_site/` to verify compilation succeeded
