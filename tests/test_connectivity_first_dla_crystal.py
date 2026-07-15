import importlib.util
from pathlib import Path

import numpy as np


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "connectivity_first_dla_crystal_20260509.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("connectivity_first", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bridge_components_connects_two_sparse_parts():
    mod = load_module()
    coords = np.asarray(
        [
            [0, 0, 0],
            [0, 1, 0],
            [4, 1, 0],
        ],
        dtype=np.int64,
    )

    bridged, report = mod.bridge_components_to_largest(coords, connectivity=6)
    stats = mod.occupancy_connectivity_stats(bridged, connectivity=6)

    assert report["components_before"] == 2
    assert report["bridge_voxels_added"] >= 2
    assert stats["component_count"] == 1
    assert stats["largest_component_ratio"] == 1.0


def test_morphological_close_fills_axis_gap():
    mod = load_module()
    coords = np.asarray([[0, 0, 0], [2, 0, 0]], dtype=np.int64)

    closed = mod.morphological_close_coords(coords, radius=1, connectivity=6)

    assert (1, 0, 0) in {tuple(row) for row in closed.tolist()}


def test_connectivity_score_penalizes_small_island():
    mod = load_module()
    coords = np.asarray(
        [
            [0, 0, 0],
            [0, 1, 0],
            [0, 2, 0],
            [8, 8, 8],
        ],
        dtype=np.int64,
    )

    stats = mod.occupancy_connectivity_stats(coords, connectivity=6)

    assert stats["component_count"] == 2
    assert stats["largest_component_ratio"] == 0.75
