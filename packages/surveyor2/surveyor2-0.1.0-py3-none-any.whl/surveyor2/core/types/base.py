"""Base types for Surveyor2."""

from __future__ import annotations
from typing import Iterable, Tuple, Dict, Any
import numpy as np

__all__ = ["Frame", "Video", "MetricResult"]

# Basic video processing types
Frame = np.ndarray  # H x W x C, dtype=uint8
Video = Iterable[Frame]  # e.g., list[Frame]
MetricResult = Tuple[str, float, Dict[str, Any]]  # (metric_name, score, extras)
