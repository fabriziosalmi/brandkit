---
title: Performance & caching
description: How BrandKit caches renders, manages memory, and handles file retention.
---

# Performance & caching

## The render cache

Resized intermediates are cached on disk under `static/uploads/cache/`, keyed by a hash of the source file bytes plus the preprocessing parameters:

```python
file_hash = hashlib.md5(open(original_path, 'rb').read()).hexdigest()
```

combined with a deterministic serialization of the options dictionary, target width, and target height.

Consequently, re-generating the same image with identical preprocessing settings is nearly instantaneous, even across varying format selections, because individual target dimensions are cached independently. Changing any preprocessing option invalidates cache hits for that configuration.

::: info Cache key hashing
The MD5 hash operates strictly as a content cache key rather than a cryptographic signature. A collision would result in an incorrect thumbnail rather than an execution vulnerability.
:::

Hashing the file requires reading its payload into memory, meaning peak memory correlates with your upload ceiling. Under the 16 MB default, this overhead is minimal; higher values for `BRANDKIT_MAX_UPLOAD_MB` scale concurrent memory consumption accordingly.

## In-memory caching

Flask-Caching is configured with `SimpleCache` (a per-process memory dictionary). It is not shared between Gunicorn workers and resets upon container restart. This design is suitable for volatile recomputable values.

## Memory management

After batch generation involving more than five formats or when variations mode is active, BrandKit triggers explicit garbage collection. When `psutil` is present, it records process memory diagnostics. `psutil` is specified in `requirements.txt`; if omitted, the service falls back gracefully:

```
Warning: psutil not available. Memory monitoring disabled.
```

### High-memory operations

| Operation | Memory profile |
| --- | --- |
| ONNX Runtime background removal | Primary memory consumer: several hundred MB on large sources |
| Variations mode | Computes multiple full preprocessing pipelines concurrently |
| `print_a4` (2480×3508) and `square_large` (2048×2048) | ~35 MB per uncompressed RGBA pixel buffer before encoding |
| EXIF metadata stripping | Materializes image pixel data through Pillow buffers |

### Optimization recommendations

- Configure container limits: `deploy.resources.limits.memory: 4G`
- Set `BRANDKIT_MAX_UPLOAD_MB` to match operational requirements
- Maintain a conservative Gunicorn worker count: each worker initializes its own ONNX session
- Avoid enabling variations mode on high-DPI print canvases simultaneously

## File cleanup

A background worker thread inspects `static/uploads/` and `static/uploads/cache/`, removing assets that exceed the retention duration while protecting `README.md`. It reports file counts and reclaimed disk space to stdout.

The worker thread starts at application import time, running under Gunicorn as well as the Flask development server.

| Environment variable | Default | Description |
| --- | --- | --- |
| `BRANDKIT_CLEANUP_ENABLED` | `true` | Set to `false` to disable the internal cleanup thread |
| `BRANDKIT_CLEANUP_INTERVAL_HOURS` | `1` | Interval between cleanup passes |
| `BRANDKIT_RETENTION_HOURS` | `24` | Retention lifespan before file deletion |

Interval and retention values support decimal fractions (e.g. `0.25` equals fifteen minutes). Cleanup exceptions are logged without terminating the worker loop.

::: tip Shorten retention for shared instances
Default 24-hour retention maintains assets on disk where they remain accessible by filename. For shared or network-exposed setups where users download archives immediately, configure shorter retention:

```bash
BRANDKIT_RETENTION_HOURS=1
BRANDKIT_CLEANUP_INTERVAL_HOURS=0.25
```

See [Privacy](/privacy#retention).
:::

### Manual cleanup execution

```bash
docker compose exec brandkit python -c "import app; print(app.cleanup_old_files(max_age_hours=1))"
```

### External host cron cleanup

To delegate disk cleanup to a system cron job (for instance, when running multi-worker Gunicorn configurations), disable the internal thread and target the bind mount:

```bash
BRANDKIT_CLEANUP_ENABLED=false
```

```bash
# Sweep uploads older than 24 hours every hour
0 * * * * find /srv/brandkit/static/uploads -type f -mmin +1440 ! -name README.md -delete
```

## Rate limits

| Scope | Limit |
| --- | --- |
| Global default | 200 per day, 50 per hour |
| `POST /upload` | 5 per minute |

Rate limits use in-memory counters per worker process. Requests exceeding limits return HTTP 429.

Behind a reverse proxy, limits evaluate the proxy's IP unless `ProxyFix` is active; consult [Deployment](/guide/deployment#nginx).

## Execution speed recommendations

1. **Target necessary formats only:** Generating all 45 canvases requires proportional CPU cycles.
2. **Constrain output encodings:** Each format is separately encoded for every active file type.
3. **Bypass background removal:** Omit neural segmentation when sources already provide clean alpha channels.
4. **Leverage cache consistency:** Retaining preprocessing options allows cached target dimensions to be served immediately.
5. **Ingest appropriate source resolutions:** A 2048×2048 master provides sufficient detail for all digital canvases without the memory overhead of extreme source sizes.
