from __future__ import annotations
import json, pathlib, sys, os
from typing import Any, Dict, Tuple, List, Optional

from .core.pipeline import MetricsPipeline
from .core.report import Report, BatchReport
from .core.parser import build_default_metrics_config_from_registry
from .core.registry import print_registered_metrics, get_higher_is_better, get_metric_cls
from .core.utils import with_progress, Colors, colorize, format_percentage_diff
from .core.types import InputItem, InputsConfig, ProfileArgs, ProfileConfig, Frame, MetricConfig
from .metrics import *


def _try_import_imageio():
    try:
        import imageio

        return imageio
    except Exception:
        return None


def decode_video_to_frames(
    uri: str | pathlib.Path, *, max_frames: int | None = None
) -> List[Frame]:
    """
    Best-effort decoder using imageio. Returns list of HxWxC uint8 frames.
    If imageio is unavailable, raises a clear error.
    """
    imageio = _try_import_imageio()
    if imageio is None:
        raise RuntimeError(
            "Video decoding requires imageio. Install with: pip install 'imageio[ffmpeg]'"
        )
    import numpy as np

    path = uri
    reader = imageio.get_reader(path)
    frames = []
    for i, frame in enumerate(reader):
        frame = frame if frame.ndim == 3 else frame[..., None]
        if frame.shape[2] == 4:  # RGBA -> RGB
            frame = frame[..., :3]
        frames.append(frame.astype(np.uint8))
        if max_frames is not None and len(frames) >= max_frames:
            break
    reader.close()
    return frames


def load_raw_config(p: str) -> Dict[str, Any]:
    """Load config file as raw dictionary."""
    path = pathlib.Path(p)
    text = path.read_text()
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml
        except Exception:
            raise RuntimeError(
                "YAML config requested but PyYAML is not installed. pip install pyyaml"
            )
        return yaml.safe_load(text)
    elif path.suffix.lower() == ".json":
        return json.loads(text)
    else:
        raise ValueError(
            f"Unsupported config extension: {path.suffix} (use .yaml/.yml or .json)"
        )


def load_inputs_config(p: str) -> InputsConfig:
    """Load and parse inputs config file."""
    raw_data = load_raw_config(p)
    return InputsConfig.from_dict(raw_data)


def load_metrics_config(p: str) -> ProfileConfig:
    """Load and parse metrics config file."""
    raw_data = load_raw_config(p)
    return ProfileConfig.from_dict(raw_data)


