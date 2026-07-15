import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSET_SCRIPT = ROOT / "assets" / "masked_naturalization_ablation_assets_20260510.py"
M2_M3_SCRIPT = ROOT / "assets" / "export_masked_naturalization_m2_m3_20260510.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_m2_m3_export_writes_same_camera_visuals_and_state_sidecars(tmp_path):
    assets_mod = load_module(ASSET_SCRIPT, "masked_naturalization_ablation_assets_20260510")
    export_mod = load_module(M2_M3_SCRIPT, "export_masked_naturalization_m2_m3_20260510")

    asset_dir = tmp_path / "masked_assets"
    assets_mod.materialize(out_dir=asset_dir, resolution=34, depth_count=3, seed=20260510)

    visual_dir = tmp_path / "masked_visuals"
    result_dir = tmp_path / "masked_m2_m3"
    summary = export_mod.export_m2_m3(asset_dir=asset_dir, visual_dir=visual_dir, result_dir=result_dir, panel_size=280)

    assert summary["schema"] == "masked_naturalization_m2_m3_export_20260510"
    assert summary["task_count"] == 3
    assert summary["protocol_count"] == 6
    assert summary["proxy_only"] is True
    assert Path(summary["m2_contact_sheet"]).exists()
    assert Path(summary["m2_visual_manifest"]).exists()
    assert Path(summary["m3_sidecar_csv"]).exists()
    assert Path(summary["m3_sidecar_json"]).exists()
    assert Path(summary["m3_trace_graph_csv"]).exists()
    assert Path(summary["m3_trace_graph_json"]).exists()

    manifest = json.loads(Path(summary["m2_visual_manifest"]).read_text(encoding="utf-8"))
    assert manifest["camera_contract"]["same_camera_per_task"] is True
    assert manifest["camera_contract"]["renderer"] == "deterministic_orthographic_projection"
    assert len(manifest["contact_sheet"]["rows"]) == 3
    assert len(manifest["task_visuals"]) == 3
    for task_id, paths in manifest["task_visuals"].items():
        assert Path(paths["same_camera_protocol_strip"]).exists(), task_id
        assert Path(paths["mask_overlay"]).exists(), task_id
        assert Path(paths["before_after_edit_overlay"]).exists(), task_id

    with Path(summary["m3_sidecar_csv"]).open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 18
    required_fields = {
        "task_id",
        "variant",
        "metric_confidence",
        "active_handle_survival_rate_proxy",
        "root_attached_mass_ratio_proxy",
        "orphan_handle_count_proxy",
        "reachable_frontier_count_proxy",
        "frontier_reachability_rate_proxy",
        "deleted_active_support_mass_proxy",
        "handle_drift_l2_mean_proxy",
        "mask_overlap_with_active_handles_proxy",
        "proxy_limitations",
    }
    assert required_fields <= set(rows[0])

    by_task_variant = {(row["task_id"], row["variant"]): row for row in rows}
    for task_id in ("botanical_root", "coral_frontier", "ifs_crystal"):
        masked = by_task_variant[(task_id, "per_depth_masked_naturalization")]
        global_n = by_task_variant[(task_id, "per_depth_global_naturalization")]
        no_n = by_task_variant[(task_id, "per_depth_projection")]

        assert masked["metric_confidence"] == "proxy_from_metadata_and_mesh"
        assert float(masked["active_handle_survival_rate_proxy"]) >= float(global_n["active_handle_survival_rate_proxy"])
        assert float(masked["root_attached_mass_ratio_proxy"]) >= float(global_n["root_attached_mass_ratio_proxy"])
        assert float(masked["frontier_reachability_rate_proxy"]) >= float(global_n["frontier_reachability_rate_proxy"])
        assert int(float(masked["orphan_handle_count_proxy"])) <= int(float(global_n["orphan_handle_count_proxy"]))
        assert float(masked["mask_overlap_with_active_handles_proxy"]) > 0.0
        assert float(no_n["handle_drift_l2_mean_proxy"]) <= float(masked["handle_drift_l2_mean_proxy"])
        assert "proxy" in masked["proxy_limitations"].lower()

    status_md = Path(summary["chinese_status_md"])
    assert status_md.exists()
    text = status_md.read_text(encoding="utf-8")
    assert "M2" in text
    assert "M3" in text
    assert "M3+" in text
    assert "proxy" in text
    assert "仍缺口" in text

    with Path(summary["m3_trace_graph_csv"]).open(encoding="utf-8") as f:
        trace_rows = list(csv.DictReader(f))
    assert len(trace_rows) == 18
    trace_required_fields = {
        "task_id",
        "variant",
        "metric_confidence",
        "active_handle_count_trace",
        "root_reachable_active_handle_count_trace",
        "active_handle_survival_rate_trace",
        "frontier_reachability_rate_trace",
        "unsupported_active_support_mass_ratio_trace",
        "root_attached_support_mass_ratio_trace",
        "trace_limitations",
    }
    assert trace_required_fields <= set(trace_rows[0])
    trace_by_task_variant = {(row["task_id"], row["variant"]): row for row in trace_rows}
    for task_id in ("botanical_root", "coral_frontier", "ifs_crystal"):
        raw = trace_by_task_variant[(task_id, "raw_grammar_proposal")]
        masked = trace_by_task_variant[(task_id, "per_depth_masked_naturalization")]
        global_n = trace_by_task_variant[(task_id, "per_depth_global_naturalization")]

        assert masked["metric_confidence"] == "instrumented_grammar_trace_graph_not_trellis_runtime"
        assert float(masked["active_handle_survival_rate_trace"]) >= float(raw["active_handle_survival_rate_trace"])
        assert float(masked["frontier_reachability_rate_trace"]) >= float(raw["frontier_reachability_rate_trace"])
        assert float(masked["unsupported_active_support_mass_ratio_trace"]) <= float(raw["unsupported_active_support_mass_ratio_trace"])
        assert float(masked["root_attached_support_mass_ratio_trace"]) >= float(raw["root_attached_support_mass_ratio_trace"])
        assert int(masked["active_handle_count_trace"]) == int(global_n["active_handle_count_trace"])
        assert "not a Trellis" in masked["trace_limitations"]
