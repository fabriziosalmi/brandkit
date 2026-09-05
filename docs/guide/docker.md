---
title: Running with Docker
description: Build, run, persist and update BrandKit with Docker and Docker Compose.
---

# Running with Docker

Docker is the supported deployment path. The image bundles the OpenCV and Pillow system libraries that are tedious to install by hand.

## Quick start

```bash
git clone https://github.com/fabriziosalmi/brandkit.git
cd brandkit
docker compose up -d --build
```

BrandKit is now on <http://localhost:8000>.

```bash
docker compose logs -f brandkit   # follow logs
docker compose down               # stop
docker compose down -v            # stop and drop volumes
```

## What the compose file does

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
      - FLASK_ENV=production        # legacy, no longer does anything
    restart: unless-stopped
```

Three things worth knowing:

- **The bind mount is a bind mount, not a named volume.** `./static/uploads` on your host *is* the app's upload directory. Everything anyone generates lands in your working copy. Add it to `.gitignore` (it already is) and read [Privacy](/privacy).
- **`FLASK_ENV=production` is now a no-op** and can be dropped. It used to gate the cleanup thread; cleanup is controlled by the [`BRANDKIT_CLEANUP_*` variables](/reference/environment#the-cleanup-variables) and runs under gunicorn regardless.
- **The port is fixed at 8000 inside the container.** Change the left-hand side only: `"127.0.0.1:9000:8000"` to bind on a different host port and stop exposing it on every interface.

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

The second volume caches rembg's ONNX models on the host, so rebuilding the image does not re-download ~180 MB.

## The image

`Dockerfile` starts from `python:3.11-slim` and installs the native dependencies for rembg and OpenCV (`libgl1`, `libglib2.0-0`, `libjpeg-dev`, `zlib1g-dev`, `libpng-dev`, `libwebp-dev`, and the OpenCV core/imgproc headers). It then installs `rembg`, `onnxruntime`, `opencv-python-headless` and `numpy`, followed by everything in `requirements.txt`.

Expect a build of several minutes and a final image around 2 GB. That is the cost of shipping ONNX Runtime and the scientific Python stack.

## The entrypoint

`CMD ["bash", "entrypoint.sh"]`. The script picks a server in this order:

1. **gunicorn**, if it is on `PATH` — `gunicorn --bind 0.0.0.0:$PORT --worker-tmp-dir /dev/shm app:app`
2. **`flask run`**, if the CLI is present *and* `FLASK_APP` is set
3. **a Python fallback** that imports `app.py` and calls `app.run(host="0.0.0.0")`

It also creates `static/uploads` if it is missing and honours `PORT` (default `8000`).

::: warning Set a secret key before adding workers
The entrypoint does not pass `--workers`, so gunicorn's default of **1** applies. If you raise it, set [`BRANDKIT_SECRET_KEY`](/reference/environment#brandkit-secret-key) first — without it each worker generates its own signing key and CSRF tokens minted by one worker are rejected by the next.

With several workers you probably also want `BRANDKIT_CLEANUP_ENABLED=false` on all but one, so a single process owns the file sweep.
:::

## Updating

```bash
cd brandkit
git pull
docker compose up -d --build
```

Uploads in the bind mount survive. If you changed `config.json`, your changes survive too — it is copied into the image at build time but you are running a fresh copy from the repo.

## Health check

There is no dedicated `/healthz` endpoint. Use the root page or the format catalogue:

```yaml
    healthcheck:
      test: ["CMD", "python", "-c",
             "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/format-info').status==200 else 1)"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 40s
```

`/format-info` is a `GET`, needs no CSRF token, does no image work, and returns JSON — a good liveness probe.

## Resource limits

Background removal on a large image can allocate a lot of memory. If you are running on a small VPS, cap it explicitly:

```yaml
    deploy:
      resources:
        limits:
          memory: 4G
```

and lower the upload ceiling with `BRANDKIT_MAX_UPLOAD_MB`. See [Environment variables](/reference/environment).
