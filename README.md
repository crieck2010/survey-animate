> [!IMPORTANT]
> **Consolidated into [EarthWatch-Suite](https://github.com/crieck2010/earthwatch-suite)**  
> This engine has been consolidated into the unified [EarthWatch-Suite monorepo](https://github.com/crieck2010/earthwatch-suite). Active development, bug fixes, releases, and unified testing now live in earthwatch-suite. This repository is preserved as an archive.

# survey-animate

Frame-sequence → video engine for the [earthwatch-suite](https://github.com/crieck2010/earthwatch-suite)
remote-sensing project. Takes ordered PNG frames — from a
[survey-flow](https://github.com/crieck2010/survey-flow) frame manifest, or
any directory of PNGs — and encodes finished videos: **MP4 (H.264)**,
**GIF** (two-pass palette), and **WebM (VP9)**.

This is module 3 of 4 in the flow-field animation program (the
mapped.earth-style animated current/temperature reel pipeline):

1. [survey-currents](https://github.com/crieck2010/survey-currents) — current + water-temperature model data
2. [survey-flow](https://github.com/crieck2010/survey-flow) — flow-field frame rendering
3. **survey-animate** (this repo) — frames → video
4. survey-reels — orchestration (planned)

## Install

```bash
pip install survey-animate            # engine core (stdlib + numpy)
pip install "survey-animate[video]"   # + imageio-ffmpeg (bundled static ffmpeg binary)
pip install "survey-animate[text]"    # + matplotlib (burned-in timestamps/title cards)
pip install "survey-animate[full]"    # everything
```

Encoding needs an `ffmpeg` binary. Resolution order: the
`imageio-ffmpeg` wheel's bundled static binary first (no system install),
then a system `ffmpeg` on `PATH`. Check yours with
`survey-animate check`.

## Quickstart

```bash
# Encode a survey-flow manifest as a vertical reel
survey-animate render --manifest frames/manifest.json --preset reel --out lake-michigan.mp4

# Same frames as a GIF
survey-animate render --manifest frames/manifest.json --preset square --out lake.gif

# Any directory of PNGs works too (alphabetical order)
survey-animate render --frames-dir ./passes --preset wide --out series.mp4

# Fully offline synthetic demo (no network, no other repos)
survey-animate demo --out demo-reel.mp4 --preset reel

# Inspect a manifest before encoding
survey-animate manifest-info frames/manifest.json
survey-animate presets
```

```python
from animate import render_video

result = render_video("frames/manifest.json", "lake.mp4",
                      preset="reel", title="Lake Michigan",
                      subtitle="one week of surface currents")
print(result.video_path, result.sidecar_path)
# every video gets a <video>.provenance.json sidecar
```

## Output presets

| Preset    | Size      | Aspect | Default fps | Use                     |
|-----------|-----------|--------|-------------|-------------------------|
| `reel`    | 1080×1920 | 9:16   | 30          | Instagram/TikTok/Shorts |
| `wide`    | 1920×1080 | 16:9   | 30          | YouTube, presentations  |
| `square`  | 1080×1080 | 1:1    | 30          | Feed posts              |
| `preview` | 540×960   | 9:16   | 15          | Fast iteration drafts   |

Input frames are aspect-fit into the preset canvas (bilinear rescale +
padding) — never stretched or cropped. See [docs/PRESETS.md](docs/PRESETS.md).

## Cinematic motion and audio

```python
from animate import MotionSpec, render_video

render_video("frames/manifest.json", "out/reel.mp4",
             motion=MotionSpec(zoom="in", zoom_speed=0.4,
                               pan="up-right", pan_speed=0.3,
                               smooth=True, smooth_steps=3),
             audio_path="music/track.mp3")
```

- **Zoom/pan drift** — `zoom="in"|"out"|"off"`, `pan` one of eight
  compass directions or `"off"`; each has a `0.0–1.0` speed slider.
  Applied via ffmpeg's `zoompan` (sub-pixel, encoder-side).
- **Smooth transitions** — `smooth=True` crossfade-blends consecutive
  frames (`smooth_steps` per gap) so monthly time steps melt together.
- **Audio** — any ffmpeg-readable audio file muxed as AAC/Opus, cut to
  the video length. GIF has no audio track and skips it with a sidecar
  note.
- `motion=` also accepts a plain dict with the same field names; both
  are validated up front. Motion/audio are recorded in the
  `.provenance.json` sidecar.

## How it works

```
survey-flow manifest.json ─┐
                           ├─► manifest.py (validate) ─► presets.py (aspect-fit)
directory of PNGs ─────────┘        │                              │
                              overlays.py                      encode.py
                      (timestamps, title card) ─► ffmpeg ─► video + .provenance.json
```

- **Input contract:** `survey-flow.frame-manifest/1.0` (ordered frames,
  per-frame `timestamp_iso`, relative PNG paths). Unknown major versions
  are rejected with a clear error. Plain PNG directories are accepted as
  a fallback.
- **Encoding:** frames are piped to ffmpeg as raw RGB24 — no temp files.
  MP4 uses H.264 (`libx264`, CRF quality, `+faststart`); GIF uses a
  two-pass global palette; WebM uses VP9.
- **Core is stdlib+numpy:** manifest handling, presets, and the built-in
  PNG codec need nothing else. `imageio`/`imageio-ffmpeg` (video) and
  `matplotlib` (text overlays) are lazy optional imports.

## API overview

| Module | Key entry points |
|--------|------------------|
| `animate.manifest` | `read_manifest(path)`, `frames_from_dir(dir)` |
| `animate.presets` | `get_preset(name)`, `list_presets()`, `resize_pad(frame, w, h)` |
| `animate.encode` | `encode_mp4/gif/webm(...)`, `encode(frames, out, fmt)`, `resolve_ffmpeg()` |
| `animate.overlays` | `burn_timestamps(frames, stamps)`, `make_title_card(...)` |
| `animate.provenance` | `write_sidecar(video_path, ...)` |
| `animate.motion` | `MotionSpec(...)`, `coerce_motion(m)`, `motion_filter(...)`, `blend_frames(...)` |
| `animate.pipeline` | `render_video(source, out_path, preset=..., motion=..., audio_path=...)` → `VideoResult` |

## Interoperability

- **survey-flow** (primary): consumes `survey-flow.frame-manifest/1.0`
  directly — `render_video("frames/manifest.json", ...)`.
- **survey-monitor / survey-thermal**: any per-pass or per-timestep PNG
  series encodes via `--frames-dir`.
- **survey-alerts / survey-monitor**: finished videos are run artifacts;
  see [docs/INTEROP.md](docs/INTEROP.md) for the attachment recipe
  (those repos are untouched).
- **survey-reels** (module 4, planned): will orchestrate
  currents → flow → animate end to end.

## Docs

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — engine layout and design decisions
- [docs/PRESETS.md](docs/PRESETS.md) — preset reference and geometry rules
- [docs/INTEROP.md](docs/INTEROP.md) — suite integration points
- [CHANGELOG.md](CHANGELOG.md)

## License

MIT — see [LICENSE](LICENSE).
