from __future__ import annotations
from typing import Mapping, Any, Optional
import tempfile
import os
import warnings
import logging
from contextlib import redirect_stdout, redirect_stderr

from ..core.metrics_base import Metric
from ..core.registry import register
from ..core.types import Video, MetricResult

_VBENCH_ERR = (
    "VBench metrics require the 'vbench' package.\n"
    "Install with: pip install vbench"
)

# VBench evaluation dimensions (10 key dimensions) with their configuration
VBENCH_DIMENSIONS = {
    "subject_consistency": {
        "higher_is_better": True,
        "enabled_by_default": True,
    },
    "background_consistency": {
        "higher_is_better": True,
        "enabled_by_default": True,
    },
    "temporal_flickering": {
        "higher_is_better": False,  # Lower flickering is better
        "enabled_by_default": True,
    },
    "motion_smoothness": {
        "higher_is_better": True,
        "enabled_by_default": True,
    },
    "dynamic_degree": {
        "higher_is_better": True,
        "enabled_by_default": False,
    },
    "aesthetic_quality": {
        "higher_is_better": True,
        "enabled_by_default": False,
    },
    "imaging_quality": {
        "higher_is_better": True,
        "enabled_by_default": True,
    },
    "human_action": {
        "higher_is_better": True,
        "enabled_by_default": False,
    },
    "temporal_style": {
        "higher_is_better": True,
        "enabled_by_default": False,
    },
    "overall_consistency": {
        "higher_is_better": True,
        "enabled_by_default": True,
    },
}


class VBenchMetricBase(Metric):
    """
    Base class for VBench metrics. Can be instantiated with any of the 10 key VBench dimensions.
    
    VBench is a comprehensive evaluation benchmark for text-to-video generation models.
    This implementation includes 10 key quality dimensions for video evaluation.
    """

    requires_reference = False

    def __init__(self, dimension: str):
        """
        Initialize a VBench metric for a specific dimension.
        
        Args:
            dimension: One of the 10 key VBench evaluation dimensions
        """
        if dimension not in VBENCH_DIMENSIONS:
            raise ValueError(
                f"Invalid VBench dimension '{dimension}'. "
                f"Must be one of: {', '.join(VBENCH_DIMENSIONS.keys())}"
            )
        self.dimension = dimension
        self.name = f"vbench_{dimension}"
        dim_config = VBENCH_DIMENSIONS.get(dimension, {})
        self.higher_is_better = dim_config.get("higher_is_better", True)
        self._vbench_kwargs = None

    @classmethod
    def get_settings(cls) -> dict[str, bool]:
        """Settings for VBench metric."""
        return {
            "device": False,
        }

    @classmethod
    def get_setting_defaults(cls) -> dict[str, Any]:
        """Default values for VBench settings."""
        return {
            "device": "cuda",
        }

    def init(self, settings: Mapping[str, Any]) -> None:
        """Initialize the VBench evaluator for this dimension."""
        try:
            # Suppress warnings during VBench import
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                from vbench import VBench
                import vbench as vbench_module
        except ImportError as e:
            raise RuntimeError(_VBENCH_ERR) from e

        # Disable all VBench logging permanently
        logging.getLogger('vbench').setLevel(logging.CRITICAL + 1)

        self.device = str(settings.get("device", "cuda"))
        
        # Auto-detect VBench package directory (internal - not user-configurable)
        # Note: full_info_dir is required by VBench constructor for initialization,
        # but we use mode='custom_input' to evaluate with custom prompts instead
        # of VBench's standard benchmark prompts
        import os
        self.full_info_dir = os.path.dirname(vbench_module.__file__)
        
        # Store VBench initialization kwargs for creating instances per evaluation
        self._vbench_kwargs = {
            "device": self.device,
            "full_info_dir": self.full_info_dir,
        }

    def evaluate(
        self, video: Video, reference: Optional[Video], params: Mapping[str, Any]
    ) -> MetricResult:
        """
        Evaluate a video using the VBench dimension.
        
        Args:
            video: Input video as an iterable of frames
            reference: Not used (VBench doesn't require reference videos)
            params: Required parameters:
                - 'prompt': Text prompt for text-to-video evaluation (required)
                - 'video': Path to the original video file (required, automatically provided by pipeline)
        
        Returns:
            MetricResult tuple: (metric_name, score, extras_dict)
        """
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                from vbench import VBench
        except ImportError:
            return self._error_result("VBench not installed")
        
        # Validate required parameters
        video_path = params.get("video")
        if not video_path:
            return self._error_result("Missing required parameter 'video' (video file path)")
        
        if not isinstance(video_path, str) or not os.path.exists(video_path):
            return self._error_result(f"Invalid video path: {video_path}")
        
        prompt = params.get("prompt")
        if not prompt:
            return self._error_result("Missing required parameter 'prompt'")
        
        # Use the existing video file directly
        frames = list(video)  # Get frame count
        video_filename = os.path.basename(video_path)
        
        # VBench requires videos_path to be a directory containing ONLY the videos to evaluate
        # If we pass the original directory, VBench will try to evaluate ALL videos in it
        # Solution: Create a temp directory with a symlink to just our video
        with tempfile.TemporaryDirectory(prefix="vbench_output_") as output_dir:
            with tempfile.TemporaryDirectory(prefix="vbench_videos_") as video_temp_dir:
                try:
                    # Create symlink to the original video in temp directory
                    video_symlink = os.path.join(video_temp_dir, video_filename)
                    os.symlink(video_path, video_symlink)
                    
                    # Initialize VBench for this evaluation
                    vbench_kwargs = dict(self._vbench_kwargs)
                    vbench_kwargs["output_path"] = output_dir
                    vbench_instance = VBench(**vbench_kwargs)
                    
                    # Run VBench evaluation with custom_input mode
                    # In custom_input mode, prompt_list is a dict: {video_filename: prompt_text}
                    prompt_dict = {video_filename: prompt}
                    
                    eval_name = f"eval_{self.dimension}"
                    
                    # VBench doesn't return results, it saves them to a JSON file
                    # Suppress print statements and warnings during evaluation
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        with open(os.devnull, 'w') as devnull:
                            with redirect_stdout(devnull), redirect_stderr(devnull):
                                vbench_instance.evaluate(
                                    videos_path=video_temp_dir,  # Temp dir with ONLY our video
                                    name=eval_name,
                                    prompt_list=prompt_dict,  # Dict mapping filename to prompt
                                    dimension_list=[self.dimension],
                                    mode="custom_input",  # Use custom prompts, not VBench standard benchmark
                                )
                    
                    # Read results from the JSON file VBench saved
                    results_file = os.path.join(output_dir, f"{eval_name}_eval_results.json")
                    
                    if os.path.exists(results_file):
                        import json
                        with open(results_file, 'r') as f:
                            results = json.load(f)
                        
                        # Extract score for this dimension
                        # VBench returns: {dimension: [score, [video_results]]}
                        if results and self.dimension in results:
                            dimension_result = results[self.dimension]
                            # Extract the score (first element of the list)
                            if isinstance(dimension_result, list) and len(dimension_result) > 0:
                                score = float(dimension_result[0])
                            else:
                                score = float(dimension_result)
                            
                            extras = {
                                "dimension": self.dimension,
                                "prompt": prompt,
                                "frames": len(frames),
                                "video_path": video_path,
                            }
                            return (self.name, score, extras)
                        else:
                            return self._error_result(f"No results for dimension {self.dimension}")
                    else:
                        return self._error_result(f"VBench results file not found: {results_file}")
                        
                except Exception as e:
                    return self._error_result(f"Evaluation failed: {str(e)}")


