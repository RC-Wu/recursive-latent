class _Normalize:
    def __init__(self, mean, std):
        import torch
        self.mean = torch.tensor(mean).view(1, -1, 1, 1)
        self.std = torch.tensor(std).view(1, -1, 1, 1)
    def __call__(self, x):
        return (x - self.mean.to(x.device, x.dtype)) / self.std.to(x.device, x.dtype)
class _Compose:
    def __init__(self, ops): self.ops = ops
    def __call__(self, x):
        for op in self.ops: x = op(x)
        return x
class _Transforms:
    Normalize = _Normalize
    Compose = _Compose
transforms = _Transforms()