def _compute_baseline_stats(
    ref_videos: List[str], R, pipe, item: InputItem, weights, max_frames: Optional[int], profile_config: ProfileConfig
) -> Dict[str, Dict[str, float]]:
    """Compute baseline statistics from reference videos.
    
    For non-reference metrics: computes stats from all reference videos (even if just one).
    For reference metrics: requires at least 2 reference videos to compare.
    
    If there's only one reference video, skip baseline computation entirely
    (can't compare reference metrics to themselves).
    
    Reuses the main pipeline's metric instances to avoid reinitializing metrics.
    """
    if not ref_videos:
        return {}
    
    # Separate metrics by whether they require reference (by name, not config)
    metric_names_no_ref: List[str] = []
    metric_names_with_ref: List[str] = []
    
    for metric_cfg in profile_config.metrics:
        try:
            metric_cls = get_metric_cls(metric_cfg.name)
            if getattr(metric_cls, "requires_reference", False):
                metric_names_with_ref.append(metric_cfg.name)
            else:
                metric_names_no_ref.append(metric_cfg.name)
        except KeyError:
            # Skip unknown metrics
            continue

    scores_by_metric: Dict[str, List[float]] = {}
    composite_scores: List[float] = []

    # 1. Run non-reference metrics on every single video in ref_videos
    # Reuse the main pipeline's metric instances instead of creating new ones
    if metric_names_no_ref:
        for ref_uri in ref_videos:
            try:
                ref_video = decode_video_to_frames(ref_uri, max_frames=max_frames)
                baseline_item = InputItem(
                    video=ref_uri,
                    reference=ref_videos,
                    max_frames=item.max_frames,
                    id=item.id,
                    prompt=item.prompt,
                )

                ref_report, _ = pipe.run(
                    video=ref_video,
                    reference=None,  # No reference for these metrics
                    cfg=baseline_item,
                    aggregate_weights=weights,
                    metric_names=metric_names_no_ref,  # Only run non-reference metrics
                )
                for m in ref_report.metrics:
                    if m.status == "ok" and m.score is not None:
                        scores_by_metric.setdefault(m.name, []).append(float(m.score))
                
                # Collect composite score if available
                if ref_report.composite.get("enabled") and ref_report.composite.get("score") is not None:
                    composite_scores.append(float(ref_report.composite["score"]))
            except Exception:
                continue

    # 2. Run reference metrics in pairs (r1 vs r2, r1 vs r3, etc.)
    # Reuse the main pipeline's metric instances instead of creating new ones
    if metric_names_with_ref and len(ref_videos) >= 2:
        r1_uri = ref_videos[0]
        r1_frames = decode_video_to_frames(r1_uri, max_frames=max_frames)
        
        for r2_uri in ref_videos[1:]:
            try:
                r2_frames = decode_video_to_frames(r2_uri, max_frames=max_frames)
                baseline_item = InputItem(
                    video=r1_uri,
                    reference=ref_videos,
                    max_frames=item.max_frames,
                    id=item.id,
                    prompt=item.prompt,
                )

                ref_report, _ = pipe.run(
                    video=r1_frames,
                    reference=r2_frames,  # Compare r1 vs r2
                    cfg=baseline_item,
                    aggregate_weights=weights,
                    metric_names=metric_names_with_ref,  # Only run reference metrics
                )
                for m in ref_report.metrics:
                    if m.status == "ok" and m.score is not None:
                        scores_by_metric.setdefault(m.name, []).append(float(m.score))
                
                # Collect composite score if available
                if ref_report.composite.get("enabled") and ref_report.composite.get("score") is not None:
                    composite_scores.append(float(ref_report.composite["score"]))
            except Exception:
                continue

    baseline_stats = {}
    for name, vals in scores_by_metric.items():
        if vals:
            baseline_stats[name] = {
                "min": min(vals),
                "max": max(vals),
                "avg": sum(vals) / float(len(vals)),
                "n": float(len(vals)),
            }
    
    # Store composite baseline statistics
    if composite_scores:
        baseline_stats["_composite"] = {
            "min": min(composite_scores),
            "max": max(composite_scores),
            "avg": sum(composite_scores) / float(len(composite_scores)),
            "n": float(len(composite_scores)),
        }

    return baseline_stats


def _attach_baseline_to_report(
    report: Report, baseline_stats: Dict[str, Dict[str, float]]
) -> None:
    """Attach baseline statistics and percentage deltas to report metrics."""
    if not baseline_stats:
        return

    for m in report.metrics:
        stats = baseline_stats.get(m.name)
        if not stats or m.score is None:
            continue

        m.extras = dict(m.extras or {})
        m.extras["baseline"] = {
            "avg": float(stats.get("avg", float("nan"))),
            "min": float(stats.get("min", float("nan"))),
            "max": float(stats.get("max", float("nan"))),
            "n": int(stats.get("n", 0)),
        }

        base = float(stats.get("avg", float("nan")))
        num = float(m.score) - base
        den = abs(base) if abs(base) > 1e-9 else None
        if den is not None:
            m.extras["pct_diff"] = float((num / den) * 100.0)
        else:
            m.extras["pct_diff"] = None
    
    # Attach composite baseline statistics and delta
    composite_baseline = baseline_stats.get("_composite")
    if composite_baseline and report.composite.get("enabled") and report.composite.get("score") is not None:
        baseline_avg = float(composite_baseline.get("avg", float("nan")))
        current_score = float(report.composite["score"])
        
        # Calculate absolute delta
        delta = current_score - baseline_avg
        
        # Calculate percentage delta
        den = abs(baseline_avg) if abs(baseline_avg) > 1e-9 else None
        pct_delta = float((delta / den) * 100.0) if den is not None else None
        
        # Store in composite extras
        report.composite = dict(report.composite)
        report.composite["baseline"] = {
            "avg": baseline_avg,
            "min": float(composite_baseline.get("min", float("nan"))),
            "max": float(composite_baseline.get("max", float("nan"))),
            "n": int(composite_baseline.get("n", 0)),
        }
        report.composite["delta"] = delta
        report.composite["pct_delta"] = pct_delta


