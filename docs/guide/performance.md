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
- Leave gunicorn at one worker (each worker is a full copy of the ONNX session)
- Do not use variations mode on the print formats

## File cleanup

`cleanup_old_files()` deletes anything in `static/uploads/` and `static/uploads/cache/` older than **24 hours**, skipping `README.md`. It reports how many files it removed and how much space it recovered.

::: danger The cleanup thread does not run under gunicorn
The scheduled cleanup thread is started inside `if __name__ == '__main__':`. When the app is served by gunicorn — which is what `entrypoint.sh` prefers, and therefore what the Docker image actually does — that block never executes, and **nothing is ever deleted**.

On a long-running deployment `static/uploads/` grows without bound.
:::

Until that is fixed upstream, schedule it externally. A host cron entry against the bind mount:

```bash
# every hour, delete upload artefacts older than 24h
0 * * * * find /srv/brandkit/static/uploads -type f -mmin +1440 ! -name README.md -delete
```

Or from inside the container, which reuses the app's own logic:

```bash
docker compose exec brandkit python -c "import app; print(app.cleanup_old_files())"
```

Wrap that in a systemd timer or a cron job on the host.

::: tip Shorten the retention
24 hours is a long time for files that anyone can fetch by URL. If people use BrandKit interactively and download immediately, `-mmin +60` is a much better privacy posture. See [Privacy](/privacy#retention).
:::

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
