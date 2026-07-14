# InvoiceFlow

**High-performance PDF invoice extraction → clean Excel workbooks.**

InvoiceFlow is a production-minded Python toolkit for generating large batches of demo invoices and extracting structured data at scale — with multiprocessing, logging, configuration, and a clean architecture ready for OCR, AI, and commercial productization.

---

## Features

- **Invoice Generator** — create thousands of realistic PDF invoices (Faker + ReportLab)
- **Invoice Processor** — extract invoice number, date, parties, subtotal, and line items
- **Excel export** — professional multi-sheet workbooks (`Invoices` + `LineItems`)
- **Multiprocessing** — `ProcessPoolExecutor` with `--workers auto` or fixed counts
- **Benchmarking** — PDFs/sec, elapsed time, worker count, optional CPU usage
- **Configuration** — `.env` + `config.py` + environment variables
- **Logging** — console + rotating file logs under `logs/`
- **Extensible design** — plugin points for OCR, AI extraction, CSV/JSON, API, GUI

---

## Installation

```bash
# Clone
git clone https://github.com/i95compile/PDF2Excel-Invoices.git
cd PDF2Excel-Invoices

# Create & activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Optional: local configuration
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

**Requirements:** Python 3.10+

---

## Quick start

```bash
# 1) Generate demo invoices
python app.py generate --count 500 --output invoices/

# 2) Process into Excel (auto CPU workers)
python app.py process --input invoices --output output/result.xlsx --workers auto

# 3) Benchmark throughput
python app.py benchmark --input invoices --workers auto
```

---

## Architecture

```
InvoiceFlow/
├── app.py                      # CLI entry point (argparse)
├── config.py                   # Root settings (.env / env vars)
├── requirements.txt
├── invoices/                   # Input PDFs
├── output/                     # Excel results
├── logs/                       # Rotating log files
├── benchmarks/                 # JSON benchmark reports
├── tests/
└── src/
    ├── invoice_generator/      # Module 1 — demo PDF creation
    │   ├── generator.py        # generate_invoices(output_folder, count)
    │   ├── templates.py        # ReportLab layout
    │   └── utils.py            # Fake data helpers
    └── processor/              # Module 2 — extraction product
        ├── pipeline.py         # Orchestration
        ├── parser.py           # PDF I/O (pdfplumber); OCR/AI hooks
        ├── extractor.py        # BaseExtractor + Text / OCR / AI strategies
        ├── worker.py           # Sequential + ProcessPoolExecutor
        ├── excel_writer.py     # pandas + openpyxl export
        ├── benchmark.py        # Throughput measurement
        ├── models.py           # InvoiceData / LineItem dataclasses
        ├── config.py           # Worker resolution
        ├── logger.py           # Console + RotatingFileHandler
        └── utils.py            # Path / money helpers
```

### Design principles

| Layer | Responsibility |
|--------|----------------|
| **CLI (`app.py`)** | Parse args, wire commands |
| **Pipeline** | Discover PDFs → workers → Excel |
| **Extractor strategy** | Map PDF → `InvoiceData` |
| **Parser** | Raw PDF text/tables (swap for OCR later) |
| **Worker** | Sequential vs multiprocessing execution |
| **Exporter** | DataFrames → Excel (CSV/JSON later) |

```
PDF folder
    │
    ▼
list_pdf_files()
    │
    ├─ sequential ──────────────┐
    │                           ▼
    └─ ProcessPoolExecutor ──► TextExtractor ──► InvoiceData[]
                                    │
                                    ▼
                              write_excel()
                                    │
                                    ▼
                              result.xlsx
```

---

## CLI reference

### `generate`

```bash
python app.py generate --count 1000 --output invoices/
```

| Flag | Description | Default |
|------|-------------|---------|
| `--count` | Number of PDFs | `100` |
| `--output` | Output folder | `invoices/` |

### `process`

```bash
python app.py process \
    --input invoices \
    --output output/result.xlsx \
    --workers auto

# Force sequential
python app.py process --input invoices --output output/result.xlsx --workers 1 --mode sequential

# Fixed worker pool
python app.py process --input invoices --output output/result.xlsx --workers 8
```

| Flag | Description | Default |
|------|-------------|---------|
| `--input` | PDF folder | `invoices/` |
| `--output` | Excel path | `output/invoices.xlsx` |
| `--workers` | `auto` or integer | `auto` |
| `--mode` | `sequential` / `multiprocessing` | derived |

### `benchmark`

```bash
python app.py benchmark --input invoices --workers auto

# Compare sequential vs multiprocessing
python app.py benchmark --input invoices --workers auto --compare
```

Example summary:

```
------------------------------------
Invoices processed: 1000
Workers: 12
Mode: multiprocessing
Elapsed: 24.3 sec
Average:
41.15 PDFs/sec
CPU usage: 78.2%
------------------------------------
```

---

## Screenshots

> Place demo images in `docs/screenshots/` and embed them below.

| Demo | Preview |
|------|---------|
| CLI generate | ![Generate](docs/screenshots/generate.gif) |
| Excel output | ![Excel](docs/screenshots/excel.png) |
| Benchmark | ![Benchmark](docs/screenshots/benchmark.png) |

---

## Configuration

Copy `.env.example` → `.env`:

```env
LOG_LEVEL=INFO
WORKERS=auto
PROCESSING_MODE=multiprocessing
DEFAULT_INPUT_DIR=invoices
DEFAULT_OUTPUT_FILE=output/invoices.xlsx
```

All keys are readable via `config.py` and overridable by OS environment variables.

---

## Testing

```bash
pytest -q
pytest --cov=src
```

---

## Benchmarking notes

1. Generate a known dataset (`--count 1000`).
2. Run `benchmark` with `--workers 1` and `--workers auto`.
3. Reports are saved as JSON under `benchmarks/`.
4. Use results for LinkedIn / YouTube performance content.

---

## Roadmap

InvoiceFlow is intentionally future-ready:

| Area | Status | Notes |
|------|--------|-------|
| Text PDF extraction | ✅ | `TextExtractor` + pdfplumber |
| Multiprocessing | ✅ | `ProcessPoolExecutor` |
| Excel export | ✅ | openpyxl styling |
| OCR support | 🧭 Planned | `PdfParser.parse_ocr`, `OcrExtractor` |
| AI extraction | 🧭 Planned | `AiExtractor` + confidence scores |
| CSV / JSON export | 🧭 Planned | Reuse DataFrames from `excel_writer` |
| GUI / drag-and-drop | 🧭 Planned | Thin UI over `process_invoices` |
| REST API | 🧭 Planned | FastAPI wrapping the pipeline |

Extension point: implement `BaseExtractor.extract()` and register it in workers — no pipeline rewrite required.

---

## Project status

**v0.1.0 — Architecture + core pipeline**

Clean module boundaries, working generator & processor, CLI, logging, config, tests, and documented extension points for OCR/AI/GUI/API.

---

## License

MIT (recommended for portfolio / open-source distribution) — add a `LICENSE` file when you publish.

---

## Author

Built as a portfolio-grade Python automation project demonstrating clean architecture, concurrency, and production practices.
