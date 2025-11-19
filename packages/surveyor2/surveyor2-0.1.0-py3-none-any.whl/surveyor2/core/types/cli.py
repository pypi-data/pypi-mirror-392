"""CLI argument type definitions for Surveyor2."""

from __future__ import annotations
from typing import List, Optional, Protocol, Union
from pathlib import Path

__all__ = ["ProfileArgs", "ScaffoldArgs", "InputsArgs", "MarkdownArgs", "PresetsArgs"]


class ProfileArgs(Protocol):
    """
    Arguments for the 'profile' command.

    Attributes:
        command: Subcommand name ('profile')
        inputs: Path to inputs YAML/JSON file
        metrics: Path to metrics YAML/JSON file (optional, uses defaults if not provided)
        preset: Name of metric preset to use (optional, cannot be used with --metrics)
        list: Whether to list registered metrics and exit
        report_json: Path to write JSON report (optional)
        report_html: Path to write HTML report (optional)
        silent: Whether to disable all printing and progress bars
    """

    command: str
    inputs: Optional[str]
    metrics: Optional[str]
    preset: Optional[str]
    list: bool
    report_json: Optional[str]
    report_html: Optional[str]
    silent: bool


class ScaffoldArgs(Protocol):
    """
    Arguments for the 'scaffold' command.

    Attributes:
        command: Subcommand name ('scaffold')
        output: Path to output YAML scaffold file
    """

    command: str
    output: str


class InputsArgs(Protocol):
    """
    Arguments for the 'inputs' command.

    Attributes:
        command: Subcommand name ('inputs')
        reference_videos: List of reference video directories
        generated_videos: Directory containing generated videos
        prompts: Path to JSONL file with prompts
        output: Path to output inputs.yaml file (optional)
    """

    command: str
    reference_videos: List[Path]
    generated_videos: Path
    prompts: str
    output: Optional[str]


class MarkdownArgs(Protocol):
    """
    Arguments for the 'markdown' command.

    Attributes:
        command: Subcommand name ('markdown')
        input: Path to input JSON report file
        output: Path to output markdown file (optional, prints to stdout if not provided)
    """

    command: str
    input: Path
    output: Optional[Path]


class PresetsArgs(Protocol):
    """
    Arguments for the 'presets' command.

    Attributes:
        command: Subcommand name ('presets')
    """

    command: str
