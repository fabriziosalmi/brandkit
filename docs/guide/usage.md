---
title: The generation workflow
description: Sequential guide to BrandKit controls, parameters, and asset generation.
---

# The generation workflow

BrandKit operates as a single-page interface organized into logical pipeline stages:

## 1. Master image ingestion

Drag an image into the upload area, click to browse, or paste directly from the clipboard via <kbd>⌘+V</kbd> / <kbd>Ctrl+V</kbd>. With the drop area focused, pressing <kbd>Space</kbd> opens the native file selector.

**Supported formats:** `png`, `jpg`, `jpeg`, `gif`, `webp`.
**Size ceiling:** 16 MB by default; configure via [`BRANDKIT_MAX_UPLOAD_MB`](/reference/environment).

### Source image recommendations

Because all downstream targets scale from the ingested master, optimal results require clean input:

- **Square or near-square PNG with transparency:** Composites cleanly across contrasting backgrounds and formats.
- **Minimum 1024 px along the shortest dimension:** Ensures large formats (`square_large` at 2048×2048, `print_a4` at 2480×3508) retain edge sharpness.
- **Uncompressed transparent buffers:** When source logos reside on solid JPEG backgrounds, enable background removal in preprocessing.

Upon file receipt, the engine strips EXIF metadata automatically and computes color telemetry, extracting dominant tones and inspecting boundary alpha distributions.

## 2. Format selection

Formats are grouped into functional categories: Social Media, Website, Mobile, Branding, Web Application, E-commerce, Print, Business Documents, Publishing, and General Purpose. Use category toggles or the search filter to select target dimensions.

If no format is checked, BrandKit defaults to all 45 canvases. For faster runs, select target presets deliberately.

Pixel dimensions and aspect ratios are listed in the [format catalogue](/reference/format-catalogue).

## 3. Output encodings

| Encoding | Alpha channel | Primary use cases |
| --- | --- | --- |
| **PNG** | Yes | Marks, icons, UI components requiring transparency |
| **JPG** | No | Photographic assets, large banners requiring compression |
| **WebP** | Yes | Modern web delivery with optimized compression ratios |
| **ICO** | Yes | Multi-resolution browser favicons |

Multiple encodings can be selected concurrently; each chosen format is rendered into every checked encoding.

::: info ICO coupling
The `.ico` encoding is generated exclusively when the `favicon` canvas format is selected. If `.ico` is selected without `favicon`, the format is omitted. The resulting ICO contains 16×16, 32×32, and 48×48 icon layers.
:::

## 4. Preprocessing parameters

Preprocessing adjustments are computed once against the master image buffer prior to format rendering, maintaining stylistic parity across all output assets.

For technical descriptions of all filters, refer to [Image preprocessing](/guide/preprocessing) and [Background removal](/guide/background-removal).

Key encoding options:
- **Quality** (default `95`): Controls JPEG and WebP quantization matrices. Ignored for PNG.
- **Strip metadata** (default disabled): Discards ICC color profiles and residual headers from output assets.

## 5. Smart background fill

When color analysis detects that greater than 15% of the master bounds are near-white, the application offers automated solid or radial gradient compositing derived from extracted brand hues.

## 6. Variations mode

Enabling **variations mode** generates a matrix of ten distinct stylistic treatments per selected format:

| Variation | Transformation |
| --- | --- |
| `Original` | Unmodified master |
| `Grayscale` | Luminance desaturation |
| `B&W` | 1-bit monochrome threshold |
| `Inverted` | Color negative |
| `Hue_+60` / `Hue_-60` | Hue rotation ±60° |
| `Warm` / `Cool` | Color temperature shift ±40 |
| `Grayscale_Contrast` | Desaturation with histogram equalization |
| `Inverted_Blur` | Color negative with Gaussian blur |

::: danger Multiplies total render volume
Ten formats × two output types × variations mode produces 200 distinct files. Use variations mode selectively to test stylistic directions.
:::

## 7. Pipeline execution

Click **Generate** or press <kbd>⌘</kbd>+<kbd>Enter</kbd> / <kbd>Ctrl</kbd>+<kbd>Enter</kbd>.

Uploads are rate-limited to 5 submissions per minute per IP address, within a global ceiling of 200 daily requests.

## 8. Review and export

The results section displays interactive preview cards alongside a high-density data table with direct download links and pixel dimensions. The complete collection is packaged as a unified ZIP archive.

Output files follow deterministic naming schemes:

```
<source-basename>_<format>.<ext>
<source-basename>_<variation>_<format>.<ext>   # variations mode
<source-basename>_favicon.ico
```

Example: `acme-logo.png` rendered for the `website` canvas produces `acme-logo_website.png`.

::: warning Public asset storage
Files in `static/uploads/` are served without authentication. On public infrastructure, enforce authentication at the reverse proxy layer (see [Deployment](/guide/deployment) and [Privacy](/privacy)).
:::

## 9. Navigation and reset

Press <kbd>Esc</kbd> to dismiss dialogs, clear search filters, abort running jobs, or reset the staging area. Refer to [Keyboard shortcuts](/guide/keyboard-shortcuts).
