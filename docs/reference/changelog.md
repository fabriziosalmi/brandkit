---
title: Changelog
description: Release history for BrandKit.
---

# Changelog

Released versions, newest first. Source of truth is the [GitHub releases page](https://github.com/fabriziosalmi/brandkit/releases).

::: warning The repository `CHANGELOG.md` is out of step
`CHANGELOG.md` in the repository root describes a `2.0.0` release. **No `v2.0.0` tag exists** — the published tags are `v1.0.0`, `v1.1.0`, `v1.1.2` and `v1.1.3`. Its feature list is accurate; its version numbers are not. This page reflects the tags that were actually cut.
:::

## v1.1.4 — 16 September 2026 {#v1-1-4}

Latest release focusing on architecture decoupling, test automation, structured observability, and atomic data persistence.

**Added**
- **Automated Test Suite**: Added a comprehensive test suite (48 tests) using `pytest` covering unit image processing, HTTP route workflows, boundary security validations (CSRF rejection, path traversal prevention, file size limits), and atomic caching.
- **CI Integration**: Upgraded `.github/workflows/ci.yml` from a simple import smoke test to run `pytest -v` across a matrix of Python 3.11 and 3.12.
- **Request Correlation**: Emits and propagates `X-Request-ID` across Flask request context (`g.request_id`), response headers, and root logger formatters for distributed tracing.
- **Application Factory**: Converted `app.py` to an explicit `create_app()` factory with lifecycle control, while maintaining full backward-compatible module re-exports.
- **Atomic File Persistence**: EXIF-stripped image uploads and resized disk cache entries now use atomic temporary write and rename semantics (`os.replace`) to eliminate file tearing risks.
- **Configuration Validation**: Introduced schema validation for custom `config.json` definitions, rejecting malformed format dimensions before runtime rendering.

**Security**
- `pillow` → 12.3.0 (closes 11 advisories: heap out-of-bounds writes in `ImageCmsTransform.apply()`, `Image.paste()`/`crop()` and `ImageFilter.RankFilter`; decompression-bomb bypasses via `PdfParser`, `GdImageFile`, and the BDF/PCF/`FontFile` font paths; an EPS infinite loop; a TGA heap-disclosure; and `WindowsViewer.get_command()` command injection)
- `rembg` → 2.0.75 (SSRF and weak default CORS in the rembg server; path traversal via custom model loading — neither reachable from BrandKit's usage, which only calls `remove()`/`new_session()` with hard-coded model names, but pinned forward regardless)
- `Flask` → 3.1.3 (missing `Vary: Cookie`)
- `Pygments` → 2.20.0 (ReDoS in the GUID regex)
- `numpy` → 2.3.5, `scikit-image` → 0.26.0, `opencv-python`/`opencv-python-headless` → 4.14.0.94 — required to satisfy the new `rembg` floor while staying inside `numba`'s `numpy<2.4` ceiling
- Removed `zipfile36`, pinned but never imported and unmaintained since 2017
- **CSP tightened**: `cdn.tailwindcss.com` and `cdn.jsdelivr.net` dropped from `script-src`. They had been left behind when the libraries were vendored in v1.1.3, so no third-party script origin is permitted any more.
- **`/download-zip/<filename>` hardened**: the name must survive `secure_filename()` unchanged and end in `.zip`, and the resolved path is confirmed to be inside the upload folder before anything is served.

**Fixed**
- **Structured Logging**: Replaced uninstrumented `print()` calls in config loading, cleanup routines, and error paths with standard `logging.info()`, `logging.warning()`, and `logging.error()`.
- **`BRANDKIT_SECRET_KEY` is now read from the environment** (`FLASK_SECRET_KEY` accepted as an alias). The key was previously `os.urandom(24)` on every import, so sessions broke on restart and multiple gunicorn workers rejected each other's CSRF tokens. When it is unset the behaviour is unchanged but a warning is logged.
- **The cleanup thread now runs under gunicorn.** It lived inside `if __name__ == '__main__':`, which gunicorn never executes, so the Docker deployment never deleted anything and `static/uploads/` grew without bound. It is started at import time and configurable via `BRANDKIT_CLEANUP_ENABLED`, `BRANDKIT_CLEANUP_INTERVAL_HOURS` and `BRANDKIT_RETENTION_HOURS`. A failing sweep is logged instead of killing the thread.
- `python app.py` now honours `PORT`, which it previously ignored while `entrypoint.sh` respected it.

**Changed**
- **Modular Architecture**: Decoupled core image transformations into `image_processing.py`, configuration parsing into `config_utils.py`, and memory/file sweeps into `cleanup.py`.
- `FLASK_ENV=production` no longer gates anything and can be removed from `docker-compose.yml`.

## v1.1.3 — 8 July 2026 {#v1-1-3}

Current release. A security and infrastructure pass with no user-facing feature changes.

**Security**
- `pillow` → 12.2.0 (high)
- `urllib3` → 2.7.0 (high)
- `protobuf` → 6.33.5 (high)
- `requests` → 2.33.0 (medium)
- `Werkzeug` → 3.1.6 (medium)
- `idna` → 3.15 (medium)

**Changed**
- **Tailwind and Alpine.js are now vendored and served same-origin** ([#19](https://github.com/fabriziosalmi/brandkit/pull/19)). Previously they were pulled from `cdn.tailwindcss.com` and `cdn.jsdelivr.net` on every page load. The app now makes no third-party requests at all — it works on an air-gapped host, and nobody outside your network learns that you loaded the page.
- CI replaced. The repository shipped a "Django CI" workflow that had nothing to do with this project; it is now a real matrix build against Python 3.11 and 3.12 that installs dependencies and imports the app ([#18](https://github.com/fabriziosalmi/brandkit/pull/18)).

## v1.1.2 — 6 December 2025 {#v1-1-2}

**Fixed**
- rembg import failure, and Flask now binds so the container is reachable from outside ([#2](https://github.com/fabriziosalmi/brandkit/pull/2), thanks [@utkarshainos](https://github.com/utkarshainos))

**Changed**
- Documentation audit and synchronisation ([#1](https://github.com/fabriziosalmi/brandkit/pull/1))
- `urllib3` → 2.6.0, `werkzeug` → 3.1.4

## v1.1.0 — 25 June 2025 {#v1-1-0}

The release that made BrandKit what it is now.

**Added**
- AI background removal via rembg, with model selection: auto, person, object, anime
- Background colour replacement — transparent, solid, or a smart radial gradient built from the image's prominent colour
- Edge smoothing on cutouts
- The full preprocessing suite: grayscale, B&W, invert, contrast, hue shift, temperature, saturation, brightness, auto-crop, noise reduction, sharpen, blur, vignette, drop shadow, watermarking
- Variations mode — ten colour treatments per format
- Format search and category grouping
- Keyboard shortcuts, with <kbd>Shift</kbd>+<kbd>?</kbd> for help
- WebP and ICO output alongside PNG and JPG
- Bulk ZIP download

**Enhanced**
- CSRF protection, rate limiting, CSP and security headers via Flask-WTF, Flask-Limiter and Flask-Talisman
- Metadata stripping on upload
- Disk cache keyed by content hash, `psutil`-backed memory monitoring, scheduled cleanup
- Rebuilt interface on Tailwind CSS and Alpine.js

## v1.0.0 — 25 April 2025 {#v1-0-0}

Initial release.

**Added**
- Image upload and multi-format generation from a single source
- PNG and JPG output
- Resizing and padding
- Docker containerisation
- Basic format selection UI

---

## Versioning

[Semantic Versioning](https://semver.org/spec/v2.0.0.html). Major for breaking changes, minor for backward-compatible features, patch for fixes and dependency bumps.

Changes are grouped as **Added**, **Changed**, **Deprecated**, **Removed**, **Fixed** and **Security**, following [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
