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

### Cloudflare proxy (orange cloud)

The DNS record is currently **proxied** (orange cloud). Cloudflare terminates
TLS at the edge and fetches the origin over HTTPS.

Keep **SSL/TLS -> Overview on Full (strict)**. `Flexible` would make Cloudflare
request the origin over plain HTTP, GitHub Pages would 301 that request back to
HTTPS, and the result is an infinite redirect loop. Verify the chain with:

```bash
# edge: should be CN=rainoffallingstar.com (wildcard, Cloudflare Universal SSL)
echo | openssl s_client -servername blog.rainoffallingstar.com \
  -connect blog.rainoffallingstar.com:443 2>/dev/null \
  | openssl x509 -noout -subject -dates

# origin: connect straight to GitHub Pages, bypassing the proxy
curl -sS -o /dev/null -w 'origin=%{http_code}\n' \
  --resolve blog.rainoffallingstar.com:443:185.199.108.153 \
  https://blog.rainoffallingstar.com/

# exactly one redirect, then 200
curl -sSL -o /dev/null -w 'final=%{url_effective} code=%{http_code} redirects=%{num_redirects}\n' \
  http://blog.rainoffallingstar.com/
```

### Certificate renewal while proxied (recurring maintenance)

Two certificates are involved and only one renews itself:

- **Cloudflare edge certificate** - renewed automatically by Cloudflare. No action.
- **GitHub Pages origin certificate** - a Let's Encrypt certificate for
  `blog.rainoffallingstar.com`. Let's Encrypt validates it with an HTTP-01
  challenge, but the orange cloud intercepts that request, so **renewal fails
  while the proxy is on**.

If the origin certificate lapses, GitHub Pages serves an expired cert, and
Cloudflare in Full (strict) mode answers **526 Invalid SSL certificate**. The
site goes down even though the edge certificate is fine.

The current origin certificate expires **2027-02-13**. Repeat this around
**2027-01-15** (a month early), and again every ~90 days after that:

1. Cloudflare DNS: switch the `blog` record to **DNS only** (grey cloud).
2. Wait for propagation, then open GitHub repo Settings -> Pages and let it
   re-issue the certificate (re-check the custom domain if the UI offers it).
   This can take a few minutes up to a few hours.
3. Confirm the new expiry date:

   ```bash
   echo | openssl s_client -servername blog.rainoffallingstar.com \
     -connect 185.199.108.153:443 2>/dev/null \
     | openssl x509 -noout -enddate
   ```

4. Switch the record back to **Proxied** (orange cloud) and re-check that
   `https://blog.rainoffallingstar.com/` returns 200.

A quick health check that catches this before visitors do:

```bash
curl -sS -o /dev/null -w '%{http_code}\n' \
  --resolve blog.rainoffallingstar.com:443:185.199.108.153 \
  https://blog.rainoffallingstar.com/
```

Anything other than `200` means the origin certificate needs attention.

### Automation, deliberately not enabled

`docs/pages-certificate-proxy.yml.disabled` contains a complete GitHub Actions
workflow that would do the grey-cloud / orange-cloud dance automatically: it
reads `https_certificate` from the Pages API, unproxies when <=30 days remain,
and re-proxies only after GitHub reports an approved certificate with >=45 days
left.

It is **not enabled**. It lives outside `.github/workflows/` and carries a
`.disabled` suffix, so GitHub never runs it. The manual procedure above is the
supported path.

Rationale for keeping it parked rather than running it:

- It needs a Cloudflare API token with DNS:Edit on the zone. That is a
  long-lived credential capable of redirecting the whole domain -- a
  meaningfully larger blast radius than anything else this repo holds.
- During the grey-cloud window the site loses Cloudflare's cache, WAF and
  proxy protection, and GitHub's re-issuance can take hours.
- Renewal comes around roughly every 90 days. A documented manual step is
  cheaper than owning automation that can silently misconfigure DNS.

The file documents how to enable it if that trade-off ever changes. Read the
header before moving it back into `.github/workflows/`.

## Commit & Pull Request Guidelines
History shows a Conventional Commit leaning (`docs:`, `feat:`, `fix:`), plus concise imperative messages. Prefer `type: short description` (example: `fix: handle empty RSS abstracts`). Keep PRs scoped; include:
- clear summary of behavior/content changes,
- linked issue (if applicable),
- screenshots for visible style/layout changes,
- notes on commands run for verification.
