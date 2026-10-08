---
title: Privacy
description: Data handling, storage lifecycle, and privacy practices in BrandKit.
---

# Privacy

Two distinct components are documented here:

- **[The BrandKit application](#the-application)**: the self-hosted software running in your environment.
- **[This documentation site](#this-documentation-site)**: a static site published via GitHub Pages.

BrandKit is not operated as a centralized multi-tenant service; there is no cloud provider collecting telemetry.

---

## The application

### Data egress

**Zero outbound transmission.** Image operations execute in-process via Pillow, NumPy, and ONNX Runtime. Images, file identifiers, and metadata are never transmitted to external services.

Tailwind CSS and Alpine.js assets are vendored locally under `static/vendor/` and served same-origin. The browser makes no third-party network calls during normal interface operation.

The single outbound network call the container can initiate is downloading the ONNX model (`u2net`) on initial use of neural background removal, fetched directly from official release assets. No user data or images are transmitted. This request can be eliminated entirely by pre-seeding `~/.u2net/` (see [Background removal](/guide/background-removal#choosing-a-model)).

The application contains no analytics, tracking pixels, crash reporters, or phone-home pings.

### Local disk storage

| File path | Purpose | Lifecycle trigger |
| --- | --- | --- |
| `static/uploads/<uuid>_<name>` | Ingested master image (EXIF-stripped) | Upload ingestion |
| `static/uploads/<name>_<format>.<ext>` | Rendered target format | Pipeline execution |
| `static/uploads/<name>_brandkit_<timestamp>.zip` | Export package archive | Pipeline execution |
| `static/uploads/cache/` | Cached canvas intermediates | Pipeline execution |
| `~/.u2net/*.onnx` | rembg neural model weights | First background removal |

When running Docker, `static/uploads/` is bind-mounted directly to the host filesystem.

### Metadata stripping

EXIF metadata is stripped from master uploads unconditionally by decoding and re-serializing the pixel buffer through Pillow prior to storage. This process removes GPS coordinates, timestamps, camera identifiers, and embedded thumbnails.

The `strip_metadata` toggle in the UI specifically controls ICC color profile retention on downstream generated target files.

::: tip Verification
```bash
exiftool static/uploads/<uuid>_yourphoto.jpg
```
The output confirms only filesystem attributes remain.
:::

### Retention and lifecycle

A daemon cleanup thread evaluates `static/uploads/` and its `cache/` directory, removing files that exceed the retention ceiling (**default: 24 hours, swept hourly**). The thread operates under both Gunicorn and development runtimes.

::: tip Recommended retention for shared environments
On multi-user instances where users download generated archives immediately, shorten the retention window:

```bash
# .env
BRANDKIT_RETENTION_HOURS=1
BRANDKIT_CLEANUP_INTERVAL_HOURS=0.25
```

Consult [Performance & caching](/guide/performance#file-cleanup) and [Environment variables](/reference/environment#the-cleanup-variables).
:::

::: warning Host persistence
Retention enforcement requires an active container. If the container process is stopped, existing assets in host bind mounts remain until the container resumes or files are manually purged.
:::

### Access control

Files within `static/uploads/` are served by Flask without authentication using predictable file paths (`<basename>_<format>.<ext>`).

On shared or networked instances, anyone with network access to the origin can retrieve stored assets. When processing confidential or unreleased brand materials, enforce authentication at the reverse proxy layer (see [Deployment](/guide/deployment)).

### Application logging

Logs stream to stdout at `INFO` level, containing timestamped request paths, format configurations, and execution durations. Image payload bytes are never logged.

### Operational governance

If you host BrandKit for third parties, you act as the data controller for uploaded content. Implement appropriate access policies, network isolation, and retention parameters accordingly.

---

## This documentation site

Published as static HTML via **GitHub Pages**.

| Metric | Practice |
| --- | --- |
| **Cookies** | None |
| **Analytics** | None |
| **Trackers** | None |
| **Third-party scripts** | None: stylesheets and client scripts are served same-origin |
| **Search** | VitePress local search: query indexing runs client-side in the browser |

### Hosting infrastructure

GitHub Pages processes incoming HTTP requests in accordance with the [GitHub Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement). The BrandKit project does not receive or manage visitor logs.

### Inquiries

Contact: **fabrizio.salmi@gmail.com**. Security disclosures must follow the [security policy](/security#reporting-a-vulnerability).