def run_profile(
    inputs_list: List[InputItem], 
    profile_config: ProfileConfig, 
    silent: bool = False
) -> Tuple[BatchReport, List[str]]:
    """
    Drives the pipeline using separate inputs list and metrics config.

    Args:
        inputs_list: List of InputItem objects
        profile_config: ProfileConfig object with metrics and aggregation settings
        silent: If True, disable all printing and progress bars

    Returns:
        Tuple of (BatchReport, parse_errors)
    """
    if not isinstance(inputs_list, list) or not inputs_list:
        raise ValueError("inputs_list must be a non-empty list of input items")

    # Convert MetricConfig objects to dicts for the parser
    weights = profile_config.aggregate.weights

    pipe = MetricsPipeline(metrics_block=profile_config.metrics, silent=silent)
    if not silent:
        print(f"Metrics pipeline initialized with {len(profile_config.metrics)} metrics")
    reports: List[Report] = []
    all_parse_errors: List[str] = []

    iterator = with_progress(
        enumerate(inputs_list),
        desc="Batch",
        unit="item",
        total=len(inputs_list),
        position=0,
        silent=silent,
    )

    for idx, item in iterator:
        if not item.video:
            raise ValueError(f"inputs[{idx}].video is required")

        G = decode_video_to_frames(item.video, max_frames=item.max_frames)

        ref_videos = []
        if item.reference:
            ref_videos = (
                item.reference if isinstance(item.reference, list) else [item.reference]
            )

        R = (
            decode_video_to_frames(ref_videos[0], max_frames=item.max_frames)
            if ref_videos
            else None
        )

        baseline_stats = _compute_baseline_stats(
            ref_videos, R, pipe, item, weights, item.max_frames, profile_config
        )

        report, parse_errors = pipe.run(
            video=G,
            reference=R,
            cfg=item,
            aggregate_weights=weights,
        )

        _attach_baseline_to_report(report, baseline_stats)

        report.inputs.video = item.video
        report.inputs.reference = ref_videos[0] if ref_videos else None
        report.inputs.reference_videos = ref_videos
        report.inputs.max_frames = item.max_frames
        report.inputs.index = idx
        if item.id is not None:
            report.inputs.id = item.id
        if item.prompt is not None:
            report.inputs.prompt = item.prompt

        reports.append(report)
        all_parse_errors.extend(parse_errors)

    try:
        pipe.teardown()
    except Exception:
        pass

    batch = BatchReport(
        run={
            "started_at": Report.now_utc(),
            "count": len(reports),
        },
        reports=reports,
    )
    batch.compute_summary()

    return batch, all_parse_errors


def run_main(args: ProfileArgs) -> int:
    """Main entry point for the run command."""
    if args.list:
        print_registered_metrics()
        return 0

    if not args.inputs:
        import sys

        print("Error: provide --inputs", file=sys.stderr)
        return 1

    inputs_cfg = load_inputs_config(args.inputs)
    if not inputs_cfg.inputs:
        raise SystemExit("inputs file must contain non-empty 'inputs: [...]'")

    inputs_list: List[InputItem] = inputs_cfg.inputs

    # Handle metrics config: preset takes precedence over metrics file
    if args.preset:
        if args.metrics:
            print(
                "Error: Cannot specify both --preset and --metrics. Use one or the other.",
                file=sys.stderr,
            )
            return 1
        from surveyor2.presets import get_preset

        try:
            metrics_config = get_preset(args.preset)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    elif args.metrics:
        metrics_config = load_metrics_config(args.metrics)
    else:
        metrics_config = build_default_metrics_config_from_registry()

    batch, parse_errors = run_profile(inputs_list, metrics_config, silent=args.silent)

    any_errors = False
    for i, report in enumerate(batch.reports):
        has_errors = report.print(
            i,
            parse_errors,
            colorize,
            format_percentage_diff,
            Colors,
            get_higher_is_better,
        )
        any_errors = any_errors or has_errors

    batch.print_summary(colorize, format_percentage_diff, Colors, get_higher_is_better)

    if args.report_json:
        p = pathlib.Path(args.report_json)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(batch.to_json())
    if args.report_html:
        from .core.html_report import render_batch_report_html

        html = render_batch_report_html(batch, title="Surveyor2 Report")
        p = pathlib.Path(args.report_html)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(html)

    return 0 if not any_errors else 1
