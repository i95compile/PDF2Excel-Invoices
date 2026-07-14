"""
Invoice Processor package.

Extract structured data from PDF invoices and export to Excel.
Designed so OCR / AI extractors can plug in later via ``BaseExtractor``.
"""

from src.processor.pipeline import process_invoices

__all__ = ["process_invoices"]
