---
title: HTTP endpoints
description: The five routes BrandKit exposes, their parameters, responses and CSRF requirements.
---

# HTTP endpoints

BrandKit exposes five routes. There is no versioned API surface and no stability guarantee — these are the endpoints the built-in UI talks to, documented so you can script against them.

| Method | Path | CSRF | Rate limit | Purpose |
| --- | --- | --- | --- | --- |
| `GET` | `/` | — | default | The application UI; also issues the CSRF token |
| `POST` | `/upload` | **required** | 5/min | Generate a brand kit |
| `POST` | `/analyze` | **required** | default | Colour and white-area analysis only |
| `GET` | `/format-info` | — | default | Format catalogue, categories and presets |
| `GET` | `/download-zip/<filename>` | — | default | Download a generated archive |

The default rate limit is **200 per day and 50 per hour**, per client IP, held in process memory.

## Authentication and CSRF

There is **no authentication**. Any client that can reach the port can use every endpoint. Put an authenticating proxy in front of a deployment — see [Deployment](/guide/deployment).

Both `POST` endpoints are protected by Flask-WTF's `CSRFProtect`. A token is minted per session and rendered into the page at `GET /`; a scripted client has to fetch it and carry the session cookie.

```bash
COOKIES=$(mktemp)

# 1. Fetch the page, keep the session cookie, scrape the token
TOKEN=$(curl -s -c "$COOKIES" http://localhost:8000/ \
  | grep -o "csrf_token', '[^']*'" | head -1 | cut -d"'" -f3)

# 2. Use both on the POST
curl -s -b "$COOKIES" \
  -F "csrf_token=$TOKEN" \
  -F "file=@logo.png" \
  -F "selected_formats=website" \
  -F "output_formats=png" \
  http://localhost:8000/upload
```

Without a valid token you get `400 Bad Request — The CSRF token is missing`.

