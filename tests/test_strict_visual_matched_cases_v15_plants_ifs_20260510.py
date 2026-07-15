import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_v15_plants_ifs_20260510.py"
LAUNCHER = ROOT / "assets" / "launch_strict_visual_matched_texture_v15_plants_ifs_20260510.sh"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_v15_plants_ifs_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v15_materializes_plants_roots_and_ifs_with_strict_connectivity_gates(tmp_path):
    mod = load_module()

    summary = mod.materialize(ROOT, tmp_path, seed=20260510)

    assert summary["num_cases"] == 9
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["storage_root"] == "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
    assert summary["surface_generator"] == "smooth_connected_plants_roots_ifs_v15"
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
        "lsys_pine_canopy_d5",
        "lsys_root_fan_d5",
        "lsys_climbing_vine_d6",
        "sc_tree_crown_260",
        "sc_root_network_260",
        "sc_bush_shell_220",
        "ifs_branch_tree_d6",
        "ifs_radial_ornament_o8_d4",
        "ifs_fractal_lattice_d4",
    }
    assert {row["traditional_target"] for row in rows} == expected_targets
    assert {row["family"] for row in rows} == {"L-system", "Space colonization", "IFS/transform"}
    assert {int(row["gpu_group"]) for row in rows} == {4, 5, 6, 7}
    assert all(row["case_id"].startswith("v15_") for row in rows)
    assert all(row["strict_one_to_one"] == "true" for row in rows)
    assert all(row["generation_policy"] == "generate_new_on_a100_2_no_local_cherrypick" for row in rows)
    assert all("DLA" not in row["family"] for row in rows)

    for row in rows:
        obj_path = Path(row["mesh_path"])
        metadata_path = Path(row["metadata_path"])
        guide_path = Path(row["guide_image"])
        assert obj_path.exists()
        assert obj_path.suffix == ".obj"
        assert metadata_path.exists()
        assert guide_path.exists()
        assert guide_path.suffix == ".png"
        assert "smooth_connected_support" in row["operator_composition"]
        assert "no_rod_scaffold" in row["operator_composition"]
        assert row["controls"]
        assert row["why_matches_traditional"]

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["case_id"] == row["case_id"]
        assert metadata["traditional_target"] == row["traditional_target"]
        assert metadata["strict_generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_posthoc_pick"
        assert metadata["remote_constraints"]["machine"] == "a100-2"
        assert metadata["remote_constraints"]["allowed_gpus"] == [4, 5, 6, 7]
        assert metadata["root_selection_log"]["root_source_type"] == "v15_smooth_connected_plants_ifs_input_generator"
        assert metadata["root_selection_log"]["source_generator"].endswith(
            "strict_visual_matched_cases_v15_plants_ifs_20260510.py"
        )
        assert metadata["traditional_alignment"]["same_category"] is True
        assert metadata["traditional_alignment"]["same_recursive_mode"]

        controls = metadata["controls"]
        assert controls["smooth_connected_support"] is True
        assert controls["connectivity_gate_lcr_min"] == 0.999
        assert controls["tapered_branch_edges"] >= 24
        assert controls["direct_voxel_blocks"] is False
        assert controls["grape_ball_primitives"] == 0
        assert controls["rod_scaffold_only"] is False
        assert controls["attached_detail_primitives"] >= 18
        assert "attached" in controls["surface_strategy"]

        contract = metadata["visual_readability_contract"]
        assert "single main component" in contract["dryrun_visual_floor"]
        assert "grape-like balls" in contract["negative_constraint"]
        assert "pure rod scaffold" in contract["negative_constraint"]
        assert "smooth connected support" in contract["positive_constraint"]

        m = metric_by_case[row["case_id"]]
        assert m["vertices"] > 900
        assert m["faces"] > 1500
        assert m["mesh_component_count"] == 1 or m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["surface_area"] > 0.0
        assert m["tapered_branch_edges"] >= 24
        assert m["attached_detail_primitives"] >= 18

    radial = next(row for row in rows if row["traditional_target"] == "ifs_radial_ornament_o8_d4")
    radial_meta = json.loads(Path(radial["metadata_path"]).read_text(encoding="utf-8"))
    assert radial_meta["controls"]["bridged_ring_count"] >= 4
    assert radial_meta["controls"]["small_bridge_count"] >= 24

    lattice = next(row for row in rows if row["traditional_target"] == "ifs_fractal_lattice_d4")
    lattice_meta = json.loads(Path(lattice["metadata_path"]).read_text(encoding="utf-8"))
    assert lattice_meta["controls"]["small_bridge_count"] >= 28
    assert "small copy bridges" in lattice_meta["visual_readability_contract"]["positive_constraint"]

    root_rows = [row for row in rows if "root" in row["traditional_target"]]
    assert len(root_rows) == 2
    for row in root_rows:
        root_meta = json.loads(Path(row["metadata_path"]).read_text(encoding="utf-8"))
        assert root_meta["controls"]["connected_root_hairs"] >= 40

    with (tmp_path / "manifest.csv").open(encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(csv_rows) == len(rows)
    assert {row["case_id"] for row in csv_rows} == {row["case_id"] for row in rows}

    all_lines = (tmp_path / "a100-2_cases.txt").read_text(encoding="utf-8").strip().splitlines()
    assert len(all_lines) == len(rows)
    for gpu in (4, 5, 6, 7):
        gpu_lines = (tmp_path / f"gpu{gpu}_cases.txt").read_text(encoding="utf-8").strip().splitlines()
        assert gpu_lines
        assert all(line.endswith(f"|{gpu}") for line in gpu_lines)


def test_v15_launcher_uses_remote_gpu4567_cache_layout_and_skip_ok_summaries():
    text = LAUNCHER.read_text(encoding="utf-8")

    assert 'ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"' in text
    assert 'RUN="${RUN:-strict_visual_matched_texture_v15_plants_ifs_20260510}"' in text
    assert 'INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_v15_plants_ifs_20260510}"' in text
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
