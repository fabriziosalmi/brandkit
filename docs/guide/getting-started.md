---
title: Getting started
description: Install and run BrandKit locally with Docker or a Python virtual environment.
---

# Getting started

There are two supported ways to run BrandKit. Use Docker unless you intend to modify the codebase directly.

## Requirements

| Requirement | Docker route | Python route |
| --- | --- | --- |
| Runtime | Docker 20.10+ and Compose v2 | Python **3.11 or 3.12** |
| RAM | 2 GB minimum, 4 GB with background removal | Same |
| Disk | ~2 GB for the image; `u2net` adds ~180 MB on first use | Same |
| System libs | Bundled in Dockerfile | `libgl1`, `libglib2.0-0` on Debian/Ubuntu for OpenCV |

::: tip Supported Python versions
CI validates 3.11 and 3.12, and the Docker image is built on `python:3.11-slim`. Newer versions may work but are not officially verified because pinned scientific packages (`numba`, `llvmlite`, `onnxruntime`) frequently lag behind newer CPython releases.
:::

## Option 1: Docker Compose (recommended)

```bash
git clone https://github.com/fabriziosalmi/brandkit.git
cd brandkit
docker compose up -d --build
```

Access the application at <http://localhost:8000>.

The Compose file mounts `./static/uploads` into the container, ensuring generated assets persist across restarts. Consult [Privacy](/privacy) prior to shared deployment.

For detailed configuration instructions, see [Running with Docker](/guide/docker).

## Option 2: Local Python environment

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

::: warning Development server note
Werkzeug's built-in server is single-threaded and intended for development only. For production or networked instances, execute `entrypoint.sh` with Gunicorn:

```bash
pip install gunicorn
PORT=8000 ./entrypoint.sh
```
:::

### Background removal dependencies

`rembg` and `onnxruntime` are included in `requirements.txt`. On initial invocation, `rembg` fetches the `u2net` ONNX model (~180 MB) to `~/.u2net/`. This download requires outbound network connectivity and extends processing time on the first run.

If background removal is unnecessary, remove `rembg` and `onnxruntime` from `requirements.txt` prior to installation. The application detects their absence at startup and hides the corresponding interface controls:

```
Background removal (rembg) not available. Install with: pip install rembg
```

All other image transformation features remain functional.

### Pre-seeding models for offline deployment

For environments lacking outbound internet connectivity, pre-download the model:

```bash
# On a machine with internet access:
python -c "from rembg import new_session; new_session('u2net')"
# Copy ~/.u2net/u2net.onnx to the target host under ~/.u2net/
```

When using Docker, mount the cached directory: `-v $HOME/.u2net:/root/.u2net`.

## Verification

```bash
# 1. UI accessibility
curl -sf http://localhost:8000/ >/dev/null && echo "UI ok"

# 2. Format catalogue response
curl -s http://localhost:8000/format-info | head -c 200

# 3. CSRF enforcement (must return HTTP 400 without token)
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:8000/upload
```

An HTTP 400 response on unauthenticated POST requests confirms active CSRF protection.

## File locations

| Path | Contents |
| --- | --- |
| `static/uploads/` | Uploaded originals, generated output formats, and ZIP archives |
| `static/uploads/cache/` | Cached resized intermediates indexed by content hash |
| `config.json` | Editable format catalogue and preprocessing defaults |
| `~/.u2net/` | Downloaded ONNX model weights for rembg |

## Next steps

- [The generation workflow](/guide/usage): operational parameters and controls
- [Configuration](/reference/configuration): format definitions and defaults
- [Deployment](/guide/deployment): reverse proxy setup and network hardening
