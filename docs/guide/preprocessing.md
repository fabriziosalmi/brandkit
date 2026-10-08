---
title: Image preprocessing
description: Preprocessing controls, operational pipeline, and default parameters in BrandKit.
---

# Image preprocessing

Preprocessing executes once on the master source image prior to rendering target formats. This ensures adjustments such as color grading, auto-cropping, and watermarks remain uniform across the entire brand asset collection.

The sequence of processing operations:

1. Background removal
2. Background color / gradient fill
3. Edge smoothing
4. Noise reduction
5. Auto-crop
6. Color adjustments: grayscale, B&W, invert, hue, temperature, saturation, brightness, contrast
7. Sharpen or blur
8. Vignette
9. Drop shadow
10. Watermark

## Color adjustments

| Control | Form field | Default | Description |
| --- | --- | --- | --- |
| Grayscale | `grayscale` | `false` | Converts RGB channels to luminance while preserving alpha transparency |
| Black & white | `bw` | `false` | High-contrast binarization to pure black and pure white |
| Invert | `invert` | `false` | Inverts RGB values while retaining alpha values |
| Hue shift | `hue_shift` | `0` | Rotates color hue in degrees (-180° to +180°) |
| Temperature | `temperature` | `0` | Warm (positive, red-shifted) to cool (negative, blue-shifted), -100 to +100 |
| Saturation | `saturation` | `1.0` | `0.0` is fully desaturated, `1.0` is neutral, `>1.0` enhances vibrance |
| Brightness | `brightness` | `1.0` | Multiplier scale matching saturation |
| Enhance contrast | `enhance_contrast` | `false` | Applies automated histogram contrast equalization |

::: tip Grayscale vs B&W
`grayscale` preserves smooth midtone tonal gradients and is recommended for monochrome brand variations. `bw` applies binary thresholding, best suited for testing stencil legibility.
:::

## Sharpness and filtering

| Control | Form field | Default | Notes |
| --- | --- | --- | --- |
| Sharpen | `sharpen` | `false` | Applies unsharp masking |
| Sharpen radius | `sharpen_radius` | `1.0` | Controls filter radius (higher values produce broader halos) |
| Blur | `apply_blur` | `false` | Applies Gaussian blur |
| Blur radius | `blur_radius` | `2` | Radius in pixels at source resolution |
| Noise reduction | `noise_reduction` | `false` | Median filter; utilizes OpenCV when present |
| Noise strength | `noise_strength` | `1` | Kernel size: higher values increase smoothing |
| Enhance quality | `enhance_quality` | `false` | Combined contrast, sharpening, and color correction pass |

Sharpening and blurring are counteracting operations. Enabling both applies them sequentially, introducing blurring with halo artifacts. Select the single filter appropriate for your source.

## Composition & framing

| Control | Form field | Default | Notes |
| --- | --- | --- | --- |
| Auto-crop | `auto_crop` | `false` | Trims empty or uniform borders down to active subject bounds |
| Crop padding | `crop_padding` | `10` | Margin in pixels retained around the subject after boundary trimming |
| Vignette | `vignette` | `false` | Applies radial perimeter darkening |
| Vignette strength | `vignette_strength` | `0.5` | Intensity scale: `0.0` to `1.0` |

Auto-crop is particularly effective for logos exported with wide transparent margins. Combining auto-crop with 10-20 px padding ensures the mark fills all output canvases proportionally.

## Drop shadow

| Control | Form field | Default |
| --- | --- | --- |
| Enable | `shadow_effect` | `false` |
| Opacity | `shadow_opacity` | `0.3` |
| Blur radius | `shadow_blur` | `4` |
| Offset X | `shadow_offset_x` | `5` |
| Offset Y | `shadow_offset_y` | `5` |

Drop shadows are calculated from the alpha boundary. This requires an image with an active alpha channel, originating either from a transparent PNG/WebP source or via [background removal](/guide/background-removal).

## Watermark overlay

| Control | Form field | Default |
| --- | --- | --- |
| Enable | `add_watermark` | `false` |
| Text | `watermark_text` | `© BrandKit` |
| Opacity | `watermark_opacity` | `0.3` |

Watermarks render using Pillow bitmap rendering unless custom system TrueType fonts are mounted. Configure default text in [`config.json`](/reference/configuration).

## Output encoding options

These settings operate during per-canvas encoding rather than global preprocessing:

| Control | Form field | Default | Notes |
| --- | --- | --- | --- |
| Quality | `quality` | `95` | Applies to JPEG and WebP; ignored by PNG and ICO |
| Strip metadata | `strip_metadata` | `false` | Discards ICC color profiles and leftover metadata from output files |

::: info Source EXIF handling
Uploaded master images are re-encoded through Pillow upon ingestion, which strips camera and GPS EXIF metadata. The `strip_metadata` parameter controls downstream target asset headers. Consult [Privacy](/privacy).
:::

## Customizing defaults

Default parameter values are declared under `preprocessing_options` in [`config.json`](/reference/configuration#preprocessing-defaults). Modifying this structure alters the initial UI state.
