"""Small subset of torchvision.transforms used by Trellis2 BiRefNet imports."""

from __future__ import annotations

import numpy as np
import torch
from PIL import Image


class InterpolationMode:
    NEAREST = 0
    NEAREST_EXACT = 0
    BILINEAR = 2
    BICUBIC = 3
    BOX = 4
    HAMMING = 5
    LANCZOS = 1


class Compose:
    def __init__(self, transforms):
        self.transforms = list(transforms)

    def __call__(self, value):
        for transform in self.transforms:
            value = transform(value)
        return value


class Resize:
    def __init__(self, size):
        self.size = tuple(size)

    def __call__(self, image):
        if isinstance(image, Image.Image):
            return image.resize((self.size[1], self.size[0]))
        return image


class ToTensor:
    def __call__(self, image):
        if isinstance(image, Image.Image):
            arr = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
            return torch.from_numpy(arr).permute(2, 0, 1)
        return image


class Normalize:
    def __init__(self, mean, std):
        self.mean = torch.as_tensor(mean, dtype=torch.float32).view(-1, 1, 1)
        self.std = torch.as_tensor(std, dtype=torch.float32).view(-1, 1, 1)

    def __call__(self, tensor):
        return (tensor - self.mean.to(tensor.device, tensor.dtype)) / self.std.to(tensor.device, tensor.dtype)


class ToPILImage:
    def __call__(self, tensor):
        if hasattr(tensor, "detach"):
            tensor = tensor.detach().cpu()
        arr = np.asarray(tensor)
        if arr.ndim == 2:
            arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
            return Image.fromarray(arr, mode="L")
        if arr.ndim == 3 and arr.shape[0] in (1, 3, 4):
            arr = np.moveaxis(arr, 0, -1)
        arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
        return Image.fromarray(arr)
