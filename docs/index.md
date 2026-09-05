---
layout: home
title: Self-hosted brand asset generator
titleTemplate: BrandKit

hero:
  name: BrandKit
  text: One logo in, a whole brand kit out.
  tagline: A self-hosted Flask app that turns a single image into 45+ production-ready sizes for web, social, mobile and print — with AI background removal, colour analysis and PNG/JPG/WebP/ICO output. No accounts, no uploads to anyone else's server.
  image:
    src: /favicon.svg
    alt: BrandKit
  actions:
    - theme: brand
      text: Get started
      link: /guide/getting-started
    - theme: alt
      text: What is BrandKit?
      link: /guide/
    - theme: alt
      text: View on GitHub
      link: https://github.com/fabriziosalmi/brandkit

features:
  - icon: 📐
    title: 45+ formats, one upload
    details: Open Graph cards, favicons, app icons, Instagram posts, hero banners, ebook covers, A4 print. Pick a category or search the catalogue — every size is defined in a JSON file you can edit.
    link: /reference/format-catalogue
    linkText: Browse the catalogue
  - icon: ✂️
    title: AI background removal
    details: rembg strips the background locally with u2net, then you composite onto a solid colour, a gradient, or keep transparency. Edge smoothing, auto-crop and drop shadows included.
    link: /guide/background-removal
    linkText: How it works
  - icon: 🎨
    title: Real image preprocessing
    details: Hue shift, colour temperature, saturation, contrast, sharpening, vignette, watermarking, blur and noise reduction — applied once, before every format is rendered.
    link: /guide/preprocessing
    linkText: All the knobs
  - icon: 🔒
    title: Runs on your own box
    details: CSRF protection, rate limiting, a strict Content Security Policy, mandatory EXIF stripping and no third-party CDN calls. Your images never leave the container.
    link: /security
    linkText: Security posture
  - icon: 🐳
    title: Docker in one command
    details: docker compose up -d and you have it on :8000. Or pip install -r requirements.txt and python app.py for local hacking.
    link: /guide/docker
    linkText: Run it
  - icon: ⚡
    title: Cached and memory-aware
    details: Processed images are cached by content hash, old uploads are swept on a schedule, and psutil-backed memory checks keep large batches from blowing up the process.
    link: /guide/performance
    linkText: Performance notes
---

<div class="vp-doc" style="max-width: 1152px; margin: 0 auto; padding: 0 24px 64px;">

## 60 seconds to your first brand kit

```bash
git clone https://github.com/fabriziosalmi/brandkit.git
cd brandkit
docker compose up -d --build
# open http://localhost:8000
```

Drop in a logo, tick the formats you want, hit **Generate**, download the ZIP. That is the whole product.

## What you get back

A single archive containing every selected format in every selected output type, named predictably (`<yourlogo>_website.png`, `<yourlogo>_favicon.ico`, …), plus a preview grid in the browser so you can check each crop before you download.

## Where to go next

| If you want to… | Read |
| --- | --- |
| Get it running | [Getting started](/guide/getting-started) · [Docker](/guide/docker) |
| Understand the UI | [The generation workflow](/guide/usage) |
| Add or resize a format | [Configuration](/reference/configuration) |
| Call it from a script | [HTTP endpoints](/reference/http-api) |
| Put it on the internet | [Deployment](/guide/deployment) |
| Know what happens to your images | [Privacy](/privacy) |
| Report a vulnerability | [Security policy](/security) |

</div>
