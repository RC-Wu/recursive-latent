import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_V23_all_family_20260510.py"
LAUNCHER = ROOT / "assets" / "launch_strict_visual_matched_texture_V23_all_family_20260510.sh"
DOC = ROOT / "docs" / "evaluation" / "strict_visual_matched_V23_all_family_plan_zh_20260510.md"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_V23_all_family_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v23_materializes_all_strict_matched_families_with_connectivity_and_manifest(tmp_path):
    mod = load_module()

    summary = mod.materialize(ROOT, tmp_path, seed=20260510)

    assert summary["num_cases"] == 16
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["surface_generator"] == "strict_all_family_matched_cases_v23"
    assert summary["mesh_input_policy"] == "obj_mesh_inputs_only"
    assert summary["mesh_pbr_policy"] == "obj_inputs_and_pbr_guides_for_trellis2_glb_export"
    assert summary["connectivity_gate"]["largest_component_vertex_ratio_min"] == 0.999
    assert summary["estimated_remote_cases"] == 16
    assert summary["gpu_case_counts"] == {"4": 4, "5": 4, "6": 4, "7": 4}
    assert summary["storage_risk"]["expected_upper_bound_gb"] <= 72

    for name in ("manifest.csv", "manifest.json", "initial_metrics.csv", "initial_metrics.json", "a100-2_cases.txt", "gpu4567_cases.txt", "README.md", "summary.json"):
        assert (tmp_path / name).exists()
    for gpu in (4, 5, 6, 7):
        assert (tmp_path / f"gpu{gpu}_cases.txt").exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((tmp_path / "initial_metrics.json").read_text(encoding="utf-8"))
    metric_by_case = {row["case_id"]: row for row in metrics}

    assert len(rows) == 16
    assert {row["family"] for row in rows} == {"L-system", "Space colonization", "DLA/frontier", "IFS/transform"}
    assert {int(row["gpu_group"]) for row in rows} == {4, 5, 6, 7}
    assert all(row["case_id"].startswith("V23_") for row in rows)
    assert all(row["strict_one_to_one"] == "true" for row in rows)
    assert all(row["generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_postprocessing" for row in rows)
    assert all(row["mesh_input_policy"] == "obj_mesh_inputs_only" for row in rows)
    assert all(row["surface_strategy"] == "connected_swept_or_facet_support_with_family_semantic_details" for row in rows)
    assert all(row["block_or_token_stamping"] == "false" for row in rows)
    assert all(row["root_variant"] for row in rows)
    assert all(row["grammar_guide"] for row in rows)
    assert all(row["parameter_variant"] for row in rows)
    assert all(row["selection_budget"] == "one_remote_generation_per_manifest_row_no_local_cherry_pick" for row in rows)

    expected_targets = {
        "lsys_pine_canopy_d5",
        "lsys_root_fan_d5",
        "lsys_climbing_vine_d6",
        "lsys_root_fan_d5_dense_rootlets",
        "sc_tree_crown_260",
        "sc_root_network_260",
        "sc_bush_shell_220",
        "sc_tree_crown_260_sparse_kill",
        "dla_coral_cluster_900",
        "dla_frontier_sheet_700",
        "dla_crystal_cluster_520",
        "dla_coral_cluster_900_lace_porosity",
        "ifs_fractal_lattice_d4",
        "ifs_radial_ornament_o8_d4",
        "ifs_fractal_tree_d5",
        "ifs_branch_ornament_d5",
    }
    assert {row["traditional_target"] for row in rows} == expected_targets

    required_operator_terms_by_family = {
        "L-system": {"lsystem_rewriting", "smooth_swept_branch_support", "shared_vertex_attachment", "largest_component_gate"},
        "Space colonization": {"attractor_select", "kill_covered_attractors", "smooth_swept_branch_support", "largest_component_gate"},
        "DLA/frontier": {"frontier_sample", "occupancy_exclusion", "bridge_to_root_certificate", "largest_component_gate"},
        "IFS/transform": {"transform_copy", "orbit_or_lattice_certificate", "contact_bridge", "largest_component_gate"},
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
        assert ".glb" not in row["mesh_path"]
        assert ".ply" not in row["mesh_path"]
        assert "token" not in row["operator_composition"].lower()
        assert "block" not in row["operator_composition"].lower()
        assert row["why_matches_traditional"]

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["case_id"] == row["case_id"]
        assert metadata["traditional_target"] == row["traditional_target"]
        assert metadata["strict_generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_postprocessing"
        assert metadata["remote_constraints"]["machine"] == "a100-2"
        assert metadata["remote_constraints"]["allowed_gpus"] == [4, 5, 6, 7]
        assert metadata["mesh_pbr_contract"]["input_mesh_format"] == "obj"
        assert metadata["mesh_pbr_contract"]["obj_mesh_inputs_only"] is True
        assert metadata["mesh_pbr_contract"]["pbr_textured_glb_required"] is True
        assert metadata["mesh_pbr_contract"]["forbidden_outputs"] == [
            "local_selected_render",
            "2d_only_image",
            "posthoc_repair_mesh",
            "non_obj_mesh_input",
            "low_poly_block_stamp",
            "mesh_token_stamp",
        ]
        assert metadata["traditional_alignment"]["same_category"] is True
        assert metadata["traditional_alignment"]["strict_one_to_one_comparison"] is True
        assert set(metadata["operators"]) >= required_operator_terms_by_family[row["family"]]
        assert metadata["grammar_mapping"]["grammar_family"] == row["family"]
        assert metadata["grammar_mapping"]["operator_to_traditional_mapping"]
        assert metadata["root_selection_log"]["root_variant"] == row["root_variant"]
        assert metadata["root_selection_log"]["grammar_guide"] == row["grammar_guide"]
        assert metadata["root_selection_log"]["parameter_variant"] == row["parameter_variant"]

        controls = metadata["controls"]
        assert controls["mesh_input_format"] == "obj"
        assert controls["same_classical_task_mode"] is True
        assert controls["connected_support"] is True
        assert controls["connectivity_gate_lcr_min"] == 0.999
        assert controls["low_poly_block_stamping"] is False
        assert controls["mesh_token_stamping"] is False
        assert controls["support_edge_count"] >= 20
        assert controls["semantic_detail_count"] >= 24

        diagnostics = metadata["family_diagnostics"]
        assert diagnostics["post_glb_required"] is True
        assert diagnostics["metric_family"] == row["family"]
        if row["family"] == "L-system":
            assert diagnostics["visible_depth"] >= 5
            assert diagnostics["path_to_root_rate_required"] >= 0.95
        elif row["family"] == "Space colonization":
            assert diagnostics["attractor_count"] >= 220
            assert diagnostics["coverage_metric_required"] is True
        elif row["family"] == "DLA/frontier":
            assert diagnostics["frontier_events"] >= 520
            assert diagnostics["bridge_certificate_required"] is True
        elif row["family"] == "IFS/transform":
            assert diagnostics["recursive_depth"] >= 4
            assert diagnostics["orbit_or_lattice_metric_required"] is True

        contract = metadata["visual_readability_contract"]
        assert "paper" in contract["positive_constraint"]
        assert "low-poly block" in contract["negative_constraint"]
        assert "token stamping" in contract["negative_constraint"]
        assert "not final selected output" in contract["dryrun_visual_floor"]

        m = metric_by_case[row["case_id"]]
        assert m["vertices"] > 1400
        assert m["faces"] > 2400
        assert m["mesh_component_count"] == 1 or m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["surface_area"] > 0.0
        assert m["support_edge_count"] >= 20
        assert m["semantic_detail_count"] >= 24
        assert m["low_poly_block_stamping"] is False
        assert m["mesh_token_stamping"] is False

    with (tmp_path / "manifest.csv").open(encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(csv_rows) == len(rows)
    assert {row["case_id"] for row in csv_rows} == {row["case_id"] for row in rows}

    all_lines = (tmp_path / "a100-2_cases.txt").read_text(encoding="utf-8").strip().splitlines()
    assert len(all_lines) == len(rows)
    for gpu in (4, 5, 6, 7):
        gpu_lines = (tmp_path / f"gpu{gpu}_cases.txt").read_text(encoding="utf-8").strip().splitlines()
        assert len(gpu_lines) == 4
        assert all(line.endswith(f"|{gpu}") for line in gpu_lines)


def test_v23_launcher_is_generate_only_safe_and_uses_gpu4567_project_caches():
    text = LAUNCHER.read_text(encoding="utf-8")

    assert 'ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"' in text
    assert 'RUN="${RUN:-strict_visual_matched_texture_V23_all_family_20260510}"' in text
    assert 'INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_V23_all_family_20260510}"' in text
    assert "for gpu in 4 5 6 7" in text
    assert "--worker" in text
    assert "--generate-only" in text
    assert 'CUDA_VISIBLE_DEVICES="$gpu"' in text
    assert 'TMPDIR="$ROOT/cache/local_tmp/$RUN"' in text
    assert 'TORCH_HOME="$ROOT/cache/torch"' in text
    assert 'TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"' in text
    assert "/tmp/" not in text
    assert "TMPDIR=/tmp" not in text
    assert "/dev/shm" not in text
    assert "--mesh \"$mesh\"" in text
    assert "--texture-size \"$tex\"" in text
    assert "--preprocess" in text
    assert "trellis2_texturing_export_glb.py" in text
    assert '"status": "ok"' in text
    assert "nohup bash" in text


def test_v23_chinese_plan_explains_batch_coverage_commands_gpu_split_and_risks():
    text = DOC.read_text(encoding="utf-8")
    assert "V23" in text
    assert "严格一对一" in text
    assert "16" in text
    assert "L-system" in text
    assert "space-colonization" in text
    assert "DLA" in text
    assert "IFS" in text
    assert "GPU 4/5/6/7" in text
    assert "每卡 4 个" in text
    assert "generate-only" in text
    assert "不要直接 ssh 启动" in text
    assert "存储风险" in text
    assert "OBJ" in text
    assert "LCR >= 0.999" in text
    assert "paper-grade" in text
