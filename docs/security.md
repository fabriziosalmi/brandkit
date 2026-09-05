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

Only the latest release receives security updates. Currently that is **v1.1.3**; the fixes listed under [Recently closed](#recently-closed) are on `main` and will ship in the next tag.

---

## What is built in

### Request layer

| Control | Implementation | Notes |
| --- | --- | --- |
| **CSRF protection** | Flask-WTF `CSRFProtect` | applies to every `POST`; token minted per session at `GET /` |
| **Rate limiting** | Flask-Limiter | 200/day, 50/hour globally; 5/min on `/upload`; `memory://` storage |
| **Security headers** | Flask-Talisman | CSP, `X-Content-Type-Options`, `X-Frame-Options`, referrer policy |
| **Upload size cap** | `MAX_CONTENT_LENGTH` | 16 MB by default, via `BRANDKIT_MAX_UPLOAD_MB` |
| **Session secret** | `BRANDKIT_SECRET_KEY` | stable across restarts and workers when set; ephemeral with a warning when not |

### Content Security Policy

```
default-src 'self'
img-src     'self' data: blob:
script-src  'self' 'unsafe-inline' 'unsafe-eval'
style-src   'self' 'unsafe-inline'
```

`'unsafe-inline'` and `'unsafe-eval'` are required by Alpine.js, which evaluates expressions from `x-` attributes. That is a real weakening of the CSP and the price of the framework.

No third-party origin is allowed: Tailwind and Alpine are vendored under `static/vendor/` and served same-origin, so nothing external can be loaded even if a script were injected.

### File handling

- **Extension allowlist** — `png`, `jpg`, `jpeg`, `gif`, `webp`, matched case-insensitively after the last dot.
- **`secure_filename()`** on every upload, plus a UUID prefix, so the stored name is `<uuid4>_<sanitised>`.
- **Decode validation** — the file is opened with Pillow immediately. If that fails, the upload is deleted and the request is rejected with `400`.
- **Mandatory EXIF stripping** — the image is re-encoded through a fresh `Image.new()` on receipt, discarding GPS coordinates, camera serials and every other tag. This is not optional and not tied to the `strip_metadata` switch.
- **Scheduled deletion** — a background thread sweeps `static/uploads/` and its cache on an interval, deleting anything past the retention window (hourly, 24 hours, by default). Configurable via [`BRANDKIT_CLEANUP_INTERVAL_HOURS` and `BRANDKIT_RETENTION_HOURS`](/reference/environment).

### No third-party egress

Since v1.1.3, loading the page contacts nothing but your own server. The only outbound connection the app ever makes is rembg fetching its ONNX model on first use, and you can pre-seed that. BrandKit runs air-gapped.

---

## Known hardening gaps

These are real and currently unfixed. They are listed here rather than buried because operators need to make decisions around them.

### Generated assets are world-readable

Everything lands in `static/uploads/`, which Flask serves without any authorisation check, and filenames follow a predictable pattern (`<basename>_<format>.<ext>`). On any instance more than one person can reach, one user's assets are enumerable by another. **Authenticate at the proxy** — see [Deployment](/guide/deployment).

This is the single most important thing to understand before exposing BrandKit to anyone else.

### Error strings are echoed to the client

`/analyze` and parts of `/upload` interpolate the exception message into the JSON response. That can disclose filesystem paths and library internals. Low impact on a trusted network; another reason not to expose the service publicly.

### No virus scanning

Uploaded files are validated as decodable images and nothing more. If you accept files from untrusted people, scan them separately.

### No test suite

CI installs the dependencies and imports the module. There is no automated coverage of the upload path, the CSRF behaviour or the image pipeline, so regressions in any of them would not be caught before release. Contributions welcome — see [Contributing](/contributing#ci).

---

## Recently closed

For operators upgrading from v1.1.3, these were documented gaps that are now fixed:

| Was | Now |
| --- | --- |
| `SECRET_KEY` regenerated per process, breaking CSRF across gunicorn workers | read from `BRANDKIT_SECRET_KEY` (or `FLASK_SECRET_KEY`), with a startup warning when unset |
| CSP still allowed `cdn.tailwindcss.com` and `cdn.jsdelivr.net` | both removed; no third-party script origin is permitted |
| `/download-zip/<filename>` joined the path without validating it | name is checked against `secure_filename()`, restricted to `.zip`, and the resolved path is confirmed to stay inside the upload folder |
| The cleanup thread never ran under gunicorn | started at import time, so it runs under gunicorn too; interval and retention are configurable |
| `zipfile36` pinned but never imported | removed |

## Dependency security

Dependencies are pinned exactly in `requirements.txt` and watched by Dependabot and OSV. The image-processing stack — Pillow above all — is a frequent source of advisories, because parsing untrusted image formats in C is exactly the kind of thing that produces heap overflows.

Dependabot is configured for **security updates only** (`.github/dependabot.yml` sets `open-pull-requests-limit: 0` on every ecosystem). Routine version bumps are not opened automatically: across pip, npm, GitHub Actions and Docker they arrive a dozen at a time and most need a judgement call — a new Python base image, a major action bump, a transitive pin that would violate another package's ceiling. Advisories are the part that has to move quickly, so that is what is automated.

The practical consequence for anyone running BrandKit: **a quiet PR queue does not mean your dependencies are current**, only that nothing has an open advisory. Upgrade deliberately as well.

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
2. **Set `BRANDKIT_SECRET_KEY`.** Without it the key is ephemeral, sessions break on restart, and you cannot run more than one worker.
3. **Terminate TLS at a proxy.** Talisman is configured with `force_https=False` and will not redirect or emit HSTS itself.
4. **Never set `FLASK_ENV=development` on a reachable host.** The Werkzeug debugger is a remote shell.
5. **Bind the container to `127.0.0.1`** and let only the proxy reach it.

---

## Threat model, stated plainly

**In scope:** malformed image files reaching the decoder, CSRF against a logged-in browser, resource exhaustion through large or numerous uploads, metadata leakage from uploaded photographs.

**Out of scope, by design:** multi-tenant isolation, access control, audit logging, and anything that assumes hostile users share an instance. BrandKit has no concept of a user. If you need those properties, they belong in the layer in front of it.
