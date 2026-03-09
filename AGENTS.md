# Repository Guidelines

## Project Structure & Module Organization
Core site content lives in `content/` and is written in Typst (`.typ`), with top-level sections such as `Blog/`, `About/`, `Links/`, and `Docs/`. Shared styling and browser-side enhancements are in `assets/` (CSS, JS, favicon). Build orchestration is in `build.py` (primary) and `Makefile` (alternative). Generated output is written to `_site/` and should not be committed.

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

## Commit & Pull Request Guidelines
History shows a Conventional Commit leaning (`docs:`, `feat:`, `fix:`), plus concise imperative messages. Prefer `type: short description` (example: `fix: handle empty RSS abstracts`). Keep PRs scoped; include:
- clear summary of behavior/content changes,
- linked issue (if applicable),
- screenshots for visible style/layout changes,
- notes on commands run for verification.
