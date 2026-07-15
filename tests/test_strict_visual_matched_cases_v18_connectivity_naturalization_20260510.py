import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_v18_connectivity_naturalization_20260510.py"
LAUNCHER = ROOT / "assets" / "launch_strict_visual_matched_texture_v18_connectivity_naturalization_20260510.sh"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_v18_connectivity_naturalization_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v18_materializes_connected_naturalized_dla_frontier_crystal_inputs(tmp_path):
    mod = load_module()

    summary = mod.materialize(ROOT, tmp_path, seed=20260510)

    assert summary["num_cases"] == 8
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["surface_generator"] == "connected_implicit_loop_naturalization_v18"
    assert summary["storage_root"] == "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
    assert summary["connectivity_gate"]["largest_component_vertex_ratio_min"] == 0.999
    assert summary["mesh_pbr_policy"] == "mesh_and_pbr_outputs_only"

    for name in ("manifest.csv", "manifest.json", "initial_metrics.csv", "initial_metrics.json", "a100-2_cases.txt", "gpu4567_cases.txt", "README.md"):
        assert (tmp_path / name).exists()
    for gpu in (4, 5, 6, 7):
        assert (tmp_path / f"gpu{gpu}_cases.txt").exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((tmp_path / "initial_metrics.json").read_text(encoding="utf-8"))
    metric_by_case = {row["case_id"]: row for row in metrics}

    assert {int(row["gpu_group"]) for row in rows} == {4, 5, 6, 7}
    assert all(row["case_id"].startswith("v18_dla_") for row in rows)
    assert all(row["strict_one_to_one"] == "true" for row in rows)
    assert all(row["generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_postprocessing" for row in rows)
    assert all(row["mesh_pbr_policy"] == "mesh_and_pbr_outputs_only" for row in rows)

    expected_motifs = {
        "coral_cluster",
        "frontier_sheet",
        "branching_reef",
        "lattice_crystal",
        "pyrite_orbit",
        "bismuth_step",
    }
    expected_targets = {
        "dla_coral_cluster_900",
        "dla_frontier_sheet_700",
        "dla_branching_reef_650",
        "dla_crystal_lattice_520",
        "dla_pyrite_orbit_480",
        "dla_bismuth_step_crystal_360",
    }
    assert expected_targets <= {row["traditional_target"] for row in rows}

    required_operator_terms = {
        "stochastic_frontier_attachment",
        "occupancy_exclusion",
        "rooted_attachment_bridges",
        "loop_closure_bridges",
        "connected_implicit_support",
        "naturalization_guides",
        "pbr_material_prompt",
        "largest_component_gate",
    }
    seen_motifs = set()
    for row in rows:
        obj_path = Path(row["mesh_path"])
        metadata_path = Path(row["metadata_path"])
        guide_path = Path(row["guide_image"])
        assert obj_path.exists()
        assert obj_path.suffix == ".obj"
        assert metadata_path.exists()
        assert guide_path.exists()
        assert guide_path.suffix == ".png"
        assert "local_postprocess" not in row["operator_composition"]
        assert "selection" not in row["operator_composition"]

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["strict_generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_postprocessing"
        assert metadata["remote_constraints"]["machine"] == "a100-2"
        assert metadata["remote_constraints"]["allowed_gpus"] == [4, 5, 6, 7]
        assert metadata["mesh_pbr_contract"]["mesh_outputs_only"] is True
        assert metadata["mesh_pbr_contract"]["pbr_textured_glb_required"] is True
        assert metadata["mesh_pbr_contract"]["forbidden_outputs"] == ["local_selected_render", "2d_only_image", "posthoc_repair_mesh"]
        assert metadata["root_selection_log"]["root_source_type"] == "v18_connected_implicit_naturalization_input_generator"
        assert metadata["traditional_alignment"]["same_category"] is True
        assert metadata["traditional_alignment"]["strict_one_to_one_comparison"] is True
        assert set(metadata["operators"]) >= required_operator_terms

        controls = metadata["controls"]
        seen_motifs.add(controls["semantic_motif"])
        assert controls["connected_implicit_support"] is True
        assert controls["bridge_root_connectivity"] is True
        assert controls["attachment_bridge_count"] >= 10
        assert controls["loop_closure_bridge_count"] >= 4
        assert controls["naturalization_detail_count"] >= 48
        assert controls["direct_voxel_blocks"] is False
        assert controls["direct_straight_rods"] is False
        assert controls["detached_chunk_policy"] == "forbid_detached_chunks_by_overlapping_primitives_before_marching_cubes"
        assert controls["largest_component_vertex_ratio_min"] == 0.999
        assert "not local repair" in controls["v18_naturalization_policy"]

        contract = metadata["visual_readability_contract"]
        assert "connected" in contract["positive_constraint"]
        assert "coral" in contract["positive_constraint"]
        assert "crystal" in contract["positive_constraint"]
        assert "rods/tubes" in contract["negative_constraint"]
        assert "fragmented chunks" in contract["negative_constraint"]

        m = metric_by_case[row["case_id"]]
        assert m["vertices"] > 1800
        assert m["faces"] > 3600
        assert m["mesh_component_count"] == 1 or m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["surface_area"] > 0.0
        assert m["attachment_bridge_count"] >= 10
        assert m["loop_closure_bridge_count"] >= 4
        assert m["naturalization_detail_count"] >= 48

    assert expected_motifs <= seen_motifs

    with (tmp_path / "manifest.csv").open(encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(csv_rows) == len(rows)
    assert {row["case_id"] for row in csv_rows} == {row["case_id"] for row in rows}

    all_lines = (tmp_path / "a100-2_cases.txt").read_text(encoding="utf-8").strip().splitlines()
    assert len(all_lines) == len(rows)
    for gpu in (4, 5, 6, 7):
        gpu_lines = (tmp_path / f"gpu{gpu}_cases.txt").read_text(encoding="utf-8").strip().splitlines()
        assert len(gpu_lines) == 2
        assert all(line.endswith(f"|{gpu}") for line in gpu_lines)


def test_v18_launcher_uses_remote_gpu4567_project_cache_and_pbr_glb_export_only():
    text = LAUNCHER.read_text(encoding="utf-8")

    assert 'ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"' in text
    assert 'RUN="${RUN:-strict_visual_matched_texture_v18_connectivity_naturalization_20260510}"' in text
    assert 'INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_v18_connectivity_naturalization_20260510}"' in text
    assert "for gpu in 4 5 6 7" in text
    assert "--worker" in text
    assert 'CUDA_VISIBLE_DEVICES="$gpu"' in text
    assert 'TMPDIR="$ROOT/cache/tmp"' in text
    assert 'TORCH_HOME="$ROOT/cache/torch"' in text
    assert 'TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"' in text
    assert "/tmp/" not in text
    assert "TMPDIR=/tmp" not in text
    assert "/dev/shm" not in text
    assert '"status": "ok"' in text
    assert "--texture-size \"$tex\"" in text
    assert "--preprocess" in text
    assert "trellis2_texturing_export_glb.py" in text
