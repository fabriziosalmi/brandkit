---
title: Environment variables
description: Configuration variables evaluated by BrandKit runtime and entrypoint scripts.
---

# Environment variables

Application environment parameters and operational overrides:

| Variable | Default | Component | Description |
| --- | --- | --- | --- |
| `BRANDKIT_SECRET_KEY` | *(ephemeral)* | `app.py` | Flask session and CSRF signature key |
| `FLASK_SECRET_KEY` | *(ephemeral)* | `app.py` | Fallback alias for session key |
| `BRANDKIT_MAX_UPLOAD_MB` | `16` | `app.py` | Upload size ceiling in megabytes (`MAX_CONTENT_LENGTH`) |
| `BRANDKIT_CLEANUP_ENABLED` | `true` | `app.py` | Set to `false` to disable automated asset sweeps |
| `BRANDKIT_CLEANUP_INTERVAL_HOURS` | `1` | `app.py` | Frequency of disk cleanup passes |
| `BRANDKIT_RETENTION_HOURS` | `24` | `app.py` | Retention duration before asset purging |
| `FLASK_ENV` | *(unset)* | `app.py` | Set to `development` to enable Werkzeug debugger in dev mode |
| `PORT` | `8000` | `app.py`, `entrypoint.sh` | Network binding port |
| `FLASK_APP` | *(unset)* | `entrypoint.sh` | Fallback flag when Gunicorn is absent |

## `BRANDKIT_SECRET_KEY`

```bash
# Generate a cryptographically secure key
python3 -c "import secrets; print(secrets.token_hex(32))"
```

```bash
BRANDKIT_SECRET_KEY=<value> docker compose up -d
```

`FLASK_SECRET_KEY` is supported as an alternate fallback.

If omitted, BrandKit generates an ephemeral key via `os.urandom(24)` and logs a warning:

```
No BRANDKIT_SECRET_KEY set - generating an ephemeral one. Sessions and CSRF
tokens will be invalidated on restart and will not work across multiple
worker processes. Set BRANDKIT_SECRET_KEY in production.
```

In multi-worker Gunicorn deployments, omitting this variable causes CSRF validation to fail across distinct worker instances.

::: warning Store securely
Specify secret keys via environment files (`.env`) or secrets managers. Do not commit credentials to repository tracking.
:::

## `BRANDKIT_MAX_UPLOAD_MB`

```bash
BRANDKIT_MAX_UPLOAD_MB=32 docker compose up -d
```

Sets the request payload limit. Submissions exceeding this threshold return HTTP 413.

Ensure reverse proxy limits (`client_max_body_size` in Nginx, `request_body max_size` in Caddy) equal or exceed this threshold.

## The cleanup variables

A background worker thread sweeps `static/uploads/` and `static/uploads/cache/`, deleting files exceeding retention while protecting `README.md`. It initializes at module import time, running under both Gunicorn and development servers.

```bash
# Sweep every 15 minutes, retain files for 1 hour
BRANDKIT_CLEANUP_INTERVAL_HOURS=0.25
BRANDKIT_RETENTION_HOURS=1
```

Supports fractional hour inputs. Invalid entries fall back to standard defaults with a warning.

```bash
# Delegate cleanup to host system cron
BRANDKIT_CLEANUP_ENABLED=false
```

Disable internal sweeps when multi-worker setups manage cleanup via system cron tasks.

::: tip Retention and asset privacy
Files in upload directories are retrievable by name until purged. On shared hosts, consider setting shorter retention intervals:

```bash
BRANDKIT_RETENTION_HOURS=1
```

See [Privacy](/privacy#retention).
:::

## `FLASK_ENV`

```bash
FLASK_ENV=development python app.py
```

Enables the interactive debugger under Werkzeug. This variable does not affect Gunicorn WSGI workers.

::: danger Security notice
Never enable `FLASK_ENV=development` on network-accessible hosts. The interactive debugger permits arbitrary code execution from the browser interface.
:::

## `PORT`

```bash
PORT=9000 ./entrypoint.sh
PORT=9000 python app.py
```

Respected by `entrypoint.sh` and `app.py` directly. When running Docker containers, map the host port via `"9000:8000"`.

## Sample `.env` configuration

```bash
# .env file for docker compose
BRANDKIT_SECRET_KEY=3f9c1e...replace-with-secure-hex
BRANDKIT_MAX_UPLOAD_MB=32
BRANDKIT_RETENTION_HOURS=2
```

```yaml
# docker-compose.yml
services:
  brandkit:
    env_file: .env
    ports:
      - "127.0.0.1:8000:8000"
```
