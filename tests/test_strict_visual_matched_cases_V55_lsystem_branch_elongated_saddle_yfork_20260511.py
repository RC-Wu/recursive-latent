import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_V55_lsystem_branch_elongated_saddle_yfork_20260511.py"
LAUNCHER = ROOT / "assets" / "launch_strict_visual_matched_texture_V55_lsystem_branch_elongated_saddle_yfork_20260511.sh"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_V55_lsystem_branch_elongated_saddle_yfork_20260511", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v55_lsystem_branch_materializes_elongated_saddle_cases(tmp_path):
    mod = load_module()
    summary = mod.materialize(ROOT, tmp_path, seed=20260511)

    assert summary["num_cases"] == 4
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["default_active_gpus"] == [4, 5]
    assert summary["max_simultaneous_remote_gpus"] == 2
    assert summary["storage_limit_gb"] == 200
    assert summary["surface_generator"] == "strict_visual_matched_cases_V55_lsystem_branch_elongated_saddle_yfork_naturalization"
    assert summary["surface_strategy"] == "v55_lsystem_branch_elongated_saddle_yfork_naturalization"
    assert summary["lsystem_branch_gate"]["mask_scope"] == "object_space_elongated_saddle_yfork_bands_only"
    assert summary["lsystem_branch_gate"]["terminal_sleeves_required"] is False
    assert summary["lsystem_branch_gate"]["min_terminal_sleeves"] == 0
    assert summary["lsystem_branch_gate"]["min_terminal_tapers"] > 0
    assert summary["lsystem_branch_gate"]["max_field_terminal_tapers"] == 0
    assert summary["lsystem_branch_gate"]["max_direct_axis_sleeves"] == 0
    assert summary["do_not_launch_remote_before_local_visual_qa"] is True

    zoom_manifest = tmp_path / "V55_obj_zoom_manifest_junctiontarget_20260511.json"
    assert zoom_manifest.exists()
    assert not (tmp_path / "V54_obj_zoom_manifest_junctiontarget_20260511.json").exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    expected_cases = {
        "V55_lsys_branch_elongated_saddle_yfork_A",
        "V55_lsys_branch_elongated_saddle_yfork_lowfrag_B",
        "V55_lsys_branch_elongated_saddle_yfork_dense_C",
        "V55_lsys_branch_elongated_saddle_yfork_slim_D",
    }
    assert {row["case_id"] for row in rows} == expected_cases
    assert {row["family"] for row in rows} == {"L-system"}
    assert {row["match_target"] for row in rows} == {"lsys_branch_side_d5"}
    assert {int(row["gpu_group"]) for row in rows} == {4, 5}
    assert all(row["surface_strategy"] == "v55_lsystem_branch_elongated_saddle_yfork_naturalization" for row in rows)
    assert all(row["strict_one_to_one"] == "true" for row in rows)
    assert all(int(row["terminal_sleeve_count"]) == 0 for row in rows)
    assert all(int(row["terminal_taper_count"]) > 0 for row in rows)
    assert all(int(row["graph_terminal_taper_count"]) > 0 for row in rows)
    assert all(int(row["field_terminal_taper_count"]) == 0 for row in rows)
    assert all(int(row["direct_axis_sleeve_count"]) == 0 for row in rows)
    assert all(int(row["implicit_saddle_swell_count"]) >= 9 for row in rows)
    assert all(float(row["largest_component_projection_retained_ratio"]) >= 0.90 for row in rows)
    assert all(float(row["external_support_max_segment_after_subdivision"]) <= 0.100001 for row in rows)

    for row in rows:
        metadata = json.loads(Path(row["metadata_path"]).read_text(encoding="utf-8"))
        assert metadata["root_selection_log"]["source_generator"] == "assets/strict_visual_matched_cases_V55_lsystem_branch_elongated_saddle_yfork_20260511.py"
        assert "v55_lsystem_branch_naturalization_contract" in metadata
        assert "v54_lsystem_branch_naturalization_contract" not in metadata
        controls = metadata["controls"]
        assert controls["v55_lsystem_branch_elongated_saddle_yfork_naturalization"] is True
        assert controls["v54_lsystem_branch_centered_bough_yfork_naturalization"] is False
        assert controls["mask_scope"] == "object_space_elongated_saddle_yfork_bands_only"
        assert controls["terminal_radius_shrink"] <= 0.10
        assert controls["tip_parent_radius_shrink"] <= 0.26
        assert controls["implicit_grid_resolution"] >= 224
        assert 0.54 <= controls["gaussian_sigma"] <= 0.58
        assert 0.42 <= controls["implicit_field_level"] <= 0.43
        assert controls["terminal_sleeve_count"] == 0
        assert controls["terminal_bud_count"] == 0
        assert controls["direct_axis_sleeve_count"] == 0
        assert controls["sdedit_seam_backprojection_available"] is False
        assert "V55 lowers terminal field floors" in controls["hard_tube_cap_mitigation"]

    zdata = json.loads(zoom_manifest.read_text(encoding="utf-8"))
    assert len(zdata["cases"]) == 4
    assert all(item["detail_target_source"] == "v55_lsystem_explicit_elongated_saddle_yfork_mask" for item in zdata["cases"])
    assert all(2.05 <= item["zoom_divisor"] <= 2.35 for item in zdata["cases"])


def test_v55_launcher_uses_two_default_gpu4567_and_project_cache():
    text = LAUNCHER.read_text(encoding="utf-8")
    assert 'RUN="${RUN:-strict_visual_matched_texture_V55_lsystem_branch_elongated_saddle_yfork_naturalization_20260511}"' in text
    assert 'INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_V55_lsystem_branch_elongated_saddle_yfork_20260511}"' in text
    assert "for gpu in ${V55_GPUS:-4 5}" in text
    assert "4|5|6|7" in text
    assert 'TMPDIR="$ROOT/cache/local_tmp/$RUN"' in text
    assert 'TORCH_HOME="$ROOT/cache/torch"' in text
    assert 'TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"' in text
    assert "/tmp" not in text
    assert "/dev/shm" not in text
    assert "strict_visual_matched_cases_V55_lsystem_branch_elongated_saddle_yfork_20260511.py" in text
