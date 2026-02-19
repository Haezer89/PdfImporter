from __future__ import annotations

import fitz
import pytesseract
from pdf2image import convert_from_path

from app.core.config import settings


def extract_pdf_text(pdf_path):
    text = _extract_text_native(pdf_path)
    if text.strip():
        return text
    return _extract_text_ocr(pdf_path)


def _extract_text_native(pdf_path):
    with fitz.open(pdf_path) as doc:
        return "\n".join(page.get_text("text") for page in doc)


def _extract_text_ocr(pdf_path):
    images = convert_from_path(str(pdf_path), dpi=300)
    page_texts = [pytesseract.image_to_string(img, lang=settings.ocr_lang) for img in images]
    return "\n".join(page_texts)
