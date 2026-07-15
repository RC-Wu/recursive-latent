import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str):
    script = ROOT / "assets" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def test_same_root_projection_aggregator_writes_missing_variant_rows(tmp_path):
    mod = load_module("same_root_projection_matrix_20260510")
    project = tmp_path / "project"
    source = project / "results/projection_matrix_gap_closure_20260509/projection_matrix_gap_closure.csv"
    write_csv(
        source,
        [
            {
                "case": "vine_compete_d3",
                "family": "vine/root/tree",
                "variant": "no_projection",
                "evidence_status": "existing",
                "component_count": 2059,
                "largest_component_ratio": 0.9049,
                "vertices": 199470,
                "faces": 405886,
                "mesh_path": "vine_direct.obj",
                "notes": "direct recursion / no projection",
            }
        ],
    )

    summary = mod.aggregate(project, tmp_path / "out")
    rows = list(csv.DictReader((tmp_path / "out" / "same_root_projection_matrix.csv").open(encoding="utf-8")))

    assert summary["row_count"] >= 6
    assert any(row["projection_variant"] == "direct" and row["status"] == "available" for row in rows)
    assert any(row["projection_variant"] == "traditional" and row["status"] == "missing" for row in rows)
    assert any(row["projection_variant"] == "bridge" and row["status"] == "missing" for row in rows)


def test_naturalization_aggregator_separates_projection_from_posthoc_repair(tmp_path):
    mod = load_module("naturalization_projection_ablation_aggregation_20260510")
    project = tmp_path / "project"
    naturalize = project / "results/naturalize_blocky_mesh_pilot_20260510/summary.csv"
    write_csv(
        naturalize,
        [
            {
                "label": "dla_coral_cluster_900",
                "source": "traditional_target.obj",
                "output_obj": "naturalized.obj",
                "occ_before_component_count": 10,
                "occ_after_component_count": 1,
                "occ_before_largest_component_ratio": 0.4,
                "occ_after_largest_component_ratio": 1.0,
                "before_faces": 10800,
                "after_faces": 67954,
            }
        ],
    )

    summary = mod.aggregate(project, tmp_path / "out")
    rows = list(csv.DictReader((tmp_path / "out" / "naturalization_projection_ablation.csv").open(encoding="utf-8")))

    assert summary["row_count"] >= 7
    repair = [row for row in rows if row["ablation_variant"] == "post-hoc repair baseline"]
    assert repair and repair[0]["projection_role"] == "post_hoc_mesh_repair_not_projection"
    assert any(row["ablation_variant"] == "masked local-N" and row["status"] == "missing" for row in rows)


def test_effective_resolution_metrics_estimate_recursive_blowup(tmp_path):
    mod = load_module("effective_resolution_metrics_20260510")
    project = tmp_path / "project"
    one_shot = project / "results/baseline_one_to_one_metrics_20260510/metrics.csv"
    write_csv(
        one_shot,
        [
            {
                "label": "sc_tree_canopy_baseline",
                "faces": 1000,
                "vertices": 500,
                "bbox_diag": 2.0,
                "occupied_voxels": 200,
                "box_count_dimension_proxy": 1.5,
                "primary_largest_component_ratio": 0.4,
                "path": "baseline.glb",
            },
            {
                "label": "ours_vine_stage5",
                "faces": 8000,
                "vertices": 4000,
                "bbox_diag": 2.0,
                "occupied_voxels": 900,
                "box_count_dimension_proxy": 2.0,
                "primary_largest_component_ratio": 1.0,
                "path": "ours.glb",
            },
        ],
    )
    runtime = project / "results/runtime_token_growth_aggregate_20260510/runtime_token_growth_case_summary.csv"
    write_csv(
        runtime,
        [
            {
                "case": "vine_runtime",
                "max_depth_observed": 6,
                "base_tokens": 100,
                "max_tokens_observed": 400,
                "max_faces_observed": 8000,
            }
        ],
    )

    summary = mod.aggregate(project, tmp_path / "out")
    rows = list(csv.DictReader((tmp_path / "out" / "effective_resolution_metrics.csv").open(encoding="utf-8")))
    pair_rows = [row for row in rows if row["row_type"] == "comparison"]

    assert summary["comparison_count"] >= 1
    assert pair_rows[0]["status"] == "available"
    assert float(pair_rows[0]["recursive_to_oneshot_terminal_detail_ratio"]) > 1.0
    assert float(pair_rows[0]["estimated_full_object_highres_faces"]) >= 8000.0
