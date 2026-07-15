import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_V20_paper_coral_crystal_20260510.py"
LAUNCHER = ROOT / "assets" / "launch_strict_visual_matched_texture_V20_paper_coral_crystal_20260510.sh"
DOC = ROOT / "docs" / "evaluation" / "strict_visual_matched_V20_paper_coral_crystal_zh_20260510.md"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_V20_paper_coral_crystal_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v20_materializes_paper_coral_crystal_strict_inputs(tmp_path):
    mod = load_module()

    summary = mod.materialize(ROOT, tmp_path, seed=20260510)

    assert summary["num_cases"] == 8
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["surface_generator"] == "paper_coral_crystal_semantics_v20"
    assert summary["mesh_pbr_policy"] == "mesh_and_pbr_outputs_only"
    assert summary["connectivity_gate"]["largest_component_vertex_ratio_min"] == 0.999
    assert summary["v20_supersedes"] == "V18 connectivity plus stronger coral calyx/polyp and crystal facet/terrace semantics"

    for name in ("manifest.csv", "manifest.json", "initial_metrics.csv", "initial_metrics.json", "a100-2_cases.txt", "gpu4567_cases.txt", "README.md", "summary.json"):
        assert (tmp_path / name).exists()
    for gpu in (4, 5, 6, 7):
        assert (tmp_path / f"gpu{gpu}_cases.txt").exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((tmp_path / "initial_metrics.json").read_text(encoding="utf-8"))
    metric_by_case = {row["case_id"]: row for row in metrics}

    assert {int(row["gpu_group"]) for row in rows} == {4, 5, 6, 7}
    assert all(row["case_id"].startswith("V20_dla_") for row in rows)
    assert all(row["strict_one_to_one"] == "true" for row in rows)
    assert all(row["generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_postprocessing" for row in rows)
    assert all(row["mesh_pbr_policy"] == "mesh_and_pbr_outputs_only" for row in rows)

    expected_motifs = {
        "staghorn_calyx_coral",
        "table_reef_plate",
        "branching_reef_loop_closure",
        "frontier_lace_sheet",
        "pyrite_cubic_crystal",
        "bismuth_stepped_crystal",
    }
    expected_targets = {
        "dla_staghorn_coral_900",
        "dla_table_coral_plate_760",
        "dla_branching_reef_loop_650",
        "dla_frontier_sheet_700",
        "dla_pyrite_cubic_crystal_520",
        "dla_bismuth_step_crystal_360",
    }
    assert expected_targets <= {row["traditional_target"] for row in rows}

    required_operator_terms = {
        "stochastic_frontier_attachment",
        "occupancy_exclusion",
        "rooted_attachment_bridges",
        "loop_closure_bridges",
        "connected_implicit_support",
        "paper_semantic_surface_primitives",
        "coral_calyx_or_crystal_facet_guides",
        "pbr_material_prompt",
        "largest_component_gate",
    }
    seen_motifs = set()
    for row in rows:
        obj_path = Path(row["mesh_path"])
        metadata_path = Path(row["metadata_path"])
        guide_path = Path(row["guide_image"])
        assert obj_path.exists()
        assert obj_path.suffix == ".obj"
        assert metadata_path.exists()
        assert guide_path.exists()
        assert guide_path.suffix == ".png"
        assert "local_postprocess" not in row["operator_composition"]
        assert "selection" not in row["operator_composition"]

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["strict_generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_postprocessing"
        assert metadata["remote_constraints"]["machine"] == "a100-2"
        assert metadata["remote_constraints"]["allowed_gpus"] == [4, 5, 6, 7]
        assert metadata["mesh_pbr_contract"]["mesh_outputs_only"] is True
        assert metadata["mesh_pbr_contract"]["pbr_textured_glb_required"] is True
        assert metadata["mesh_pbr_contract"]["forbidden_outputs"] == ["local_selected_render", "2d_only_image", "posthoc_repair_mesh"]
        assert metadata["root_selection_log"]["root_source_type"] == "V20_paper_coral_crystal_input_generator"
        assert metadata["traditional_alignment"]["same_category"] is True
        assert metadata["traditional_alignment"]["strict_one_to_one_comparison"] is True
        assert set(metadata["operators"]) >= required_operator_terms

        controls = metadata["controls"]
        seen_motifs.add(controls["semantic_motif"])
        assert controls["connected_implicit_support"] is True
        assert controls["bridge_root_connectivity"] is True
        assert controls["attachment_bridge_count"] >= 12
        assert controls["loop_closure_bridge_count"] >= 6
        assert controls["naturalization_detail_count"] >= 64
        assert controls["paper_semantic_upgrade_over_v18"] is True
        assert controls["direct_voxel_blocks"] is False
        assert controls["direct_straight_rods"] is False
        assert controls["detached_chunk_policy"] == "forbid_detached_chunks_by_overlapping_primitives_before_marching_cubes"
        assert controls["largest_component_vertex_ratio_min"] == 0.999
        if controls["semantic_domain"] == "coral":
            assert controls["calyx_polyp_count"] >= 96
            assert controls["rounded_porous_reef_surface"] is True
            assert controls["flat_rod_cut_policy"] == "forbid_flat_rod_cuts"
        if controls["semantic_domain"] == "crystal":
            assert controls["facet_plate_count"] >= 72
            assert controls["stepped_terrace_or_cubic_symmetry"] is True
            assert controls["smooth_blob_policy"] == "forbid_smooth_crystal_blobs"

        contract = metadata["visual_readability_contract"]
        assert "staghorn coral" in contract["positive_constraint"]
        assert "table coral" in contract["positive_constraint"]
        assert "pyrite" in contract["positive_constraint"]
        assert "bismuth" in contract["positive_constraint"]
        assert "textured organic branches/sheets" in contract["negative_constraint"]
        assert "flat rod cuts" in contract["negative_constraint"]

        m = metric_by_case[row["case_id"]]
        assert m["vertices"] > 2200
        assert m["faces"] > 4400
        assert m["mesh_component_count"] == 1 or m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["largest_mesh_component_vertex_ratio"] >= 0.999
        assert m["surface_area"] > 0.0
        assert m["attachment_bridge_count"] >= 12
        assert m["loop_closure_bridge_count"] >= 6
        assert m["naturalization_detail_count"] >= 64

    assert expected_motifs <= seen_motifs

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


def test_v20_launcher_uses_gpu4567_project_cache_and_pbr_glb_export_only():
    text = LAUNCHER.read_text(encoding="utf-8")

    assert 'ROOT="${ROOT:-/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507}"' in text
    assert 'RUN="${RUN:-strict_visual_matched_texture_V20_paper_coral_crystal_20260510}"' in text
    assert 'INPUT_NAME="${INPUT_NAME:-strict_visual_matched_cases_V20_paper_coral_crystal_20260510}"' in text
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


def test_v20_chinese_doc_explains_superseding_v18_and_strict_mapping():
    text = DOC.read_text(encoding="utf-8")
    assert "V20" in text
    assert "取代 V18" in text
    assert "严格一对一" in text
    assert "DLA/frontier/crystal" in text
    assert "mesh/PBR" in text
    assert "连通" in text
    assert "staghorn" in text
    assert "pyrite" in text
    assert "bismuth" in text
