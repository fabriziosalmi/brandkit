---
layout: home
title: Self-hosted brand asset generator
titleTemplate: BrandKit

hero:
  name: BrandKit
  text: Asset generation engine
  tagline: A self-hosted Flask application that transforms a single image into 45+ production-ready sizes for web, social, mobile, and print, featuring background removal, color analysis, and multi-format encoding (PNG, JPG, WebP, ICO). Self-contained with no external data transmission.
  image:
    src: /favicon.svg
    alt: BrandKit
  actions:
    - theme: brand
      text: Get started
      link: /guide/getting-started
    - theme: alt
      text: Architecture
      link: /guide/
    - theme: alt
      text: GitHub
      link: https://github.com/fabriziosalmi/brandkit

features:
  - title: 45+ formats, one upload
    details: Open Graph cards, favicons, application icons, Instagram posts, hero banners, document covers, and print sizes. Filter by category or search the catalog. Every dimension is declared in config.json.
    link: /reference/format-catalogue
    linkText: Browse catalog
  - title: Background removal
    details: Local segmentation via rembg with u2net models. Composite onto solid colors, dominant palette fills, or preserve alpha transparency. Edge smoothing and auto-crop included.
    link: /guide/background-removal
    linkText: Implementation details
  - title: Image preprocessing
    details: Adjust hue, color temperature, saturation, contrast, sharpness, vignette, watermark, blur, and noise reduction prior to format rendering.
    link: /guide/preprocessing
    linkText: Preprocessing options
  - title: Self-hosted security
    details: CSRF protection, rate limiting, strict Content Security Policy, mandatory EXIF stripping, and vendored assets. No third-party network telemetry.
    link: /security
    linkText: Security posture
  - title: Single-command deployment
    details: Deploy with docker compose up -d on port 8000, or run directly via Python 3.11+ virtual environment.
    link: /guide/docker
    linkText: Deployment guide
  - title: Content caching & memory awareness
    details: Operations are cached by content hash, outdated uploads are purged via background worker, and psutil monitoring guards process memory limits.
    link: /guide/performance
    linkText: Performance guide
---

<div class="vp-doc" style="max-width: 1152px; margin: 0 auto; padding: 0 24px 64px;">

## Quick Start

```bash
git clone https://github.com/fabriziosalmi/brandkit.git
cd brandkit
docker compose up -d --build
# Access http://localhost:8000
```

Upload a master asset, select target formats, and click **Generate Brand Kit** to download the consolidated ZIP archive.

## Output Specifications

A structured archive containing every configured format in each selected encoding format (`<name>_website.png`, `<name>_favicon.ico`, etc.), accompanied by a real-time inspection grid in the browser.

## Documentation Navigation

| Objective | Reference |
| :--- | :--- |
| Initial Setup | [Getting started](/guide/getting-started) · [Docker](/guide/docker) |
| Interface & Workflow | [Generation workflow](/guide/usage) · [Keyboard shortcuts](/guide/keyboard-shortcuts) |
| Format Specifications | [Configuration](/reference/configuration) · [Catalog](/reference/format-catalogue) |
| Automation & API | [HTTP endpoints](/reference/http-api) |
| Production Hosting | [Deployment](/guide/deployment) · [Environment variables](/reference/environment) |
| Security & Compliance | [Security policy](/security) · [Privacy](/privacy) |

</div>
