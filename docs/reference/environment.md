---
title: Environment variables
description: Every environment variable BrandKit and its entrypoint actually read.
---

# Environment variables

There are four, and only four. Everything else is in [`config.json`](/reference/configuration).

| Variable | Default | Read by | Effect |
| --- | --- | --- | --- |
| `BRANDKIT_MAX_UPLOAD_MB` | `16` | `app.py` | Maximum upload size in megabytes → `MAX_CONTENT_LENGTH` |
| `FLASK_ENV` | *(unset)* | `app.py` | `development` enables the Werkzeug debugger and disables the cleanup thread |
| `PORT` | `8000` | `entrypoint.sh` | Port the server binds to |
| `FLASK_APP` | *(unset)* | `entrypoint.sh` | Only consulted if gunicorn is absent, to decide whether to use `flask run` |

## `BRANDKIT_MAX_UPLOAD_MB`

```bash
BRANDKIT_MAX_UPLOAD_MB=32 docker compose up -d
```

Parsed with `int()`; a non-numeric value falls back to `16` rather than failing to start. Exceeding the limit returns `413`.

Raise it deliberately. Peak memory during upload scales with file size — the EXIF-stripping step materialises every pixel in Python — and the whole file is read into memory again to compute the cache key. See [Performance](/guide/performance#what-actually-eats-memory).

Whatever you set, your reverse proxy needs a matching body limit or it will reject large uploads first, with a less helpful error. See [Deployment](/guide/deployment).

## `FLASK_ENV`

```bash
FLASK_ENV=development python app.py     # debugger on, auto-reload on
```

Two effects, both in the `__main__` block:

- `development` → `app.run(debug=True)`, which enables the interactive Werkzeug debugger
- anything else (including unset) → the hourly cleanup thread is started

::: danger Never set `development` on a reachable host
The Werkzeug debugger executes arbitrary Python from the browser on any unhandled exception. On a machine anyone else can reach, that is a remote shell.
:::

::: warning `FLASK_ENV` is a no-op under gunicorn
Both effects live inside `if __name__ == '__main__':`. When gunicorn imports `app:app` — which is what `entrypoint.sh` and therefore the Docker image do — that block never runs. The stock `docker-compose.yml` sets `FLASK_ENV=production` and it changes nothing, including the cleanup thread it looks like it should be enabling. See [Performance](/guide/performance#file-cleanup) for how to schedule cleanup yourself.
:::

## `PORT`

```bash
PORT=9000 ./entrypoint.sh
```

Consumed by `entrypoint.sh` for all three of its server strategies. Note that `python app.py` **ignores it** and hard-codes `port=8000`.

In Docker, the internal port is effectively fixed at 8000 by `EXPOSE` and the compose mapping — remap on the host side instead: `"9000:8000"`.

## `FLASK_APP`

Only relevant on the fallback path. If gunicorn is not installed *and* `FLASK_APP` is set, the entrypoint runs `flask run --host=0.0.0.0 --port=$PORT`. In a normal Docker install gunicorn is present, so this is never used.

## Not implemented

::: warning `FLASK_SECRET_KEY` does nothing
The project README lists a `FLASK_SECRET_KEY` variable. **The application does not read it.** `app.py` sets:

```python
app.config['SECRET_KEY'] = os.urandom(24)
```

unconditionally, at import time. The key is therefore regenerated on every start and is different in every process. Consequences and mitigation are in [Security](/security#known-hardening-gaps); the short version is to leave gunicorn at one worker.
:::

Also absent, in case you are looking for them: there is no variable for the rate limits, the cleanup interval, the cache backend, the upload directory, or the log level. All of those are literals in `app.py`.

## A worked `.env`

```bash
# .env — used by docker compose
BRANDKIT_MAX_UPLOAD_MB=32
```

```yaml
# docker-compose.yml
services:
  brandkit:
    env_file: .env
    ports:
      - "127.0.0.1:8000:8000"
```

Keep `.env` out of version control. It is already covered by `.gitignore`.
