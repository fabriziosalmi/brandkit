---
title: Changelog
description: Release history for BrandKit.
---

# Changelog

Released versions, newest first. Source of truth is the [GitHub releases page](https://github.com/fabriziosalmi/brandkit/releases).

::: warning The repository `CHANGELOG.md` is out of step
`CHANGELOG.md` in the repository root describes a `2.0.0` release. **No `v2.0.0` tag exists** — the published tags are `v1.0.0`, `v1.1.0`, `v1.1.2` and `v1.1.3`. Its feature list is accurate; its version numbers are not. This page reflects the tags that were actually cut.
:::

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
