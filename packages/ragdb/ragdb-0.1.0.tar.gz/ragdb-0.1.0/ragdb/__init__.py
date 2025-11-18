"""
RAGdb core package.

This package exposes the `RAGdb` class, which implements a small,
embedded document store backed by SQLite with TF–IDF based similarity
search. It supports ingestion of plain text, JSON, CSV, Excel, PDF,
DOCX, images (with OCR text when possible), and basic audio/video metadata.
"""

from .core import RAGdb

__all__ = ["RAGdb"]
