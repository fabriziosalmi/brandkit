---
title: Format catalogue
description: Reference index of BrandKit output formats, dimensions, aspect ratios, and target specifications.
---

# Format catalogue

The standard BrandKit configuration defines **45 named canvas formats** across ten operational categories. Canvases can be customized or extended by editing [`config.json`](/reference/configuration).

Dimensions represent canvas boundaries. Source images scale proportionally within the boundaries without upscaling beyond original pixel dimensions.

## Format categories

### Social Media

| Format key | Size | Ratio | Description |
| --- | --- | --- | --- |
| `social` | 1080×1080 | 1:1 | Social media square |
| `twitter` | 1500×500 | 3:1 | Twitter header |
| `instagram` | 1080×1350 | 4:5 | Instagram post |
| `linkedin` | 1200×627 | 400:209 | LinkedIn post |
| `facebook` | 1200×630 | 40:21 | Facebook post |
| `social_icon_small` | 32×32 | 1:1 | Social media icon (small) |
| `social_icon_large` | 48×48 | 1:1 | Social media icon (large) |

### Website

| Format key | Size | Ratio | Description |
| --- | --- | --- | --- |
| `website` | 1200×630 | 40:21 | Standard website banner |
| `hero_mobile` | 360×200 | 9:5 | Hero image (mobile) |
| `hero_desktop` | 1280×720 | 16:9 | Hero image (desktop) |
| `website_banner_mobile` | 360×120 | 3:1 | Website banner (mobile) |
| `website_banner_desktop` | 1200×400 | 3:1 | Website banner (desktop) |
| `background_mobile` | 360×640 | 9:16 | Background image (mobile) |
| `background_desktop` | 2560×1400 | 64:35 | Background image (desktop) |
| `lightbox_mobile` | 360×640 | 9:16 | Lightbox image (mobile) |
| `lightbox_desktop` | 1600×500 | 16:5 | Lightbox image (desktop) |
| `blog_post_mobile` | 360×240 | 3:2 | Blog post image (mobile) |
| `blog_post_desktop` | 1200×800 | 3:2 | Blog post image (desktop) |

### Mobile

| Format key | Size | Ratio | Description |
| --- | --- | --- | --- |
| `mobile` | 1080×1920 | 9:16 | Mobile screen |
| `thumbnail_small` | 90×90 | 1:1 | Thumbnail image (small) |
| `thumbnail_large` | 300×300 | 1:1 | Thumbnail image (large) |

### Branding

| Format key | Size | Ratio | Description |
| --- | --- | --- | --- |
| `logo_transparent` | 512×512 | 1:1 | Transparent Logo (PNG only) |
| `square_1024` | 1024×1024 | 1:1 | Square (1024x1024): App icon, profile, general purpose |
| `favicon` | 16×16 | 1:1 | Favicon |
| `square_small` | 256×256 | 1:1 | Small Square Icon |
| `square_large` | 2048×2048 | 1:1 | Large Square Format |

### E-commerce

| Format key | Size | Ratio | Description |
| --- | --- | --- | --- |
| `product_square` | 800×800 | 1:1 | Product Image Square |
| `product_wide` | 1200×800 | 3:2 | Product Image Wide |
| `square_1024` | 1024×1024 | 1:1 | Square (1024x1024): App icon, profile, general purpose |

### Print

| Format key | Size | Ratio | Description |
| --- | --- | --- | --- |
| `print_a4` | 2480×3508 | 620:877 | A4 Print Ready (300 DPI) |
| `print_letter` | 2550×3300 | 17:22 | Letter Print Ready (300 DPI) |
| `poster` | 1080×1350 | 4:5 | Poster Format |
| `business_card` | 1050×600 | 7:4 | Business Card |

### Web Application

| Format key | Size | Ratio | Description |
| --- | --- | --- | --- |
| `webapp` | 512×512 | 1:1 | Web app icon |
| `favicon` | 16×16 | 1:1 | Favicon |
| `square_logo_small` | 60×60 | 1:1 | Square logo (small) |
| `square_logo_large` | 100×100 | 1:1 | Square logo (large) |
| `rectangle_logo_small` | 160×40 | 4:1 | Rectangle logo (small) |
| `rectangle_logo_large` | 400×100 | 4:1 | Rectangle logo (large) |

### General Purpose

| Format key | Size | Ratio | Description |
| --- | --- | --- | --- |
| `square_1024` | 1024×1024 | 1:1 | Square (1024x1024): App icon, profile, general purpose |

