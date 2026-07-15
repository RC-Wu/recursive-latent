import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "postprocess_v61_lsystem_branch_clean_export_20260512.py"


def load_module():
    spec = importlib.util.spec_from_file_location("postprocess_v61_lsystem_branch_clean_export_20260512", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v61_clean_export_defaults_are_fine_and_versioned():
    mod = load_module()
    assert mod.v60.HAS_BLENDER is False
    assert mod.DEFAULT_OUT.name == "strict_visual_matched_texture_V61_lsystem_branch_clean_export_fine_20260512"
    assert len(mod.DEFAULT_CASES) == 2
    assert {label for label, _ in mod.DEFAULT_CASES} == {
        "V61_lsys_branch_clean_dense_B",
        "V61_lsys_branch_clean_balanced_C",
    }
    assert all("strict_visual_matched_texture_V61_lsystem_branch_dense_clean_bough_yfork_BC_20260512_remote" in str(path) for _, path in mod.DEFAULT_CASES)
    assert all(str(path).endswith("textured.glb") for _, path in mod.DEFAULT_CASES)


def test_v61_parser_uses_density_preserving_clean_export_defaults():
    mod = load_module()
    parser = mod.build_parser()
    args = parser.parse_args([])
    assert args.voxel_size == 0.0065
    assert args.smooth_iters == 3
    assert args.smooth_factor == 0.04
    assert args.merge_distance == 0.00035
    assert args.decimate_ratio == 0.0
