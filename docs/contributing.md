---
title: Contributing
description: How to report bugs, propose features and open pull requests against BrandKit.
---

# Contributing

Contributions are welcome. The project is small and single-maintainer, so the process is light.

The authoritative version of this document is [`CONTRIBUTING.md`](https://github.com/fabriziosalmi/brandkit/blob/main/CONTRIBUTING.md) in the repository.

## Before you start

Everyone participating is bound by the [Code of Conduct](/code-of-conduct).

## Reporting a bug

Open a [bug report](https://github.com/fabriziosalmi/brandkit/issues/new?template=bug_report.md) and include:

- what you expected and what happened instead
- exact steps to reproduce
- the startup log — `docker compose logs brandkit` or the console output
- Python version, or Docker and Compose versions
- your operating system
- the source image, if it is not confidential and the bug depends on it

::: danger Never report a security issue as a public issue
Email **fabrizio.salmi@gmail.com** instead. See the [security policy](/security#reporting-a-vulnerability).
:::

## Proposing a feature

Open a [feature request](https://github.com/fabriziosalmi/brandkit/issues/new?template=feature_request.md). Describe the problem before the solution — what are you trying to do that BrandKit makes hard?

Two things that are almost always accepted:

- **New formats.** They are pure data in `config.json`. If a platform changed its recommended image size, that is a one-line PR and a genuinely useful one.
- **Documentation fixes.** Every page on this site has an "Edit this page on GitHub" link at the bottom.

## Development setup

```bash
git clone https://github.com/fabriziosalmi/brandkit.git
cd brandkit

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

FLASK_ENV=development python app.py
```

`FLASK_ENV=development` gives you auto-reload and the Werkzeug debugger on `http://127.0.0.1:8000`. Never set it anywhere anyone else can reach.

### Where things live

| File | What it is |
| --- | --- |
| `app.py` | the entire backend — routes, image pipeline, caching, cleanup |
| `templates/index.html` | the entire frontend — one Jinja template with inline Alpine.js |
| `config.json` | the format catalogue and preprocessing defaults |
| `static/vendor/` | vendored Tailwind and Alpine — **do not replace with CDN links** |
| `docs/` | this documentation site (VitePress) |

The project is deliberately two files. If a change would split them, say so in the issue first.

## Pull requests

1. Fork and branch — `git checkout -b feat/short-description`
2. Make the change
3. Test it (see below)
4. Commit with a [Conventional Commits](https://www.conventionalcommits.org/) prefix — `feat:`, `fix:`, `docs:`, `ci:`, `build(deps):`
5. Open the PR against `main`, describing what changed and how you verified it

Keep pull requests focused. A formatting sweep mixed into a behaviour change is very hard to review.

### CI

Every push and pull request runs the [CI workflow](https://github.com/fabriziosalmi/brandkit/blob/main/.github/workflows/ci.yml): install `requirements.txt` on Python 3.11 and 3.12, then `pytest -v`.

Run tests locally with:

```bash
pytest -q
```

### Manual test checklist

Beyond the automated test suite, verify manually:

- [ ] the page loads and the format catalogue renders
- [ ] an upload generates the expected files with the expected dimensions
- [ ] PNG output keeps transparency; JPG flattens it
- [ ] ICO is produced when `favicon` is selected, and only then
- [ ] background removal works, or degrades cleanly when `rembg` is absent
- [ ] the ZIP contains everything shown in the results grid
- [ ] `POST /upload` without a CSRF token still returns `400`
- [ ] the sixth upload in a minute returns `429`

### Documentation

If your change alters behaviour, update the docs in the same pull request.

```bash
npm install
npm run docs:dev      # http://localhost:5173
npm run docs:build    # production build, catches dead links
```

`docs:build` fails on broken internal links, so run it before pushing.

::: info Why `package.json` has an `overrides` block
VitePress 1.6.4 pins Vite 5, which is no longer receiving fixes for a set of dev-server advisories (a `server.fs.deny` bypass, a path traversal in optimized-deps `.map` handling, and the esbuild CORS issue). VitePress 2 is still alpha, so the toolchain is pulled forward with npm `overrides` instead:

```json
"overrides": {
  "esbuild": "^0.25.12",
  "vite": "^6.4.3"
}
```

The combination is verified — the site builds and renders correctly — but it is ahead of what VitePress 1.6 declares. If a build breaks after a dependency bump, this block is the first thing to look at. Drop it once VitePress 2 is stable.

None of this reaches the published site: GitHub Pages serves static output, so Vite exists only at build time and in `npm run docs:dev`.
:::

## Style

**Python** — PEP 8, four spaces, `snake_case`. Docstrings on any function that is not obvious. Prefer clarity over cleverness; this codebase is read far more often than it is written.

**Commits** — imperative mood, Conventional Commits prefix, one logical change each.

## Getting help

- [Issues](https://github.com/fabriziosalmi/brandkit/issues) for bugs and features
- [Troubleshooting](/guide/troubleshooting) for problems running it
- **fabrizio.salmi@gmail.com** for security reports

## Licence

Contributions are licensed under the [MIT License](https://github.com/fabriziosalmi/brandkit/blob/main/LICENSE), the same as the project.
