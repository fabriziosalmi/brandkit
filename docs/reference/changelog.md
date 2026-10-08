---
title: Changelog
description: Release history for BrandKit.
---

# Changelog

Released versions, ordered from newest to oldest. Source of truth is the [GitHub releases page](https://github.com/fabriziosalmi/brandkit/releases).

::: warning Repository changelog synchronization
The root `CHANGELOG.md` outlines planned feature revisions ahead of version tags. Canonical published releases are documented below.
:::

## v1.1.4 (16 September 2026) {#v1-1-4}

Architecture decoupling, automated test coverage, structured observability, and atomic data persistence.

**Added**
- **Automated Test Suite**: Comprehensive test suite (48 tests) using `pytest` covering unit image processing, HTTP route workflows, boundary security validations (CSRF rejection, path traversal prevention, file size limits), and atomic caching.
- **CI Integration**: Upgraded `.github/workflows/ci.yml` from import smoke testing to run `pytest -v` across Python 3.11 and 3.12.
- **Request Correlation**: Emits and propagates `X-Request-ID` across Flask request context (`g.request_id`), response headers, and root logger formatters for distributed tracing.
- **Application Factory**: Converted `app.py` to an explicit `create_app()` factory with lifecycle control, while maintaining full backward-compatible module re-exports.
- **Atomic File Persistence**: EXIF-stripped image uploads and resized disk cache entries now use atomic temporary write and rename semantics (`os.replace`) to eliminate file tearing risks.
- **Configuration Validation**: Introduced schema validation for custom `config.json` definitions, rejecting malformed format dimensions before runtime rendering.

**Security**
- `pillow` -> 12.3.0 (closes 11 advisories: heap out-of-bounds writes in `ImageCmsTransform.apply()`, `Image.paste()`/`crop()` and `ImageFilter.RankFilter`; decompression-bomb bypasses via `PdfParser`, `GdImageFile`, and the BDF/PCF/`FontFile` font paths; an EPS infinite loop; a TGA heap-disclosure; and `WindowsViewer.get_command()` command injection)
- `rembg` -> 2.0.75 (SSRF and weak default CORS in the rembg server; path traversal via custom model loading)
- `Flask` -> 3.1.3 (missing `Vary: Cookie`)
- `Pygments` -> 2.20.0 (ReDoS in GUID regex)
- `numpy` -> 2.3.5, `scikit-image` -> 0.26.0, `opencv-python`/`opencv-python-headless` -> 4.14.0.94: matches new `rembg` baseline within `numba`'s `numpy<2.4` constraint
- Removed `zipfile36` (unused dependency)
- **CSP tightened**: Dropped obsolete CDN rules for `cdn.tailwindcss.com` and `cdn.jsdelivr.net`.
- **`/download-zip/<filename>` hardened**: Filenames must pass `secure_filename()` validation, end in `.zip`, and resolve strictly within the designated uploads directory.

**Fixed**
- **Structured Logging**: Replaced uninstrumented `print()` calls in config loading, cleanup routines, and error paths with standard `logging.info()`, `logging.warning()`, and `logging.error()`.
- **`BRANDKIT_SECRET_KEY` Environment Support**: Reads signing keys from `BRANDKIT_SECRET_KEY` or `FLASK_SECRET_KEY`. Logs a warning if an ephemeral key is generated.
- **Gunicorn Cleanup Execution**: Cleanup thread starts at module import time, ensuring active sweeps when running under multi-worker WSGI containers.
- Fixed `python app.py` port binding to honor the `PORT` environment variable.

**Changed**
- **Modular Architecture**: Decoupled core image transformations into `image_processing.py`, configuration parsing into `config_utils.py`, and memory/file sweeps into `cleanup.py`.
- `FLASK_ENV=production` deprecated in favor of explicit configuration.

## v1.1.3 (8 July 2026) {#v1-1-3}

Security hardening and asset dependency vendoring.

**Security**
- `pillow` -> 12.2.0
- `urllib3` -> 2.7.0
- `protobuf` -> 6.33.5
- `requests` -> 2.33.0
- `Werkzeug` -> 3.1.6
- `idna` -> 3.15

**Changed**
- **Vendored Client Assets**: Tailwind CSS and Alpine.js assets vendored under `static/vendor/` and served same-origin ([#19](https://github.com/fabriziosalmi/brandkit/pull/19)), eliminating third-party network egress.
- CI pipeline modernized with matrix builds across Python 3.11 and 3.12 ([#18](https://github.com/fabriziosalmi/brandkit/pull/18)).

## v1.1.2 (6 December 2025) {#v1-1-2}

**Fixed**
- rembg import handling and container port binding ([#2](https://github.com/fabriziosalmi/brandkit/pull/2))

**Changed**
- Documentation review and synchronization ([#1](https://github.com/fabriziosalmi/brandkit/pull/1))
- Dependency updates: `urllib3` -> 2.6.0, `werkzeug` -> 3.1.4

## v1.1.0 (25 June 2025) {#v1-1-0}

Feature expansion and preprocessing pipeline addition.

**Added**
- Neural background removal via rembg (models: auto, person, object, anime)
- Background color replacement: transparent, solid, or radial gradient based on extracted dominant hues
- Alpha edge smoothing
- Image preprocessing filters: grayscale, B&W, invert, contrast, hue shift, temperature, saturation, brightness, auto-crop, noise reduction, sharpen, blur, vignette, drop shadow, and watermarks
- Variations mode: batch generation of ten tonal treatments per format
- Format search filtering and category classification
- Keyboard shortcuts dialog (<kbd>Shift</kbd>+<kbd>?</kbd>)
- WebP and ICO encoding support
- Bulk ZIP export archive

**Enhanced**
- CSRF protection, rate limiting, and security headers via Flask-WTF, Flask-Limiter, and Flask-Talisman
- Automated EXIF sanitization
- Disk caching keyed by content hash, `psutil` memory monitoring, and scheduled cleanup

## v1.0.0 (25 April 2025) {#v1-0-0}

Initial release.

**Added**
- Single-source image upload and multi-format generation
- PNG and JPG output encodings
- Resizing and padding pipeline
- Docker containerization
- Format selection interface

---

## Versioning specification

Releases adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Changelog categories follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
