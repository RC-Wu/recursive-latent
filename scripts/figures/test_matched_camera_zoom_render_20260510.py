import importlib.util
import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).with_name("matched_camera_zoom_render_20260510.py")


def load_module():
    spec = importlib.util.spec_from_file_location("matched_camera_zoom_render_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_zoom_chain_prefers_upper_non_trunk_detail_and_keeps_square_panels():
    mod = load_module()
    vertices = [
        (0.0, 0.0, z / 10.0) for z in range(11)
    ] + [
        (0.9, 0.1, 0.72),
        (1.0, 0.1, 0.78),
        (1.1, 0.1, 0.82),
        (1.2, 0.1, 0.86),
    ]

    plan = mod.plan_case(
        label="branchy",
        mesh="branchy.obj",
        vertices=vertices,
        out_dir=Path("/tmp/matched"),
        resolution=1024,
        zoom_levels=2,
    )

    assert plan["background"] == "white"
    assert plan["overview"]["resolution"] == [1024, 1024]
    assert plan["overview"]["kind"] == "raw_camera_render"
    assert [zoom["resolution"] for zoom in plan["zooms"]] == [[1024, 1024], [1024, 1024]]
    assert all(zoom["kind"] == "camera_render" for zoom in plan["zooms"])
    assert plan["zooms"][1]["parent"] == plan["zooms"][0]["id"]
    assert plan["zooms"][0]["target"][0] > 0.45
    assert plan["zooms"][0]["target"][2] > 0.6
    assert plan["zooms"][0]["ortho_scale"] < plan["overview"]["ortho_scale"]


def test_plan_only_cli_writes_manifest_without_blender(tmp_path):
    manifest = tmp_path / "cases.json"
    mesh = tmp_path / "toy.obj"
    mesh.write_text(
        "\n".join(
            [
                "v 0 0 0",
                "v 0 0 1",
                "v 0.9 0.1 0.8",
                "v 1.1 0.1 0.9",
                "f 1 2 3",
            ]
        ),
        encoding="utf-8",
    )
    manifest.write_text(json.dumps({"cases": [{"label": "toy", "mesh": str(mesh)}]}), encoding="utf-8")

    out_dir = tmp_path / "out"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(manifest),
            "--out-dir",
            str(out_dir),
            "--plan-only",
            "--zoom-levels",
            "2",
            "--resolution",
            "900",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    plan = json.loads((out_dir / "matched_camera_zoom_plan.json").read_text(encoding="utf-8"))
    assert plan["strict_requirements"]["white_background"] is True
    assert plan["strict_requirements"]["zoom_panels_are_camera_renders"] is True
    assert plan["cases"][0]["overview"]["path"].endswith("toy/overview_raw.png")
    assert len(plan["cases"][0]["zooms"]) == 2
    assert "strict_matched_zoom_comparison.png" not in result.stdout
