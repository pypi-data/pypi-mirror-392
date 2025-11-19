from __future__ import annotations
import numpy as np
from typing import Mapping, Any, Optional, Set
from ..core.metrics_base import Metric
from ..core.registry import register
from ..core.types import Video, MetricResult


@register
class PSNR(Metric):
    """
    Peak Signal-to-Noise Ratio (dB), averaged over frames.
    - Assumes inputs are uint8 RGB frames by default (max_pixel=255).
    """

    name = "psnr"
    requires_reference = True
    higher_is_better = True  # Higher PSNR scores are better
    enabled_by_default = False # PSNR is a part of VMAF, so we don't need to enable it by default

    @classmethod
    def get_settings(cls) -> dict[str, bool]:
        # max_pixel is optional (use 255 for uint8)
        return {"max_pixel": False}

    @classmethod
    def get_setting_defaults(cls) -> dict[str, Any]:
        return {"max_pixel": 255.0}

    @classmethod
    def normalize(cls, value: float) -> float:
        import math

        x0 = 30.0  # midpoint of transition (20–40 range)
        k = 0.25  # steepness; higher = sharper transition
        return 1.0 / (1.0 + math.exp(-k * (value - x0)))  # sigmoid function

    def init(self, settings: Mapping[str, Any]) -> None:
        self.maxp = float(settings.get("max_pixel", 255.0))

    def evaluate(
        self, video: Video, reference: Optional[Video], params: Mapping[str, Any]
    ) -> MetricResult:
        assert reference is not None, "PSNR requires a reference video"
        A = list(video)
        B = list(reference)
        n = min(len(A), len(B))
        if n == 0:
            return (self.name, float("nan"), {"note": "no overlapping frames"})

        vals = []
        for a, b in zip(A[:n], B[:n]):
            a32 = a.astype(np.float32)
            b32 = b.astype(np.float32)
            mse = float(np.mean((a32 - b32) ** 2))
            if mse == 0.0:
                vals.append(float("inf"))
            else:
                vals.append(20.0 * np.log10(self.maxp) - 10.0 * np.log10(mse))
        score = float(np.mean(vals))
        return (self.name, score, {"per_frame": vals, "paired_frames": n})
