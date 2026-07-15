#!/usr/bin/env python3
"""Download Trellis2 inference dependencies into a project-local HF cache."""

from __future__ import annotations

import os
from pathlib import Path

from huggingface_hub import hf_hub_download, snapshot_download


ROOT = Path(os.environ.get("RGG_ROOT", "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"))
HF_HOME = ROOT / "hf_home"


def main() -> None:
    HF_HOME.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HOME"] = str(HF_HOME)
    os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:27890")
    os.environ.setdefault("HTTP_PROXY", "http://127.0.0.1:27890")

    print(f"HF_HOME={HF_HOME}", flush=True)

    repos = [
        "microsoft/TRELLIS.2-4B",
        "microsoft/TRELLIS-image-large",
        "facebook/dinov3-vitl16-pretrain-lvd1689m",
        "ZhengPeng7/BiRefNet",
    ]
    for repo in repos:
        print(f"SNAPSHOT_START {repo}", flush=True)
        path = snapshot_download(repo_id=repo)
        print(f"SNAPSHOT_DONE {repo} {path}", flush=True)

    # Explicitly touch the cross-repo model files used by pipeline.json. This
    # makes failures point to the exact missing model rather than surfacing later
    # during a GPU run.
    for filename in [
        "ckpts/ss_dec_conv3d_16l8_fp16.json",
        "ckpts/ss_dec_conv3d_16l8_fp16.safetensors",
    ]:
        p = hf_hub_download("microsoft/TRELLIS-image-large", filename)
        print(f"TOUCHED microsoft/TRELLIS-image-large/{filename} {p}", flush=True)


if __name__ == "__main__":
    main()

