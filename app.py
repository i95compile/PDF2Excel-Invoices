#!/usr/bin/env python3
"""
InvoiceFlow — CLI entry point.

Commands:
    generate   Create demo invoice PDFs
    process    Extract invoice data → Excel
    benchmark  Measure processing throughput
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path when running ``python app.py``
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config as root_config
from src.processor.logger import setup_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="invoiceflow",
        description="InvoiceFlow - generate and process PDF invoices at scale.",
    )
    parser.add_argument(
        "--log-level",
        default=root_config.LOG_LEVEL,
        help="Logging level (DEBUG, INFO, WARNING, ERROR).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ------------------------------------------------------------------
    # generate
    # ------------------------------------------------------------------
    gen = subparsers.add_parser(
        "generate",
        help="Generate realistic demo invoice PDFs.",
    )
    gen.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of invoices to generate (default: 100).",
    )
    gen.add_argument(
        "--output",
        type=str,
        default=str(root_config.DEFAULT_INPUT_DIR),
        help="Output folder for generated PDFs (default: invoices/).",
    )

    # ------------------------------------------------------------------
    # process
    # ------------------------------------------------------------------
    proc = subparsers.add_parser(
        "process",
        help="Extract data from invoice PDFs into Excel.",
    )
    proc.add_argument(
        "--input",
        type=str,
        default=str(root_config.DEFAULT_INPUT_DIR),
        help="Folder containing PDF invoices.",
    )
    proc.add_argument(
        "--output",
        type=str,
        default=str(root_config.DEFAULT_OUTPUT_FILE),
        help="Destination Excel workbook path.",
    )
    proc.add_argument(
        "--workers",
        default=root_config.WORKERS,
        help="Worker processes: 'auto' or an integer (default: auto).",
    )
    proc.add_argument(
        "--mode",
        choices=["sequential", "multiprocessing"],
        default=None,
        help="Processing mode (default: derived from workers).",
    )

    # ------------------------------------------------------------------
    # benchmark
    # ------------------------------------------------------------------
    bench = subparsers.add_parser(
        "benchmark",
        help="Benchmark processing throughput.",
    )
    bench.add_argument(
        "--input",
        type=str,
        default=str(root_config.DEFAULT_INPUT_DIR),
        help="Folder containing PDF invoices.",
    )
    bench.add_argument(
        "--workers",
        default=root_config.WORKERS,
        help="Worker processes: 'auto' or an integer (default: auto).",
    )
    bench.add_argument(
        "--mode",
        choices=["sequential", "multiprocessing"],
        default=None,
        help="Processing mode override.",
    )
    bench.add_argument(
        "--compare",
        action="store_true",
        help="Run sequential vs multiprocessing comparison.",
    )

    return parser


def cmd_generate(args: argparse.Namespace) -> int:
    from src.invoice_generator import generate_invoices

    paths = generate_invoices(output_folder=args.output, count=args.count)
    print(f"Generated {len(paths)} invoice(s) -> {args.output}")
    return 0


def cmd_process(args: argparse.Namespace) -> int:
    from src.processor import process_invoices

    invoices = process_invoices(
        input_dir=args.input,
        output_file=args.output,
        workers=args.workers,
        mode=args.mode,
    )
    print(f"Processed {len(invoices)} invoice(s) -> {args.output}")
    return 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    from src.processor.benchmark import compare_modes, run_benchmark

    if args.compare:
        compare_modes(args.input, workers=args.workers)
    else:
        run_benchmark(
            args.input,
            workers=args.workers,
            mode=args.mode,
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    root_config.ensure_runtime_directories()
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging(level=args.log_level)

    handlers = {
        "generate": cmd_generate,
        "process": cmd_process,
        "benchmark": cmd_benchmark,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
