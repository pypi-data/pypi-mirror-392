#!/usr/bin/env python3
"""
Surveyor2 CLI

Usage:
    surveyor2 profile --inputs ... [--metrics ... | --preset ...]
    surveyor2 scaffold --output config.yaml
    surveyor2 inputs --reference-videos ... --generated-videos ...
    surveyor2 markdown --input report.json --output summary.md
    surveyor2 presets
"""
from __future__ import annotations
import argparse
import sys
from typing import List, Optional


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="surveyor2",
        description="Video quality evaluation toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    profile_parser = subparsers.add_parser(
        "profile",
        help="Run video quality evaluation metrics",
        description="Run video quality evaluation metrics on generated videos",
    )
    profile_parser.add_argument(
        "-i", "--inputs", help="Path to INPUTS YAML/JSON (contains 'inputs: [...]')"
    )
    profile_parser.add_argument(
        "-m",
        "--metrics",
        help="Path to METRICS YAML/JSON (contains 'metrics:' and optional 'aggregate:')",
    )
    profile_parser.add_argument(
        "-p",
        "--preset",
        help="Use a metric preset by name (e.g., 'basic', 'fast', 'vbench'). Cannot be used with --metrics.",
    )
    profile_parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List registered metrics with their settings and params, then exit",
    )
    profile_parser.add_argument(
        "-j", "--report-json", help="Path to write BatchReport JSON (optional)"
    )
    profile_parser.add_argument(
        "-H", "--report-html", help="Path to write HTML report (optional)"
    )
    profile_parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="Disable all printing and progress bars",
    )

    scaffold_parser = subparsers.add_parser(
        "scaffold",
        help="Generate YAML scaffold file",
        description="Generate a YAML scaffold file with all registered metrics and their default settings",
    )
    scaffold_parser.add_argument(
        "-o",
        "--output",
        default="metrics.yaml",
        help="Path to output scaffold YAML file (default: metrics.yaml)",
    )

    inputs_parser = subparsers.add_parser(
        "inputs",
        help="Generate Surveyor2 inputs YAML file",
        description="Generate Surveyor2 inputs YAML file from video folders and prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (creates inputs.yaml in current directory)
  surveyor2 inputs \\
    -r ./reference_videos \\
    -g ./generated_videos \\
    -p ./prompts.jsonl

  # Multiple reference directories
  surveyor2 inputs \\
    -r ./reference_videos1 -r ./reference_videos2 \\
    -g ./generated_videos \\
    -p ./prompts.jsonl \\
    -o ./my_inputs.yaml

  # JSONL format (required fields):
  {"id": "video_001", "prompt": "A cat playing with a ball"}
        """,
    )
    inputs_parser.add_argument(
        "-r",
        "--reference-videos",
        required=True,
        action="append",
        help="Directory containing reference videos (can be specified multiple times)",
    )
    inputs_parser.add_argument(
        "-g",
        "--generated-videos",
        required=True,
        help="Directory containing generated videos to evaluate",
    )
    inputs_parser.add_argument(
        "-p",
        "--prompts",
        required=True,
        help="JSONL file containing prompts (one JSON object per line)",
    )
    inputs_parser.add_argument(
        "-o",
        "--output",
        help="Path to output inputs.yaml file (default: inputs.yaml in current directory)",
    )

    markdown_parser = subparsers.add_parser(
        "markdown",
        help="Generate markdown summary table from JSON report",
        description="Generate a markdown summary table from a Surveyor2 JSON report",
    )
    markdown_parser.add_argument(
        "--input", "-i", required=True, help="Path to input JSON report file"
    )
    markdown_parser.add_argument(
        "--output",
        "-o",
        help="Path to output markdown file (if not provided, prints to stdout)",
    )

    presets_parser = subparsers.add_parser(
        "presets",
        help="List available metric presets",
        description="List all available metric presets with their configured metrics",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command == "profile":
        from .driver import run_main

        return run_main(args)
    elif args.command == "scaffold":
        from .commands.scaffold import scaffold_main

        return scaffold_main(args)
    elif args.command == "inputs":
        from .commands.inputs import inputs_main

        return inputs_main(args)
    elif args.command == "markdown":
        from .commands.markdown import markdown_main

        return markdown_main(args)
    elif args.command == "presets":
        from .commands.presets import presets_main

        return presets_main(args)
    else:
        parser.error(f"Unknown command: {args.command}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
