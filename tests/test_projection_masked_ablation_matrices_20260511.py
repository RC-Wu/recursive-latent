import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "projection_masked_ablation_matrices_20260511.py"


def load_module():
    spec = importlib.util.spec_from_file_location("projection_masked_ablation_matrices_20260511", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_projection_and_masked_matrices_close_required_variants(tmp_path):
    mod = load_module()
    out_dir = tmp_path / "results"
    visual_dir = tmp_path / "visuals"
    drafts_dir = tmp_path / "drafts"
    figures_dir = tmp_path / "figures"
    status_doc = tmp_path / "status.md"

    summary = mod.run_all(
        out_dir=out_dir,
        visual_dir=visual_dir,
        drafts_dir=drafts_dir,
        figures_dir=figures_dir,
        status_doc=status_doc,
        seeds=[20260510],
        resolution=28,
        depth_count=3,
    )

    assert summary["schema"] == "projection_masked_ablation_matrices_20260511"
    assert summary["task_count"] == 4
    assert summary["projection_variant_count"] == 5
    assert summary["naturalization_variant_count"] == 10
    assert Path(summary["projection_table_tex"]).exists()
    assert Path(summary["naturalization_table_tex"]).exists()
    assert Path(summary["projection_visual_manifest"]).exists()
    assert Path(summary["naturalization_visual_manifest"]).exists()
    assert Path(summary["projection_source_sheet"]).exists()
    assert Path(summary["naturalization_source_sheet"]).exists()
    assert summary["projection_visual_tasks"] == ["coral_frontier", "ifs_crystal"]
    assert summary["naturalization_visual_tasks"] == ["botanical_root", "vine_trellis"]
    assert status_doc.exists()

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))["rows"]
    assert len(manifest) == 4 * (5 + 10)
    projection_variants = {row["variant"] for row in manifest if row["experiment"] == "projection"}
    naturalization_variants = {row["variant"] for row in manifest if row["experiment"] == "naturalization"}
    assert projection_variants == set(mod.PROJECTION_VARIANTS)
    assert naturalization_variants == set(mod.NATURALIZATION_VARIANTS)

    with (out_dir / "metrics.csv").open(encoding="utf-8") as f:
        metric_rows = list(csv.DictReader(f))
    assert len(metric_rows) == len(manifest)
    required_metric_fields = {
        "occupancy_lcr_6n",
        "recursive_root_reachability_proxy",
        "recursive_orphan_active_handles_proxy",
        "recursive_handle_survival_proxy",
        "topology_drift_proxy",
        "local_artifact_index_proxy",
    }
    assert required_metric_fields <= set(metric_rows[0])
    for row in metric_rows:
        assert 0.0 <= float(row["occupancy_lcr_6n"]) <= 1.0
        assert 0.0 <= float(row["recursive_root_reachability_proxy"]) <= 1.0
        assert 0.0 <= float(row["recursive_handle_survival_proxy"]) <= 1.0


def test_projection_main_table_exposes_inside_loop_metrics(tmp_path):
    mod = load_module()
    summary = mod.run_all(
        out_dir=tmp_path / "results",
        visual_dir=tmp_path / "visuals",
        drafts_dir=tmp_path / "drafts",
        figures_dir=tmp_path / "figures",
        status_doc=tmp_path / "status.md",
        seeds=[20260510],
        resolution=28,
        depth_count=3,
    )

    rows = {row["variant"]: row for row in summary["projection_main_rows"]}
    assert set(rows) == set(mod.PROJECTION_VARIANTS)
    assert rows["final_only_projection"]["occupancy_lcr_mean"] >= rows["no_projection"]["occupancy_lcr_mean"]
    assert rows["final_only_projection"]["root_reachability_mean"] < rows["per_depth_connector_aware"]["root_reachability_mean"]
    assert rows["final_only_projection"]["handle_survival_mean"] < rows["full_ps_rslg"]["handle_survival_mean"]
    assert rows["final_only_projection"]["orphan_active_handles_mean"] > rows["full_ps_rslg"]["orphan_active_handles_mean"]
    assert rows["full_ps_rslg"]["failure_rate_mean"] <= rows["per_depth_connector_aware"]["failure_rate_mean"]

    tex = Path(summary["projection_table_tex"]).read_text(encoding="utf-8")
    assert "Occ. LCR" in tex
    assert "Root reach." in tex
    assert "Orphan active" in tex
    assert "Handle survival" in tex


def test_masked_naturalization_matrix_separates_projection_and_global_control(tmp_path):
    mod = load_module()
    summary = mod.run_all(
        out_dir=tmp_path / "results",
        visual_dir=tmp_path / "visuals",
        drafts_dir=tmp_path / "drafts",
        figures_dir=tmp_path / "figures",
        status_doc=tmp_path / "status.md",
        seeds=[20260510],
        resolution=28,
        depth_count=3,
    )

    rows = {row["variant"]: row for row in summary["naturalization_main_rows"]}
    assert set(rows) == set(mod.NATURALIZATION_VARIANTS)
    assert rows["masked_local_with_projection"]["handle_survival_mean"] >= rows["masked_local_no_projection"]["handle_survival_mean"]
    assert rows["masked_local_with_projection"]["failure_rate_mean"] <= rows["masked_local_no_projection"]["failure_rate_mean"]
    assert rows["masked_local_with_projection"]["surface_roughness_mean"] < rows["no_naturalization_with_projection"]["surface_roughness_mean"]
    assert rows["masked_local_with_projection"]["topology_drift_mean"] <= rows["global_naturalization_with_projection"]["topology_drift_mean"] + 0.05
    assert rows["masked_local_with_projection"]["rendered_asset_quality_mean"] >= rows["global_naturalization_with_projection"]["rendered_asset_quality_mean"]

    tex = Path(summary["naturalization_table_tex"]).read_text(encoding="utf-8")
    assert "Naturalization variant" in tex
    assert "masked/+proj" in tex
    assert "global/+proj" in tex
