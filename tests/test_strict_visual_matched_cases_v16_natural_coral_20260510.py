import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_v16_natural_coral_20260510.py"
LAUNCHER = ROOT / "assets" / "launch_strict_visual_matched_texture_v16_natural_coral_20260510.sh"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_v16_natural_coral_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v16_materializes_natural_coral_dla_frontier_inputs_with_connected_smooth_surfaces(tmp_path):
    mod = load_module()

    summary = mod.materialize(ROOT, tmp_path, seed=20260510)

    assert summary["num_cases"] == 8
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["storage_root"] == "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
    assert summary["surface_generator"] == "implicit_sdf_taubin_natural_coral_v16"
    assert summary["connectivity_gate"]["largest_component_vertex_ratio_min"] == 0.999
    assert (tmp_path / "manifest.csv").exists()
    assert (tmp_path / "manifest.json").exists()
    assert (tmp_path / "initial_metrics.csv").exists()
    assert (tmp_path / "initial_metrics.json").exists()
    assert (tmp_path / "a100-2_cases.txt").exists()
    assert (tmp_path / "gpu4567_cases.txt").exists()
    for gpu in (4, 5, 6, 7):
        assert (tmp_path / f"gpu{gpu}_cases.txt").exists()
    assert (tmp_path / "README.md").exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((tmp_path / "initial_metrics.json").read_text(encoding="utf-8"))
    metric_by_case = {row["case_id"]: row for row in metrics}

    expected_targets = {
        "dla_coral_cluster_900",
        "dla_frontier_sheet_700",
        "dla_crystal_cluster_520",
    }
    assert {row["traditional_target"] for row in rows} == expected_targets
    assert {row["family"] for row in rows} == {"DLA/frontier"}
    assert {int(row["gpu_group"]) for row in rows} == {4, 5, 6, 7}
    assert all(row["case_id"].startswith("v16_dla_natural_") for row in rows)
    assert all(row["strict_one_to_one"] == "true" for row in rows)
    assert all(row["generation_policy"] == "generate_new_on_a100_2_no_local_cherrypick" for row in rows)
    assert sum(row["case_role"] == "priority_a100_2" for row in rows) >= 6

    expected_motifs = {
        "staghorn",
        "branching_elkhorn",
        "table_coral",
        "porous_reef_plate",
        "frontier_sheet",
        "faceted_crystal_boundary",
    }
    seen_motifs = set()
    required_operator_terms = {
        "stochastic_frontier_attachment",
        "occupancy_exclusion",
        "bridge_root_connectivity",
        "implicit_sdf_union",
        "high_resolution_marching_cubes",
        "taubin_laplacian_shape_smoothing",
        "rounded_tapered_terminal_tips",
        "subtle_pore_depressions",
        "attached_polyp_buds",
        "surface_ridge_microrelief",
        "continuous_reef_base",
    }

    for row in rows:
        obj_path = Path(row["mesh_path"])
        metadata_path = Path(row["metadata_path"])
        guide_path = Path(row["guide_image"])
        assert obj_path.exists()
        assert obj_path.suffix == ".obj"
        assert metadata_path.exists()
        assert guide_path.exists()
        assert guide_path.suffix == ".png"
        assert "natural_coral_semantics" in row["operator_composition"]
        assert "local_postprocess_repair" not in row["operator_composition"]
        assert row["controls"]
        assert row["why_matches_traditional"]

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["case_id"] == row["case_id"]
        assert metadata["traditional_target"] == row["traditional_target"]
        assert metadata["strict_generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_posthoc_pick"
        assert metadata["remote_constraints"]["machine"] == "a100-2"
        assert metadata["remote_constraints"]["allowed_gpus"] == [4, 5, 6, 7]
        assert metadata["root_selection_log"]["root_source_type"] == "v16_native_natural_coral_input_generator"
        assert metadata["root_selection_log"]["source_generator"].endswith(
            "strict_visual_matched_cases_v16_natural_coral_20260510.py"
        )
        assert metadata["traditional_alignment"]["operator_family"] == "traditional DLA/frontier accretive attachment"
        assert metadata["traditional_alignment"]["same_category"] is True
        assert "fresh on a100-2" in metadata["traditional_alignment"]["why_strict_one_to_one"]
        assert set(metadata["operators"]) >= required_operator_terms

        controls = metadata["controls"]
        seen_motifs.add(controls["natural_coral_motif"])
        assert controls["frontier_attachment_mode"].startswith("stochastic active-tip frontier")
        assert controls["occupancy_exclusion_radius"] > 0.0
        assert controls["bridge_root_connectivity"] is True
        assert controls["continuous_base"] is True
        assert controls["direct_voxel_blocks"] is False
        assert controls["direct_straight_rods"] is False
        assert controls["flat_terminal_cuts"] is False
        assert controls["huge_shell_blob"] is False
        assert controls["implicit_grid_resolution"] >= 84
        assert controls["section_samples_per_edge"] >= 14
        assert controls["taubin_smoothing_iterations"] >= 8
        assert controls["metaball_sample_count"] >= 1400
        assert controls["generated_nodes"] >= 180
        assert controls["rounded_terminal_tip_count"] >= 44
        assert controls["attached_polyp_count"] >= 70
        assert controls["subtle_pore_depression_count"] >= 36
        assert controls["surface_ridge_count"] >= 70
        assert controls["largest_component_vertex_ratio_min"] == 0.999
        assert "generator-native" in controls["surface_strategy"]
        assert "not local repair" in controls["v16_naturalization_policy"]

        contract = metadata["visual_readability_contract"]
        assert "single main component" in contract["dryrun_visual_floor"]
        assert "faceted/low-poly coarse branches" in contract["v14_failure_addressed"]
        assert "coral/reef" in contract["positive_constraint"]
        assert "voxel blocks" in contract["negative_constraint"]
        assert "straight rods" in contract["negative_constraint"]

        m = metric_by_case[row["case_id"]]
        assert m["vertices"] > 4200
        assert m["faces"] > 8000
        assert m["mesh_component_count"] == 1 or m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["surface_area"] > 0.0
        assert m["rounded_terminal_tip_count"] >= 44
        assert m["attached_polyp_count"] >= 70
        assert m["subtle_pore_depression_count"] >= 36
        assert m["surface_ridge_count"] >= 70

    assert seen_motifs == expected_motifs

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


def test_v16_launcher_uses_remote_gpu4567_cache_layout_worker_mode_and_skip_ok_summaries():
    text = LAUNCHER.read_text(encoding="utf-8")

    assert 'ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"' in text
    assert 'RUN="${RUN:-strict_visual_matched_texture_v16_natural_coral_20260510}"' in text
    assert 'INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_v16_natural_coral_20260510}"' in text
    assert "for gpu in 4 5 6 7" in text
    assert "--worker" in text
    assert 'CUDA_VISIBLE_DEVICES="$gpu"' in text
    assert 'DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"' in text
    assert 'TMPDIR="$ROOT/cache/tmp"' in text
    assert 'TORCH_HOME="$ROOT/cache/torch"' in text
    assert 'TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"' in text
    assert "/tmp/devshm" not in text
    assert '"status": "ok"' in text
    assert "--texture-size \"$tex\"" in text
