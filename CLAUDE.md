# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Tufted Blog** using [Tufted-Blog-Template](https://github.com/Yousa-Mirage/Tufted-Blog-Template). Content is written in [Typst](https://typst.app/) and built to static HTML via a Python build script. The site is deployed via GitHub Pages at `https://blog.rainoffallingstar.com`.

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

**Site Config**: `config.typ` is a thin wrapper over the vendored template in `tufted-lib/`:
```typst
#import "tufted-lib/tufted.typ" as tufted

#let site-title = "rainoffallingstar’s Blog"
#let site-url = "https://blog.rainoffallingstar.com"

#let site = tufted.tufted-web.with(
  header-links: header-links,
  website-title: site-title,
  website-url: site-url,
  feed-dir: ("/Blog/",),
  css: ("/assets/custom.css", "/assets/site.css"),
)
```

`site-url` drives `canonical`, `sitemap.xml`, `feed.xml` and Open Graph URLs.
Keep it in sync with `CNAME` and the `cname:` input in `deploy.yml`.

**Build Config**: `build.py` handles:
- Incremental compilation (only rebuilds changed files)
- Dependency tracking via `#import` statements in `.typ` files
- `--input page-path=...` so the template can build canonical URLs
- Static asset copying from `assets/` to `_site/assets/`
- `feed.xml` (full-text RSS), `sitemap.xml` and `robots.txt` generation

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

The template lives in `tufted-lib/`, vendored from upstream and therefore **not to be edited by hand** — `.github/workflows/update.yml` overwrites it every two weeks. Site-specific overrides belong in `config.typ` and `assets/site.css`, both listed in `.github/.templatesyncignore`.

### Static Assets

Located in `assets/`, layered in this order:
- `tufted.css` - upstream feature layer (grid, code blocks, tables, TOC, blog entries)
- `theme.css` - upstream light/dark theme variables
- `custom.css` - user override hook (currently empty)
- `site.css` - this site's visual layer: tokens, typography, header, archive, dark mode
- `site.js` - site-only script (sticky header scroll state)
- `icons/` - RSS / moon / sun SVGs used as CSS masks
- `scripts/` - upstream scripts (theme toggle, TOC, back-to-top, code blocks, math copy, note toggles)

Stylesheets and scripts are referenced from `config.typ` through the template's
`css` and `js-scripts` parameters, not injected by `build.py`.

### Deployment

**GitHub Actions** (`.github/workflows/deploy.yml`):
- Triggers on push to `githubversion` branch
- Uses `typst-community/setup-typst@v4` to install Typst
- Runs `python build.py build --force` for clean build
- Verifies `CNAME` exists and is non-empty, then copies it into `_site/`
- Deploys `_site/` to the `gh-pages` branch via `peaceiris/actions-gh-pages@v3`
  with `cname: blog.rainoffallingstar.com`

### Custom Domain

The domain is defined in exactly three places and all three must change together:

1. `CNAME` (repository root) - bare hostname.
2. `config.typ` - `site-url`.
3. `.github/workflows/deploy.yml` - the `cname:` input.

Never edit `CNAME` on `gh-pages`; that branch is build output and the next
deploy overwrites it. DNS lives at Cloudflare as a CNAME to
`rainoffallingstar.github.io`; proxy must be off ("DNS only") until GitHub
issues the TLS certificate. Verify with:

```bash
gh api repos/rainoffallingstar/rainoffallingstar.github.io/pages \
  --jq '{cname, https_enforced, status}'
```

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

### Adding a Post to the Homepage

`build.py` renders every `content/Blog/*/index.typ` on its own URL, but the
homepage archive is driven by the `posts` array in `content/index.typ`. Add an
entry there too or the post will be reachable but unlisted:

```typst
(date: "2024-01-01", title: "Post Title", href: "/Blog/2024-01-01-post-title/"),
```

Dates must be `YYYY-MM-DD`. RSS generation also needs a date, either from this
folder name or from an explicit `date:` argument in the post.

### Troubleshooting Build Issues
- If changes don't appear: Try `python build.py build --force`
- If Typst not found: Ensure Typst CLI is installed and in PATH
- Check output in `_site/` to verify compilation succeeded
