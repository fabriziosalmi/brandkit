---
title: Configuration
description: The config.json schema — formats, categories, output types and preprocessing defaults.
---

# Configuration

All of BrandKit's tunable behaviour lives in one file at the repository root: **`config.json`**. It is read on every request by `load_config()`, so **changes take effect without a restart** — though a restart is still the safest way to be sure, since a syntax error is silently swallowed.

## The merge rule (read this first)

`config.json` does **not replace** the built-in defaults. It is merged over them, one level deep:

```python
for key, value in file_config.items():
    if key in config and isinstance(config[key], dict) and isinstance(value, dict):
        config[key].update(value)     # shallow merge
    else:
        config[key] = value           # replace
```

Two consequences that surprise everyone at least once:

1. **You cannot delete a built-in format by omitting it from `config.json`.** The 26 formats hard-coded in `DEFAULT_CONFIG` are always present. `config.json` adds to them and overrides same-named keys. That is why the effective catalogue is 45 formats, not the 32 in the file.
2. **`format_categories` is merged by category name.** Supplying `"Social Media": [...]` replaces that category's whole list, but categories you do not mention keep their built-in contents.

If you genuinely need a smaller catalogue, edit `DEFAULT_CONFIG` in `app.py`.

## Failure behaviour

| Situation | What happens |
| --- | --- |
| `config.json` missing | `logger.warning("Configuration file '...' not found...")` — defaults only |
| `config.json` is invalid JSON | `logger.error("Configuration file '...' is not valid JSON...")` — **defaults only, request still succeeds** |
| A format entry lacks `width` or `height` | that format fails at render time, others continue |

The second row is the dangerous one: a broken edit does not produce an error page, it produces a catalogue that quietly reverts. Validate before you trust it:

```bash
python3 -m json.tool config.json > /dev/null && echo "valid JSON"
```

## Top-level shape

```json
{
  "formats": { },
  "format_categories": { },
  "output_formats": ["png", "jpg", "webp", "ico"],
  "preprocessing_options": { }
}
```

## `formats`

A map of format key → canvas definition.

```json
"formats": {
  "website": {
    "width": 1200,
    "height": 630,
    "description": "Standard website banner"
  }
}
```

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `width` | integer | yes | target canvas width in pixels |
| `height` | integer | yes | target canvas height in pixels |
| `description` | string | no | shown next to the checkbox in the UI |

The **key** is what appears in generated filenames and in the `selected_formats` form field. Use lowercase with underscores; it is not sanitised for you, and it ends up in a path.

::: warning `favicon` is special-cased
The `favicon` key triggers `create_favicon()`, which ignores your `width`/`height` and always writes a multi-resolution `.ico` containing 16×16, 32×32 and 48×48. Renaming the key disables ICO generation entirely.
:::

## `format_categories`

A map of display name → list of format keys. Drives the grouping in the UI.

```json
"format_categories": {
  "Social Media": ["social", "twitter", "instagram", "linkedin", "facebook"],
  "Print": ["print_a4", "print_letter", "poster", "business_card"]
}
```

A format key that appears in no category is still generated and still findable through the search box — it simply has no group heading. A category listing a key that does not exist in `formats` is skipped silently.

## `output_formats`

```json
"output_formats": ["png", "jpg", "webp", "ico"]
```

The list of encodings offered in the UI. Only these four values are implemented; adding a fifth string does nothing useful. Removing one hides it from the interface.

## `preprocessing_options`

The default state of every control in the preprocessing panel. All 25 keys, with the shipped defaults:

```json
"preprocessing_options": {
  "grayscale": false,
  "bw": false,
  "invert": false,
  "hue_shift": 0,
  "temperature": 0,
  "enhance_contrast": false,
  "apply_blur": false,
  "blur_radius": 2,
  "add_watermark": false,
  "watermark_text": "© BrandKit",
  "watermark_opacity": 0.3,
  "vignette": false,
  "vignette_strength": 0.5,
  "saturation": 1.0,
  "brightness": 1.0,
  "sharpen": false,
  "sharpen_radius": 1.0,
  "remove_background": false,
  "background_color": "#FFFFFF",
  "edge_smooth": false,
  "noise_reduction": false,
  "auto_crop": false,
  "shadow_effect": false,
  "shadow_opacity": 0.3,
  "shadow_blur": 4
}
```

What each one does is documented in [Image preprocessing](/guide/preprocessing).

::: tip Set your own watermark
`watermark_text` is the one people change most often. Set it to your studio name and it becomes the default for every generation on that instance.
:::

Note that a handful of runtime options accepted by `POST /upload` — `background_removal_method`, `smooth_radius`, `noise_strength`, `crop_padding`, `shadow_offset_x`, `shadow_offset_y`, `enhance_quality` — have hard-coded fallbacks in `app.py` and are **not** read from `config.json`. Adding them to the file has no effect.

## A complete worked example

Adding an email signature banner and a 3:2 case-study image, and changing the default watermark:

```json
{
  "formats": {
    "signature":  { "width": 600,  "height": 150, "description": "Email signature banner" },
    "case_study": { "width": 1500, "height": 1000, "description": "Case study hero (3:2)" }
  },
  "format_categories": {
    "Business Documents": [
      "email_header", "document_header", "presentation_slide", "signature"
    ],
    "Website": [
      "website", "hero_mobile", "hero_desktop", "case_study"
    ]
  },
  "preprocessing_options": {
    "watermark_text": "© Acme Studio"
  }
}
```

Because of the merge rule, this file alone is enough — every other format, category and default is inherited.

Validate, then reload:

```bash
python3 -m json.tool config.json > /dev/null && docker compose restart brandkit
```

## See also

- [Environment variables](/reference/environment) — the settings that are *not* in `config.json`
- [Format catalogue](/reference/format-catalogue) — the effective merged result
