import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/figures/build_real_case_ablation_pptx_manifest_20260512.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_real_case_manifest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_png(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n")


def test_builds_real_case_manifests_with_ours_rightmost_and_callout_paths(tmp_path):
    module = load_module()
    input_dir = tmp_path / "inputs"
    render_dir = tmp_path / "renders"
    output_dir = tmp_path / "out"
    manifest_rows = []

    case_specs = {
        "projection": {
            "cases": ["proj_staghorn_frontier", "proj_pyrite_lattice"],
            "variants": module.PROJECTION_VARIANTS,
        },
        "naturalization": {
            "cases": ["nat_distributed_bough_B", "nat_balanced_bough_C"],
            "variants": module.NATURALIZATION_VARIANTS,
        },
    }
    plan_cases = []
    for experiment, spec in case_specs.items():
        for case_id in spec["cases"]:
            for order, variant in enumerate(spec["variants"]):
                label = f"realab_{experiment}_{case_id}_{variant}"
                mesh_path = input_dir / label / f"{label}.obj"
                meta_path = input_dir / label / f"{label}_metadata.json"
                mesh_path.parent.mkdir(parents=True, exist_ok=True)
                mesh_path.write_text("# obj\n", encoding="utf8")
                meta_path.write_text("{}", encoding="utf8")
                manifest_rows.append(
                    {
                        "label": label,
                        "experiment": experiment,
                        "case_id": case_id,
                        "case_label": case_id.replace("_", " "),
                        "variant": variant,
                        "variant_label": "OURS" if variant == "ours" else variant.replace("_", " "),
                        "mesh_path": str(mesh_path),
                        "metadata_path": str(meta_path),
                        "priority_order": order,
                    }
                )
                case_dir = render_dir / label
                overview = case_dir / "overview_raw.png"
                overview_callouts = case_dir / "overview_callouts.png"
                zoom = case_dir / "zoom_01.png"
                write_png(overview)
                write_png(overview_callouts)
                write_png(zoom)
                plan_cases.append(
                    {
                        "label": label,
                        "case_dir": str(case_dir),
                        "overview": {
                            "path": str(overview),
                            "annotated_path": str(overview_callouts),
                        },
                        "zooms": [{"id": "zoom_01", "path": str(zoom)}],
                    }
                )

    input_manifest = input_dir / "manifest.json"
    zoom_plan = render_dir / "matched_camera_zoom_plan.json"
    input_manifest.write_text(json.dumps(manifest_rows), encoding="utf8")
    zoom_plan.write_text(json.dumps({"cases": plan_cases}), encoding="utf8")

    result = module.build_manifests(input_manifest, zoom_plan, output_dir, write=True)

    assert result["projection"]["case_count"] == 2
    assert result["projection"]["panel_count"] == 20
    assert result["naturalization"]["case_count"] == 2
    assert result["naturalization"]["panel_count"] == 24

    projection = json.loads((output_dir / module.PROJECTION_OUTPUT_NAME).read_text(encoding="utf8"))
    naturalization = json.loads((output_dir / module.NATURALIZATION_OUTPUT_NAME).read_text(encoding="utf8"))

    assert projection[0]["variants"][-1] == "ours"
    assert projection[0]["labels"][-1] == "OURS"
    assert projection[0]["ours_column"] == 4
    assert naturalization[0]["variants"][-1] == "ours"
    assert naturalization[0]["ours_column"] == 5

    first_panels = projection[0]["panels"]
    assert first_panels[0]["kind"] == "overview"
    assert first_panels[0]["path"].endswith("overview_callouts.png")
    assert first_panels[1]["kind"] == "zoom"
    assert first_panels[1]["path"].endswith("zoom_01.png")
    assert "summary" in projection[0]
    assert "provenance" in projection[0]

    dry_output = tmp_path / "dry"
    dry_result = module.build_manifests(input_manifest, zoom_plan, dry_output, write=False)
    assert dry_result["would_write"] is False
    assert not dry_output.exists()
