---
title: Security
description: BrandKit security architecture, builtin protections, operational considerations, and vulnerability disclosure.
---

# Security

BrandKit is an **unauthenticated, single-tenant image-processing service** designed for deployment within trusted environments. Every security decision follows from that model. When exposing the application across untrusted networks, perimeter security controls must be implemented at the reverse proxy layer.

## Reporting a vulnerability

**Do not open a public GitHub issue for security disclosures.**

Email **fabrizio.salmi@gmail.com** with:

- Vulnerability description and impact assessment
- Reproduction steps and proof of concept
- Remediation proposal (if available)
- Contact details

Machine-readable contact metadata is published at [`/.well-known/security.txt`](/.well-known/security.txt) per [RFC 9116](https://www.rfc-editor.org/rfc/rfc9116).

### Response timeline

| Stage | Target window |
| --- | --- |
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 5 business days |
| Status updates | Every 7 days until resolved |
| Remediation (Critical) | Within 30 days |
| Public disclosure | Within 90 days, coordinated with reporter |

Researchers are credited upon publication unless anonymity is requested.

### Severity classification

| Level | Examples |
| --- | --- |
| **Critical** | Remote code execution, arbitrary file writes |
| **High** | Data exposure, path traversal |
| **Medium** | Cross-site scripting (XSS), cross-site request forgery (CSRF) bypass |
| **Low** | Verbose error disclosures, localized resource consumption |

### Supported versions

Security patches are published exclusively against the latest release branch (currently **v1.1.4**).

---

## Built-in security controls

### Request handling

| Control | Mechanism | Description |
| --- | --- | --- |
| **CSRF defense** | Flask-WTF `CSRFProtect` | Enforced on all state-changing HTTP POST endpoints; token minted on `GET /` |
| **Rate limiting** | Flask-Limiter | 200/day, 50/hour globally; 5/min on `/upload`; in-memory tracking |
| **Security headers** | Flask-Talisman | CSP, `X-Content-Type-Options`, `X-Frame-Options`, strict referrer policy |
| **Payload ceiling** | `MAX_CONTENT_LENGTH` | 16 MB default, configurable via `BRANDKIT_MAX_UPLOAD_MB` |
| **Session secret** | `BRANDKIT_SECRET_KEY` | Deterministic secret storage; displays startup warning when omitted |

### Content Security Policy

```
default-src 'self'
img-src     'self' data: blob:
script-src  'self' 'unsafe-inline' 'unsafe-eval'
style-src   'self' 'unsafe-inline'
```

`'unsafe-inline'` and `'unsafe-eval'` are required by Alpine.js for declarative directive execution.

No external origins are permitted: Tailwind CSS and Alpine.js assets are vendored under `static/vendor/` and served same-origin, eliminating external script injection vectors.

### File system integrity

- **Extension validation:** Restricted to `png`, `jpg`, `jpeg`, `gif`, `webp` (matched case-insensitively).
- **Name sanitization:** `secure_filename()` applied to all incoming uploads alongside a UUID4 prefix (`<uuid4>_<sanitized>`).
- **Buffer validation:** Uploads are immediately parsed through Pillow. Corrupt or unparseable buffers are deleted and rejected with HTTP 400.
- **Mandatory EXIF stripping:** Ingested images are re-encoded through a clean Pillow memory buffer, stripping camera metadata, serials, and geolocation coordinates.
- **Scheduled purge:** Internal worker thread sweeps `static/uploads/` and cache directories according to configured retention periods.

### Network isolation

Loading application pages initiates zero external network requests. The only external request the container can trigger is downloading neural weights on initial background removal invocations, which can be pre-cached to support air-gapped environments.

---

## Operational hardening considerations

### Asset visibility

Files in `static/uploads/` are served without authentication. On multi-tenant or internet-exposed instances, enforce access control at the reverse proxy layer (see [Deployment](/guide/deployment)).

### Verbose error feedback

Selected endpoints (`/analyze`) return raw error strings for debugging convenience. In production, proxy layers should intercept 5xx errors to prevent revealing filesystem paths.

### Antivirus scanning

Buffers are validated for image decodability. Deploy an external antivirus scanner if processing untrusted public submissions.

---

## Dependency management

Dependencies are pinned in `requirements.txt` and monitored via Dependabot and OSV audits. Image processing libraries (particularly Pillow) require consistent maintenance:

```bash
# Audit installed packages against known CVEs
pip install pip-audit && pip-audit
```

Rebuild container images after applying updates: `docker compose up -d --build`.

---

## Core deployment rules

1. **Authenticate site-wide:** Enforce reverse-proxy authentication over both application endpoints and `/static/`.
2. **Configure `BRANDKIT_SECRET_KEY`:** Required for multi-worker Gunicorn stability.
3. **Terminate TLS externally:** Configure reverse proxies to manage certificates and enforce HSTS.
4. **Enforce `FLASK_ENV=production`:** Never enable debug mode in exposed environments.
5. **Bind container to localhost:** Map `"127.0.0.1:8000:8000"` to avoid exposing internal sockets to public network interfaces.

---

## Threat model boundaries

**In scope:** Image parser exploit mitigation, CSRF protection, resource limit enforcement, EXIF metadata sanitization.

**Out of scope:** Native multi-tenant isolation, user identity management, audit logging. Security boundaries must be enforced upstream.
