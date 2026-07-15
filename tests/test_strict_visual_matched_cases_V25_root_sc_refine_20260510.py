import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_V25_root_sc_refine_20260510.py"
LAUNCHER = ROOT / "assets" / "launch_strict_visual_matched_texture_V25_root_sc_refine_20260510.sh"
DOC = ROOT / "docs" / "evaluation" / "strict_visual_matched_V25_root_sc_refine_plan_zh_20260510.md"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_V25_root_sc_refine_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v25_root_sc_refine_materializes_eight_case_manifest_and_metrics(tmp_path):
    mod = load_module()

    summary = mod.materialize(ROOT, tmp_path, seed=20260510)

    assert summary["num_cases"] == 8
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["storage_limit_gb"] == 200
    assert summary["surface_generator"] == "strict_visual_matched_cases_V25_root_sc_refine"
    assert summary["mesh_input_policy"] == "obj_mesh_inputs_only"
    assert summary["connectivity_gate"]["largest_component_vertex_ratio_min"] == 0.999
    assert summary["connectivity_gate"]["boundary_tag_allowed"] is False
    assert summary["do_not_launch_remote"] is True
    assert summary["gpu_case_counts"] == {"4": 2, "5": 2, "6": 2, "7": 2}
    assert summary["storage_risk"]["expected_upper_bound_gb"] <= 40

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

    assert len(rows) == 8
    assert {row["family"] for row in rows} == {"L-system", "Space colonization"}
    assert {int(row["gpu_group"]) for row in rows} == {4, 5, 6, 7}
    assert all(row["case_id"].startswith("V25_") for row in rows)
    assert all(row["strict_one_to_one"] == "true" for row in rows)
    assert all(row["generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_postprocessing" for row in rows)
    assert all(row["mesh_input_policy"] == "obj_mesh_inputs_only" for row in rows)
    assert all(row["mesh_pbr_policy"] == "obj_inputs_and_pbr_guides_for_trellis2_glb_export" for row in rows)
    assert all(row["surface_strategy"] == "v25_root_sc_refine_tapered_support_and_attached_detail" for row in rows)
    assert all(row["block_or_token_stamping"] == "false" for row in rows)
    assert all(float(row["pre_export_lcr_gate"]) == 0.999 for row in rows)
    assert all(row["pre_export_gate_or_boundary"] == "lcr>=0.999" for row in rows)
    assert all(not row["boundary_tag"] for row in rows)
    assert all(row["selection_budget"] == "small_refinement_batch_8_manifest_rows_predeclared" for row in rows)

    expected_cases = {
        "V25_lsys_root_fan_dense_anchorC_stable",
        "V25_lsys_root_fan_dense_anchorD_stable",
        "V25_lsys_root_fan_smooth_anchorC_stable",
        "V25_lsys_root_fan_smooth_anchorD_stable",
        "V25_sc_tree_crown_tapered_A",
        "V25_sc_tree_crown_tapered_B",
        "V25_sc_tree_crown_leafshield_A",
        "V25_sc_tree_crown_leafshield_B",
    }
    assert {row["case_id"] for row in rows} == expected_cases

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
        assert metadata["root_selection_log"]["source_generator"] == "assets/strict_visual_matched_cases_V25_root_sc_refine_20260510.py"
        assert metadata["v25_remote_cache_policy"]["cache_root"].endswith("/cache")
        assert metadata["v25_remote_cache_policy"]["no_system_tmp"] is True
        assert metadata["strict_generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_postprocessing"

        controls = metadata["controls"]
        assert controls["mesh_input_format"] == "obj"
        assert controls["v25_root_sc_refine"] is True
        assert controls["connectivity_gate_lcr_min"] == 0.999
        assert controls["low_poly_block_stamping"] is False
        assert controls["mesh_token_stamping"] is False

        m = metrics_by_case[row["case_id"]]
        assert m["vertices"] > 2500
        assert m["faces"] > 4500
        assert m["mesh_component_count"] == 1
        assert m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["support_edge_count"] >= 20
        assert m["semantic_detail_count"] >= 50

    with (tmp_path / "manifest.csv").open(encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(csv_rows) == len(rows)
    assert {row["case_id"] for row in csv_rows} == expected_cases

    for gpu in (4, 5, 6, 7):
        gpu_lines = (tmp_path / f"gpu{gpu}_cases.txt").read_text(encoding="utf-8").strip().splitlines()
        assert len(gpu_lines) == 2
        assert all(line.endswith(f"|{gpu}") for line in gpu_lines)


def test_v25_launcher_is_generate_only_safe_uses_gpu4567_and_project_cache():
    text = LAUNCHER.read_text(encoding="utf-8")

    assert 'ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"' in text
    assert 'RUN="${RUN:-strict_visual_matched_texture_V25_root_sc_refine_20260510}"' in text
    assert 'INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_V25_root_sc_refine_20260510}"' in text
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
    assert "strict_visual_matched_cases_V25_root_sc_refine_20260510.py" in text


def test_v25_plan_documents_replacement_gates_and_boundaries():
    text = DOC.read_text(encoding="utf-8")
    assert "V25" in text
    assert "root/SC refine" in text
    assert "GPU 4/5/6/7" in text
    assert "8" in text
    assert "200GB" in text
    assert "generate-only" in text
    assert "OBJ" in text
    assert "LCR >= 0.999" in text
    assert "root fan" in text
    assert "SC tree crown" in text
    assert "不能直接替换" in text
    assert "r0" in text
    assert "V25_lsys_root_fan_dense_anchorC_stable" in text
    assert "V25_sc_tree_crown_tapered_A" in text
