---
title: Running with Docker
description: Build, run, persist and update BrandKit with Docker and Docker Compose.
---

# Running with Docker

Docker is the supported deployment path. The image bundles OpenCV and Pillow system libraries required for processing.

## Quick start

```bash
git clone https://github.com/fabriziosalmi/brandkit.git
cd brandkit
docker compose up -d --build
```

BrandKit is available on <http://localhost:8000>.

```bash
docker compose logs -f brandkit   # follow logs
docker compose down               # stop
docker compose down -v            # stop and remove volumes
```

## Docker Compose configuration

```yaml
services:
  brandkit:
    build: .
    container_name: brandkit
    ports:
      - "8000:8000"
    volumes:
      - ./static/uploads:/app/static/uploads
    environment:
      - FLASK_ENV=production        # legacy variable
    restart: unless-stopped
```

Key configuration details:

- **Upload volume:** `./static/uploads` on the host is the container upload directory. Generated assets are stored directly in this directory.
- **Port binding:** The internal container port is 8000. To bind specifically to host loopback, specify `"127.0.0.1:8000:8000"`.
- **Cleanup handling:** Background cleanup runs under Gunicorn and is configured via [`BRANDKIT_CLEANUP_*` environment variables](/reference/environment#the-cleanup-variables).

## Running without Compose

```bash
docker build -t brandkit .

docker run -d \
  --name brandkit \
  -p 127.0.0.1:8000:8000 \
  -v "$(pwd)/static/uploads:/app/static/uploads" \
  -v "$HOME/.u2net:/root/.u2net" \
  -e BRANDKIT_MAX_UPLOAD_MB=32 \
  --restart unless-stopped \
  brandkit
```

Mounting `$HOME/.u2net` persists downloaded ONNX models across container rebuilds.

## Image specification

The `Dockerfile` builds on `python:3.11-slim` and installs system dependencies for rembg and OpenCV (`libgl1`, `libglib2.0-0`, `libjpeg-dev`, `zlib1g-dev`, `libpng-dev`, `libwebp-dev`, and OpenCV development headers). It then installs `rembg`, `onnxruntime`, `opencv-python-headless`, `numpy`, and dependencies listed in `requirements.txt`.

Initial builds take several minutes, resulting in an image size of approximately 2 GB due to the ONNX Runtime and scientific Python stack.

## Entrypoint process

The container executes `entrypoint.sh`, selecting a WSGI runner in priority order:

1. **Gunicorn** (when available on `PATH`): `gunicorn --bind 0.0.0.0:$PORT --worker-tmp-dir /dev/shm app:app`
2. **Flask CLI** (when `FLASK_APP` is set): `flask run`
3. **Python runtime**: imports `app.py` and initiates `app.run(host="0.0.0.0")`

The entrypoint creates `static/uploads` if absent and respects the `PORT` environment variable (default: `8000`).

::: warning Configure secret key before scaling workers
The default configuration runs 1 Gunicorn worker. Before increasing worker count, configure [`BRANDKIT_SECRET_KEY`](/reference/environment#brandkit-secret-key) to ensure consistent CSRF session verification across workers.
:::

## Updating

```bash
cd brandkit
git pull
docker compose up -d --build
```

Upload directories in the bind mount persist across rebuilds.

## Health check

The `/format-info` endpoint serves as a lightweight HTTP GET probe without requiring CSRF authentication:

```yaml
    healthcheck:
      test: ["CMD", "python", "-c",
             "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/format-info').status==200 else 1)"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 40s
```

## Resource limits

Background removal on high-resolution images can allocate significant RAM. On resource-constrained hosts, specify explicit limits:

```yaml
    deploy:
      resources:
        limits:
          memory: 4G
```

Configure `BRANDKIT_MAX_UPLOAD_MB` accordingly. See [Environment variables](/reference/environment).
