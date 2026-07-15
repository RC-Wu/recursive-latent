import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_V43_lsystem_branch_wood_yfork_naturalization_20260511.py"
LAUNCHER = ROOT / "assets" / "launch_strict_visual_matched_texture_V43_lsystem_branch_wood_yfork_naturalization_20260511.sh"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_V43_lsystem_branch_wood_yfork_naturalization_20260511", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v43_lsystem_branch_materializes_wood_yfork_case_manifest_and_metrics(tmp_path):
    mod = load_module()

    summary = mod.materialize(ROOT, tmp_path, seed=20260511)

    assert summary["num_cases"] == 4
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["default_active_gpus"] == [4, 5]
    assert summary["max_simultaneous_remote_gpus"] == 2
    assert summary["storage_limit_gb"] == 200
    assert summary["surface_generator"] == "strict_visual_matched_cases_V43_lsystem_branch_wood_yfork_naturalization"
    assert summary["surface_strategy"] == "v43_lsystem_branch_wood_yfork_sidebranch_naturalization"
    assert summary["mesh_input_policy"] == "obj_mesh_inputs_only"
    assert summary["lsystem_branch_gate"]["match_target"] == "lsys_branch_side_d5"
    assert summary["lsystem_branch_gate"]["terminal_sleeves_required"] is False
    assert summary["lsystem_branch_gate"]["min_terminal_sleeves"] == 0
    assert summary["lsystem_branch_gate"]["junction_zoom_pair_min_distance"] >= mod.ZOOM_PAIR_MIN_DISTANCE
    assert summary["lsystem_branch_gate"]["min_junction_zoom_targets"] > 0
    assert summary["lsystem_branch_gate"]["min_saddle_necks"] >= 6
    assert summary["lsystem_branch_gate"]["min_terminal_forks"] >= 3
    assert summary["lsystem_branch_gate"]["min_wood_yfork_branches"] >= 3
    assert summary["lsystem_branch_gate"]["max_external_support_segment_after_subdivision"] <= 0.100001
    assert summary["do_not_launch_remote_before_local_visual_qa"] is True

    for name in (
        "manifest.csv",
        "manifest.json",
        "initial_metrics.csv",
        "initial_metrics.json",
        "a100-2_cases.txt",
        "gpu45_cases.txt",
        "README.md",
        "summary.json",
        "V43_obj_zoom_manifest_junctiontarget_20260511.json",
    ):
        assert (tmp_path / name).exists()
    for gpu in (4, 5, 6, 7):
        assert (tmp_path / f"gpu{gpu}_cases.txt").exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((tmp_path / "initial_metrics.json").read_text(encoding="utf-8"))
    metrics_by_case = {row["case_id"]: row for row in metrics}

    expected_cases = {
        "V43_lsys_branch_wood_yfork_A",
        "V43_lsys_branch_wood_yfork_lowfrag_B",
        "V43_lsys_branch_wood_yfork_dense_C",
        "V43_lsys_branch_wood_yfork_slim_D",
    }
    assert {row["case_id"] for row in rows} == expected_cases
    assert {row["family"] for row in rows} == {"L-system"}
    assert {row["match_target"] for row in rows} == {"lsys_branch_side_d5"}
    assert {int(row["gpu_group"]) for row in rows} == {4, 5}
    assert all(row["strict_one_to_one"] == "true" for row in rows)
    assert all(row["surface_strategy"] == "v43_lsystem_branch_wood_yfork_sidebranch_naturalization" for row in rows)
    assert all(row["block_or_token_stamping"] == "false" for row in rows)
    assert all(int(row["branch_junction_count"]) >= 4 for row in rows)
    assert all(int(row["saddle_neck_count"]) >= 6 for row in rows)
    assert all(int(row["wood_yfork_branch_count"]) >= 3 for row in rows)
    assert all(int(row["seam_mask_center_count"]) > 0 for row in rows)
    assert all(int(row["junction_zoom_target_count"]) > 0 for row in rows)
    assert all(int(row["junction_collar_count"]) > 0 for row in rows)
    assert all(int(row["terminal_fork_count"]) >= 4 for row in rows)
    assert all(int(row["terminal_sleeve_count"]) == 0 for row in rows)
    assert all(int(row["ridge_count"]) > 0 for row in rows)
    assert all(float(row["external_support_max_segment_after_subdivision"]) <= 0.100001 for row in rows)
    assert all(row["sdedit_seam_backprojection_available"] == "false" for row in rows)

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
        assert metadata["family"] == "L-system"
        assert metadata["remote_constraints"]["allowed_gpus"] == [4, 5, 6, 7]
        assert metadata["root_selection_log"]["source_generator"] == "assets/strict_visual_matched_cases_V43_lsystem_branch_wood_yfork_naturalization_20260511.py"
        assert metadata["v43_remote_cache_policy"]["cache_root"].endswith("/cache")
        assert metadata["v43_remote_cache_policy"]["no_system_tmp"] is True
        assert metadata["v43_remote_cache_policy"]["max_simultaneous_gpus"] == 2

        contract = metadata["v43_lsystem_branch_naturalization_contract"]
        assert contract["target_failure"].startswith("V35 remained connected")
        assert contract["seam_mask"]["space"] == "object_xyz"
        assert contract["zoom_targets"]["source"].startswith("wood-yfork")
        assert contract["zoom_targets"]["pair_count"] > 0
        assert contract["sdedit_seam_backprojection_available"] is False
        assert "no 2D seam inpaint backprojection claim" in contract["texture_operator"]

        controls = metadata["controls"]
        assert controls["v43_lsystem_branch_wood_yfork_naturalization"] is True
        assert controls["masked_local_naturalization_target"] == "L-system saddle-neck side-branch wood-yfork bands with wood-only tapered terminals"
        assert controls["mask_scope"] == "object_space_side_branch_saddle_wood_yfork_bands_only"
        assert controls["terminal_radius_shrink"] <= 0.26
        assert controls["tip_parent_radius_shrink"] <= 0.45
        assert controls["support_base_radius"] >= 0.028
        assert controls["support_radius_floor"] >= 0.005
        assert controls["saddle_neck_count"] > 0
        assert controls["terminal_fork_count"] >= 3
        assert controls["wood_yfork_branch_count"] >= 3
        assert len(controls["wood_yfork_anchor_indices"]) >= 2
        assert controls["terminal_sleeve_count"] == 0
        assert controls["terminal_bud_count"] == 0
        assert controls["junction_zoom_target_count"] > 0
        assert controls["junction_zoom_pair_count"] > 0
        assert controls["wood_yfork_zoom_pair_count"] >= 3
        assert controls["junction_zoom_pairs"][0] == controls["wood_yfork_zoom_pairs"][0]
        assert all(len(pair) == 2 for pair in controls["junction_zoom_pairs"])
        assert controls["short_segment_gate_pass"] is True
        assert controls["external_support_max_segment_after_subdivision"] <= 0.100001
        assert controls["sdedit_seam_backprojection_available"] is False
        assert controls["hard_tube_cap_mitigation"].startswith("wood-only twig continuation")

        m = metrics_by_case[row["case_id"]]
        assert m["vertices"] > 3200
        assert m["faces"] > 6200
        assert m["mesh_component_count"] == 1
        assert m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert 35 <= m["semantic_detail_count"] <= 180
        assert m["branch_junction_count"] >= 4
        assert m["saddle_neck_count"] > 0
        assert m["wood_yfork_branch_count"] >= 3
        assert m["terminal_fork_count"] >= 3
        assert m["terminal_sleeve_count"] == 0
        assert m["junction_zoom_target_count"] > 0

    with (tmp_path / "manifest.csv").open(encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(csv_rows) == len(rows)
    assert {row["case_id"] for row in csv_rows} == expected_cases

    zoom_manifest = json.loads((tmp_path / "V43_obj_zoom_manifest_junctiontarget_20260511.json").read_text(encoding="utf-8"))
    assert len(zoom_manifest["cases"]) == 4
    assert all(item["detail_target_source"] == "v43_lsystem_explicit_wood_yfork_mask" for item in zoom_manifest["cases"])
    for item in zoom_manifest["cases"]:
        assert item["zoom_divisor"] >= 3.0
        fixed = item["fixed_detail_targets"]
        assert len(fixed) == 2
        delta = sum((float(fixed[0][axis]) - float(fixed[1][axis])) ** 2 for axis in range(3)) ** 0.5
        assert delta >= mod.ZOOM_PAIR_MIN_DISTANCE


def test_v43_launcher_is_generate_only_safe_uses_two_default_gpu4567_and_project_cache():
    text = LAUNCHER.read_text(encoding="utf-8")

    assert 'ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"' in text
    assert 'RUN="${RUN:-strict_visual_matched_texture_V43_lsystem_branch_wood_yfork_naturalization_20260511}"' in text
    assert 'INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_V43_lsystem_branch_wood_yfork_naturalization_20260511}"' in text
    assert "for gpu in ${V43_GPUS:-4 5}" in text
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
    assert "strict_visual_matched_cases_V43_lsystem_branch_wood_yfork_naturalization_20260511.py" in text
