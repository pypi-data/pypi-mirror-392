from .pdf_doc import PDFDoc
from .pdf_doc_batch import PDFDocBatch
from .signature_detector import SignatureDetector, Signature

"""
PDF processing toolkit providing:

- PDFDoc: represents a single PDF, with text extraction, section parsing,
  semantic search, and signature detection support.

- PDFDocBatch: utility for batch-loading and batch-searching PDFs.

- SignatureDetector: low-level signature detection engine
  (use PDFDoc.search_signature() for intended usage).

This module exposes the public-facing API of the package.
"""

__all__ = [
    "PDFDoc",
    "PDFDocBatch",
    "SignatureDetector",
    "Signature",
]