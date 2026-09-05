---
title: Privacy
description: What BrandKit does with your images, what it stores, for how long, and what this documentation site collects.
---

# Privacy

Two different things are covered here, and they are worth keeping apart.

- **[The BrandKit application](#the-application)** — the software you run. It has no telemetry and sends nothing anywhere, but it does write your images to disk.
- **[This documentation site](#this-documentation-site)** — a static site on GitHub Pages.

Neither is operated as a service by anyone. There is no hosted BrandKit, so there is no operator collecting anything.

---

## The application

### What leaves your machine

**Nothing.** Images are processed in-process by Pillow, NumPy and ONNX Runtime. No image, no filename and no metadata is ever transmitted to a third party.

Since v1.1.3, Tailwind and Alpine.js are vendored under `static/vendor/` and served from your own origin, so **loading the page makes no third-party requests at all**. Earlier versions fetched them from `cdn.tailwindcss.com` and `cdn.jsdelivr.net`, which disclosed your IP address and the fact that you loaded the page to those CDNs. If you are still on v1.1.2 or earlier, that is a reason to upgrade.

The one outbound connection the application can make is **rembg downloading its ONNX model** on first use of background removal, from GitHub's release infrastructure. It transmits no data about you or your image — it is a plain file download — and you can eliminate it entirely by pre-seeding `~/.u2net/`. See [Background removal](/guide/background-removal#choosing-a-model).

There is no analytics, no telemetry, no crash reporting, no update check and no phone-home of any kind.

### What is written to disk

| Path | Contents | Written when |
| --- | --- | --- |
| `static/uploads/<uuid>_<name>` | your uploaded original, EXIF-stripped | on every upload |
| `static/uploads/<name>_<format>.<ext>` | every generated asset | on every generation |
| `static/uploads/<name>_brandkit_<timestamp>.zip` | the download archive | on every generation |
| `static/uploads/cache/` | resized intermediates, keyed by content hash | on every generation |
| `~/.u2net/*.onnx` | rembg models | first background removal |

In Docker, `static/uploads/` is bind-mounted to the host — so these files are in your working copy, not confined to the container.

### Metadata

EXIF is stripped from every upload, unconditionally, by re-encoding the image through a fresh Pillow buffer before anything else touches it. That removes GPS coordinates, timestamps, camera and lens identifiers, and any embedded thumbnail.

This happens whether or not you enable the `strip_metadata` option — that switch controls metadata and ICC profiles on the **generated** files, which is a separate step.

::: tip Verify it yourself
```bash
exiftool static/uploads/<uuid>_yourphoto.jpg
```
You should see file-system attributes and nothing else.
:::

### Retention

A background thread deletes everything in `static/uploads/` and its `cache/` subdirectory once it is past the retention window — **24 hours by default, swept hourly**. It runs under gunicorn as well as under the development server, so the standard `docker compose up` does clean up after itself.

::: tip 24 hours is a default, not a recommendation
Generated assets are readable by anyone who can reach the instance. If your users download within seconds, there is no reason to keep the files for a day:

```bash
# .env
BRANDKIT_RETENTION_HOURS=1
BRANDKIT_CLEANUP_INTERVAL_HOURS=0.25
```

Full details in [Performance & caching](/guide/performance#file-cleanup) and [Environment variables](/reference/environment#the-cleanup-variables).
:::

::: warning The sweep is per-container
Retention is enforced by the running application. If you stop the container and leave the bind-mounted `static/uploads/` directory on the host, nothing deletes it — the files sit there until the container comes back or you remove them yourself.
:::

### Who can read the files

Everything under `static/uploads/` is served by Flask **without any authentication or authorisation check**, and filenames are predictable (`<basename>_<format>.<ext>`).

On a localhost instance that is irrelevant. On any instance more than one person can reach, it means **anyone who can load the page can fetch anyone else's assets** by guessing a name — and search-engine crawlers can index them if the instance is public.

If BrandKit handles client work, unreleased branding or anything else confidential, put an authenticating proxy in front of the whole application, `/static/` included. [Deployment](/guide/deployment) shows how with Caddy, Nginx and Cloudflare Access.

### Logs

Application logs go to stdout at `INFO` level and include filenames, chosen formats and processing timings. They do not contain image content. In Docker they are captured by the container runtime — `docker compose logs` — and are subject to whatever retention your log driver has.

### Your obligations

If you run BrandKit for other people, **you** are the data controller for whatever they upload. Nothing in this project makes that determination for you. In practice that means: know what your retention actually is (see the warning above), restrict access, and tell your users where their files go.

---

## This documentation site

This site is a static build published on **GitHub Pages**.

| | |
| --- | --- |
| **Cookies** | none set by this site |
| **Analytics** | none. No Google Analytics, no Plausible, no pixel of any kind |
| **Trackers** | none |
| **Third-party requests** | none — fonts, CSS and JavaScript are all served from the same origin |
| **Search** | VitePress local search. The index is a static file downloaded to your browser; queries never leave your device |

### What GitHub sees

GitHub Pages, like any web host, processes the requests it serves. GitHub states that it collects IP addresses of Pages visitors for security and abuse-prevention purposes, and retains them for a limited period. That processing is GitHub's, governed by the [GitHub Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement), and this project has no access to it and no control over it.

### Contact

Questions about this page, or about data this project holds: **fabrizio.salmi@gmail.com**.

Security issues go through the [security policy](/security#reporting-a-vulnerability) instead.

---

*Last reviewed: September 2026.*
