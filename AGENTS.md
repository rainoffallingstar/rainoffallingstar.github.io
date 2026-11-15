# Repository Guidelines

## Project Structure & Module Organization
Core site content lives in `content/` and is written in Typst (`.typ`), with top-level sections such as `Blog/`, `About/`, `Links/`, and `Docs/`. Build orchestration is in `build.py` (primary) and `Makefile` (alternative). Generated output is written to `_site/` and should not be committed.

The template implementation is vendored in `tufted-lib/`, synced from
[Yousa-Mirage/Tufted-Blog-Template](https://github.com/Yousa-Mirage/Tufted-Blog-Template).
`config.typ` imports it and wraps `tufted-web`; do not edit `tufted-lib/` by
hand, because `.github/workflows/update.yml` overwrites it from upstream every
two weeks. Site-specific overrides live in `.github/.templatesyncignore`.

`assets/` holds styling and browser-side enhancements, layered as
`tufted.css` (upstream features) -> `theme.css` (upstream theme variables) ->
`custom.css` (user hook, currently empty) -> `site.css` (this site's visual
layer). Keep site-specific rules in `site.css`; upstream files would be
overwritten on the next sync.

## Build, Test, and Development Commands
- `python build.py build` - full site build (HTML, PDF, assets).
- `python build.py build --force` - rebuild everything, skipping incremental checks.
- `python build.py html` / `python build.py pdf` - build only one target type.
- `python build.py preview -p 8000` - local preview server.
- `python build.py clean` - remove generated output in `_site/`.
- `make build` - Makefile-based full build if you prefer `make`.

## Coding Style & Naming Conventions
Use 4-space indentation in Python and keep functions small, single-purpose, and explicit. Follow existing file naming patterns: dated content folders like `content/Blog/YYYY-MM-DD-title/` and `index.typ` as the page entrypoint. Keep Typst imports relative and reuse shared config (`config.typ`) instead of duplicating template logic. For script edits, preserve UTF-8 handling and deterministic JSON output.

## Testing Guidelines
There is no dedicated test suite yet. Treat build and script execution as validation:
- Run `python build.py build --force` before opening a PR.
- Confirm no unintended files are generated outside `_site/`.

## Custom Domain

The site is served at `https://blog.rainoffallingstar.com`, a GitHub Pages
custom domain backed by the `gh-pages` branch. The domain is defined in exactly
three places; changing it requires updating all three in the same commit:

1. `CNAME` (repository root) - bare hostname, no protocol, no trailing slash,
   no trailing newline required but tolerated. GitHub Pages reads this file.
2. `config.typ` - the `site-url` binding. Drives `canonical`, `sitemap.xml`,
   `feed.xml` and Open Graph URLs.
3. `.github/workflows/deploy.yml` - the `cname:` input of the
   `peaceiris/actions-gh-pages` step. Must match `CNAME`.

Editing `CNAME` on `gh-pages` by hand is never correct: that branch is build
output, and the next deploy overwrites it from the root `CNAME`. The deploy
workflow verifies `CNAME` exists and is non-empty before publishing, so a broken
value fails the run instead of silently dropping the domain.

After changing the domain: update the DNS record at the registrar (Cloudflare)
to a CNAME pointing at `rainoffallingstar.github.io` with the proxy disabled
("DNS only"), let GitHub issue the TLS certificate, then re-enable the proxy if
desired. Confirm with:

```bash
gh api repos/rainoffallingstar/rainoffallingstar.github.io/pages \
  --jq '{cname, https_enforced, status}'
curl -sSI https://blog.rainoffallingstar.com/ | head -1
```

`https_enforced` must stay `true`, and plain HTTP must return a 301 to HTTPS.

## Commit & Pull Request Guidelines
History shows a Conventional Commit leaning (`docs:`, `feat:`, `fix:`), plus concise imperative messages. Prefer `type: short description` (example: `fix: handle empty RSS abstracts`). Keep PRs scoped; include:
- clear summary of behavior/content changes,
- linked issue (if applicable),
- screenshots for visible style/layout changes,
- notes on commands run for verification.
