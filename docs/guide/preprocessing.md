---
title: Image preprocessing
description: Every preprocessing control in BrandKit, what it does to the image, and its default.
---

# Image preprocessing

Preprocessing runs **once on the source image**, before any format is rendered. That is what keeps a watermark or a hue shift consistent across the whole kit — and it is also why a setting that looks fine on a 1080×1080 square can look wrong on a 2480×3508 print sheet.

The order of operations is fixed:

1. Background removal
2. Background colour / gradient fill
3. Edge smoothing
4. Noise reduction
5. Auto-crop
6. Colour operations — grayscale, B&W, invert, hue, temperature, saturation, brightness, contrast
7. Sharpen or blur
8. Vignette
9. Drop shadow
10. Watermark

## Colour

| Control | Form field | Default | What it does |
| --- | --- | --- | --- |
| Grayscale | `grayscale` | `false` | Converts to luminance, keeping the alpha channel |
| Black & white | `bw` | `false` | Hard threshold to pure black and white — no midtones |
| Invert | `invert` | `false` | Inverts RGB, leaves alpha alone |
| Hue shift | `hue_shift` | `0` | Rotates hue in degrees, −180 to +180 |
| Temperature | `temperature` | `0` | Warm (positive, boosts red) to cool (negative, boosts blue), −100 to +100 |
| Saturation | `saturation` | `1.0` | `0.0` is fully desaturated, `1.0` is unchanged, `>1.0` boosts |
| Brightness | `brightness` | `1.0` | Same scale as saturation |
| Enhance contrast | `enhance_contrast` | `false` | Applies an autocontrast pass |

::: tip Grayscale vs B&W
`grayscale` is what you want for a monochrome logo variant. `bw` is a hard threshold — useful for testing whether a mark survives being reduced to a stencil, rarely useful as a deliverable.
:::

## Sharpness and blur

| Control | Form field | Default | Notes |
| --- | --- | --- | --- |
| Sharpen | `sharpen` | `false` | Unsharp mask |
| Sharpen radius | `sharpen_radius` | `1.0` | Larger radius, coarser halo |
| Blur | `apply_blur` | `false` | Gaussian blur |
| Blur radius | `blur_radius` | `2` | In pixels, at source resolution |
| Noise reduction | `noise_reduction` | `false` | Median filter; needs OpenCV for the stronger path |
| Noise strength | `noise_strength` | `1` | Integer; higher is more aggressive and softer |
| Enhance quality | `enhance_quality` | `false` | Combined contrast + sharpness + colour pass |

Sharpen and blur are mutually antagonistic — turning both on will apply both, in that order, and you will get a soft image with ringing. Pick one.

## Composition

| Control | Form field | Default | Notes |
| --- | --- | --- | --- |
| Auto-crop | `auto_crop` | `false` | Trims uniform borders down to the content bounding box |
| Crop padding | `crop_padding` | `10` | Pixels of margin left around the content after trimming |
| Vignette | `vignette` | `false` | Darkens the edges radially |
| Vignette strength | `vignette_strength` | `0.5` | `0.0`–`1.0` |

**Auto-crop is the single most useful control here.** If your logo has a lot of empty canvas around it, every format will render it small and lost. Auto-crop with 10–20 px of padding fixes that once, for all formats.

## Drop shadow

| Control | Form field | Default |
| --- | --- | --- |
| Enable | `shadow_effect` | `false` |
| Opacity | `shadow_opacity` | `0.3` |
| Blur radius | `shadow_blur` | `4` |
| Offset X | `shadow_offset_x` | `5` |
| Offset Y | `shadow_offset_y` | `5` |

The shadow is drawn from the alpha channel, so it only produces something meaningful on an image that actually has transparency — either a source PNG with an alpha channel or the output of [background removal](/guide/background-removal).

## Watermark

| Control | Form field | Default |
| --- | --- | --- |
| Enable | `add_watermark` | `false` |
| Text | `watermark_text` | `© BrandKit` |
| Opacity | `watermark_opacity` | `0.3` |

The watermark is rendered with Pillow's default bitmap font unless a TrueType face is available on the host, so it will look coarse on very large canvases. Set your own default text in [`config.json`](/reference/configuration).

## Output encoding

These two are not preprocessing — they apply at encode time, per generated file.

| Control | Form field | Default | Notes |
| --- | --- | --- | --- |
| Quality | `quality` | `95` | JPEG and WebP only; PNG and ICO ignore it |
| Strip metadata | `strip_metadata` | `false` | Drops the ICC profile and remaining metadata from generated files |

::: info EXIF is always stripped from the upload
Regardless of the `strip_metadata` switch, the *uploaded original* is re-encoded through Pillow immediately on receipt, which discards EXIF — including GPS coordinates and camera serial numbers. `strip_metadata` controls the *generated* files only. See [Privacy](/privacy).
:::

## Changing the defaults

Every default above lives in `preprocessing_options` in [`config.json`](/reference/configuration#preprocessing-defaults). Edit it there and the UI starts with your values.
