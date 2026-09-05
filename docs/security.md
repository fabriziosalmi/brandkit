---
title: Security
description: BrandKit's security model, its built-in controls, its known gaps, and how to report a vulnerability.
---

# Security

BrandKit is an **unauthenticated, single-tenant image-processing service** designed to run on a machine you control. Every security decision below follows from that. If you deploy it differently, the threat model changes and the mitigations are yours to add.

## Reporting a vulnerability

**Do not open a public GitHub issue for a security vulnerability.**

Email **fabrizio.salmi@gmail.com** with:

- a description of the vulnerability
- steps to reproduce
- the impact you believe it has
- a suggested fix, if you have one
- how to contact you

Machine-readable contact details are published at [`/.well-known/security.txt`](/.well-known/security.txt) per [RFC 9116](https://www.rfc-editor.org/rfc/rfc9116).

### What to expect

| Stage | Target |
| --- | --- |
| Acknowledgement | within 48 hours |
| Initial assessment | within 5 business days |
| Progress updates | every 7 days until resolved |
| Fix for a critical issue | within 30 days |
| Public disclosure | within 90 days of a fix, timing coordinated with you |

Researchers are credited unless they prefer to stay anonymous.

### Severity

| Level | Examples |
| --- | --- |
| **Critical** | remote code execution, authentication bypass |
| **High** | data exposure, privilege escalation |
| **Medium** | XSS, CSRF not covered by existing protections |
| **Low** | information disclosure, minor issues |

### Supported versions

Only the latest release receives security updates. Currently that is **v1.1.3**.

---

## What is built in

### Request layer

| Control | Implementation | Notes |
| --- | --- | --- |
| **CSRF protection** | Flask-WTF `CSRFProtect` | applies to every `POST`; token minted per session at `GET /` |
| **Rate limiting** | Flask-Limiter | 200/day, 50/hour globally; 5/min on `/upload`; `memory://` storage |
| **Security headers** | Flask-Talisman | CSP, `X-Content-Type-Options`, `X-Frame-Options`, referrer policy |
| **Upload size cap** | `MAX_CONTENT_LENGTH` | 16 MB by default, via `BRANDKIT_MAX_UPLOAD_MB` |

### Content Security Policy

```
default-src 'self'
img-src     'self' data: blob:
script-src  'self' 'unsafe-inline' 'unsafe-eval'
            https://cdn.tailwindcss.com/ https://cdn.jsdelivr.net/
style-src   'self' 'unsafe-inline'
```

`'unsafe-inline'` and `'unsafe-eval'` are required by Alpine.js, which evaluates expressions from `x-` attributes. That is a real weakening of the CSP and the price of the framework.

The two CDN origins are **vestigial** — since v1.1.3 both libraries are vendored under `static/vendor/` and served same-origin, and the page makes no third-party requests. The CSP has not caught up; see [the gaps below](#known-hardening-gaps).

### File handling

- **Extension allowlist** — `png`, `jpg`, `jpeg`, `gif`, `webp`, matched case-insensitively after the last dot.
- **`secure_filename()`** on every upload, plus a UUID prefix, so the stored name is `<uuid4>_<sanitised>`.
- **Decode validation** — the file is opened with Pillow immediately. If that fails, the upload is deleted and the request is rejected with `400`.
- **Mandatory EXIF stripping** — the image is re-encoded through a fresh `Image.new()` on receipt, discarding GPS coordinates, camera serials and every other tag. This is not optional and not tied to the `strip_metadata` switch.
- **Scheduled deletion** — `cleanup_old_files()` removes anything older than 24 hours. See the caveat in [Performance](/guide/performance#file-cleanup).

### No third-party egress

Since v1.1.3, loading the page contacts nothing but your own server. The only outbound connection the app ever makes is rembg fetching its ONNX model on first use, and you can pre-seed that. BrandKit runs air-gapped.

---

## Known hardening gaps

These are real and currently unfixed. They are listed here rather than buried because operators need to make decisions around them.

### The secret key is regenerated per process

```python
app.config['SECRET_KEY'] = os.urandom(24)
```

Set unconditionally at import time. Consequences:

- **Every restart invalidates every session and CSRF token.** A user who had the page open gets a `400` on submit.
- **Every gunicorn worker holds a different key.** With more than one worker, a token minted by worker A is rejected by worker B, so uploads fail roughly `(n−1)/n` of the time.

`entrypoint.sh` does not pass `--workers`, so gunicorn's default of **1** applies and the second problem does not bite out of the box. **Do not add workers until this is fixed.**

The project README documents a `FLASK_SECRET_KEY` environment variable. It is not implemented — nothing reads it. See [Environment variables](/reference/environment#not-implemented).

### The CSP still allows two CDN origins

`script-src` permits `cdn.tailwindcss.com` and `cdn.jsdelivr.net` even though nothing loads from them any more. It does not create a vulnerability by itself, but it widens the set of origins an injected script could be loaded from, and it undercuts the point of vendoring. Removing both entries is a one-line change with no functional impact.

### `/download-zip/<filename>` does not normalise its path

```python
zip_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
```

There is no `secure_filename()` call and no check that the resolved path stays inside the upload folder. Flask's default URL converter does not match `/`, which is what prevents straightforward traversal, so this is defence-in-depth rather than a live exploit — but it is free to add and the current code depends on routing behaviour rather than on its own validation.

### Generated assets are world-readable

Everything lands in `static/uploads/`, which Flask serves without any authorisation check, and filenames follow a predictable pattern. On any instance more than one person can reach, one user's assets are enumerable by another. **Authenticate at the proxy** — see [Deployment](/guide/deployment).

### Error strings are echoed to the client

`/analyze` and parts of `/upload` interpolate the exception message into the JSON response. That can disclose filesystem paths and library internals. Low impact on a trusted network; another reason not to expose the service publicly.

### Cleanup does not run under gunicorn

The scheduled cleanup thread starts inside `if __name__ == '__main__':`, which gunicorn never executes. On a container deployment nothing is ever deleted and `static/uploads/` grows without bound — a disk-exhaustion risk as much as a privacy one. Workarounds in [Performance](/guide/performance#file-cleanup).

### No virus scanning

Uploaded files are validated as decodable images and nothing more. If you accept files from untrusted people, scan them separately.

---

## Dependency security

Dependencies are pinned exactly in `requirements.txt` and watched by Dependabot and OSV. The image-processing stack — Pillow above all — is a frequent source of advisories, because parsing untrusted image formats in C is exactly the kind of thing that produces heap overflows.

**Keep Pillow current. It is the single most security-relevant dependency in this project**, and it is the one that sits directly in front of attacker-controlled bytes.

```bash
# see what is outdated
pip list --outdated

# check installed packages against the OSV database
pip install pip-audit && pip-audit
```

Rebuild the container after any bump: `docker compose up -d --build`.

---

## Deployment guidance

The full checklist is in [Deployment](/guide/deployment#production-checklist). The four that matter most:

1. **Authenticate everything, including `/static/`.** Basic auth is enough for a small team; Cloudflare Access is better.
2. **Terminate TLS at a proxy.** Talisman is configured with `force_https=False` and will not redirect or emit HSTS itself.
3. **Never set `FLASK_ENV=development` on a reachable host.** The Werkzeug debugger is a remote shell.
4. **Bind the container to `127.0.0.1`** and let only the proxy reach it.

---

## Threat model, stated plainly

**In scope:** malformed image files reaching the decoder, CSRF against a logged-in browser, resource exhaustion through large or numerous uploads, metadata leakage from uploaded photographs.

**Out of scope, by design:** multi-tenant isolation, access control, audit logging, and anything that assumes hostile users share an instance. BrandKit has no concept of a user. If you need those properties, they belong in the layer in front of it.
