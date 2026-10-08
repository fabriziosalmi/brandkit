---
title: Troubleshooting
description: Operational diagnostics, common error states, and resolutions in BrandKit.
---

# Troubleshooting

## Quick triage

```bash
# Verify HTTP status
curl -sf http://localhost:8000/ >/dev/null && echo UP || echo DOWN

# Review startup logs
docker compose logs --tail=50 brandkit

# Validate CSRF enforcement (must return HTTP 400)
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:8000/upload

# Check format catalogue payload
curl -s http://localhost:8000/format-info | python3 -m json.tool | head -20
```

## Startup issues

### `ModuleNotFoundError: No module named 'rembg'`

Non-fatal dependency warning. The application catches the exception and disables background removal:

```
Background removal (rembg) not available. Install with: pip install rembg
```

Install the optional package (`pip install rembg onnxruntime`) or proceed with base image processing.

### `ImportError: libGL.so.1: cannot open shared object file`

OpenCV requires native system runtime libraries:

```bash
# Debian / Ubuntu
sudo apt-get install -y libgl1 libglib2.0-0
```

The standard Docker image includes these libraries by default.

### `Address already in use`

Port 8000 is occupied by another process:

```bash
lsof -i :8000                 # macOS / Linux
docker compose down           # Terminate previous containers
```

Alternatively, map a distinct host port in `docker-compose.yml` (e.g. `"8001:8000"`).

### `Warning: config.json not found. Using default configuration.`

The application process was launched from outside the repository root directory. Launch `app.py` from the root directory containing `config.json`.

### `Error: config.json is not valid JSON. Using default configuration.`

The configuration file contains syntax errors. Validate with:

```bash
python3 -m json.tool config.json > /dev/null && echo "valid"
```

The application defaults to internal presets if the JSON file cannot be parsed.

## Upload issues

### `400 Bad Request: The CSRF token is missing`

Expected behavior when invoking `/upload` without an active session CSRF token. Refer to [HTTP endpoints](/reference/http-api#authentication-and-csrf).

If encountered in the browser, verify:

- Multiple Gunicorn workers are running without a shared [`BRANDKIT_SECRET_KEY`](/reference/environment#brandkit-secret-key)
- Application was restarted between page render and submission
- Browser cookies are blocked for the application origin

### `413 Request Entity Too Large`

The uploaded file exceeds the configured size ceiling. Check two limits:

```bash
BRANDKIT_MAX_UPLOAD_MB=32 docker compose up -d
```

Ensure reverse proxy body limits (`client_max_body_size` in Nginx, `request_body max_size` in Caddy) equal or exceed this value.

### `File type not allowed`

Accepted extensions: `png`, `jpg`, `jpeg`, `gif`, `webp`. Files are matched on the final extension component case-insensitively.

Rasterize vector sources prior to upload:

```bash
rsvg-convert -w 2048 logo.svg -o logo.png
```

### `Invalid image file`

Pillow could not decode the uploaded buffer (corrupted file or invalid format signature). Verify integrity locally:

```bash
python3 -c "from PIL import Image; Image.open('yourfile.png').verify(); print('ok')"
```

### `429 Too Many Requests`

Rate limiting threshold reached: 5 uploads/minute, 50 requests/hour, 200/day per IP.

## Generation issues

### Initial background removal latency

`rembg` downloads the ~180 MB ONNX model upon first invocation. Subsequent runs execute locally against cached weights in `~/.u2net/`.

### Container exit 137 (OOM killed)

System killed the container due to memory exhaustion. Mitigations:

```bash
docker stats brandkit          # Monitor live memory utilization
```

Disable variations mode, ingest a lower-resolution source, reduce `BRANDKIT_MAX_UPLOAD_MB`, or increase container RAM allocations.

### `504 Gateway Timeout` from reverse proxy

Pipeline execution exceeded the upstream proxy timeout. Increase timeout values (e.g. `proxy_read_timeout 300s;` in Nginx).

### ICO asset not produced

The `.ico` encoding is generated exclusively when the `favicon` canvas format is selected.

### Flattened background transparency

JPEG encodings discard the alpha channel. Select PNG or WebP to retain transparency.

### Subject appears disproportionately small

The source contains excessive transparent or solid padding. Enable **auto-crop** with 10-20 px padding to trim perimeter space uniformly.

### Repeated cache misses

Ensure `static/uploads/cache/` has write permissions for the container process:

```bash
ls -la static/uploads/
chmod -R u+rwX static/uploads/
```

Modifying any preprocessing slider or toggle generates a distinct cache key.

## Disk management

### Upload storage growth

Confirm cleanup worker status in startup logs:

```
Scheduled cleanup started: every 1.0h, deleting files older than 24.0h
```

If throughput is high, shorten the retention window via `BRANDKIT_RETENTION_HOURS=1`. Consult [Performance & caching](/guide/performance#file-cleanup).

## Support & contributions

- Review existing reports on the [issue tracker](https://github.com/fabriziosalmi/brandkit/issues)
- Open a [bug report](https://github.com/fabriziosalmi/brandkit/issues/new?template=bug_report.md) including startup logs and environment details
- Report security concerns via the [security policy](/security#reporting-a-vulnerability)
