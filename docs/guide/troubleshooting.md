---
title: Troubleshooting
description: Symptoms, causes and fixes for the problems people actually hit running BrandKit.
---

# Troubleshooting

## Quick triage

```bash
# Is it up?
curl -sf http://localhost:8000/ >/dev/null && echo UP || echo DOWN

# What did it say at startup?
docker compose logs --tail=50 brandkit

# Is CSRF live? (must return 400)
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:8000/upload

# Is the catalogue loading?
curl -s http://localhost:8000/format-info | python3 -m json.tool | head -20
```

## Startup

### `ModuleNotFoundError: No module named 'rembg'`

Not fatal. The app catches it and disables background removal:

```
Background removal (rembg) not available. Install with: pip install rembg
```

Install it (`pip install rembg onnxruntime`) or accept the loss of the feature.

### `ImportError: libGL.so.1: cannot open shared object file`

OpenCV needs system libraries that a bare `pip install` does not provide.

```bash
# Debian / Ubuntu
sudo apt-get install -y libgl1 libglib2.0-0
```

The Docker image already installs these. If you see it in a container, you have changed the base image.

### `Address already in use`

Something else holds port 8000.

```bash
lsof -i :8000                 # macOS / Linux
docker compose down           # if it is an old BrandKit container
```

Or move the host port: `"8001:8000"` in `docker-compose.yml`.

### `Warning: config.json not found. Using default configuration.`

You started the app from a directory that is not the repo root. `load_config()` opens `config.json` by relative path. `cd` into the project first.

### `Error: config.json is not valid JSON. Using default configuration.`

Your edit broke the file. Validate it:

```bash
python3 -m json.tool config.json > /dev/null && echo "valid"
```

The app falls back to built-in defaults rather than crashing, which is why the symptom is "my new format vanished" rather than an error page.

## Uploads

### `400 Bad Request — The CSRF token is missing`

Expected if you are calling `/upload` with `curl` or a script. Every `POST` needs a valid CSRF token; see [HTTP endpoints](/reference/http-api#authentication-and-csrf) for how to obtain one.

If it happens **in the browser**, the usual causes are:

- more than one gunicorn worker, each with a different `SECRET_KEY` — see [the known gap](/security#known-hardening-gaps)
- the app restarted between page load and submit, regenerating the key
- cookies blocked for the origin

### `413 Request Entity Too Large`

The file is over the limit. Two limits are in play:

```bash
BRANDKIT_MAX_UPLOAD_MB=32 docker compose up -d      # the app's limit
```

and your reverse proxy's own body limit (`client_max_body_size` in Nginx, `request_body max_size` in Caddy), which must be at least as large. If Flask never logs the request, the proxy rejected it.

### `File type not allowed`

Only `png`, `jpg`, `jpeg`, `gif`, `webp` are accepted, matched on the extension after the last dot, case-insensitively. Rename or convert:

```bash
# SVG is not supported — rasterise first
rsvg-convert -w 2048 logo.svg -o logo.png
```

### `Invalid image file`

The extension was allowed but Pillow could not decode the contents — a corrupt file, or something misnamed. The upload is deleted and the request fails. Verify locally:

```bash
python3 -c "from PIL import Image; Image.open('yourfile.png').verify(); print('ok')"
```

### `429 Too Many Requests`

Rate limiting: 5 uploads/minute, 50 requests/hour, 200/day per IP. Wait it out, or adjust the decorators in `app.py` for a trusted deployment.

## Generation

### It hangs on the first background removal

rembg is downloading a ~180 MB ONNX model. Watch for network activity and check `~/.u2net/`. Subsequent runs are fast. Pre-seed the directory for offline hosts — see [Background removal](/guide/background-removal#choosing-a-model).

### The container is killed mid-generation (exit 137)

Out of memory. ONNX Runtime plus a large image plus variations mode will do it.

```bash
docker stats brandkit          # watch it climb
```

Fixes, in order of effectiveness: turn off variations mode, use a smaller source, lower `BRANDKIT_MAX_UPLOAD_MB`, raise the container memory limit.

### `504 Gateway Timeout` from the proxy

A long generation outran the proxy's read timeout. Raise it to 300 s — `proxy_read_timeout 300s;` in Nginx. See [Deployment](/guide/deployment#nginx).

### The ICO file did not appear

`ico` is only produced when the `favicon` format is also selected. If you tick `ico` without `favicon`, it is silently dropped from the output types.

### Transparency was lost

You selected `jpg`, which has no alpha channel. Use PNG or WebP.

### The logo looks tiny in every format

Your source has a lot of empty canvas around the mark. Turn on **auto-crop** with 10–20 px of padding — it trims once and every format benefits.

### Generation is slow every single time

The disk cache is missing. Either the preprocessing options changed between runs (any change invalidates every entry), or `static/uploads/cache/` is not writable:

```bash
ls -la static/uploads/
chmod -R u+rwX static/uploads/
```

In Docker, check that the bind-mounted host directory is writable by the container user.

## Disk

### `static/uploads/` has grown to gigabytes

The scheduled cleanup does not run under gunicorn. This is expected behaviour today, not a misconfiguration on your part. Schedule it yourself — the recipes are in [Performance & caching](/guide/performance#file-cleanup).

## Still stuck

- Search the [issue tracker](https://github.com/fabriziosalmi/brandkit/issues)
- Open a [bug report](https://github.com/fabriziosalmi/brandkit/issues/new?template=bug_report.md) with the startup log, your Python or Docker version, and the exact steps
- For anything security-sensitive, use the [security policy](/security#reporting-a-vulnerability) instead of a public issue
