import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_v17_plants_roots_20260510.py"
LAUNCHER = ROOT / "assets" / "launch_strict_visual_matched_texture_v17_plants_roots_20260510.sh"
PLAN = ROOT / "docs" / "evaluation" / "strict_visual_matched_v17_root_source_plan_zh_20260510.md"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_v17_plants_roots_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v17_materializes_six_strict_visual_matched_plant_inputs_with_source_provenance(tmp_path):
    mod = load_module()

    summary = mod.materialize(ROOT, tmp_path, seed=20260510)

    assert summary["num_cases"] == 6
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["storage_root"] == "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
    assert summary["surface_generator"] == "visual_reference_seeded_connected_botanical_v17"
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
    }
    assert {row["traditional_target"] for row in rows} == expected_targets
    assert {row["family"] for row in rows} == {"L-system", "Space colonization"}
    assert {int(row["gpu_group"]) for row in rows} == {4, 5, 6, 7}
    assert all(row["case_id"].startswith("v17_") for row in rows)
    assert all(row["strict_one_to_one"] == "true" for row in rows)
    assert all(row["generation_policy"] == "generate_new_on_a100_2_no_local_cherrypick" for row in rows)
    assert all("DLA" not in row["family"] and "IFS" not in row["family"] for row in rows)

    required_operator_terms = {
        "same_classical_recursive_mode",
        "reference_seeded_root_source_strategy",
        "connected_swept_botanical_surface",
        "fused_branch_sleeve_envelope",
        "attached_pbr_surface_regions",
        "no_local_selection",
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
        assert "reference_seeded_root_source_strategy" in row["operator_composition"]
        assert "connected_swept_botanical_surface" in row["operator_composition"]
        assert "local_postprocess_repair" not in row["operator_composition"]
        assert row["controls"]
        assert row["why_matches_traditional"]

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["case_id"] == row["case_id"]
        assert metadata["traditional_target"] == row["traditional_target"]
        assert metadata["strict_generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_posthoc_pick"
        assert metadata["remote_constraints"]["machine"] == "a100-2"
        assert metadata["remote_constraints"]["allowed_gpus"] == [4, 5, 6, 7]
        assert metadata["root_selection_log"]["root_source_type"] == "v17_reference_seeded_botanical_input_generator"
        assert metadata["root_selection_log"]["source_generator"].endswith(
            "strict_visual_matched_cases_v17_plants_roots_20260510.py"
        )
        assert "visuals/textured_glb_20260508/tree_compete_s3/textured.glb" in metadata["root_selection_log"]["high_quality_source_references"]
        assert "visuals/programmatic_pbr_renders_20260508/tree_auto_iso.png" in metadata["root_selection_log"]["high_quality_source_references"]
        assert metadata["traditional_alignment"]["same_category"] is True
        assert metadata["traditional_alignment"]["same_recursive_mode"]
        assert set(metadata["operators"]) >= required_operator_terms

        controls = metadata["controls"]
        assert controls["same_classical_task_mode"] is True
        assert controls["connected_swept_botanical_surface"] is True
        assert controls["reference_seeded_root_source_strategy"] is True
        assert controls["mesh_pbr_output_only"] is True
        assert controls["direct_voxel_blocks"] is False
        assert controls["grape_ball_primitives"] == 0
        assert controls["rod_scaffold_only"] is False
        assert controls["local_selection_or_postprocess"] is False
        assert controls["fused_branch_sleeve_count"] >= 30
        assert controls["pbr_surface_region_count"] >= 18
        assert controls["root_source_anchor_count"] >= 1
        assert "reference-seeded" in controls["surface_strategy"]

        contract = metadata["visual_readability_contract"]
        assert "single main component" in contract["dryrun_visual_floor"]
        assert "V15/V6" in contract["failure_addressed"]
        assert "rod" in contract["negative_constraint"]
        assert "proxy" in contract["negative_constraint"]
        assert "botanical" in contract["positive_constraint"]

        m = metric_by_case[row["case_id"]]
        assert m["vertices"] > 1400
        assert m["faces"] > 2500
        assert m["mesh_component_count"] == 1 or m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["surface_area"] > 0.0
        assert m["fused_branch_sleeve_count"] >= 30
        assert m["pbr_surface_region_count"] >= 18

    root_rows = [row for row in rows if "root" in row["traditional_target"]]
    assert len(root_rows) == 2
    for row in root_rows:
        root_meta = json.loads(Path(row["metadata_path"]).read_text(encoding="utf-8"))
        assert root_meta["controls"]["connected_root_hairs"] >= 80
        assert root_meta["controls"]["root_source_anchor_count"] >= 4
        assert "root" in root_meta["visual_readability_contract"]["positive_constraint"]

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


def test_v17_launcher_and_plan_record_remote_first_gpu4567_constraints_and_chinese_provenance():
    text = LAUNCHER.read_text(encoding="utf-8")

    assert 'ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"' in text
    assert 'RUN="${RUN:-strict_visual_matched_texture_v17_plants_roots_20260510}"' in text
    assert 'INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_v17_plants_roots_20260510}"' in text
    assert "for gpu in 4 5 6 7" in text
    assert "--worker" in text
    assert 'CUDA_VISIBLE_DEVICES="$gpu"' in text
    assert 'DINO="$ROOT/weights/dinov3_transformers/facebook_dinov3_vitl16_pretrain_lvd1689m_local"' in text
    assert 'TMPDIR="$ROOT/cache/tmp"' in text
    assert 'TORCH_HOME="$ROOT/cache/torch"' in text
    assert 'TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"' in text
    assert '="/tmp' not in text
    assert " /tmp" not in text
    assert "/dev/shm" not in text
    assert '"status": "ok"' in text
    assert "--texture-size \"$tex\"" in text

    plan = PLAN.read_text(encoding="utf-8")
    assert "V17" in plan
    assert "根/源策略" in plan
    assert "一对一" in plan
    assert "不是本地筛选" in plan
    assert "visuals/textured_glb_20260508/tree_compete_s3/textured.glb" in plan
    assert "visuals/textured_glb_20260508/vine_d5_compete_s5_inference/textured.glb" in plan
    assert "visuals/public_guide_textured_glb_20260509/tree_compete_d4_pruned_tree_roots_steps8_tex2048_xformers/textured.glb" in plan
    assert "visuals/programmatic_pbr_renders_20260508/tree_auto_iso.png" in plan
    assert "visuals/programmatic_pbr_renders_20260508/vine_auto_iso.png" in plan
