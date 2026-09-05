---
title: Environment variables
description: Every environment variable BrandKit and its entrypoint read.
---

# Environment variables

Everything else is in [`config.json`](/reference/configuration).

| Variable | Default | Read by | Effect |
| --- | --- | --- | --- |
| `BRANDKIT_SECRET_KEY` | *(ephemeral)* | `app.py` | Flask session and CSRF signing key |
| `FLASK_SECRET_KEY` | *(ephemeral)* | `app.py` | Fallback alias for the above |
| `BRANDKIT_MAX_UPLOAD_MB` | `16` | `app.py` | Maximum upload size in megabytes → `MAX_CONTENT_LENGTH` |
| `BRANDKIT_CLEANUP_ENABLED` | `true` | `app.py` | Set to `false`/`0`/`no` to disable the periodic sweep |
| `BRANDKIT_CLEANUP_INTERVAL_HOURS` | `1` | `app.py` | How often the sweep runs |
| `BRANDKIT_RETENTION_HOURS` | `24` | `app.py` | How old a file must be before it is deleted |
| `FLASK_ENV` | *(unset)* | `app.py` | `development` enables the Werkzeug debugger (dev server only) |
| `PORT` | `8000` | `app.py`, `entrypoint.sh` | Port the server binds to |
| `FLASK_APP` | *(unset)* | `entrypoint.sh` | Only consulted if gunicorn is absent, to decide whether to use `flask run` |

## `BRANDKIT_SECRET_KEY`

```bash
# generate one once, then keep it
python3 -c "import secrets; print(secrets.token_hex(32))"
```

```bash
BRANDKIT_SECRET_KEY=<that value> docker compose up -d
```

`FLASK_SECRET_KEY` is accepted as an alias, checked second.

If neither is set, BrandKit generates an ephemeral key with `os.urandom(24)` and logs:

```
No BRANDKIT_SECRET_KEY set - generating an ephemeral one. Sessions and CSRF
tokens will be invalidated on restart and will not work across multiple
worker processes. Set BRANDKIT_SECRET_KEY in production.
```

That is fine on a laptop. On a server it means two things:

- **Every restart invalidates every open session.** A user who had the page loaded gets a `400 CSRF token missing` when they submit.
- **You cannot run more than one gunicorn worker.** Each process would generate its own key, so a token minted by worker A is rejected by worker B.

Set it, and multiple workers become safe.

::: warning Keep it out of version control
Put it in a `.env` file (already covered by `.gitignore`) or your orchestrator's secret store — never in `docker-compose.yml`.
:::

## `BRANDKIT_MAX_UPLOAD_MB`

```bash
BRANDKIT_MAX_UPLOAD_MB=32 docker compose up -d
```

Parsed with `int()`; a non-numeric value falls back to `16` rather than failing to start. Exceeding the limit returns `413`.

Raise it deliberately. Peak memory during upload scales with file size — the EXIF-stripping step materialises every pixel in Python — and the whole file is read into memory again to compute the cache key. See [Performance](/guide/performance#what-actually-eats-memory).

Whatever you set, your reverse proxy needs a matching body limit or it will reject large uploads first, with a less helpful error. See [Deployment](/guide/deployment).

## The cleanup variables

A daemon thread sweeps `static/uploads/` and `static/uploads/cache/`, deleting files past the retention window and skipping `README.md`. It is started **at import time**, so it runs under gunicorn as well as under `python app.py`.

```bash
# sweep every 15 minutes, keep files for one hour
BRANDKIT_CLEANUP_INTERVAL_HOURS=0.25
BRANDKIT_RETENTION_HOURS=1
```

Both accept fractional hours. A non-numeric or non-positive value logs a warning and falls back to the default.

```bash
# hand cleanup to a host cron job instead
BRANDKIT_CLEANUP_ENABLED=false
```

Disable it when something outside the container already sweeps the directory, or when you run several workers and want only one process doing the deleting.

::: tip Retention is a privacy setting, not just a disk setting
Generated assets are readable by anyone who can reach the instance. Twenty-four hours is a long exposure window for something a user downloads within seconds. See [Privacy](/privacy#retention).
:::

A failed sweep is logged and the thread keeps running; it does not take the app down.

## `FLASK_ENV`

```bash
FLASK_ENV=development python app.py     # debugger on, auto-reload on
```

`development` makes `app.run()` start with `debug=True`. This only applies to the development server — under gunicorn the `__main__` block never executes, so the variable has no effect there.

::: danger Never set `development` on a reachable host
The Werkzeug debugger executes arbitrary Python from the browser on any unhandled exception. On a machine anyone else can reach, that is a remote shell.
:::

`FLASK_ENV` no longer has anything to do with cleanup — that moved to the `BRANDKIT_CLEANUP_*` variables above. The `FLASK_ENV=production` line in the stock `docker-compose.yml` is now a no-op you can drop.

## `PORT`

```bash
PORT=9000 ./entrypoint.sh
PORT=9000 python app.py
```

Honoured by `entrypoint.sh` for all three of its server strategies, and by `app.py` directly.

In Docker the internal port is effectively fixed at 8000 by `EXPOSE` and the compose mapping — remap on the host side instead: `"9000:8000"`.

## `FLASK_APP`

Only relevant on the fallback path. If gunicorn is not installed *and* `FLASK_APP` is set, the entrypoint runs `flask run --host=0.0.0.0 --port=$PORT`. In a normal Docker install gunicorn is present, so this is never used.

## Not configurable

In case you are looking for them: there is no variable for the rate limits, the cache backend, the upload directory, or the log level. Those are literals in `app.py`.

## A worked `.env`

```bash
# .env — used by docker compose. Not in version control.
BRANDKIT_SECRET_KEY=3f9c1e...replace-with-your-own
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
