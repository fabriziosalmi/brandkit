---
title: What is BrandKit?
description: BrandKit is a self-hosted Flask application that turns one source image into a complete set of correctly-sized brand assets.
---

# What is BrandKit?

BrandKit is a small, self-hosted web application that solves one narrow, annoying problem: **you have a logo, and you need it in thirty different sizes by tomorrow.**

You upload one image. BrandKit resizes, pads, crops and converts it into every format you tick — Open Graph cards, favicons, PWA icons, Instagram posts, LinkedIn banners, ebook covers, A4 print sheets — and hands you back a ZIP.

It runs on your own machine or your own server. Your images are processed in-process by Pillow and never sent to a third-party API.

## Who it is for

- **Solo developers and small teams** shipping a product who need a favicon, an OG image and an app icon *right now*, without opening a design tool.
- **Anyone doing client work** who has to deliver "the logo pack" and would rather not resize twenty files by hand.
- **Self-hosters** who do not want to paste their client's unreleased branding into a free online converter.

## What it actually does

<div class="tip custom-block" style="padding-top: 8px">

The pipeline is deliberately simple, and it runs in this order for every generation.

</div>

1. **Upload & validate** — extension is checked against an allowlist (`png`, `jpg`, `jpeg`, `gif`, `webp`), size against `MAX_CONTENT_LENGTH`, and the file is re-encoded through Pillow. EXIF metadata is stripped unconditionally at this step.
2. **Analyse** *(optional)* — the app samples the image to find its prominent colour and to detect whether it contains a significant white region. That drives the "fill white with prominent colour" behaviour and the gradient backgrounds.
3. **Preprocess once** — background removal, colour grading, sharpening, watermarking, vignette, auto-crop and so on are applied a single time to the source, not per format.
4. **Render every format** — the preprocessed image is fitted into each selected canvas, then encoded into each selected output type.
5. **Package** — everything goes into a ZIP served from `/download-zip/<filename>`, and the browser shows a preview grid.

## What it is not

- **Not a design tool.** There is no canvas, no layers, no typography. It resizes and converts what you give it.
- **Not multi-tenant.** There are no accounts, no per-user isolation and no authorisation layer. If you expose it publicly, put an authenticating reverse proxy in front — see [Deployment](/guide/deployment).
- **Not a hosted service.** There is no brandkit.com. You run the container.

## The stack

| Layer | What it uses |
| --- | --- |
| Web framework | Flask 3.1 (`app.py`, a single module) |
| Image processing | Pillow, NumPy, OpenCV (optional), scikit-image |
| Background removal | rembg + onnxruntime (optional, `u2net` family) |
| Frontend | Alpine.js + Tailwind, both **vendored and served same-origin** — no CDN calls |
| Security middleware | Flask-WTF (CSRF), Flask-Limiter, Flask-Talisman (CSP + headers) |
| Caching | Flask-Caching in memory, plus an on-disk cache keyed by content hash |
| Packaging | Docker / Docker Compose, gunicorn via `entrypoint.sh` |

The entire backend is one file — [`app.py`](https://github.com/fabriziosalmi/brandkit/blob/main/app.py), about 1,500 lines. The entire frontend is one Jinja template. That is intentional: you can read all of it in an afternoon.

## Next steps

- [Getting started](/guide/getting-started) — install and run it locally
- [Running with Docker](/guide/docker) — the recommended path
- [The generation workflow](/guide/usage) — what each control in the UI does
