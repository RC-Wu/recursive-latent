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
        self.transforms = transforms

    def __call__(self, x):
        for transform in self.transforms:
            x = transform(x)
        return x


class Resize:
    def __init__(self, size, interpolation=None, max_size=None, antialias=True):
        self.size = size

    def __call__(self, x):
        return x.resize(self.size) if hasattr(x, "resize") else x


class CenterCrop:
    def __init__(self, size):
        self.size = size

    def __call__(self, x):
        return x


class ToTensor:
    def __call__(self, x):
        import numpy as np
        import torch

        arr = np.asarray(x.convert("RGB"), dtype="float32") / 255.0
        return torch.from_numpy(arr).permute(2, 0, 1)


class Normalize:
    def __init__(self, mean, std):
        import torch

        self.mean = torch.tensor(mean, dtype=torch.float32).view(-1, 1, 1)
        self.std = torch.tensor(std, dtype=torch.float32).view(-1, 1, 1)

    def __call__(self, x):
        mean = self.mean.to(device=x.device, dtype=x.dtype)
        std = self.std.to(device=x.device, dtype=x.dtype)
        return (x - mean) / std


class ToPILImage:
    def __call__(self, x):
        import numpy as np
        from PIL import Image

        if hasattr(x, "detach"):
            x = x.detach().cpu().numpy()
        x = np.asarray(x)
        if x.ndim == 2:
            return Image.fromarray((x * 255).clip(0, 255).astype("uint8"))
        return Image.fromarray((x.transpose(1, 2, 0) * 255).clip(0, 255).astype("uint8"))
