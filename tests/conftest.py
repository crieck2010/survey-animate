"""Shared fixtures: temp dirs, tiny PNGs, synthetic manifests."""

from __future__ import annotations

import json
import os

import numpy as np
import pytest

from animate import _png
from animate.manifest import Manifest, ManifestFrame


@pytest.fixture()
def tmp_png(tmp_path):
    def _make(name="f.png", shape=(32, 48, 3), seed=0):
        rng = np.random.default_rng(seed)
        img = (rng.random(shape) * 255).astype(np.uint8)
        p = str(tmp_path / name)
        _png.write_png(p, img)
        return p, img
    return _make


@pytest.fixture()
def manifest_dict(tmp_png):
    p0, _ = tmp_png("a.png", seed=1)
    p1, _ = tmp_png("b.png", seed=2)
    return {
        "schema": "survey-flow.frame-manifest/1.0",
        "generator": "survey-flow 0.1.0",
        "created": "2026-09-25T00:00:00+00:00",
        "fps": 12.0,
        "size_px": [48, 32],
        "field_source": "synthetic/test",
        "n_frames": 2,
        "frames": [
            {"frame_index": 0, "timestamp_iso": "2026-09-16T00:00:00+00:00",
             "png_path": os.path.basename(p0), "scalar": "temperature",
             "scalar_range": [10.0, 20.0], "colormap": "cividis",
             "style": "reel-dark", "render_params": {"seed": 7}},
            {"frame_index": 1, "timestamp_iso": "2026-09-16T01:00:00+00:00",
             "png_path": os.path.basename(p1), "scalar": "temperature",
             "scalar_range": [10.0, 20.0], "colormap": "cividis",
             "style": "reel-dark", "render_params": {"seed": 7}},
        ],
    }


@pytest.fixture()
def manifest_file(tmp_path, manifest_dict):
    p = str(tmp_path / "manifest.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(manifest_dict, fh)
    return p
