from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable
import time, json, hashlib, pathlib, os, sys

from .types import InputItem


@dataclass
class MetricEntry:
    """Result of a single metric evaluation."""

    name: str
    score: Optional[float] = None
    status: str = "ok"  # "ok" | "error"
    weight: float = 1.0
    settings: Dict[str, Any] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    extras: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timing_ms: Optional[float] = None


@dataclass
class Report:
    """Container for all results of one evaluation run."""

    run: Dict[str, Any] = field(
        default_factory=dict
    )  # metadata (timestamp, device, etc.)
    inputs: Optional[InputItem] = None  # input video info
    metrics: List[MetricEntry] = field(default_factory=list)
    composite: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    # --- helpers ---
    @staticmethod
    def now_utc() -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    @staticmethod
    def config_hash(cfg: dict) -> str:
        blob = json.dumps(cfg, sort_keys=True, ensure_ascii=False).encode()
        return hashlib.sha256(blob).hexdigest()[:8]

    def add_metric(self, entry: MetricEntry) -> None:
        self.metrics.append(entry)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)

    def aggregate(self, weights: Optional[Dict[str, float]] = None) -> None:
        """Compute weighted average score across all ok metrics using normalized scores.
        
        All metrics should normalize to higher_is_better=True in their normalize() methods.
        """
        from .registry import get_metric_cls

        weights = weights or {}
        total = 0.0
        total_w = 0.0
        for m in self.metrics:
            if m.status != "ok" or m.score is None:
                continue

            # Normalize the score using the metric's normalize function
            # normalize() should handle inversion for lower_is_better metrics
            normalized_score = m.score
            try:
                metric_cls = get_metric_cls(m.name)
                normalized_score = metric_cls.normalize(m.score)
            except (KeyError, Exception):
                # If metric not found in registry or normalize fails, use raw score
                self.add_error(f"Metric {m.name} not found in registry or normalize failed")
                pass

            w = float(weights.get(m.name, m.weight))
            total += w * normalized_score
            total_w += w
        self.composite = {
            "score": (total / total_w) if total_w > 0 else None,
            "weights": weights,
            "enabled": bool(self.metrics),
        }

    def print(
        self,
        index: int,
        parse_errors: List[str],
        colorize: Callable[[str, str], str],
        format_pct_diff: Callable[[Optional[float], bool], str],
        colors: Any,
        get_higher_is_better: Callable[[str], bool],
    ) -> bool:
        """Print a single report. Returns True if there were errors."""
        print(f"== Surveyor2 report [{index}] ==")
        print(f"started_at: {self.run.get('started_at')}")
        print(f"device:     {self.run.get('device')}")

        print(f"video:      {self.inputs.video}")

        if parse_errors:
            print("parse_errors:")
            for e in parse_errors:
                print(f"  - {e}")

        print("metrics:")
        for m in self.metrics:
            pct_diff = None
            if hasattr(m, "extras") and isinstance(m.extras, dict):
                pct_diff = m.extras.get("pct_diff")

            status = getattr(m, "status", "ok")
            score = getattr(m, "score", None)
            err = getattr(m, "error", None)

            if status != "ok":
                # Print error in score field
                error_msg = err if err else "error"
                print(f"  - {m.name}: {error_msg}")
            else:
                score_str = f"{score:.4f}" if score is not None else "None"
                higher_is_better = get_higher_is_better(m.name)
                pct_str = format_pct_diff(pct_diff, higher_is_better)

                if pct_str:
                    print(
                        f"  - {m.name}: {score_str}, %Δ={pct_str}"
                    )
                else:
                    print(f"  - {m.name}: {score_str}")

        if self.composite.get("enabled"):
            composite_score = self.composite.get("score")
            if composite_score is not None:
                score_str = f"{composite_score:.4f}"
                print(f"  composite: {colorize(score_str, colors.CYAN)}")
            else:
                print(f"  composite: {composite_score}")

        print()
        return bool(self.errors)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(asdict(self), indent=indent, ensure_ascii=False)

    @classmethod
    def from_json(cls, s: str) -> Report:
        d = json.loads(s)
        # reconstruct MetricEntry objects
        metrics = [MetricEntry(**m) for m in d.get("metrics", [])]
        d["metrics"] = metrics
        return cls(**d)


