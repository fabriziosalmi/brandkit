---
title: Output formats
description: How to choose which formats and which file types to generate.
---

# Output formats

BrandKit ships 45 named canvas sizes grouped into ten categories. The full table with pixel dimensions is the [format catalogue](/reference/format-catalogue) — this page is about choosing.

## Two independent choices

**Formats** are canvas sizes: `website` is 1200×630, `favicon` is 16×16. **Output types** are file encodings: PNG, JPG, WebP, ICO. Every selected format is rendered into every selected type, so five formats × two types is ten files.

## Starter selections

Rather than ticking boxes at random, start from one of these.

### Shipping a website

```
website               1200×630   Open Graph / Twitter card
favicon               16×16      → produces a multi-size .ico
webapp                512×512    PWA manifest icon
hero_desktop          1280×720
hero_mobile           360×200
```
Output types: **PNG + ICO**. Add WebP if you serve modern formats.

### Social launch

```
social                1080×1080  square post
instagram             1080×1350  portrait post
twitter               1500×500   header banner
linkedin              1200×627
facebook              1200×630
social_icon_large     48×48
```
Output types: **PNG** (JPG if the source is photographic and you care about bytes).

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
Output types: **PNG**. These are the largest canvases in the catalogue — expect the slowest renders.

## Choosing a file type

| | PNG | JPG | WebP | ICO |
| --- | --- | --- | --- | --- |
| Transparency | ✅ | ❌ | ✅ | ✅ |
| Lossy | no | yes | yes | no |
| Honours the quality slider | ❌ | ✅ | ✅ | ❌ |
| Typical size, 1200×630 logo | large | small | smallest | — |
| Universal browser support | ✅ | ✅ | ✅ (since 2020) | ✅ |

Rules of thumb:

- **Anything with an alpha channel → PNG or WebP.** Selecting JPG flattens it, usually onto white.
- **Photographic sources at large sizes → JPG or WebP** at quality 85–95. PNG will be several times larger for no visible gain.
- **Favicons → ICO**, and remember it is only generated if the `favicon` format is also ticked.
- **When in doubt → PNG.** It is lossless and it is what the rest of the toolchain expects.

## Aspect ratio is the thing that bites

BrandKit fits your source into each canvas; it does not crop intelligently to a subject. A tall logo dropped into `twitter` (3:1) will end up small and centred with a lot of empty space on either side.

If your kit spans wildly different ratios — 3:1 banners and 9:16 mobile backgrounds in the same run — expect to want two source images rather than one. That is a limitation of any automated resize, not of this tool specifically.

## Adding your own

Formats are data, not code. Add a key to `formats` in `config.json`, list it under a category, restart:

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

Details and gotchas — including the fact that `config.json` **merges over** the built-in defaults rather than replacing them — are in [Configuration](/reference/configuration).
