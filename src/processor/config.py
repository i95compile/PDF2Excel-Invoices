"""Processor-specific configuration and worker resolution."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import config as root_config


@dataclass(frozen=True)
class ProcessorConfig:
    """Runtime options for invoice processing."""

    input_dir: Path
    output_file: Path
    workers: int
    mode: str  # sequential | multiprocessing
    show_progress: bool = True

    @classmethod
    def from_cli(
        cls,
        input_dir: str | Path,
        output_file: str | Path,
        workers: str | int = "auto",
        mode: str | None = None,
        show_progress: bool = True,
    ) -> ProcessorConfig:
        """Build config from CLI-facing arguments."""
        resolved_workers = resolve_worker_count(workers)
        resolved_mode = mode or root_config.PROCESSING_MODE
        if resolved_workers <= 1:
            resolved_mode = "sequential"
        return cls(
            input_dir=Path(input_dir),
            output_file=Path(output_file),
            workers=resolved_workers,
            mode=resolved_mode,
            show_progress=show_progress,
        )


def resolve_worker_count(workers: str | int | None = None) -> int:
    """
    Resolve worker count from CLI / env.

    - ``auto`` / None → ``os.cpu_count()`` (fallback 1)
    - integer string or int → that many workers
    """
    if workers is None:
        workers = root_config.WORKERS

    if isinstance(workers, int):
        return max(1, workers)

    value = str(workers).strip().lower()
    if value in {"auto", ""}:
        return max(1, os.cpu_count() or 1)

    try:
        return max(1, int(value))
    except ValueError as exc:
        raise ValueError(
            f"Invalid workers value: {workers!r}. Use 'auto' or an integer."
        ) from exc
