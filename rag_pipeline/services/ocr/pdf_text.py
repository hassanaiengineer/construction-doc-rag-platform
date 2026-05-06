from __future__ import annotations

import logging
from pathlib import Path

import fitz  # PyMuPDF

from rag_pipeline.services.ocr.models import PageText

logger = logging.getLogger(__name__)


class PdfTextExtractor:
    def extract(self, pdf_path: Path) -> list[PageText]:
        pages: list[PageText] = []
        with fitz.open(pdf_path) as doc:
            for index in range(doc.page_count):
                page = doc.load_page(index)
                text = page.get_text("text") or ""
                pages.append(PageText(page_number=index + 1, text=text, method="text"))
        logger.info("Extracted embedded text for %s pages", len(pages))
        return pages

