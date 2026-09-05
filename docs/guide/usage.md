---
title: The generation workflow
description: What every control in the BrandKit interface does, in the order you meet it.
---

# The generation workflow

The whole app is one page. This is what each part of it does, top to bottom.

## 1. Upload a source image

Drag an image onto the drop zone, or click it and pick a file. With the drop zone focused, <kbd>Space</kbd> opens the file selector.

**Accepted:** `png`, `jpg`, `jpeg`, `gif`, `webp`.
**Size limit:** 16 MB by default — change it with [`BRANDKIT_MAX_UPLOAD_MB`](/reference/environment).

### Pick the right source

Everything downstream is a resize of what you upload, and BrandKit does not upscale intelligently. Give it the largest, cleanest version you have:

- **A square or near-square PNG with transparency** is the ideal input. It composites cleanly onto any background and crops well into both landscape and portrait canvases.
- **At least 1024 px on the short edge** if you want the large formats (`square_large` at 2048×2048, `print_a4` at 2480×3508) to look sharp.
- **Avoid pre-flattened JPEGs with a white box around the logo** — or turn on background removal to get rid of it.

As soon as the file is accepted, two things happen automatically: **EXIF metadata is stripped** (unconditionally, by re-encoding through Pillow) and the image is **analysed** for its prominent colour and for the presence of a large white region.

## 2. Choose formats

Formats are grouped into categories — Social Media, Website, Mobile, Branding, Web Application, E-commerce, Print, Business Documents, Publishing, General Purpose. Expand a category and tick what you need, or type in the search box to filter the whole catalogue by name.

Nothing ticked? BrandKit falls back to **every format in the catalogue**, which is 45 renders per output type. That is rarely what you want and it is slow. Tick deliberately.

The complete list of names and pixel dimensions is in the [format catalogue](/reference/format-catalogue).

## 3. Choose output types

| Type | Transparency | Good for |
| --- | --- | --- |
| **PNG** | yes | logos, icons, anything that will sit on an unknown background |
| **JPG** | no | photographic sources, large banners where file size matters |
| **WebP** | yes | modern web delivery — smaller than PNG at equal quality |
| **ICO** | yes | browser favicons only |

You can select several at once; each selected format is rendered into each selected type.

::: info ICO is coupled to the favicon format
If you tick `ico` as an output type but do not tick the `favicon` format, BrandKit silently drops `ico` from the list. If that leaves no output types at all, it falls back to `png`. The ICO file itself is multi-resolution: 16×16, 32×32 and 48×48 are packed into one `.ico`.
:::

## 4. Preprocessing (optional)

Everything in this panel is applied **once, to the source image**, before any format is rendered — so a hue shift or a watermark appears identically across the whole kit.

The controls are documented in detail in [Image preprocessing](/guide/preprocessing) and [Background removal](/guide/background-removal). The two settings that most often surprise people:

- **Quality** (default `95`) applies to JPEG and WebP encoding. PNG ignores it.
- **Strip metadata** (default off) removes the ICC profile and any remaining metadata from the *generated* files. Note that EXIF on the *uploaded* file is always stripped regardless of this switch.

## 5. Smart background fill

If the analysis in step 1 found a significant white area (more than 15% of the image is near-white), BrandKit offers to replace that white with the image's prominent colour, or with a radial gradient built from it.

This is what turns a logo-on-white into a logo-on-brand-colour without you picking a hex value. It is a heuristic: check the previews.

## 6. Variations mode

Turning on **variations mode** renders each selected format ten times, once per preset:

| Preset | Effect |
| --- | --- |
| `Original` | no change |
| `Grayscale` | desaturated |
| `B&W` | 1-bit black and white |
| `Inverted` | colour-inverted |
| `Hue_+60` / `Hue_-60` | hue rotated ±60° |
| `Warm` / `Cool` | colour temperature ±40 |
| `Grayscale_Contrast` | desaturated with contrast boost |
| `Inverted_Blur` | inverted with a 2 px blur |

::: danger This multiplies your render count by ten
Ten formats × two output types × variations mode = **200 images**. On a small machine that will take minutes and a lot of RAM. Use it to explore a direction on two or three formats, not to generate a deliverable.
:::

## 7. Generate

Click **Generate**, or press <kbd>Ctrl</kbd>+<kbd>Enter</kbd> (<kbd>⌘</kbd>+<kbd>Enter</kbd> on macOS). The button is only active when you have a file, at least one format and at least one output type, and nothing is already running.

Uploads are rate-limited to **5 per minute** per IP address, on top of a global default of 200/day and 50/hour. If you hit the limit you get a `429`; wait and retry.

## 8. Review and download

The result grid shows a thumbnail per generated asset with its name and dimensions. Click any thumbnail to open the full-size file, or take the whole set as a ZIP.

Files are named predictably:

```
<source-basename>_<format>_<width>x<height>.<ext>
<source-basename>_favicon.ico
```

so `acme-logo.png` uploaded and rendered for `website` gives you `acme-logo_website_1200x630.png`.

::: warning Generated files are publicly readable
Assets are served out of `/static/uploads/`, which Flask exposes without authentication. Anyone who knows or guesses a filename can fetch it. On a public deployment, put an authenticating proxy in front of the whole app — see [Deployment](/guide/deployment) and [Privacy](/privacy).
:::

## 9. Start over

<kbd>Esc</kbd> resets the form, cancels an in-flight operation, closes the help dialog or clears the format search, depending on what is on screen. Full list in [Keyboard shortcuts](/guide/keyboard-shortcuts).
