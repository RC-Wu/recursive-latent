import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_V21_ifs_transform_natural_20260510.py"
LAUNCHER = ROOT / "assets" / "launch_strict_visual_matched_texture_V21_ifs_transform_natural_20260510.sh"
DOC = ROOT / "docs" / "evaluation" / "strict_visual_matched_V21_ifs_transform_natural_zh_20260510.md"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_V21_ifs_transform_natural_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v21_materializes_strict_ifs_transform_inputs_with_lcr_gate(tmp_path):
    mod = load_module()

    summary = mod.materialize(ROOT, tmp_path, seed=20260510)

    assert summary["num_cases"] >= 7
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["surface_generator"] == "strict_ifs_transform_natural_mesh_v21"
    assert summary["mesh_input_policy"] == "obj_mesh_inputs_only"
    assert summary["mesh_pbr_policy"] == "mesh_and_pbr_outputs_only"
    assert summary["connectivity_gate"]["largest_component_vertex_ratio_min"] == 0.999
    assert summary["v21_focus"] == "IFS transform radial lattice strict one-to-one natural mesh branch"

    for name in ("manifest.csv", "manifest.json", "initial_metrics.csv", "initial_metrics.json", "a100-2_cases.txt", "gpu4567_cases.txt", "README.md", "summary.json"):
        assert (tmp_path / name).exists()
    for gpu in (4, 5, 6, 7):
        assert (tmp_path / f"gpu{gpu}_cases.txt").exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((tmp_path / "initial_metrics.json").read_text(encoding="utf-8"))
    metric_by_case = {row["case_id"]: row for row in metrics}

    assert {int(row["gpu_group"]) for row in rows} == {4, 5, 6, 7}
    assert all(row["case_id"].startswith("V21_") for row in rows)
    assert all(row["family"] == "IFS/transform" for row in rows)
    assert all(row["strict_one_to_one"] == "true" for row in rows)
    assert all(row["generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_postprocessing" for row in rows)
    assert all(row["mesh_input_policy"] == "obj_mesh_inputs_only" for row in rows)
    assert all(row["mesh_pbr_policy"] == "mesh_and_pbr_outputs_only" for row in rows)

    expected_targets = {
        "ifs_branch_tree_d6",
        "ifs_radial_ornament_o12_d5",
        "ifs_pyrite_lattice_transform_d4",
        "ifs_bismuth_stepped_transform_d5",
        "ifs_escher_recursive_stair_loop_d4",
        "transform_compat_positive_affine_stack_d4",
        "transform_compat_negative_axis_mismatch_d4",
    }
    assert expected_targets <= {row["traditional_target"] for row in rows}

    expected_motifs = {
        "fractal_branch_ifs_tree",
        "radial_ornament",
        "pyrite_lattice_transform",
        "bismuth_stepped_transform",
        "escher_recursive_stair_loop",
        "transform_compat_positive",
        "transform_compat_negative",
    }
    required_operator_terms = {
        "affine_transform_grammar",
        "recursive_copy_depth_schedule",
        "strict_traditional_target_mapping",
        "shared_vertex_connected_support",
        "attached_natural_mesh_detail",
        "obj_mesh_input_only",
        "pbr_material_prompt",
        "largest_component_gate",
    }
    seen_motifs = set()
    compatibility_labels = set()

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
        assert "local_postprocess" not in row["operator_composition"]
        assert "selection" not in row["operator_composition"]

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["strict_generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_postprocessing"
        assert metadata["remote_constraints"]["machine"] == "a100-2"
        assert metadata["remote_constraints"]["allowed_gpus"] == [4, 5, 6, 7]
        assert metadata["mesh_pbr_contract"]["mesh_outputs_only"] is True
        assert metadata["mesh_pbr_contract"]["input_mesh_format"] == "obj"
        assert metadata["mesh_pbr_contract"]["obj_mesh_inputs_only"] is True
        assert metadata["mesh_pbr_contract"]["pbr_textured_glb_required"] is True
        assert metadata["mesh_pbr_contract"]["forbidden_outputs"] == ["local_selected_render", "2d_only_image", "posthoc_repair_mesh", "non_obj_mesh_input"]
        assert metadata["root_selection_log"]["root_source_type"] == "V21_strict_ifs_transform_natural_input_generator"
        assert metadata["traditional_alignment"]["same_category"] is True
        assert metadata["traditional_alignment"]["strict_one_to_one_comparison"] is True
        assert set(metadata["operators"]) >= required_operator_terms
        assert "ifs" in metadata["grammar_mapping"]["grammar_family"].lower()
        assert metadata["grammar_mapping"]["target_symbol"]
        assert metadata["grammar_mapping"]["operator_to_traditional_mapping"]
        assert metadata["grammar_mapping"]["remote_comparison_unit"] == "one generated OBJ input to one traditional target"

        controls = metadata["controls"]
        seen_motifs.add(controls["semantic_motif"])
        compatibility_labels.add(controls["transform_compatibility_label"])
        assert controls["mesh_input_format"] == "obj"
        assert controls["connected_support"] is True
        assert controls["connectivity_gate_lcr_min"] == 0.999
        assert controls["shared_vertex_anchor_count"] >= 8
        assert controls["recursive_depth"] >= 4
        assert controls["affine_transform_count"] >= 2
        assert controls["attached_natural_mesh_detail_count"] >= 24
        assert controls["direct_voxel_blocks"] is False
        assert controls["detached_chunk_policy"] == "forbid_detached_transform_islands_by_shared_support_faces"

        contract = metadata["visual_readability_contract"]
        assert "IFS" in contract["positive_constraint"]
        assert "radial" in contract["positive_constraint"]
        assert "lattice" in contract["positive_constraint"]
        assert "bismuth" in contract["positive_constraint"]
        assert "OBJ" in contract["dryrun_visual_floor"]
        assert "detached transform islands" in contract["negative_constraint"]

        m = metric_by_case[row["case_id"]]
        assert m["vertices"] > 1400
        assert m["faces"] > 2400
        assert m["mesh_component_count"] == 1 or m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["surface_area"] > 0.0
        assert m["attached_natural_mesh_detail_count"] >= 24
        assert m["shared_vertex_anchor_count"] >= 8

    assert expected_motifs <= seen_motifs
    assert {"positive", "negative"} <= compatibility_labels

    negative = next(row for row in rows if row["traditional_target"] == "transform_compat_negative_axis_mismatch_d4")
    negative_meta = json.loads(Path(negative["metadata_path"]).read_text(encoding="utf-8"))
    assert negative_meta["transform_compatibility"]["expected_compatible"] is False
    assert "negative control" in negative_meta["transform_compatibility"]["comparison_role"]

    positive = next(row for row in rows if row["traditional_target"] == "transform_compat_positive_affine_stack_d4")
    positive_meta = json.loads(Path(positive["metadata_path"]).read_text(encoding="utf-8"))
    assert positive_meta["transform_compatibility"]["expected_compatible"] is True
    assert positive_meta["controls"]["compatible_transform_stack"] is True

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


def test_v21_launcher_uses_gpu4567_project_cache_obj_mesh_and_pbr_glb_export_only():
    text = LAUNCHER.read_text(encoding="utf-8")

    assert 'ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"' in text
    assert 'RUN="${RUN:-strict_visual_matched_texture_V21_ifs_transform_natural_20260510}"' in text
    assert 'INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_V21_ifs_transform_natural_20260510}"' in text
    assert "for gpu in 4 5 6 7" in text
    assert "--worker" in text
    assert 'CUDA_VISIBLE_DEVICES="$gpu"' in text
    assert 'TMPDIR="$ROOT/cache/local_tmp"' in text
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


def test_v21_chinese_doc_explains_ifs_transform_grammar_mapping_and_strict_obj_policy():
    text = DOC.read_text(encoding="utf-8")
    assert "V21" in text
    assert "IFS" in text
    assert "transform" in text
    assert "radial" in text
    assert "lattice" in text
    assert "pyrite" in text
    assert "bismuth" in text
    assert "Escher" in text
    assert "OBJ" in text
    assert "LCR >= 0.999" in text
    assert "严格一对一" in text
    assert "正/负" in text
    assert "mesh/PBR" in text
