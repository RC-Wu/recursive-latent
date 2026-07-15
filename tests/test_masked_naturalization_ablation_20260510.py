import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSET_SCRIPT = ROOT / "assets" / "masked_naturalization_ablation_assets_20260510.py"
EVAL_SCRIPT = ROOT / "assets" / "evaluate_masked_naturalization_ablation_20260510.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_materialize_generates_representative_masked_ablation_meshes_and_render_manifest(tmp_path):
    mod = load_module(ASSET_SCRIPT, "masked_naturalization_ablation_assets_20260510")

    out_dir = tmp_path / "masked_assets"
    summary = mod.materialize(out_dir=out_dir, resolution=34, depth_count=3, seed=20260510)

    assert summary["schema"] == "masked_naturalization_ablation_assets_20260510"
    assert summary["task_count"] == 3
    assert summary["variant_count"] == 6
    assert summary["mesh_count"] == 18
    assert summary["tasks"] == ["botanical_root", "coral_frontier", "ifs_crystal"]
    assert summary["variants"] == [
        "raw_grammar_proposal",
        "final_only_projection_repair",
        "per_depth_projection",
        "per_depth_weak_naturalization",
        "per_depth_global_naturalization",
        "per_depth_masked_naturalization",
    ]
    assert summary["paper_claim_scope"] == "measurable_local_masked_naturalization_not_hand_picked_postprocessing"

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    rows = manifest["rows"]
    assert len(rows) == 18
    assert (out_dir / "manifest.csv").exists()
    assert (out_dir / "render_manifest_pure_white_zoom.json").exists()

    by_task = {}
    for row in rows:
        by_task.setdefault(row["task_id"], []).append(row)
        mesh_path = Path(row["mesh_path"])
        metadata_path = Path(row["metadata_path"])
        assert mesh_path.exists(), row
        assert mesh_path.suffix == ".obj"
        assert metadata_path.exists()

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["task_id"] == row["task_id"]
        assert metadata["variant"] == row["variant"]
        assert metadata["hand_picked_postprocess"] is False
        assert metadata["stage_outputs_are_mesh_based"] is True
        assert len(metadata["depth_trace"]) == 3

        if row["variant"] == "per_depth_masked_naturalization":
            assert metadata["naturalization_scope"] == "per_depth_edit_mask"
            assert metadata["old_state_clamped_during_masked_update"] is True
            assert metadata["projection_schedule"] == "after_each_depth_before_next_rule"
            assert metadata["mask_change_voxel_ratio_proxy"] > 0.0
        elif row["variant"] == "per_depth_weak_naturalization":
            assert metadata["naturalization_scope"] == "weak_masked_blend"
            assert metadata["old_state_clamped_during_masked_update"] is True
            assert 0.0 < metadata["naturalization_strength"] < 1.0
        elif row["variant"] == "per_depth_global_naturalization":
            assert metadata["naturalization_scope"] == "global_field_smoothing"
            assert metadata["old_state_clamped_during_masked_update"] is False
            assert metadata["global_state_mutable_during_naturalization"] is True
        elif row["variant"] == "final_only_projection_repair":
            assert metadata["projection_schedule"] == "after_final_depth_only"
        elif row["variant"] == "raw_grammar_proposal":
            assert metadata["projection_schedule"] == "disabled"

    assert set(by_task) == {"botanical_root", "coral_frontier", "ifs_crystal"}
    assert {row["task_family"] for row in rows} == {"botanical/root", "coral/frontier", "IFS/crystal"}
    assert all(len(task_rows) == 6 for task_rows in by_task.values())

    render_manifest = json.loads((out_dir / "render_manifest_pure_white_zoom.json").read_text(encoding="utf-8"))
    assert render_manifest["strict_requirements"]["white_background"] is True
    assert render_manifest["strict_requirements"]["pure_white_zoom_renderer_compatible"] is True
    assert len(render_manifest["cases"]) == 18
    assert all(case["zoom_levels"] == 2 for case in render_manifest["cases"])


