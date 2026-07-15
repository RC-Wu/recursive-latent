import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_V67_lsystem_branch_same_scaffold_tapered_twig_20260512.py"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_V67_lsystem_branch_same_scaffold_tapered_twig_20260512", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v67_same_scaffold_tapered_twig_materializes(tmp_path):
    mod = load_module()
    summary = mod.materialize(ROOT, tmp_path, seed=20260512)

    assert summary["num_cases"] == 4
    assert summary["surface_generator"] == "strict_visual_matched_cases_V67_lsystem_branch_same_scaffold_tapered_twig"
    assert summary["surface_strategy"] == "v67_lsystem_same_scaffold_tapered_twig_depth_density_matched"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["max_simultaneous_remote_gpus"] == 2
    assert summary["do_not_launch_remote_before_local_visual_qa"] is True
    assert summary["lsystem_branch_gate"]["same_scaffold_as_traditional_baseline"] is True
    assert summary["lsystem_branch_gate"]["source_segment_count"] == 1296
    assert summary["lsystem_branch_gate"]["min_branch_junctions"] >= 259
    assert summary["lsystem_branch_gate"]["min_terminal_count"] >= 598
    assert summary["lsystem_branch_gate"]["min_terminal_tip_count"] >= 598
    assert summary["lsystem_branch_gate"]["flat_terminal_caps_disabled"] is True
    assert summary["v67_design"]["generator_change_required"] is True

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert {row["case_id"] for row in rows} == {
        "V67_lsys_branch_tapered_twig_A",
        "V67_lsys_branch_tapered_dense_B",
        "V67_lsys_branch_tapered_fine_C",
        "V67_lsys_branch_tapered_soft_D",
    }
    assert {int(row["gpu_group"]) for row in rows} == {4, 5}
    assert all(row["surface_strategy"] == "v67_lsystem_same_scaffold_tapered_twig_depth_density_matched" for row in rows)
    assert all(row["case_role"] == "v67_lsystem_branch_same_scaffold_tapered_twig_naturalization" for row in rows)
    assert all(row["flat_terminal_caps_disabled"] == "true" for row in rows)
    assert all(row["sdedit_seam_backprojection_available"] == "false" for row in rows)
    assert all(int(row["branch_junction_count"]) >= 259 for row in rows)
    assert all(int(row["terminal_count"]) >= 598 for row in rows)
    assert all(int(row["terminal_tip_count"]) >= 598 for row in rows)

    for row in rows:
        controls = json.loads(row["controls"])
        assert controls["same_scaffold_as_traditional_baseline"] is True
        assert controls["flat_terminal_caps_disabled"] is True
        assert controls["graph_native_tapered_terminal_tips"] is True
        assert controls["source_cylinder_segments"] == 1296
        assert controls["branch_junction_count"] >= 259
        assert controls["terminal_count"] >= 598
        assert controls["terminal_tip_count"] >= 598
        assert controls["sdedit_seam_backprojection_available"] is False
        assert "V66" in controls["v66_failure_addressed"]
        metadata = json.loads(Path(row["metadata_path"]).read_text(encoding="utf-8"))
        assert metadata["root_selection_log"]["source_segment_count"] == 1296
        assert "v67_lsystem_branch_naturalization_contract" in metadata

    metrics_rows = json.loads((tmp_path / "initial_metrics.json").read_text(encoding="utf-8"))
    assert len(metrics_rows) == 4
    assert all(int(row["mesh_component_count"]) == 1 for row in metrics_rows)
    assert all(float(row["largest_mesh_component_vertex_ratio"]) >= 0.999 for row in metrics_rows)
    assert all(int(row["terminal_tip_count"]) >= 598 for row in metrics_rows)

    zoom_manifest = tmp_path / "V67_obj_zoom_manifest_same_scaffold_tapered_twig_20260512.json"
    assert zoom_manifest.exists()
    zdata = json.loads(zoom_manifest.read_text(encoding="utf-8"))
    assert len(zdata["cases"]) == 4
    assert all(item["detail_target_source"] == "v67_same_scaffold_high_degree_lsystem_junctions_no_terminal_caps" for item in zdata["cases"])
    assert all(len(item["fixed_detail_targets"]) == 2 for item in zdata["cases"])
