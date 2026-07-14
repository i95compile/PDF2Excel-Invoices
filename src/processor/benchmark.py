"""
Benchmarking utilities for InvoiceFlow.

Measures elapsed time, throughput, worker count, and optional CPU usage.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import config as root_config
from src.processor.config import ProcessorConfig, resolve_worker_count
from src.processor.logger import get_logger
from src.processor.pipeline import process_invoices
from src.processor.utils import list_pdf_files

logger = get_logger(__name__)

try:
    import psutil
except ImportError:  # pragma: no cover - optional at runtime
    psutil = None  # type: ignore


@dataclass
class BenchmarkResult:
    """Structured benchmark metrics."""

    invoices_processed: int
    workers: int
    mode: str
    elapsed_sec: float
    pdfs_per_sec: float
    cpu_percent: Optional[float]
    input_dir: str
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def format_benchmark_summary(result: BenchmarkResult) -> str:
    """Pretty console summary used by CLI and demos."""
    cpu_line = (
        f"CPU usage: {result.cpu_percent:.1f}%"
        if result.cpu_percent is not None
        else "CPU usage: n/a (install psutil)"
    )
    return "\n".join(
        [
            "------------------------------------",
            f"Invoices processed: {result.invoices_processed}",
            f"Workers: {result.workers}",
            f"Mode: {result.mode}",
            f"Elapsed: {result.elapsed_sec:.1f} sec",
            "Average:",
            f"{result.pdfs_per_sec:.2f} PDFs/sec",
            cpu_line,
            "------------------------------------",
        ]
    )


def run_benchmark(
    input_dir: str | Path,
    *,
    workers: str | int = "auto",
    mode: str | None = None,
    output_file: str | Path | None = None,
    save_report: bool = True,
) -> BenchmarkResult:
    """
    Process all PDFs in ``input_dir`` and return timing metrics.

    Writes a JSON report under ``benchmarks/`` when ``save_report`` is True.
    """
    pdfs = list_pdf_files(input_dir)
    worker_count = resolve_worker_count(workers)
    resolved_mode = mode or (
        "sequential" if worker_count <= 1 else "multiprocessing"
    )

    out = Path(output_file) if output_file else (
        root_config.DEFAULT_OUTPUT_DIR / "benchmark_result.xlsx"
    )

    cpu_before = _sample_cpu()
    started = time.perf_counter()

    process_invoices(
        input_dir=input_dir,
        output_file=out,
        workers=worker_count,
        mode=resolved_mode,
        show_progress=True,
    )

    elapsed = time.perf_counter() - started
    cpu_after = _sample_cpu()
    cpu_percent = None
    if cpu_before is not None and cpu_after is not None:
        cpu_percent = round((cpu_before + cpu_after) / 2.0, 1)

    count = len(pdfs)
    result = BenchmarkResult(
        invoices_processed=count,
        workers=worker_count,
        mode=resolved_mode,
        elapsed_sec=round(elapsed, 3),
        pdfs_per_sec=round(count / elapsed, 2) if elapsed > 0 else 0.0,
        cpu_percent=cpu_percent,
        input_dir=str(Path(input_dir)),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    summary = format_benchmark_summary(result)
    print(summary)
    logger.info("Benchmark complete:\n%s", summary)

    if save_report:
        _save_report(result)

    return result


def compare_modes(
    input_dir: str | Path,
    *,
    workers: str | int = "auto",
) -> dict[str, BenchmarkResult]:
    """
    Run sequential vs multiprocessing benchmarks for easy comparisons.

    TODO: Add CSV/chart export for YouTube / LinkedIn demo visuals.
    """
    sequential = run_benchmark(
        input_dir,
        workers=1,
        mode="sequential",
        output_file=root_config.DEFAULT_OUTPUT_DIR / "benchmark_sequential.xlsx",
        save_report=True,
    )
    parallel = run_benchmark(
        input_dir,
        workers=workers,
        mode="multiprocessing",
        output_file=root_config.DEFAULT_OUTPUT_DIR / "benchmark_parallel.xlsx",
        save_report=True,
    )
    return {"sequential": sequential, "multiprocessing": parallel}


def _sample_cpu() -> Optional[float]:
    if psutil is None:
        return None
    # First call after import may return 0.0; small interval improves accuracy
    return float(psutil.cpu_percent(interval=0.2))


def _save_report(result: BenchmarkResult) -> Path:
    root_config.BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = root_config.BENCHMARK_DIR / f"benchmark_{stamp}.json"
    path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    logger.info("Saved benchmark report: %s", path)
    return path