### Business Documents

| Format key | Size | Ratio | Description |
| --- | --- | --- | --- |
| `email_header` | 600×200 | 3:1 | Email header image |
| `document_header` | 1200×200 | 6:1 | Document header image |
| `presentation_slide` | 1920×1080 | 16:9 | Presentation slide (16:9) |

### Publishing

| Format key | Size | Ratio | Description |
| --- | --- | --- | --- |
| `ebook_cover` | 1600×2560 | 5:8 | Ebook cover (portrait) |

### Uncategorized formats

Available across format matrices and indexed by search queries:

| Format key | Size | Ratio | Description |
| --- | --- | --- | --- |
| `instagram_story` | 1080×1920 | 9:16 | Instagram Story |
| `youtube_thumbnail` | 1280×720 | 16:9 | YouTube Thumbnail |
| `profile_picture` | 400×400 | 1:1 | Profile Picture |
| `cover_photo` | 1920×1080 | 16:9 | Cover Photo |

## Alphabetical index

| Format key | Size | Ratio |
| --- | --- | --- |
| `background_desktop` | 2560×1400 | 64:35 |
| `background_mobile` | 360×640 | 9:16 |
| `blog_post_desktop` | 1200×800 | 3:2 |
| `blog_post_mobile` | 360×240 | 3:2 |
| `business_card` | 1050×600 | 7:4 |
| `cover_photo` | 1920×1080 | 16:9 |
| `document_header` | 1200×200 | 6:1 |
| `ebook_cover` | 1600×2560 | 5:8 |
| `email_header` | 600×200 | 3:1 |
| `facebook` | 1200×630 | 40:21 |
| `favicon` | 16×16 | 1:1 |
| `hero_desktop` | 1280×720 | 16:9 |
| `hero_mobile` | 360×200 | 9:5 |
| `instagram` | 1080×1350 | 4:5 |
| `instagram_story` | 1080×1920 | 9:16 |
| `lightbox_desktop` | 1600×500 | 16:5 |
| `lightbox_mobile` | 360×640 | 9:16 |
| `linkedin` | 1200×627 | 400:209 |
| `logo_transparent` | 512×512 | 1:1 |
| `mobile` | 1080×1920 | 9:16 |
| `poster` | 1080×1350 | 4:5 |
| `presentation_slide` | 1920×1080 | 16:9 |
| `print_a4` | 2480×3508 | 620:877 |
| `print_letter` | 2550×3300 | 17:22 |
| `product_square` | 800×800 | 1:1 |
| `product_wide` | 1200×800 | 3:2 |
| `profile_picture` | 400×400 | 1:1 |
| `rectangle_logo_large` | 400×100 | 4:1 |
| `rectangle_logo_small` | 160×40 | 4:1 |
| `social` | 1080×1080 | 1:1 |
| `social_icon_large` | 48×48 | 1:1 |
| `social_icon_small` | 32×32 | 1:1 |
| `square_1024` | 1024×1024 | 1:1 |
| `square_large` | 2048×2048 | 1:1 |
| `square_logo_large` | 100×100 | 1:1 |
| `square_logo_small` | 60×60 | 1:1 |
| `square_small` | 256×256 | 1:1 |
| `thumbnail_large` | 300×300 | 1:1 |
| `thumbnail_small` | 90×90 | 1:1 |
| `twitter` | 1500×500 | 3:1 |
| `webapp` | 512×512 | 1:1 |
| `website` | 1200×630 | 40:21 |
| `website_banner_desktop` | 1200×400 | 3:1 |
| `website_banner_mobile` | 360×120 | 3:1 |
| `youtube_thumbnail` | 1280×720 | 16:9 |

## Output encoding options

| Format | Alpha channel | Characteristics |
| --- | --- | --- |
| `png` | Yes | Lossless compression, universal standard |
| `jpg` | No | Quantized lossy encoding; discards alpha |
| `webp` | Yes | Compact modern encoding; retains alpha |
| `ico` | Yes | Generated for `favicon` canvas; packages 16×16, 32×32, and 48×48 icons |

## Naming conventions

```
<source-basename>_<format-key>.<ext>
<source-basename>_favicon.ico
```

Under variations mode, the treatment identifier is injected: `<source-basename>_<variation>_<format>.<ext>`.

Target pixel dimensions are mapped directly from format keys rather than encoded in the filename.