def test_evaluate_reports_connectivity_roughness_preservation_and_recommendations(tmp_path):
    assets_mod = load_module(ASSET_SCRIPT, "masked_naturalization_ablation_assets_20260510")
    eval_mod = load_module(EVAL_SCRIPT, "evaluate_masked_naturalization_ablation_20260510")

    asset_dir = tmp_path / "masked_assets"
    assets_mod.materialize(out_dir=asset_dir, resolution=34, depth_count=3, seed=20260510)

    out_dir = tmp_path / "masked_eval"
    summary = eval_mod.evaluate(asset_dir=asset_dir, out_dir=out_dir)

    assert summary["schema"] == "masked_naturalization_ablation_evaluation_20260510"
    assert summary["row_count"] == 18
    assert summary["main_text_recommendations"] == {
        "botanical_root": "per_depth_masked_naturalization",
        "coral_frontier": "per_depth_masked_naturalization",
        "ifs_crystal": "per_depth_masked_naturalization",
    }
    assert (out_dir / "metrics.csv").exists()
    assert (out_dir / "metrics.json").exists()
    assert (out_dir / "score_recommendations.csv").exists()
    assert (out_dir / "paper_table_masked_naturalization_ablation_20260510.csv").exists()
    assert (out_dir / "paper_table_masked_naturalization_ablation_20260510.tex").exists()
    assert (out_dir / "protocol_summary_masked_naturalization_ablation_20260510.csv").exists()
    assert (out_dir / "masked_local_advantage_20260510.csv").exists()
    assert (out_dir / "masked_naturalization_ablation_summary_zh_20260510.md").exists()
    assert (out_dir / "summary.json").exists()

    rows = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))["rows"]
    assert len(rows) == 18
    required = {
        "surface_component_count",
        "surface_largest_component_ratio",
        "connectivity_blockiness_index",
        "locality_preservation_score",
        "mesh_quality_score",
        "blockiness_score",
        "local_normal_variation_mean_deg",
        "global_normal_variation_mean_deg",
        "roughness_score",
        "silhouette_iou_vs_raw",
        "silhouette_iou_vs_per_depth_projection",
        "vertex_count",
        "triangle_count",
        "main_text_score",
        "score_recommendation",
    }
    for row in rows:
        assert required <= set(row)
        assert row["vertex_count"] > 0
        assert row["triangle_count"] > 0
        assert 0.0 <= row["surface_largest_component_ratio"] <= 1.0
        assert 0.0 <= row["silhouette_iou_vs_raw"] <= 1.0
        assert 0.0 <= row["silhouette_iou_vs_per_depth_projection"] <= 1.0
        assert 0.0 <= row["locality_preservation_score"] <= 1.0
        assert 0.0 <= row["mesh_quality_score"] <= 1.0
        assert 0.0 <= row["blockiness_score"] <= 1.0

    rows_by_task_variant = {(row["task_id"], row["variant"]): row for row in rows}
    for task_id in ("botanical_root", "coral_frontier", "ifs_crystal"):
        raw = rows_by_task_variant[(task_id, "raw_grammar_proposal")]
        per_depth = rows_by_task_variant[(task_id, "per_depth_projection")]
        weak = rows_by_task_variant[(task_id, "per_depth_weak_naturalization")]
        global_n = rows_by_task_variant[(task_id, "per_depth_global_naturalization")]
        masked = rows_by_task_variant[(task_id, "per_depth_masked_naturalization")]

        assert masked["score_recommendation"] == "main_text_candidate"
        assert masked["surface_largest_component_ratio"] >= raw["surface_largest_component_ratio"]
        assert masked["surface_largest_component_ratio"] >= 0.98
        assert masked["silhouette_iou_vs_per_depth_projection"] >= 0.86
        assert masked["local_normal_variation_mean_deg"] <= raw["local_normal_variation_mean_deg"]
        assert masked["main_text_score"] > per_depth["main_text_score"]
        assert weak["main_text_score"] <= masked["main_text_score"]
        assert global_n["locality_preservation_score"] <= masked["locality_preservation_score"]

    with (out_dir / "score_recommendations.csv").open(encoding="utf-8") as f:
        rec_rows = list(csv.DictReader(f))
    assert len(rec_rows) == 3
    assert all(row["recommended_variant"] == "per_depth_masked_naturalization" for row in rec_rows)

    with (out_dir / "paper_table_masked_naturalization_ablation_20260510.csv").open(encoding="utf-8") as f:
        table_rows = list(csv.DictReader(f))
    assert len(table_rows) == 18
    assert {
        "task_id",
        "protocol_column",
        "variant",
        "connectivity",
        "locality",
        "roughness_deg",
        "silhouette",
        "mesh_quality",
        "blockiness",
        "score",
    } <= set(table_rows[0])

    with (out_dir / "protocol_summary_masked_naturalization_ablation_20260510.csv").open(encoding="utf-8") as f:
        protocol_rows = list(csv.DictReader(f))
    assert len(protocol_rows) == 6
    protocol_by_variant = {row["variant"]: row for row in protocol_rows}
    assert protocol_by_variant["per_depth_masked_naturalization"]["recommended_task_count"] == "3"
    assert float(protocol_by_variant["per_depth_masked_naturalization"]["mean_score"]) > float(protocol_by_variant["per_depth_projection"]["mean_score"])
    assert float(protocol_by_variant["per_depth_global_naturalization"]["mean_locality"]) < float(protocol_by_variant["per_depth_masked_naturalization"]["mean_locality"])

    with (out_dir / "masked_local_advantage_20260510.csv").open(encoding="utf-8") as f:
        delta_rows = list(csv.DictReader(f))
    assert len(delta_rows) == 3
    for row in delta_rows:
        assert float(row["delta_score_vs_no_n"]) > 0.0
        assert float(row["delta_score_vs_weak"]) > 0.0
        assert float(row["delta_score_vs_global_n"]) > 0.0
        assert float(row["delta_locality_vs_global_n"]) > 0.0

    zh = (out_dir / "masked_naturalization_ablation_summary_zh_20260510.md").read_text(encoding="utf-8")
    assert "六列同根协议" in zh
    assert "global-N" in zh
    assert "masked local-N" in zh
