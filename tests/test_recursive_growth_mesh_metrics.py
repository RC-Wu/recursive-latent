import argparse
import importlib.util
from pathlib import Path

import numpy as np


MODULE_PATH = Path(__file__).resolve().parents[1] / "assets" / "recursive_growth_mesh_metrics.py"
spec = importlib.util.spec_from_file_location("recursive_growth_mesh_metrics", MODULE_PATH)
metrics = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(metrics)


def test_quantized_weld_connectivity_merges_duplicate_spatial_vertices():
    vertices = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=np.float64,
    )
    faces = np.asarray([[0, 1, 2], [3, 4, 5]], dtype=np.int64)

    raw = metrics.component_stats(vertices, faces)
    welded = metrics.welded_component_stats(vertices, faces, tolerance=1e-6)

    assert raw["component_count"] == 2
    assert welded["welded_vertices"] == 4
    assert welded["welded_component_count"] == 1
    assert welded["largest_welded_component_vertex_ratio"] == 1.0


def test_metric_one_marks_occupancy_as_default_primary_connectivity(tmp_path):
    obj = tmp_path / "two_triangles.obj"
    obj.write_text(
        "\n".join(
            [
                "v 0 0 0",
                "v 1 0 0",
                "v 0 1 0",
                "v 1 0 0",
                "v 1 1 0",
                "v 0 1 0",
                "f 1 2 3",
                "f 4 5 6",
            ]
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        sample_limit=1000,
        occupancy_resolution=8,
        box_resolutions=[4, 8],
        weld_tolerance=1e-6,
        primary_connectivity="occupancy",
    )

    row = metrics.metric_one(obj, "fixture", args)

    assert row["component_count"] == 2
    assert row["welded_component_count"] == 1
    assert row["primary_connectivity_metric"] == "occupancy_6n_vertex_voxel"
    assert row["primary_component_count"] == row["occupancy_component_count_6n"]
