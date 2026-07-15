import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "evaluation"
    / "connectivity_depth_parameter_protocol.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("connectivity_depth_parameter_protocol", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_summarize_depth_curves_marks_connected_and_fragmenting_methods(tmp_path):
    mod = load_module()
    metrics_path = tmp_path / "metrics.csv"
    write_csv(
        metrics_path,
        [
            {
                "case": "vine",
                "method": "proposed_per_depth",
                "depth": 1,
                "same_seed": 20260509,
                "occupancy_component_count_6n": 1,
                "largest_occupancy_component_ratio_6n": 1.0,
                "root_component_ratio": 1.0,
                "orphan_mass_ratio": 0.0,
                "vertices": 100,
                "faces": 200,
                "tips": 4,
            },
            {
                "case": "vine",
                "method": "proposed_per_depth",
                "depth": 3,
                "same_seed": 20260509,
                "occupancy_component_count_6n": 1,
                "largest_occupancy_component_ratio_6n": 0.998,
                "root_component_ratio": 1.0,
                "orphan_mass_ratio": 0.0,
                "vertices": 260,
                "faces": 520,
                "tips": 7,
            },
            {
                "case": "vine",
                "method": "direct_sparse_grammar",
                "depth": 1,
                "same_seed": 20260509,
                "occupancy_component_count_6n": 2,
                "largest_occupancy_component_ratio_6n": 0.83,
                "root_component_ratio": 0.81,
                "orphan_mass_ratio": 0.19,
                "vertices": 110,
                "faces": 210,
                "tips": 5,
            },
            {
                "case": "vine",
                "method": "direct_sparse_grammar",
                "depth": 3,
                "same_seed": 20260509,
                "occupancy_component_count_6n": 9,
                "largest_occupancy_component_ratio_6n": 0.62,
                "root_component_ratio": 0.59,
                "orphan_mass_ratio": 0.41,
                "vertices": 410,
                "faces": 810,
                "tips": 14,
            },
        ],
    )

    rows = mod.load_metric_rows([metrics_path])
    summaries = mod.summarize_depth_curves(rows, max_components=1, min_lcr=0.98, max_orphan_mass=0.02)
    by_method = {row["method"]: row for row in summaries}

    assert by_method["proposed_per_depth"]["connectivity_curve_status"] == "pass"
    assert by_method["proposed_per_depth"]["max_occ_components_6n"] == 1
    assert by_method["proposed_per_depth"]["depth_count"] == 2
    assert by_method["direct_sparse_grammar"]["connectivity_curve_status"] == "fail"
    assert by_method["direct_sparse_grammar"]["component_growth_per_depth"] == 3.5
    assert by_method["direct_sparse_grammar"]["final_orphan_mass_ratio"] == 0.41


def test_cli_writes_summary_csv_json_and_protocol_gaps(tmp_path):
    metrics_path = tmp_path / "baseline.csv"
    write_csv(
        metrics_path,
        [
            {
                "case": "tree",
                "method": "lsystem",
                "depth": 4,
                "same_root_anchor": "0,0,0",
                "same_seed": 20260509,
                "same_max_depth": 4,
                "occupancy_component_count_6n": 1,
                "largest_occupancy_component_ratio_6n": 1.0,
                "orphan_mass_ratio": 0.0,
            },
            {
                "case": "tree",
                "method": "proposed_connected",
                "depth": 4,
                "same_root_anchor": "0,0,0",
                "same_seed": 20260509,
                "same_max_depth": 4,
                "occupancy_component_count_6n": 1,
                "largest_occupancy_component_ratio_6n": 1.0,
                "orphan_mass_ratio": 0.0,
            },
        ],
    )
    out_csv = tmp_path / "summary.csv"
    out_json = tmp_path / "summary.json"

    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input",
            str(metrics_path),
            "--out-csv",
            str(out_csv),
            "--out-json",
            str(out_json),
        ],
        check=True,
    )

    rows = list(csv.DictReader(out_csv.open(encoding="utf-8")))
    assert {row["method"] for row in rows} == {"lsystem", "proposed_connected"}
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["protocol_gaps"][0]["case"] == "tree"
    assert "direct_sparse_grammar" in payload["protocol_gaps"][0]["missing_required_methods"]
    assert payload["run_config"]["inputs"] == [str(metrics_path)]
