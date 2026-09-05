---
title: Performance & caching
description: How BrandKit caches renders, manages memory and cleans up old files — and what you have to do yourself.
---

# Performance & caching

## The render cache

Resized intermediates are cached on disk under `static/uploads/cache/`, keyed by a hash of **the source file's bytes plus the preprocessing options**:

```python
file_hash = hashlib.md5(open(original_path, 'rb').read()).hexdigest()
```

combined with a stable serialisation of the options dictionary, plus the target width and height.

The practical consequence: **re-generating the same image with the same preprocessing settings is nearly free**, even across different format selections, because each target size is cached independently. Change any preprocessing option — even one you cannot see in the output — and the whole cache misses.

::: info MD5 here is not a security decision
The hash is a cache key, not a signature. Collisions would mean a wrong thumbnail, not a vulnerability. It is still worth swapping for BLAKE2b at some point, purely to keep static analysers quiet.
:::

Reading the whole file into memory to hash it means peak memory scales with your upload limit. At the 16 MB default this is irrelevant; if you raise `BRANDKIT_MAX_UPLOAD_MB` to something large, remember that each concurrent request holds a full copy.

## In-memory caching

Flask-Caching is configured with `SimpleCache` — a per-process dictionary. It is not shared between gunicorn workers and it is lost on restart. That is fine for what it holds (small, recomputable values) but it means cache hit rates get worse, not better, as you add workers.

## Memory management

After any generation involving **more than five formats** or with **variations mode** on, BrandKit forces a garbage collection pass and, when `psutil` is installed, logs process memory. `psutil` is in `requirements.txt`, so this is normally active; without it the app prints:

```
Warning: psutil not available. Memory monitoring disabled.
```

and still runs.

### What actually eats memory

| Operation | Cost |
| --- | --- |
| ONNX Runtime background removal | the largest single spike — hundreds of MB on a big image |
| Variations mode | ten full preprocessing passes held alongside each other |
| `print_a4` (2480×3508) and `square_large` (2048×2048) | ~35 MB per RGBA buffer, before intermediates |
| The EXIF-stripping re-encode on upload | `list(img.getdata())` materialises every pixel as a Python tuple — briefly very expensive on large images |

That last one is worth knowing about: the upload path builds a Python list of every pixel to strip metadata. For a 4000×4000 image that is 16 million tuples. It works, but it is the reason a large upload feels slow before anything visible happens.

### Keeping it in bounds

- Cap the container: `deploy.resources.limits.memory: 4G`
- Lower `BRANDKIT_MAX_UPLOAD_MB` from 16 to something matched to your actual sources
- Keep the gunicorn worker count low — each worker holds its own ONNX session, so memory scales linearly with workers, not with traffic
- Do not use variations mode on the print formats

## File cleanup

A daemon thread sweeps `static/uploads/` and `static/uploads/cache/`, deleting anything past the retention window and skipping `README.md`. It logs how many files it removed and how much space it recovered.

It is started **at import time**, so it runs under gunicorn — the server the Docker image actually uses — as well as under `python app.py`.

| Variable | Default | Meaning |
| --- | --- | --- |
| `BRANDKIT_CLEANUP_ENABLED` | `true` | set to `false` to turn the thread off entirely |
| `BRANDKIT_CLEANUP_INTERVAL_HOURS` | `1` | how often it sweeps |
| `BRANDKIT_RETENTION_HOURS` | `24` | how old a file must be to be deleted |

Both interval and retention accept fractional hours, so `0.25` is fifteen minutes. A sweep that throws is logged and the thread survives to try again on the next tick.

::: tip Shorten the retention
24 hours is a long time for files that anyone who can reach the instance can fetch. If people use BrandKit interactively and download immediately, an hour is a much better privacy posture:

```bash
BRANDKIT_RETENTION_HOURS=1
BRANDKIT_CLEANUP_INTERVAL_HOURS=0.25
```

See [Privacy](/privacy#retention).
:::

### Running the sweep by hand

```bash
docker compose exec brandkit python -c "import app; print(app.cleanup_old_files(max_age_hours=1))"
```

### Handing cleanup to the host instead

If you would rather a cron job owned it — for example because you run several workers and want exactly one process deleting — disable the thread and sweep the bind mount:

```bash
BRANDKIT_CLEANUP_ENABLED=false
```

```bash
# every hour, delete upload artefacts older than 24h
0 * * * * find /srv/brandkit/static/uploads -type f -mmin +1440 ! -name README.md -delete
```

## Rate limits

| Scope | Limit |
| --- | --- |
| Global default | 200 per day, 50 per hour |
| `POST /upload` | 5 per minute |

Storage is `memory://`, so limits are per-process and reset on restart — and, again, are not shared across gunicorn workers. Exceeding a limit returns `429`.

Behind a reverse proxy these limits key on the proxy's IP unless you configure `ProxyFix`; see the warning in [Deployment](/guide/deployment#nginx).

## Making generation faster

1. **Select fewer formats.** Leaving the selection empty renders all 45.
2. **Select fewer output types.** Each type is a separate encode of every format.
3. **Skip background removal** when the source already has an alpha channel.
4. **Reuse the same preprocessing settings** across runs so the disk cache hits.
5. **Start from a reasonably sized source.** A 8000×8000 master gives you nothing that a 2048×2048 one does not, and costs you every intermediate.