# Register all 10 VBench dimensions as separate metrics
def _create_vbench_metric_class(dimension: str) -> type:
    """Factory function to create a VBench metric class for a specific dimension."""
    
    class_name = f"VBench_{dimension.title().replace('_', '')}"
    
    class VBenchDimensionMetric(VBenchMetricBase):
        """Auto-generated VBench metric for a specific dimension."""
        
        name = f"vbench_{dimension}"  # Set name at class level for registry
        dim_config = VBENCH_DIMENSIONS.get(dimension, {})
        enabled_by_default = dim_config.get("enabled_by_default", True)
        higher_is_better = dim_config.get("higher_is_better", True)
        
        @classmethod
        def normalize(cls, value: float) -> float:
            """Normalize VBench score to [0, 1] range, inverting if lower_is_better."""
            # VBench scores are typically in [0, 1] range already
            normalized = max(0.0, min(1.0, value))
            # If lower_is_better, invert so higher normalized score = better
            if not cls.higher_is_better:
                normalized = 1.0 - normalized
            return normalized
        
        def __init__(self):
            super().__init__(dimension=dimension)
    
    VBenchDimensionMetric.__name__ = class_name
    VBenchDimensionMetric.__qualname__ = class_name
    
    # Register after class is fully configured
    register(VBenchDimensionMetric)
    
    return VBenchDimensionMetric


# Create and register all 10 VBench metric classes
_vbench_metric_classes = {}
for dim in VBENCH_DIMENSIONS.keys():
    _vbench_metric_classes[dim] = _create_vbench_metric_class(dim)


# Export the base class and all dimension-specific classes
__all__ = ["VBenchMetricBase"] + [cls.__name__ for cls in _vbench_metric_classes.values()]

