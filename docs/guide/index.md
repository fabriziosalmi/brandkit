---
title: What is BrandKit?
description: BrandKit is a self-hosted application that turns a single source image into a complete set of correctly-sized brand assets.
---

# What is BrandKit?

BrandKit is a self-hosted web utility engineered for automated brand asset derivation.

You upload a single source image. BrandKit resizes, pads, crops, and converts it into each selected format (Open Graph cards, favicons, PWA icons, social banners, document headers, and print sheets) and packages the outputs into a ZIP archive.

Processing executes entirely in-process using Pillow, OpenCV, and ONNX Runtime. Images are never transmitted to third-party endpoints.

## Target use cases

- **Product engineering teams** generating favicons, Open Graph cards, and app manifests during deployment without requiring heavy desktop design applications.
- **Client brand delivery** producing standardized format suites from vector or high-resolution raster master logos.
- **Privacy-sensitive deployments** operating in air-gapped or internal network environments where asset leakage to third-party SaaS converters is unacceptable.

## Architecture pipeline

<div class="tip custom-block" style="padding-top: 8px">

The image processing pipeline executes sequentially for each batch generation.

</div>

1. **Ingestion & Validation**: File extensions are checked against an explicit allowlist (`png`, `jpg`, `jpeg`, `gif`, `webp`), size is constrained to `MAX_CONTENT_LENGTH`, and pixel buffers are parsed through Pillow. EXIF metadata is systematically stripped.
2. **Telemetry & Analysis**: The engine samples color distributions to extract dominant hues and evaluate transparent/white boundary coverage for background compositing.
3. **Master Preprocessing**: Background removal, color adjustments, sharpening, watermarking, and auto-crop operations are computed once against the master buffer rather than per-output canvas.
4. **Target Rendering**: The processed master is scaled and fitted into each target canvas specification, then encoded into the requested output encodings.
5. **Archive Assembly**: Assets are packaged into a downloadable ZIP archive with metadata manifests, while the UI displays interactive previews and high-density result tables.

## Scope boundaries

- **Not a vector illustration or layout tool:** Operates as a headless derivation engine rather than a canvas editor.
- **Single-tenant runtime:** Does not implement multi-tenant user authentication or isolated tenant storage natively. Terminate behind an authenticating reverse proxy for remote access (see [Deployment](/guide/deployment)).
- **Self-hosted:** Containerized for private infrastructure.

## Technical stack

| Component | Implementation |
| --- | --- |
| HTTP service | Flask 3.1 (`app.py`) |
| Image pipeline | Pillow, NumPy, OpenCV, scikit-image |
| Neural segmentation | rembg, ONNX Runtime (`u2net` architecture) |
| Frontend | Alpine.js, Tailwind CSS (vendored and served same-origin without external CDN dependencies) |
| Security | Flask-WTF (CSRF), Flask-Limiter, Flask-Talisman (Content Security Policy) |
| Cache layer | Memory caching plus content-hash disk persistence |
| Container runtime | Docker, Docker Compose, Gunicorn |

## Next steps

- [Getting started](/guide/getting-started): installation and setup
- [Running with Docker](/guide/docker): container orchestration
- [The generation workflow](/guide/usage): configuration parameters and processing controls
