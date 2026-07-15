"""Minimal torchvision stub for Trellis2 no-op rembg imports.

The Trellis2 pipeline imports ``from torchvision import transforms`` while this
project replaces the background remover with a no-op. Some remote environments
have Torch wheels newer than the available torchvision wheel, causing import
failure before the no-op can be installed. This stub provides only the transform
objects required for module import and is meant to be used through a run-local
PYTHONPATH prefix, not as a general torchvision replacement.
"""

from . import io, transforms

__all__ = ["io", "transforms"]
