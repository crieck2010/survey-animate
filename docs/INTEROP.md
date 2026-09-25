# Interoperability

survey-animate sits at the end of the earthwatch animation chain and
also works standalone on any PNG sequence.

## As a survey-flow consumer (primary path)

```python
from animate import render_video

result = render_video(
    "frames/manifest.json",          # survey-flow.frame-manifest/1.0
    "lake-michigan.mp4",
    preset="reel",
    title="Lake Michigan",
    subtitle="one week of surface currents, colored by water temperature",
)
# result.video_path, result.sidecar_path ("lake-michigan.mp4.provenance.json")
```

- survey-flow stays an **optional peer**, not a hard dependency:
  animate reads the manifest JSON schema, never imports survey-flow.
- The manifest's `timestamp_iso` values become the burned-in labels
  (`16 Sep 2026 00:00 UTC`); blank timestamps leave frames untouched.
- survey-flow burns its own colorbar legend — animate does not
  double-draw one.

## On survey-monitor / survey-thermal PNG series

Any ordered PNG series encodes without a manifest:

```bash
# survey-monitor per-pass rasters, survey-thermal heatwave frames, ...
survey-animate render --frames-dir ./thermal_passes --preset wide \
    --out heatwave.mp4 --no-timestamps
```

`frames_from_dir()` sorts by filename; pass explicit `timestamps=[...]`
from Python when labels matter.

## Finished videos as run artifacts (documented integration)

These repos are **not modified** — the recipes below are the intended
wiring for module 4 (survey-reels) and for users:

- **survey-monitor**: treat the MP4 + `.provenance.json` as run
  artifacts next to the run summary. A natural hook is
  `monitor.alerts.RunSummary` — attach `video_path` as an artifact
  path in the summary JSON written by `write_summary()`.
- **survey-alerts**: attach the reel to the digest email / embed a
  poster frame in the PDF/HTML report. The provenance sidecar gives the
  report builder everything needed for a caption (source, preset,
  frame count, encoder).
- **survey-qgis**: no direct hook — animate works on rendered frames,
  while qgis works on geodata. The bridge is survey-flow's static
  snapshot maps, which can enter QGIS as a Processing algorithm
  (see survey-flow's `docs/INTEROP.md`).

## Stable contracts

| Direction | Format | Spec |
|-----------|--------|------|
| In (primary) | survey-flow frame manifest | `survey-flow.frame-manifest/1.0` |
| In (fallback) | directory of PNGs | alphabetical order |
| Out | MP4 (H.264) / GIF / WebM | docs/PRESETS.md |
| Out | provenance sidecar | `survey-animate.provenance/1.0` |

Breaking changes to the provenance schema will bump its major version;
readers should check the `schema` field the same way animate checks the
manifest's.
