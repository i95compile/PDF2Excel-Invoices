"""Placeholder tests for benchmarking helpers."""

from __future__ import annotations

from src.processor.benchmark import BenchmarkResult, format_benchmark_summary


def test_format_benchmark_summary_contains_key_metrics() -> None:
    result = BenchmarkResult(
        invoices_processed=1000,
        workers=12,
        mode="multiprocessing",
        elapsed_sec=24.3,
        pdfs_per_sec=41.15,
        cpu_percent=75.0,
        input_dir="invoices",
        timestamp="2026-01-01T00:00:00+00:00",
    )
    summary = format_benchmark_summary(result)
    assert "Invoices processed: 1000" in summary
    assert "Workers: 12" in summary
    assert "41.15 PDFs/sec" in summary
