---
title: Configuration
description: Schema specification for config.json covering formats, categories, encodings, and preprocessing defaults.
---

# Configuration

Tunable application parameters reside in a single root file: **`config.json`**. The configuration is evaluated by `load_config()`, allowing modifications to take effect immediately. Restarting the service confirms that schema updates are parsed without syntax errors.

## The merge rule

`config.json` does **not replace** built-in defaults; it merges on top of them:

```python
# Custom formats and categories are validated (positive integer dimensions)
# and merged into default configuration:
for fmt_name, fmt_spec in file_config.get('formats', {}).items():
    if validate_format_spec(fmt_name, fmt_spec):
        config['formats'][fmt_name] = fmt_spec
```

Key operational implications:

1. **Built-in formats cannot be removed by omission:** The base formats defined in `DEFAULT_CONFIG` remain active. Entries in `config.json` add new specifications or override existing keys with identical names.
2. **Category lists merge by category identifier:** Specifying `"Social Media": [...]` replaces that category array entirely, while unspecified categories retain their built-in defaults.

To restrict output options to an exclusive custom subset, adjust `DEFAULT_CONFIG` in `app.py`.

## Failure handling

| Condition | Behavior |
| --- | --- |
| `config.json` missing | `logger.warning(...)`: falls back to built-in presets |
| `config.json` invalid JSON | `logger.error(...)`: falls back to built-in presets without interrupting requests |
| Format spec missing dimensions | The invalid format fails during rendering; remaining formats proceed |

Validate custom configurations before deploying:

```bash
python3 -m json.tool config.json > /dev/null && echo "valid JSON"
```

## Top-level structure

```json
{
  "formats": { },
  "format_categories": { },
  "output_formats": ["png", "jpg", "webp", "ico"],
  "preprocessing_options": { }
}
```

## `formats`

Mapping of format keys to canvas dimensions:

```json
"formats": {
  "website": {
    "width": 1200,
    "height": 630,
    "description": "Standard website banner"
  }
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `width` | integer | Yes | Target canvas width in pixels |
| `height` | integer | Yes | Target canvas height in pixels |
| `description` | string | No | Label rendered alongside the UI checkbox |

Format keys determine output filenames and form payload values. Use lowercase alphanumeric characters and underscores.

::: warning `favicon` key behavior
The `favicon` key invokes `create_favicon()`, generating a multi-resolution `.ico` container with 16×16, 32×32, and 48×48 dimensions. Renaming the key disables `.ico` bundling.
:::

## `format_categories`

Mapping of category titles to format keys:

```json
"format_categories": {
  "Social Media": ["social", "twitter", "instagram", "linkedin", "facebook"],
  "Print": ["print_a4", "print_letter", "poster", "business_card"]
}
```

Format keys excluded from categories remain available via search filters. Category references to undefined format keys are skipped during rendering.

## `output_formats`

```json
"output_formats": ["png", "jpg", "webp", "ico"]
```

Controls the active encoding options presented in the UI.

## `preprocessing_options`

Sets default values for image processing controls across 25 keys:

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

Consult [Image preprocessing](/guide/preprocessing) for detailed parameter interactions.

Runtime parameters such as `background_removal_method`, `smooth_radius`, `noise_strength`, `crop_padding`, `shadow_offset_x`, `shadow_offset_y`, and `enhance_quality` use internal fallbacks defined in `app.py`.

## Configuration example

Customizing signature banners and updating default watermark text:

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

Due to the merge rule, undefined formats and categories retain their standard defaults.

Validate and apply changes:

```bash
python3 -m json.tool config.json > /dev/null && docker compose restart brandkit
```

## Related documentation

- [Environment variables](/reference/environment): runtime and deployment flags
- [Format catalogue](/reference/format-catalogue): complete list of default dimensions
