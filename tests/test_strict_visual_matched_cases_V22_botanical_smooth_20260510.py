import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_V22_botanical_smooth_20260510.py"
LAUNCHER = ROOT / "assets" / "launch_strict_visual_matched_texture_V22_botanical_smooth_20260510.sh"
DOC = ROOT / "docs" / "evaluation" / "strict_visual_matched_V22_botanical_smooth_zh_20260510.md"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_V22_botanical_smooth_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v22_materializes_strict_smooth_botanical_cases_with_lcr_gate(tmp_path):
    mod = load_module()

    summary = mod.materialize(ROOT, tmp_path, seed=20260510)

    assert summary["num_cases"] == 8
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["surface_generator"] == "strict_lsystem_space_colonization_smooth_botanical_v22"
    assert summary["mesh_input_policy"] == "obj_mesh_inputs_only"
    assert summary["mesh_pbr_policy"] == "obj_inputs_and_pbr_guides_for_trellis2_glb_export"
    assert summary["connectivity_gate"]["largest_component_vertex_ratio_min"] == 0.999
    assert summary["v22_fix_focus"] == "smooth connected botanical semantics without low_poly_block_or_token_stamping"

    for name in ("manifest.csv", "manifest.json", "initial_metrics.csv", "initial_metrics.json", "a100-2_cases.txt", "gpu4567_cases.txt", "README.md", "summary.json"):
        assert (tmp_path / name).exists()
    for gpu in (4, 5, 6, 7):
        assert (tmp_path / f"gpu{gpu}_cases.txt").exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((tmp_path / "initial_metrics.json").read_text(encoding="utf-8"))
    metric_by_case = {row["case_id"]: row for row in metrics}

    expected_targets = {
        "lsys_pine_canopy_d5",
        "lsys_root_fan_d5",
        "lsys_climbing_vine_d6",
        "sc_tree_crown_260",
        "sc_root_network_260",
        "sc_bush_shell_220",
        "lsys_pine_canopy_depth_sweep_d6",
        "sc_root_network_parameter_sweep_dense",
    }
    assert {row["traditional_target"] for row in rows} == expected_targets
    assert {row["family"] for row in rows} == {"L-system", "Space colonization"}
    assert {int(row["gpu_group"]) for row in rows} == {4, 5, 6, 7}
    assert all(row["case_id"].startswith("V22_") for row in rows)
    assert all(row["strict_one_to_one"] == "true" for row in rows)
    assert all(row["generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_postprocessing" for row in rows)
    assert all(row["mesh_input_policy"] == "obj_mesh_inputs_only" for row in rows)
    assert all(row["surface_strategy"] == "smooth_implicit_swept_connected_support_with_attached_semantic_details" for row in rows)
    assert all(row["block_or_token_stamping"] == "false" for row in rows)

    required_operator_terms = {
        "same_classical_recursive_mode",
        "lsystem_or_space_colonization_control",
        "smooth_implicit_radius_field",
        "swept_connected_support",
        "shared_vertex_semantic_detail_attachment",
        "pre_export_leaf_needle_rootlet_details",
        "obj_mesh_input_only",
        "pbr_guide_output_for_trellis2",
        "largest_component_gate",
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
        assert metadata["mesh_pbr_contract"]["forbidden_outputs"] == ["local_selected_render", "2d_only_image", "posthoc_repair_mesh", "non_obj_mesh_input", "low_poly_block_stamp", "mesh_token_stamp"]
        assert metadata["traditional_alignment"]["same_category"] is True
        assert metadata["traditional_alignment"]["strict_one_to_one_comparison"] is True
        assert set(metadata["operators"]) >= required_operator_terms
        assert metadata["grammar_mapping"]["grammar_family"] in {"L-system", "Space colonization"}
        assert metadata["grammar_mapping"]["operator_to_traditional_mapping"]
        assert "F" in metadata["grammar_mapping"]["grammar_symbols"] or "attractor" in metadata["grammar_mapping"]["grammar_symbols"]

        controls = metadata["controls"]
        assert controls["mesh_input_format"] == "obj"
        assert controls["same_classical_task_mode"] is True
        assert controls["connected_support"] is True
        assert controls["connectivity_gate_lcr_min"] == 0.999
        assert controls["low_poly_block_stamping"] is False
        assert controls["mesh_token_stamping"] is False
        assert controls["procedural_block_tokens"] is False
        assert controls["smooth_implicit_support"] is True
        assert controls["swept_support"] is True
        assert controls["shared_vertex_attachment"] is True
        assert controls["semantic_detail_count"] >= 120
        assert controls["support_edge_count"] >= 20

        detail_breakdown = metadata["semantic_detail_breakdown"]
        assert detail_breakdown["total"] == controls["semantic_detail_count"]
        assert detail_breakdown["needle_count"] + detail_breakdown["leaf_count"] + detail_breakdown["rootlet_count"] + detail_breakdown["tendril_count"] >= 120

        contract = metadata["visual_readability_contract"]
        assert "smooth" in contract["positive_constraint"]
        assert "leaf" in contract["positive_constraint"] or "needle" in contract["positive_constraint"] or "rootlet" in contract["positive_constraint"]
        assert "low-poly block" in contract["negative_constraint"]
        assert "token stamping" in contract["negative_constraint"]
        assert "V17" in contract["failure_addressed"]
        assert "V19" in contract["failure_addressed"]

        m = metric_by_case[row["case_id"]]
        assert m["vertices"] > 2500
        assert m["faces"] > 4500
        assert m["mesh_component_count"] == 1 or m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["surface_area"] > 0.0
        assert m["semantic_detail_count"] >= 120
        assert m["low_poly_block_stamping"] is False
        assert m["mesh_token_stamping"] is False

    root_rows = [row for row in rows if "root" in row["traditional_target"]]
    assert len(root_rows) == 3
    for row in root_rows:
        root_meta = json.loads(Path(row["metadata_path"]).read_text(encoding="utf-8"))
        assert root_meta["semantic_detail_breakdown"]["rootlet_count"] >= 120
        assert root_meta["controls"]["rootlet_count"] >= 120

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


def test_v22_launcher_uses_gpu4567_project_local_caches_and_does_not_auto_launch_in_dryrun():
    text = LAUNCHER.read_text(encoding="utf-8")

    assert 'ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"' in text
    assert 'RUN="${RUN:-strict_visual_matched_texture_V22_botanical_smooth_20260510}"' in text
    assert 'INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_V22_botanical_smooth_20260510}"' in text
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


def test_v22_chinese_doc_explains_smooth_grammar_and_failure_fix():
    text = DOC.read_text(encoding="utf-8")
    assert "V22" in text
    assert "严格一对一" in text
    assert "L-system" in text
    assert "space-colonization" in text
    assert "OBJ" in text
    assert "LCR >= 0.999" in text
    assert "平滑" in text
    assert "隐式半径场" in text
    assert "扫掠支撑" in text
    assert "叶片" in text
    assert "针叶" in text
    assert "根须" in text
    assert "不是 low-poly block" in text
    assert "不是 token stamping" in text
    assert "V17" in text
    assert "V19" in text
    assert "GPU 4/5/6/7" in text
