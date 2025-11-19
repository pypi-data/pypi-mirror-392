from __future__ import annotations
from typing import Mapping, Any, Optional, Set
import json as _json
import subprocess, tempfile, os, pathlib

from ..core.metrics_base import Metric
from ..core.registry import register
from ..core.types import Video, MetricResult

_VMAF_ERR = (
    "VMAF requires ffmpeg with libvmaf enabled.\n"
    "On many systems: sudo apt install ffmpeg libvmaf or use conda-forge ffmpeg"
)


@register
class VMAF(Metric):
    """
    Video Multimethod Assessment Fusion (VMAF) via ffmpeg/libvmaf.
    Requires a reference video.
    Uses original video files directly (paths provided via params).
    """

    name = "vmaf"
    requires_reference = True
    higher_is_better = True  # Higher VMAF scores are better
    enabled_by_default = False

    @classmethod
    def get_settings(cls) -> dict[str, bool]:
        return {"model": False}

    @classmethod
    def get_setting_defaults(cls) -> dict[str, Any]:
        # "vmaf_v0.6.1.json" is a common default; ffmpeg may choose latest if omitted
        return {"model": "auto"}

    @classmethod
    def normalize(cls, value: float) -> float:
        return value / 100.0

    def init(self, settings: Mapping[str, Any]) -> None:
        self.model = str(settings.get("model", "auto"))

    def evaluate(
        self, video: Video, reference: Optional[Video], params: Mapping[str, Any]
    ) -> MetricResult:
        if reference is None:
            raise ValueError("VMAF requires a reference video")

        # Get original video paths from params (provided by pipeline via cfg)
        video_uri = params.get("video")
        ref_uri = params.get("reference")

        if not video_uri or not isinstance(video_uri, str):
            raise ValueError("VMAF requires 'video' path in params")
        if not ref_uri:
            raise ValueError("VMAF requires 'reference' path in params")

        # Handle reference as single path or list
        if isinstance(ref_uri, list):
            if not ref_uri:
                raise ValueError("VMAF requires at least one reference video")
            ref_uri = ref_uri[0]

        if not isinstance(ref_uri, str):
            raise ValueError("VMAF reference must be a file path")

        if not os.path.exists(video_uri):
            raise FileNotFoundError(f"Video file not found: {video_uri}")
        if not os.path.exists(ref_uri):
            raise FileNotFoundError(f"Reference video file not found: {ref_uri}")

        gen_path = video_uri
        ref_path = ref_uri

        with tempfile.TemporaryDirectory() as td:
            out_json = os.path.join(td, "vmaf.json")

            # Build ffmpeg command
            # Example filter: libvmaf=model=path=...:log_path=...:log_fmt=json
            if self.model == "auto":
                vmaf_filter = f"libvmaf=log_path={out_json}:log_fmt=json"
            else:
                # if custom model path provided
                vmaf_filter = (
                    f"libvmaf=model=path={self.model}:log_path={out_json}:log_fmt=json"
                )

            cmd = [
                "ffmpeg",
                "-v",
                "error",
                "-i",
                gen_path,
                "-i",
                ref_path,
                "-lavfi",
                vmaf_filter,
                "-f",
                "null",
                "-",
            ]

            try:
                subprocess.run(
                    cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
            except Exception as e:
                raise RuntimeError(_VMAF_ERR) from e

            # Parse VMAF JSON
            try:
                with open(out_json, "r", encoding="utf-8") as f:
                    data = _json.load(f)
            except Exception as e:
                raise RuntimeError("Failed to read VMAF JSON output") from e

        # Extract per-frame and mean
        frames = data.get("frames", [])
        per_frame = []
        for fr in frames:
            metrics = fr.get("metrics", {})
            if "vmaf" in metrics:
                per_frame.append(float(metrics["vmaf"]))
        score = float(sum(per_frame) / len(per_frame)) if per_frame else float("nan")
        return (
            self.name,
            score,
            {"per_frame": per_frame, "n_frames_scored": len(per_frame)},
        )
