import csv
import importlib.util
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "figures"
    / "build_remote_generation_case_gallery_index_20260510.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "build_remote_generation_case_gallery_index_20260510", SCRIPT
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_build_index_groups_strict_remote_batches_by_series_family_and_readiness(tmp_path):
    mod = load_module()
    repo = tmp_path / "repo"
    visual_dir = (
        repo
        / "visuals"
        / "strict_visual_matched_texture_v13_smooth_coral_crystal_zoom_20260510"
    )
    visual_dir.mkdir(parents=True)
    contact = visual_dir / "strict_visual_matched_texture_v13_contact_sheet_20260510.png"
    contact.write_bytes(b"fake image")

    results_inputs = (
        repo
        / "results"
        / "strict_visual_matched_texture_v14_branching_coral_20260510_remote"
        / "inputs"
    )
    results_inputs.mkdir(parents=True)
    with (results_inputs / "manifest.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "case_id",
                "family",
                "traditional_target",
                "generation_policy",
                "case_role",
                "recommended_use",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "case_id": "v14_dla_branching_staghorn_a",
                "family": "DLA/frontier",
                "traditional_target": "dla_coral_cluster_900",
                "generation_policy": "generate_new_on_a100_2_no_local_cherrypick",
                "case_role": "priority_a100_2",
                "recommended_use": "paper-candidate",
            }
        )

    negative_dir = repo / "visuals" / "strict_visual_matched_texture_v15_reject_negative_zoom_20260510"
    negative_dir.mkdir(parents=True)
    (negative_dir / "v15_reject_contact_sheet.png").write_bytes(b"fake image")

    output_dir = tmp_path / "gallery"
    entries = mod.build_index(repo, output_dir)

    assert output_dir.joinpath("remote_generation_case_gallery_index_20260510.md").exists()
    assert output_dir.joinpath("remote_generation_case_gallery_index_20260510.csv").exists()
    assert not output_dir.joinpath("contact_sheets").exists()

    keyed = {(entry.series, entry.family, entry.readiness) for entry in entries}
    assert ("V13", "DLA/frontier", "diagnostic-only") in keyed
    assert ("V14", "DLA/frontier", "paper-candidate") in keyed
    assert ("V15", "DLA/frontier", "reject/negative") in keyed

    md = output_dir.joinpath("remote_generation_case_gallery_index_20260510.md").read_text(
        encoding="utf-8"
    )
    assert "## DLA/frontier" in md
    assert "### paper-candidate" in md
    assert "v14_dla_branching_staghorn_a" in md
    assert "strict_visual_matched_texture_v13_contact_sheet_20260510.png" in md

    with output_dir.joinpath("remote_generation_case_gallery_index_20260510.csv").open(
        encoding="utf-8"
    ) as f:
        rows = list(csv.DictReader(f))
    assert {row["series"] for row in rows} == {"V13", "V14", "V15"}
    assert any(row["kind"] == "manifest-case" for row in rows)
    assert any(row["kind"] == "contact-sheet" for row in rows)


def test_copy_contact_sheets_is_opt_in(tmp_path):
    mod = load_module()
    repo = tmp_path / "repo"
    visual_dir = repo / "visuals" / "strict_visual_matched_texture_v12_tapered_staghorn_zoom_20260510"
    visual_dir.mkdir(parents=True)
    source = visual_dir / "strict_visual_matched_texture_v12_tapered_contact_sheet_20260510.png"
    source.write_bytes(b"fake image")

    output_dir = tmp_path / "gallery"
    mod.build_index(repo, output_dir, copy_contact_sheets=True)

    copied = output_dir / "contact_sheets" / "V12_strict_visual_matched_texture_v12_tapered_contact_sheet_20260510.png"
    assert copied.exists()
    assert copied.read_bytes() == b"fake image"