@dataclass
class BatchReport:
    """
    Aggregated result of evaluating multiple inputs.
    - reports: list of per-item Report objects
    - summary: per-metric statistics across reports: { metric: {min, max, avg} }
    """

    run: Dict[str, Any] = field(default_factory=dict)
    reports: List[Report] = field(default_factory=list)
    summary: Dict[str, Dict[str, float]] = field(default_factory=dict)
    composite_summary: Dict[str, float] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def compute_summary(self) -> None:
        scores_by_metric: Dict[str, List[float]] = {}
        for rpt in self.reports:
            for m in rpt.metrics:
                if m.status == "ok" and m.score is not None:
                    scores_by_metric.setdefault(m.name, []).append(float(m.score))

        out: Dict[str, Dict[str, float]] = {}
        for name, vals in scores_by_metric.items():
            if not vals:
                continue
            vmin = min(vals)
            vmax = max(vals)
            avg = sum(vals) / float(len(vals))
            out[name] = {"min": vmin, "max": vmax, "avg": avg}
        self.summary = out

        # Composite score summary across reports
        composite_scores: List[float] = []
        for rpt in self.reports:
            try:
                if rpt.composite.get("enabled"):
                    s = rpt.composite.get("score")
                    if s is not None:
                        composite_scores.append(float(s))
            except Exception:
                # if composite block is not present or malformed, skip
                pass
        if composite_scores:
            self.composite_summary = {
                "min": min(composite_scores),
                "max": max(composite_scores),
                "avg": sum(composite_scores) / float(len(composite_scores)),
            }
        else:
            self.composite_summary = {}

        # Aggregate errors from all reports
        all_errors: List[Dict[str, Any]] = []
        for rpt in self.reports:
            input_id = rpt.inputs.id or "unknown"

            # Collect metric-level errors
            for m in rpt.metrics:
                if m.status == "error" or m.error is not None:
                    all_errors.append(
                        {"id": input_id, "metric_name": m.name, "error": m.error}
                    )

            # Collect report-level errors
            for err in rpt.errors:
                all_errors.append({"id": input_id, "metric_name": None, "error": err})

        self.errors = all_errors

    def print_summary(
        self,
        colorize: Callable[[str, str], str],
        format_pct_diff: Callable[[Optional[float], bool], str],
        colors: Any,
        get_higher_is_better: Callable[[str], bool],
    ) -> None:
        """Print batch-level summary statistics."""
        # Collect baseline statistics
        baseline_summary = {}
        pct_diff_summary = {}
        composite_baseline_avgs = []
        composite_pct_deltas = []
        
        for report in self.reports:
            for metric in report.metrics:
                if metric.status != "ok" or metric.score is None:
                    continue
                name = metric.name
                if isinstance(metric.extras, dict):
                    baseline = metric.extras.get("baseline", {})
                    pct_diff = metric.extras.get("pct_diff")

                    if isinstance(baseline, dict) and baseline.get("avg") is not None:
                        if name not in baseline_summary:
                            baseline_summary[name] = []
                        baseline_summary[name].append(float(baseline["avg"]))

                    if pct_diff is not None:
                        if name not in pct_diff_summary:
                            pct_diff_summary[name] = []
                        pct_diff_summary[name].append(float(pct_diff))
            
            # Collect composite baseline statistics
            if isinstance(report.composite, dict):
                composite_baseline = report.composite.get("baseline")
                composite_pct_delta = report.composite.get("pct_delta")
                
                if isinstance(composite_baseline, dict) and composite_baseline.get("avg") is not None:
                    composite_baseline_avgs.append(float(composite_baseline["avg"]))
                
                if composite_pct_delta is not None:
                    composite_pct_deltas.append(float(composite_pct_delta))

        # Print combined summary
        has_baseline = bool(baseline_summary or composite_baseline_avgs)
        if has_baseline:
            print("== Batch summary (min/max/avg) + Baseline (ref avg / avg %Δ) ==")
        else:
            print("== Batch summary (min/max/avg) ==")
        
        # Print regular metrics
        for name in sorted(self.summary.keys()):
            s = self.summary[name]
            min_val = f"{s['min']:.4f}"
            max_val = f"{s['max']:.4f}"
            avg_val = f"{s['avg']:.4f}"
            
            baseline_info = ""
            if name in baseline_summary and baseline_summary[name]:
                baseline_avg = sum(baseline_summary[name]) / len(baseline_summary[name])
                avg_pct_diff = ""
                if name in pct_diff_summary and pct_diff_summary[name]:
                    avg_pct_val = sum(pct_diff_summary[name]) / len(
                        pct_diff_summary[name]
                    )
                    higher_is_better = get_higher_is_better(name)
                    avg_pct_diff = f", avg %Δ={format_pct_diff(avg_pct_val, higher_is_better)}"
                baseline_info = f", baseline_avg={baseline_avg:.4f}{avg_pct_diff}"
            
            print(f"- {name}: min={min_val}, max={max_val}, avg={avg_val}{baseline_info}")
        
        # Print composite summary
        if self.composite_summary:
            cs = self.composite_summary
            min_val = colorize(f"{cs['min']:.4f}", colors.CYAN)
            max_val = colorize(f"{cs['max']:.4f}", colors.CYAN)
            avg_val = colorize(f"{cs['avg']:.4f}", colors.CYAN)
            
            composite_baseline_info = ""
            if composite_baseline_avgs:
                composite_baseline_avg = sum(composite_baseline_avgs) / len(composite_baseline_avgs)
                avg_composite_pct_delta = ""
                if composite_pct_deltas:
                    avg_pct_val = sum(composite_pct_deltas) / len(composite_pct_deltas)
                    # Composite is generally better when higher (weighted average of normalized scores)
                    avg_composite_pct_delta = f", avg %Δ={format_pct_diff(avg_pct_val, True)}"
                composite_baseline_info = f", baseline_avg={composite_baseline_avg:.4f}{avg_composite_pct_delta}"
            
            print(f"composite: min={min_val}, max={max_val}, avg={avg_val}{composite_baseline_info}")

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(asdict(self), indent=indent, ensure_ascii=False)

    @classmethod
    def from_json(cls, s: str) -> "BatchReport":
        d = json.loads(s)
        # reconstruct nested Report/MetricEntry
        reports: List[Report] = []
        for r in d.get("reports", []):
            metrics = [MetricEntry(**m) for m in r.get("metrics", [])]
            r["metrics"] = metrics
            reports.append(Report(**r))
        d["reports"] = reports
        return cls(**d)
