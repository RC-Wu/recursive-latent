import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "postprocess_v60_lsystem_branch_clean_export_20260511.py"


def load_module():
    spec = importlib.util.spec_from_file_location("postprocess_v60_lsystem_branch_clean_export_20260511", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v60_clean_export_defaults_are_versioned_and_non_destructive():
    mod = load_module()
    assert mod.HAS_BLENDER is False
    assert mod.DEFAULT_OUT.name == "strict_visual_matched_texture_V60_lsystem_branch_clean_export_20260511"
    assert len(mod.DEFAULT_CASES) == 2
    assert {label for label, _ in mod.DEFAULT_CASES} == {
        "V60_lsys_branch_clean_short_bough_lowfrag_B",
        "V60_lsys_branch_clean_short_bough_compact_D",
    }
    assert all("V59_lsys_branch_smooth_short_bough" in str(path) for _, path in mod.DEFAULT_CASES)
    assert all(str(path).endswith("textured.glb") for _, path in mod.DEFAULT_CASES)


def test_v60_parser_keeps_project_local_cache_defaults():
    mod = load_module()
    parser = mod.build_parser()
    args = parser.parse_args([])
    assert args.voxel_size == 0.0175
    assert args.smooth_iters == 5
    assert args.smooth_factor == 0.10
    assert args.merge_distance == 0.0008
    assert args.decimate_ratio == 0.0