::: tip Scripting this properly
See the [Python client](#a-python-client) at the bottom of this page for a version that handles the session, retries and the ZIP download.
:::

---

## `POST /upload`

Uploads a source image and generates every selected format in every selected output type.

**Content type:** `multipart/form-data`
**Rate limit:** 5 per minute per IP

### File

| Field | Required | Notes |
| --- | --- | --- |
| `file` | yes | `png`, `jpg`, `jpeg`, `gif` or `webp`; max `BRANDKIT_MAX_UPLOAD_MB` (16 by default) |

### Selection

| Field | Repeatable | Default | Notes |
| --- | --- | --- | --- |
| `selected_formats` | yes | **all 45 formats** | one field per format key |
| `output_formats` | yes | `png` | `png`, `jpg`, `webp`, `ico` |
| `variations_mode` | no | `false` | `"true"` renders 10 variations per format |
| `fill_white_with_prominent` | no | `false` | `"true"` replaces detected white areas with the prominent colour |

::: warning Omitting `selected_formats` is not a shortcut
It does not mean "none" — it means **all 45**, multiplied by every output type. Always send the formats you actually want.
:::

### Preprocessing

All optional. Booleans are the literal string `"true"`; anything else is false.

| Field | Type | Default |
| --- | --- | --- |
| `grayscale` | bool | `false` |
| `bw` | bool | `false` |
| `invert` | bool | `false` |
| `hue_shift` | int (−180…180) | `0` |
| `temperature` | int (−100…100) | `0` |
| `enhance_contrast` | bool | `false` |
| `saturation` | float | `1.0` |
| `brightness` | float | `1.0` |
| `sharpen` | bool | `false` |
| `sharpen_radius` | float | `1.0` |
| `apply_blur` | bool | `false` |
| `blur_radius` | float | `2.0` |
| `noise_reduction` | bool | `false` |
| `noise_strength` | int | `1` |
| `vignette` | bool | `false` |
| `vignette_strength` | float | `0.5` |
| `add_watermark` | bool | `false` |
| `watermark_text` | string | `© BrandKit` |
| `watermark_opacity` | float | `0.3` |
| `auto_crop` | bool | `false` |
| `crop_padding` | int | `10` |
| `remove_background` | bool | `false` |
| `background_removal_method` | `auto`\|`object`\|`person`\|`anime` | `auto` |
| `background_color` | hex or `transparent` | `transparent` |
| `edge_smooth` | bool | `false` |
| `smooth_radius` | float | `2.0` |
| `shadow_effect` | bool | `false` |
| `shadow_opacity` | float | `0.3` |
| `shadow_blur` | int | `4` |
| `shadow_offset_x` | int | `5` |
| `shadow_offset_y` | int | `5` |
| `enhance_quality` | bool | `false` |
| `quality` | int (1–100) | `95` |
| `strip_metadata` | bool | `false` |

Defaults for most of these come from `preprocessing_options` in [`config.json`](/reference/configuration#preprocessing-defaults); the last seven are hard-coded in `app.py`.

### Response — `200 OK`

```json
{
  "success": true,
  "message": "File processed successfully",
  "results": {
    "original": {
      "path": "static/uploads/8f3c…-acme.png",
      "url": "/static/uploads/8f3c…-acme.png"
    },
    "analysis": {
      "prominent_color": [37, 99, 235],
      "has_white_area": true,
      "white_area_ratio": 0.42
    },
    "website": {
      "dimensions": "1200x630",
      "description": "Standard website banner",
      "outputs": {
        "png": {
          "path": "static/uploads/acme_website.png",
          "url": "/static/uploads/acme_website.png"
        }
      }
    },
    "favicon_ico": {
      "path": "static/uploads/acme_favicon.ico",
      "url": "/static/uploads/acme_favicon.ico"
    },
    "zip": {
      "path": "static/uploads/acme_brandkit_20260905143012.zip",
      "url": "/static/uploads/acme_brandkit_20260905143012.zip",
      "filename": "acme_brandkit_20260905143012.zip"
    }
  }
}
```

Every key in `results` other than `original`, `analysis`, `zip`, `favicon_ico` and `variations` is a format key. With `variations_mode=true`, the per-format entries move under `results.variations.<Label>.<format>.outputs`.

### Errors

| Code | Body | Cause |
| --- | --- | --- |
| `400` | `{"error": "No file part"}` | no `file` field |
| `400` | `{"error": "No selected file"}` | empty filename |
| `400` | `{"error": "File type not allowed"}` | extension not in the allowlist |
| `400` | `{"error": "Invalid image file"}` | Pillow could not decode it; the upload is deleted |
| `400` | CSRF error page | missing or stale token |
| `413` | — | over `MAX_CONTENT_LENGTH` |
| `429` | — | rate limit |
| `500` | `{"error": "An unexpected error occurred during processing."}` | see server logs |

Individual formats that fail are skipped silently — they are simply absent from `results`. A `200` does not guarantee you got everything you asked for; compare the keys.

---

## `POST /analyze`

Analyses an image without generating anything. Useful to preview what the smart-fill heuristic will decide.

**Content type:** `multipart/form-data` · **Field:** `file` · **CSRF:** required

```json
{
  "success": true,
  "analysis": {
    "prominent_color": [37, 99, 235],
    "has_white_area": true,
    "white_area_ratio": 0.42
  }
}
```

`prominent_color` is `[r, g, b]`, ignoring near-white pixels. `has_white_area` is true when more than **15%** of the image is near-white. The file is written to a temporary path, read, and deleted in a `finally` block — nothing is retained.

On error the endpoint returns `{"success": false, "error": "…"}` with `400` or `500`.

::: warning Error strings are echoed back
Failure responses interpolate the exception message into `error`. That can leak filesystem paths to the caller. One more reason not to expose this to strangers.
:::

---

## `GET /format-info`

No parameters, no CSRF, no side effects. Good liveness probe.

```json
{
  "success": true,
  "categories": { "Social Media": ["social", "twitter", "…"] },
  "purposes":   { "social": ["social", "twitter", "…"] },
  "recommendations": {
    "Social Media Pack": ["social", "twitter", "instagram", "facebook", "social_icon_large"],
    "Website Essentials": ["website", "favicon", "hero_desktop", "background_desktop"],
    "Mobile App Pack": ["webapp", "mobile", "square_logo_small", "square_logo_large"],
    "Complete Branding": ["social", "website", "favicon", "webapp", "background_desktop"]
  }
}
```

`categories` reflects your live `config.json`. `purposes` and `recommendations` are hard-coded in `app.py` and are **not** kept in sync with the catalogue — a few keys they reference no longer exist. Treat them as UI hints, not as a contract.

---

## `GET /download-zip/<filename>`

Streams an archive from the upload folder as an attachment.

```bash
curl -OJ http://localhost:8000/download-zip/acme_brandkit_20260905143012.zip
```

The filename is validated: it must survive `secure_filename()` unchanged, end in `.zip`, and resolve to a path inside the upload folder. Anything else — including traversal attempts — returns `404`, as does a file that has already been swept by the retention cleanup.

::: danger The route is unauthenticated, and so is `/static/uploads/`
Validation stops path traversal, not access. This route performs no authorisation check, and every generated file is *also* reachable directly under `/static/uploads/<name>`. Filenames are predictable (`<basename>_<format>.<ext>`), so on a shared instance one user's assets are guessable by another. Authenticate at the proxy. See [Privacy](/privacy).
:::

---

## A Python client

```python
import re
import requests

BASE = "http://localhost:8000"

s = requests.Session()
page = s.get(f"{BASE}/").text
token = re.search(r"csrf_token', '([^']+)'", page).group(1)

with open("logo.png", "rb") as fh:
    r = s.post(
        f"{BASE}/upload",
        files={"file": fh},
        data=[
            ("csrf_token", token),
            ("selected_formats", "website"),
            ("selected_formats", "favicon"),
            ("selected_formats", "social"),
            ("output_formats", "png"),
            ("output_formats", "ico"),
            ("auto_crop", "true"),
            ("crop_padding", "16"),
            ("quality", "95"),
        ],
        timeout=300,          # background removal can be slow
    )

r.raise_for_status()
results = r.json()["results"]

zip_url = results["zip"]["url"]
archive = s.get(f"{BASE}{zip_url}", timeout=120)
open(results["zip"]["filename"], "wb").write(archive.content)

print("generated:", [k for k in results if k not in
                     ("original", "analysis", "zip")])
```

Note the repeated `selected_formats` and `output_formats` entries — that is why `data` is a list of tuples rather than a dict.

The 300-second timeout is not paranoia: a first-run background removal downloads a 180 MB model before it does any work.
