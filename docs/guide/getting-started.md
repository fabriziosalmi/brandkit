---
title: Getting started
description: Install and run BrandKit locally with Docker or a Python virtual environment.
---

# Getting started

There are two supported ways to run BrandKit. Pick Docker unless you intend to change the code.

## Requirements

| | Docker route | Python route |
| --- | --- | --- |
| Runtime | Docker 20.10+ and Compose v2 | Python **3.11 or 3.12** |
| RAM | 2 GB minimum, 4 GB if you use background removal | same |
| Disk | ~2 GB for the image; the `u2net` model adds ~180 MB on first use | same |
| System libs | handled by the Dockerfile | `libgl1`, `libglib2.0-0` on Debian/Ubuntu for OpenCV |

::: tip Which Python?
CI tests 3.11 and 3.12, and the Docker image is built on `python:3.11-slim`. Newer versions may work but are not verified — several of the pinned scientific dependencies (`numba`, `llvmlite`, `onnxruntime`) lag behind the latest CPython release.
:::

## Option 1 — Docker Compose (recommended)

```bash
git clone https://github.com/fabriziosalmi/brandkit.git
cd brandkit
docker compose up -d --build
```

Open <http://localhost:8000>. That is it.

The compose file mounts `./static/uploads` into the container, so generated assets survive a restart — and so does everything anyone else generated. See [Privacy](/privacy) before you leave it running.

Full details, including the port and volume layout, are in [Running with Docker](/guide/docker).

## Option 2 — Local Python environment

```bash
git clone https://github.com/fabriziosalmi/brandkit.git
cd brandkit

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

python app.py
```

The development server binds to `127.0.0.1:8000`.

::: warning `python app.py` is the development server
Werkzeug's built-in server is single-threaded and not hardened for public traffic. For anything beyond your laptop, use `entrypoint.sh`, which prefers gunicorn:

```bash
pip install gunicorn
PORT=8000 ./entrypoint.sh
```
:::

### Background removal is optional but heavy

`rembg` and `onnxruntime` are in `requirements.txt`, so a normal install pulls them in. On first use, rembg downloads the `u2net` ONNX model (~180 MB) into `~/.u2net/`. That first request will be slow — a minute or more on a cold cache — and the app needs outbound network access to fetch it.

If you do not want background removal at all, remove `rembg` and `onnxruntime` from `requirements.txt` before installing. The app detects their absence at import time, logs it, and simply hides the feature:

```
Background removal (rembg) not available. Install with: pip install rembg
```

Everything else keeps working.

### Pre-seeding the model for offline installs

If the machine that runs BrandKit has no outbound internet, download the model elsewhere and copy it in:

```bash
# on a machine with network access
python -c "from rembg import new_session; new_session('u2net')"
# then copy ~/.u2net/u2net.onnx to the target host's ~/.u2net/
```

For Docker, mount it: `-v $HOME/.u2net:/root/.u2net`.

## Verify the install

```bash
# 1. The page loads
curl -sf http://localhost:8000/ >/dev/null && echo "UI ok"

# 2. The format catalogue responds
curl -s http://localhost:8000/format-info | head -c 200

# 3. CSRF protection is live — this must be rejected
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:8000/upload
# expect 400
```

A `400` on that last call is the correct answer: it means Flask-WTF rejected a POST with no CSRF token.

## Where files land

| Path | Contents |
| --- | --- |
| `static/uploads/` | uploaded originals and generated assets, plus the ZIP archives |
| `static/uploads/cache/` | resized intermediates keyed by content hash |
| `config.json` | the format catalogue and preprocessing defaults you can edit |
| `~/.u2net/` | rembg's downloaded ONNX models |

## Next steps

- [The generation workflow](/guide/usage) — what every control does
- [Configuration](/reference/configuration) — add your own formats
- [Deployment](/guide/deployment) — put it behind a reverse proxy
