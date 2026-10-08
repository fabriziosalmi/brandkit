---
title: Output formats
description: How to choose which formats and which file types to generate.
---

# Output formats

BrandKit ships 45 named canvas sizes grouped into ten categories. The full table with pixel dimensions is the [format catalogue](/reference/format-catalogue); this page focuses on format selection.

## Two independent choices

**Formats** are canvas sizes: `website` is 1200×630, `favicon` is 16×16. **Output types** are file encodings: PNG, JPG, WebP, ICO. Every selected format is rendered into every selected type, so five formats × two types produces ten files.

## Starter selections

Rather than selecting items arbitrarily, start from one of these presets.

### Shipping a website

```
website               1200×630   Open Graph / Twitter card
favicon               16×16      Multi-size .ico bundle
webapp                512×512    PWA manifest icon
hero_desktop          1280×720
hero_mobile           360×200
```
Output types: **PNG + ICO**. Add WebP when serving modern web formats.

### Social launch

```
social                1080×1080  Square post
instagram             1080×1350  Portrait post
twitter               1500×500   Header banner
linkedin              1200×627
facebook              1200×630
social_icon_large     48×48
```
Output types: **PNG** (or JPG for photographic sources where file size is critical).

### App icon set

```
webapp                512×512
square_1024           1024×1024
square_logo_small     60×60
square_logo_large     100×100
thumbnail_small       90×90
thumbnail_large       300×300
favicon               16×16
```
Output types: **PNG + ICO**. Start from a square source with transparency.

### Print and documents

```
print_a4              2480×3508  300 DPI
print_letter          2550×3300  300 DPI
poster                1080×1350
business_card         1050×600
document_header       1200×200
presentation_slide    1920×1080
```
Output types: **PNG**. These are the largest canvases in the catalogue; rendering takes longer.

## Choosing a file type

| Attribute | PNG | JPG | WebP | ICO |
| --- | --- | --- | --- | --- |
| Transparency | Yes | No | Yes | Yes |
| Lossy | No | Yes | Yes | No |
| Honors quality slider | No | Yes | Yes | No |
| Typical size, 1200×630 logo | Large | Small | Smallest | N/A |
| Browser support | Universal | Universal | Modern (since 2020) | Universal |

Recommendations:

- **Alpha channel preservation:** PNG or WebP. Selecting JPG flattens transparency onto a solid background.
- **Photographic sources at large sizes:** JPG or WebP at quality 85-95. PNG results in significantly larger files with minimal perceptible gain.
- **Favicons:** ICO. Note that `.ico` generation requires the `favicon` format to be selected.
- **Default choice:** PNG is lossless and standard across production toolchains.

## Aspect ratio considerations

BrandKit scales your source into each canvas; it does not perform automated subject cropping. A tall logo placed into `twitter` (3:1) will be centered with blank padding on both flanks.

If your target outputs span divergent aspect ratios (such as 3:1 banners and 9:16 mobile backgrounds in the same run), prepare dedicated source images for optimal composition.

## Adding custom formats

Formats are configuration data, not code. Add an entry to `formats` in `config.json`, assign it to a category, and restart:

```json
{
  "formats": {
    "signature": { "width": 600, "height": 150, "description": "Email signature banner" }
  },
  "format_categories": {
    "Business Documents": ["email_header", "document_header", "presentation_slide", "signature"]
  }
}
```

Details and operational notes, including how `config.json` merges over built-in defaults, are covered in [Configuration](/reference/configuration).
