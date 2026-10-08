---
title: Background removal
description: How BrandKit uses rembg to cut out a subject, and what to do with the result.
---

# Background removal

BrandKit removes backgrounds with [rembg](https://github.com/danielgatis/rembg) running an ONNX U²-Net model **locally**, through `onnxruntime`. Nothing is sent to an external service.

## Turning it on

Tick **Remove background** in the preprocessing panel. It is off by default, and the control is hidden entirely if `rembg` failed to import at startup. Check the logs for:

```
Background removal (rembg) not available. Install with: pip install rembg
```

## Choosing a model

The **method** selector maps to a different ONNX model:

| Method | Model | Use it for |
| --- | --- | --- |
| `auto` *(default)* | `u2net` | General-purpose: logos, products, standard objects |
| `object` | `u2net` | Explicit object segmentation |
| `person` | `u2net_human_seg` | Photographs of people; optimized for hair and contours |
| `anime` | `u2net_anime` | Illustrated and cel-shaded artwork |

There is no dynamic heuristic behind `auto`; it routes to the general model. If your subject is a person, pick `person` explicitly for optimal boundary preservation.

::: warning The first run downloads ~180 MB
On first use of each model, rembg fetches the `.onnx` file into `~/.u2net/`. That request needs outbound internet access and causes the initial generation to take longer. Subsequent runs are fast. In Docker, mount `$HOME/.u2net:/root/.u2net` so the download survives image rebuilds. See [Running with Docker](/guide/docker#running-without-compose).
:::

## What you get

The output is always **RGBA with a real alpha channel**. What happens next depends on the background colour setting:

| `background_color` | Result |
| --- | --- |
| `transparent` *(default when removal is on)* | Alpha is preserved: PNG and WebP retain transparency, JPG flattens to white |
| A hex value like `#0f172a` | The cutout is composited onto that solid colour |
| Detected prominent colour | The [smart fill](/guide/usage#_5-smart-background-fill) path, driven by image telemetry |

Hex parsing accepts `#abc`, `#aabbcc`, and notations without a leading `#`. Values that fail validation fall back to white rather than terminating the request.

::: tip JPG and transparency do not mix
If you select `jpg` as an output type with a transparent result, the alpha channel is flattened. Select PNG or WebP to retain background transparency.
:::

## Cleaning up the edges

Model output can benefit from edge refinement. Three controls help:

- **Edge smoothing** (`edge_smooth`, radius default `2`): feathers the alpha channel to prevent staircasing against contrasting backgrounds.
- **Auto-crop** (`auto_crop`): trims empty transparent margins after removal so the subject fills target canvases proportionally.
- **Drop shadow** (`shadow_effect`): renders an offset shadow against the synthesized alpha boundaries.

Recommended recipe for a logo on a solid background:

```
remove_background = true
background_removal_method = auto
background_color = transparent
edge_smooth = true, smooth_radius = 2
auto_crop = true, crop_padding = 16
output_formats = png, webp
```

## Troubleshooting

| Symptom | Cause | Resolution |
| --- | --- | --- |
| Nothing happens, background persists | `rembg` not importable | Check startup logs; run `pip install rembg onnxruntime` |
| First request hangs, then succeeds | Model download in progress | Expected behavior on initial run; pre-seed `~/.u2net/` |
| Foreground elements cut out | U²-Net classified flat brand color as background | Use `object` method, or disable removal and use matte threshold |
| White perimeter halo around subject | Source JPEG artifacts along subject boundaries | Enable edge smoothing or ingest a lossless PNG source |
| Process killed mid-generation | ONNX Runtime memory limit exceeded | Downscale source or increase container memory allocations (see [Performance](/guide/performance)) |

## Running without it

`rembg` and `onnxruntime` are the primary heavy dependencies in the project. Together they account for most of the Docker image footprint. If background removal is not required, omit them from `requirements.txt`. The application detects dependency availability at launch and disables removal controls without impacting other processing capabilities.
