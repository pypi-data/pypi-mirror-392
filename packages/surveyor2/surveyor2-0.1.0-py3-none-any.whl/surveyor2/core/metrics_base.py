# vqeval/core/metrics_base.py
from __future__ import annotations
from typing import Dict, Any, Set, Mapping, Optional
from .types import Video, MetricResult


class Metric:
    """
    Base class for all metrics:
      - Declarative settings/params
      - init() once, evaluate() many, teardown() at end
    
    Subclasses must define:
      - name: str
      - requires_reference: bool
      - higher_is_better: bool
      - get_settings(), get_setting_defaults(), get_params(), normalize()
      - init(), evaluate(), teardown()
    """

    name: str
    requires_reference: bool
    higher_is_better: bool  # True if higher scores are better, False if lower scores are better
    enabled_by_default: bool = True  # If False, metric is excluded from default metrics list

    @classmethod
    def get_settings(cls) -> Dict[str, bool]:
        """Return settings dict mapping setting names to whether they're required."""
        return {}

    @classmethod
    def get_setting_defaults(cls) -> Dict[str, Any]:
        """Return default values for settings."""
        return {}

    @classmethod
    def get_params(cls) -> Set[str]:
        """Return set of parameter names this metric accepts."""
        return set()

    @classmethod
    def normalize(cls, value: float) -> float:
        """Normalize a metric value. Default: return value as-is."""
        return value

    def init(self, settings: Mapping[str, Any]) -> None:
        """Initialize the metric with given settings."""
        pass

    def evaluate(
        self, video: Video, reference: Optional[Video], params: Mapping[str, Any]
    ) -> MetricResult:
        """Evaluate a video and return (name, score, extras). Must be implemented by subclass."""
        raise NotImplementedError

    def teardown(self) -> None:
        """Clean up metric resources."""
        pass

    def _error_result(self, error_message: str) -> MetricResult:
        """
        Helper method to return a standardized error result.
        
        Args:
            error_message: Error message to include in the result
            
        Returns:
            MetricResult tuple with NaN score and error in extras
        """
        return (self.name, float("nan"), {"error": error_message})
