import importlib.util
from pathlib import Path

import numpy as np
import trimesh


MODULE_PATH = Path(__file__).resolve().parents[1] / "assets" / "naturalize_blocky_mesh_pilot_20260510.py"
spec = importlib.util.spec_from_file_location("naturalize_blocky_mesh_pilot_20260510", MODULE_PATH)
pilot = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(pilot)


def test_bridge_connects_two_voxel_components_without_deleting_support():
    matrix = np.zeros((12, 12, 12), dtype=bool)
    matrix[2:4, 5:7, 5:7] = True
    matrix[8:10, 5:7, 5:7] = True

    before = pilot.component_stats_6n(matrix)
    bridged = pilot.bridge_components_to_largest(matrix, max_components=4, min_voxels=1, bridge_radius=1)
    after = pilot.component_stats_6n(bridged)

    assert before["component_count"] == 2
    assert after["component_count"] == 1
    assert after["occupied_voxels"] > before["occupied_voxels"]
    assert np.all(bridged[matrix])


def test_naturalize_mesh_returns_connected_marching_cubes_mesh_for_separated_cubes():
    left = trimesh.creation.box(extents=(1.0, 1.0, 1.0))
    left.apply_translation((-1.3, 0.0, 0.0))
    right = trimesh.creation.box(extents=(1.0, 1.0, 1.0))
    right.apply_translation((1.3, 0.0, 0.0))
    mesh = trimesh.util.concatenate([left, right])

    result = pilot.naturalize_mesh(
        mesh,
        resolution=32,
        initial_dilate=1,
        close_iterations=1,
        smooth_sigma=0.35,
        bridge=True,
        bridge_radius=1,
        simplify_faces=0,
    )

    assert len(result.mesh.vertices) > 0
    assert len(result.mesh.faces) > 0
    assert result.after["component_count"] == 1
    assert result.after["largest_component_ratio"] == 1.0
    assert result.after["occupied_voxels"] >= result.before["occupied_voxels"]
