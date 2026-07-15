import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_V26_sc_tree_seam_naturalization_20260511.py"
LAUNCHER = ROOT / "assets" / "launch_strict_visual_matched_texture_V26_sc_tree_seam_naturalization_20260511.sh"
DOC = ROOT / "docs" / "evaluation" / "strict_visual_matched_V26_sc_tree_seam_naturalization_plan_zh_20260511.md"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_V26_sc_tree_seam_naturalization_20260511", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v26_sc_tree_seam_naturalization_materializes_four_case_manifest_and_metrics(tmp_path):
    mod = load_module()

    summary = mod.materialize(ROOT, tmp_path, seed=20260511)

    assert summary["num_cases"] == 4
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["storage_limit_gb"] == 200
    assert summary["surface_generator"] == "strict_visual_matched_cases_V26_sc_tree_seam_naturalization"
    assert summary["surface_strategy"] == "v26_sc_tree_junction_collar_masked_local_naturalization"
    assert summary["mesh_input_policy"] == "obj_mesh_inputs_only"
    assert summary["connectivity_gate"]["largest_component_vertex_ratio_min"] == 0.999
    assert summary["connectivity_gate"]["boundary_tag_allowed"] is False
    assert summary["seam_naturalization_gate"]["mask_scope"] == "branch_crown_junction_band_only"
    assert summary["seam_naturalization_gate"]["min_seam_mask_centers"] > 0
    assert summary["seam_naturalization_gate"]["low_contrast_guides"] is True
    assert summary["seam_naturalization_gate"]["object_space_pbr_qa_recommended"] is True
    assert summary["gpu_case_counts"] == {"4": 1, "5": 1, "6": 1, "7": 1}
    assert summary["storage_risk"]["expected_upper_bound_gb"] <= 24
    assert summary["do_not_launch_remote"] is True

    for name in (
        "manifest.csv",
        "manifest.json",
        "initial_metrics.csv",
        "initial_metrics.json",
        "a100-2_cases.txt",
        "gpu4567_cases.txt",
        "README.md",
        "summary.json",
    ):
        assert (tmp_path / name).exists()
    for gpu in (4, 5, 6, 7):
        assert (tmp_path / f"gpu{gpu}_cases.txt").exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((tmp_path / "initial_metrics.json").read_text(encoding="utf-8"))
    metrics_by_case = {row["case_id"]: row for row in metrics}

    expected_cases = {
        "V26_sc_tree_crown_junction_collar_A_lowcontrast",
        "V26_sc_tree_crown_leafshield_B_lowcontrast",
        "V26_sc_tree_crown_cambium_sleeve_C_lowcontrast",
        "V26_sc_tree_crown_soft_canopy_D_lowcontrast",
    }
    assert {row["case_id"] for row in rows} == expected_cases
    assert {row["family"] for row in rows} == {"Space colonization"}
    assert {int(row["gpu_group"]) for row in rows} == {4, 5, 6, 7}
    assert all(row["strict_one_to_one"] == "true" for row in rows)
    assert all(row["generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_postprocessing" for row in rows)
    assert all(row["mesh_pbr_policy"] == "obj_inputs_lowcontrast_guides_for_trellis2_glb_export_plus_object_space_pbr_qa" for row in rows)
    assert all(row["surface_strategy"] == "v26_sc_tree_junction_collar_masked_local_naturalization" for row in rows)
    assert all(row["block_or_token_stamping"] == "false" for row in rows)
    assert all(row["selection_budget"] == "four_predeclared_sc_tree_seam_candidates_one_per_gpu" for row in rows)
    assert all(int(row["seam_mask_center_count"]) > 0 for row in rows)
    assert all(int(row["junction_collar_count"]) > 0 for row in rows)
    assert all(int(row["junction_leafshield_count"]) > 0 for row in rows)

    for row in rows:
        obj_path = Path(row["mesh_path"])
        metadata_path = Path(row["metadata_path"])
        guide_path = Path(row["guide_image"])
        assert obj_path.exists()
        assert obj_path.suffix == ".obj"
        assert metadata_path.exists()
        assert guide_path.exists()
        assert guide_path.suffix == ".png"

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["case_id"] == row["case_id"]
        assert metadata["remote_constraints"]["allowed_gpus"] == [4, 5, 6, 7]
        assert metadata["root_selection_log"]["source_generator"] == "assets/strict_visual_matched_cases_V26_sc_tree_seam_naturalization_20260511.py"
        assert metadata["v26_remote_cache_policy"]["cache_root"].endswith("/cache")
        assert metadata["v26_remote_cache_policy"]["no_system_tmp"] is True
        assert metadata["v26_seam_naturalization_contract"]["mask_scope"] == "branch_crown_junction_band_only"
        assert metadata["v26_seam_naturalization_contract"]["seam_mask_center_count"] > 0
        assert metadata["v26_seam_naturalization_contract"]["texture_operator"].startswith("low-contrast")

        controls = metadata["controls"]
        assert controls["v26_sc_tree_seam_naturalization"] is True
        assert controls["masked_local_naturalization_target"] == "tree branch/crown junction band"
        assert controls["naturalization_not_global_resampling"] is True
        assert controls["low_contrast_guide_required"] is True
        assert controls["mesh_token_stamping"] is False

        m = metrics_by_case[row["case_id"]]
        assert m["vertices"] > 4000
        assert m["faces"] > 8000
        assert m["mesh_component_count"] == 1
        assert m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["support_edge_count"] >= 20
        assert m["semantic_detail_count"] >= 100
        assert m["seam_mask_center_count"] > 0

    with (tmp_path / "manifest.csv").open(encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(csv_rows) == len(rows)
    assert {row["case_id"] for row in csv_rows} == expected_cases


def test_v26_launcher_is_generate_only_safe_uses_gpu4567_and_project_cache():
    text = LAUNCHER.read_text(encoding="utf-8")

    assert 'ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"' in text
    assert 'RUN="${RUN:-strict_visual_matched_texture_V26_sc_tree_seam_naturalization_20260511}"' in text
    assert 'INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_V26_sc_tree_seam_naturalization_20260511}"' in text
    assert "for gpu in 4 5 6 7" in text
    assert "4|5|6|7" in text
    assert "--worker" in text
    assert "--generate-only" in text
    assert 'CUDA_VISIBLE_DEVICES="$gpu"' in text
    assert 'TMPDIR="$ROOT/cache/local_tmp/$RUN"' in text
    assert 'TORCH_HOME="$ROOT/cache/torch"' in text
    assert 'XDG_CACHE_HOME="$ROOT/cache/xdg"' in text
    assert 'TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"' in text
    assert "/tmp/" not in text
    assert "TMPDIR=/tmp" not in text
    assert "/dev/shm" not in text
    assert "--mesh \"$mesh\"" in text
    assert "--texture-size \"$tex\"" in text
    assert "--preprocess" in text
    assert "trellis2_texturing_export_glb.py" in text
    assert "strict_visual_matched_cases_V26_sc_tree_seam_naturalization_20260511.py" in text


def test_v26_plan_documents_seam_goal_and_claim_boundaries():
    text = DOC.read_text(encoding="utf-8")
    assert "V26" in text
    assert "树枝和树冠" in text
    assert "接缝" in text
    assert "GPU 4/5/6/7" in text
    assert "4 个预声明候选" in text
    assert "junction collar" in text
    assert "低对比" in text
    assert "object-space" in text
    assert "不能写" in text
