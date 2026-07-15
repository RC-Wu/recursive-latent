import argparse
import json
from pathlib import Path

import torch
from transformers import DINOv3ViTConfig, DINOv3ViTModel


def convert_state_dict(src):
    dst = {}
    dst["embeddings.cls_token"] = src["cls_token"]
    dst["embeddings.mask_token"] = src["mask_token"].reshape(1, 1, -1)
    dst["embeddings.register_tokens"] = src["storage_tokens"]
    dst["embeddings.patch_embeddings.weight"] = src["patch_embed.proj.weight"]
    dst["embeddings.patch_embeddings.bias"] = src["patch_embed.proj.bias"]

    num_layers = max(int(k.split(".")[1]) for k in src if k.startswith("blocks.")) + 1
    for i in range(num_layers):
        prefix = f"blocks.{i}"
        out = f"layer.{i}"
        dst[f"{out}.norm1.weight"] = src[f"{prefix}.norm1.weight"]
        dst[f"{out}.norm1.bias"] = src[f"{prefix}.norm1.bias"]
        dst[f"{out}.norm2.weight"] = src[f"{prefix}.norm2.weight"]
        dst[f"{out}.norm2.bias"] = src[f"{prefix}.norm2.bias"]

        q_w, k_w, v_w = src[f"{prefix}.attn.qkv.weight"].chunk(3, dim=0)
        q_b, _k_b, v_b = src[f"{prefix}.attn.qkv.bias"].chunk(3, dim=0)
        dst[f"{out}.attention.q_proj.weight"] = q_w
        dst[f"{out}.attention.k_proj.weight"] = k_w
        dst[f"{out}.attention.v_proj.weight"] = v_w
        dst[f"{out}.attention.q_proj.bias"] = q_b
        dst[f"{out}.attention.v_proj.bias"] = v_b
        dst[f"{out}.attention.o_proj.weight"] = src[f"{prefix}.attn.proj.weight"]
        dst[f"{out}.attention.o_proj.bias"] = src[f"{prefix}.attn.proj.bias"]

        dst[f"{out}.layer_scale1.lambda1"] = src[f"{prefix}.ls1.gamma"]
        dst[f"{out}.layer_scale2.lambda1"] = src[f"{prefix}.ls2.gamma"]
        dst[f"{out}.mlp.up_proj.weight"] = src[f"{prefix}.mlp.fc1.weight"]
        dst[f"{out}.mlp.up_proj.bias"] = src[f"{prefix}.mlp.fc1.bias"]
        dst[f"{out}.mlp.down_proj.weight"] = src[f"{prefix}.mlp.fc2.weight"]
        dst[f"{out}.mlp.down_proj.bias"] = src[f"{prefix}.mlp.fc2.bias"]

    dst["norm.weight"] = src["norm.weight"]
    dst["norm.bias"] = src["norm.bias"]
    return dst, num_layers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pth", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--image-size", type=int, default=512)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    raw = torch.load(args.pth, map_location="cpu")
    if isinstance(raw, dict) and "state_dict" in raw:
        raw = raw["state_dict"]
    elif isinstance(raw, dict) and "model" in raw:
        raw = raw["model"]

    hidden = raw["patch_embed.proj.weight"].shape[0]
    patch_size = raw["patch_embed.proj.weight"].shape[-1]
    intermediate = raw["blocks.0.mlp.fc1.weight"].shape[0]
    num_register_tokens = raw["storage_tokens"].shape[1]
    state, num_layers = convert_state_dict(raw)

    cfg = DINOv3ViTConfig(
        image_size=args.image_size,
        patch_size=patch_size,
        hidden_size=hidden,
        intermediate_size=intermediate,
        num_hidden_layers=num_layers,
        num_attention_heads=hidden // 64,
        num_register_tokens=num_register_tokens,
        key_bias=False,
        query_bias=True,
        value_bias=True,
        proj_bias=True,
        mlp_bias=True,
        apply_layernorm=True,
        layerscale_value=1.0,
        use_gated_mlp=False,
    )
    model = DINOv3ViTModel(cfg)
    result = model.load_state_dict(state, strict=False)
    model.save_pretrained(args.out)

    report = {
        "source": str(args.pth),
        "out": str(args.out),
        "hidden_size": hidden,
        "intermediate_size": intermediate,
        "num_hidden_layers": num_layers,
        "num_attention_heads": hidden // 64,
        "num_register_tokens": num_register_tokens,
        "missing_keys": list(result.missing_keys),
        "unexpected_keys": list(result.unexpected_keys),
    }
    (args.out / "conversion_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
