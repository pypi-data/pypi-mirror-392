from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import time

from .metrics_base import Metric

from .parser import parse_metrics_block
from .report import Report, MetricEntry
from .utils import with_progress
from .types import MetricConfig, InputItem
from dataclasses import asdict


@dataclass
class MetricInstance:
    inst: Metric
    settings: Dict[str, Any]
    params: Dict[str, Any]
    init_ms: int


class MetricsPipeline:
    """
    Minimal pipeline:
      - parse/resolve metric settings & params
      - init all metrics
      - run evaluate() for each metric
      - collect into Report (no I/O; videos are iterables of frames)
    """

    def __init__(
        self, *, continue_on_error: bool = True, metrics_block: List[MetricConfig] = [], silent: bool = False
    ):
        self.continue_on_error = continue_on_error
        self._silent = silent
        self._instances: List[MetricInstance] = []
        self._parse_errors: List[str] = []
        self.initialize_metrics(metrics_block)

    def initialize_metrics(self, metrics_block: List[MetricConfig]) -> List[str]:
        """
        Parse and initialize metrics once for the pipeline lifecycle.
        Returns list of parse errors.
        """
        # Parse/resolve metrics
        parsed, parse_errors = parse_metrics_block(metrics_block)
        self._parse_errors = list(parse_errors)
        self._instances = []
        if parse_errors and not self.continue_on_error:
            return self._parse_errors

        # Init all metrics once
        for m in parsed:
            metric_cls = m.cls
            settings = m.settings
            params = m.params
            inst = metric_cls()  # type: ignore[call-arg]
            t0 = time.time()
            try:
                inst.init(settings)
                init_ms = int((time.time() - t0) * 1000)
                self._instances.append(
                    MetricInstance(
                        inst=inst, settings=settings, params=params, init_ms=init_ms
                    )
                )
            except Exception as _:
                # Record as parse-like error for visibility; defer specific per-item entry to run
                self._parse_errors.append(
                    f"{getattr(metric_cls, 'name', 'metric')}: init failed"
                )
                if not self.continue_on_error:
                    return self._parse_errors
        return self._parse_errors

    def teardown(self) -> None:
        # Teardown all initialized metrics once at the end of batch
        for instance in self._instances:
            try:
                instance.inst.teardown()
            except Exception:
                pass

    def run(
        self,
        *,
        video,  # iterable of frames (list[np.ndarray] in tests)
        reference=None,  # iterable of frames or None
        cfg: Optional[InputItem] = None,
        aggregate_weights: Optional[Dict[str, float]] = None,
        metric_names: Optional[List[str]] = None,
    ) -> Tuple[Report, List[str]]:
        """
        Returns:
          - Report with per-metric results (and composite if weights provided)
          - List[str] of parse errors (e.g., missing required settings)
        
        Args:
          metric_names: Optional list of metric names to run. If None, runs all metrics.
                       Useful for filtering metrics without reinitializing them.
        """
        rpt = Report(
            run={
                "started_at": Report.now_utc(),
                "continue_on_error": self.continue_on_error,
                "config_hash": Report.config_hash({}),
            },
            inputs=cfg,
        )

        # 1) surface any initialization/parse errors
        for e in self._parse_errors:
            rpt.add_error(e)
        if self._parse_errors and not self.continue_on_error:
            return rpt, list(self._parse_errors)

        # 2) Filter instances if metric_names is provided
        instances_to_run = self._instances
        if metric_names is not None:
            metric_names_set = set(metric_names)
            instances_to_run = [
                inst for inst in self._instances
                if inst.inst.name in metric_names_set
            ]

        # 3) evaluate each metric using pre-initialized instances
        iterator = with_progress(
            instances_to_run, desc="Metrics", unit="metric", position=1, silent=self._silent
        )

        for metric_instance in iterator:
            metric_name = metric_instance.inst.name
            if hasattr(iterator, "set_description"):
                iterator.set_description(f"Metric: {metric_name}")
            entry = MetricEntry(name=metric_instance.inst.name, settings=metric_instance.settings, params=metric_instance.params)  # type: ignore[attr-defined]
            t0 = time.time()
            try:
                # Inject per-item inputs context for metrics that need it (e.g., CLIPScore prompt)
                params_with_cfg = dict(metric_instance.params)
                if cfg is not None:
                    try:
                        params_with_cfg.update(asdict(cfg))
                    except Exception:
                        pass
                name, score, extras = metric_instance.inst.evaluate(
                    video, reference, params_with_cfg
                )
                eval_ms = int((time.time() - t0) * 1000)
                entry.status = "ok"
                entry.score = float(score)
                entry.extras = extras
                entry.timing_ms = metric_instance.init_ms + eval_ms
            except Exception as ex:
                entry.status = "error"
                entry.error = f"evaluate failed: {ex}"
                if not self.continue_on_error:
                    rpt.add_metric(entry)
                    return rpt, list(self._parse_errors)
            rpt.add_metric(entry)

        # 4) optional aggregation (only if running all metrics or weights are provided)
        if aggregate_weights:
            # Filter weights to only include metrics that were actually run
            filtered_weights = {
                name: weight
                for name, weight in aggregate_weights.items()
                if name in {inst.inst.name for inst in instances_to_run}
            }
            rpt.aggregate(filtered_weights)
        else:
            rpt.aggregate({})  # still set composite.enabled/score (score may be None)

        return rpt, list(self._parse_errors)
