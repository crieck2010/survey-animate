# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-25

### Added
- Frame-sequence → video engine: ordered PNGs in, MP4 (H.264) / GIF
  (two-pass palette) / WebM (VP9) out, via a runtime-resolved ffmpeg
  binary (`imageio-ffmpeg` bundled static binary preferred, system
  `ffmpeg` fallback, `EncoderUnavailable` with install guidance
  otherwise). Frames stream as raw RGB24 — O(one frame) memory.
- `manifest.py`: survey-flow frame-manifest reader
  (`survey-flow.frame-manifest/1.0`) with strict validation — schema id
  check, unknown-major-version rejection, sequential-index enforcement,
  `n_frames` match, missing-PNG reporting; relative paths resolve
  against the manifest directory. `frames_from_dir()` accepts any plain
  PNG directory (alphabetical order, optional timestamps).
- `_png.py`: dependency-free PNG codec (8-bit RGB/RGBA read incl. all
  filter types 0–4, grayscale expansion; RGB/RGBA write) so the core
  stays stdlib+numpy.
- `presets.py`: `reel` (1080×1920), `wide` (1920×1080), `square`
  (1080×1080), `preview` (540×960 draft) presets with fps/CRF/pixel
  format; aspect-fit geometry (bilinear rescale + padding, never
  stretched/cropped); even-dimension enforcement for yuv420p.
- `overlays.py` (matplotlib, lazy): burned-in per-frame timestamps
  (`16 Sep 2026 00:00 UTC`, four positions) via render-once/composite
  strips; `make_title_card()` title/subtitle frames. Graceful
  degradation without matplotlib (skipped + recorded in provenance).
- `provenance.py`: `<video>.provenance.json` sidecars
  (`survey-animate.provenance/1.0`) — source manifest path + SHA-256,
  preset, params, encoder binary, output SHA-256.
- `pipeline.py`: `render_video()` end-to-end orchestration with
  progress callbacks, returning `VideoResult`.
- `cli.py`: `render` / `demo` / `presets` / `manifest-info` / `check`
  commands; `demo` renders a fully offline synthetic clip.
- Docs: README, ARCHITECTURE, PRESETS, INTEROP; MIT license.
