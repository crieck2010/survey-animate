# Presets

Presets bundle delivered-video geometry, default frame rate, and quality.
Get one with `animate.presets.get_preset(name)` or list them with
`survey-animate presets`.

| Name      | Canvas (W×H) | Aspect | fps | CRF | Pixel fmt | Intended use              |
|-----------|--------------|--------|-----|-----|-----------|---------------------------|
| `reel`    | 1080 × 1920  | 9:16   | 30  | 18  | yuv420p   | Instagram / TikTok / Shorts |
| `wide`    | 1920 × 1080  | 16:9   | 30  | 18  | yuv420p   | YouTube, presentations    |
| `square`  | 1080 × 1080  | 1:1    | 30  | 18  | yuv420p   | Feed posts                |
| `preview` | 540 × 960    | 9:16   | 15  | 23  | yuv420p   | Fast iteration drafts     |

CRF is the H.264/VP9 quality factor (lower = better; 18 is visually
near-lossless, 23 is a good draft). Any preset value can be overridden
per render (`fps=`, `crf=`).

## Geometry rules

1. **Aspect-fit, never stretch.** Each input frame is bilinearly
   rescaled to the largest size that fits inside the canvas, then
   centered on a solid pad color (default black). A 16:9 frame in the
   `reel` preset gets letterbox bars; a 9:16 frame in `wide` gets
   pillarbox bars. Nothing is cropped silently.
2. **Even dimensions.** H.264 with `yuv420p` requires even width/height;
   odd inputs are rounded up (`even_dims`).
3. **Manifest `size_px` is advisory.** The manifest records what
   survey-flow rendered, but the preset always wins — the same manifest
   encodes cleanly to `reel`, `wide`, or `square`.

## Formats

| Format | Container | Video codec | Notes                              |
|--------|-----------|-------------|------------------------------------|
| `mp4`  | MP4       | H.264 (`libx264`, else `mpeg4`) | `+faststart` for web playback |
| `gif`  | GIF       | —           | two-pass global palette; best at low fps |
| `webm` | WebM      | VP9         | open-codec alternative to MP4      |

Format is inferred from the output suffix (`.mp4` / `.gif` / `.webm`)
or set explicitly with `--format`.
