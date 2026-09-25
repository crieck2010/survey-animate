# Architecture

survey-animate is an **engine-first** package: pure logic in
`src/animate/`, a thin CLI in `src/animate/cli.py`, no UI-framework
imports anywhere.

## Module layout

```
src/animate/
  __init__.py    version + lazy public API (read_manifest, render_video, ...)
  manifest.py    input contract: survey-flow manifest validation, PNG-dir fallback
  _png.py        minimal pure-Python PNG codec (8-bit RGB/RGBA, non-interlaced)
  presets.py     output presets + aspect-fit geometry (bilinear rescale + pad)
  encode.py      ffmpeg backend resolution + mp4/gif/webm encoders
  overlays.py    burned-in timestamps + title cards (matplotlib, lazy)
  provenance.py  <video>.provenance.json sidecars (SHA-256)
  pipeline.py    render_video(): the orchestrated end-to-end path
  cli.py         argparse thin wrapper (render/demo/presets/manifest-info/check)
```

## Design decisions

**Core is stdlib+numpy.** Manifest parsing, presets, geometry, and the
PNG codec need nothing beyond numpy. This keeps the engine importable
and testable in bare environments (69 tests run fully offline).

**ffmpeg, not a Python video library.** Encoding shells out to an ffmpeg
binary resolved at runtime:

1. `imageio-ffmpeg` wheel's bundled static binary (preferred — zero
   system setup on user machines),
2. system `ffmpeg` on `PATH` (fallback),
3. `EncoderUnavailable` with install guidance (never a silent failure).

Frames stream to ffmpeg's stdin as raw RGB24 — no intermediate files,
one process per encode. The GIF path does two ffmpeg passes
(palettegen → paletteuse) for quality.

**imageio is optional, not required.** `_png.py` decodes the PNGs the
pipeline needs. If `imageio` happens to be installed it is tried first
(broader format tolerance); otherwise the built-in codec handles
everything survey-flow writes (8-bit RGB/RGBA, all filter types,
grayscale expanded to RGB).

**Text overlays are the only matplotlib dependency — and lazy.**
`burn_timestamps` renders each distinct label once into an RGBA strip
and alpha-composites with numpy, so per-frame cost is trivial. Without
matplotlib the pipeline degrades gracefully: timestamps/title are
skipped and recorded in the provenance sidecar's `params`
(`timestamps_skipped` / `title_skipped`), never a crash mid-render.

**survey-flow already burns its colorbar legend in.** This package
deliberately does not draw another one — `overlays.py` handles
timestamps and title cards only.

**Manifest validation is strict where it matters.** Schema id must be
`survey-flow.frame-manifest/1.0`; unknown major versions are rejected;
frame indices must be sequential `0..n-1`; `n_frames` must match; every
referenced PNG must exist (missing files are listed, first five shown).
Relative PNG paths resolve against the manifest's directory so output
trees stay portable.

**Every output is reproducible on paper.** The `.provenance.json`
sidecar records the source manifest path + SHA-256, preset, format,
fps, frame count, encode params, encoder binary path, and the output's
SHA-256 (`survey-animate.provenance/1.0`).

## Data flow

```
manifest.json / PNG dir
  → manifest.py      ordered ManifestFrames (validated)
  → _png.py          (H, W, 3) uint8 per frame
  → presets.py       aspect-fit into preset canvas (e.g. 1080x1920)
  → overlays.py      title cards prepended; timestamps burned in
  → encode.py        rawvideo pipe → ffmpeg → MP4/GIF/WebM
  → provenance.py    <video>.provenance.json
```

## Scaling notes

- Frames stream one at a time through the pipeline; memory is O(one
  frame), not O(video). Long reels do not blow up RAM.
- `render_video(..., progress=callable)` reports per-frame progress for
  UIs and logs.
- The `preview` preset (540×960 @ 15 fps) exists for fast iteration
  before committing to full-resolution encodes.
- No frame-range parallelism in v0.1.0 — the ffmpeg pipe is inherently
  sequential; chunked parallel encoding is a possible v0.2.0.
