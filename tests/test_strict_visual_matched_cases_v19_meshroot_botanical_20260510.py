import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_V19_meshroot_botanical_20260510.py"
LAUNCHER = ROOT / "assets" / "launch_strict_visual_matched_texture_V19_meshroot_botanical_20260510.sh"
DOC = ROOT / "docs" / "evaluation" / "strict_visual_matched_V19_meshroot_botanical_zh_20260510.md"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_V19_meshroot_botanical_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v19_materializes_strict_meshroot_botanical_cases_with_connectivity_metadata(tmp_path):
    mod = load_module()

    summary = mod.materialize(ROOT, tmp_path, seed=20260510)

    assert summary["num_cases"] == 6
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["surface_generator"] == "real_glb_mesh_token_botanical_grammar_v19"
    assert summary["mesh_token_policy"] == "production_real_project_glbs_with_explicit_tiny_fallback"
    assert summary["connectivity_gate"]["largest_component_vertex_ratio_min"] == 0.999
    assert summary["mesh_pbr_policy"] == "obj_inputs_and_pbr_guides_for_trellis2_glb_export"

    for name in ("manifest.csv", "manifest.json", "initial_metrics.csv", "initial_metrics.json", "a100-2_cases.txt", "gpu4567_cases.txt", "README.md"):
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
    }
    assert {row["traditional_target"] for row in rows} == expected_targets
    assert {row["family"] for row in rows} == {"L-system", "Space colonization"}
    assert {int(row["gpu_group"]) for row in rows} == {4, 5, 6, 7}
    assert all(row["case_id"].startswith("v19_") for row in rows)
    assert all(row["strict_one_to_one"] == "true" for row in rows)
    assert all(row["generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_postprocessing" for row in rows)
    assert all(row["mesh_token_source"] == "real_project_glb" for row in rows)

    required_operator_terms = {
        "same_classical_recursive_mode",
        "real_glb_mesh_token_library",
        "grammar_skeleton_or_attractor_field",
        "oriented_mesh_token_stamping",
        "shared_vertex_support_bridge",
        "connected_botanical_support_sweep",
        "pbr_guide_output_for_trellis2",
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
        assert "real_glb_mesh_token_library" in row["operator_composition"]
        assert "shared_vertex_support_bridge" in row["operator_composition"]
        assert "procedural_rods_only" not in row["operator_composition"]
        assert row["why_matches_traditional"]

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["case_id"] == row["case_id"]
        assert metadata["traditional_target"] == row["traditional_target"]
        assert metadata["strict_generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_postprocessing"
        assert metadata["remote_constraints"]["machine"] == "a100-2"
        assert metadata["remote_constraints"]["allowed_gpus"] == [4, 5, 6, 7]
        assert metadata["mesh_pbr_contract"]["obj_input_required"] is True
        assert metadata["mesh_pbr_contract"]["pbr_textured_glb_required"] is True
        assert metadata["mesh_token_provenance"]["source_type"] == "real_project_glb"
        assert metadata["mesh_token_provenance"]["fallback_used"] is False
        assert len(metadata["mesh_token_provenance"]["source_glbs"]) >= 4
        assert "visuals/textured_glb_20260508/tree_compete_s3/textured.glb" in metadata["mesh_token_provenance"]["source_glbs"]
        assert "visuals/textured_glb_20260508/vine_d5_compete_s5_inference/textured.glb" in metadata["mesh_token_provenance"]["source_glbs"]
        assert "visuals/public_guide_textured_glb_20260509/tree_compete_d4_pruned_tree_roots_steps8_tex2048_xformers/textured.glb" in metadata["mesh_token_provenance"]["source_glbs"]
        assert "visuals/gen3d_baseline_texture_fairness_20260510/meshspace_genroot_vine_d2/textured.glb" in metadata["mesh_token_provenance"]["source_glbs"]
        assert metadata["traditional_alignment"]["same_category"] is True
        assert metadata["traditional_alignment"]["strict_one_to_one_comparison"] is True
        assert set(metadata["operators"]) >= required_operator_terms

        controls = metadata["controls"]
        assert controls["same_classical_task_mode"] is True
        assert controls["real_glb_mesh_token_library"] is True
        assert controls["oriented_mesh_token_stamping"] is True
        assert controls["connected_botanical_support_sweep"] is True
        assert controls["shared_vertex_support_bridge"] is True
        assert controls["mesh_pbr_output_only"] is True
        assert controls["procedural_rods_only"] is False
        assert controls["local_selection_or_postprocess"] is False
        assert controls["token_stamp_count"] >= 12
        assert controls["support_bridge_count"] >= controls["token_stamp_count"]
        assert controls["token_faces_per_stamp"] >= 120

        contract = metadata["visual_readability_contract"]
        assert "mesh tokens" in contract["positive_constraint"]
        assert "classical silhouette" in contract["positive_constraint"]
        assert "rod/card-only" in contract["negative_constraint"]
        assert "V17" in contract["failure_addressed"]

        m = metric_by_case[row["case_id"]]
        assert m["vertices"] > 1800
        assert m["faces"] > 3000
        assert m["mesh_component_count"] == 1 or m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["surface_area"] > 0.0
        assert m["token_stamp_count"] >= 12
        assert m["support_bridge_count"] >= m["token_stamp_count"]

    root_rows = [row for row in rows if "root" in row["traditional_target"]]
    assert len(root_rows) == 2
    for row in root_rows:
        root_meta = json.loads(Path(row["metadata_path"]).read_text(encoding="utf-8"))
        assert root_meta["controls"]["root_hair_count"] >= 80
        assert root_meta["controls"]["root_token_anchor_count"] >= 4
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


def test_v19_launcher_and_chinese_doc_record_remote_first_real_glb_provenance():
    text = LAUNCHER.read_text(encoding="utf-8")

    assert 'ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"' in text
    assert 'RUN="${RUN:-strict_visual_matched_texture_V19_meshroot_botanical_20260510}"' in text
    assert 'INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_V19_meshroot_botanical_20260510}"' in text
    assert "for gpu in 4 5 6 7" in text
    assert "--worker" in text
    assert 'CUDA_VISIBLE_DEVICES="$gpu"' in text
    assert 'TMPDIR="$ROOT/cache/tmp"' in text
    assert 'TORCH_HOME="$ROOT/cache/torch"' in text
    assert 'TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"' in text
    assert "/tmp/" not in text
    assert "TMPDIR=/tmp" not in text
    assert "/dev/shm" not in text
    assert '"status": "ok"' in text
    assert "--texture-size \"$tex\"" in text
    assert "--preprocess" in text
    assert "trellis2_texturing_export_glb.py" in text

    doc = DOC.read_text(encoding="utf-8")
    assert "V19" in doc
    assert "真实 GLB 网格 token" in doc
    assert "一对一" in doc
    assert "操作符组合" in doc
    assert "不是本地筛选" in doc
    assert "visuals/textured_glb_20260508/tree_compete_s3/textured.glb" in doc
    assert "visuals/textured_glb_20260508/vine_d5_compete_s5_inference/textured.glb" in doc
    assert "visuals/public_guide_textured_glb_20260509/tree_compete_d4_pruned_tree_roots_steps8_tex2048_xformers/textured.glb" in doc
    assert "visuals/gen3d_baseline_texture_fairness_20260510/meshspace_genroot_vine_d2/textured.glb" in doc
