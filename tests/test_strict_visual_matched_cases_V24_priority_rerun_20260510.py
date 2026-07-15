import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_V24_priority_rerun_20260510.py"
LAUNCHER = ROOT / "assets" / "launch_strict_visual_matched_texture_V24_priority_rerun_20260510.sh"
DOC = ROOT / "docs" / "evaluation" / "strict_visual_matched_V24_priority_rerun_plan_zh_20260510.md"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_V24_priority_rerun_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v24_priority_rerun_materializes_root_sc_first_manifest_and_metrics(tmp_path):
    mod = load_module()

    summary = mod.materialize(ROOT, tmp_path, seed=20260510)

    assert summary["num_cases"] == 15
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["surface_generator"] == "strict_visual_matched_cases_V24_priority_rerun"
    assert summary["mesh_input_policy"] == "obj_mesh_inputs_only"
    assert summary["connectivity_gate"]["largest_component_vertex_ratio_min"] == 0.999
    assert summary["connectivity_gate"]["boundary_tag_allowed"] is True
    assert summary["do_not_launch_remote"] is True
    assert summary["storage_risk"]["expected_upper_bound_gb"] <= 64

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

    assert len(rows) == 15
    assert all(row["case_id"].startswith("V24_") for row in rows)
    assert {row["family"] for row in rows} == {"L-system", "Space colonization", "DLA/frontier", "IFS/transform"}
    assert {int(row["gpu_group"]) for row in rows} == {4, 5, 6, 7}
    assert all(row["strict_one_to_one"] == "true" for row in rows)
    assert all(row["generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_postprocessing" for row in rows)
    assert all(row["mesh_input_policy"] == "obj_mesh_inputs_only" for row in rows)
    assert all(row["mesh_pbr_policy"] == "obj_inputs_and_pbr_guides_for_trellis2_glb_export" for row in rows)
    assert all(row["surface_strategy"] == "v24_priority_root_sc_rerun_with_dla_ifs_polish" for row in rows)
    assert all(row["block_or_token_stamping"] == "false" for row in rows)
    assert all(float(row["pre_export_lcr_gate"]) == 0.999 for row in rows)
    assert all(row["pre_export_gate_or_boundary"] in {"lcr>=0.999", "boundary_tag"} for row in rows)
    assert all(row["root_variant"] for row in rows)
    assert all(row["grammar_guide"] for row in rows)
    assert all(row["parameter_variant"] for row in rows)
    assert all(row["rerun_reason"] for row in rows)

    family_counts = {}
    priority_counts = {}
    for row in rows:
        family_counts[row["family"]] = family_counts.get(row["family"], 0) + 1
        priority_counts[row["qa_priority"]] = priority_counts.get(row["qa_priority"], 0) + 1
    assert family_counts == {
        "L-system": 4,
        "Space colonization": 6,
        "DLA/frontier": 3,
        "IFS/transform": 2,
    }
    assert priority_counts["root_quality"] == 6
    assert priority_counts["visual_quality"] == 4
    assert priority_counts["visual_polish"] == 4
    assert priority_counts["boundary_visual_polish"] == 1

    expected_cases = {
        "V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA",
        "V24_lsys_root_fan_d5_dense_rootlets_anchorB_seedB",
        "V24_lsys_root_fan_d5_smooth_rootlets_anchorA_seedA",
        "V24_lsys_root_fan_d5_smooth_rootlets_anchorB_seedB",
        "V24_sc_root_network_260_anchorA_seedA",
        "V24_sc_root_network_260_anchorB_seedB",
        "V24_sc_tree_crown_260_attractor_clean_seedA",
        "V24_sc_tree_crown_260_attractor_clean_seedB",
        "V24_sc_tree_crown_260_sparse_kill_clean_seedA",
        "V24_sc_tree_crown_260_sparse_kill_clean_seedB",
        "V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA",
        "V24_dla_frontier_sheet_700_open_boundary_polish_seedA",
        "V24_dla_coral_cluster_900_lace_porosity_boundary_seedA",
        "V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA",
        "V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA",
    }
    assert {row["case_id"] for row in rows} == expected_cases

    boundary_rows = [row for row in rows if row["boundary_tag"]]
    assert [row["case_id"] for row in boundary_rows] == ["V24_dla_coral_cluster_900_lace_porosity_boundary_seedA"]
    assert boundary_rows[0]["pre_export_gate_or_boundary"] == "boundary_tag"

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

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["case_id"] == row["case_id"]
        assert metadata["remote_constraints"]["allowed_gpus"] == [4, 5, 6, 7]
        assert metadata["mesh_pbr_contract"]["input_mesh_format"] == "obj"
        assert metadata["mesh_pbr_contract"]["obj_mesh_inputs_only"] is True
        assert metadata["mesh_pbr_contract"]["pbr_textured_glb_required"] is True
        assert metadata["root_selection_log"]["source_generator"] == "assets/strict_visual_matched_cases_V24_priority_rerun_20260510.py"
        assert metadata["rerun_reason"] == row["rerun_reason"]
        assert metadata["qa_priority"] == row["qa_priority"]
        assert metadata["v24_remote_cache_policy"]["cache_root"].endswith("/cache")
        assert metadata["v24_remote_cache_policy"]["no_system_tmp"] is True

        controls = metadata["controls"]
        assert controls["mesh_input_format"] == "obj"
        assert controls["v24_priority_rerun"] is True
        assert controls["connectivity_gate_lcr_min"] == 0.999
        assert controls["low_poly_block_stamping"] is False
        assert controls["mesh_token_stamping"] is False

        m = metrics_by_case[row["case_id"]]
        assert m["vertices"] > 1400
        assert m["faces"] > 2400
        assert m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["surface_area"] > 0.0
        assert m["support_edge_count"] >= 20
        assert m["semantic_detail_count"] >= 24
        assert m["low_poly_block_stamping"] is False
        assert m["mesh_token_stamping"] is False

    with (tmp_path / "manifest.csv").open(encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(csv_rows) == len(rows)
    assert {row["case_id"] for row in csv_rows} == expected_cases

    all_lines = (tmp_path / "a100-2_cases.txt").read_text(encoding="utf-8").strip().splitlines()
    assert len(all_lines) == len(rows)
    for gpu in (4, 5, 6, 7):
        gpu_lines = (tmp_path / f"gpu{gpu}_cases.txt").read_text(encoding="utf-8").strip().splitlines()
        assert len(gpu_lines) in {3, 4}
        assert all(line.endswith(f"|{gpu}") for line in gpu_lines)


def test_v24_launcher_is_generate_only_safe_uses_gpu4567_and_project_cache():
    text = LAUNCHER.read_text(encoding="utf-8")

    assert 'ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"' in text
    assert 'RUN="${RUN:-strict_visual_matched_texture_V24_priority_rerun_20260510}"' in text
    assert 'INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_V24_priority_rerun_20260510}"' in text
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
    assert "nohup bash" in text
    assert "strict_visual_matched_cases_V24_priority_rerun_20260510.py" in text


def test_v24_plan_documents_priority_cases_commands_and_boundaries():
    text = DOC.read_text(encoding="utf-8")
    assert "V24" in text
    assert "priority rerun" in text
    assert "root quality" in text
    assert "SC tree" in text
    assert "SC root" in text
    assert "DLA" in text
    assert "IFS" in text
    assert "GPU 4/5/6/7" in text
    assert "15" in text
    assert "generate-only" in text
    assert "不要启动远端" in text
    assert "OBJ" in text
    assert "LCR >= 0.999" in text
    assert "boundary tag" in text
    assert "V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA" in text
    assert "V24_sc_root_network_260_anchorA_seedA" in text
    assert "V24_dla_coral_cluster_900_lace_porosity_boundary_seedA" in text
