---
title: Contributing
description: How to report bugs, propose features and open pull requests against BrandKit.
---

# Contributing

Contributions are welcome. The project is maintained with a straightforward contribution workflow.

The authoritative version of this document is [`CONTRIBUTING.md`](https://github.com/fabriziosalmi/brandkit/blob/main/CONTRIBUTING.md) in the repository.

## Before you start

Everyone participating is bound by the [Code of Conduct](/code-of-conduct).

## Reporting a bug

Open a [bug report](https://github.com/fabriziosalmi/brandkit/issues/new?template=bug_report.md) and include:

- Expected behavior versus observed behavior
- Exact steps to reproduce the issue
- Service logs: `docker compose logs brandkit` or terminal console output
- Python version, or Docker and Compose versions
- Operating system details
- Sample source image, if non-confidential and required to reproduce

::: danger Never report a security issue as a public issue
Email **fabrizio.salmi@gmail.com** directly. Refer to the [security policy](/security#reporting-a-vulnerability).
:::

## Proposing a feature

Open a [feature request](https://github.com/fabriziosalmi/brandkit/issues/new?template=feature_request.md). Describe the concrete problem before the proposed solution, clarifying the specific user need.

Common contribution areas:

- **New target formats:** Declared in `config.json`. Platform image dimension updates can be submitted as single-line pull requests.
- **Documentation improvements:** Every documentation page includes an "Edit this page on GitHub" reference.

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

`FLASK_ENV=development` enables auto-reload and the Werkzeug debugger on `http://127.0.0.1:8000`. Never expose this mode on public networks.

### Architecture Map

| File | Purpose |
| :--- | :--- |
| `app.py` | Backend application factory, route dispatching, and security middleware |
| `image_processing.py` | Image resizing, color grading, background segmentation, and transformations |
| `cleanup.py` | Background retention sweeper and garbage collection |
| `config_utils.py` | Configuration ingestion and validation utilities |
| `templates/index.html` | High-density Linear/Vercel frontend workbench with Alpine.js |
| `config.json` | Format specifications and preprocessing parameter defaults |
| `static/vendor/` | Vendored Tailwind and Alpine libraries (served same-origin) |
| `docs/` | VitePress documentation source files |

## Pull requests

1. Fork and branch: `git checkout -b feat/short-description`
2. Implement your modification
3. Run the automated test suite
4. Commit using Conventional Commits prefixes (`feat:`, `fix:`, `docs:`, `ci:`, `build(deps):`)
5. Open the pull request against `main`, detailing changes and validation steps

Keep pull requests focused and atomic.

### Continuous Integration (CI)

Every push and pull request executes the [CI workflow](https://github.com/fabriziosalmi/brandkit/blob/main/.github/workflows/ci.yml): installing `requirements.txt` on Python 3.11 and 3.12, followed by `pytest -v`.

Execute tests locally with:

```bash
pytest -q
```

### Manual Verification Checklist

- [ ] Web workbench loads and displays all format groups
- [ ] Ingestion bench processes single and batch images
- [ ] Clipboard paste (`⌘+V` / `Ctrl+V`) loads images properly
- [ ] Theme switcher toggles cleanly between Light, Dark, and System modes with zero FOUC
- [ ] PNG outputs preserve alpha transparency; JPG flattens to specified matte
- [ ] ICO output generates multi-size streams when `favicon` is selected
- [ ] Background removal functions as expected or falls back cleanly
- [ ] ZIP archive contains all expected asset outputs
- [ ] `POST /upload` rejects requests lacking CSRF tokens with HTTP `400`
- [ ] Rate limits enforce HTTP `429` on excessive upload attempts

### Documentation Verification

When modifying application behavior, update documentation files accordingly.

```bash
npm install
npm run docs:dev      # Dev server on http://localhost:5173
npm run docs:build    # Production build and dead-link validation
```

::: info Dependency Overrides
VitePress 1.6.4 requires specific security overrides in `package.json`:

```json
"overrides": {
  "esbuild": "^0.25.12",
  "vite": "^6.4.3"
}
```

The combination is verified: the site builds and renders correctly.
:::

## Code Style

**Python**: Adhere to PEP 8, 4 spaces indentation, `snake_case`. Document non-trivial functions with docstrings.

**Commits**: Use imperative mood with Conventional Commits prefixes.

## Community & Support

- [GitHub Issues](https://github.com/fabriziosalmi/brandkit/issues) for defect tracking and features
- [Troubleshooting](/guide/troubleshooting) for operational diagnostics
- **fabrizio.salmi@gmail.com** for responsible security disclosure

## License

BrandKit is licensed under the MIT License. See [LICENSE](https://github.com/fabriziosalmi/brandkit/blob/main/LICENSE) for terms.
