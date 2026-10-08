---
title: HTTP endpoints
description: Specification for BrandKit HTTP endpoints, request parameters, responses, and CSRF handling.
---

# HTTP endpoints

BrandKit exposes five HTTP endpoints utilized by the frontend interface:

| Method | Path | CSRF required | Rate limit | Description |
| --- | --- | --- | --- | --- |
| `GET` | `/` | No | Default | Application interface; sets session cookie and CSRF token |
| `POST` | `/upload` | Yes | 5/min | Master image upload and asset generation |
| `POST` | `/analyze` | Yes | Default | Color telemetry and boundary analysis |
| `GET` | `/format-info` | No | Default | Format definitions, categories, and presets |
| `GET` | `/download-zip/<filename>` | No | Default | Export archive download |

Default rate limit is **200 per day and 50 per hour** per client IP, tracked in worker process memory.

## Authentication and CSRF

BrandKit does not implement user accounts. Protect networked instances using an authenticating reverse proxy (see [Deployment](/guide/deployment)).

Both `POST` endpoints enforce CSRF validation via Flask-WTF `CSRFProtect`. Tokens are generated per session and rendered in the initial `GET /` document. Scripted clients must obtain the session cookie and CSRF token:

```bash
COOKIES=$(mktemp)

# 1. Retrieve session cookie and extract CSRF token
TOKEN=$(curl -s -c "$COOKIES" http://localhost:8000/ \
  | grep -o "csrf_token', '[^']*'" | head -1 | cut -d"'" -f3)

# 2. Transmit request with session cookie and CSRF token header/field
curl -s -b "$COOKIES" \
  -F "csrf_token=$TOKEN" \
  -F "file=@logo.png" \
  -F "selected_formats=website" \
  -F "output_formats=png" \
  http://localhost:8000/upload
```

Requests lacking valid CSRF tokens return HTTP 400 (`The CSRF token is missing`).

For an automated implementation, refer to the [Python client](#a-python-client) example.

---

## `POST /upload`

Processes the uploaded master image and generates requested formats.

**Content-Type:** `multipart/form-data`
**Rate limit:** 5 requests per minute per IP

### Payload parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `file` | file | Yes | `png`, `jpg`, `jpeg`, `gif`, `webp`. Max size: `BRANDKIT_MAX_UPLOAD_MB` (16 MB default) |
| `selected_formats` | string (repeatable) | No | Format keys. If omitted, defaults to all 45 formats |
| `output_formats` | string (repeatable) | No | `png`, `jpg`, `webp`, `ico` (default: `png`) |
| `variations_mode` | string | No | Set `"true"` to generate 10 stylistic treatments per format |
| `fill_white_with_prominent` | string | No | Set `"true"` to composite prominent color onto white backgrounds |

### Preprocessing parameters

Optional form fields. Booleans accept literal string `"true"`:

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `grayscale` | bool | `false` | Desaturate RGB channels |
| `bw` | bool | `false` | Binary 1-bit monochrome threshold |
| `invert` | bool | `false` | Invert RGB values |
| `hue_shift` | int (-180..180) | `0` | Rotate color hue in degrees |
| `temperature` | int (-100..100) | `0` | Color temperature balance |
| `enhance_contrast` | bool | `false` | Histogram contrast equalization |
| `saturation` | float | `1.0` | Color saturation multiplier |
| `brightness` | float | `1.0` | Brightness multiplier |
| `sharpen` | bool | `false` | Unsharp masking filter |
| `sharpen_radius` | float | `1.0` | Sharpening kernel radius |
| `apply_blur` | bool | `false` | Gaussian blur |
| `blur_radius` | float | `2.0` | Blur radius in pixels |
| `noise_reduction` | bool | `false` | Median filter denoising |
| `noise_strength` | int | `1` | Denoising kernel size |
| `vignette` | bool | `false` | Radial edge darkening |
| `vignette_strength` | float | `0.5` | Vignette intensity scale (0.0 to 1.0) |
| `add_watermark` | bool | `false` | Render textual watermark |
| `watermark_text` | string | `© BrandKit` | Watermark text string |
| `watermark_opacity` | float | `0.3` | Watermark alpha opacity |
| `auto_crop` | bool | `false` | Trim empty boundary margins |
| `crop_padding` | int | `10` | Margin in pixels retained around cropped subject |
| `remove_background` | bool | `false` | Neural U²-Net segmentation |
| `background_removal_method` | enum | `auto` | Model selection: `auto`, `object`, `person`, `anime` |
| `background_color` | string | `transparent` | Hex code (`#ffffff`) or `transparent` |
| `edge_smooth` | bool | `false` | Alpha edge antialiasing |
| `smooth_radius` | float | `2.0` | Edge antialiasing radius |
| `shadow_effect` | bool | `false` | Render drop shadow behind alpha boundary |
| `shadow_opacity` | float | `0.3` | Drop shadow opacity |
| `shadow_blur` | int | `4` | Shadow blur radius |
| `shadow_offset_x` | int | `5` | Horizontal shadow offset |
| `shadow_offset_y` | int | `5` | Vertical shadow offset |
| `enhance_quality` | bool | `false` | Multi-filter enhancement pass |
| `quality` | int (1..100) | `95` | JPEG and WebP quantization quality |
| `strip_metadata` | bool | `false` | Discard ICC profile and metadata headers from outputs |

### Response payload (HTTP 200)

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

### Error codes

| Code | Payload | Cause |
| --- | --- | --- |
| `400` | `{"error": "No file part"}` | Missing `file` form part |
| `400` | `{"error": "No selected file"}` | Empty filename submitted |
| `400` | `{"error": "File type not allowed"}` | Disallowed extension |
| `400` | `{"error": "Invalid image file"}` | Buffer decoding error |
| `400` | CSRF error page | Invalid or missing CSRF token |
| `413` | Empty body | Request payload exceeds `MAX_CONTENT_LENGTH` |
| `429` | Empty body | Rate limit exceeded |
| `500` | `{"error": "An unexpected error occurred during processing."}` | Processing error; check server logs |

---

## `POST /analyze`

Inspects an image buffer without generating downstream targets.

**Content-Type:** `multipart/form-data` | **Parameter:** `file` | **CSRF:** Required

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

The temporary upload buffer is deleted immediately after analysis.

---

## `GET /format-info`

Returns active format catalogue definitions and preset bundles.

```json
{
  "success": true,
  "categories": { "Social Media": ["social", "twitter"] },
  "purposes":   { "social": ["social", "twitter"] },
  "recommendations": {
    "Social Media Pack": ["social", "twitter", "instagram", "facebook", "social_icon_large"],
    "Website Essentials": ["website", "favicon", "hero_desktop", "background_desktop"],
    "Mobile App Pack": ["webapp", "mobile", "square_logo_small", "square_logo_large"],
    "Complete Branding": ["social", "website", "favicon", "webapp", "background_desktop"]
  }
}
```

---

## `GET /download-zip/<filename>`

Streams generated ZIP archives as binary attachments.

```bash
curl -OJ http://localhost:8000/download-zip/acme_brandkit_20260905143012.zip
```

Filenames must survive `secure_filename()` sanitization, retain the `.zip` extension, and resolve within the authorized upload directory. Traversal attempts and missing files return HTTP 404.

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
        timeout=300,
    )

r.raise_for_status()
results = r.json()["results"]

zip_url = results["zip"]["url"]
archive = s.get(f"{BASE}{zip_url}", timeout=120)
with open(results["zip"]["filename"], "wb") as f:
    f.write(archive.content)

print("Generated formats:", [k for k in results if k not in ("original", "analysis", "zip")])
```
