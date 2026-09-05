---
title: Background removal
description: How BrandKit uses rembg to cut out a subject, and what to do with the result.
---

# Background removal

BrandKit removes backgrounds with [rembg](https://github.com/danielgatis/rembg) running an ONNX U²-Net model **locally**, through `onnxruntime`. Nothing is sent to an external service.

## Turning it on

Tick **Remove background** in the preprocessing panel. It is off by default, and the control is hidden entirely if `rembg` failed to import at startup — check the logs for:

```
Background removal (rembg) not available. Install with: pip install rembg
```

## Choosing a model

The **method** selector maps to a different ONNX model:

| Method | Model | Use it for |
| --- | --- | --- |
| `auto` *(default)* | `u2net` | general-purpose — logos, products, most things |
| `object` | `u2net` | same as auto, named explicitly |
| `person` | `u2net_human_seg` | photographs of people; much better at hair and limbs |
| `anime` | `u2net_anime` | illustrated and cel-shaded artwork |

There is no automatic detection behind `auto` — it simply uses the general model. If your subject is a person, pick `person` explicitly; the difference is large.

::: warning The first run downloads ~180 MB
On first use of each model, rembg fetches the `.onnx` file into `~/.u2net/`. That request needs outbound internet access and will make the first generation take a minute or more. Subsequent runs are fast. In Docker, mount `$HOME/.u2net:/root/.u2net` so the download survives image rebuilds — see [Running with Docker](/guide/docker#running-without-compose).
:::

## What you get

The output is always **RGBA with a real alpha channel**. What happens next depends on the background colour setting:

| `background_color` | Result |
| --- | --- |
| `transparent` *(default when removal is on)* | alpha is preserved — PNG and WebP keep it, JPG flattens to white |
| a hex value like `#0f172a` | the cutout is composited onto that solid colour |
| the detected prominent colour | the [smart fill](/guide/usage#_5-smart-background-fill) path, driven by image analysis |

Hex parsing accepts `#abc`, `#aabbcc`, and the same without the leading `#`. Anything it cannot parse falls back to white rather than failing the request.

::: tip JPG and transparency do not mix
If you select `jpg` as an output type with a transparent result, the alpha is flattened. Select PNG or WebP if you need the cutout to stay cut out.
:::

## Cleaning up the edges

Model output is rarely pixel-perfect. Three controls help:

- **Edge smoothing** (`edge_smooth`, radius default `2`) — feathers the alpha channel so the cutout does not have a jagged staircase against a contrasting background.
- **Auto-crop** (`auto_crop`) — after removal the subject is usually surrounded by fully transparent pixels. Auto-crop trims to the bounding box, which makes the subject fill each format instead of floating in the middle.
- **Drop shadow** (`shadow_effect`) — only does anything useful once there *is* an alpha channel, so it pairs naturally with removal.

A good default recipe for a logo on a white JPEG:

```
remove_background = true
background_removal_method = auto
background_color = transparent
edge_smooth = true, smooth_radius = 2
auto_crop = true, crop_padding = 16
output_formats = png, webp
```

## When it goes wrong

| Symptom | Cause | Fix |
| --- | --- | --- |
| Nothing happens, background still there | `rembg` not importable | check startup logs; `pip install rembg onnxruntime` |
| First request hangs, then works | model download | expected; pre-seed `~/.u2net/` |
| Parts of the logo were eaten | U²-Net treated flat brand colour as background | try `object`, or skip removal and use the smart white-fill instead |
| Halo of white pixels around the subject | source was a JPEG with compression artefacts against white | enable edge smoothing; start from a PNG if you have one |
| Process killed mid-generation | ONNX Runtime memory spike on a large image | shrink the source, or raise the container memory limit — see [Performance](/guide/performance) |

## Running without it

`rembg` and `onnxruntime` are the two heaviest dependencies in the project — together they account for most of the ~2 GB Docker image. If you never need background removal, remove both lines from `requirements.txt` before installing. The app detects their absence at import time and degrades gracefully; every other feature is unaffected.
